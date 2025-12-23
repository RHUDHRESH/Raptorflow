create or replace function match_muse_assets (
  query_embedding vector(768),
  match_threshold float,
  match_count int
)
returns table (
  id uuid,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
begin
  return query
  select
    muse_assets.id,
    muse_assets.content,
    muse_assets.metadata,
    1 - (muse_assets.embedding <=> query_embedding) as similarity
  from muse_assets
  where 1 - (muse_assets.embedding <=> query_embedding) > match_threshold
  order by muse_assets.embedding <=> query_embedding
  limit match_count;
end;
$$;
