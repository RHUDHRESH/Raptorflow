# 🔄 Frontend Integration Migration Guide

## Overview

This guide will help you merge the advanced backend features from `main` into your working branch and integrate them with the frontend.

## Current State

- **Your branch**: `claude/app-pricing-evaluation-01RM9vqCWZzTMSEnGmfx6v2s` (basic backend)
- **Main branch**: Has ALL advanced features (memory, performance prediction, enhanced critic/guardian, semantic search, etc.)
- **Goal**: Get all advanced features working with the frontend

---

## 🎯 Migration Steps

### Step 1: Backup Current Work

```bash
# Create a backup branch just in case
git branch backup/pre-merge-$(date +%Y%m%d)

# Commit any uncommitted changes
git add .
git commit -m "Save current state before merge"
```

### Step 2: Merge Main Into Your Branch

```bash
# Fetch latest from origin
git fetch origin

# Merge main into current branch
git merge origin/main

# You may encounter merge conflicts - resolve them:
# 1. Open conflicted files
# 2. Look for <<<<<<< HEAD markers
# 3. Choose which version to keep
# 4. Remove conflict markers
# 5. git add <resolved-file>
# 6. git commit
```

### Step 3: Verify Backend Features

After merge, verify these directories exist:

```bash
ls -la backend/memory/          # Should have 9 files
ls -la backend/semantic/        # Semantic intelligence layer
ls -la backend/language/        # Language optimization
ls -la backend/performance/     # Performance prediction
ls -la backend/meta_learning/   # Meta-learning system
```

Check these files are enhanced:

```bash
wc -l backend/agents/safety/critic_agent.py    # Should be ~823 lines
wc -l backend/agents/safety/guardian_agent.py  # Should be ~944 lines
```

### Step 4: Update Dependencies

```bash
cd backend
pip install -r requirements.txt

# New dependencies from main:
# - chromadb>=0.4.22 (vector database)
# - sentence-transformers>=2.2.2 (embeddings)
# - torch>=2.0.0 (ML models)
```

### Step 5: Setup New Services

#### Redis (if not already running)
```bash
docker run -d -p 6379:6379 redis:latest
```

#### ChromaDB (for semantic memory)
```bash
# Will auto-initialize on first run
# Data stored in backend/chroma_data/
```

#### Supabase Migration
```sql
-- Add workspace_memory table (if not exists)
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

### Step 6: Update Environment Variables

Add to your `.env` file:

```env
# Memory System
REDIS_URL=redis://localhost:6379/0
CHROMADB_PATH=./chroma_data
EMBEDDING_MODEL=sentence-transformers/all-MiniLM-L6-v2

# Performance Prediction
ENABLE_PERFORMANCE_PREDICTION=true
PERFORMANCE_MODEL_PATH=./models/engagement_predictor.pkl

# Language Optimization
ENABLE_LANGUAGE_OPTIMIZATION=true
GRAMMAR_CHECK_ENABLED=true

# Meta Learning
ENABLE_META_LEARNING=true
PATTERN_EXTRACTION_ENABLED=true
```

### Step 7: Test Backend

```bash
# Start backend
cd backend
uvicorn main:app --reload --port 8000

# Test health endpoint
curl http://localhost:8000/health

# Test new memory endpoint
curl -X POST http://localhost:8000/api/v1/memory/remember \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{"workspace_id": "test", "key": "test_key", "value": {"data": "test"}}'
```

### Step 8: Frontend Integration

Now proceed with the 10 prompts to build the frontend!

---

## 🐛 Troubleshooting

### Merge Conflicts

**Common conflicts:**

1. **requirements.txt**: Keep the version from main (has more dependencies)
2. **main.py**: Keep the version from main (has memory initialization)
3. **routers/*.py**: Keep main version (has enhanced endpoints)

**To resolve:**
```bash
# If you want to keep main's version completely:
git checkout --theirs <file>

# If you want to keep your version:
git checkout --ours <file>

# Then:
git add <file>
```

### Import Errors After Merge

```bash
# Reinstall all dependencies
pip install -r backend/requirements.txt --force-reinstall

# If torch fails to install:
pip install torch --index-url https://download.pytorch.org/whl/cpu
```

### Redis Connection Errors

```bash
# Check if Redis is running:
redis-cli ping
# Should return: PONG

# If not running:
docker run -d -p 6379:6379 redis:latest
```

### ChromaDB Errors

```bash
# Remove and reinitialize:
rm -rf backend/chroma_data
# Will auto-create on next run
```

---

## 📊 Feature Checklist

After merge, you should have:

- [x] Memory system (conversation, agent, workspace, semantic)
- [x] Enhanced Critic agent (7-dimensional analysis)
- [x] Enhanced Guardian agent (6 compliance checks)
- [x] Performance prediction API
- [x] Language optimization engine
- [x] Semantic intelligence layer
- [x] Meta-learning system
- [x] Agent memory integration

---

## 🚀 Next Steps

1. Complete merge
2. Verify all features work
3. Proceed with **10 Frontend Integration Prompts**
4. Build amazing UI on top of world-class backend!

---

## 📞 Need Help?

If you encounter issues:

1. Check backend logs: `docker-compose logs -f backend`
2. Check frontend console: Browser DevTools
3. Verify API responses: Use Swagger docs at `http://localhost:8000/api/docs`
4. Test individual endpoints with curl or Postman

---

**Ready to build the future! 🦖**
