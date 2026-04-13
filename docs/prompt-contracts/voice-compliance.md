# Voice Compliance Contract

Use this contract when content must be checked against the current Foundation voice fingerprint.

## Input

- `content_text`
- `voice_fingerprint`
- `brand_personality`
- `channel`
- `campaign_id`

## Output

- A compliance verdict
- A short list of violations or mismatches
- A repair hint when the content is close but not acceptable

## Failure behavior

- Return non-compliant when voice confidence is too low
- Do not rewrite the content silently
