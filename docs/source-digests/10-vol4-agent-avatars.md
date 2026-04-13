# Digest: `Vol4_AgentAvatars_FULL.docx`

## Intent

- Define avatar identity, the Strategist, support specialists, and interns.

## Key requirements

- Avatars have persistent essence, not cosmetic personas.
- Council avatars, strategist, support specialists, and interns are separate operational roles.
- Intern delegation is a built-in cognitive extension.

## Scaffold implications

- Added `council`, `eel`, `office`, and `integrations` backend crates with room for avatar and intern contracts.
- Shared contracts reserve `InternTask`, `CouncilSession`, and `CouncilAgentPosition`.
- Office and Council shells are structured around named avatar roles instead of anonymous agents.
