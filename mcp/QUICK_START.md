# Quick Start Guide

Get the MCP movie server running in 5 minutes.

---

## Your Current Setup

✅ Docker PostgreSQL (pgvector): `postgres_db` on port 5432  
✅ Docker Ollama: `archive_mcp_ollama` on port 11434  
✅ Backend running on port 8000  
✅ Frontend running on port 3000  

---

## Phase 1: Basic Setup (Works Now)

The app **already works** with dummy data fallback. To use real database:

### 1. Check Database Connection

```bash
cd /Volumes/RD/rabbit3/mcp
python check_schema.py
```

### 2. If Database/Table Missing

```bash
# Create database (if needed)
docker exec -it postgres_db createdb -U postgres rabbit3

# Create table
docker exec -it postgres_db psql -U postgres -d rabbit3 < migrations/001_base_table.sql

# Or copy migration into container first
docker cp migrations/001_base_table.sql postgres_db:/tmp/
docker exec -it postgres_db psql -U postgres -d rabbit3 -f /tmp/001_base_table.sql
```

### 3. Insert Sample Data

```bash
docker exec -it postgres_db psql -U postgres -d rabbit3 <<EOF
INSERT INTO data_archive_movie_master (title, original_title, overview, release_date, poster_url, vote_average, vote_count, genre_ids, product_type, runtime) VALUES
('Spirited Away', '千と千尋の神隠し', 'A young girl finds herself in a magical world of spirits.', '2001-07-20', 'https://image.tmdb.org/t/p/w500/39wmItIWsg5sZMyRUHLkWBcuVCM.jpg', 8.5, 14000, '16,14', 'movie', 125),
('Your Name', '君の名は。', 'Two teenagers share a profound connection.', '2016-08-26', 'https://image.tmdb.org/t/p/w500/q719jXXEhI1am6qdBIAbpZBecbg.jpg', 8.6, 9700, '16,18,14', 'movie', 106);
EOF
```

### 4. Test It

Search for movies in your app — you should now see real database results!

---

## Phase 2: Vector Search (Optional)

Enable semantic search with your local Ollama.

### Quick Setup

```bash
# 1. Pull embedding model
docker exec -it archive_mcp_ollama ollama pull nomic-embed-text

# 2. Add embedding column
docker cp migrations/002_add_vector.sql postgres_db:/tmp/
docker exec -it postgres_db psql -U postgres -d rabbit3 -f /tmp/002_add_vector.sql

# 3. Generate embeddings
cd /Volumes/RD/rabbit3/mcp
python generate_embeddings.py

# 4. Uncomment vector search tool in server.py (line 122)

# 5. Restart backend
```

**See `PHASE2_GUIDE.md` for detailed instructions.**

---

## Troubleshooting

### App returns dummy movies
- ✓ **Expected behavior** when database is unavailable
- Check `check_schema.py` output
- Verify `MOVIE_DATABASE_URL` in `.env`

### "Cannot connect to database"
```bash
# Check if PostgreSQL container is running
docker ps | grep postgres_db

# Start if needed
docker start postgres_db

# Test connection
docker exec -it postgres_db psql -U postgres -l
```

### "ModuleNotFoundError: asyncpg"
```bash
cd /Volumes/RD/rabbit3/backend
source .venv/bin/activate
pip install asyncpg
```

---

## File Reference

| File | Purpose |
|:-----|:--------|
| `check_schema.py` | Verify database setup |
| `test_db.py` | Test database connection |
| `generate_embeddings.py` | Phase 2: Generate embeddings |
| `SETUP.md` | Detailed setup guide |
| `PHASE2_GUIDE.md` | Vector search guide |
| `README.md` | Complete documentation |

---

## Architecture

```
Backend → MCP Server (subprocess) → PostgreSQL (Docker)
                                  → Ollama (Docker, Phase 2)
```

---

## Status Check

Run this to see your current status:

```bash
cd /Volumes/RD/rabbit3/mcp

echo "=== Docker Containers ==="
docker ps | grep -E "postgres_db|ollama"

echo -e "\n=== Database Status ==="
python check_schema.py

echo -e "\n=== Backend Status ==="
curl -s http://localhost:8000/healthz

echo -e "\n=== Frontend Status ==="
curl -s http://localhost:3000 > /dev/null && echo "✓ Running" || echo "✗ Not running"
```

---

## Next Steps

1. ✅ **Phase 1 working?** → Add more movie data
2. ✅ **Want semantic search?** → Follow `PHASE2_GUIDE.md`
3. ✅ **Need help?** → Check `SETUP.md` troubleshooting section

🎬 Happy movie searching!
