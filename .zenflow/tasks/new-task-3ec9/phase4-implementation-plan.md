# Phase 4 Implementation Plan: BCM Generation & Storage

## Overview
This phase implements the Business Context Manifest (BCM) generation, compression, tiered storage, and API endpoints. It consists of 14 concrete tasks organized into 5 implementation areas.

## Phase 4 Tasks (14 tasks total)

### Area 1: BCM Extraction & Compression (4 tasks)

#### Task 4.1.1: Complete BCMReducer Foundation Extraction
**File**: `backend/integration/bcm_reducer.py`
**Objective**: Ensure `_extract_foundation()` method properly extracts company profile data
**Subtasks**:
- Verify foundation extraction handles all 23 onboarding steps
- Add validation for required foundation fields
- Add unit tests for foundation extraction
**Acceptance Criteria**:
- Foundation extraction covers company_profile, intelligence, and foundation sections
- Missing fields logged with warnings
- Unit tests achieve >90% coverage

#### Task 4.1.2: Implement ICP Extraction Method
**File**: `backend/integration/bcm_reducer.py`
**Objective**: Add `_extract_icps()` method to extract ICP data from onboarding
**Subtasks**:
- Extract ICPs from `business_context['intelligence']['icps']`
- Add ICP validation (name, description, attributes required)
- Add ICP prioritization (primary, secondary)
- Add error handling for missing ICP data
**Acceptance Criteria**:
- Extracts up to 3 ICPs with full attributes
- Validates ICP structure and logs warnings for invalid data
- Returns prioritized ICP list

#### Task 4.1.3: Implement Competitive Intelligence Extraction
**File**: `backend/integration/bcm_reducer.py`
**Objective**: Add `_extract_competitive()` method for competitive analysis data
**Subtasks**:
- Extract competitors from onboarding steps 7-8
- Add competitive positioning data
- Add market landscape analysis
- Add competitive advantage statements
**Acceptance Criteria**:
- Extracts competitor profiles with strengths/weaknesses
- Includes positioning relative to competitors
- Handles missing competitive data gracefully

#### Task 4.1.4: Implement Messaging & Positioning Extraction
**File**: `backend/integration/bcm_reducer.py`
**Objective**: Add `_extract_messaging()` method for brand messaging data
**Subtasks**:
- Extract value propositions from onboarding
- Add brand voice and tone guidelines
- Add messaging pillars and key messages
- Add communication channel preferences
**Acceptance Criteria**:
- Extracts comprehensive messaging framework
- Includes brand voice attributes
- Validates message structure and consistency

### Area 2: Token Compression & Checksum (2 tasks)

#### Task 4.2.1: Implement Token Counting with TikToken
**File**: `backend/integration/bcm_reducer.py`
**Objective**: Add token counting to ensure BCM stays under 1200 tokens
**Subtasks**:
- Install and configure tiktoken for GPT-4 tokenization
- Add `_count_tokens()` method
- Add token counting to extraction methods
- Add logging for token usage per section
**Acceptance Criteria**:
- Accurate token counting using GPT-4 tokenizer
- Token usage logged for each extraction step
- Token budget tracking (1200 token limit)

#### Task 4.2.2: Implement Compression Algorithm
**File**: `backend/integration/bcm_reducer.py`
**Objective**: Add `_compress_to_budget()` method to reduce tokens while preserving meaning
**Subtasks**:
- Implement intelligent text compression (summarization, pruning)
- Add priority-based compression (ICPs > messaging > competitive)
- Add semantic preservation checks
- Add compression statistics logging
**Acceptance Criteria**:
- Compresses BCM to ≤1200 tokens
- Preserves critical business information
- Maintains semantic coherence
- Logs compression ratio and preserved elements

#### Task 4.2.3: Add Checksum Calculation
**File**: `backend/integration/bcm_reducer.py`
**Objective**: Add `_compute_checksum()` method for data integrity
**Subtasks**:
- Implement SHA256 checksum calculation
- Add checksum to BCM manifest
- Add checksum verification method
- Add checksum validation in storage
**Acceptance Criteria**:
- SHA256 checksum computed for all BCMs
- Checksum stored in manifest metadata
- Verification detects data corruption

### Area 3: Tiered Redis Storage (3 tasks)

#### Task 4.3.1: Create BCM Redis Storage Module
**File**: `backend/redis/bcm_storage.py`
**Objective**: Create Redis storage client with tiered caching
**Subtasks**:
- Create BCMStorage class with connection pooling
- Implement tier0 (hot), tier1 (warm), tier2 (cold) storage
- Add TTL management (1h, 24h, 7d)
- Add error handling with retry logic
**Acceptance Criteria**:
- Connection pooling configured for Redis
- Three storage tiers with appropriate TTLs
- Retry logic for transient failures
- Comprehensive error logging

#### Task 4.3.2: Implement BCM Storage Methods
**File**: `backend/redis/bcm_storage.py`
**Objective**: Add storage and retrieval methods with tier fallback
**Subtasks**:
- Implement `store_bcm()` method (stores in all tiers)
- Implement `get_bcm()` method (tier0 → tier1 → tier2 fallback)
- Add cache hit/miss logging
- Add cache invalidation methods
**Acceptance Criteria**:
- BCM stored in all three tiers simultaneously
- Retrieval tries tiers in order with fallback
- Cache performance metrics logged
- Invalidation removes from all tiers

#### Task 4.3.3: Add Redis Connection Management
**File**: `backend/redis/bcm_storage.py`
**Objective**: Ensure robust Redis connection handling
**Subtasks**:
- Add connection health checks
- Implement connection retry with exponential backoff
- Add connection pooling configuration
- Add graceful degradation on Redis failure
**Acceptance Criteria**:
- Health checks detect connection issues
- Automatic reconnection on failure
- Connection pooling optimizes performance
- Graceful fallback to database on Redis failure

### Area 4: Supabase Storage & Versioning (3 tasks)

#### Task 4.4.1: Create BCM Storage Migration
**File**: `supabase/migrations/003_bcm_storage.sql`
**Objective**: Create database table for BCM persistence
**Subtasks**:
- Create `business_context_manifests` table
- Add version columns (major, minor, patch)
- Add checksum and metadata columns
- Add appropriate indexes
- Add RLS policies for workspace isolation
**Acceptance Criteria**:
- Table created with all required columns
- Indexes optimize query performance
- RLS policies enforce workspace isolation
- Unique constraints prevent duplicate versions

#### Task 4.4.2: Implement Semantic Versioning Logic
**File**: `backend/services/bcm_service.py`
**Objective**: Add version management for BCM
**Subtasks**:
- Implement semantic versioning (major.minor.patch)
- Add version increment logic
- Add version conflict detection
- Add version history tracking
**Acceptance Criteria**:
- Semantic versioning follows semver spec
- Version increments based on change type
- Version conflicts detected and resolved
- Complete version history maintained

#### Task 4.4.3: Add Database Storage Methods
**File**: `backend/services/bcm_service.py`
**Objective**: Add Supabase storage operations
**Subtasks**:
- Implement `store_bcm_supabase()` method
- Implement `get_bcm_supabase()` method
- Add version conflict resolution
- Add data integrity checks
**Acceptance Criteria**:
- BCM stored with version and checksum
- Retrieval by workspace_id and version
- Conflict resolution preserves latest version
- Data integrity validated on storage/retrieval

### Area 5: BCM Service & API Endpoints (2 tasks)

#### Task 4.5.1: Create BCM Service Orchestrator
**File**: `backend/services/bcm_service.py`
**Objective**: Create service layer orchestrating BCM operations
**Subtasks**:
- Create BCMService class with dependency injection
- Implement `create_bcm()` method (reduce → compress → store)
- Implement `get_bcm()` method (cache → database fallback)
- Implement `rebuild_bcm()` method
- Add comprehensive error handling
**Acceptance Criteria**:
- End-to-end BCM creation pipeline
- Intelligent caching with fallback
- Rebuild capability from source data
- Error handling with detailed logging

#### Task 4.5.2: Create BCM API Endpoints
**File**: `backend/api/v1/context.py`
**Objective**: Add REST API endpoints for BCM management
**Subtasks**:
- Add `GET /api/v1/context/manifest` endpoint
- Add `POST /api/v1/context/rebuild` endpoint
- Add `GET /api/v1/context/version-history` endpoint
- Add `GET /api/v1/context/export` endpoint
- Add authentication and rate limiting
**Acceptance Criteria**:
- All endpoints functional with proper responses
- Authentication required for all operations
- Rate limiting prevents abuse
- Comprehensive error responses

## Task Dependencies

### Critical Path
1. **4.1.1 → 4.1.2 → 4.1.3 → 4.1.4** (Extraction methods must be complete)
2. **4.2.1 → 4.2.2 → 4.2.3** (Token counting before compression before checksum)
3. **4.3.1 → 4.3.2 → 4.3.3** (Storage module before methods before connection management)
4. **4.4.1 → 4.4.2 → 4.4.3** (Database before versioning before storage methods)
5. **4.5.1 → 4.5.2** (Service layer before API endpoints)

### Parallel Execution
- Tasks 4.1.x can run in parallel with 4.3.x and 4.4.x
- Tasks 4.2.x depend on 4.1.x completion
- Tasks 4.5.x depend on all previous areas

## Timeline (7 days)

### Day 1: Foundation Extraction
- Task 4.1.1: Complete BCMReducer Foundation Extraction
- Task 4.1.2: Implement ICP Extraction Method

### Day 2: Complete Extraction & Compression
- Task 4.1.3: Implement Competitive Intelligence Extraction
- Task 4.1.4: Implement Messaging & Positioning Extraction
- Task 4.2.1: Implement Token Counting with TikToken

### Day 3: Compression & Checksum
- Task 4.2.2: Implement Compression Algorithm
- Task 4.2.3: Add Checksum Calculation

### Day 4: Redis Storage
- Task 4.3.1: Create BCM Redis Storage Module
- Task 4.3.2: Implement BCM Storage Methods
- Task 4.3.3: Add Redis Connection Management

### Day 5: Database Storage
- Task 4.4.1: Create BCM Storage Migration
- Task 4.4.2: Implement Semantic Versioning Logic
- Task 4.4.3: Add Database Storage Methods

### Day 6: Service Layer
- Task 4.5.1: Create BCM Service Orchestrator

### Day 7: API Endpoints
- Task 4.5.2: Create BCM API Endpoints
- Integration testing and bug fixes

## Verification Criteria

### Functional Requirements
- [ ] BCM generation produces valid manifest under 1200 tokens
- [ ] Compression preserves critical business information
- [ ] Tiered storage provides appropriate cache hit rates
- [ ] Versioning maintains complete history
- [ ] API endpoints respond correctly with proper authentication

### Performance Requirements
- [ ] BCM generation < 5 seconds (p95)
- [ ] Redis retrieval < 50ms (tier0), < 100ms (tier1), < 200ms (tier2)
- [ ] Database retrieval < 300ms
- [ ] API response times < 200ms (cached), < 500ms (uncached)

### Quality Requirements
- [ ] Unit test coverage > 90% for BCM components
- [ ] Integration tests cover end-to-end flows
- [ ] Error handling covers all failure scenarios
- [ ] Logging provides sufficient debugging information

## Risk Mitigation

### Technical Risks
- **Token budget exceeded**: Implement aggressive compression with semantic preservation
- **Redis connection failure**: Graceful fallback to database with retry logic
- **Compression loses meaning**: Add semantic validation and manual review checkpoints
- **Version conflicts**: Implement conflict detection and resolution strategies

### Operational Risks
- **Cache stampede**: Implement request coalescing and rate limiting
- **Storage costs**: Monitor Redis memory usage and implement cleanup policies
- **Data corruption**: Checksum validation and automatic recovery procedures

## Success Metrics

### Technical Metrics
- BCM generation success rate: >99.5%
- Average token count: ≤1100 (10% buffer)
- Cache hit rate: >85% (tier0), >95% (tier0+tier1)
- API response time p95: <200ms (cached), <500ms (uncached)

### Business Metrics
- BCM freshness: <7 days for 90% of workspaces
- BCM rebuild success rate: >98%
- User satisfaction with BCM quality: >4.0/5.0
- Feature adoption rate with BCM integration: >80%
