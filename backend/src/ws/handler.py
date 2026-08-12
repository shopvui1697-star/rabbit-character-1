"""WebSocket handler — connects the frontend to the agent pipeline."""

from __future__ import annotations

import json
import logging
import uuid

from fastapi import WebSocket, WebSocketDisconnect

from src.agents.coordinator import route_and_run
from src.tracing import log_input, trace_step
from src.models.session import SessionDependencies, SessionState
from src.session.store import InMemorySessionStore
from src.tools.hotpepper import HotPepperClient
from src.tools.movie import MovieClient

logger = logging.getLogger(__name__)

# Shared across connections (Phase 1: in-memory, Phase 4: Redis)
_session_store = InMemorySessionStore()
_hotpepper_client = HotPepperClient()
_movie_client = MovieClient()


async def websocket_handler(ws: WebSocket) -> None:
    """Handle a single WebSocket connection lifecycle."""
    await ws.accept()

    session_id = ws.query_params.get("session_id") or str(uuid.uuid4())[:8]
    state = await _session_store.get(session_id) or SessionState(session_id=session_id)
    message_history: list = []

    logger.info("WS connected: session=%s", session_id)

    try:
        while True:
            raw = await ws.receive_text()
            try:
                msg = json.loads(raw)
            except json.JSONDecodeError:
                await ws.send_json({"type": "error", "data": {"message": "Invalid JSON"}})
                continue

            msg_type = msg.get("type")
            msg_data = msg.get("data", {})

            if msg_type in ("text_input", "chip_selected"):
                user_text = msg_data.get("text") or msg_data.get("chip", "")
                if not user_text:
                    continue

                # Notify frontend: thinking
                await ws.send_json({"type": "status", "data": {"state": "thinking"}})

                deps = SessionDependencies(
                    state=state,
                    hotpepper_client=_hotpepper_client,
                    movie_client=_movie_client,
                )

                try:
                    log_input("ws_turn", user_text)
                    async with trace_step(
                        "ws_turn",
                        session_id=session_id,
                        msg_type=msg_type or "",
                    ):
                        log_input("route_and_run", user_text)
                        async with trace_step("route_and_run", session_id=session_id):
                            output, message_history, domain = await route_and_run(
                                user_text,
                                deps=deps,
                                message_history=message_history,
                            )

                        # Send voice response
                        log_input("send_voice", output.voice_response)
                        async with trace_step("send_voice", session_id=session_id):
                            await ws.send_json({
                                "type": "voice_response",
                                "data": {"text": output.voice_response},
                            })

                        # Send UI actions
                        log_input("send_ui_update", ",".join(a.action.value for a in output.ui_actions) or "none")
                        async with trace_step("send_ui_update", session_id=session_id):
                            await ws.send_json({
                                "type": "ui_update",
                                "data": {
                                    "actions": [a.model_dump(mode="json") for a in output.ui_actions]
                                },
                            })

                        # Send suggestions
                        log_input("send_suggestions", "|".join(output.suggestions) if output.suggestions else "none")
                        async with trace_step("send_suggestions", session_id=session_id):
                            await ws.send_json({
                                "type": "suggestions",
                                "data": {"chips": output.suggestions},
                            })

                        # Apply context update
                        if output.context_update:
                            state.apply_context_update(
                                output.context_update.model_dump(exclude_none=True)
                            )

                        state.turn_count += 1
                        async with trace_step("session_save", session_id=session_id):
                            await _session_store.save(session_id, state)

                except Exception as e:
                    logger.exception("Agent error: %s", e)
                    await ws.send_json({
                        "type": "voice_response",
                        "data": {"text": f"Sorry, something went wrong: {e}"},
                    })

                # Notify frontend: idle
                await ws.send_json({"type": "status", "data": {"state": "idle"}})

            elif msg_type == "feedback":
                logger.info(
                    "Feedback: session=%s score=%s",
                    session_id,
                    msg_data.get("score"),
                )

            else:
                await ws.send_json({
                    "type": "error",
                    "data": {"message": f"Unknown message type: {msg_type}"},
                })

    except WebSocketDisconnect:
        logger.info("WS disconnected: session=%s", session_id)
