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
                "prompt": "positive movies"
            }
        )
        query_embedding = response.json()["embedding"]
    
    # Convert list to PostgreSQL vector format: '[1.0, 2.0, 3.0]'
    vector_str = "[" + ",".join(str(x) for x in query_embedding) + "]"
    
    # Search database
    conn = await asyncpg.connect("postgresql://postgres:password@localhost:5432/rabbit3")
    
    rows = await conn.fetch("""
        SELECT title, 1 - (embedding <=> $1::vector) AS similarity
        FROM data_archive_movie_master
        WHERE embedding IS NOT NULL
        ORDER BY embedding <=> $1::vector
        LIMIT 500
    """, vector_str)
    
    print("Top 500 similar movies:")
    for row in rows:
        print(f"  {row['title']}: {row['similarity']:.3f}")
    
    await conn.close()

asyncio.run(test_vector_search())