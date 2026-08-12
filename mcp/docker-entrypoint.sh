#!/bin/bash
set -euo pipefail

POSTGRES_HOST="${POSTGRES_HOST:-postgres}"
POSTGRES_USER="${POSTGRES_USER:-postgres}"
POSTGRES_PASSWORD="${POSTGRES_PASSWORD:-password}"
POSTGRES_DB="${POSTGRES_DB:-rabbit3}"
OLLAMA_HOST="${OLLAMA_HOST:-ollama}"
EMBEDDING_MODEL="${EMBEDDING_MODEL:-nomic-embed-text}"

export MOVIE_DATABASE_URL="${MOVIE_DATABASE_URL:-postgresql://${POSTGRES_USER}:${POSTGRES_PASSWORD}@${POSTGRES_HOST}:5432/${POSTGRES_DB}}"
export OLLAMA_URL="${OLLAMA_URL:-http://${OLLAMA_HOST}:11434}"
export PGPASSWORD="${POSTGRES_PASSWORD}"

wait_for_postgres() {
  echo "Waiting for PostgreSQL at ${POSTGRES_HOST}..."
  until pg_isready -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" >/dev/null 2>&1; do
    sleep 1
  done
  echo "PostgreSQL is ready"
}

wait_for_ollama() {
  echo "Waiting for Ollama at ${OLLAMA_URL}..."
  until curl -sf "${OLLAMA_URL}/api/tags" >/dev/null; do
    sleep 2
  done
  echo "Ollama is ready"
}

ensure_embedding_model() {
  if curl -sf "${OLLAMA_URL}/api/tags" | grep -q "\"name\":\"${EMBEDDING_MODEL}"; then
    echo "Model '${EMBEDDING_MODEL}' is already available"
    return
  fi

  echo "Pulling model '${EMBEDDING_MODEL}'..."
  curl -sf "${OLLAMA_URL}/api/pull" \
    -H "Content-Type: application/json" \
    -d "{\"name\":\"${EMBEDDING_MODEL}\"}" >/dev/null
  echo "Model '${EMBEDDING_MODEL}' is ready"
}

run_migration() {
  echo "Applying vector migration..."
  psql -h "${POSTGRES_HOST}" -U "${POSTGRES_USER}" -d "${POSTGRES_DB}" \
    -f migrations/002_add_vector.sql
}

run_embed() {
  wait_for_postgres
  wait_for_ollama
  ensure_embedding_model
  run_migration
  exec python generate_embeddings.py --model "${EMBEDDING_MODEL}"
}

case "${1:-embed}" in
  embed)
    run_embed
    ;;
  migrate)
    wait_for_postgres
    run_migration
    ;;
  check)
    wait_for_postgres
    exec python check_schema.py
    ;;
  shell)
    exec bash
    ;;
  *)
    exec "$@"
    ;;
esac
