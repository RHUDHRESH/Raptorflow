## Summary

Bombed the existing dark/cyber Office and rebuilt it as a Paper / Amber / Editorial SaaS command desk.

The Office is now the central operating surface of RaptorFlow: "The Office — where campaigns become moves."

## Old Office problems removed

1. Full-screen PixiJS canvas with fake avatars removed
2. Fake "6 council members present" text removed
3. Fake avatar names (Cortex, Sentinel, Maven, Oracle, Wraith, Axiom) removed
4. Dead input box replaced with real Muse command router
5. Dark `#08081a` background replaced with Paper/Amber identity
6. Negative margin sidebar bypass fixed

## New Office layout

- **Header** — WORKSPACE / The Office / status pill / War Room + New Campaign actions
- **Morning Briefing** — Real counts from `GET /api/v1/office`
- **Campaign Fronts** — Real campaigns from `GET /api/v1/campaigns`
- **Council Activity** — Real sessions from `GET /api/v1/council`
- **Move Ladder** — Honest empty state (needs campaign contract repair)
- **Artifact Ledger** — Real content from `GET /api/v1/content`
- **Muse Command** — Real input that routes to `/muse?prompt=`
- **Right Rail** — Avatar roster, system signals, quick links

## APIs used

| Endpoint                | Data                 |
| ----------------------- | -------------------- |
| `GET /api/v1/office`    | Office state summary |
| `GET /api/v1/campaigns` | Campaign fronts      |
| `GET /api/v1/council`   | Council sessions     |
| `GET /api/v1/content`   | Content artifacts    |

## Unavailable/missing APIs

- Rich move ladder — honest empty state shown, needs campaign contract repair
- Avatar presence real-time — shows "unknown" honestly

## Fake data removed

- No fake KPIs
- No fake avatar presence
- No fake council member count
- No fake snark feed
- No fake event log seeding

## Responsive behavior

- Mobile: windows stack, rail below
- Tablet: 2-column grids
- Desktop: full layout with right rail

## Commands run with pass/fail table

| Command                   | Result                    |
| ------------------------- | ------------------------- |
| `pnpm typecheck`          | PASS                      |
| `pnpm lint`               | PASS                      |
| `pnpm structural:check`   | PASS (pre-existing WARNs) |
| `cargo fmt --all --check` | PASS                      |
| `cargo check --workspace` | PASS                      |

## Known limitations

- Move ladder needs campaign contract repair for real data
- Avatar roster shows "unknown" status until presence API exists
- PixiJS canvas files remain in repo but are no longer imported by /office

## Confirmations

- [x] No fake data added
- [x] No product contracts changed
- [x] No billing/landing work
- [x] No campaign contract repair in this phase
- [x] No force push
- [x] No stale PR merge
