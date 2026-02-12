# Root File Policy

This file defines the strict root-level grouping used for the renovation baseline.

## Runtime Group

Must remain at root because toolchains expect them there:

- `backend/`
- `src/`
- `public/`
- `supabase/`
- `scripts/`
- `tests/`
- `package.json`
- `package-lock.json`
- `next.config.js`
- `tsconfig.json`
- `tailwind.config.js`
- `postcss.config.js`
- `next-env.d.ts`

## Infra Group

Deployment/runtime wiring:

- `Dockerfile`
- `docker-entrypoint.sh`
- `docker-compose.yml`
- `docker-compose.local.yml`
- `docker-compose.test.yml`
- `deploy.sh`
- `deploy_production.sh`
- `vercel.json`
- `.github/`

## Dev-Only Group

Developer tooling/configuration:

- `eslint.config.js`
- `vitest.config.ts`
- `playwright.config.ts`
- `pytest.ini`
- `.editorconfig`
- `.gitignore`
- `.prettierignore`
- `.prettierrc.json`
- `.pre-commit-config.yaml`
- `.npmrc`
- `.eslintignore`
- `.lintstagedrc.json`
- `.flake8`
- `.gitattributes`
- `sentry.edge.config.ts`
- `sentry.server.config.ts`
- `instrumentation-client.ts`

## Prune Log (This Pass)

Removed as non-essential or legacy root clutter:

- `index.html` (unused Vite-era entrypoint)
- `vite.config.js` (unused Vite config)
- `jsconfig.json` (redundant with `tsconfig.json`)
- `ecosystem.config.js` (stale PM2 config with merge conflicts)
- `.prettierrc` (duplicate/conflicting with `.prettierrc.json`)
