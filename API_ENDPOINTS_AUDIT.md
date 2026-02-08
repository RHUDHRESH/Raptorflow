# RaptorFlow API Endpoints - Comprehensive Audit

## Summary
**Total Endpoints Found: 50+ across 3 separate services**

---

## 1. Main Backend API (FastAPI)
**Location:** `backend/api/v1/` + `backend/api/system.py`
**Base URL:** `http://localhost:8000/api`

### System Endpoints (2)
| Method | Path | File | Description |
|--------|------|------|-------------|
| GET | `/` | system.py:16 | Root endpoint - service info |
| GET | `/health` | system.py:28 | Health check with DB + Muse status |

### Workspaces (3)
| Method | Path | File | Description |
|--------|------|------|-------------|
| POST | `/workspaces/` | workspaces.py:71 | Create workspace |
| GET | `/workspaces/{id}` | workspaces.py:105 | Get workspace by ID |
| PATCH | `/workspaces/{id}` | workspaces.py:124 | Update workspace |

### Campaigns (5)
| Method | Path | File | Description |
|--------|------|------|-------------|
| GET | `/campaigns/` | campaigns.py:97 | List campaigns |
| POST | `/campaigns/` | campaigns.py:116 | Create campaign |
| GET | `/campaigns/{id}` | campaigns.py:143 | Get campaign |
| PATCH | `/campaigns/{id}` | campaigns.py:169 | Update campaign |
| DELETE | `/campaigns/{id}` | campaigns.py:208 | Delete campaign |

### Moves (4)
| Method | Path | File | Description |
|--------|------|------|-------------|
| GET | `/moves/` | moves.py:120 | List moves |
| POST | `/moves/` | moves.py:178 | Create move |
| PATCH | `/moves/{id}` | moves.py:227 | Update move |
| DELETE | `/moves/{id}` | moves.py:299 | Delete move |

### Foundation (2)
| Method | Path | File | Description |
|--------|------|------|-------------|
| GET | `/foundation/` | foundation.py:60 | Get foundation data |
| PUT | `/foundation/` | foundation.py:81 | Save foundation data |

### Context/BCM (4)
| Method | Path | File | Description |
|--------|------|------|-------------|
| GET | `/context/` | context.py:72 | Get latest BCM |
| POST | `/context/rebuild` | context.py:97 | Rebuild BCM |
| POST | `/context/seed` | context.py:122 | Seed BCM from JSON |
| GET | `/context/versions` | context.py:142 | List BCM versions |

### Muse (2)
| Method | Path | File | Description |
|--------|------|------|-------------|
| GET | `/muse/health` | muse.py:58 | Muse health check |
| POST | `/muse/generate` | muse.py:70 | Generate AI content |

**Main API Total: 22 endpoints**

---

## 2. Cloud Scraper Services

### A. Production Scraper Service
**File:** `cloud-scraper/production_service.py`
**Port:** 8081

| Method | Path | Line | Description |
|--------|------|------|-------------|
| GET | `/health` | 29 | Health check |
| POST | `/scrape/production` | 40 | Production scraping |
| GET | `/production/analytics` | 80 | Get analytics |
| POST | `/production/strategy` | 93 | Update strategy |
| GET | `/production/strategies` | 120 | List strategies |

### B. Free Web Search Service
**File:** `cloud-scraper/free_web_search.py`
**Port:** 8084

| Method | Path | Line | Description |
|--------|------|------|-------------|
| GET | `/search` | 509 | Free web search |
| GET | `/search/engines` | 539 | List search engines |
| GET | `/health` | 560 | Health check |

### C. Enhanced Scraper Service
**File:** `cloud-scraper/enhanced_scraper_service.py`
**Port:** Unknown

| Method | Path | Description |
|--------|------|-------------|
| Various | Various | 11+ endpoints (OCR, scraping, etc.) |

### D. Production Search Service
**File:** `cloud-scraper/production_search_service.py`

| Method | Path | Description |
|--------|------|-------------|
| Various | Various | 5+ endpoints |

### E. Ultra Fast Scraper
**File:** `cloud-scraper/ultra_fast_scraper.py`

| Method | Path | Description |
|--------|------|-------------|
| Various | Various | 5+ endpoints |

### F. Scraper Service
**File:** `cloud-scraper/scraper_service.py`

| Method | Path | Description |
|--------|------|-------------|
| Various | Various | 4+ endpoints |

### G. Visual Intelligence Extractor
**File:** `cloud-scraper/visual_intelligence_extractor.py`

| Method | Path | Description |
|--------|------|-------------|
| Various | Various | 2+ endpoints |

**Cloud Scraper Total: 35+ endpoints across 7 services**

---

## 3. Frontend API Services
**Location:** `src/services/*.service.ts`

These map to the main backend API:

| Service | Methods | Backend Endpoints Used |
|---------|---------|------------------------|
| campaigns.service.ts | list, create, get, update, delete | GET/POST/PATCH/DELETE /campaigns |
| workspaces.service.ts | create, get, update | POST/GET/PATCH /workspaces |
| moves.service.ts | list, create, update, delete | GET/POST/PATCH/DELETE /moves |
| foundation.service.ts | get, save | GET/PUT /foundation |
| bcm.service.ts | get, rebuild, seed, listVersions | GET/POST /context/* |
| muse.service.ts | health, generate | GET/POST /muse/* |
| cohorts.service.ts | list, create, update, remove | Uses foundation endpoints |

---

## Issues Found

### 1. Multiple Separate FastAPI Instances
- **Problem:** 7+ separate FastAPI services in cloud-scraper/
- **Impact:** Port conflicts, resource waste, maintenance nightmare
- **Solution:** Consolidate into single scraper service or microservices with gateway

### 2. Mock/Fallback Code Remaining
- **File:** `scraper_service.py:84-150` - Mock Google Cloud clients
- **File:** `free_web_search.py` - Try/except blocks for optional deps (lines 35-41)
- **Solution:** Remove mocks, make dependencies required

### 3. Duplicate Scraper Logic
- Multiple scraper services with overlapping functionality
- `production_scraper.py`, `enhanced_scraper_service.py`, `ultra_fast_scraper.py`
- **Solution:** Consolidate to single scraper with strategy pattern

### 4. Missing API Documentation
- No OpenAPI specs for cloud-scraper services
- No unified API documentation

### 5. Frontend HTTP Client
- **File:** `src/services/http.ts` - Centralized API client using `/api/proxy/v1`
- All frontend services use this consistently ✓

---

## Recommended Actions

### Priority 1: Consolidate Scraper Services
Merge these into single service:
- production_service.py
- enhanced_scraper_service.py
- ultra_fast_scraper.py
- scraper_service.py

### Priority 2: Remove Mock Implementations
- Remove MockStorageClient, MockPubSubClient, etc.
- Make Google Cloud dependencies required

### Priority 3: Standardize Ports
Document and standardize:
- Main API: 8000
- Scraper Service: 8080
- Search Service: 8084

### Priority 4: Add API Gateway
Consider adding Kong/nginx to route:
- `/api/*` → Main backend (8000)
- `/scraper/*` → Scraper service (8080)
- `/search/*` → Search service (8084)

---

## Files to Clean Up

### Delete/Merge (Duplicates):
- `cloud-scraper/enhanced_scraper_service.py` → Merge into production_service.py
- `cloud-scraper/ultra_fast_scraper.py` → Merge into production_service.py  
- `cloud-scraper/scraper_service.py` → Merge into production_service.py
- Multiple validation DB files (*.db)
- Multiple test scripts with similar functionality

### Remove Mocks:
- Lines 84-150 in `scraper_service.py`
- Optional import fallbacks in `free_web_search.py`
- Optional import fallbacks in `enhanced_scraper_service.py`

---

## Current Status

✅ Main Backend API: Cleaned up (mocks removed, consolidated to /api prefix)
⚠️ Cloud Scraper: Needs consolidation (7 services → 1-2 services)
✅ Frontend Services: Well organized, all use consistent http.ts client

**Total Endpoints to Maintain: 50+**
**Services to Consolidate: 7 → 2**
**Mock Implementations to Remove: 5+ files**
