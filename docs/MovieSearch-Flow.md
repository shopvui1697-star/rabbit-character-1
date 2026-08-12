# Movie Search Flow — SQL + Vector Hybrid

End-to-end flow for how a movie search query travels from user input to database results, including Phase 1 (SQL/ILIKE), Phase 2 (pgvector semantic), and the planned hybrid.

---

## Architecture Overview

```
User
  │  text_input / chip_selected (WebSocket)
  ▼
FastAPI WebSocket Handler          backend/src/ws/handler.py
  │  route_and_run(text)
  ▼
Coordinator                        backend/src/agents/coordinator.py
  │  keyword_route → "movie"
  │  (or LLM route if ambiguous)
  ▼
Movie Agent (Pydantic AI)          backend/src/agents/movie.py
  │  LLM decides to call find_movies(query)
  ▼
MovieClient                        backend/src/tools/movie.py
  │  spawns MCP subprocess (stdio)
  ▼
MCP Server                         mcp/server.py
  │  SQL / Vector query
  ▼
PostgreSQL                         data_archive_movie_master
  │  asyncpg connection pool
  ▼
Results bubble back up the chain → VoiceBotOutput → WebSocket → Frontend
```

---

## Step 1 — Routing (Coordinator)

**File:** `backend/src/agents/coordinator.py`

```
User: "find disaster movies"
         │
         ▼
   _keyword_route(text)
   ─ Scans for keywords:
     _MOVIE_KEYWORDS = { "movie", "movies", "film", "映画", ... }
     _GOURMET_KEYWORDS = { "restaurant", "レストラン", ... }
         │
   hit: "movies" → domain = "movie"     ← fast, no LLM call
         │
   (if ambiguous) → _llm_route(text)    ← Bedrock LLM call
         │                                 returns { "domain": "movie" }
         ▼
   movie_agent.run(text, deps, history)
```

Keyword routing avoids an LLM call when the intent is obvious. LLM routing is the fallback for ambiguous input.

---

## Step 2 — Movie Agent (LLM)

**File:** `backend/src/agents/movie.py`

The agent is a Pydantic AI agent backed by **AWS Bedrock (Claude 3.5 Sonnet)**.

### System prompt built from two parts

| Part | Source | Content |
|------|--------|---------|
| Static instructions | `instructions/movie.md` | Rules, personality, output format |
| Dynamic context | `add_session_context()` | `current_topic`, `last_search_results` titles |

### Agent loop

```
LLM receives:
  - system prompt (static + dynamic)
  - message history (previous turns)
  - user text: "disaster earthquake films"

LLM decides:
  → call tool: find_movies(query="earthquake disaster", count=5)

Tool executes → results returned to LLM

LLM produces VoiceBotOutput:
  {
    "voice_response": "I found 5 disaster movies...",
    "ui_actions": [{ "action": "SHOW_MOVIE_LIST", "data": { "movies": [...] } }],
    "suggestions": ["Show tsunami films", "Find apocalyptic movies"],
    "context_update": { "current_topic": "movie" }
  }
```

---

## Step 3 — MovieClient (MCP Bridge)

**File:** `backend/src/tools/movie.py`

The backend **never connects to PostgreSQL directly**. It spawns the MCP server as a child process over stdio.

```python
_MCP_SERVER = StdioServerParameters(
    command="python",
    args=["server.py"],
    cwd=".../mcp/",
    env={"MOVIE_DATABASE_URL": settings.movie_database_url},
)

async with stdio_client(_MCP_SERVER) as (read, write):
    async with ClientSession(read, write) as session:
        await session.initialize()
        result = await session.call_tool(
            "search_movies",
            arguments={"query": query, "count": count, "page": page},
        )
```

### Fallback

If the MCP server is unreachable (subprocess fails):

```
MCP error → logger.exception → return DUMMY_MOVIES (3 hardcoded films)
```

---

## Step 4A — Phase 1: SQL Text Search (Current)

**File:** `mcp/server.py` → `search_movies()`

### Algorithm

```
query = "earthquake disaster"
         │
keywords = ["earthquake", "disaster"]    ← split by space
         │
WHERE (title ILIKE '%earthquake%' OR original_title ILIKE '%earthquake%' OR overview ILIKE '%earthquake%')
  AND (title ILIKE '%disaster%'   OR original_title ILIKE '%disaster%'   OR overview ILIKE '%disaster%')
         │
ORDER BY vote_count DESC NULLS LAST, id
LIMIT $n OFFSET $m
```

### SQL generated

```sql
SELECT id, title, original_title, overview, release_date,
       poster_path AS poster_url, backdrop_path AS backdrop_url,
       source AS source, vote_average, vote_count, genre_ids, runtime
FROM data_archive_movie_master
WHERE (title ILIKE $1 OR original_title ILIKE $1 OR overview ILIKE $1)
  AND (title ILIKE $2 OR original_title ILIKE $2 OR overview ILIKE $2)
ORDER BY vote_count DESC NULLS LAST, id
LIMIT $3 OFFSET $4
```

### Characteristics

| Property | Value |
|----------|-------|
| Match type | Exact substring (case-insensitive) |
| Multi-keyword | AND logic (all keywords must match) |
| Ranking | By `vote_count` descending |
| Index | Sequential scan or B-tree on text fields |
| Supports | Exact title, partial title, keyword in overview |
| Fails on | Semantics ("sad love story" ≠ "romantic drama") |

---

## Step 4B — Phase 2: Vector Similarity Search

**File:** `mcp/server.py` → `search_movies_by_vector()`

### Offline: Embed all movies (one-time)

**Script:** `mcp/generate_embeddings.py`

```
For each movie in data_archive_movie_master:
  text = title + " " + original_title + " " + overview
         │
  POST http://localhost:11434/api/embeddings
       { "model": "nomic-embed-text", "prompt": text }
         │
  embedding = [float × 768]
         │
  vector_str = "[x1,x2,...,x768]"
         │
  UPDATE data_archive_movie_master
    SET embedding = $1::vector
    WHERE id = $2
```

### Database schema

```sql
-- Migration: 002_add_vector.sql
CREATE EXTENSION IF NOT EXISTS vector;

ALTER TABLE data_archive_movie_master
    ADD COLUMN embedding vector(768);

CREATE INDEX idx_movie_embedding
    ON data_archive_movie_master
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);
```

### Online: Search by vector

```
User query: "romantic anime love story"
         │
Ollama API: POST /api/embeddings
            { "model": "nomic-embed-text", "prompt": query }
         │
query_vector = [float × 768]
vector_str   = "[x1,x2,...,x768]"   ← must be string for asyncpg
         │
SQL:
  SELECT title, 1 - (embedding <=> $1::vector) AS similarity
  FROM data_archive_movie_master
  WHERE embedding IS NOT NULL
  ORDER BY embedding <=> $1::vector   ← cosine distance (lower = closer)
  LIMIT $2
         │
Results ranked by semantic similarity (0.0 = unrelated, 1.0 = identical)
```

### How cosine similarity works

```
similarity = 1 - cosine_distance(query_vec, movie_vec)

query_vec  = embedding of "romantic anime love story"
movie_vec  = embedding of movie title + overview

Closest movies: those whose embedding space direction
                most closely matches the query direction.

Example output:
  発情娘 糸ひき生下着    0.757
  ある日わたしは         0.755
  ラブ・アージ・カル     0.750
```

### HNSW index

```
HNSW (Hierarchical Navigable Small World):
- Approximate nearest-neighbor graph
- m = 16: connections per node (quality vs memory tradeoff)
- ef_construction = 64: build-time accuracy
- Search is O(log n) instead of O(n) full scan
- ~5–20ms for 100k movies
```

---

## Step 4C — Phase 2+: Hybrid Search (Planned)

Combine SQL keyword match with vector semantic match.

### Strategy

```
score = weight_sql * sql_score + weight_vec * vector_score
```

### SQL

```sql
-- Option A: Union approach
SELECT id, title, 1.0 AS score, 'sql' AS source
FROM data_archive_movie_master
WHERE title ILIKE '%earthquake%'

UNION ALL

SELECT id, title,
       1 - (embedding <=> $1::vector) AS score,
       'vector' AS source
FROM data_archive_movie_master
WHERE embedding IS NOT NULL
  AND 1 - (embedding <=> $1::vector) > 0.5   ← similarity threshold

ORDER BY score DESC
LIMIT 10;
```

```sql
-- Option B: Keyword OR semantic (single pass)
SELECT id, title,
    CASE
        WHEN title ILIKE '%keyword%' THEN 1.0
        ELSE 1 - (embedding <=> $1::vector)
    END AS score
FROM data_archive_movie_master
WHERE title ILIKE '%keyword%'
   OR embedding <=> $1::vector < 0.5
ORDER BY score DESC
LIMIT 10;
```

### When to use each

| Query type | Best search | Reason |
|------------|-------------|--------|
| Exact title: "Spirited Away" | SQL ILIKE | Fast, precise |
| Keyword in overview: "Ghibli" | SQL ILIKE | Substring match |
| Semantic: "sad story of old parents" | Vector | No keyword match |
| Mixed: "tokyo earthquake disaster film" | Hybrid | Both keyword + meaning |
| Multilingual: "千と千尋" | Vector | Cross-lingual embedding |

---

## Data Flow Summary

```
User: "disaster earthquake films"
   │
   │ WebSocket: { type: "text_input", data: { text } }
   ▼
handler.py
   │ status: "thinking"
   │ route_and_run(text)
   ▼
coordinator.py
   │ _keyword_route → "movie"   (keyword: "films")
   ▼
movie_agent (Pydantic AI + Bedrock)
   │ LLM call → find_movies(query="earthquake disaster", count=5)
   ▼
MovieClient.search_movies()
   │ stdio subprocess → MCP server
   ▼
mcp/server.py: search_movies()
   │
   │── Phase 1 (now): ILIKE multi-keyword SQL
   │── Phase 2:       Ollama embed → pgvector cosine search
   │── Hybrid:        SQL score + vector score combined
   │
   ▼
PostgreSQL: data_archive_movie_master
   │ rows returned
   ▼
MCP server → JSON text block
   ▼
MovieClient._parse_mcp_result() → list[dict]
   │ _row_to_movie() → list[Movie]
   ▼
movie_agent LLM sees results → builds VoiceBotOutput
   ▼
handler.py sends:
   { type: "voice_response", data: { text: "..." } }
   { type: "ui_update",      data: { actions: [SHOW_MOVIE_LIST] } }
   { type: "suggestions",    data: { chips: [...] } }
   { type: "status",         data: { state: "idle" } }
   ▼
Frontend: MovieList panel + SuggestionChips
```

---

## Files Reference

| File | Role |
|------|------|
| `backend/src/ws/handler.py` | Entry point, WebSocket lifecycle |
| `backend/src/agents/coordinator.py` | Keyword + LLM routing |
| `backend/src/agents/movie.py` | Movie specialist agent + `find_movies` tool |
| `backend/src/agents/instructions/movie.md` | LLM system prompt |
| `backend/src/tools/movie.py` | MCP client (spawns subprocess) |
| `backend/src/models/movie.py` | `Movie` Pydantic model |
| `mcp/server.py` | MCP tools: `search_movies`, `search_movies_by_vector` |
| `mcp/db.py` | asyncpg connection pool |
| `mcp/generate_embeddings.py` | Offline embedding generation script |
| `mcp/migrations/002_add_vector.sql` | pgvector extension + HNSW index |
| `mcp/test_vector_search.py` | Manual test for vector search |
