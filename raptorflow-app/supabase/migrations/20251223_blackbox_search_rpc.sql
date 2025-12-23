-- Search function for Blackbox Learnings (Strategic Memory)
CREATE OR REPLACE FUNCTION match_blackbox_learnings (
  query_embedding vector(768),
  match_threshold float DEFAULT 0.5,
  match_count int DEFAULT 10
)
RETURNS TABLE (
  id uuid,
  content text,
  learning_type text,
  source_ids uuid[],
  similarity float
)
LANGUAGE plpgsql
AS $$
BEGIN
  RETURN QUERY
  SELECT
    bbl.id,
    bbl.content,
    bbl.learning_type,
    bbl.source_ids,
    1 - (bbl.embedding <=> query_embedding) AS similarity
  FROM blackbox_learnings_industrial bbl
  WHERE 1 - (bbl.embedding <=> query_embedding) > match_threshold
  ORDER BY similarity DESC
  LIMIT match_count;
END;
$$;
