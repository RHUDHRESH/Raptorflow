# Contributing to RaptorFlow

## Development Setup

### Prerequisites
- Node.js 22.x
- npm >= 10
- Python 3.11+
- Git

### Getting Started

1. **Clone the repository**
```bash
git clone <repository-url>
cd raptorflow
```

2. **Install dependencies**
```bash
# Frontend
npm install

# Backend
cd backend
pip install -r requirements.txt
```

3. **Set up environment variables**
```bash
cp .env.example .env.local
# Edit .env.local with your configuration
```

4. **Run development servers**
```bash
# Frontend (port 3000)
npm run dev

# Backend (port 8000)
python -m backend.run_simple
```

## Code Quality Standards

### TypeScript
- **Strict mode enabled** - All code must pass TypeScript strict checks
- **No `any` types** - Use proper type definitions
- **Explicit return types** - Functions should have explicit return types

### Code Formatting
- **Prettier** - All code is formatted with Prettier
- **EditorConfig** - Follow .editorconfig settings
- **2-space indentation** for JS/TS/JSON/CSS
- **4-space indentation** for Python

### Linting
```bash
# Run ESLint
npm run lint

# Fix auto-fixable issues
npm run lint:fix

# Type check
npm run type-check
```

## Git Workflow

### Branch Naming
- `feature/description` - New features
- `fix/description` - Bug fixes
- `refactor/description` - Code refactoring
- `docs/description` - Documentation updates

### Commit Messages
Follow conventional commits:
```
feat: add new feature
fix: resolve bug in component
refactor: reorganize file structure
docs: update README
test: add unit tests
chore: update dependencies
```

### Pre-commit Hooks
Husky runs automatically before commits:
- Lints staged files
- Formats code with Prettier
- Runs type checks

## Testing

### Unit Tests
```bash
npm run test
```

### E2E Tests
```bash
npm run test:e2e
```

### Coverage
```bash
npm run test:coverage
```

## Project Structure

```
raptorflow/
├── src/                    # Frontend source
│   ├── app/               # Next.js App Router
│   ├── components/        # React components
│   ├── lib/              # Utilities
│   ├── services/         # API clients
│   └── stores/           # Zustand stores
├── backend/               # FastAPI backend
│   ├── api/              # API routes
│   ├── services/         # Business logic
│   ├── core/             # Infrastructure
│   └── tests/            # Backend tests
├── supabase/             # Database migrations
└── public/               # Static assets
```

## Code Style Guide

### React Components
- Use functional components with hooks
- Prefer named exports for components
- Use TypeScript interfaces for props
- Keep components focused and small

### File Naming
- Components: `PascalCase.tsx`
- Utilities: `camelCase.ts`
- Constants: `UPPER_SNAKE_CASE.ts`
- Tests: `*.test.ts` or `*.spec.ts`

### Import Order
1. React/Next.js imports
2. Third-party libraries
3. Internal components
4. Utilities and helpers
5. Types and interfaces
6. Styles

## Common Tasks

### Adding a New Component
1. Create component file in appropriate directory
2. Add TypeScript interface for props
3. Implement component with proper types
4. Add to component exports if needed
5. Write tests

### Adding a New API Route
1. Create route file in `backend/api/v1/`
2. Define Pydantic schemas
3. Implement route handler
4. Add to router registry
5. Update API_INVENTORY.md

### Running Bundle Analyzer
```bash
ANALYZE=true npm run build
```

## Troubleshooting

### TypeScript Errors
```bash
# Check all errors
npm run type-check

# Fix auto-fixable issues
npm run lint:fix
```

### Build Failures
```bash
# Clear Next.js cache
rm -rf .next

# Reinstall dependencies
rm -rf node_modules
npm install
```

### Database Issues
```bash
# Reset local database
supabase db reset

# Run migrations
supabase db push
```

## Documentation

- **API Documentation**: See API_INVENTORY.md
- **Architecture**: See REPO_MAP.md
- **Auth Flow**: See AUTH_INVENTORY.md
- **ADRs**: See ADRs/ directory

## Getting Help

- Check existing issues
- Review documentation
- Ask in team chat
- Create detailed issue with reproduction steps

## Pull Request Process

1. **Create feature branch** from main
2. **Make changes** following code standards
3. **Write/update tests** for changes
4. **Update documentation** if needed
5. **Run all checks** locally
6. **Create PR** with clear description
7. **Address review feedback**
8. **Squash and merge** when approved

## Code Review Guidelines

### For Authors
- Keep PRs focused and small
- Write clear descriptions
- Add screenshots for UI changes
- Respond to feedback promptly

### For Reviewers
- Be constructive and specific
- Test changes locally
- Check for edge cases
- Approve when satisfied

## Release Process

1. Update version in package.json
2. Update CHANGELOG.md
3. Create release tag
4. Deploy to staging
5. Run smoke tests
6. Deploy to production
7. Monitor for issues

## Security

- Never commit secrets or API keys
- Use environment variables
- Follow security best practices
- Report vulnerabilities privately

## License

By contributing, you agree that your contributions will be licensed under the project's license.
