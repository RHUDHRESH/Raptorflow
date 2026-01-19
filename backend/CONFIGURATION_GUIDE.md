# Raptorflow Backend Configuration Guide

## Overview

Raptorflow backend has been simplified from 481 lines to ~389 lines with only essential configuration variables. This guide explains the new configuration system and how to use it effectively.

## Configuration System Architecture

### Core Components

1. **EssentialConfig** - Main configuration class with 20-30 core settings
2. **RedisRateLimiter** - Redis-based rate limiting with configurable limits
3. **Configuration Health Checks** - API endpoints for monitoring configuration
4. **Hot Reload Support** - Configuration change detection and reloading

### Key Features

- ✅ **Simplified Configuration**: Only 20 essential environment variables
- ✅ **Redis-based Rate Limiting**: Distributed rate limiting with configurable limits
- ✅ **Environment Validation**: Automatic validation of required settings
- ✅ **Hot Reload**: Configuration changes detected and applied without restart
- ✅ **Health Monitoring**: API endpoints for configuration health status
- ✅ **Type Safety**: Pydantic-based configuration with type checking

## Environment Variables

### Required Variables

| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `GOOGLE_API_KEY` | Google Cloud API key | None | `AIzaSy...` |
| `GOOGLE_PROJECT_ID` | Google Cloud project ID | None | `my-project-123` |
| `SECRET_KEY` | JWT secret key | `your-secret-key-change-in-production` | `super-secret-key` |

### Optional Variables

#### Basic Settings
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `APP_NAME` | Application name | `Raptorflow Backend` | `My Raptorflow` |
| `ENVIRONMENT` | Environment type | `development` | `production` |
| `DEBUG` | Debug mode | `false` | `true` |
| `HOST` | Server host | `0.0.0.0` | `127.0.0.1` |
| `PORT` | Server port | `8000` | `8080` |

#### Database
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `DATABASE_URL` | Database connection string | `sqlite:///./raptorflow.db` | `postgresql://user:pass@localhost/db` |

#### Redis
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `REDIS_URL` | Redis connection string | `redis://localhost:6379/0` | `redis://user:pass@localhost:6379/0` |
| `REDIS_KEY_PREFIX` | Redis key prefix | `raptorflow:` | `myapp:` |

#### LLM Configuration
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `LLM_PROVIDER` | LLM provider | `google` | `openai` |
| `GOOGLE_REGION` | Google Cloud region | `us-central1` | `europe-west1` |

#### CORS
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `CORS_ORIGINS` | Allowed CORS origins | `http://localhost:3000` | `https://app.example.com` |

#### Agent Settings
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `AGENT_TIMEOUT_SECONDS` | Agent execution timeout | `120` | `300` |
| `MAX_TOKENS_PER_REQUEST` | Max LLM tokens per request | `8192` | `16384` |

#### Rate Limiting
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `RATE_LIMIT_ENABLED` | Enable rate limiting | `true` | `false` |
| `RATE_LIMIT_PER_MINUTE` | Requests per minute per user | `60` | `120` |
| `RATE_LIMIT_PER_HOUR` | Requests per hour per user | `1000` | `5000` |

#### Monitoring
| Variable | Description | Default | Example |
|----------|-------------|----------|---------|
| `LOG_LEVEL` | Logging level | `INFO` | `DEBUG` |
| `SENTRY_DSN` | Sentry error tracking DSN | None | `https://...@sentry.io/...` |

## Configuration API Endpoints

### Health Check
```http
GET /api/v1/config/health
```

Returns configuration system health status including:
- Configuration loaded status
- Redis connection status
- Validation results
- Environment details

### Configuration Status
```http
GET /api/v1/config/status
```

Returns current configuration status:
- Environment
- Configuration hash
- Change detection status
- Validation errors

### Configuration Reload
```http
POST /api/v1/config/reload
```

Reloads configuration from environment variables:
- Validates new configuration
- Updates rate limiter if needed
- Returns success/failure status

### Rate Limit Statistics
```http
GET /api/v1/config/rate-limit/stats/{user_id}?endpoint=api
```

Returns rate limiting statistics for a user:
- Current usage
- Remaining requests
- Reset times
- Limits

### Reset Rate Limit
```http
POST /api/v1/config/rate-limit/reset/{user_id}?endpoint=api
```

Resets rate limiting for a specific user and endpoint.

## Rate Limiting System

### Architecture

The rate limiting system uses Redis with a sliding window algorithm:

1. **Minute Window**: Tracks requests per minute
2. **Hour Window**: Tracks requests per hour
3. **User-based**: Limits applied per user ID
4. **Endpoint-based**: Different limits per endpoint type

### Rate Limit Keys

Redis keys follow the pattern:
```
{prefix}rl:{user_id}:{endpoint}:{window}
```

Example:
```
raptorflow:rl:user123:api:minute
raptorflow:rl:user123:api:hour
```

### Rate Limit Response

```json
{
  "allowed": true,
  "remaining_minute": 45,
  "remaining_hour": 850,
  "current_minute": 15,
  "current_hour": 150,
  "limit_minute": 60,
  "limit_hour": 1000
}
```

## Configuration Change Detection

The system automatically detects configuration changes:

1. **Hash Calculation**: Computes SHA-256 hash of configuration values
2. **Change Detection**: Compares current hash with stored hash
3. **Hot Reload**: Automatically reloads when changes detected
4. **Service Updates**: Updates dependent services (rate limiter, etc.)

### Configuration Hash

The hash includes these configuration values:
- app_name
- environment
- host, port
- llm_provider
- google_project_id, google_region
- cors_origins
- agent_timeout_seconds
- max_tokens_per_request
- rate_limit_enabled, rate_limit_per_minute, rate_limit_per_hour
- log_level

## Usage Examples

### Basic Setup

1. Copy the simplified environment file:
```bash
cp .env.simple .env
```

2. Edit `.env` with your values:
```bash
GOOGLE_API_KEY=AIzaSyYourApiKeyHere
GOOGLE_PROJECT_ID=your-project-123
SECRET_KEY=super-secret-key-for-production
```

3. Start the application:
```bash
python -m backend.main
```

### Configuration Validation

Check configuration health:
```bash
curl http://localhost:8000/api/v1/config/health
```

Expected response:
```json
{
  "healthy": true,
  "config_loaded": true,
  "rate_limiter_connected": true,
  "validation_passed": true,
  "environment": "development",
  "timestamp": "2024-01-15T10:30:00Z"
}
```

### Rate Limiting

Check user rate limits:
```bash
curl http://localhost:8000/api/v1/config/rate-limit/stats/user123
```

Reset user rate limits:
```bash
curl -X POST http://localhost:8000/api/v1/config/rate-limit/reset/user123
```

### Hot Reload

Update configuration without restart:
```bash
curl -X POST http://localhost:8000/api/v1/config/reload
```

## Migration from Old Configuration

### Removed Variables

The following 400+ environment variables have been removed:
- Complex enum configurations
- Feature flag systems
- Legacy agent configurations
- Unused service configurations
- Deprecated monitoring settings

### Updated Code

Update your code to use the new configuration:

```python
# Old way
from backend.config.settings import get_settings
settings = get_settings()
database_url = settings.DATABASE_URL

# New way
from backend.config import get_config
config = get_config()
database_url = config.database_url.get_secret_value()
```

### Rate Limiting

Update rate limiting usage:

```python
# Old way
from backend.core.rate_limiter import check_rate_limit
allowed, reason = check_rate_limit(user_id)

# New way
from backend.config import get_rate_limiter
rate_limiter = get_rate_limiter()
allowed, stats = await rate_limiter.check_limit(user_id)
```

## Production Deployment

### Required Production Settings

1. **Security**:
   ```bash
   SECRET_KEY=your-very-secure-secret-key
   ENVIRONMENT=production
   DEBUG=false
   ```

2. **Database**:
   ```bash
   DATABASE_URL=postgresql://user:password@localhost/raptorflow_prod
   ```

3. **Redis**:
   ```bash
   REDIS_URL=redis://redis-cluster:6379/0
   ```

4. **LLM**:
   ```bash
   GOOGLE_API_KEY=production-api-key
   GOOGLE_PROJECT_ID=production-project
   ```

5. **CORS**:
   ```bash
   CORS_ORIGINS=https://app.raptorflow.com
   ```

### Monitoring

Enable production monitoring:
```bash
LOG_LEVEL=WARNING
SENTRY_DSN=https://your-sentry-dsn
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=120
RATE_LIMIT_PER_HOUR=10000
```

## Troubleshooting

### Common Issues

1. **Configuration Validation Failed**:
   - Check required variables are set
   - Verify Google API key and project ID
   - Ensure SECRET_KEY is changed in production

2. **Redis Connection Failed**:
   - Verify Redis URL is correct
   - Check Redis is running and accessible
   - Confirm network connectivity

3. **Rate Limiting Not Working**:
   - Ensure `RATE_LIMIT_ENABLED=true`
   - Check Redis connection
   - Verify user ID is being passed correctly

### Debug Mode

Enable debug mode for detailed logging:
```bash
DEBUG=true
LOG_LEVEL=DEBUG
```

### Configuration Reset

Reset to defaults by removing `.env` and using `.env.simple`:
```bash
rm .env
cp .env.simple .env
```

## Performance Considerations

### Rate Limiting Performance

- Redis operations are O(1) complexity
- Sliding window uses minimal memory
- Automatic cleanup of expired keys
- Connection pooling for high throughput

### Configuration Performance

- Lazy initialization of services
- Minimal validation overhead
- Hash-based change detection is O(1)
- Hot reload without service interruption

## Security Considerations

### Secret Management

1. **Never commit `.env` files to version control**
2. **Use environment-specific secret management**
3. **Rotate API keys regularly**
4. **Use different keys for development/production**

### Rate Limiting Security

1. **Rate limits are per-user, not per-IP**
2. **Redis provides distributed protection**
3. **Consider adding IP-based limits for additional security**
4. **Monitor rate limit violations for abuse detection**

## Conclusion

The simplified configuration system provides:

- ✅ **Reduced Complexity**: From 481 to 389 lines
- ✅ **Essential Variables**: Only 20-30 core settings
- ✅ **Better Performance**: Optimized Redis rate limiting
- ✅ **Improved Monitoring**: Health check endpoints
- ✅ **Hot Reload**: Configuration changes without restart
- ✅ **Type Safety**: Pydantic validation
- ✅ **Better Documentation**: Clear examples and guides

This configuration system is production-ready and provides a solid foundation for scaling Raptorflow backend services.
