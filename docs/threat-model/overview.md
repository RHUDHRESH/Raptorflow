# Threat Model Overview

- Tenant isolation is enforced with `org_id`.
- Auth is Clerk JWT validation in the Rust API and middleware in the frontend.
- Production secrets live in AWS Secrets Manager or the Vercel env system.
- No removed cache or external inference dependency remains in the active stack.
