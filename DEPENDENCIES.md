# Dependencies Documentation

## Frontend Dependencies (package.json)

### Core Framework
- **next**: ^14.2.5 - React framework for production
- **react**: ^18.3.1 - UI library
- **react-dom**: ^18.3.1 - React DOM renderer
- **typescript**: ^5.6.3 - TypeScript compiler

### UI & Styling
- **tailwindcss**: ^3.4.18 - Utility-first CSS framework
- **@radix-ui/react-***: Multiple packages - Headless UI components
- **lucide-react**: ^0.554.0 - Icon library
- **framer-motion**: ^12.23.24 - Animation library
- **gsap**: ^3.14.2 - Animation platform
- **@gsap/react**: ^2.1.2 - GSAP React integration

### State Management
- **zustand**: ^5.0.9 - State management library

### Data Visualization
- **recharts**: ^3.5.0 - Chart library
- **@react-three/fiber**: ^9.4.2 - React renderer for Three.js
- **@react-three/drei**: ^10.7.7 - Three.js helpers
- **three**: ^0.181.2 - 3D library

### Forms & Validation
- **zod**: ^4.1.13 - Schema validation
- **react-hook-form**: (not installed but commonly used with Zod)

### Utilities
- **clsx**: ^2.1.1 - Conditional className utility
- **tailwind-merge**: ^3.4.0 - Merge Tailwind classes
- **class-variance-authority**: ^0.7.1 - CSS variant API
- **date-fns**: ^4.1.0 - Date utility library
- **uuid**: ^13.0.0 - UUID generator

### AI/ML Integration
- **@google-cloud/vertexai**: ^1.10.0 - Vertex AI SDK
- **@langchain/core**: ^1.1.2 - LangChain core
- **@langchain/google-vertexai**: ^2.0.2 - LangChain Vertex AI
- **langchain**: ^1.1.3 - LangChain framework

### Email
- **resend**: ^6.8.0 - Email API

### Monitoring
- **@sentry/nextjs**: ^10.36.0 - Error tracking
- **@sentry/profiling-node**: ^10.36.0 - Performance profiling
- **posthog-js**: ^1.96.1 - Product analytics

### Development Tools
- **eslint**: ^8.57.1 - Linter
- **prettier**: (needs installation) - Code formatter
- **@typescript-eslint/eslint-plugin**: ^8.14.0 - TypeScript ESLint
- **@typescript-eslint/parser**: ^8.14.0 - TypeScript parser
- **vitest**: ^1.0.4 - Test framework
- **@vitest/ui**: ^1.0.4 - Vitest UI
- **@vitest/coverage-v8**: ^1.0.4 - Coverage tool
- **@testing-library/react**: ^16.3.0 - React testing utilities

### Potentially Unused Dependencies
- **@magicuidesign/mcp**: ^1.0.6 - Unknown usage
- **@hugeicons/core-free-icons**: ^3.1.1 - May be redundant with lucide-react
- **@hugeicons/react**: ^1.1.4 - May be redundant with lucide-react
- **hugeicons-react**: ^0.3.1 - Duplicate icon library
- **@phosphor-icons/react**: ^2.1.10 - Another icon library (redundant?)
- **leaflet**: ^1.9.4 - Map library (is this used?)
- **react-leaflet**: ^5.0.0 - React wrapper for Leaflet
- **react-router-dom**: ^7.9.6 - Routing (Next.js has built-in routing)
- **react-helmet-async**: ^2.0.5 - Head management (Next.js has built-in)
- **cheerio**: ^1.1.2 - HTML parsing (backend only?)
- **dompurify**: ^3.3.0 - XSS sanitization
- **isomorphic-dompurify**: ^2.32.0 - Duplicate of dompurify?

## Backend Dependencies (requirements.txt)

### Core Framework
- **fastapi**: Web framework
- **uvicorn**: ASGI server
- **pydantic**: Data validation

### Database
- **supabase**: Supabase client
- **asyncpg**: PostgreSQL async driver

### Cache & Storage
- **redis**: Redis client
- **google-cloud-storage**: GCS client

### AI/ML
- **google-cloud-aiplatform**: Vertex AI
- **langchain**: LangChain framework
- **langchain-google-vertexai**: Vertex AI integration

### Utilities
- **python-dotenv**: Environment variables
- **structlog**: Structured logging

## Security Vulnerabilities (npm audit)

### High Severity
1. **next** (10.0.0 - 15.5.9)
   - DoS via Image Optimizer remotePatterns
   - HTTP request deserialization DoS
   - Fix: Upgrade to next@16.1.6

### Moderate Severity
2. **esbuild** (<=0.24.2)
   - Development server request vulnerability
   - Fix: Upgrade via vite update

3. **vite** (0.11.0 - 6.1.6)
   - Depends on vulnerable esbuild
   - Fix: Upgrade to vite@7.3.1

4. **vite-node** (<=2.2.0-beta.2)
   - Depends on vulnerable vite
   - Fix: Upgrade via vitest

5. **vitest** (multiple ranges)
   - Depends on vulnerable vite and vite-node
   - Fix: Upgrade to latest

## Recommended Actions

### Immediate
1. Run `npm audit fix --force` to fix breaking changes
2. Remove unused icon libraries (keep only lucide-react)
3. Remove react-router-dom (use Next.js routing)
4. Remove react-helmet-async (use Next.js Head)
5. Consolidate dompurify packages

### Future
1. Add prettier as devDependency
2. Add husky for pre-commit hooks
3. Add lint-staged for staged file linting
4. Add webpack-bundle-analyzer
5. Consider removing unused map libraries if not needed

## Package Size Analysis
- Total dependencies: 88 packages
- Estimated reduction potential: 15-20 packages
- Target: ~70 essential packages
