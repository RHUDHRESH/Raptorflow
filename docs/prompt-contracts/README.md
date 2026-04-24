# Prompt Contracts

Prompt contracts define the input/output shape for AWS Bedrock calls made by the Rust backend.

- AI provider: AWS Bedrock only
- Inference crate: `crates/aws`
- Heavy model: `mistral.mistral-large-3-675b-instruct`
- Light model: `mistral.ministral-3-8b-instruct`

When a prompt contract changes, update the matching schema in `schemas/` and the consuming Rust/TypeScript types.
