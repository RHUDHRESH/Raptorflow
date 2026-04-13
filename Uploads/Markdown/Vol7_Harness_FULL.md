**RAPTORFLOW**

MASTER DOCUMENT SERIES

**VOLUME SEVEN**

**The Agent Avatar Harness**

_How to build the most advanced multi-agent orchestration system in production — complete technical specification for Rust, Axum, Tokio, graph-flow, and the Gemini inference layer_

CONFIDENTIAL — INTERNAL BLUEPRINT

# **Opening: What the Harness Is and Why It Is Hard**

The Agent Avatar Harness is the orchestration system that coordinates the twenty-one avatars, manages their tool access, enforces their isolation boundaries, routes inference to the correct models, assembles their contexts from the PRL and EEL, streams their outputs to the frontend, and persists all session state across sessions. It is the nervous system of RaptorFlow — the infrastructure through which everything the PRL and EEL compute becomes a user-facing product experience.

Building a harness that works is relatively straightforward. Building one that works correctly — with real personality isolation, real memory persistence, real tool boundary enforcement, real streaming at scale, and real cost efficiency — is significantly harder. The most common failure mode in multi-agent systems is not that they cannot run multiple agents. It is that the agents are not actually isolated from each other in the ways that matter: they share context they should not, they have access to tools they should not, they do not maintain their individual memory streams, and their outputs converge toward each other over time because the boundaries that should keep them distinct are implemented in prompts rather than in architecture.

This volume describes how to build the Harness correctly. Every decision is grounded in the requirements of the EEL and PRL systems that the Harness serves. Every isolation boundary is architectural rather than instructional. Every tool access pattern is enforced at the type level where possible and at the handler level where not. The Harness described here is production-grade — not a prototype that works in happy-path conditions but a system that handles session failures, inference timeouts, streaming backpressure, and concurrent multi-agent operations correctly.

# **Part One: The Architecture of the Harness**

## **Chapter 1.1 — The Core Components**

The Harness consists of six core components that interact through well-defined interfaces. Understanding each component and its interface before writing any code is essential — the most common implementation mistake is building these components as a monolith, which makes the isolation boundaries impossible to enforce correctly.

### **Component 1: The Session Manager**

The Session Manager owns the lifecycle of every inference session. A session begins when a user triggers an action that requires agent inference — a Muse message, a Council deliberation, a content generation request, a campaign brief submission. A session ends when all active inference streams have completed and all resulting ripples have been written to the PRL.

The Session Manager is responsible for: creating the session record in Aurora with a unique session_id, loading the agent_essences records for all relevant agents from Aurora into a session-scoped in-memory cache, triggering the EEL decay function for all loaded agents (applying the inter-session emotional decay), initializing or refreshing the DragonflyDB working memory cache for all loaded agents, and registering the session with the WebSocket connection so that streaming outputs are correctly routed.

The Session Manager is a Rust struct with an async new() constructor that performs all of the above operations and returns a fully initialized SessionContext. The SessionContext is passed by reference to all other Harness components — it is the single source of truth for all session-scoped state.

### **Component 2: The Context Assembler**

The Context Assembler builds the complete inference context for each agent invocation. It takes as inputs: the agent_id for the agent being invoked, the current request (the task or question the agent must respond to), the SessionContext, and the scope of context required (private, campaign, org). It produces a ContextPack — the structured assembly of memories, skills, Essence Core content, ego metadata, and Foundation data that will frame the agent's response.

The Context Assembler orchestrates the CORTEX retrieval system, the EEL skill retrieval, and the Essence Core force-inclusion. It also assembles the Foundation context — either from the DragonflyDB Foundation cache or directly from the Aurora Foundation tables if the cache has expired. It produces the complete context in under 10 milliseconds for the full five-pass retrieval.

### **Component 3: The Inference Router**

The Inference Router selects the correct Gemini model for each inference call and constructs the API request. The routing logic is deterministic: Campaign Strategist synthesis for sessions with more than six Council agents uses Gemini 3.1 Pro; Campaign Strategist for all other operations uses Gemini 3.1 Flash-Lite Reasoning; Council avatars use Gemini 3.1 Flash-Lite Reasoning; interns use Gemini 3.1 Flash-Lite Normal; all background batch operations use Gemini 3.1 Flash-Lite Normal with batch API.

The Inference Router also manages context caching. The Foundation JSON is cached through Vertex AI's context caching API. The Router checks the cache validity before each inference call and refreshes the cache if it has expired. Cache TTL is one hour from the last write. Cache invalidation is triggered whenever the Foundation is updated.

### **Component 4: The Tool Gateway**

The Tool Gateway enforces tool access boundaries. It is the only component through which agents can access external tools — web search, file access, calendar, email, calculator. Every tool call from any agent goes through the Tool Gateway, which checks the calling agent's tier before executing the tool.

The Tool Gateway is implemented as a Rust enum with one variant per tool and match arms that enforce the access rules at compile time where possible. Agents that should not have access to a specific tool cannot construct a valid tool request that the Gateway will accept — the type system prevents it. This is architectural enforcement, not runtime checking after the fact.

### **Component 5: The Stream Coordinator**

The Stream Coordinator manages the WebSocket streaming of inference outputs to the frontend. It receives token events from the Gemini streaming API and forwards them to the appropriate WebSocket connection through the DragonflyDB pub/sub channel. It handles backpressure — the case where the frontend is consuming tokens more slowly than Gemini is generating them — and manages the ordered delivery of tokens from multiple concurrent agent streams during Council sessions.

### **Component 6: The Event Harvester**

The Event Harvester collects the meaningful events from a completed session and submits them to the PRL ingest pipeline. It processes the inference outputs, identifies which events should become ripples, constructs the MemoryEvent structs, and sends them to the MPSC channel. It also triggers the ego_state update for each agent based on the emotional events from the session and writes the updated ego_state back to the agent_essences table.

## **Chapter 1.2 — The Data Flow Through the Harness**

Understanding the data flow through the complete Harness is essential for understanding how the components fit together. A complete trace of a Council deliberation from user request to final output:

Step 1: User submits a question to the Council through the frontend. The request arrives at the Axum WebSocket handler as a council.start message with the question text and optionally a list of requested agents.

Step 2: The WebSocket handler validates the JWT token, extracts the org_id, and creates a new session through the Session Manager. The Session Manager creates the session record in Aurora, loads agent essences, applies decay, and refreshes working memory caches. A SessionContext is returned.

Step 3: The Complexity Router assesses the question and determines which agents should participate and which Council session tier applies (Tactical, Operational, Strategic, or War Room). The participating agent list is either confirmed from the request or determined by the router.

Step 4: For each participating Council agent, the Context Assembler runs in parallel via Tokio concurrent tasks. Each agent gets its own ContextPack constructed from its private PRL ripples, the shared campaign ripples, its Skill Weave, its Essence Core, and its current Ego Signature metadata. The Foundation context is shared across all agents from the DragonflyDB cache.

Step 5: The Inference Router constructs the API request for each agent using its ContextPack and the question. All Council agent requests use Gemini 3.1 Flash-Lite Reasoning. Requests are sent concurrently — all Council agents begin generating simultaneously, not sequentially.

Step 6: The Stream Coordinator begins receiving token events from the Gemini streaming API for all active agent streams simultaneously. For each token received, it publishes to the DragonflyDB pub/sub channel with the format debate:{session_id}:{agent_id}. The WebSocket connection for this user is subscribed to debate:{session_id}:\* and receives all tokens as they arrive.

Step 7: The frontend receives tokens from all agents via the WebSocket connection. Each token message includes the agent_id so the frontend knows which agent's response is being streamed. The debate view renders tokens as they arrive, building each agent's response progressively.

Step 8: When all Council agent streams complete, the Strategist's synthesis context is assembled. The synthesis context includes: all Council agents' complete responses, the original question, the Strategist's private ContextPack, and the Foundation context. The Strategist synthesis uses Gemini 3.1 Pro if more than six agents participated, Flash-Lite Reasoning otherwise.

Step 9: The Strategist synthesis streams to the frontend via the same WebSocket channel with agent_id 'synthesis'. The frontend renders the synthesis as a distinct card below the individual agent responses.

Step 10: When the synthesis stream completes, the Event Harvester processes the session. It creates ripples for each agent's position, the synthesis outcome, any notable debate dynamics, and the prediction content of each agent's response. Ego state updates are computed and written to agent_essences. The session record is closed in Aurora.

## **Chapter 1.3 — The 20/80 Inference Split in Practice**

The 20/80 split between Gemini 3.1 Pro and Gemini 3.1 Flash-Lite is the primary cost efficiency mechanism of the Harness. Implementing it correctly — routing the right calls to the right models — requires clear routing rules that the Inference Router enforces consistently.

Gemini 3.1 Pro is used for: Campaign Strategist synthesis when more than six Council agents participated (War Room and large Strategic sessions), complex campaign planning operations where the Strategist must reason across multiple competing strategic frameworks simultaneously, and any explicit user-initiated request that asks for the Strategist's deep strategic analysis on a high-stakes decision.

Gemini 3.1 Flash-Lite Reasoning is used for: all Council avatar positions in debates, Campaign Strategist operations not qualifying for Pro (most Strategist operations), all reflection calls in the EEL, all alignment gate reframing calls, and all post-debate private reflections.

Gemini 3.1 Flash-Lite Normal is used for: all intern operations (research, data gathering, first drafts), all content generation (ad copy, social posts, blog drafts), all brand voice compliance checks, all competitive intelligence analysis, all Daily Wins generation (batch mode), all Nudge generation, all summary generation for PRL ingest, and all onboarding URL analysis.

The practical consequence: in a typical Council session with six agents, the Pro model is used for synthesis only — one call. The six agent positions use Flash-Lite Reasoning — six calls. Any intern research that runs before the session uses Flash-Lite Normal — multiple calls but at the lowest cost tier. The content generated from the session's output uses Flash-Lite Normal. The synthesis is the expensive call; everything around it is cheap.

# **Part Two: Session Management in Complete Technical Detail**

## **Chapter 2.1 — The SessionContext Struct**

The SessionContext is the central data structure of the Harness. Every component that needs session-scoped data receives a reference to the SessionContext. It is constructed once per session and lives for the duration of that session in the application's heap.

The SessionContext contains: the session_id ULID, the org_id UUID identifying the tenant, the user_id UUID identifying the requesting user, a HashMap from agent_id to AvatarState (the in-memory representation of each agent's loaded state), the Foundation cache (the parsed Foundation JSON loaded for this session), the DragonflyDB connection pool reference, the Aurora database connection pool reference, the active WebSocket sender for streaming to this user, and the inference client references (pre-configured Vertex AI clients for each model tier).

The AvatarState is the in-memory representation of a loaded agent. It contains: the agent_essences record loaded from Aurora (all fields including essence_core, ego_state, skill_atoms, persona_vector, and reflection fields), the working memory ripple list loaded from DragonflyDB (up to 50 ripple summaries), the assembled ContextPack from the last retrieval operation (cached for the duration of the session), and the event log (the list of MemoryEvent structs that have been fired during this session and will be submitted to the PRL ingest pipeline at session end).

The SessionContext is not cloned — it is passed by reference. In Rust, this means passing Arc references for components that need to be shared across async tasks (like the inference clients and database pool references) and using appropriate synchronization primitives for mutable state (like the working memory list and event log). The design minimizes lock contention by keeping mutable state within each AvatarState and avoiding shared mutable state between avatars.

## **Chapter 2.2 — Session Initialization**

Session initialization is an async operation that must complete before any inference can begin. The initialization sequence is partly sequential (steps that depend on each other) and partly concurrent (steps that can run in parallel).

Sequential phase: create the session_id using the ULID generation library, extract the org_id from the validated JWT token, load the Foundation JSON from DragonflyDB cache or from Aurora if cache miss, validate that the Foundation is complete (all required sections present), create the session record in Aurora.

Concurrent phase: for each agent that will participate in this session, concurrently load their agent_essences record from Aurora, apply the ego decay function to their ego_state using the inter-session timestamp, load their working memory from DragonflyDB, and store the initialized AvatarState in the SessionContext's HashMap.

The concurrent phase uses Tokio's join_all to run all agent loading operations simultaneously. For a Council session with 12 agents, this means 12 concurrent Aurora queries and 12 concurrent DragonflyDB operations. With connection pooling, this typically completes in 15 to 25 milliseconds — fast enough to be imperceptible at the user experience level, which perceives the brief pause between button press and first token as 'the system is thinking.'

After the concurrent phase completes, the SessionContext is fully initialized and ready for inference operations. The total initialization time target is under 30 milliseconds.

## **Chapter 2.3 — Session Persistence and Recovery**

Sessions can be interrupted: network disconnections, browser refreshes, server restarts. The Harness must handle these gracefully without losing session state or creating inconsistent memory states in the PRL.

All session state is persisted to Aurora incrementally during the session, not only at the end. The session record in Aurora is updated after each major operation: when each agent's context assembly completes, when each agent's inference stream completes, when the synthesis completes. This incremental persistence ensures that even if the session is interrupted, the completed portions of the session's work are not lost.

The session_state field in the Aurora sessions table tracks the current phase: initializing, agents_generating, synthesizing, events_harvesting, complete, or failed. If a session is in an intermediate state when a reconnection occurs, the system can determine where the session was in its lifecycle and resume from the appropriate point.

For WebSocket reconnections during an active session: the reconnection request includes the session_id. The Session Manager looks up the session in Aurora, verifies it is in an active state, and reconnects the WebSocket sender in the SessionContext to the new WebSocket connection. Any inference streams that are still active continue streaming to the new connection. This allows users to refresh their browser during a long Council session without losing the in-progress debate.

# **Part Three: Context Assembly — Building the Agent's Mind**

## **Chapter 3.1 — The ContextPack Structure**

The ContextPack is the structured representation of everything an agent needs to know to generate its response. It is assembled by the Context Assembler for each agent invocation and is the primary input to the Inference Router's context construction process.

A ContextPack contains seven sections, each with a specific function in the final generation context:

Section 1 — Identity (from EEL Essence Core): the avatar's constitutional principles, core beliefs, characteristic language patterns, and forbidden response types. This section is always present and cannot be empty.

Section 2 — Emotional Register (from EEL Ego Signature): the current ego_state as the dominant emotion and active dyad, the confidence modifier, and a tonal directive derived from the dyad computation.

Section 3 — Procedural Knowledge (from EEL Skill Weave): the top 3 relevant SkillAtoms retrieved for the current task, each presented as a structured procedure the avatar draws on.

Section 4 — Episodic Memory (from PRL Pass A and B): the top working memory ripples and semantically similar ripples from the full retrieval, presented as the avatar's relevant recent and long-term memories.

Section 5 — Associative Memory (from PRL Passes D and E): the Hebbian-spread and trajectory-matched ripples, presented as contextually associated memories that the avatar is drawing on.

Section 6 — Shared Context (Foundation and Campaign): the Foundation JSON relevant fields, the current campaign context if applicable, and any shared_campaign or shared_org ripples accessible to this agent.

Section 7 — Current Task: the specific request the agent must respond to, structured to match the agent's expected input format for this type of task.

The ContextPack is serialized into the Gemini API request as a structured system prompt (Sections 1 through 6) plus a user message (Section 7). The structured system prompt is the component that benefits from Vertex AI context caching — the Foundation portion (Section 6) is cached, reducing the input token cost by approximately 90 percent for repeated calls within the cache TTL window.

## **Chapter 3.2 — Foundation Context Caching Strategy**

The Foundation JSON is the most frequently repeated content in the inference pipeline. Every agent invocation for every user includes the Foundation JSON — or the relevant portions of it. Without caching, this repeated content represents a significant and entirely avoidable inference cost.

Vertex AI's explicit context caching API allows content to be cached at the model level. Cached content is billed at 10 percent of standard input token rates. For a Foundation JSON that is 4,000 tokens, the saving per agent invocation is 3,600 tokens — at Gemini 3.1 Flash-Lite Normal pricing ($0.10/1M tokens), this is $0.00036 per invocation. At 200 agent invocations per user per day across all operations, this is $0.072 per user per day in savings — nearly $2.16 per user per month — purely from Foundation caching.

The caching implementation: the Foundation JSON is posted to the Vertex AI caching API at session initialization. The API returns a cache_id. All subsequent inference calls within the session include the cache_id rather than repeating the Foundation content. The cache has a default TTL of one hour. If the session extends beyond one hour, the cache is refreshed.

Foundation content that is not appropriate for caching — content that changes between agents or between calls — is excluded from the cached portion and included in the per-call context. The ICP-specific context for a specific campaign, for example, might be included per-call rather than in the cached Foundation, because different agents may need different ICP emphasis depending on their expertise area.

## **Chapter 3.3 — Agent Isolation in Context Assembly**

The most critical requirement of context assembly is that each agent's context is assembled from that agent's private data and the correctly scoped shared data — not from other agents' private data. A bug in context assembly that leaks one agent's private ripples into another agent's context would corrupt the personality isolation that makes the system valuable.

The isolation is enforced through the ripple retrieval filters in the PRL queries. Every query to the ripples table includes an agent_id filter for private data and an explicit scope filter for shared data. The Context Assembler constructs these queries using the agent_id from the current AvatarState — it cannot accidentally query another agent's private data because it uses the agent_id from the AvatarState rather than from any external source.

The second isolation point is the EEL data. Each agent's Essence Core, Ego Signature, and Skill Weave are loaded from their specific agent_essences record. The AvatarState HashMap is keyed by agent_id, and the Context Assembler always accesses the correct agent's AvatarState by using the agent_id as the HashMap key.

A defense-in-depth measure: the Rust borrow checker prevents direct memory access violations. The type system enforces that AvatarState objects are accessed through their proper ownership chain. Even if the Context Assembler had a logic bug that caused it to use the wrong agent_id, the borrow checker would prevent it from accessing data through an invalid reference. This is one of the reasons Rust is the correct language for the Harness: the type system provides isolation enforcement that garbage-collected languages cannot.

# **Part Four: The Inference Layer**

## **Chapter 4.1 — The Vertex AI Client Configuration**

The Harness maintains three Vertex AI client configurations — one per model tier — pre-configured with the appropriate model endpoint, authentication credentials, streaming settings, and safety filter configuration. These clients are initialized at application startup and stored in the application state for reuse across sessions.

The Pro client configuration: model endpoint gemini-3-1-pro-002 (or the current stable Pro model identifier), temperature 0.7 for strategic reasoning tasks, top_p 0.95, max_output_tokens 8192, streaming enabled, safety filters at the standard threshold (not maximum — maximum safety filters occasionally reject legitimate business content).

The Flash-Lite Reasoning client configuration: model endpoint gemini-3-1-flash-lite-reasoning-001, temperature 0.6 for Council avatar positions (slightly lower than Pro to encourage more consistent character), top_p 0.90, max_output_tokens 4096, streaming enabled.

The Flash-Lite Normal client configuration: model endpoint gemini-3-1-flash-lite-001, temperature 0.5 for content generation and classification tasks, top_p 0.85, max_output_tokens 2048, streaming enabled for generation tasks, streaming disabled for classification and analysis tasks where the complete response is needed before processing.

Authentication uses a service account credentials file stored in AWS Secrets Manager. The credentials are loaded at application startup and cached in memory. A background task refreshes the credentials before they expire, typically every 55 minutes for credentials with one-hour expiry.

## **Chapter 4.2 — Constructing the Inference Request**

The inference request construction takes the ContextPack and produces a Vertex AI API request struct. The construction is deterministic given the same ContextPack — there is no randomness in request construction beyond the temperature parameter in the client configuration.

The request construction for a Council avatar position call: the system message is constructed from Sections 1 through 6 of the ContextPack, structured as a JSON object with named sections. The structure: identity section as a JSON object with constitutional_principles and core_beliefs arrays, emotional_register section with dominant_emotion and tonal_directive strings, procedural_knowledge section with an array of up to 3 skill procedure objects, episodic_memory section with an array of up to 10 ripple summaries, associative_memory section with an array of up to 5 ripple summaries, and shared_context section with the Foundation relevant fields and campaign context.

The user message is Section 7 — the current task — structured as plain text with clear formatting. For a Council debate position, the user message is: 'Council question: \[question\]. Based on your identity, expertise, and relevant memories, provide your position on this question. Be specific. Reference your relevant experience where applicable. Maintain your characteristic voice and convictions.'

The cache_id from the Foundation cache is included in the request metadata. The session_id is included as a tracking identifier for cost attribution.

## **Chapter 4.3 — Streaming Response Handling**

The Gemini streaming API returns a Server-Sent Events stream of token chunks. The Harness consumes this stream asynchronously using a Tokio async reader and processes each chunk as it arrives.

Each chunk from the Gemini API is a JSON object containing: the generated text token or tokens in this chunk, the finish_reason (null for in-progress, 'STOP' for complete, 'MAX_TOKENS' for truncation, 'SAFETY' for safety filter triggered), and cumulative token usage statistics.

The Stream Coordinator processes each chunk: it extracts the text content, publishes it to the DragonflyDB pub/sub channel with the message format {type: 'token', agent_id: agent_id, token: token_text, session_id: session_id}, and appends the token to the in-memory response accumulator for the current agent. When the finish_reason is STOP, the Stream Coordinator publishes a completion message {type: 'complete', agent_id: agent_id, full_response: accumulated_response, session_id: session_id} and signals the inference router that this agent's stream is complete.

Backpressure handling: DragonflyDB pub/sub does not provide backpressure — published messages are delivered immediately and not buffered per subscriber. If the WebSocket connection cannot consume messages as fast as they are published, the Axum WebSocket handler uses a bounded channel (capacity 128 messages) between the DragonflyDB subscriber and the WebSocket sender. If this channel is full, message publication blocks the Stream Coordinator until the consumer catches up. This prevents unbounded memory growth from fast producers and slow consumers.

## **Chapter 4.4 — The Fan-Out Pattern for Council Sessions**

A Council session requires concurrent inference across multiple agents simultaneously. The fan-out pattern manages this concurrency correctly — ensuring that all agents start simultaneously, that each agent's stream is correctly identified, and that the synthesis does not begin until all agent streams are complete.

The fan-out implementation using Tokio: a JoinSet is created for all participating agents. For each agent, a Tokio task is spawned that performs the context assembly and inference call for that specific agent. The task takes ownership of the agent's AvatarState reference for the duration of its execution. All tasks are spawned before any await points, ensuring that all inference calls begin simultaneously rather than sequentially.

The JoinSet::join_next() method is then called in a loop to collect results as they complete. Agent streams do not complete at the same time — some agents generate longer responses than others, some models return tokens faster than others. The loop collects each agent's result as it completes rather than waiting for all to complete before processing any. As each agent's result is collected, it is stored in the SessionContext for use in the synthesis context.

When the JoinSet is exhausted — when all agents have completed — the synthesis context assembly begins. The synthesis context includes the complete responses from all agents, structured as an array of {agent: agent_name, position: full_response} objects. The Strategist's synthesis call begins only after all agent streams are complete.

Timeout handling: each agent inference task has a timeout of 30 seconds. If an agent's inference call does not complete within 30 seconds — due to Gemini API latency, content safety review, or other delays — the task is cancelled and the agent's position is marked as timeout in the session. The synthesis proceeds with the available agent positions. The timeout is implemented using tokio::time::timeout wrapping the inference call.

## **Chapter 4.5 — Tool Access Enforcement**

Tool access is enforced through the Tool Gateway, which is implemented as a Rust enum that prevents agents from calling tools they do not have access to at the type level.

The ToolRequest enum has variants for each available tool: WebSearch(WebSearchParams), FileRead(FileReadParams), EmailSend(EmailSendParams), CalendarAccess(CalendarParams), Calculator(CalculatorParams), and StorageAccess(StorageParams). Each variant has a distinct parameter type that contains only the parameters relevant to that tool.

The AgentTier enum classifies each agent: Strategist, CouncilAvatar, Intern, or SupportSpecialist. The Tool Gateway's execute function signature is: async fn execute(tool: ToolRequest, tier: AgentTier) -> Result&lt;ToolResult, ToolError&gt;. The function body begins with a tier check: if the tool variant is not permitted for the tier, the function returns a ToolError::Unauthorized immediately, before any tool execution occurs.

The permitted tools per tier: Strategist may call all tools. CouncilAvatar may call WebSearch only, and only through their intern dispatch mechanism (they do not call WebSearch directly — they request an intern to execute a search task). Intern may call WebSearch only. SupportSpecialist may call Calculator, WebSearch (limited), and StorageAccess for their specific storage scope.

The intern dispatch mechanism is important: Council avatars do not call the Tool Gateway directly. When a Council avatar needs web search, it generates an InternTask struct that specifies the search query and the expected output format. This task is dispatched to the intern pool, where an intern executes the search through the Tool Gateway and returns the result to the requesting avatar. This indirect mechanism preserves the fiction of the office — interns do the legwork, avatars do the thinking — while correctly routing tool access through the proper tier.

# **Part Five: The Complexity Router**

## **Chapter 5.1 — How the Router Works**

The Complexity Router determines which agents should participate in any given operation and what session tier the operation represents. It is invoked before context assembly begins and produces an AgentSelection struct that specifies the participating agents, the session tier, and any agent-specific configurations for this session.

The router uses a multi-signal assessment that combines: the request content (what is being asked), the current campaign context (what phase is the campaign in), the user's recent interaction history (what types of operations they have been initiating), and the user's usage budget remaining for the current period.

### **Signal 1: Request Content Analysis**

The request content is analyzed using a lightweight Flash-Lite Normal classification call that identifies: the domain of the question (creative, strategic, analytical, operational), the stakes involved (high-stakes positioning decision vs routine content request), the number of distinct expert perspectives that would genuinely improve the output, and whether the question is well-defined (allowing for precise agent selection) or exploratory (potentially benefiting from a broader Council).

This classification call uses a structured output format: {domain: string, stakes: 'routine' | 'moderate' | 'high' | 'critical', perspectives_needed: number, question_clarity: 'clear' | 'exploratory'}. The classification is inexpensive — under 200 tokens input, under 50 tokens output — and completes in under one second.

### **Signal 2: Agent Relevance Scoring**

Each of the 12 Council avatars and 8 support specialists is scored for relevance to the current request using their domain_tags and a brief description of the request. The scoring function: relevance = sum of matching domain_tags / total domain_tags × request_alignment_bonus. The request_alignment_bonus is 1.5 for agents whose Essence Core constitutional principles directly address the request domain, 1.0 for relevant agents, and 0.5 for tangentially relevant agents.

Agents with relevance below 0.25 are excluded from the candidate set. From the remaining candidates, agents are selected in relevance order up to the tier maximum.

### **The Four Tiers**

Tactical tier (2 to 3 agents): routine content requests, specific tactical questions with clear answers, quick feedback on a specific creative element. Typical Tactical sessions: Muse routes a specific copy question to Ogilvy plus Hopkins, a headline review request goes to Ogilvy plus Bernbach, a Meta ad structure question goes to Patel plus the Media Buyer.

Operational tier (3 to 5 agents): Move planning for a specific campaign phase, channel mix strategy for a specific period, content calendar design for a quarter. Typical Operational sessions: campaign Move planning involves the Strategist plus 3 to 4 relevant Council members.

Strategic tier (5 to 8 agents): full Campaign planning, positioning review, new market entry assessment. Typical Strategic sessions: Campaign planning for a major launch involves the Strategist plus 6 to 8 Council members representing all relevant expertise domains.

War Room tier (8 to 13+ agents): major business pivots with marketing implications, annual marketing strategy, competitive crisis response, significant underperformance assessment. Typical War Room sessions: all 12 Council avatars participate plus potentially relevant support specialists.

## **Chapter 5.2 — User Override**

Users can override the router's agent selection. The Council UI shows the router's recommendation and allows the user to add or remove agents before the session begins. The override is respected completely — if a user adds Godin to a session the router determined did not need him, Godin participates. If a user removes Hopkins, Hopkins does not participate.

Override history is tracked and contributes to the router's personalization over time. A user who consistently adds Sharp to sessions the router did not initially include will see Sharp appear more frequently in the router's suggestions for similar session types. A user who consistently removes Kotler will see Kotler recommended less often.

The override personalization is implemented by storing override events as preference ripples in the Strategist's PRL — the Strategist learns this user's Council composition preferences over time and the router uses the Strategist's preference ripples as an additional signal in its selection.

# **Part Six: WebSocket Architecture for Streaming**

## **Chapter 6.1 — The WebSocket Connection Lifecycle**

A single persistent WebSocket connection serves all streaming needs for a user session. The connection is established when the user authenticates and loads the dashboard. It persists for the duration of the user's session in the application. It is used for all streaming operations: Council debates, Muse responses, content generation, intelligence alerts, and office event animations.

The Axum WebSocket handler upgrades the HTTP connection at the /ws endpoint. After upgrade, the handler validates the auth token from the connection query parameters, creates a WebSocket sender and receiver pair, registers the sender with the Session Manager, and begins the message routing loop.

The message routing loop: the Axum WebSocket receiver waits for client messages (user actions that trigger new operations), processes them by dispatching to the appropriate Harness component, and returns to waiting. Meanwhile, the DragonflyDB subscriber is publishing messages from active inference streams. The WebSocket sender is subscribed to all channels relevant to this user's session and forwards any received messages to the WebSocket connection.

This architecture — WebSocket for client-to-server and DragonflyDB pub/sub for server-to-client — decouples the WebSocket connection from the inference operations. An inference operation does not need to hold a reference to the WebSocket connection while it runs. It publishes to a channel and the WebSocket handler delivers the messages. This makes the system robust to WebSocket reconnections during active inference — the inference continues publishing to the channel and the reconnected WebSocket handler begins consuming from the channel where it left off.

## **Chapter 6.2 — The Message Protocol**

All WebSocket messages use a JSON envelope with a consistent structure: {type: string, session_id: string, payload: object}. The type field identifies the message type. The session_id identifies which session the message belongs to (allowing multiple sessions to be multiplexed on a single WebSocket connection if needed). The payload contains the message-specific data.

Server-to-client messages: council.agent_start (signals that a specific agent has begun generating, includes agent_id and agent_display_name), council.token (a streaming token from a specific agent, includes agent_id and token string), council.agent_complete (signals that a specific agent has finished, includes agent_id and word_count), council.synthesis_start (signals synthesis has begun), council.synthesis_token (streaming token from synthesis), council.complete (signals the full Council session is complete, includes a summary of participating agents and completion time), muse.token (streaming Muse response token), muse.complete (Muse response complete), content.token (streaming content generation token), content.complete (content generation complete with compliance score), intel.alert (competitive intelligence alert), office.event (office animation trigger event), nudge.new (new nudge available), daily_wins.ready (Daily Wins briefing is ready).

Client-to-server messages: council.start (trigger a Council session, includes question and optional agent_list), council.override_agents (update agent list before session begins), muse.send (send a message to Muse, includes message and optional context), content.generate (trigger content generation, includes type and parameters), office.mode (switch between active and passive office modes), presence.ping (keepalive ping to maintain WebSocket connection).

## **Chapter 6.3 — DragonflyDB Pub/Sub Channels**

The pub/sub channel naming convention follows a pattern that allows selective subscription based on session and message type. The Axum WebSocket handler subscribes to all channels relevant to the current user's session using pattern subscription.

Channel naming: council:{session_id}:{agent_id} for individual agent streams during Council sessions; council:{session_id}:synthesis for the synthesis stream; muse:{session_id} for Muse response streams; content:{session_id}:{generation_id} for content generation streams; office:{org_id} for office animation events (org-scoped rather than session-scoped, because office events continue between sessions); intel:{org_id} for intelligence alerts; nudge:{user_id} for user-specific nudges.

Pattern subscription: the WebSocket handler subscribes using the pattern council:{session_id}:\*, which matches all Council channel variants for the current session. This allows a single subscription to receive tokens from all participating agents and the synthesis without needing to know in advance which agents will participate.

Channel cleanup: when a session ends, all session-scoped channels are deleted from DragonflyDB. The org-scoped channels (office and intel) persist indefinitely. The DragonflyDB memory footprint is bounded by the number of active sessions rather than growing with the history of all sessions.

# **Part Seven: The Event Harvester — Closing the Learning Loop**

## **Chapter 7.1 — What Gets Harvested**

The Event Harvester runs at the end of every session. Its job is to identify the meaningful events from the session's outputs and create the appropriate ripples in the PRL. The harvester is not a simple transcript logger. It is a semantic analysis process that extracts the events worth remembering from the full session activity.

The harvester processes four categories of session output. First: agent position content. Each Council avatar's response is analyzed to identify the core claim, the key reasoning, and any predictions embedded in the position. These become episodic ripples in each agent's private PRL stream. Second: debate dynamics. The relationship between agent positions — which agents agreed, which disagreed, how dramatically they disagreed — produces shared_campaign ripples that capture the debate's strategic substance. Third: synthesis outcomes. The Strategist's synthesis is the most important content of any Council session. It produces multiple ripples: a shared_campaign ripple capturing the synthesis recommendation, a strategist_only ripple capturing the Strategist's confidence in the synthesis, and prediction ripples for any claims in the synthesis that can be validated against future performance data.

Fourth: emotional events. The emotional character of the session — the specific events that moved avatars' emotional states significantly — produces affective ripples that contribute to the ego_state update and to the emotional memory of the session.

## **Chapter 7.2 — The Harvesting Process**

The harvesting process runs as a series of Flash-Lite Normal inference calls that analyze the session content. Each call takes a portion of the session content and produces structured output that the harvester uses to construct MemoryEvent structs.

Call 1: position analysis. Input: the full text of each agent's response. Output: for each agent, a structured summary of their core claim, supporting reasoning, key assumptions, and any implicit predictions. This call uses batch mode — all agent responses are sent in a single batch request to reduce latency and cost.

Call 2: debate dynamics analysis. Input: all agent responses plus the synthesis. Output: a structured summary of the key agreements, key disagreements, notable position shifts if any occurred during the debate, and the Strategist's synthesis assessment (what elements of which positions were incorporated and why). This call runs after Call 1 because it requires the position summaries to be complete.

Call 3: prediction extraction. Input: the synthesis and any high-confidence agent positions. Output: a list of implicit predictions — claims that can be evaluated against future performance data. For each prediction: the claim text, the expected outcome, the timeframe, and the participating agents who made the prediction. This list is used to populate the prediction_json fields of the relevant ripples.

The Flash-Lite Normal inference cost for the harvesting calls: approximately $0.0002 per Council session across all three calls — less than a cent for the complete learning process of every Council session.

## **Chapter 7.3 — Ego State Update After Session**

After the ripples are created and submitted to the PRL ingest pipeline, the Event Harvester computes the ego_state update for each participating agent and writes it back to agent_essences.

The ego_state update process: for each agent, collect all the emotion_vector fields from the ripples created by that agent during this session. Compute the aggregate emotional impact of the session by summing the deltas across all ripples, weighted by their salience scores. Apply the aggregate delta to the pre-session ego_state using the ego multipliers. Apply the decay function to move the updated state partway toward the baseline. Write the final ego_state back to agent_essences using an UPDATE query.

The write is performed as a single UPDATE that sets the ego_state, last_active_at, and any reflection field updates (if the VFE crossed the threshold during the session). The UPDATE is atomic — either all fields are updated or none are — preventing partial ego_state updates that would leave the agent in an inconsistent state.

# **Part Eight: Background Operations**

## **Chapter 8.1 — The Cron Scheduler**

The Harness includes a cron scheduler implemented with the tokio-cron-scheduler crate. The scheduler runs all background operations that do not require real-time user interaction: SWR consolidation, Daily Wins generation, competitive intelligence scans, Nudge evaluation, and usage aggregation.

The scheduler is configured at application startup with all scheduled jobs and their cron expressions. All cron expressions use IST (Indian Standard Time, UTC+5:30) as the reference timezone, because the user base is primarily Indian and daily operations should align with Indian business hours.

Daily Wins generation schedule: 04:00 IST (6 AM IST minus 2 hours for processing time — the briefing is generated at 4 AM to be ready by 6 AM). SWR consolidation schedule: 02:00 IST (chosen to minimize overlap with daily usage peaks). Competitive website scanning schedule: every 24 hours starting at 01:00 IST. Social monitoring schedule: every 6 hours starting at 00:00 IST. Ad library monitoring schedule: every 12 hours starting at 00:30 IST. Nudge evaluation schedule: every 2 hours. Usage aggregation schedule: 23:30 IST.

Each scheduled job runs as a Tokio task spawned by the scheduler. The scheduler maintains a job registry that tracks which jobs are currently running, preventing the same job from being started twice if the previous run is still ongoing. If a job runs longer than its scheduled interval, the scheduler logs a warning and skips the next scheduled run.

## **Chapter 8.2 — The SWR Consolidation Job**

The SWR consolidation job is the most computationally intensive background operation and must be designed to run efficiently without impacting the application's responsiveness to user requests.

The consolidation job acquires a per-org distributed lock from DragonflyDB before beginning. The lock prevents two consolidation runs from occurring for the same org simultaneously — which could happen if the scheduled run starts while a previous run is still in progress. Lock acquisition uses SET NX EX to create the lock with a 35-minute expiry, ensuring the lock is automatically released even if the job crashes before completing.

The consolidation job processes each org sequentially — not concurrently across orgs — to prevent Aurora from being overwhelmed by simultaneous heavy read-write operations from many orgs. Within each org, the five consolidation phases (replay selection, edge strengthening, BARR suppression, lesson distillation, predictive compression) run sequentially. The total runtime for a typical org with 10,000 ripples is 5 to 8 minutes. At 100 orgs, the full consolidation run takes 8 to 13 hours — which is why the 02:00 IST start time ensures it completes before the morning peak.

As the user base scales beyond the single-server consolidation capacity, the job architecture shifts to use multiple workers: orgs are assigned to workers based on a consistent hash of the org_id, ensuring each org always runs on the same worker without coordination overhead.

## **Chapter 8.3 — Daily Wins Generation**

Daily Wins generation runs at 04:00 IST for all orgs. It uses the batch API to submit all org briefing generation requests simultaneously and collect the results over the next 1 to 2 hours.

The batch generation process: for each org, assemble the briefing context (recent performance data, overnight intelligence alerts, active campaign status, Foundation relevant fields). Submit all briefing generation requests as a single batch to the Vertex AI batch API endpoint. The batch API guarantees 50 percent cost reduction and can process requests asynchronously over up to 24 hours, though typical processing time is under 2 hours.

Briefing generation uses Flash-Lite Normal with the structured output format. The Strategist's persona — the specific personality calibrated during Screen 21 — is included in the generation context so the briefing sounds like the user's specific Strategist rather than a generic AI assistant.

Completed briefings are written to the daily_wins table in Aurora and a WebSocket message (daily_wins.ready) is queued for delivery when the user next opens the app. The message is delivered through the persistent WebSocket connection if the user is currently active, or queued in DragonflyDB for delivery on the next connection.

# **Part Nine: The Autonomous Agent Operation**

## **Chapter 9.1 — Agents Working Without User Presence**

One of the most powerful features of the Harness is that agents can do meaningful work without the user being present. The intelligence pipeline runs continuously. SWR consolidation strengthens the agents' memories. The Daily Wins briefing is generated before the user wakes up. Competitive alerts are generated as soon as significant events are detected.

This autonomous operation is the product experience that makes the office metaphor feel most real: users arrive to a workspace where work has been happening in their absence. The inbox has items. The intelligence has been gathered. The agents have been thinking.

The Harness supports autonomous operation through several mechanisms. Background Tokio tasks run continuously and do not depend on active WebSocket connections. The DragonflyDB notification queue stores messages for delivery when the user next connects. The Daily Wins is ready before the user opens the app. The competitive monitoring scans run on their schedule regardless of user activity.

## **Chapter 9.2 — Dynamic Campaign Replanning**

Campaign replanning is the most complex autonomous operation in the Harness. It is triggered by specific system events — a missed task, a significant competitive change, a KPI deviation — and involves a full mini-Council session that the user is notified of but does not need to actively participate in.

The replanning trigger evaluation runs as part of the Nudge evaluation job (every 2 hours). For each active campaign, the evaluator checks three conditions: whether any tasks are overdue by more than 24 hours, whether the intel pipeline has generated any high-priority competitive alerts that affect this campaign, and whether any performance metric has deviated more than 20 percent from the campaign's projections.

When a replanning trigger is identified, the Harness creates a replanning session. Unlike a user-initiated session, a replanning session does not require a WebSocket connection. It runs as a background Tokio task, assembles the necessary agent contexts, runs the relevant Council positions (typically 3 to 5 agents most relevant to the trigger type), generates a Strategist synthesis of the replanning recommendation, and stores the result in the database.

The result appears in the user's interface as a Campaign Alert Nudge: 'Your \[Campaign Name\] has been adjusted based on \[trigger reason\]. Here is what changed and why.' The user can review the changes, accept them, or request modifications. If the user does not respond within 48 hours, the recommended adjustments are auto-applied with a note that they can be reversed at any time.

The autonomous replanning is one of the clearest demonstrations of the compounding value proposition. An agent system without persistent memory cannot do autonomous replanning — it lacks the context to understand what the original plan was, why it was created, and how the new situation changes its rationale. The PRL provides exactly this context: the campaign planning ripples contain the original strategic reasoning, the intelligence ripples contain the detected change, and the synthesis produces a recommendation that accounts for both.

# **Part Ten: Build Sequence and Validation**

## **Chapter 10.1 — The Recommended Build Order**

Building the complete Harness correctly requires following a build order that respects the dependencies between components. The following sequence ensures that each component is built on a solid foundation and can be tested before the next component is added.

Phase 1 — Infrastructure (Prerequisite): Aurora tables created and RLS-enabled, DragonflyDB instance running, Qdrant instance running, Vertex AI credentials configured, basic Axum server running with authentication middleware. This phase should be complete before any Harness components are built.

Phase 2 — Session Manager: implement the SessionContext struct, the AvatarState struct, the session initialization sequence (sequential and concurrent phases), and the session persistence logic. Test with a single agent (the Campaign Strategist) loading correctly and ego decay being applied. Verify that the AvatarState correctly reflects the loaded agent_essences record.

Phase 3 — Context Assembler (minimal): implement the ContextPack struct, the Foundation cache loading from DragonflyDB, and the basic context construction from Essence Core content only (no PRL retrieval yet). Test that a minimal ContextPack can be constructed for the Strategist. Verify that the Foundation content is correctly included and cached.

Phase 4 — Inference Router (single model): implement the API request construction for Flash-Lite Normal only. Implement the streaming response handler. Test with a simple Muse-style request that produces a streaming response. Verify that tokens are published to DragonflyDB and deliverable via WebSocket.

Phase 5 — Tool Gateway: implement the ToolRequest enum, the AgentTier enum, and the access enforcement logic. Implement WebSearch as the first tool. Test that Council avatar tier correctly rejects direct WebSearch calls and only Intern tier can call it through the Gateway.

Phase 6 — CORTEX Retrieval Integration: add PRL retrieval to the Context Assembler. Implement all five passes. Test that the ContextPack correctly includes retrieved ripples from all five passes within the 10-millisecond target.

Phase 7 — Multi-Agent Fan-Out: implement the JoinSet-based Council fan-out. Test with a 3-agent Tactical session. Verify that all agents' streams are correctly identified in the WebSocket output and that the synthesis does not begin until all agents complete. Test timeout handling.

Phase 8 — Event Harvester: implement the harvesting process and the ego_state update. Test with a completed Council session and verify that the correct ripples are created in Aurora and that the ego_state updates are correctly written to agent_essences.

Phase 9 — Complexity Router: implement the request content classification call and the agent relevance scoring. Test with various request types and verify that the router produces appropriate agent selections. Test the user override mechanism.

Phase 10 — Background Operations: implement the cron scheduler and all scheduled jobs. Test Daily Wins generation with a mock org. Test SWR consolidation with a populated ripple set. Verify that the consolidation correctly identifies and processes high-salience ripples.

## **Chapter 10.2 — Key Validation Tests**

Several validation tests are essential for confirming that the Harness is operating correctly before production deployment. These tests should be run after each phase and after any significant change to the Harness.

Isolation test: create two orgs with similar content. Verify that ripples from Org A never appear in retrieval results for Org B. Verify that agent_essences from Org A are never loaded in sessions for Org B. This test must pass with 100 percent reliability — any failure indicates a fundamental isolation breach.

Agent isolation test: within a single org, verify that private ripples for Agent A never appear in retrieval results for Agent B. Verify that Agent A's ego_state is correctly maintained independently of Agent B's. This test must also pass with 100 percent reliability.

Personality stability test: run 50 sequential Council sessions with the same question for each of the 12 Council avatars. After 50 sessions, verify that each avatar's response to the same question is semantically closer to their Essence Core than to any other avatar's Essence Core. If avatars are converging — producing increasingly similar outputs — the EEL isolation is failing.

Streaming latency test: measure the time from user request submission to first token received by the frontend. Target: under 800 milliseconds for Muse single-agent responses, under 1.5 seconds for Council first-agent responses. Test under concurrent load with 50 simultaneous sessions to verify that latency does not degrade significantly under load.

Cost accuracy test: run 100 inference sessions of known composition and measure the actual Vertex AI cost against the predicted cost from the 20/80 routing model. Verify that the routing is correctly applying the model tiers and that the caching mechanism is reducing costs as expected. Acceptable variance: plus or minus 10 percent from predicted cost.

Memory persistence test: run a Council session, complete the session, close the WebSocket connection, wait 5 minutes, reconnect, and run the same session question again. Verify that the second session's agent contexts correctly reflect the memories created in the first session — that the EEL decay has been applied and that the new ripples from the first session are available in CORTEX retrieval. This test validates the complete lifecycle of the memory persistence system.