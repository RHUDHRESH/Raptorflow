# Raptorflow Backend - Search Module Only

This is a minimal backend containing only the working search functionality.

## What's Included

- **Search Module**: `core/search_native.py` - Functional search using Brave Search API and DuckDuckGo fallbacks
- **Configuration**: `core/config.py` - Minimal configuration for search
- **Secrets**: `core/secrets.py` - GCP Secret Manager integration

## What Was Removed

All fake/non-functional backend modules have been removed:
- Agent systems
- Onboarding modules
- Skills systems
- Vector databases
- ML pipelines
- Complex orchestrators
- Mock APIs

## Usage

```python
from core.search_native import NativeSearch

search = NativeSearch()
results = await search.query("ice cream", limit=5)
await search.close()
```

## Installation

```bash
pip install -r requirements.txt
```

## Environment Variables

- `BRAVE_SEARCH_API_KEY`: Optional Brave Search API key
- `GCP_PROJECT_ID`: GCP project ID for Secret Manager
