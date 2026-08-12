"""Generate embeddings for all movies using local Ollama.

Usage:
    python generate_embeddings.py [--model MODEL_NAME]

Models:
    nomic-embed-text (default) — 768 dimensions
    mxbai-embed-large — 1024 dimensions
    all-minilm — 384 dimensions
"""

import asyncio
import argparse
import os
import asyncpg
import httpx


OLLAMA_URL = os.environ.get("OLLAMA_URL", "http://localhost:11434")


async def check_ollama_model(model: str) -> bool:
    """Check if the Ollama model is available."""
    async with httpx.AsyncClient() as client:
        try:
            response = await client.get(f"{OLLAMA_URL}/api/tags")
            if response.status_code == 200:
                models = response.json().get("models", [])
                return any(m["name"].startswith(model) for m in models)
        except Exception:
            pass
    return False


async def get_embedding(client: httpx.AsyncClient, text: str, model: str) -> list[float] | None:
    """Get embedding from Ollama."""
    try:
        response = await client.post(
            f"{OLLAMA_URL}/api/embeddings",
            json={"model": model, "prompt": text},
            timeout=30.0
        )
        if response.status_code == 200:
            return response.json()["embedding"]
    except Exception as e:
        print(f"  Error getting embedding: {e}")
    return None


async def populate_embeddings(model: str = "nomic-embed-text"):
    """Generate embeddings for all movies."""
    
    # Check if Ollama is running
    print(f"Checking Ollama at {OLLAMA_URL}...")
    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(f"{OLLAMA_URL}/api/tags", timeout=5.0)
            if response.status_code != 200:
                print("❌ Ollama is not responding")
                return
    except Exception:
        print("❌ Cannot connect to Ollama. Is it running?")
        print("   Start with: docker start archive_mcp_ollama")
        return
    
    print("✓ Ollama is running")
    
    # Check if model is available
    print(f"Checking if model '{model}' is available...")
    if not await check_ollama_model(model):
        print(f"❌ Model '{model}' not found")
        print(f"   Pull it with: ollama pull {model}")
        return
    
    print(f"✓ Model '{model}' is available")
    
    # Connect to database
    dsn = os.environ.get("MOVIE_DATABASE_URL", "postgresql://postgres:password@localhost:5432/rabbit3")
    print(f"\nConnecting to database...")
    
    try:
        conn = await asyncpg.connect(dsn)
    except Exception as e:
        print(f"❌ Cannot connect to database: {e}")
        return
    
    print("✓ Connected to database")
    
    # Check if embedding column exists
    has_embedding = await conn.fetchval("""
        SELECT EXISTS (
            SELECT FROM information_schema.columns
            WHERE table_name = 'data_archive_movie_master'
            AND column_name = 'embedding'
        )
    """)
    
    if not has_embedding:
        print("❌ Embedding column doesn't exist")
        print("   Run migration first: psql -d rabbit3 -f migrations/002_add_vector.sql")
        await conn.close()
        return
    
    print("✓ Embedding column exists")
    
    # Get all movies
    rows = await conn.fetch("SELECT id, title, original_title, overview FROM data_archive_movie_master")
    total = len(rows)
    
    if total == 0:
        print("⚠️  No movies in database")
        await conn.close()
        return
    
    print(f"\n🎬 Generating embeddings for {total} movies...\n")
    
    # Generate embeddings
    success_count = 0
    async with httpx.AsyncClient() as client:
        for i, row in enumerate(rows, 1):
            # Combine fields for embedding
            text_parts = []
            if row['title']:
                text_parts.append(row['title'])
            if row['original_title'] and row['original_title'] != row['title']:
                text_parts.append(row['original_title'])
            if row['overview']:
                text_parts.append(row['overview'])
            
            text = " ".join(text_parts)
            
            if not text.strip():
                print(f"⚠️  [{i}/{total}] Skipping movie ID {row['id']} (no text)")
                continue
            
            # Get embedding
            embedding = await get_embedding(client, text, model)
            
            if embedding:
                # Convert list to PostgreSQL vector format: '[1.0, 2.0, 3.0]'
                vector_str = '[' + ','.join(str(x) for x in embedding) + ']'
                
                # Update database
                await conn.execute(
                    "UPDATE data_archive_movie_master SET embedding = $1::vector WHERE id = $2",
                    vector_str, row['id']
                )
                success_count += 1
                title = row['title'][:50] + "..." if len(row['title']) > 50 else row['title']
                print(f"✓ [{i}/{total}] {title}")
            else:
                print(f"✗ [{i}/{total}] Failed: {row['title']}")
    
    await conn.close()
    
    print(f"\n🎉 Done! Generated {success_count}/{total} embeddings")
    
    if success_count < total:
        print(f"⚠️  {total - success_count} movies failed")


async def main():
    parser = argparse.ArgumentParser(description="Generate movie embeddings using Ollama")
    parser.add_argument(
        "--model",
        default="nomic-embed-text",
        choices=["nomic-embed-text", "mxbai-embed-large", "all-minilm"],
        help="Ollama embedding model to use (default: nomic-embed-text)"
    )
    args = parser.parse_args()
    
    print("=" * 60)
    print("Movie Embedding Generator (Ollama)")
    print("=" * 60)
    print(f"Model: {args.model}")
    print("=" * 60)
    print()
    
    await populate_embeddings(args.model)


if __name__ == "__main__":
    asyncio.run(main())
