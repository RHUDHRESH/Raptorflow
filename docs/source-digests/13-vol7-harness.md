# Digest: `Vol7_Harness_FULL.docx`

## Intent

- Define the orchestration system that coordinates avatars, sessions, tools, and jobs.

## Key requirements

- Session manager, context assembler, inference router, tool gateway, stream coordinator, and event harvester are separate responsibilities.
- WebSocket streaming and job scheduling are first-class architecture, not add-ons.
- Build order matters because infra, auth, PRL, and context assembly are prerequisites.

## Scaffold implications

- Added backend crate split that mirrors harness boundaries.
- Added REST and websocket schema scaffolding plus internal job surfaces.
- Added cron/job placeholders and deployment runbooks for autonomous operations.
