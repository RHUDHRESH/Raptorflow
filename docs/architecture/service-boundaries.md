# Service Boundaries

## Web application

- Renders marketing and authenticated product surfaces
- Owns browser-only state, app shell orchestration, and Office rendering
- Talks to the Rust API over REST and WebSockets

## API binary

- Owns auth enforcement, tenant context, contracts, jobs, and integrations
- Exposes REST, WebSockets, and internal job commands
- Delegates domain structure to internal crates

## Data systems

- Aurora is the primary source of truth
- Qdrant stores filtered vector collections
- DragonflyDB stores ephemeral cache, pub/sub, and locks

## External systems

- Clerk for identity
- GCP API for inference
- Razorpay for billing
- S3 for blobs
- SQS for background queues
