# Digest: `Vol2_Foundation_FULL.docx`

## Intent

- Define the 21-screen Foundation flow and the live Foundation document.

## Key requirements

- Foundation is a substantive data acquisition system, not quick onboarding.
- Quick scan and deep scan run separately with websocket-fed updates.
- Foundation must be versioned and partially injectible into prompts.

## Scaffold implications

- Added frontend route placeholders for Foundation and backend `foundation` domain crate.
- Added contract types for `FoundationSnapshot` and `FoundationPatch`.
- Local and canonical docs preserve scan, versioning, and cache-invalidation concerns.
