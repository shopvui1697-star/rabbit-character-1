"""Coordinator — lightweight intent router that delegates to specialist agents.

Uses a fast LLM call to classify the user's intent into a domain, then
delegates to the appropriate specialist agent (gourmet or movie).
"""

from __future__ import annotations

import json
import logging
import time
from pathlib import Path

from pydantic_ai import Agent

from pydantic_graph.nodes import End

from src.agents.llm import chat_model
from src.models.output import VoiceBotOutput
from src.models.session import SessionDependencies
from src.tracing import log_input, log_step, trace_step, trace_step_sync

logger = logging.getLogger(__name__)

# Load system prompt
_instructions_path = Path(__file__).parent / "instructions" / "coordinator.md"
_instructions = _instructions_path.read_text(encoding="utf-8")

# ─── Quick keyword-based routing (avoids LLM call for obvious cases) ─────────

_MOVIE_KEYWORDS = {
    "movie", "movies", "film", "films", "cinema", "映画", "シネマ",
    "ムービー", "上映", "watch", "trailer", "actor", "actress",
    "director", "監督", "俳優", "女優",
}
_GOURMET_KEYWORDS = {
    "restaurant", "restaurants", "food", "dining", "レストラン", "ランチ",
    "ディナー", "居酒屋", "ラーメン", "寿司", "焼肉", "カフェ",
    "グルメ", "食事", "予約", "予算",
}


def _keyword_route(text: str, current_topic: str | None) -> str | None:
    """Return domain if obvious from keywords, else None (needs LLM)."""
    lower = text.lower()

    movie_hits = sum(1 for kw in _MOVIE_KEYWORDS if kw in lower)
    gourmet_hits = sum(1 for kw in _GOURMET_KEYWORDS if kw in lower)

    if movie_hits and not gourmet_hits:
        return "movie"
    if gourmet_hits and not movie_hits:
        return "gourmet"

    # Both or neither → cannot decide from keywords alone
    return None


# ─── LLM-based router (fallback) ─────────────────────────────────────────────

_router_agent: Agent[None, str] = Agent(
    chat_model,
    output_type=str,
    instructions=_instructions,
    retries=1,
)


async def _llm_route(text: str, current_topic: str | None) -> str:
    """Use a lightweight LLM call to classify the user's intent."""
    context = f"(Current topic: {current_topic}) " if current_topic else ""
    prompt = f"{context}User message: {text}"

    try:
        result = await _router_agent.run(prompt)
        raw = result.output.strip()
        # Try to parse JSON
        try:
            data = json.loads(raw)
            return data.get("domain", "gourmet")
        except json.JSONDecodeError:
            # If the model just returned the domain name
            if "movie" in raw.lower():
                return "movie"
            return "gourmet"
    except Exception:
        logger.exception("Router LLM call failed, defaulting to gourmet")
        return "gourmet"


# ─── Agent run with child-step tracing ───────────────────────────────────────


def _node_step_name(node: object) -> str:
    """Map graph node to a human-readable trace step name."""
    from pydantic_ai._agent_graph import CallToolsNode, ModelRequestNode, UserPromptNode

    if isinstance(node, UserPromptNode):
        return "agent_user_prompt"
    if isinstance(node, ModelRequestNode):
        return "agent_llm_request"
    if isinstance(node, CallToolsNode):
        return "agent_tool_call"
    if isinstance(node, End):
        return "agent_end"
    return f"agent_node_{type(node).__name__}"


def _get_node_input(node: object) -> str:
    """Extract input summary for a graph node for trace logging."""
    from pydantic_ai._agent_graph import CallToolsNode, ModelRequestNode, UserPromptNode

    if isinstance(node, UserPromptNode):
        return str(getattr(node, "user_prompt", "") or "")
    if isinstance(node, ModelRequestNode):
        req = getattr(node, "request", None)
        if req:
            parts = getattr(req, "parts", []) or []
            return f"request({len(parts)} parts)"
        return "request"
    if isinstance(node, CallToolsNode):
        tools = _get_tool_names(node)
        return f"tools={','.join(tools)}" if tools else "tool_call"
    return ""


def _get_tool_names(node: object) -> list[str]:
    """Extract tool names from CallToolsNode if available."""
    from pydantic_ai._agent_graph import CallToolsNode

    if not isinstance(node, CallToolsNode):
        return []
    names: list[str] = []
    try:
        resp = getattr(node, "model_response", None)
        parts = getattr(resp, "parts", []) or []
        for part in parts:
            if getattr(part, "tool_name", None):
                names.append(str(part.tool_name))
    except Exception:
        pass
    return names


async def _run_agent_with_tracing(agent, text: str, deps, history: list):
    """Run agent via iter() and trace each child step (LLM request, tool call, etc.)."""
    prev_node = None
    prev_ts = None
    result = None

    async with agent.iter(text, deps=deps, message_history=history) as agent_run:
        async for node in agent_run:
            now = time.perf_counter()
            if prev_node is not None and prev_ts is not None:
                elapsed_ms = (now - prev_ts) * 1000
                step = _node_step_name(prev_node)
                extras = {}
                if step == "agent_tool_call":
                    tools = _get_tool_names(prev_node)
                    if tools:
                        extras["tools"] = ",".join(tools)
                log_step(step, elapsed_ms, **extras)
            # Log input for this node (before we process it)
            step = _node_step_name(node)
            if isinstance(node, End):
                log_input(step, "completed")
            else:
                log_input(step, _get_node_input(node))
            prev_node = node
            prev_ts = now
            if isinstance(node, End):
                result = agent_run.result
                elapsed_ms = (time.perf_counter() - prev_ts) * 1000
                log_step("agent_end", elapsed_ms)
                break

    return result


# ─── Public API ───────────────────────────────────────────────────────────────


async def route_and_run(
    text: str,
    deps: SessionDependencies,
    message_history: list | None = None,
) -> tuple[VoiceBotOutput, list, str]:
    """Route user message to the right specialist and run it.

    Returns:
        (output, updated_message_history, domain)
    """
    from src.agents.gourmet import gourmet_agent
    from src.agents.movie import movie_agent

    current_topic = deps.state.current_topic
    history = message_history or []

    # Step 1: Determine domain
    log_input("coordinator_keyword_route", text)
    with trace_step_sync("coordinator_keyword_route"):
        domain = _keyword_route(text, current_topic)

    if domain is None:
        # Use current topic as default if set, else ask LLM
        if current_topic in ("gourmet", "movie"):
            domain = current_topic
        else:
            log_input("coordinator_llm_route", text)
            async with trace_step("coordinator_llm_route"):
                domain = await _llm_route(text, current_topic)

    logger.info("Routing to domain=%s for text=%r", domain, text[:80])

    # Step 2: Run the specialist (with child-step tracing when debug)
    agent = movie_agent if domain == "movie" else gourmet_agent
    step_name = f"agent_{domain}"
    async with trace_step(step_name, domain=domain):
        result = await _run_agent_with_tracing(agent, text, deps, history)

    return result.output, result.all_messages(), domain
