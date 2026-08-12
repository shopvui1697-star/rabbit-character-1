# Movie MCP Server

> MCP (Model Context Protocol) server for movie search — queries `rabbit3.data_archive_movie_master` table in PostgreSQL.

---

## Overview

This MCP server provides movie search capabilities to the Rabbit3 backend via HTTP/SSE transport.

**Architecture:**

```
Backend (FastAPI)  ──stdio──▶  MCP Server (subprocess)  ──asyncpg──▶  PostgreSQL
                                                                        (rabbit3.data_archive_movie_master)
```

The backend spawns the MCP server as a subprocess and communicates via stdin/stdout using the MCP protocol.

**Key features:**
- **Phase 1**: SQL-based text search (ILIKE pattern matching on title, original_title, overview)
- **Phase 2**: Vector similarity search using pgvector (semantic search on embeddings)

---

## Setup

### 1. Install dependencies

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Or with uv:

```bash
cd mcp
python3 -m venv .venv
source .venv/bin/activate
uv pip install -r requirements.txt
```

### 2. Configure environment

Copy `.env.example` to `.env` and set your database connection:

```bash
cp .env.example .env
```

Edit `mcp/.env`:

```env
# Database connection (MCP server owns this — backend never sees it)
MOVIE_DATABASE_URL=postgresql://localhost:5432/rabbit3

# Server
MCP_HOST=0.0.0.0
MCP_PORT=8001
```

### 3. Ensure database table exists

The MCP server expects a table `data_archive_movie_master` in the `rabbit3` database.

**Reference schema** (see `migrations/001_base_table.sql`):

```sql
CREATE TABLE data_archive_movie_master (
    id              SERIAL PRIMARY KEY,
    title           TEXT,
    original_title  TEXT,
    overview        TEXT,
    release_date    TEXT,
    poster_path      TEXT,
    backdrop_path    TEXT,
    source          TEXT,
    vote_average    DOUBLE PRECISION,
    vote_count      INTEGER DEFAULT 0,
    genre_ids       TEXT,
    product_type    TEXT,
    runtime         INTEGER
);
```

If the table doesn't exist, create it:

```bash
psql -d rabbit3 -f migrations/001_base_table.sql
```

---

## Running the server

The MCP server is automatically spawned by the backend as a subprocess when needed. You don't need to run it manually.

**For testing purposes only**, you can run it directly:

```bash
cd mcp
python server.py
```

This will start the MCP server in stdio mode (reads from stdin, writes to stdout). You can send MCP protocol messages via stdin to test it.

---

## Available tools

### `search_movies`

Search movies by free-text query (matches title, original_title, overview).

**Arguments:**
- `query` (str): Search keywords (e.g. "tokyo action", "studio ghibli", "comedy 2024")
- `count` (int): Max results per page (1-100, default 10)
- `page` (int): Page number (1-based, default 1)

**Returns:** List of movie dicts with fields: `id`, `title`, `original_title`, `overview`, `release_date`, `poster_path`, `backdrop_path`, `source`, `vote_average`, `vote_count`, `genre_ids`, `product_type`, `runtime`

**Example:**
```python
# Via MCP client
result = await session.call_tool(
    "search_movies",
    arguments={"query": "spirited away", "count": 5}
)
```

### `get_movie_by_id`

Fetch a single movie by its primary key.

**Arguments:**
- `movie_id` (int): Movie ID

**Returns:** Single movie dict, or `None` if not found.

### `list_genres`

Get all distinct `genre_ids` values in the database.

**Returns:** List of dicts with `genre_ids` field.

---

## Phase 2: Vector search

To enable semantic similarity search using pgvector:

### 1. Run the migration

```bash
psql -d rabbit3 -f migrations/002_add_vector.sql
```

This adds:
- `embedding vector(1536)` column
- HNSW index for fast approximate nearest-neighbor search
- Optional full-text search index (`search_tsv`)

### 2. Populate embeddings

Generate embeddings for all movies using your local Ollama instance:

```python
import asyncio
import asyncpg
import httpx

async def populate_embeddings():
    """Generate embeddings using local Ollama (nomic-embed-text or mxbai-embed-large)."""
    conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/rabbit3")
    rows = await conn.fetch("SELECT id, title, overview FROM data_archive_movie_master")
    
    async with httpx.AsyncClient() as client:
        for i, row in enumerate(rows, 1):
            # Combine title and overview for embedding
            text = f"{row['title']} {row['overview']}"
            
            # Call local Ollama API
            response = await client.post(
                "http://localhost:11434/api/embeddings",
                json={
                    "model": "nomic-embed-text",  # or "mxbai-embed-large"
                    "prompt": text
                }
            )
            
            if response.status_code == 200:
                embedding = response.json()["embedding"]
                
                # Update database
                await conn.execute(
                    "UPDATE data_archive_movie_master SET embedding = $1 WHERE id = $2",
                    embedding, row['id']
                )
                print(f"✓ {i}/{len(rows)}: {row['title']}")
            else:
                print(f"✗ Failed to embed: {row['title']}")
    
    await conn.close()
    print(f"\n✓ Generated embeddings for {len(rows)} movies")

if __name__ == "__main__":
    asyncio.run(populate_embeddings())
```

**Available Ollama embedding models:**
- `nomic-embed-text` (768 dimensions) — Good for semantic search
- `mxbai-embed-large` (1024 dimensions) — Higher quality
- `all-minilm` (384 dimensions) — Faster, smaller

**Pull the model first:**
```bash
ollama pull nomic-embed-text
```

### 3. Uncomment the vector search tool

In `server.py`, uncomment the `search_movies_by_vector` tool (lines 129-145).

### 4. Install pgvector dependency

```bash
pip install -r requirements-vector.txt
```

### 5. Restart the server

The `search_movies_by_vector` tool will now be available.

---

## Testing

### Manual test with curl

```bash
# Start the server
cd mcp
python server.py

# In another terminal, call the search_movies tool
curl -X POST http://localhost:8001/sse \
  -H "Content-Type: application/json" \
  -d '{
    "jsonrpc": "2.0",
    "method": "tools/call",
    "params": {
      "name": "search_movies",
      "arguments": {"query": "spirited away", "count": 3}
    },
    "id": 1
  }'
```

### Test from the backend

The backend's `MovieClient` (in `backend/src/tools/movie.py`) automatically connects to the MCP server.

```python
# In backend/src/repl.py or any agent code
from src.tools.movie import MovieClient

client = MovieClient()
movies = await client.search_movies(query="your name", count=5)
for movie in movies:
    print(f"{movie.title} ({movie.release_date})")
```

---

## Troubleshooting

### Connection refused

- Ensure the MCP server is running: `cd mcp && python server.py`
- Check the backend's `MOVIE_MCP_URL` matches the server's host/port

### Database connection error

- Verify `MOVIE_DATABASE_URL` in `mcp/.env` is correct
- Test the connection: `psql postgresql://localhost:5432/rabbit3`
- Ensure PostgreSQL is running: `brew services start postgresql@16` (macOS)

### No results returned

- Check if the `data_archive_movie_master` table has data: `psql -d rabbit3 -c "SELECT COUNT(*) FROM data_archive_movie_master;"`
- Check the server logs for SQL errors

### Import errors

- Ensure dependencies are installed: `pip install -r requirements.txt` (from `mcp/` directory)
- For vector search: `pip install -r requirements-vector.txt`

---

## Development

### Project structure

```
mcp/
├── server.py              # MCP server entry point (FastMCP)
├── db.py                  # PostgreSQL connection pool (asyncpg)
├── pyproject.toml         # Dependencies
├── .env                   # Database credentials (gitignored)
├── .env.example           # Template
├── migrations/
│   ├── 001_base_table.sql # Phase 1 schema
│   └── 002_add_vector.sql # Phase 2 schema (pgvector)
└── README.md              # This file
```

### Adding new tools

Add a new tool to `server.py`:

```python
@mcp.tool()
async def my_new_tool(arg1: str, arg2: int) -> dict:
    """Tool description (shown to LLM)."""
    pool = await get_pool()
    # ... your logic
    return {"result": "..."}
```

The tool will automatically be exposed via the MCP protocol.

---

## Production deployment

### Option 1: Run as a systemd service (Linux)

Create `/etc/systemd/system/mcp-movie.service`:

```ini
[Unit]
Description=Movie MCP Server
After=network.target postgresql.service

[Service]
Type=simple
User=rabbit3
WorkingDirectory=/opt/rabbit3/mcp
Environment="MOVIE_DATABASE_URL=postgresql://localhost:5432/rabbit3"
Environment="MCP_HOST=0.0.0.0"
Environment="MCP_PORT=8001"
ExecStart=/opt/rabbit3/venv/bin/python server.py
Restart=always

[Install]
WantedBy=multi-user.target
```

Enable and start:

```bash
sudo systemctl enable mcp-movie
sudo systemctl start mcp-movie
```

### Option 2: Docker

Create `mcp/Dockerfile`:

```dockerfile
FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml .
RUN pip install -e .
COPY . .
CMD ["python", "server.py"]
```

Build and run:

```bash
docker build -t rabbit3-mcp-movie mcp/
docker run -p 8001:8001 --env-file mcp/.env rabbit3-mcp-movie
```

### Option 3: Docker Compose (with PostgreSQL)

Add to `docker-compose.yml`:

```yaml
services:
  postgres:
    image: pgvector/pgvector:pg16
    environment:
      POSTGRES_DB: rabbit3
      POSTGRES_PASSWORD: password
    volumes:
      - pgdata:/var/lib/postgresql/data

  mcp-movie:
    build: ./mcp
    ports:
      - "8001:8001"
    environment:
      MOVIE_DATABASE_URL: postgresql://postgres:password@postgres:5432/rabbit3
      MCP_HOST: 0.0.0.0
      MCP_PORT: 8001
    depends_on:
      - postgres

volumes:
  pgdata:
```

---

## License

Part of the Rabbit3 project.
