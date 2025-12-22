-- Enable pgvector extension
create extension if not exists vector;

-- Create Skills Table
create table if not exists skills (
  id uuid primary key default gen_random_uuid(),
  name text not null,
  description text,
  instructions text not null,
  type text not null check (type in ('system', 'custom')),
  created_at timestamptz default now(),
  updated_at timestamptz default now()
);

-- Create Muse Assets Table (for RAG)
create table if not exists muse_assets (
  id uuid primary key default gen_random_uuid(),
  content text not null,
  metadata jsonb default '{}'::jsonb,
  embedding vector(768), -- Dimensions for Gemini Text Embedding (Gecko) - verify 768 is correct for 004/005, usually 768 for text-embedding-004
  created_at timestamptz default now()
);

-- Create HNSW index for vector search
create index on muse_assets using hnsw (embedding vector_cosine_ops);

-- LangGraph Checkpointing Tables
-- Reference: https://langchain-ai.github.io/langgraphjs/how-tos/persistence_postgres/
CREATE TABLE IF NOT EXISTS checkpoints (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    parent_checkpoint_id TEXT,
    type TEXT,
    checkpoint BYTEA,
    metadata BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id)
);

CREATE TABLE IF NOT EXISTS checkpoint_blobs (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    channel TEXT NOT NULL,
    version TEXT NOT NULL,
    type TEXT,
    blob BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, channel, version)
);

CREATE TABLE IF NOT EXISTS checkpoint_writes (
    thread_id TEXT NOT NULL,
    checkpoint_ns TEXT NOT NULL DEFAULT '',
    checkpoint_id TEXT NOT NULL,
    task_id TEXT NOT NULL,
    idx INTEGER NOT NULL,
    channel TEXT NOT NULL,
    type TEXT,
    blob BYTEA,
    PRIMARY KEY (thread_id, checkpoint_ns, checkpoint_id, task_id, idx)
);
