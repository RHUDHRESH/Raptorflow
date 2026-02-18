# backend/features/ - Domain Modules

**Parent:** `backend/AGENTS.md`

## OVERVIEW
Clean architecture domain modules with hexagonal structure: auth, campaign, workspace, asset.

## STRUCTURE
```
backend/features/
├── auth/                    # Authentication domain
│   ├── domain/              # Entities (User, Session)
│   ├── application/         # Services, ports (interfaces)
│   └── adapters/            # Supabase implementation
├── campaign/               # Campaign management
├── workspace/              # Workspace management
└── asset/                  # Asset management
```

## WHERE TO LOOK
| Module | Domain | Application |
|--------|--------|-------------|
| Auth | `features/auth/domain/entities.py` | `features/auth/application/services.py` |
| Campaign | `features/campaign/domain/` | `features/campaign/application/` |
| Workspace | `features/workspace/domain/` | `features/workspace/application/` |
| Asset | `features/asset/domain/` | `features/asset/application/` |

## CONVENTIONS
- Clean architecture: domain → application → adapters
- Entities in `domain/entities.py`
- Services in `application/services.py`
- Ports (interfaces) in `application/ports.py`
- Implementations in `adapters/`

## ANTI-PATTERNS
- NO business logic in adapters
- NO direct DB calls in domain layer
- NO circular dependencies between features
