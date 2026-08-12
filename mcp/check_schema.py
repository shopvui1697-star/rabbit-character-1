"""Check the actual schema of data_archive_movie_master table."""

import asyncio
import os
import asyncpg


async def main():
    dsn = os.environ.get("MOVIE_DATABASE_URL", "postgresql://postgres:password@localhost:5432/rabbit3")
    print(f"Connecting to: {dsn.replace(':password@', ':***@')}")
    
    try:
        conn = await asyncpg.connect(dsn)
        print("✓ Connected successfully\n")
        
        # Check if table exists
        exists = await conn.fetchval("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_name = 'data_archive_movie_master'
            )
        """)
        
        if not exists:
            print("❌ Table 'data_archive_movie_master' does not exist")
            print("\nCreate it with:")
            print("  psql -d rabbit3 -f migrations/001_base_table.sql")
            await conn.close()
            return
        
        print("✓ Table 'data_archive_movie_master' exists\n")
        
        # Get actual columns
        columns = await conn.fetch("""
            SELECT column_name, data_type, is_nullable
            FROM information_schema.columns
            WHERE table_name = 'data_archive_movie_master'
            ORDER BY ordinal_position
        """)
        
        print("Actual table schema:")
        print("-" * 60)
        for col in columns:
            nullable = "NULL" if col['is_nullable'] == 'YES' else "NOT NULL"
            print(f"  {col['column_name']:<20} {col['data_type']:<20} {nullable}")
        
        print("\n" + "-" * 60)
        
        # Expected columns
        expected = [
            'id', 'title', 'original_title', 'overview', 'release_date',
            'poster_path', 'backdrop_path', 'source_url', 'vote_average',
            'vote_count', 'genre_ids', 'product_type', 'runtime'
        ]
        
        actual = [col['column_name'] for col in columns]
        
        missing = set(expected) - set(actual)
        extra = set(actual) - set(expected)
        
        if missing:
            print(f"\n⚠️  Missing columns: {', '.join(missing)}")
        if extra:
            print(f"\n✓ Extra columns (OK): {', '.join(extra)}")
        if not missing and not extra:
            print("\n✓ Schema matches expected structure perfectly!")
        
        # Check row count
        count = await conn.fetchval("SELECT COUNT(*) FROM data_archive_movie_master")
        print(f"\n✓ Table has {count} rows")
        
        if count > 0:
            # Show sample row
            row = await conn.fetchrow("SELECT * FROM data_archive_movie_master LIMIT 1")
            print(f"\nSample row:")
            for key, value in dict(row).items():
                display_value = str(value)[:50] + "..." if len(str(value)) > 50 else value
                print(f"  {key}: {display_value}")
        
        await conn.close()
        
    except asyncpg.InvalidPasswordError:
        print("❌ Authentication failed - check username/password in MOVIE_DATABASE_URL")
    except asyncpg.InvalidCatalogNameError:
        print("❌ Database 'rabbit3' does not exist")
        print("\nCreate it with:")
        print("  createdb rabbit3")
    except Exception as e:
        print(f"❌ Error: {e}")


if __name__ == "__main__":
    asyncio.run(main())
