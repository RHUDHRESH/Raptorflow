# EEL Reflection Contract

Use this contract when an avatar needs an identity-safe reflection that can update memory without drift.

## Input

- `avatar_key`
- `session_id`
- `essence_core`
- `ego_signature`
- `skill_weave`
- `context_pack`

## Output

- A gated reflection block
- A note about whether the reflection should influence memory or action
- Optional candidate updates for EEL and PRL

## Failure behavior

- Keep the reflection private when the identity model is unstable
- Prefer no-op output over persona drift
