# Phase 2: Vector Search with Local Ollama

Complete guide to enabling semantic search using your existing Ollama setup.

---

## Prerequisites

✅ You already have:
- Docker container `postgres_db` (pgvector/pgvector:pg17)
- Docker container `archive_mcp_ollama` (ollama/ollama:latest)
- PostgreSQL with pgvector extension

---

## Step-by-Step Setup

### 1. Ensure Ollama is Running

```bash
# Check if Ollama container is running
docker ps | grep ollama

# If not running, start it
docker start archive_mcp_ollama

# Test Ollama API
curl http://localhost:11434/api/tags
```

### 2. Pull Embedding Model

Choose one of these models:

```bash
# Option A: nomic-embed-text (768 dimensions) — Recommended
docker exec -it archive_mcp_ollama ollama pull nomic-embed-text

# Option B: mxbai-embed-large (1024 dimensions) — Higher quality
docker exec -it archive_mcp_ollama ollama pull mxbai-embed-large

# Option C: all-minilm (384 dimensions) — Faster, smaller
docker exec -it archive_mcp_ollama ollama pull all-minilm
```

**Recommended:** `nomic-embed-text` (good balance of quality and speed)

### 3. Update Migration for Your Model

Edit `migrations/002_add_vector.sql` and set the correct dimension:

```sql
-- For nomic-embed-text (768 dimensions)
ALTER TABLE data_archive_movie_master
    ADD COLUMN IF NOT EXISTS embedding vector(768);

-- For mxbai-embed-large (1024 dimensions)
-- ALTER TABLE data_archive_movie_master
--     ADD COLUMN IF NOT EXISTS embedding vector(1024);

-- For all-minilm (384 dimensions)
-- ALTER TABLE data_archive_movie_master
--     ADD COLUMN IF NOT EXISTS embedding vector(384);
```

### 4. Run the Migration

```bash
# Connect to your PostgreSQL container
docker exec -it postgres_db psql -U postgres -d rabbit3 -f /path/to/migrations/002_add_vector.sql

# Or if you have psql locally
psql -U postgres -d rabbit3 -f migrations/002_add_vector.sql
```

Verify the column was added:

```bash
psql -U postgres -d rabbit3 -c "\d data_archive_movie_master"
```

You should see an `embedding` column with type `vector(768)` (or your chosen dimension).

### 5. Generate Embeddings

Run the embedding generation script:

```bash
cd /Volumes/RD/rabbit3/mcp

# Using default model (nomic-embed-text)
python generate_embeddings.py

# Or specify a different model
python generate_embeddings.py --model mxbai-embed-large
```

**This will:**
1. ✓ Check if Ollama is running
2. ✓ Check if the model is available
3. ✓ Connect to the database
4. ✓ Generate embeddings for all movies
5. ✓ Update the database with embeddings

**Expected output:**
```
============================================================
Movie Embedding Generator (Ollama)
============================================================
Model: nomic-embed-text
============================================================

Checking Ollama at http://localhost:11434...
✓ Ollama is running
Checking if model 'nomic-embed-text' is available...
✓ Model 'nomic-embed-text' is available

Connecting to database...
✓ Connected to database
✓ Embedding column exists

🎬 Generating embeddings for 150 movies...

✓ [1/150] Spirited Away
✓ [2/150] Your Name
✓ [3/150] Tokyo Story
...
✓ [150/150] The Last Movie

🎉 Done! Generated 150/150 embeddings
```

### 6. Enable Vector Search in MCP Server

Edit `server.py` and **uncomment** the `search_movies_by_vector` tool (around line 122):

```python
# Remove the # comments from this block:
@mcp.tool()
async def search_movies_by_vector(
    query_embedding: list[float],
    count: int = 10,
) -> list[dict[str, Any]]:
    # ... (uncomment the entire function)
```

### 7. Test Vector Search

Create a test script:

```python
# test_vector_search.py
import asyncio
import httpx
import asyncpg

async def test_vector_search():
    # Get embedding for query
    async with httpx.AsyncClient() as client:
        response = await client.post(
            "http://localhost:11434/api/embeddings",
            json={
                "model": "nomic-embed-text",
                "prompt": "romantic anime love story"
            }
        )
        query_embedding = response.json()["embedding"]
    
    # Search database
    conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/rabbit3")
    
    rows = await conn.fetch("""
        SELECT title, 1 - (embedding <=> $1::vector) AS similarity
        FROM data_archive_movie_master
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> $1::vector
        LIMIT 5
    """, query_embedding)
    
    print("Top 5 similar movies:")
    for row in rows:
        print(f"  {row['title']}: {row['similarity']:.3f}")
    
    await conn.close()

asyncio.run(test_vector_search())
```

Run it:
```bash
python test_vector_search.py
```

---

## Performance Tuning

### Index Optimization

The HNSW index parameters can be tuned:

```sql
-- Default (from migration)
CREATE INDEX idx_movie_embedding 
    ON data_archive_movie_master 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- For better accuracy (slower build, faster search)
CREATE INDEX idx_movie_embedding 
    ON data_archive_movie_master 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 32, ef_construction = 128);

-- For faster build (less accurate)
CREATE INDEX idx_movie_embedding 
    ON data_archive_movie_master 
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 8, ef_construction = 32);
```

### Embedding Model Comparison

| Model | Dimensions | Speed | Quality | Use Case |
|:------|:-----------|:------|:--------|:---------|
| `nomic-embed-text` | 768 | Fast | Good | **Recommended** — Best balance |
| `mxbai-embed-large` | 1024 | Medium | Excellent | High accuracy needed |
| `all-minilm` | 384 | Very Fast | Decent | Speed critical |

---

## Hybrid Search (Phase 2+)

Combine SQL text search with vector similarity:

```sql
-- Hybrid: keyword match OR semantic similarity
SELECT 
    id, title, 
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

---

## Troubleshooting

### "Ollama not responding"
```bash
docker start archive_mcp_ollama
docker logs archive_mcp_ollama
```

### "Model not found"
```bash
docker exec -it archive_mcp_ollama ollama list
docker exec -it archive_mcp_ollama ollama pull nomic-embed-text
```

### "Embedding column doesn't exist"
```bash
psql -U postgres -d rabbit3 -f migrations/002_add_vector.sql
```

### "Cannot connect to database"
Check your `MOVIE_DATABASE_URL` in `.env`:
```bash
# Should match your Docker PostgreSQL credentials
MOVIE_DATABASE_URL=postgresql://postgres:password@localhost:5432/rabbit3
```

### Slow embedding generation
- Use a smaller model (`all-minilm`)
- Reduce batch size
- Check Ollama container resources

---

## Next Steps

Once vector search is working:

1. **Update backend** to use `search_movies_by_vector` for semantic queries
2. **Implement hybrid search** combining SQL + vector
3. **Add relevance tuning** based on user feedback
4. **Enable multilingual search** (embeddings work across languages!)

---

## Summary

✅ **Phase 1:** SQL text search (ILIKE) — Working now  
✅ **Phase 2:** Vector search (Ollama) — Ready to enable  
🚀 **Phase 2+:** Hybrid search — Future enhancement  

Your local setup is perfect for this — no external API calls, no costs, full control! 🎬
