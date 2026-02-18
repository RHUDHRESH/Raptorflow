#!/bin/bash
export AUTH_MODE=demo
export ENVIRONMENT=development
python -m uvicorn backend.main:app --host 0.0.0.0 --port 8040
