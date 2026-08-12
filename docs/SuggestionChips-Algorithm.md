# Suggestion Chips — Backend Algorithm

How the backend creates suggestion chips for the voice assistant UI.

---

## Overview

Suggestion chips are **LLM-generated**, not rule-based. There is no explicit algorithm in code. The LLM produces a `suggestions` list as part of its structured output, guided by:

1. **Schema** — `VoiceBotOutput.suggestions` (list of strings, max 4)
2. **Instructions** — Domain-specific prompts that tell the LLM to "always include suggestions"
3. **Session context** — Injected state (last search results, selected area, etc.)

---

## Flow

```
User message (text_input or chip_selected)
        │
        ▼
Coordinator routes to specialist (gourmet | movie)
        │
        ▼
Specialist agent runs with:
  - System instructions (gourmet.md / movie.md)
  - Dynamic session context (add_session_context)
  - Tools (find_restaurants, find_movies, etc.)
        │
        ▼
LLM returns VoiceBotOutput JSON:
  - voice_response
  - ui_actions
  - suggestions  ← chips
  - context_update
        │
        ▼
WebSocket sends { type: "suggestions", data: { chips } }
        │
        ▼
Frontend renders SuggestionChips
```

---

## Schema

**File:** `backend/src/models/output.py`

```python
class VoiceBotOutput(BaseModel):
    voice_response: str = ...
    ui_actions: list[UIAction] = ...
    suggestions: list[str] = Field(
        default_factory=list,
        description="Follow-up suggestion chips shown to the user. Max 4 items.",
    )
    follow_up_prompt: str | None = ...
    context_update: ContextUpdate | None = ...
```

- **Type:** `list[str]`
- **Constraint:** Max 4 items (enforced by instruction, not schema)
- **Validation:** Pydantic AI validates and retries up to 3 times on failure

---

## Instructions (Algorithm Guidance)

### Gourmet

**File:** `backend/src/agents/instructions/gourmet.md`

- Rule 8: "Always include suggestions for follow-up actions (filter, book, details, etc.)"
- UI Actions: "SHOW_SUGGESTION_CHIPS — always provide 2-4 follow-up suggestions"

**Typical patterns:**
- Show map
- Private rooms
- Show details (for selected restaurant)
- Different area / genre
- Budget filter

### Movie

**File:** `backend/src/agents/instructions/movie.md`

- Rule 6: "Always include suggestions for follow-up actions (similar movies, details, different genre)"

**Typical patterns:**
- Search for earthquake movies
- Find tsunami films
- Look for apocalyptic films
- Show details for [title]
- Different genre

---

## Context Inputs

Session state is injected into the agent via `add_session_context` (dynamic instructions). The LLM uses this to tailor suggestions.

| Context field | Gourmet | Movie |
|---------------|---------|-------|
| `selected_area` | ✓ Area-specific follow-ups | — |
| `last_search_results` | ✓ "Show details", "Show map" | ✓ "Similar movies", "Details for X" |
| `selected_restaurant` | ✓ "Show reviews", "Book" | — |
| `current_topic` | ✓ Domain awareness | ✓ Domain awareness |
| `preferred_cuisines` | ✓ Filter suggestions | — |
| `budget_preference` | ✓ Budget-related chips | — |

---

## Implementation Notes

### No explicit algorithm

- No `if/else` or template logic for chips
- No separate "suggestion generator" function
- Chips are a field in the same LLM call that produces voice_response and ui_actions

### Cost

- **No extra LLM call** — suggestions are part of the turn response
- **Token cost** — Small (typically 20–80 tokens for 2–4 short strings)

### Consistency

- Quality depends on model and instructions
- No guarantee of format (e.g. "Show map" vs "地図を見る") — language follows user/session
- Duplicates or irrelevant chips possible; instruction tuning improves this

---

## Possible Enhancements (Future)

| Approach | Description |
|----------|-------------|
| **Rule-based fallback** | If LLM returns empty suggestions, fill with domain defaults (e.g. "Show map", "Different area") |
| **Post-filter** | Deduplicate, truncate long labels, enforce max 4 |
| **Template + LLM** | Predefine slots (e.g. "Show details for {title}") and let LLM fill variables |
| **Hybrid** | Combine rule-based "always show" chips with LLM-generated contextual ones |
