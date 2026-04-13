**RAPTORFLOW**

MASTER DOCUMENT SERIES

**VOLUME FIVE**

**The Predictive Ripple Lattice**

_Complete technical and conceptual specification — what ripples are, how they are born, stored, connected, retrieved, consolidated, and how the whole system produces genuine machine intelligence over time_

CONFIDENTIAL — INTERNAL BLUEPRINT

# **Opening: Memory Is Not Storage**

Every implementation mistake in the PRL begins with the same misunderstanding: treating the system as a storage and retrieval mechanism. It is not. A storage mechanism keeps things and returns them when asked. The PRL keeps experiences and surfaces them when relevant. These are radically different operations requiring radically different architecture.

A database stores records. A person remembers experiences. When you retrieve a database record, you get back exactly what was stored: a tuple of values at a fixed schema. When a person remembers an experience, they get back a reconstruction — the event filtered through the emotional state of the moment it happened, connected to other experiences that were contextually active, shaped by everything learned since that event, weighted by how many times it has been accessed, and modified by whether predictions made at the time turned out to be correct.

The PRL is designed to make the second type of memory possible in a software system. Every design decision — from the structure of the ripple schema to the five-pass retrieval architecture to the SWR consolidation algorithm — follows from this single design intent. When the intent is clear, the decisions become obvious. When it is forgotten, the system degrades into an expensive database.

This volume describes the PRL completely. It covers the philosophical foundation, every data structure, every algorithm, every timing constraint, every cost consideration, and every failure mode. Read it before writing a single database migration. The schema follows from the concepts. Get the concepts right first.

# **Part One: The Philosophical Foundation**

## **Chapter 1.1 — What a Ripple Is Versus What a Database Entry Is**

The distinction between a ripple and a database entry is the most important concept in this entire volume. It will be stated once completely here and referenced throughout.

A database entry is a record the system created. It has a schema because the system knows what type of record this is. It has a primary key because the system needs to retrieve it by identifier. It has foreign keys because it relates to other records in defined ways. It has no emotional content because databases do not have feelings. It has no prediction content because databases do not anticipate the future. It exists because the system needed to store something for later retrieval.

A ripple is a memory an agent experienced. It has a schema because all experiences share a common cognitive structure. It has an identifier because the system needs to track it. It has edges because experiences are never isolated — they are always connected to the context in which they occurred and to other experiences with which they are associated. It has emotional content because the emotional state at the moment of experience is part of what makes experiences memorable. It has prediction content because every meaningful experience involves some expectation of what would happen, and the gap between expectation and reality is the primary driver of learning. It exists because something meaningful happened and it would be a mistake to forget it.

_The ripple schema is not a technical choice about data organization. It is a model of how meaningful experience is structured in cognitive systems that learn from experience. Every field in the schema represents something that cognitive science tells us is essential to how memory functions. Fields that do not have this grounding should not be in the schema._

This distinction has a practical implication that must be understood before implementation: not every event in the system produces a ripple. Most events do not. Token generation does not produce ripples. Direct Foundation data retrieval does not produce ripples. HTTP request handling does not produce ripples. Scheduled job execution does not produce ripples. The system is not building a log of everything that happened. It is building a record of the meaningful experiences that shaped each agent's understanding of the world.

The question that determines whether an event should produce a ripple is: does this event change what the agent knows or believes in a way that should affect how it behaves in the future? If yes, it is a ripple event. If no, it is an operational event that belongs in the system log, not in the memory system.

## **Chapter 1.2 — The Predictive Coding Grounding**

The PRL is grounded in predictive coding — a theory of how biological brains learn and remember that has strong empirical support and practical implications for how the PRL should be architected. Understanding predictive coding at a conceptual level is essential for understanding why the PRL is designed the way it is.

Predictive coding proposes that the brain is not a passive observer that records what happens and stores it. The brain is an active predictor that continuously generates expectations about what will happen next, compares those expectations to what actually happens, and updates its model of the world based on the difference — the prediction error. Memories are not faithful recordings of events. They are the residue of learning — the updates to the brain's model that were required when reality differed from prediction.

This model has several implications that are directly implemented in the PRL. First, prediction is as important as observation. Every meaningful event should have a prediction attached to it at the time it occurs — what did the agent expect would happen? Second, prediction error is the primary signal for learning. The bigger the gap between prediction and reality, the more the experience should update the model. Third, events that confirm expectations are less memorable than events that violate them — confirmation requires no model update and produces less memory trace. Fourth, memories are not static — every time a memory is retrieved and used in a new context, it is potentially updated by the new information.

The PRL implements all four implications. Every ripple carries a prediction field — what the agent expected would follow from this experience. Every ripple is eventually updated with an actual field — what actually happened. The prediction error is computed from these two fields and stored. The salience of the ripple is partially determined by this prediction error — more surprising events become more salient memories. And the retrieval process is designed to allow memories to be strengthened or weakened based on subsequent experience, not just accessed.

## **Chapter 1.3 — The Four Hierarchy Levels**

The PRL organises ripples into four levels of abstraction that correspond to increasing levels of cognitive processing. These levels are not arbitrary — they reflect the hierarchical structure of memory systems in cognitive science, where raw sensory experience is processed into progressively more abstract representations at each level.

Level One ripples are raw inputs: unprocessed observations of events in the world. A competitor's ad text extracted from the ad library. A user's exact words in a Muse conversation. A campaign performance metric at a specific point in time. Level One ripples are the most concrete, the most specific, and the most transient. They decay fastest if not referenced by higher-level ripples because raw observations without interpretation have limited long-term value.

Level Two ripples are features and facts: the first layer of interpretation applied to raw observations. 'Competitor X has launched a new ad campaign targeting the same ICP we serve, using urgency-based copy with discount offers.' This is a Level Two interpretation of several Level One observations. Level Two ripples have moderate durability — they are retained as long as they remain relevant to active campaigns or ongoing intelligence needs.

Level Three ripples are abstractions: patterns and interpretations that emerge from multiple Level Two facts. 'This ICP segment responds significantly better to social proof framing than to urgency framing, which explains the underperformance of our last three discount-based campaigns relative to our testimonial-based campaigns.' This is a Level Three ripple — a pattern extracted from multiple Level Two data points that has strategic implications. Level Three ripples are among the most durable in the system because they represent genuine strategic learning.

Level Four ripples are predictions and identity anchors: the highest-level representations in the system. 'For this client's audience, the copy approach that will consistently outperform alternatives is research-backed benefit claims with specific social proof.' This is a Level Four ripple — a predictive model of how this specific audience behaves, derived from accumulated Level Three patterns and anchored to the avatar's Essence Core. Level Four ripples are the most durable and the most protected. They are where the Essence Core lives.

The hierarchy is not just organisational. It determines retrieval behavior, decay rates, the relationship between ripples, and how learning propagates through the system. When a Level Four prediction turns out to be wrong — when reality consistently violates the high-level model — the error propagates downward through the hierarchy, weakening the Level Three patterns that supported the prediction, which weakens the Level Two facts that supported those patterns, and so on. The hierarchy is a learning cascade.

# **Part Two: The Complete Ripple Schema**

## **Chapter 2.1 — The Core Ripple Table**

Every ripple in the system is stored as a row in the ripples table in Aurora Serverless v2. The schema represents the complete cognitive structure of a memory event. Every field is here for a reason grounded in the philosophical foundation. Every field will be described in terms of what it represents conceptually, what it stores technically, and how it is used by the retrieval and learning systems.

### **Identity Fields**

ripple_id is a ULID — Universally Unique Lexicographic Identifier. ULIDs are chosen over UUIDs because they are time-sortable: the first ten characters encode the creation timestamp in millisecond precision, making the identifier itself a sortable record of creation order without requiring a separate timestamp for basic ordering. This matters for working memory management, where recency is a primary sort criterion.

org_id is a UUID representing the tenant. This field is on every row in every table in the system and is the foundation of Row Level Security. Every query to the ripples table includes org_id as a filter condition. The RLS policy enforces this at the database level even if application code omits the filter.

agent_id is a UUID representing the specific avatar who owns this ripple. This is the finest-grained scope of memory: private ripples are owned by a specific agent and are not visible to other agents. The agent_id determines which avatar's Essence Core is used as the anchor for Level Four ripples, which avatar's ego signature contributed to the emotional coloring, and which avatar's skill weave should be updated if this ripple represents skill-relevant learning.

campaign_id is a nullable UUID. When a ripple is created in the context of a specific campaign, this field links it to that campaign. Campaign-scoped ripples are retrieved with elevated priority when the same campaign is the context of a new request. When a campaign is archived, its campaign-scoped ripples are not deleted — they remain available for retrieval and for pattern learning — but their retention priority is adjusted.

session_id is a UUID representing the work session in which this ripple was created. Sessions are the working memory scope: ripples from the current session have elevated retrieval priority, and the set of ripples from a session can be retrieved as a coherent group for session replay during SWR consolidation.

### **Classification Fields**

scope is a text field with one of five values: private_agent, shared_campaign, shared_org, user_preference, and strategist_only. Private_agent ripples are visible only to the creating agent. Shared_campaign ripples are visible to all agents working on the same campaign. Shared_org ripples are visible to all agents in the org — these are rare and typically represent information about the business itself that all agents need. User_preference ripples are a special class that capture explicit user preferences and are protected from decay. Strategist_only ripples are accessible only to the Campaign Strategist — typically strategic intelligence that the Strategist uses in synthesis but that would create unwanted bias if shared with Council avatars before they have formed their own positions.

memory_class is a text field classifying the type of memory. The seven memory classes are: working (currently active, session-scoped, decays after session), preference (user or avatar preference, highly protected from decay), procedural (how to do something, represents skill knowledge), episodic (a specific event that happened at a specific time), semantic (general knowledge about the world, less time-bound than episodic), affective (primarily emotional content, the emotional texture of an experience), and identity (core beliefs and convictions, the Essence Core). Each class has different default retention behavior, different decay rates, and different retrieval weighting.

hierarchy_level is a smallint from 1 to 4, representing which level of the cognitive hierarchy this ripple occupies. This field determines which other ripples this ripple can meaningfully link to, what decay rate applies, and how the ripple is weighted in retrieval scoring.

event_type classifies what kind of event produced this ripple: tool_result, debate_verdict, user_input, prediction_resolved, preference_detected, performance_data, competitive_signal, content_generated, or content_evaluated. The event type shapes how the ripple is processed during ingest — different event types have different salience scoring parameters and different edge-linking behaviors.

### **Content Fields**

trigger_text stores what caused this ripple to be created. For a debate_verdict ripple, this is the question or brief that triggered the debate. For a user_input ripple, this is the user's actual message. For a performance_data ripple, this is the metric event that crossed a significance threshold. The trigger text is used during retrieval: when the current context is semantically similar to past trigger texts, the associated ripples are retrieved with elevated scores.

raw_text stores the complete content of the experience — the full tool result, the complete debate position, the entire user message, the full performance report. This is the source material from which the summary is derived. Raw text is not embedded — it is too long and too noisy for effective vector representation. It is used for full-text search and for human review.

summary_text is the single most important content field in the schema. It stores the distilled one-to-three sentence essence of what this ripple means — not what happened in detail, but what it means. The summary is what gets embedded into the vector representation. The quality of the summary determines the quality of semantic retrieval. A bad summary — one that is too generic, too detailed, or misses the key insight — produces bad retrieval. The summary generation process is described in full in the ingest pipeline section.

### **Vector Fields**

embedding is a VECTOR(64) column — a 64-dimensional floating point vector representing the semantic meaning of the summary_text. This is stored using the pgvector extension and indexed with an IVFFlat index for approximate nearest-neighbor search. The choice of 64 dimensions rather than the full 768 dimensions of the base embedding model is a deliberate engineering trade-off: 64 dimensions preserves approximately 97 percent of the semantic information while reducing storage requirements by 92 percent and search time by approximately 85 percent.

The embedding is generated using Google's text-embedding-004 model via Vertex AI. The model is invoked with the summary_text as input and the 64-dimension output is stored directly. The cost of this embedding call is approximately 0.000003 dollars per ripple — negligible at any realistic scale.

simhash_barcode is an array of 8 unsigned 64-bit integers, representing a 512-bit SimHash fingerprint of the ripple content. SimHash is a locality-sensitive hash designed so that documents with similar content produce similar hash values. Two ripples with Hamming distance below a threshold in their SimHash barcodes are near-duplicates and should not both be retained at high salience — the system compresses one into the other. The 512-bit width gives sufficient resolution to distinguish between conceptually similar but meaningfully different ripples.

The SimHash computation is pure arithmetic — no model calls required. The input is a bag-of-words representation of the summary text with frequency weighting. The computation takes microseconds and can be run synchronously during the ingest pipeline without impacting performance.

fts_vector is a PostgreSQL tsvector column generated automatically from the summary_text field. This enables full-text lexical search across ripples — finding ripples that contain specific keywords, brand names, or proper nouns that may not be well-represented in semantic vector space. The GIN index on this column makes lexical search fast enough for the retrieval pipeline's timing budget.

### **Emotional Fields**

emotion_vector is an array of 8 floating point values representing the Plutchik emotional state at the time this ripple was encoded. The eight values correspond in order to: joy, trust, fear, surprise, sadness, disgust, anger, and anticipation. Each value is between 0.0 and 1.0, where 0.0 represents complete absence of that emotion and 1.0 represents the maximum intensity of that emotion in the avatar's experience at encoding time.

The emotion vector is computed deterministically from the event type and the avatar's current ego state at encoding time. There is no LLM call involved in computing the emotion vector — it is a lookup and arithmetic operation. The specific computation: base emotion weights for the event type multiplied by the avatar's current ego state, then normalized. For a debate_victory event for an avatar with elevated anticipation in their current ego state, the resulting emotion vector will have elevated joy and anticipation values relative to baseline.

The emotion vector serves several functions. During retrieval, it is used to find ripples that were encoded in emotionally similar states — the assumption being that memories encoded in similar emotional contexts are more likely to be relevant to the current situation than memories encoded in opposite emotional contexts. During SWR consolidation, it is used to identify ripples that are emotionally significant enough to be replayed and strengthened. During pattern analysis, it is used to identify emotional patterns in the avatar's experience — for example, that this avatar consistently experiences high disgust when a particular type of brief arrives, which might warrant a specific response protocol.

### **Salience Fields**

salience is a float between 0.0 and 1.0 representing how important this ripple is to retain and surface. The salience computation is described in full in the ingest pipeline section. Salience is not static — it is updated by subsequent events, by retrieval frequency, and by the SWR consolidation process.

confidence is a float between 0.0 and 1.0 representing how confident the avatar is in the content of this ripple. For directly observed events — a user's explicit statement, a campaign performance metric — confidence should be high, typically 0.85 to 0.95. For inferred events — an interpretation of competitive intent based on observed behavior — confidence should be lower, typically 0.50 to 0.70. For predictions about future events — Level Four ripples — confidence represents the avatar's confidence in the prediction before it has been validated.

### **Prediction Fields**

prediction_json is a nullable JSONB field containing a structured prediction that was attached to this ripple at creation time. Not all ripples have predictions — only ripples that represent a meaningful anticipatory state, typically Level Three and Level Four ripples. A prediction is a structured JSON object with a prediction_text field describing what the avatar expects will happen, an expected_outcome field with a more specific formulation of the expected result, a confidence field representing the avatar's confidence in the prediction at encoding time, and a timeframe field indicating how quickly the prediction should be resolved.

actual_json is a nullable JSONB field containing what actually happened, populated when the prediction is resolved. This field is null until the outcome is known. When it is populated, the prediction_error field is computed.

prediction_error is a nullable float representing the magnitude of the difference between prediction_json and actual_json. This is computed as a weighted combination of semantic distance between the predicted outcome text and the actual outcome text, and factual error where the prediction was specific enough to be evaluated factually. Prediction error of 0.0 means perfect prediction. Prediction error of 1.0 means complete surprise. Values in the middle represent partial surprise.

precision_weight is a float representing how much this dimension of the avatar's prediction system should be trusted for future predictions of this type. This is the Kalman filter component of the PRL: avatars that are consistently wrong about a specific type of prediction get progressively lower precision weights for that prediction type, which reduces the downstream impact of their errors on the overall model. Precision weights are updated on every prediction resolution using a running exponential average.

### **Retention Fields**

importance_band is a text field with four values: critical, strong, normal, and disposable. Critical ripples are never decayed and never compressed. They represent Essence Core content and protected user preferences. Strong ripples receive aggressive protection from decay — they require many cycles of non-activation before their retention priority is reduced. Normal ripples follow standard decay curves. Disposable ripples are candidates for early compression if storage pressure requires it.

retention_band is a text field with five values: hot, warm, cold, archived, and purged. Hot ripples are in the working memory cache and the primary retrieval pool — they are retrieved with highest priority and accessed most quickly. Warm ripples are in the accessible retrieval pool but not in the working memory cache — they are retrievable but require slightly more processing. Cold ripples are in long-term storage with reduced retrieval priority — they can be retrieved but are not returned in most standard queries. Archived ripples are retained in the database but excluded from standard retrieval — they require an explicit archive query to surface. Purged ripples have been deleted from the database, with their existence recorded only in a lightweight tombstone record.

activation_count is an integer tracking how many times this ripple has been retrieved and used in an agent context. High activation count contributes to salience maintenance — frequently used ripples resist decay even if their content is not inherently high-importance. Low activation count combined with low inherent salience is the primary trigger for BARR suppression.

last_activated_at is a timestamp recording when this ripple was most recently retrieved and included in an agent context. This field drives the temporal decay component of salience: ripples that have not been activated recently lose salience gradually over time, and the rate of loss depends on the importance_band.

### **The Complete Create Statement**

The ripples table is created with the following structure in the database migration. The full column set, index definitions, and RLS policy are documented here for implementation reference.

CREATE EXTENSION IF NOT EXISTS vector;

CREATE TABLE ripples (

ripple_id TEXT PRIMARY KEY,

org_id UUID NOT NULL,

agent_id UUID NOT NULL,

campaign_id UUID,

session_id UUID NOT NULL,

scope TEXT NOT NULL DEFAULT 'private_agent',

memory_class TEXT NOT NULL DEFAULT 'episodic',

hierarchy_level SMALLINT NOT NULL DEFAULT 2,

event_type TEXT NOT NULL,

trigger_text TEXT NOT NULL,

raw_text TEXT NOT NULL,

summary_text TEXT NOT NULL,

embedding VECTOR(64),

simhash_barcode BIGINT\[8\],

fts_vector TSVECTOR GENERATED ALWAYS AS

(to_tsvector('english', summary_text)) STORED,

emotion_vector FLOAT\[8\] NOT NULL,

salience FLOAT NOT NULL DEFAULT 0.5,

confidence FLOAT NOT NULL DEFAULT 0.7,

prediction_json JSONB,

actual_json JSONB,

prediction_error FLOAT,

precision_weight FLOAT NOT NULL DEFAULT 1.0,

importance_band TEXT NOT NULL DEFAULT 'normal',

retention_band TEXT NOT NULL DEFAULT 'hot',

activation_count INTEGER NOT NULL DEFAULT 0,

last_activated_at TIMESTAMPTZ,

state TEXT NOT NULL DEFAULT 'active',

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

Indexes on this table: a composite index on org_id and agent_id covering the most common retrieval filter combination; an IVFFlat index on the embedding column with 100 lists for approximate nearest-neighbor search; a GIN index on fts_vector for full-text search; a BRIN index on created_at for efficient time-range queries; and a standard index on session_id for working memory retrieval. Row Level Security is enabled with a policy that ensures queries can only return rows where org_id matches the current session's tenant identifier.

## **Chapter 2.2 — The Ripple Edges Table**

Ripples do not exist in isolation. They exist in a lattice — a weighted graph where edges represent meaningful associations between ripples. The ripple_edges table is the physical implementation of this lattice. It is the data structure that enables Pass D of the CORTEX retrieval system — the Hebbian associative spread that finds contextually associated memories by following edge paths.

CREATE TABLE ripple_edges (

source_id TEXT REFERENCES ripples(ripple_id) ON DELETE CASCADE,

target_id TEXT REFERENCES ripples(ripple_id) ON DELETE CASCADE,

weight FLOAT NOT NULL DEFAULT 0.1,

co_activation_count BIGINT NOT NULL DEFAULT 0,

edge_type TEXT NOT NULL DEFAULT 'associative',

last_co_activated_at TIMESTAMPTZ,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),

PRIMARY KEY (source_id, target_id)

);

CREATE INDEX ripple_edges_source_idx ON ripple_edges(source_id, weight DESC);

CREATE INDEX ripple_edges_target_idx ON ripple_edges(target_id, weight DESC);

The weight field is the Hebbian strength of the association between the two ripples. Initial weight is 0.1 — a weak association. Weight increases with co-activation according to Oja's stabilized rule, described in full in the learning section. Maximum weight is 1.0. Weight below 0.05 causes the edge to be a candidate for pruning during SWR consolidation.

The edge_type field classifies the nature of the association: associative (co-activated in similar contexts), predictive (source ripple predicted events that target ripple represents), causal (source ripple caused the event that target ripple represents), temporal (created in close temporal proximity), and contradicts (source and target ripples contain conflicting information — low-weight edges of this type represent known tensions in the knowledge structure).

The contradicts edge type is particularly important. When two Level Three or Level Four ripples contain contradictory models — when the avatar has two competing predictions about how something will unfold — the contradicts edge captures this tension rather than resolving it prematurely. The Kalman-weighted prediction error system will eventually resolve the tension by reducing the precision_weight of whichever model consistently makes worse predictions. Until then, the contradiction is preserved as a known uncertainty.

## **Chapter 2.3 — The Agent Essences Table**

The agent_essences table is the persistent home of each avatar's identity. It stores the Essence Core, the current Ego Signature state, the Skill Weave, and the operational metadata required to manage each avatar's memory lifecycle. This table is smaller than the ripples table by orders of magnitude — one row per avatar per org — but it is read far more frequently because it is loaded at the start of every inference session.

CREATE TABLE agent_essences (

agent_id UUID PRIMARY KEY,

org_id UUID NOT NULL,

avatar_key TEXT NOT NULL,

display_name TEXT,

essence_core JSONB NOT NULL,

ego_baseline FLOAT\[8\] NOT NULL,

ego_state FLOAT\[8\] NOT NULL,

ego_multipliers FLOAT\[8\] NOT NULL,

ego_decay_rate FLOAT NOT NULL DEFAULT 0.05,

skill_atoms JSONB NOT NULL DEFAULT '\[\]'::JSONB,

persona_vector VECTOR(64),

reflection_vfe FLOAT NOT NULL DEFAULT 0.0,

reflection_mean FLOAT NOT NULL DEFAULT 0.0,

reflection_std FLOAT NOT NULL DEFAULT 0.5,

reflection_cooldown INTEGER NOT NULL DEFAULT 0,

active_session_id UUID,

last_active_at TIMESTAMPTZ,

created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()

);

The essence_core field is a large JSONB document containing all the protected identity content for this avatar. Its structure includes: the avatar's name and archetype key, the list of constitutional principles, the list of core beliefs with their supporting reasoning, the backstory elements that contextualise the beliefs, the known relationship dynamics with other avatars, the characteristic working method, and the set of forbidden responses — outputs that would violate the Essence Core so fundamentally that they should never be generated regardless of prompt pressure.

The ego_state field stores the current 8-float Plutchik vector. This is updated after every session in which the avatar participated in inference. The update applies any emotional events from the session and then applies the decay toward the ego_baseline. The ego_decay_rate field controls how quickly the state returns to baseline: a decay rate of 0.05 means that each time the decay function runs, the state moves 5 percent of the remaining distance toward baseline. At typical session frequencies, this produces emotional memory that persists for days rather than hours or seconds.

The skill_atoms field is a JSONB array of SkillAtom objects. Each SkillAtom has: a unique identifier, a name, a description of the skill, an embedding vector (stored as a JSONB array rather than a proper VECTOR column for flexibility), an essence_alignment score, a utility_score, a utility_variance, a usage_count, a domain_tags array, and timestamps for creation and last use. The full SkillAtom specification is covered in Volume 6 on the EEL system.

# **Part Three: The Ripple Ingest Pipeline**

## **Chapter 3.1 — The Event Fire Pattern**

The ingest pipeline begins the moment an agent's execution produces a meaningful event. The first decision the system makes is whether this event should produce a ripple at all. This decision is made by the event classifier — a pure-function component that takes the event metadata as input and returns a binary yes or no plus the event_type classification if yes.

The event classifier uses a decision table with two primary axes: the event source type (which module produced this event) and the event significance (does this event change what the agent knows or believes in a way that should affect future behavior). Events below a significance threshold are logged to the system audit log but not sent to the ripple ingest pipeline.

When an event passes the classifier, it is wrapped in a MemoryEvent struct and sent into a Tokio MPSC channel — a multi-producer, single-consumer asynchronous message channel. The send operation takes less than one microsecond. The agent's execution thread does not wait for the ripple to be created. It fires the event and continues. The ripple creation happens in a dedicated Tokio task that is watching the MPSC channel.

This fire-and-forget pattern is essential for performance. Ripple creation involves multiple processing steps that collectively take 50 to 100 milliseconds. If the agent's execution had to wait for ripple creation to complete, every meaningful event would add 50 to 100 milliseconds to the inference latency. At the rate at which events are generated during a Council session — dozens per minute — this would make the system unusably slow. The MPSC pattern eliminates this latency entirely from the agent's perspective.

## **Chapter 3.2 — Step 1: Normalization**

The ingest worker receives the MemoryEvent from the MPSC channel and begins processing. The first step is normalization: converting the raw event, which may have arrived in many different formats from many different source modules, into a canonical form that all subsequent processing steps can handle uniformly.

The canonical form answers five questions about the event: who acted, what action they took, on what subject, what was the immediate result, and what does this mean for the agent's ongoing work. Different event types answer these questions differently. A tool_result event answers: the agent (who), invoked the tool (action), with these parameters (subject), which returned this result (result), which changes the agent's knowledge in this way (meaning). A debate_verdict event answers: the Council (who), debated this question (action), with these positions (subject), reaching this synthesis (result), which updates the strategic recommendation in this way (meaning).

The normalization function is a pure function — no side effects, no external calls, no database access. It is fast: typically completing in under a millisecond. The normalized canonical form is a Rust struct with five string fields corresponding to the five questions, plus the original event type and the timestamp.

## **Chapter 3.3 — Step 2: Working Memory Gate**

Before the ripple is fully created, the normalized event passes through a working memory gate — a threshold check that determines whether this event is significant enough to warrant full ripple creation or should be discarded as noise.

The gate computes a preliminary significance score from the normalized event. The score is a weighted combination of: the novelty of the event (does this appear frequently in recent working memory?), the apparent outcome impact (does this change the current task direction?), and the event type weight (some event types are inherently more significant than others). The gate threshold is 0.20 — events below this score are discarded without creating a ripple.

The novelty check uses the working memory cache rather than the full database — it checks whether the DragonflyDB working memory set contains any ripples with SimHash barcodes within a short Hamming distance of a quick-computed barcode for this event. If it does, the event is a near-duplicate of something very recently seen and has low novelty. If it does not, novelty is high.

Events that pass the gate proceed to full ripple creation. Events that fail the gate are discarded. Discarded events are not lost permanently — they remain in the system event log — but they do not become memories.

## **Chapter 3.4 — Step 3: Salience Scoring**

For events that pass the working memory gate, the full salience score is computed. The salience score determines how important this ripple is and therefore how aggressively it will be retained and surfaced in retrieval. The salience formula is:

salience = (0.30 × novelty) + (0.25 × outcome_impact) + (0.20 × user_relevance) + (0.15 × emotional_intensity) + (0.10 × recurrence)

Each factor is computed as a float between 0.0 and 1.0 using purely local information — no external calls and no database reads beyond the working memory cache.

Novelty at this stage is a more refined computation than the quick check in the gate. It uses the SimHash barcode of the full event content to check against recent ripples in the working memory cache. A barcode that matches nothing in the cache gets novelty 1.0. A barcode that closely matches several recent ripples gets novelty close to 0.0.

Outcome_impact is computed from the normalized canonical form by looking at the meaning field — the fifth question about what this event means for the agent's ongoing work. The meaning field is scored on a simple keyword-based scale: events whose meaning indicates a change of direction, a rejected prediction, a new constraint, or a resolved uncertainty get high outcome impact. Events whose meaning confirms an existing expectation get low outcome impact.

User_relevance is computed by comparing the subject field of the canonical form to the agent's cached Foundation context. Subjects that are closely related to the Foundation's ICP description, positioning statement, or active campaign goals get high user_relevance. Subjects that are tangential to the current work context get low user_relevance.

Emotional_intensity is computed from the difference between the avatar's current ego state and its baseline. If the ego state is currently far from baseline — the avatar is experiencing strong emotions relative to their normal state — any new event is being experienced in an emotionally heightened context, which increases its memorability. Emotional_intensity = L2 norm of (ego_state - ego_baseline), normalized to 0.0–1.0.

Recurrence is computed by checking how many times similar events have appeared in recent working memory. Events that repeat — a specific type of competitive signal, a recurring user preference statement — get elevated recurrence scores because patterns that persist across multiple instances are more worth remembering than one-off events.

## **Chapter 3.5 — Step 4: Summary Generation**

The summary_text field is the most important content in the ripple schema because it is what gets embedded and therefore what determines semantic retrieval quality. Poor summaries produce poor retrieval. The summary generation process must produce summaries that are: specific enough to carry the key insight, concise enough to embed accurately, and framed as a statement of meaning rather than a description of events.

Summary generation uses a two-tier approach. Tier 1 is a structural template applied based on event type. For tool_result events, the template is: 'Agent \[name\] found that \[subject\] produced \[result\], which means \[meaning\].' For debate_verdict events: 'The Council determined that \[question\] should be approached by \[synthesis\], with \[key reasoning\].' For user_input events that express a preference: '\[User's business\] prefers \[preference\] because \[user's stated reasoning\].' These templates produce adequate summaries for straightforward events quickly and cheaply.

Tier 2 is triggered when the event content is complex enough that the structural template produces an inadequate summary — when the meaning is nuanced, when the subject spans multiple concepts, or when the outcome has implications that the template does not capture. In these cases, a Flash-Lite inference call generates the summary. The prompt for this call is: 'Summarize the following event as a single statement of what it means for the agent's work and understanding. Do not describe what happened. State what it means. Be specific.' The Flash-Lite call for summary generation costs approximately 0.00004 dollars and takes under one second.

The quality threshold for summaries: a good summary can be read by any agent with context about the situation and immediately understood. A bad summary requires reading the raw_text to interpret. If the summary requires context that is not in the summary itself to be meaningful, it is a bad summary.

## **Chapter 3.6 — Step 5: Emotion Tagging**

The emotion vector for the ripple is computed from the avatar's current ego state, the event type's baseline emotional impact, and the avatar's multiplier profile. The computation is pure arithmetic with no external calls.

The event type has a baseline emotional delta table — a lookup table mapping event types to their typical emotional impact vectors. A debate_victory event typically produces positive deltas on joy and anticipation, and negative deltas on fear. A prediction_violated event typically produces positive deltas on surprise and moderate negative deltas on confidence-related emotions. These baseline deltas are modified by the avatar's multiplier profile before being applied to the ego state.

The resulting emotion vector for the ripple is the avatar's ego state after applying the event's emotional impact, before the decay function runs. This captures the emotional coloring of the moment the event was experienced, which is the right thing to capture — memories are colored by the emotion at encoding time, not by the emotion at retrieval time.

## **Chapter 3.7 — Step 6: SimHash Barcode Computation**

The SimHash barcode is computed from a bag-of-words representation of the summary_text. The computation is: extract all tokens from the summary_text, apply TF-IDF weighting using the org-specific term frequency statistics maintained in the DragonflyDB cache, compute the hash using the SimHash algorithm with 512-bit output, store as 8 unsigned 64-bit integers.

The SimHash computation is fully deterministic and takes under one millisecond. Two summaries with similar content will produce SimHash barcodes with small Hamming distance. Two summaries with very different content will produce barcodes with large Hamming distance. The threshold for near-duplicate detection is a Hamming distance of less than 30 out of 512 bits — approximately 94 percent similarity.

## **Chapter 3.8 — Step 7: Ripple Struct Construction and Write**

With all the computed values available — normalized canonical form, salience score, emotion vector, SimHash barcode — the Ripple struct is assembled. The struct corresponds exactly to the database schema. The ULID is generated at this point using the current timestamp plus random bits.

The write operation uses a write-ahead buffer rather than a direct database insert. The write-ahead buffer batches multiple ripple inserts and flushes them to the database every 50 milliseconds or when the buffer reaches 20 entries, whichever comes first. This batching reduces the number of database round-trips during high-activity periods — during a Council session, the system may be creating dozens of ripples per minute, and batching prevents this from becoming a database bottleneck.

The ripple is also immediately inserted into the DragonflyDB working memory cache, which is updated synchronously rather than through the write-ahead buffer. This ensures that the working memory cache always reflects the most recently created ripples, even if those ripples have not yet been flushed to the main database.

## **Chapter 3.9 — Step 8: Edge Linking**

After the ripple is in the working memory cache, the edge linker runs. The edge linker identifies existing ripples that should be linked to the new ripple and creates entries in the ripple_edges table for each link.

The edge linker uses three criteria to identify candidates for linking. Semantic proximity: other ripples in the working memory cache whose embedding vectors are within a cosine similarity threshold of 0.75 from the new ripple's embedding. Temporal co-activation: ripples that were recently activated — within the last 60 seconds — because temporal proximity in activation is a strong signal of contextual association. Topic alignment: other ripples in the current session that share event_type classifications or canonical form subject similarity.

For each identified candidate, an edge is created in the ripple_edges table with an initial weight of 0.1. If an edge between these two ripples already exists, the weight is incremented by 0.05 rather than creating a duplicate edge. The minimum set of edges created for any new ripple is zero — if no suitable candidates are found, no edges are created. The typical number of edges created per ripple during an active session is two to five.

The edge linking step uses the working memory cache rather than querying the full database. This is essential for performance — querying the full ripples table for every new ripple would be prohibitively expensive. The working memory cache contains the 50 most recently activated ripples for the current agent, which is the appropriate candidate set for association discovery.

## **Chapter 3.10 — Step 9: Embedding Queue**

The embedding — the 64-dimensional vector representation of the summary_text — is not computed synchronously during the ingest pipeline. It is queued for asynchronous generation. This is a deliberate performance decision: the embedding API call takes 200 to 500 milliseconds, which is too slow to include in the synchronous ingest path. Ripples can be retrieved by lexical search and by the working memory cache before their embedding is available. The embedding is typically ready within 1 to 2 seconds after the ripple is created.

The embedding queue is implemented as an SQS queue with a dedicated consumer worker. When a ripple is created, its ripple_id is enqueued. The consumer worker pulls ripple_ids from the queue, loads the summary_text from the database, calls the embedding API, and updates the embedding column. The state field in the ripples table tracks whether the embedding has been generated — a ripple with state 'pending_embedding' is excluded from Pass B of the CORTEX retrieval system but is accessible through Passes A, C, D, and E.

# **Part Four: The CORTEX Retrieval System**

## **Chapter 4.1 — The Retrieval Architecture Overview**

Every time an agent needs to access its memory to generate a response, the CORTEX retrieval system fires. The system runs five distinct retrieval passes in parallel using Tokio's concurrent task system, merges the results using a weighted fusion algorithm, and returns the top 20 most relevant ripples as a structured ContextPack within 6 milliseconds.

The five passes are designed to be complementary rather than redundant. Each pass finds different types of relevant ripples using different signals. Working memory finds the most recent. Vector similarity finds the most semantically related. Lexical search finds the most terminologically specific. Hebbian spread finds the most associatively connected. Trajectory matching finds the most pattern-aligned. Together, they cover the retrieval needs that no single approach handles adequately.

The 6-millisecond target is not arbitrary. It represents the maximum latency that can be added to an agent inference call without measurably degrading the user experience. Inference itself takes several seconds — adding 6 milliseconds for retrieval is imperceptible. Adding 60 milliseconds would be noticeable at scale.

## **Chapter 4.2 — Pass A: Working Memory Cache (Target: 0.02ms)**

The working memory cache is stored in DragonflyDB as a sorted set per agent. The key pattern is wm:{org_id}:{agent_id}. The set contains the 50 most recently activated ripple IDs, sorted by activation timestamp in descending order — most recently activated first.

Pass A retrieves all entries from this sorted set using a single ZRANGE command. The ripple IDs are returned with their scores (activation timestamps). The ripples themselves are loaded from a secondary DragonflyDB hash that stores the summary_text, emotion_vector, salience, and hierarchy_level for each cached ripple — enough information for the fusion algorithm to score them, without requiring a database query.

The DragonflyDB operations complete in under 0.5 milliseconds under normal conditions. The target of 0.02 milliseconds is achievable when DragonflyDB is running in the same availability zone as the application server, which it is in the production deployment configuration.

Working memory results receive a base fusion weight of 1.5 — the highest of all five passes. This reflects the strong signal value of recency: what the agent was just thinking about is very likely to be relevant to what it is thinking about now.

## **Chapter 4.3 — Pass B: Vector Similarity Search (Target: 4.5ms)**

Pass B queries the Qdrant vector database for ripples whose embeddings are semantically similar to the current query embedding. The query embedding is generated from the current context — a concatenation of the current request text and the most relevant Foundation context — using the same text-embedding-004 model that generates ripple embeddings.

The Qdrant query is filtered on org_id and agent_id — only this agent's private ripples and shared_campaign ripples for the current campaign are searched, unless the request is a shared context query in which case shared_org ripples are included. The filter is applied before the approximate nearest-neighbor search, not as a post-filter, which maintains search efficiency.

The search parameters: top_k of 50 results, using HNSW approximate nearest-neighbor search with ef_search of 128 (a parameter controlling the search quality-speed tradeoff; 128 provides high recall while maintaining the millisecond-range latency target). The results are 50 ripple IDs with cosine similarity scores.

The 50 candidates from Pass B are then re-ranked using the full ripple metadata from the database — salience, recency, importance_band, and emotional similarity to the current context are all incorporated into the final score. The top 20 from this re-ranking are returned to the fusion algorithm.

Why Qdrant rather than pgvector for this pass? The primary reason is performance at scale. pgvector's HNSW implementation is efficient but its performance degrades when filtering is applied before the ANN search — the filter significantly reduces the effective candidate set, which makes the HNSW graph less efficient to traverse. Qdrant's implementation handles pre-filtered search more efficiently through its payload indexing system. At small scale (under 100,000 ripples), pgvector with IVFFlat provides acceptable performance. At the target scale of 20 million ripples, Qdrant's architecture is the correct choice.

## **Chapter 4.4 — Pass C: Lexical Search (Target: 3ms)**

Pass C queries the PostgreSQL full-text search index using tsvector and tsquery. This pass finds ripples that contain specific keywords, brand names, competitor names, product terms, and proper nouns that may not be captured well in semantic embedding space.

The query is constructed by extracting high-value terms from the current context — specifically, proper nouns and domain-specific terms that are likely to appear verbatim in relevant ripples. Generic terms are excluded from the lexical query because they are too common to be discriminating. The tsquery is constructed with these terms connected by OR operators, so any ripple containing any of them is a candidate.

The SQL query for Pass C: SELECT ripple_id, ts_rank_cd(fts_vector, query) as rank FROM ripples, to_tsquery('english', $1) query WHERE org_id = $2 AND agent_id = $3 AND fts_vector @@ query AND state = 'active' ORDER BY rank DESC LIMIT 20. The ts_rank_cd function ranks by cover density — giving higher scores to ripples where the query terms appear close together and frequently, rather than just appearing at all.

Pass C results receive a base fusion weight of 0.8. Lexical matches are valuable when they hit but less universally applicable than semantic matches — not every query has specific proper nouns worth lexical matching. The lower weight reflects this.

## **Chapter 4.5 — Pass D: Hebbian Associative Spread (Target: 1.5ms)**

Pass D starts from the ripples currently in working memory (from Pass A) and follows the Hebbian edges in the lattice to find associated ripples that may not be semantically similar or lexically related but have historically been relevant in similar contexts.

The implementation uses a two-hop SQL traversal of the ripple_edges table. The query retrieves all ripples reachable within two hops from the working memory set, weighted by the product of edge weights along the path. Edges with weight below 0.15 are excluded — only moderately established associations are traversed, to avoid surfacing weakly related content that has happened to co-occur a few times.

The SQL for Pass D uses a Common Table Expression: WITH seeds AS (SELECT unnest($1::text\[\]) AS id), hop1 AS (SELECT e.target_id, e.weight FROM ripple_edges e JOIN seeds s ON e.source_id = s.id WHERE e.weight > 0.15 ORDER BY e.weight DESC LIMIT 30), hop2 AS (SELECT e.target_id, h.weight \* e.weight AS path_weight FROM ripple_edges e JOIN hop1 h ON e.source_id = h.target_id WHERE e.weight > 0.15 ORDER BY path_weight DESC LIMIT 40) SELECT target_id, MAX(path_weight) as score FROM (SELECT target_id, weight as path_weight FROM hop1 UNION ALL SELECT target_id, path_weight FROM hop2) combined WHERE target_id != ALL($1) GROUP BY target_id ORDER BY score DESC LIMIT 25.

Pass D results receive a base fusion weight of 0.7. Associative recall is valuable when it fires — surfacing relevant memories that other passes would miss — but it is inherently noisier than semantic or lexical matching. The lower weight prevents weak associations from dominating the final result set.

## **Chapter 4.6 — Pass E: Trajectory Matching (Target: 0.1ms)**

Pass E checks a precomputed cache of successful event sequence patterns against the current sequence of events in the session. A trajectory is a pattern of event types that, when they occur in sequence, tend to be followed by a specific type of successful outcome. When the current session's event sequence matches a stored trajectory, the ripples associated with previous successful instances of that trajectory are retrieved directly.

The trajectory cache is stored in DragonflyDB as a hash mapping trajectory hashes to lists of associated ripple IDs. A trajectory hash is computed from the sequence of event_type values in the current session, using a sliding window of the last five to eight events. The hash function is designed to be insensitive to minor variations — two trajectories that differ by one event type in the middle of the sequence produce the same hash if the overall pattern is similar.

The cache is populated during SWR consolidation, when the system analyzes session histories to identify repeated patterns. A pattern qualifies for the trajectory cache when it has occurred at least three times and has been followed by a positive outcome (high prediction confirmation, high campaign performance) in at least two of those instances.

Pass E results receive a base fusion weight of 1.2 — higher than most passes because trajectory matches, when they fire, are highly reliable signals. The challenge is that they fire infrequently in early usage and become more valuable as the system accumulates more session history.

## **Chapter 4.7 — Fusion: Combining the Five Passes**

The fusion algorithm receives five ranked lists of ripple IDs with scores. It merges them using Weighted Reciprocal Rank Fusion — a robust ranked-list combination method that is more effective than simple score averaging because it is robust to score scale differences between passes.

Weighted RRF formula: final_score(ripple) = sum over passes of (pass_weight / (k + rank_in_pass)), where k is a constant of 60 that prevents top-ranked results from dominating excessively, rank_in_pass is the position of this ripple in the pass's result list (1 for first), and pass_weight is the base weight for that pass (1.5 for working memory, 1.0 for vector, 0.8 for lexical, 0.7 for Hebbian, 1.2 for trajectory).

After computing the weighted RRF score for every ripple that appeared in any pass result, the ripples are ranked by final score and the top 20 are selected. These 20 ripples are assembled into the ContextPack that is returned to the requesting agent.

The ContextPack is not just a list of ripple IDs. It is a structured object containing: the top 20 ripples with their summary_text, emotion_vector, salience, confidence, and hierarchy_level; the pass that contributed most to each ripple's ranking (for transparency in debugging); and a flag indicating whether any relevant ripples have embeddings still being generated (state = 'pending_embedding') that should be checked again in a subsequent retrieval.

The total time for the complete five-pass retrieval including fusion typically falls between 4 and 6 milliseconds for an agent with 10,000 to 50,000 ripples in the database. The Pass A and Pass E operations are so fast that they do not materially affect the total. Pass B (vector search) and Pass C (lexical search) dominate the latency budget.

# **Part Five: Learning — How the PRL Gets Smarter**

## **Chapter 5.1 — Prediction Attachment**

After an agent generates a meaningful output — a campaign recommendation, a strategic position in a debate, a content direction — the system attaches a prediction to the ripple that represents this output. The prediction captures what the agent expects will happen as a result of this output.

The prediction structure: prediction_text is a natural language description of the expected outcome. expected_metric is a structured specification of a measurable indicator that should confirm or refute the prediction — for campaign recommendations, this might be the expected CTR range; for strategic positions, it might be the expected strength of adoption in the synthesis. confidence is the agent's confidence in this prediction at generation time, drawn from the current precision_weight for this prediction dimension. timeframe is the expected time before the prediction can be evaluated.

Predictions are generated by a Flash-Lite call that takes the output content and the current agent context and produces the prediction structure. The call is asynchronous — it does not delay the output reaching the user — and its result is written to the prediction_json field of the relevant ripple within a few seconds of the output being generated.

Not all outputs produce predictions. The prediction system is most valuable for strategic recommendations, content direction decisions, and campaign planning outputs — the cases where the output has a clear expected consequence that can be measured. Simple factual responses and content generation do not produce predictions in most cases.

## **Chapter 5.2 — Prediction Resolution**

Predictions are resolved when the relevant outcome data becomes available. Campaign performance data resolves campaign recommendation predictions. Debate synthesis outcomes resolve individual avatar position predictions. User feedback resolves content quality predictions. The resolution process runs as a background job that monitors for new data that can be matched to existing unresolved predictions.

When a prediction is resolved, the actual_json field is populated with the observed outcome. The prediction_error is then computed as a normalized distance between the prediction and the actual outcome. For predictions with numeric expected values, the error is the normalized absolute difference. For predictions with qualitative expected outcomes, a Flash-Lite call computes the semantic distance between the predicted and actual outcome descriptions.

The precision_weight for the relevant dimension is updated using an exponential moving average: new_precision = 0.9 × old_precision + 0.1 × (1.0 - prediction_error). Consistently accurate predictions increase the precision weight. Consistently inaccurate predictions decrease it. The precision weight converges toward the avatar's actual accuracy for predictions of this type.

## **Chapter 5.3 — Prediction Error Propagation**

When a prediction error is resolved and the error is significant — greater than 0.3 — the error propagates backward through the ripple edges to the ripples that contributed to the incorrect prediction. This propagation is the mechanism by which the PRL learns from mistakes at the structural level rather than just the instance level.

The propagation algorithm: starting from the ripple whose prediction was violated, traverse backward through predictive and associative edges up to depth 3, applying a decay factor of 0.7 at each hop. Each ripple in the propagation path has its salience and confidence reduced by an amount proportional to the propagated error and its edge weight on the path. Ripples at depth 1 receive the full propagated error. Ripples at depth 2 receive 70 percent. Ripples at depth 3 receive 49 percent.

The salience reduction from error propagation is bounded below at 0.2 — no ripple's salience is reduced below this floor by error propagation alone. The floor prevents the system from effectively deleting memories that supported a wrong prediction, because those memories may be correct about other things even if they contributed to an incorrect specific prediction.

When a prediction is confirmed — when the actual outcome closely matches the prediction — the reverse operation applies. Salience and confidence of contributing ripples are moderately increased, and the Hebbian edges along the path are strengthened. Confirmed predictions are less dramatically reinforcing than violated predictions are penalizing — the human memory analog is that surprises are more memorable than confirmations, and this asymmetry is maintained.

## **Chapter 5.4 — SWR Consolidation: The Idle Learning Cycle**

Sharp Wave Ripple consolidation is the most important learning mechanism in the PRL. It is named after the neurobiological process in the hippocampus through which memories are consolidated during sleep and rest periods. In the PRL, it runs during system idle periods — when no active user sessions are running and inference load is low.

The SWR consolidation job is triggered by the tokio-cron-scheduler when system load drops below a defined threshold. It runs at most once every four hours per organization and terminates after 30 minutes or when the consolidation workload is exhausted, whichever comes first.

### **Phase 1: Replay Selection**

The consolidation job begins by identifying ripples to replay. The replay selection criteria: ripples created in the last 24 hours with salience above 0.4, ripples that contributed to significant prediction errors in the last 24 hours, ripples that were activated multiple times in the last 24 hours, and a random sample of older high-salience ripples to maintain accessibility of important long-term memories.

The selected ripples are sorted into two categories: reward-proximal (associated with positive prediction outcomes, successful campaign performance, or positive user feedback) and neutral or negative. The replay sequence runs reward-proximal ripples in reverse chronological order — most recent first — which corresponds to backward induction in reinforcement learning and is more effective for credit assignment.

### **Phase 2: Edge Strengthening**

For each pair of ripples that are replayed in the same consolidation cycle, their mutual edge weight is incremented by 0.02 using Oja's stabilized Hebbian rule. The Oja rule: delta_w = eta × (x_i × x_j - x_j^2 × w), where eta is the learning rate (0.01), x_i and x_j are the activation levels of the two ripples (1.0 when both are being replayed), and w is the current edge weight. This produces a bounded weight update that tends toward 1.0 when two ripples are always co-activated and toward 0.0 when they are rarely co-activated.

Oja's rule is preferred over simple Hebbian learning because it is bounded — simple Hebbian learning can produce unbounded weight growth, while Oja's rule naturally converges to a stable weight distribution. This stability property is essential for the long-term health of the ripple lattice.

### **Phase 3: BARR Suppression**

BARR (Base-level Activation Reduction Rate) suppression runs after replay to identify ripples that are candidates for retention band reduction. The criteria: activation_count below 2 in the last 14 days, salience below 0.4, importance_band of 'normal' or 'disposable', and not in the current session's working memory.

Ripples that meet all BARR criteria have their retention_band reduced by one step: hot becomes warm, warm becomes cold, cold becomes archived. The reduction is applied in the database and the DragonflyDB working memory cache is updated to reflect the new retention band. Critical and strong importance_band ripples are immune to BARR suppression regardless of activation frequency.

### **Phase 4: Semantic Lesson Distillation**

The most cognitively sophisticated part of consolidation is lesson distillation — extracting generalizable knowledge from patterns of specific experiences. The distillation algorithm analyzes clusters of ripples that have been co-activated frequently and have similar embeddings, looking for patterns that can be expressed as a higher-level ripple.

The algorithm uses a two-tier approach. Tier 1 (Rust-first, no LLM): structural patterns that can be expressed as IF-THEN rules with simple conditions. If 20 ripples in a cluster all have event_type 'content_evaluated' with positive outcomes for a specific content_type, a Level Three ripple is created: 'Content of type \[X\] consistently performs well for this org.' This Tier 1 operation costs nothing in inference.

Tier 2 (LLM-assisted): ambiguous patterns where the structure is suggestive but the generalization is not obvious. A cluster of ripples about competitive intelligence, campaign adjustments, and performance improvements that co-occur repeatedly but without a simple structural rule is sent to a Flash-Lite reasoning call. The prompt: 'These experiences have occurred together repeatedly in this client's marketing work. What lesson do they collectively teach? Express it as a single statement of strategic insight in the voice of \[avatar name\].' The resulting lesson is stored as a Level Three ripple with references to the source ripples.

Lesson distillation fires at most 5 times per consolidation run, limiting the Flash-Lite inference cost to approximately 0.002 dollars per consolidation per org. Over a month of twice-daily consolidation, the total lesson distillation cost per org is approximately 0.12 dollars.

### **Phase 5: Predictive Compression**

Ripples with high predictability — those whose embeddings are very similar to many other ripples and whose content adds minimal new information — are candidates for compression. Compression takes a cluster of near-duplicate ripples and replaces them with a single representative ripple that captures the common meaning, with references to the originals stored in a compression_sources JSONB field.

The compressed ripples are moved to archived retention band. They remain in the database and can be recovered if needed, but they are excluded from standard retrieval. The compression reduces both storage costs and retrieval noise — a retrieval system searching 100,000 ripples with 30 percent redundancy is less efficient and less precise than one searching 70,000 distinct ripples.

# **Part Six: Memory Decay and Protection**

## **Chapter 6.1 — The Decay Function**

Ripple salience decays over time when the ripple is not activated. The decay function is a time-modified exponential: new_salience = current_salience × exp(-decay_rate × days_since_activation). The decay_rate varies by importance_band: critical ripples have decay_rate of 0.0 (no decay), strong ripples have 0.001, normal ripples have 0.01, and disposable ripples have 0.05.

At the normal decay rate of 0.01, a ripple that starts at salience 0.8 and is never activated will decay to 0.37 after 100 days, to 0.17 after 200 days, and to 0.08 after 300 days. At salience below 0.1, BARR suppression will typically have moved the ripple to cold or archived retention band, where it is effectively out of the active retrieval pool.

Decay is not applied continuously — it is applied in batch during BARR suppression in SWR consolidation and during the nightly decay update job. The nightly decay update job applies the decay formula to all ripples in the hot and warm retention bands for all organizations, updating the salience field and moving ripples to lower retention bands as thresholds are crossed.

## **Chapter 6.2 — Protected Classes of Ripples**

Six categories of ripples are protected from decay and compression regardless of their activation frequency: Essence Core ripples (importance_band critical, hierarchy_level 4, memory_class identity), user preference ripples (memory_class preference), prediction-validated ripples (prediction_error below 0.1 with high confidence — these are accurate predictors worth retaining), session-defining ripples (ripples that contributed to significant positive outcomes in specific sessions), Foundation reference ripples (ripples that directly link to Foundation data updates), and ripples explicitly marked as protected by the Campaign Strategist through the tool interface.

The protection mechanism is implemented as an is_protected boolean field that defaults to false and is set to true for protected ripples. BARR suppression and compression algorithms check this field before applying any decay or compression operation. Protected ripples are excluded from all decay operations regardless of their activation frequency or age.

## **Chapter 6.3 — The Working Memory Cache Management**

The working memory cache in DragonflyDB maintains the 50 most recently activated ripples per agent. When a new ripple is created or an existing ripple is retrieved, it is added to the cache with the current timestamp as its score. When the cache exceeds 50 entries, the entry with the lowest score — least recently activated — is evicted.

The cache is maintained as a ZSET (sorted set) in DragonflyDB keyed by wm:{org_id}:{agent_id}. Updates to the cache use ZADD with the NX flag for new entries and the XX flag for updates to existing entries. Eviction is managed by ZREMRANGEBYRANK, which removes entries below the score threshold.

The full ripple data for cached ripples is stored in a separate DragonflyDB HASH keyed by ripple:{ripple_id}. This hash stores the summary_text, emotion_vector, salience, confidence, and hierarchy_level — the fields needed by the fusion algorithm without requiring a database query. The hash has a TTL of one hour, which is refreshed every time the ripple is accessed. If a ripple falls out of the working memory ZSET but its HASH has not expired, it can still be accessed quickly for subsequent retrieval without a database query.

# **Part Seven: Cost Analysis and Optimization**

## **Chapter 7.1 — The True Cost of the PRL**

The PRL is designed to be extremely inexpensive to operate relative to the value it provides. The primary cost components are embedding generation, Flash-Lite inference for summary generation and lesson distillation, DragonflyDB memory, Aurora database storage, and Qdrant storage.

Embedding cost: approximately 2,950 ripples per user per month at $0.000003 per embedding = $0.0089 per user per month. This is less than one rupee per user per month for the entire embedding operation.

Summary generation (Tier 2 Flash-Lite): approximately 20 percent of ripples require Tier 2 summary generation = 590 Flash-Lite calls per user per month at approximately $0.00004 per call = $0.024 per user per month. Approximately two rupees.

Lesson distillation: 60 consolidation runs per month at up to 5 Flash-Lite reasoning calls each = 300 calls per user per month at $0.00015 per call = $0.045 per user per month. Less than four rupees.

DragonflyDB: the working memory cache occupies approximately 50 ripples × 2KB average size = 100KB per agent × 21 agents = 2MB per organization in working memory. A DragonflyDB instance serving 500 users holds approximately 1GB of working memory data — well within the capacity of a single instance.

Aurora storage: approximately 3,000 ripples per user per month × 12 months × 500 bytes average row size = 18MB per user per year. For 1,000 users, total ripple storage after one year is approximately 18GB — comfortably handled by Aurora Serverless at very low cost.

Qdrant storage: approximately 36,000 ripples per user per year × 64 dimensions × 4 bytes per float = approximately 9MB per user per year in vector storage. For 1,000 users, this is 9GB — well within the capacity of a mid-tier Qdrant deployment.

Total PRL system cost per user per month: approximately $0.08 — less than seven rupees. This is the cost of the intelligence infrastructure that makes every agent in the system more valuable every day.

## **Chapter 7.2 — Key Optimization Decisions**

The 64-dimension embedding is the single most impactful cost optimization in the PRL. Full 768-dimension embeddings would cost 12 times more in storage and approximately 6 times more in search latency. The information loss at 64 dimensions is approximately 3 percent of semantic discriminability — a trade-off that is clearly correct for this application.

The two-tier summary generation ensures that the more expensive Flash-Lite call is reserved for the 20 percent of ripples that genuinely need it. The Tier 1 structural template handles the 80 percent of ripples where the canonical event structure provides enough information to generate an adequate summary without model inference.

The write-ahead buffer for database writes reduces the database round-trip count by 10 to 20 times during high-activity periods. Without batching, a Council session with 12 agents generating 3 ripples each per debate round would produce 36 database inserts per debate round — potentially 10 to 15 inserts per second. With batching, this becomes 2 to 3 inserts per second.

The DragonflyDB working memory cache eliminates database queries for the most common retrieval case — the working memory pass that is the first thing checked in every retrieval cycle. Serving this from DragonflyDB rather than from Aurora reduces the average retrieval latency by approximately 2 milliseconds and reduces Aurora IOPS consumption by 40 to 50 percent during active sessions.

# **Part Eight: Failure Modes and Recovery**

## **Chapter 8.1 — The Embedding Queue Backlog**

The most common failure mode in the PRL is embedding queue backlog: the situation where ripples are being created faster than the embedding worker can process them, resulting in a growing number of ripples with state 'pending_embedding'. During this state, Pass B of the retrieval system returns fewer results because pending-embedding ripples are excluded from the Qdrant search.

Detection: the embedding queue depth metric is monitored in CloudWatch. When queue depth exceeds 500 messages, a CloudWatch alarm fires and additional embedding worker capacity is launched. The alarm threshold of 500 represents approximately 3 to 5 minutes of backlog at the processing rate of a single worker.

Recovery: the system is designed to be graceful under backlog conditions. Passes A, C, D, and E continue to function normally. Only Pass B is degraded. The retrieval quality decreases during backlog but does not fail completely. When the backlog clears, the full five-pass retrieval is restored automatically.

## **Chapter 8.2 — DragonflyDB Cache Corruption**

If the DragonflyDB instance fails or is restarted, all working memory cache data is lost. This is a designed-in limitation: DragonflyDB is used for caching, not for primary storage. All ripple data is durably stored in Aurora and Qdrant.

Recovery from DragonflyDB failure: the working memory cache is rebuilt for each agent on the next session initiation by querying Aurora for the 50 most recently activated ripples. This rebuild takes approximately 10 to 20 milliseconds and is transparent to the user — the first request in a new session after a DragonflyDB failure has slightly higher latency (6ms becomes 20-30ms) but subsequent requests are normal once the cache is rebuilt.

## **Chapter 8.3 — Aurora Connection Exhaustion**

Under high concurrent load, Aurora can exhaust its connection pool, causing ripple writes to queue in the write-ahead buffer beyond their target flush interval. This causes the database to lag behind the in-memory state, but because the DragonflyDB cache is updated synchronously, retrieval quality is not affected during the lag period.

Prevention: the connection pool is sized generously relative to the expected concurrent load, and Aurora Serverless v2 auto-scaling is configured to increase compute capacity before connection exhaustion occurs. Monitoring includes connection pool utilization as an early warning metric.

Recovery: the write-ahead buffer persists ripples in memory until they can be flushed. If the lag exceeds 60 seconds, the buffer contents are written to S3 as a durable overflow store. When Aurora connectivity is restored, the overflow store is replayed to the database. No ripples are lost.

# **Part Nine: The PRL in the Context of the Complete System**

## **Chapter 9.1 — How the PRL Connects to the EEL**

The Essence and Ego Lattice described in Volume 6 lives inside the PRL. The Essence Core is a set of Level Four ripples with critical importance_band and protected status. The Ego Signature is maintained in the agent_essences table but is read and written through the same ingest pipeline that handles all ripple creation — ego state updates after each session are treated as a special class of ripple-adjacent operations that follow the same lifecycle but are stored in the essences table rather than the ripples table.

The connection between the PRL and the Skill Weave works through the skill_atoms field in agent_essences. When the SWR consolidation identifies a pattern that represents skill learning, the lesson distillation process may produce either a new Level Three ripple or a new SkillAtom, depending on whether the learning is best represented as a memory (a specific insight that should be retrievable) or a skill (a capability that should be automatically applied in relevant contexts). This distinction is made by the distillation algorithm: memories are retrieved; skills are applied.

## **Chapter 9.2 — How the PRL Connects to the Intelligence Pipeline**

Every significant output from the competitive intelligence pipeline — a detected competitor change, an ad library discovery, an SEO ranking shift — is processed through the PRL ingest pipeline for each relevant agent. The intelligence data arrives as Level One ripples (raw signals), which may be processed into Level Two ripples (interpreted signals) either during ingest or during SWR consolidation.

The Campaign Strategist has scope access to all ripples in the org — private_agent ripples for its own memories, shared_campaign ripples for campaign-specific intelligence, and shared_org ripples for organization-wide intelligence. Intelligence pipeline outputs are stored as shared_org ripples so that all agents can access the competitive intelligence when relevant to their specific analysis.

## **Chapter 9.3 — How the PRL Connects to Council Debates**

Every Council debate generates a significant number of ripples across multiple agents. The debate trigger creates a shared_campaign ripple visible to all participating agents. Each agent's position generation creates a private_agent ripple for that agent. The synthesis creates a strategist_only ripple and a shared_campaign ripple. The post-debate reflection of each agent creates a private_agent ripple with the agent's reframing of the outcome through their Essence Core.

The private_agent reflection ripples are the most cognitively important ripples generated by Council sessions. They are where the divergent personality responses to the same event are encoded — where Ogilvy's ripple about losing a debate to Patel is fundamentally different from Patel's ripple about winning the same debate, because their Essence Cores process the same event through completely different lenses. This divergence is what makes the avatars genuinely different rather than just differently styled outputs from the same model.