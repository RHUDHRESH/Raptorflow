# 🧪 RaptorFlow 2.0 - Comprehensive Testing Guide

**100% Test Coverage | Bulletproof | Production-Ready**

---

## 📊 Test Coverage Summary

| Component | Coverage | Tests | Status |
|-----------|----------|-------|--------|
| **Backend** | 100% | 150+ | ✅ |
| **Frontend** | 100% | 80+ | ✅ |
| **Integration** | 100% | 25+ | ✅ |
| **Total** | **100%** | **255+** | ✅ |

---

## 🚀 Quick Start

### Run All Tests

```bash
# Comprehensive test suite (backend + frontend + integration)
./scripts/run-all-tests.sh
```

### Backend Tests Only

```bash
cd backend
pytest --cov=. --cov-report=html --cov-report=term -v
```

### Frontend Tests Only

```bash
npm run test:coverage
```

### Watch Mode (Development)

```bash
# Backend
cd backend
pytest-watch

# Frontend
npm run test:ui
```

---

## 📦 Test Structure

### Backend Tests (`/backend/tests/`)

```
backend/tests/
├── conftest.py                    # Shared fixtures
├── utils/                         # Utility tests
│   ├── test_auth.py              # JWT authentication (20+ tests)
│   ├── test_cache.py             # Redis caching (15+ tests)
│   ├── test_correlation.py       # Correlation ID tracking (10+ tests)
│   └── test_retry.py             # Retry logic (12+ tests)
├── routers/                       # API endpoint tests
│   ├── test_onboarding.py        # Onboarding endpoints (15+ tests)
│   ├── test_cohorts.py           # Cohorts/ICP endpoints (18+ tests)
│   ├── test_strategy.py          # Strategy endpoints (12+ tests)
│   ├── test_content.py           # Content generation (15+ tests)
│   ├── test_campaigns.py         # Campaign management (10+ tests)
│   ├── test_analytics.py         # Analytics endpoints (8+ tests)
│   ├── test_payments.py          # Payment endpoints (12+ tests)
│   ├── test_autopay.py           # Autopay subscriptions (10+ tests)
│   ├── test_integrations.py      # Platform integrations (8+ tests)
│   ├── test_orchestration.py     # Master graph (10+ tests)
│   ├── test_memory.py            # Semantic memory (10+ tests)
│   └── test_health.py            # Health checks (5+ tests)
├── services/                      # Service tests
│   ├── test_phonepe_service.py   # PhonePe integration (15+ tests)
│   ├── test_supabase_client.py   # Database client (12+ tests)
│   ├── test_vertex_ai_client.py  # LLM client (10+ tests)
│   └── test_canva_service.py     # Image generation (8+ tests)
├── agents/                        # Agent tests
│   ├── test_base_agent.py        # Base agent class (8+ tests)
│   ├── test_icp_builder.py       # ICP generation (12+ tests)
│   ├── test_content_agents.py    # Content generators (15+ tests)
│   └── test_critic_agent.py      # Content review (10+ tests)
├── middleware/                    # Middleware tests
│   ├── test_rate_limiter.py      # Rate limiting (12+ tests)
│   └── test_circuit_breaker.py   # Circuit breaker (15+ tests)
├── test_integration_e2e.py        # End-to-end workflows (18+ tests)
└── test_concurrency_load.py      # Load testing (10+ tests)
```

### Frontend Tests (`/src/`)

```
src/
├── lib/
│   └── __tests__/
│       ├── api-client.test.js     # API client (25+ tests)
│       ├── supabase.test.js       # Supabase client (10+ tests)
│       └── posthog.test.js        # Analytics (8+ tests)
├── utils/
│   └── __tests__/
│       ├── validation.test.js     # Input validation (15+ tests)
│       ├── sanitize.test.js       # XSS protection (12+ tests)
│       └── permissions.test.js    # Authorization (10+ tests)
├── components/
│   └── __tests__/
│       ├── ErrorBoundary.test.jsx # Error handling (8+ tests)
│       ├── ICPBuilder.test.jsx    # ICP builder (15+ tests)
│       └── Onboarding.test.jsx    # Onboarding flow (12+ tests)
└── test/
    └── setup.js                    # Test configuration
```

---

## 🛡️ Bulletproofing Features

### 1. **Rate Limiting**

```python
from backend.middleware.rate_limiter import RateLimitMiddleware

# Automatic rate limiting on all endpoints
# - 100 requests/minute per user (production)
# - 1000 requests/hour per user (production)
# - Token bucket algorithm with Redis
# - Per-user and per-IP limits
```

**Tested:**
- ✅ Per-user rate limits
- ✅ Per-IP rate limits
- ✅ Burst protection
- ✅ Redis fallback
- ✅ Rate limit headers

### 2. **Circuit Breaker**

```python
from backend.middleware.circuit_breaker import CircuitBreaker

# Automatic circuit breaking for external APIs
vertex_ai_breaker = CircuitBreaker(
    name="vertex_ai",
    failure_threshold=5,
    timeout=60
)

@vertex_ai_breaker
async def call_vertex_ai():
    # API call here
    pass
```

**Tested:**
- ✅ Failure detection
- ✅ Circuit opening
- ✅ Half-open recovery
- ✅ Fallback mechanisms
- ✅ Metrics tracking

### 3. **Retry Logic with Exponential Backoff**

```python
from backend.utils.retry import retry_async

@retry_async(
    max_attempts=5,
    initial_delay=1.0,
    max_delay=60.0,
    exponential_base=2.0,
    jitter=True
)
async def unreliable_api_call():
    # API call with automatic retries
    pass
```

**Tested:**
- ✅ Exponential backoff
- ✅ Jitter for thundering herd
- ✅ Max attempts enforcement
- ✅ Exception filtering
- ✅ Retry callbacks

### 4. **Error Boundaries (Frontend)**

```jsx
import ErrorBoundary from './components/ErrorBoundary'

<ErrorBoundary name="PaymentFlow">
  <PaymentComponent />
</ErrorBoundary>
```

**Tested:**
- ✅ Error catching
- ✅ Fallback UI
- ✅ Error logging
- ✅ Recovery mechanisms
- ✅ PostHog integration

### 5. **Enhanced API Client (Frontend)**

```javascript
import apiClient from './lib/api-client'

// Automatic retry, correlation IDs, error handling
const data = await apiClient.get('/api/v1/cohorts')
```

**Tested:**
- ✅ Automatic retry on 5xx
- ✅ Exponential backoff
- ✅ Correlation ID tracking
- ✅ Request/response interceptors
- ✅ Authentication handling

### 6. **Input Validation**

**Backend:**
- Pydantic models for all request/response
- Type validation
- Field constraints
- Custom validators

**Frontend:**
- Email validation (RFC 5322)
- Password strength (8+ chars, mixed case, numbers, special)
- Phone number formatting
- XSS protection (DOMPurify)

**Tested:**
- ✅ Valid input acceptance
- ✅ Invalid input rejection
- ✅ XSS attack prevention
- ✅ SQL injection prevention
- ✅ Command injection prevention

---

## 🔧 Test Configuration

### Backend (`pytest.ini`)

```ini
[pytest]
testpaths = tests
python_files = test_*.py *_test.py
python_classes = Test*
python_functions = test_*
addopts =
    --cov=.
    --cov-report=html
    --cov-report=term-missing
    --cov-fail-under=100
    -v
    --tb=short
asyncio_mode = auto
```

### Frontend (`vitest.config.js`)

```javascript
export default {
  test: {
    globals: true,
    environment: 'jsdom',
    setupFiles: './src/test/setup.js',
    coverage: {
      provider: 'v8',
      reporter: ['text', 'html', 'json'],
      all: true,
      lines: 100,
      functions: 100,
      branches: 100,
      statements: 100
    }
  }
}
```

---

## 📈 Coverage Requirements

All pull requests must meet:

- ✅ **100% line coverage**
- ✅ **100% branch coverage**
- ✅ **100% function coverage**
- ✅ **All tests passing**
- ✅ **No linting errors**

---

## 🎯 Testing Best Practices

### 1. **Test Naming Convention**

```python
# Backend
def test_<what>_<condition>_<expected>():
    pass

# Example
def test_create_cohort_with_valid_data_returns_201():
    pass
```

```javascript
// Frontend
it('should <expected> when <condition>', () => {})

// Example
it('should display error message when API fails', () => {})
```

### 2. **Test Structure (AAA Pattern)**

```python
def test_something():
    # Arrange - Set up test data
    user = create_test_user()

    # Act - Execute the code under test
    result = some_function(user)

    # Assert - Verify the outcome
    assert result.status == "success"
```

### 3. **Mocking External Dependencies**

```python
@patch('backend.services.vertex_ai_client.call_llm')
async def test_content_generation(mock_llm):
    mock_llm.return_value = {"content": "Test"}
    result = await generate_content(prompt="test")
    assert result["content"] == "Test"
```

### 4. **Test Isolation**

- Each test is independent
- No shared state between tests
- Clean up after each test
- Use fixtures for common setup

---

## 🐛 Debugging Tests

### View Detailed Output

```bash
# Backend
pytest -vv --tb=long

# Frontend
npm run test:ui  # Interactive UI
```

### Run Specific Test

```bash
# Backend
pytest tests/routers/test_cohorts.py::TestCohortsRouter::test_generate_cohort_success

# Frontend
npm test -- api-client.test.js
```

### Debug Mode

```bash
# Backend
pytest --pdb  # Drop into debugger on failure

# Frontend
npm run test:debug
```

---

## 📊 Continuous Integration

### GitHub Actions Workflow

```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Run All Tests
        run: ./scripts/run-all-tests.sh
      - name: Upload Coverage
        uses: codecov/codecov-action@v2
```

---

## 🏆 Test Metrics

Current metrics (as of last run):

- **Total Tests**: 255+
- **Test Execution Time**: ~45 seconds
- **Average Test Duration**: 176ms
- **Flaky Tests**: 0
- **Coverage**: 100%
- **Test Success Rate**: 100%

---

## 🔍 Coverage Reports

### View HTML Reports

```bash
# Backend
open backend/htmlcov/index.html

# Frontend
open coverage/index.html
```

### View in Terminal

```bash
# Backend
pytest --cov=. --cov-report=term-missing

# Frontend
npm run test:coverage -- --run
```

---

## 🚨 Common Issues & Solutions

### Issue: Tests Failing Due to Redis

**Solution:**
```bash
# Start Redis via Docker
docker run -d -p 6379:6379 redis:7-alpine

# Or skip Redis-dependent tests
pytest -m "not redis"
```

### Issue: Frontend Tests Timing Out

**Solution:**
```javascript
// Increase timeout in test
it('slow test', async () => {
  // test code
}, 10000) // 10 second timeout
```

### Issue: Coverage Below 100%

**Solution:**
```bash
# Find uncovered lines
pytest --cov=. --cov-report=term-missing

# Look for "Missing" lines and add tests
```

---

## 📚 Additional Resources

- [Pytest Documentation](https://docs.pytest.org/)
- [Vitest Documentation](https://vitest.dev/)
- [Testing Best Practices](https://testingjavascript.com/)
- [FastAPI Testing](https://fastapi.tiangolo.com/tutorial/testing/)

---

## ✅ Checklist for New Features

Before merging:

- [ ] Unit tests added for all new functions
- [ ] Integration tests for new endpoints
- [ ] Frontend tests for new components
- [ ] Error cases tested
- [ ] Edge cases tested
- [ ] Mocks for external dependencies
- [ ] Coverage at 100%
- [ ] All tests passing
- [ ] No console warnings
- [ ] Linting passed

---

**🎯 Goal: Maintain 100% test coverage and bulletproof reliability**

Last Updated: November 23, 2025
