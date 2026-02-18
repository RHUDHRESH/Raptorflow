# Authentication System

Complete authentication system documentation for RaptorFlow.

## Contents

- [Architecture](ARCHITECTURE.md) - System design and flow
- [API Reference](API.md) - API endpoints and responses
- [Security](SECURITY.md) - Security measures implemented
- [Troubleshooting](TROUBLESHOOTING.md) - Common issues and solutions

## Quick Start

### 1. Configure Environment

Add to your `.env`:
```bash
# Supabase
SUPABASE_URL=https://your-project.supabase.co
NEXT_PUBLIC_SUPABASE_URL=https://your-project.supabase.co
SUPABASE_ANON_KEY=eyJ...
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Auth
AUTH_MODE=supabase
```

### 2. Verify Setup

```bash
python scripts/verify_auth_env.py
```

### 3. Test Authentication

```bash
# Login
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"user@example.com","password":"password123"}'

# Verify
curl -X POST http://localhost:8000/api/v1/auth/verify \
  -H "Authorization: Bearer <token>"
```

## Development Modes

| Mode | Description | Use Case |
|------|-------------|-----------|
| `demo` | Any credentials work | Local development |
| `supabase` | Real Supabase auth | Production |
| `disabled` | No auth | Testing only |

Switch modes by changing `AUTH_MODE` in your `.env` file.

## Features

- HTTP-only secure cookies
- Token refresh
- Rate limiting
- Email validation
- Row Level Security (RLS)
- Frontend middleware protection
- Login/signup pages

## File Structure

```
backend/
├── services/auth/
│   ├── supabase.py    # Supabase auth service
│   ├── demo.py        # Demo auth service
│   ├── factory.py     # Auth service factory
│   └── disabled.py    # Disabled auth service
└── api/v1/auth/
    └── routes.py       # Auth API endpoints

src/
├── lib/supabase/      # Supabase clients
├── stores/            # Auth state
├── middleware.ts      # Route protection
└── app/              # Login/signup pages

scripts/
├── verify_auth_env.py     # Environment verification
└── migrations/
    └── rls_policies.sql  # Database RLS policies

documentation/auth/
├── ARCHITECTURE.md
├── API.md
├── SECURITY.md
└── TROUBLESHOOTING.md
```

## Next Steps

1. Review [API Documentation](API.md) for endpoint details
2. Check [Security](SECURITY.md) for implemented measures
3. Read [Troubleshooting](TROUBLESHOOTING.md) if issues arise
