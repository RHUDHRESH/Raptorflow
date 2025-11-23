# 🔄 Frontend Integration Migration Guide

## Overview
This guide helps you bring the advanced backend features from `main` onto your working branch and wire them into the frontend.

## Current State
- Working branch: `claude/app-pricing-evaluation-01RM9vqCWZzTMSEnGmfx6v2s`
- `main`: ships memory system, performance prediction, enhanced critic/guardian, semantic/language/meta-learning layers, and expanded routers
- Goal: merge `main`, update env/deps, and integrate via the 10 prompts below

---

## Migration Steps

### 1) Backup and clean slate
```bash
git branch backup/pre-merge-$(date +%Y%m%d)
git status
# commit or stash anything uncommitted before merging
```

### 2) Merge `main` into your branch
```bash
git fetch origin
git checkout claude/app-pricing-evaluation-01RM9vqCWZzTMSEnGmfx6v2s
git merge origin/main
# resolve conflicts, then:
git add <files>
git commit
```

### 3) Verify key directories exist (post-merge)
- `backend/memory/`
- `backend/semantic/`
- `backend/language/`
- `backend/performance/`
- `backend/meta_learning/`

Sanity check enhanced safety agents:
```bash
wc -l backend/agents/safety/critic_agent.py    # ~800+
wc -l backend/agents/safety/guardian_agent.py  # ~900+
```

### 4) Update dependencies
```bash
cd backend
pip install -r requirements.txt
# includes chromadb, sentence-transformers, torch, etc.
```

### 5) Services to have running
- Redis (e.g., `docker run -d -p 6379:6379 redis:latest`)
- ChromaDB local store auto-inits at `backend/chroma_data/`

### 6) Supabase migration (if needed)
Ensure `workspace_memory` table exists:
```sql
CREATE TABLE IF NOT EXISTS workspace_memory (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    workspace_id UUID NOT NULL,
    memory_key VARCHAR(255) NOT NULL,
    memory_type VARCHAR(50),
    value JSONB NOT NULL,
    metadata JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW(),
    embedding vector(384),
    UNIQUE(workspace_id, memory_key)
);
CREATE INDEX IF NOT EXISTS idx_workspace_memory_workspace ON workspace_memory(workspace_id);
CREATE INDEX IF NOT EXISTS idx_workspace_memory_type ON workspace_memory(memory_type);
```

### 7) Env vars (augment your `.env`)
```
# Memory
REDIS_URL=redis://localhost:6379/0
CHROMADB_PATH=./chroma_data
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Performance prediction
ENABLE_PERFORMANCE_PREDICTION=true
PERFORMANCE_MODEL_PATH=./models/engagement_predictor.pkl

# Language optimization / meta-learning
ENABLE_LANGUAGE_OPTIMIZATION=true
GRAMMAR_CHECK_ENABLED=true
ENABLE_META_LEARNING=true
PATTERN_EXTRACTION_ENABLED=true
```

### 8) Smoke test backend
```bash
cd backend
uvicorn main:app --reload --port 8000
curl http://localhost:8000/health
curl -X POST http://localhost:8000/api/v1/memory/remember \
  -H "Authorization: Bearer <token>" \
  -H "Content-Type: application/json" \
  -d '{"workspace_id":"test","key":"ping","value":{"ok":true}}'
```

### 9) Frontend next steps
Proceed with the 10 corrected prompts below to wire up the UI to the advanced backend.

---

## Troubleshooting quick fixes
- **Merge conflicts**: prefer `--theirs` for requirements/routers/main to keep `main` versions.
- **Torch install issues**: `pip install torch --index-url https://download.pytorch.org/whl/cpu`
- **Redis errors**: ensure container running; `redis-cli ping` → `PONG`.
- **Chroma errors**: delete `backend/chroma_data/` to re-init.

---

## Feature checklist after merge
- [ ] Memory system (conversation, agent, workspace, semantic)
- [ ] Enhanced critic (7D analysis) and guardian (compliance)
- [ ] Performance prediction APIs
- [ ] Language optimization and semantic intelligence
- [ ] Meta-learning patterns
- [ ] Agent memory integration

---

## Go build!
Once merged and envs are set, jump into the prompts and wire the frontend to the now world-class backend. 🦖🚀
