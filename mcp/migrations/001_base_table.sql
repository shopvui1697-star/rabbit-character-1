-- Phase 1: Base table for movie search (MCP server + backend).
-- Run before 002_add_vector.sql:
--   psql -U postgres -d rabbit3 -f migrations/001_base_table.sql

CREATE TABLE IF NOT EXISTS data_archive_movie_master (
    id              SERIAL PRIMARY KEY,
    title           TEXT,
    original_title  TEXT,
    overview        TEXT,
    release_date    TEXT,
    poster_path     TEXT,
    backdrop_path   TEXT,
    source          TEXT,
    vote_average    DOUBLE PRECISION,
    vote_count      INTEGER DEFAULT 0,
    genre_ids       TEXT,
    product_type    TEXT,
    runtime         INTEGER
);

-- Help Phase 1 ILIKE search and common sort/filter paths
CREATE INDEX IF NOT EXISTS idx_movie_title ON data_archive_movie_master (title);
CREATE INDEX IF NOT EXISTS idx_movie_vote_count ON data_archive_movie_master (vote_count DESC NULLS LAST);
