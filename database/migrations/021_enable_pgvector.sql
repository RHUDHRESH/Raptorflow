-- Enable pgvector extension for embeddings
-- Required for semantic memory and vector search features

CREATE EXTENSION IF NOT EXISTS vector;

-- Verify extension is installed
DO $$
BEGIN
  IF NOT EXISTS (
    SELECT 1 FROM pg_extension WHERE extname = 'vector'
  ) THEN
    RAISE EXCEPTION 'Failed to enable vector extension';
  END IF;
END $$;
