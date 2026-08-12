# Rabbit3 Backend

> Python backend for the Rabbit3 agentic voice assistant — Pydantic AI agents, HotPepper Gourmet API, and structured VoiceBotOutput.

---

## Quick Start

```bash
# Create virtual environment
python3 -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
uvicorn src.main:app --reload --port 8000

# Install dependencies
pip install -e ".[dev]"

# Configure environment
cp .env.example .env

# Run the interactive REPL
python -m src.repl
```

---

## Structure

```
backend/
├── src/
│   ├── config.py          # Settings (pydantic-settings)
│   ├── main.py            # FastAPI app (health check)
│   ├── observability.py   # Logfire instrumentation
│   ├── repl.py            # Text REPL for testing
│   ├── agents/
│   │   ├── gourmet.py     # Gourmet specialist agent
│   │   └── instructions/
│   │       └── gourmet.md # System prompt
│   ├── tools/
│   │   └── hotpepper.py   # HotPepper Gourmet API client
│   ├── models/
│   │   ├── output.py      # VoiceBotOutput, UIAction, etc.
│   │   ├── session.py     # SessionState, SessionDependencies
│   │   └── restaurant.py  # Restaurant, Genre, Area
│   └── session/
│       └── store.py       # In-memory session store
├── tests/
├── pyproject.toml
└── .env.example
```

---

## Environment Variables

| Variable | Required | Description |
|:---------|:---------|:------------|
| `AWS_ACCESS_KEY_ID` | Yes | AWS access key for Bedrock |
| `AWS_SECRET_ACCESS_KEY` | Yes | AWS secret key for Bedrock |
| `AWS_REGION` | Yes | AWS region (e.g., `us-east-1`) |
| `LOVVIT_API_KEY` | No* | Lovvit OpenSearch API key (required when `USE_DUMMY_GOURMET=false`) |
| `USE_DUMMY_GOURMET` | No | `true` (default) = dummy data; `false` = Lovvit API |
| `LOGFIRE_TOKEN` | No | Pydantic Logfire token for tracing (optional) |
| `ENVIRONMENT` | No | `development` \| `staging` \| `production` |
| `LOG_LEVEL` | No | `debug` \| `info` \| `warning` \| `error` |

---

## Step Timing (Debug Mode)

When `LOG_LEVEL=debug`, each execution step is traced to `backend/logs/trace_YYYYMMDD.log`:

```
2026-02-12T10:54:39.794Z [coordinator_keyword_route] 0.01ms
2026-02-12T10:54:39.798Z [agent_user_prompt] 0.37ms
2026-02-12T10:54:42.002Z [agent_llm_request] 2204.29ms
2026-02-12T10:54:42.245Z [tool_search_restaurants] 240.79ms source=lovvit
2026-02-12T10:54:42.246Z [agent_tool_call] 243.94ms tools=find_restaurants
2026-02-12T10:54:44.883Z [agent_llm_request] 2637.15ms
...
2026-02-12T10:54:56.791Z [agent_llm_request] 8907.05ms
2026-02-12T10:54:56.792Z [agent_tool_call] 2.00ms tools=final_result
2026-02-12T10:54:56.793Z [agent_gourmet] 16998.91ms domain=gourmet
2026-02-12T10:54:56.810Z [send_suggestions] 0.12ms session_id=abc123
```

**Child steps:**
- `agent_user_prompt` — Parse user input and build prompt
- `agent_llm_request` — LLM call (generates response, UI actions, suggestion chips)
- `agent_tool_call` — Tool execution (tools=name when available)
- `agent_end` — Run finished
- `tool_search_restaurants` / `tool_search_movies` — External API calls

**Top-level steps:** `ws_turn`, `route_and_run`, `send_voice`, `send_ui_update`, `send_suggestions`, `session_save`, `coordinator_keyword_route`, `coordinator_llm_route`, `agent_gourmet` / `agent_movie`.

---

## Commands

| Command | Description |
|:-------|:------------|
| `python -m src.repl` | Interactive text REPL — chat with the gourmet agent |
| `uvicorn src.main:app --reload --port 8000` | Start FastAPI server (health check at `/healthz`) |
| `pytest tests/ -v` | Run tests |
| `ruff check src/` | Lint |
| `ruff format src/` | Format |

---

## REPL Usage

```
You: Find Italian restaurants in Shibuya

Voice: "I found 5 Italian restaurants in Shibuya. Trattoria Milano..."

UI Actions:
  [1] SHOW_RESTAURANT_LIST: 5 restaurants
  [2] SHOW_MAP: 5 markers

Suggestions: [Show reviews] [Private rooms only] [Change budget]

You: Private rooms only
...
```

**Special commands:**
- `state` — Print current session state (debug)
- `clear` — Reset session
- `quit` / `exit` — Exit REPL

---

## Architecture

- **Agent:** Pydantic AI with Claude 3.5 Sonnet via AWS Bedrock
- **Output:** Structured `VoiceBotOutput` (voice_response + ui_actions + suggestions + context_update)
- **Tools:** 6 gourmet tools (search, lookup genre/area/budget, get detail, search by location)
- **API:** HotPepper Gourmet (restaurant search in Japan)

See [../docs/ARCHITECTURE.md](../docs/ARCHITECTURE.md) for full design.
