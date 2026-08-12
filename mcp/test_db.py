"""Quick test script to verify database connection and table structure."""

import asyncio
import os

import asyncpg


async def main():
    dsn = os.environ.get("MOVIE_DATABASE_URL", "postgresql://localhost:5432/rabbit3")
    print(f"Connecting to: {dsn}")
    
    try:
        conn = await asyncpg.connect(dsn)
        print("✓ Connected successfully")
        
        # Check if table exists
        exists = await conn.fetchval(
            "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'data_archive_movie_master')"
        )
        print(f"✓ Table 'data_archive_movie_master' exists: {exists}")
        
        if exists:
            # Count rows
            count = await conn.fetchval("SELECT COUNT(*) FROM data_archive_movie_master")
            print(f"✓ Table has {count} rows")
            
            # Show first row
            if count > 0:
                row = await conn.fetchrow("SELECT * FROM data_archive_movie_master LIMIT 1")
                print(f"✓ Sample row: {dict(row)}")
            else:
                print("⚠ Table is empty — run migrations/001_base_table.sql and insert some data")
        else:
            print("⚠ Table doesn't exist — run migrations/001_base_table.sql")
        
        await conn.close()
        
    except Exception as e:
        print(f"✗ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
