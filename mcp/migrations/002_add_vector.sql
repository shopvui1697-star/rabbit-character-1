-- Active: 1757658319975@@127.0.0.1@5432@rabbit3
-- Phase 2: Add pgvector extension and embedding column for semantic search.
-- Run this migration when ready to enable vector similarity search.

-- Step 1: Enable pgvector extension
CREATE EXTENSION IF NOT EXISTS vector;

-- Step 2: Add embedding column
-- Dimension depends on your embedding model:
--   - nomic-embed-text (Ollama): 768
--   - mxbai-embed-large (Ollama): 1024
--   - OpenAI text-embedding-3-small: 1536
ALTER TABLE data_archive_movie_master
    ADD COLUMN IF NOT EXISTS embedding vector(768);  -- Change to match your model

-- Step 3: Create HNSW index for fast approximate nearest-neighbor search
CREATE INDEX IF NOT EXISTS idx_movie_embedding
    ON data_archive_movie_master
    USING hnsw (embedding vector_cosine_ops)
    WITH (m = 16, ef_construction = 64);

-- Step 4 (optional): Full-text search index as fallback
ALTER TABLE data_archive_movie_master
    ADD COLUMN IF NOT EXISTS search_tsv tsvector
    GENERATED ALWAYS AS (
        to_tsvector('simple', coalesce(title, '') || ' ' || coalesce(original_title, '') || ' ' || coalesce(overview, ''))
    ) STORED;

CREATE INDEX IF NOT EXISTS idx_movie_fts ON data_archive_movie_master USING gin (search_tsv);
