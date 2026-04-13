# Prompt Contracts

Every AI inference call in RaptorFlow is governed by a structured contract. These are **interface contracts, not final prompt prose** — they define the input shape, expected output markers, parsing rules, and failure behaviour. Actual prompt text is not stored here.

**These are stubs.** The prompt contracts document the expected interface between the Rust inference layer (`crates/gcp/`) and the AI model. When a worker is implemented, the contract is the specification it must satisfy.

---

## The 17 contracts

| Contract                  | Used by         | What it does                                                            |
| ------------------------- | --------------- | ----------------------------------------------------------------------- |
| `brief-evaluation.md`     | Strategist      | Evaluates a brief, plan, or artifact before execution                   |
| `strategist-synthesis.md` | Strategist      | Synthesises council positions into a campaign recommendation            |
| `council-position.md`     | Council avatars | Produces a position, objection, or recommendation from an avatar        |
| `private-reflection.md`   | All avatars     | Identity-safe reflection that doesn't cause persona drift               |
| `eel-reflection.md`       | All avatars     | Reflection that can update PRL memory without corruption                |
| `content-generation.md`   | Content worker  | Generates marketing content grounded in foundation                      |
| `muse-routing.md`         | Muse            | Classifies and routes a user message to the right AI tier               |
| `daily-wins.md`           | Muse            | Generates the daily briefing from overnight PRL activity                |
| `nudge.md`                | PRL             | Produces a nudge — a lightweight operator notification or prompt        |
| `voice-compliance.md`     | All avatars     | Checks that avatar output stays within voice and brand guardrails       |
| `replanning.md`           | Strategist      | Triggers autonomous replanning when performance diverges from targets   |
| `research-request.md`     | Muse / Council  | Triage research requests to the appropriate handler                     |
| `intern-research.md`      | Intern          | Executes delegated research with supervisor-reviewed return             |
| `intern-dispatch.md`      | Strategist      | Wraps an intern task envelope for delegated execution                   |
| `tool-gateway.md`         | All avatars     | Executes a tool call on behalf of an avatar (web search, browser, etc.) |
| `stream-coordinator.md`   | Council / Muse  | Coordinates multi-turn session precheck and routing                     |
| `event-harvester.md`      | PRL ingest      | Ingests a raw event into PRL as a ripple with salience scoring          |

---

## Contract structure

Every contract follows this structure:

```markdown
# <Contract Name>

Use this contract when <trigger condition>.

## Input

- `<field_name>`: <type> — <description>

## Output

- <description of what the model must produce>
- <expected output markers or JSON block shape>

## Failure behaviour

- <what to return or do when the model can't produce valid output>
- <safety constraints>
```

### Example

```markdown
## Input

- `session_id`: string — the active council session
- `avatar_key`: string — the avatar taking the position
- `position_prompt`: string — the specific question or claim to address

## Output

- A parser-friendly position block
- Enough structured metadata to route into the session stream

## Failure behaviour

- Return a short failure block; never invent foundation facts or campaign state
```

---

## Adding a new prompt contract

1. Create `docs/prompt-contracts/<name>.md` following the structure above
2. Implement the handler in `crates/<domain>/src/` using `crates/gcp/` for the inference call
3. Add the prompt contract to the pre-commit validation in `scripts/scaffold:check` if you want file-presence validation
4. When implementing the worker, the contract is your specification

---

## Relationship to code

Prompt contracts are not enforced by the compiler — they're design contracts. The `crates/gcp/` crate calls Gemini. The prompt contracts define what input goes in and what output shape is expected out. Workers in `crates/<domain>/` are responsible for assembling the input and parsing the output.
