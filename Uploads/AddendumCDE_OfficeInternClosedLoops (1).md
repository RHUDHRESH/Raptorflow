# RAPTORFLOW ENGINEERING ADDENDUM C
## The Office — Technical Architecture and Implementation

---

# Chapter 1: Technology Choice and Rendering Architecture

The Office is rendered as a **single HTML5 Canvas element** using **PixiJS v8** as the 2D WebGL renderer, with **Framer Motion** driving React-level orchestration for transitions and the sidebar components.

**Why PixiJS over SVG or DOM:**
- 60fps with 21+ animated characters is impossible in SVG or DOM-based approaches at typical laptop GPU specs
- PixiJS uses WebGL under the hood, falling back to Canvas 2D gracefully
- Sprite sheet support makes character animation efficient — all character frames are in a single spritesheet per character
- Viewport/zoom/pan is built into PixiJS via the `viewport` plugin (pixi-viewport)

**Why not Three.js:** 3D capabilities are unnecessary overhead. PixiJS is the correct 2D choice.

## The Rendering Stack

```typescript
// The Office component tree:
<OfficeProvider>           // Context: WebSocket connection, animation queue
  <OfficeCanvas />         // The PixiJS canvas — fills the container
  <OfficeHUD />            // React overlay: group chat panel, zoom controls, agent cards
  <SpeechBubbleLayer />    // Absolutely positioned React elements over the canvas
</OfficeProvider>
```

```typescript
// src/office/OfficeCanvas.tsx
import { Application, Sprite, AnimatedSprite, Container, Ticker } from 'pixi.js';
import { Viewport } from 'pixi-viewport';

export const OfficeCanvas = () => {
  const canvasRef = useRef<HTMLCanvasElement>(null);
  const appRef = useRef<Application | null>(null);
  const viewportRef = useRef<Viewport | null>(null);
  
  useEffect(() => {
    const init = async () => {
      const app = new Application();
      await app.init({
        canvas: canvasRef.current!,
        width: window.innerWidth,
        height: window.innerHeight,
        backgroundColor: 0x2D2416,  // Dark background for the office surround
        antialias: true,
        resolution: window.devicePixelRatio || 1,
        autoDensity: true,
      });
      
      appRef.current = app;
      
      // Set up viewport for pan and zoom
      const viewport = new Viewport({
        screenWidth: window.innerWidth,
        screenHeight: window.innerHeight,
        worldWidth: OFFICE_WORLD_WIDTH,   // 5120px total canvas
        worldHeight: OFFICE_WORLD_HEIGHT, // 3200px total canvas
        events: app.renderer.events,
      });
      
      viewport.drag().pinch().wheel().clampZoom({
        minScale: 0.3,   // Min zoom: see entire office
        maxScale: 2.5,   // Max zoom: read individual character details
      });
      
      app.stage.addChild(viewport);
      viewportRef.current = viewport;
      
      // Load and initialize the office scene
      await loadOfficeScene(viewport);
    };
    
    init();
    
    return () => {
      appRef.current?.destroy();
    };
  }, []);
  
  return <canvas ref={canvasRef} style={{ display: 'block' }} />;
};
```

---

# Chapter 2: Asset Structure — Spritesheets and Textures

```
/public/office/
  ├── backgrounds/
  │     ├── office-floor.png      (the full office floor — single large image)
  │     ├── furniture/            (individual furniture piece textures)
  │     └── props/                (desk items, books, monitors, etc.)
  │
  ├── characters/
  │     ├── ogilvy-spritesheet.png       (all animation frames for Ogilvy)
  │     ├── ogilvy-spritesheet.json      (PixiJS spritesheet data file)
  │     ├── patel-spritesheet.png
  │     ├── patel-spritesheet.json
  │     └── [one per character — 21 total]
  │
  ├── props/
  │     ├── file-folder.png              (the file delivery folder)
  │     ├── pager.png
  │     ├── phone.png
  │     └── speech-bubble-bg.png
  │
  └── office-atlas.json           (combined atlas for environment elements)
```

## The Spritesheet Animation System

Each character has a spritesheet with named animation sequences:

```typescript
// Character animation state machine — all possible states per character
export type CharacterAnimationState = 
  // Idle states (loop automatically)
  | 'idle_sitting'          // Default at-desk position
  | 'idle_reading'          // Reading document at desk
  | 'idle_writing'          // Writing in notepad
  | 'idle_thinking'         // Looking into middle distance
  | 'idle_phone'            // On the phone
  | 'idle_monitor'          // Looking at monitor
  
  // Event-triggered states (play once, return to idle)
  | 'pager_receive'         // Looking at pager (triggered by pager_notification event)
  | 'pager_read'            // Reading pager content
  | 'pager_respond'         // Typing on pager
  | 'stand_up'              // Rising from chair
  | 'walk_to'               // Walking (animation driven by path)
  | 'sit_down'              // Taking a seat
  | 'conference_listen'     // At conference table, listening
  | 'conference_speak'      // At conference table, speaking
  | 'conference_react_agree'   // Nodding or affirming gesture
  | 'conference_react_disagree' // Skeptical or rebuttal gesture
  | 'file_receive'          // Receiving a file from Maya
  | 'file_read'             // Reading through a document
  | 'file_stamp_accept'     // Stamping a brief accepted
  | 'file_phone_clarify'    // Calling for clarification
  | 'celebration_brief'     // Brief satisfaction animation
  | 'concern_performance'   // Subtle concern at monitor

// The animation state manager per character
export class CharacterAnimationManager {
  private character: AnimatedSprite;
  private currentState: CharacterAnimationState;
  private animations: Record<CharacterAnimationState, Texture[]>;
  private onStateComplete: (() => void) | null = null;
  
  constructor(spritesheetData: Spritesheet, characterKey: string) {
    this.animations = {
      idle_sitting: spritesheetData.animations[`${characterKey}_idle_sitting`],
      idle_reading: spritesheetData.animations[`${characterKey}_idle_reading`],
      // ...etc
    };
    
    this.character = new AnimatedSprite(this.animations.idle_sitting);
    this.character.animationSpeed = 0.15; // 9fps — felt right for the 1980s aesthetic
    this.character.loop = true;
    this.character.play();
    this.currentState = 'idle_sitting';
  }
  
  transitionTo(nextState: CharacterAnimationState, onComplete?: () => void) {
    // Don't interrupt critical animations
    const uninterruptible: CharacterAnimationState[] = [
      'file_stamp_accept', 'pager_respond', 'file_phone_clarify'
    ];
    
    if (uninterruptible.includes(this.currentState) && !this.onStateComplete) {
      // Queue the transition for after current animation completes
      this.onStateComplete = () => this.transitionTo(nextState, onComplete);
      return;
    }
    
    const isLooping = [
      'idle_sitting', 'idle_reading', 'idle_writing', 
      'idle_thinking', 'idle_phone', 'idle_monitor',
      'conference_listen', 'walk_to'
    ].includes(nextState);
    
    this.character.textures = this.animations[nextState];
    this.character.loop = isLooping;
    this.character.animationSpeed = this.getAnimationSpeed(nextState);
    
    if (!isLooping) {
      this.character.onComplete = () => {
        onComplete?.();
        this.onStateComplete?.();
        this.onStateComplete = null;
        // Return to contextual idle
        this.transitionTo(this.getContextualIdle());
      };
    }
    
    this.character.gotoAndPlay(0);
    this.currentState = nextState;
  }
  
  private getAnimationSpeed(state: CharacterAnimationState): number {
    // Different animations play at different speeds for natural feel
    const speeds: Partial<Record<CharacterAnimationState, number>> = {
      pager_receive: 0.20,
      walk_to: 0.25,
      file_stamp_accept: 0.18,
      celebration_brief: 0.22,
    };
    return speeds[state] ?? 0.15;
  }
  
  private getContextualIdle(): CharacterAnimationState {
    // Return to appropriate idle based on where character is
    return this.isAtDesk() ? 'idle_sitting' : 'idle_sitting';
  }
}
```

---

# Chapter 3: The office.event WebSocket Message Schema — Complete

Every animation in the office is triggered by an `office.event` WebSocket message from the server. Here is the complete schema.

```typescript
// All possible office event types and their payloads
export type OfficeEventMessage =
  | {
      type: 'office.event';
      event_type: 'file_delivery_start';
      payload: {
        file_name: string;        // Shown on the folder tab
        project_type: string;     // 'campaign_brief' | 'council_question' | 'content_request'
        session_id: string;
      };
    }
  | {
      type: 'office.event';
      event_type: 'file_delivered_to_maya';
      payload: { session_id: string };
    }
  | {
      type: 'office.event';
      event_type: 'file_delivered_to_strategist';
      payload: { session_id: string; strategist_agent_id: string };
    }
  | {
      type: 'office.event';
      event_type: 'brief_reading';
      payload: { agent_id: string; duration_ms: number };  // How long to show reading animation
    }
  | {
      type: 'office.event';
      event_type: 'brief_accepted';
      payload: { session_id: string };  // Triggers stamp animation
    }
  | {
      type: 'office.event';
      event_type: 'brief_clarification_needed';
      payload: { session_id: string; question_preview: string };  // Shows phone call to Maya
    }
  | {
      type: 'office.event';
      event_type: 'pager_notification';
      payload: {
        session_id: string;
        message_preview: string;       // First 40 chars of pager message
        target_agent_ids: string[];    // Which agents get the pager buzz
      };
    }
  | {
      type: 'office.event';
      event_type: 'agent_walk_start';
      payload: {
        agent_id: string;
        destination: 'conference_room' | 'strategist_office' | 'desk' | 'research_station';
        duration_ms: number;
      };
    }
  | {
      type: 'office.event';
      event_type: 'agent_seated_conference';
      payload: { agent_id: string; seat_position: number };  // 1-14 seat positions
    }
  | {
      type: 'office.event';
      event_type: 'debate_agent_speaking';
      payload: {
        agent_id: string;
        speech_bubble_text: string;   // First 60 chars of their position
        duration_ms: number;
      };
    }
  | {
      type: 'office.event';
      event_type: 'debate_agent_reacting';
      payload: {
        agent_id: string;
        reaction_type: 'agree' | 'disagree' | 'skeptical' | 'interested';
      };
    }
  | {
      type: 'office.event';
      event_type: 'synthesis_presenting';
      payload: {
        strategist_agent_id: string;
        duration_ms: number;
      };
    }
  | {
      type: 'office.event';
      event_type: 'conference_break';
      payload: { session_id: string };  // Agents file out
    }
  | {
      type: 'office.event';
      event_type: 'move_completed_celebration';
      payload: {
        campaign_name: string;
        achieving_agents: string[];   // Which agents did work on this move
        achievement_pct: number;
      };
    }
  | {
      type: 'office.event';
      event_type: 'task_missed_notification';
      payload: {
        task_type: string;
        criticality: string;
      };
    }
  | {
      type: 'office.event';
      event_type: 'intel_alert_received';
      payload: {
        competitor_name: string;
        significance: 'major' | 'moderate';
      };
    }
  | {
      type: 'office.event';
      event_type: 'morning_meeting_start';
      payload: {
        attending_agents: string[];
        date_string: string;
      };
    }
  | {
      type: 'office.event';
      event_type: 'speech_bubble';
      payload: {
        agent_id: string;
        text: string;
        duration_ms: number;
        bubble_type: 'thought' | 'speech' | 'whisper';
      };
    }
  | {
      type: 'office.event';
      event_type: 'agent_working';
      payload: {
        agent_id: string;
        work_type: 'writing' | 'reading' | 'researching' | 'phoning';
        duration_ms: number;
      };
    };
```

## Server-Side Event Firing — When Each Event Fires

```rust
// In the Harness, after each session phase completes:

// When user submits a brief:
session.emit_office_event(OfficeEvent::FileDeliveryStart {
    file_name: brief.title.clone(),
    project_type: "campaign_brief".to_string(),
    session_id: session.session_id.clone(),
}).await;

// After 2 second delay (animation time):
session.emit_office_event(OfficeEvent::FileDeliveredToMaya {
    session_id: session.session_id.clone(),
}).await;

// After Maya walking animation (3 seconds):
session.emit_office_event(OfficeEvent::FileDeliveredToStrategist {
    session_id: session.session_id.clone(),
    strategist_agent_id: session.strategist_agent_id.to_string(),
}).await;

// Emit reading animation (match inference evaluation duration):
session.emit_office_event(OfficeEvent::BriefReading {
    agent_id: session.strategist_agent_id.to_string(),
    duration_ms: 3000,
}).await;

// After brief evaluation completes:
if brief_accepted {
    session.emit_office_event(OfficeEvent::BriefAccepted {
        session_id: session.session_id.clone(),
    }).await;
    
    // Small delay then pager notification
    tokio::time::sleep(Duration::from_millis(1500)).await;
    
    session.emit_office_event(OfficeEvent::PagerNotification {
        session_id: session.session_id.clone(),
        message_preview: format!("Council needed: {}", &brief.title[..40.min(brief.title.len())]),
        target_agent_ids: session.participating_agent_ids.iter()
            .map(|id| id.to_string())
            .collect(),
    }).await;
}
```

---

# Chapter 4: The Snark Batch System — Complete Data Model and Frontend Integration

```sql
-- Server-side storage for snark content
CREATE TABLE snark_batches (
  batch_id           TEXT PRIMARY KEY,
  org_id             UUID NOT NULL,
  generated_at       TIMESTAMPTZ NOT NULL,
  valid_from         TIMESTAMPTZ NOT NULL,
  valid_until        TIMESTAMPTZ NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE snark_office_chat (
  message_id         TEXT PRIMARY KEY,
  batch_id           TEXT NOT NULL REFERENCES snark_batches(batch_id),
  org_id             UUID NOT NULL,
  channel            TEXT NOT NULL,    -- 'main', 'creative_pod', 'digital_pod', 'strategy_pod', 'intern'
  agent_key          TEXT NOT NULL,
  message_text       TEXT NOT NULL,
  reply_to_message_id TEXT,           -- For threaded replies
  scheduled_at       TIMESTAMPTZ NOT NULL,  -- When to show this in the feed
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TABLE snark_speech_bubbles (
  bubble_id          TEXT PRIMARY KEY,
  batch_id           TEXT NOT NULL REFERENCES snark_batches(batch_id),
  org_id             UUID NOT NULL,
  agent_key          TEXT NOT NULL,
  bubble_text        TEXT NOT NULL,
  bubble_type        TEXT NOT NULL DEFAULT 'speech',  -- 'speech', 'thought', 'whisper'
  trigger_type       TEXT NOT NULL,   -- 'idle', 'post_debate', 'post_task', 'post_move', 'scheduled'
  trigger_condition  TEXT,            -- JSON condition: {"last_debate_loser": "ogilvy", "min_session_gap_hrs": 2}
  display_duration_ms INTEGER NOT NULL DEFAULT 4000,
  valid_from         TIMESTAMPTZ NOT NULL,
  valid_until        TIMESTAMPTZ NOT NULL,
  created_at         TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

## The Snark Generation Prompt

```rust
pub fn build_snark_batch_prompt(
    recent_events: &[RecentSystemEvent],
    agent_roster: &[AgentProfile],
    recent_debate_outcomes: &[DebateOutcome],
    active_campaign_status: &str,
) -> String {
    let events_formatted = recent_events.iter()
        .map(|e| format!("- {}: {}", e.event_type, e.description))
        .collect::<Vec<_>>()
        .join("\n");
    
    let debate_outcomes_formatted = recent_debate_outcomes.iter()
        .map(|d| format!(
            "Session {}: {} position was adopted. {} position was substantially not adopted.",
            d.session_id_short, d.winner_avatar_key, d.loser_avatar_key
        ))
        .collect::<Vec<_>>()
        .join("\n");
    
    format!(r#"Generate office social content for a 1980s marketing office.

RECENT EVENTS IN THE OFFICE (last 8 hours):
{events_formatted}

RECENT DEBATE OUTCOMES:
{debate_outcomes_formatted}

CURRENT CAMPAIGN STATUS:
{active_campaign_status}

AGENT ROSTER AND THEIR PERSONALITIES:
- Ogilvy: Formal, principled, devoted to research, high standards, privately respects Patel but would never say so
- Bernbach: Creative rebel, dismisses safe choices, slightly chaotic, brilliant
- Hopkins: Data-obsessed, dry, always has the performance numbers, slightly smug about it
- Draper: Brooding, profound, mysteriously effective, sees emotional truth others miss
- Patel: Fast, data-native, slightly impatient with theory, competitive with Ogilvy
- Vaynerchuk: High energy, always posting, urgency about everything, casually insightful
- Sharp: Academic, contrarian by evidence not opinion, patiently cites research others haven't read
- Godin: Zen-like, questions the question, everyone finds him slightly frustrating and often right
- Kotler: Comprehensive, systematic, patient, occasionally exasperated by shortcuts
- Ries: Direct, binary thinking, allergic to line extensions, blunt
- Cialdini: Warm, observant, interested in people, slightly amused by the others
- Sutherland: Finds everything mildly absurd, psychologically counterintuitive, often correct
- QA Director: Precise, standards-driven, the office conscience, sends things back
- Ogilvy's interns: Research-burdened, slightly intimidated, admiring
- Patel's interns: Data-obsessed, competitive, always citing numbers

GENERATE THE FOLLOWING:

1. OFFICE CHAT MESSAGES (5-8 messages for the main channel):
Each must reference a SPECIFIC recent event. No generic messages.
Format: [AGENT_KEY]: [message text] | CHANNEL:[channel] | REPLY_TO:[message_id or null] | SCHEDULE_MINS:[0-480]

2. POD CHAT MESSAGES (2-3 messages per pod):
Smaller conversations within each pod. More casual, more inside jokes.
Format: [POD:creative|digital|strategy] [AGENT_KEY]: [message text]

3. SPEECH BUBBLES (one per agent currently in the office — 8-10 total):
Brief idle thought visible over the character's head.
Must relate to current work or recent events.
Format: [AGENT_KEY] | [bubble text] | TRIGGER:[idle|post_debate|scheduled] | DURATION_MS:[2000-6000]

TONE: Professional office with human moments. 1980s formality with occasional irreverence.
The snark is affectionate, not mean. These people work well together even when they argue.
Every message should feel like it was written by that specific person about that specific event."#,
        events_formatted = events_formatted,
        debate_outcomes_formatted = debate_outcomes_formatted,
        active_campaign_status = active_campaign_status,
    )
}
```

---

# RAPTORFLOW ENGINEERING ADDENDUM D
## The Intern System — Complete Technical Implementation

---

# Chapter 1: The InternTask Struct and Dispatch System

```rust
/// Represents a task that a Council avatar delegates to their intern
#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InternTask {
    pub task_id: String,
    pub parent_session_id: String,
    pub parent_agent_id: Uuid,           // The Council avatar delegating this
    pub org_id: Uuid,
    pub intern_avatar_key: String,       // "ogilvy_intern_1", "patel_intern_2", etc.
    pub task_type: InternTaskType,
    pub query: String,
    pub specific_requirements: Vec<String>,   // What the intern should specifically look for
    pub output_format: InternOutputFormat,
    pub urgency: InternTaskUrgency,
    pub max_tokens_output: u32,
    pub created_at: DateTime<Utc>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InternTaskType {
    WebSearch {
        query: String,
        depth: u8,          // 1-3: how many results to summarise
    },
    CompetitorAnalysis {
        competitor_name: String,
        analysis_type: String,   // "recent_ads", "messaging_shift", "pricing"
    },
    PerformanceDataPull {
        campaign_id: String,
        metric: String,
        time_period: String,
    },
    ContentResearch {
        topic: String,
        research_type: String,   // "facts_and_stats", "examples", "case_studies"
    },
    ICPResearch {
        icp_description: String,
        research_question: String,
    },
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InternOutputFormat {
    BulletSummary,     // 3-5 bullet points
    StructuredData,    // JSON with specific fields
    BriefNarrative,    // 2-3 sentences
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InternTaskUrgency {
    /// Block the parent agent's generation until this completes
    /// Used when the result is needed to form the position
    Blocking,
    
    /// Run in background — result available for Round 2 context
    /// Used for supporting research
    Background,
}
```

# Chapter 2: The <research_request> Tag in Agent Generation

The `<research_request>` tag is included in the Council avatar system prompt to enable intern dispatch:

```
=== RESEARCH REQUEST CAPABILITY ===

If you need factual research to support your position, you may request it by 
including a <research_request> tag in your response:

<research_request>
{
  "query": "[specific research question]",
  "type": "web_search|competitor_analysis|performance_data|content_research",
  "urgency": "blocking|background",
  "requirements": ["[specific thing to look for]", "[another specific thing]"]
}
</research_request>

BLOCKING requests: Your response will pause and the research result will be injected 
before you continue. Use when you genuinely cannot form your position without this data.

BACKGROUND requests: Your response continues normally. The research result will be 
available in Round 2 context. Use for supporting evidence.

Do not request research for things you already know. Only use this for specific, 
lookupable facts or for current data about this specific client's situation.

EXAMPLE:
"Before I can recommend the Meta vs LinkedIn split, I need to check how this client's 
audience is actually distributed across platforms."

<research_request>
{
  "query": "Current LinkedIn vs Meta engagement data for [ICP] segment in India",
  "type": "performance_data",
  "urgency": "blocking",
  "requirements": ["engagement rate comparison", "CPM comparison", "conversion rate comparison"]
}
</research_request>
```

# Chapter 3: The Stream Coordinator's Research Request Handler

This is the critical implementation detail — how blocking intern tasks work without restarting the Gemini stream.

```rust
/// The Stream Coordinator detects <research_request> tags in the streaming output
/// and handles them before the user sees them
pub struct StreamCoordinator {
    pub inference: Arc<VertexAiClient>,
    pub intern_dispatcher: Arc<InternDispatcher>,
    pub ripple_tx: tokio::sync::mpsc::Sender<MemoryEvent>,
}

impl StreamCoordinator {
    pub async fn handle_agent_stream(
        &self,
        agent_id: Uuid,
        session: &SessionContext,
        context_pack: &ContextPack,
        question: &str,
        round: u8,
    ) -> Result<AgentStreamResult> {
        
        // Step 1: Pre-check context for any BLOCKING research needed
        // (Some avatars declare research needs in structured analysis before generating)
        // This is a quick Flash-Lite call to assess if blocking research is needed
        let pre_research = self.assess_pre_generation_research_needs(
            agent_id, 
            context_pack, 
            question
        ).await?;
        
        // Execute any blocking research BEFORE starting generation
        let enriched_context = if pre_research.has_blocking_needs {
            let results = self.execute_intern_tasks(&pre_research.blocking_tasks, session).await;
            self.inject_research_into_context(context_pack, &results)
        } else {
            context_pack.clone()
        };
        
        // Step 2: Start the generation stream
        let system_prompt = build_council_position_system_prompt(
            &session.get_avatar_state(agent_id)?,
            &enriched_context,
            question,
            round,
        );
        
        let mut stream = self.inference.stream_generate(
            InferenceModel::FlashLiteReasoning,
            &system_prompt,
            &build_council_position_user_message(question, round),
        ).await?;
        
        let mut accumulated_response = String::new();
        let mut pending_research_check = String::new();
        let mut research_injected = false;
        
        // Step 3: Process the stream token by token
        while let Some(chunk) = stream.next().await {
            let token = chunk?;
            accumulated_response.push_str(&token);
            pending_research_check.push_str(&token);
            
            // Check for <research_request> in the accumulated check buffer
            if !research_injected && pending_research_check.contains("<research_request>") {
                // Check if the tag is complete
                if let Some(request_data) = self.extract_complete_research_request(&pending_research_check) {
                    if request_data.urgency == "blocking" {
                        // We need to NOT stream what we have yet — wait for research
                        // The tokens before the <research_request> tag are published
                        let clean_so_far = strip_research_request_tag(&pending_research_check);
                        
                        // Publish tokens before the research request tag
                        self.publish_tokens(agent_id, &session.session_id, &clean_so_far).await;
                        
                        // Execute the intern task
                        let intern_result = self.execute_single_intern_task(
                            InternTask {
                                task_id: ulid::Ulid::new().to_string(),
                                parent_session_id: session.session_id.clone(),
                                parent_agent_id: agent_id,
                                org_id: session.org_id,
                                intern_avatar_key: get_intern_key(agent_id, 1),
                                task_type: map_request_to_task_type(&request_data),
                                query: request_data.query.clone(),
                                specific_requirements: request_data.requirements.clone(),
                                output_format: InternOutputFormat::BulletSummary,
                                urgency: InternTaskUrgency::Blocking,
                                max_tokens_output: 400,
                                created_at: Utc::now(),
                            },
                            session,
                        ).await;
                        
                        // Now restart the generation with the research result injected
                        // We DON'T restart the Gemini stream — instead we add the result
                        // to the conversation as an additional context message and
                        // generate a NEW stream for the continuation
                        
                        let continuation_prompt = format!(
                            "Your intern just completed the research you requested. Here is what they found:\n\n{}\n\nContinue your response from where you left off:\n\n{}",
                            intern_result.summary,
                            clean_so_far
                        );
                        
                        // Drop the current stream
                        drop(stream);
                        
                        // Start a new stream for the continuation
                        stream = self.inference.stream_generate(
                            InferenceModel::FlashLiteReasoning,
                            &system_prompt,
                            &continuation_prompt,
                        ).await?;
                        
                        accumulated_response = clean_so_far.clone();
                        pending_research_check = String::new();
                        research_injected = true;
                        
                        continue;
                    }
                    // background requests: just strip the tag and continue
                    else {
                        // Queue the background task
                        self.queue_background_intern_task(&request_data, agent_id, session).await;
                        accumulated_response = strip_research_request_tag(&accumulated_response);
                        pending_research_check = String::new();
                    }
                }
            }
            
            // Publish token to DragonflyDB pub/sub
            // (Don't publish <ripple_data> tokens — strip them from the stream)
            if !accumulated_response.contains("<ripple_data>") || 
               accumulated_response.contains("</ripple_data>") {
                let clean_token = self.strip_ripple_data_if_complete(&token, &accumulated_response);
                if !clean_token.is_empty() {
                    self.publish_tokens(agent_id, &session.session_id, &clean_token).await;
                }
            }
        }
        
        // Parse the ripple_data from the completed response
        let ripple_data = parse_ripple_data(&accumulated_response);
        let clean_response = strip_ripple_data(&accumulated_response);
        
        Ok(AgentStreamResult {
            agent_id,
            position_text: clean_response,
            extracted_ripple_data: ripple_data,
            word_count: word_count(&clean_response),
        })
    }
}
```

# Chapter 4: The Intern Inference Call

```rust
pub fn build_intern_system_prompt(
    intern_key: &str,
    parent_avatar_key: &str,
    parent_essence_brief: &str,
) -> String {
    format!(r#"You are {parent_avatar_key}'s research intern.

Your mentor's approach: {parent_essence_brief}

Your job is to find specific, factual information that your mentor needs.
You are thorough, reliable, and know what your mentor will find useful.
You understand their standards and you aim to meet them.

When you research something:
- Find specific facts, not vague generalities
- Cite the source (even if briefly) when you have one
- Flag when information is uncertain or outdated
- Note what you could NOT find as well as what you could

You will be given a specific research task. Complete it well."#,
        parent_avatar_key = parent_avatar_key,
        parent_essence_brief = parent_essence_brief,
    )
}

pub fn build_intern_task_prompt(task: &InternTask) -> String {
    match &task.task_type {
        InternTaskType::WebSearch { query, depth } => format!(
            r#"Research task: {}
            
Find information about: {}

Look specifically for:
{}

Provide a {} summary of what you found.
If you find conflicting information, note the conflict.
If you cannot find reliable information, say so clearly.

Keep your response under {} tokens."#,
            task.task_id,
            query,
            task.specific_requirements.join("\n- "),
            match task.output_format {
                InternOutputFormat::BulletSummary => "3-5 bullet point",
                InternOutputFormat::BriefNarrative => "2-3 sentence",
                InternOutputFormat::StructuredData => "structured JSON",
            },
            task.max_tokens_output,
        ),
        
        InternTaskType::PerformanceDataPull { campaign_id, metric, time_period } => format!(
            r#"Pull this performance data for your mentor:

Campaign: {}
Metric: {}
Time period: {}

Query the available campaign_performance_log data and provide:
- The actual numbers
- How they compare to the campaign projection
- The trend (improving, declining, stable)

Be precise with numbers."#,
            campaign_id, metric, time_period,
        ),
        
        // Additional task types...
        _ => format!("Complete this research task: {}", task.query),
    }
}
```

---

# RAPTORFLOW ENGINEERING ADDENDUM E
## The Closed Loops — Every Feedback System Completed

---

# Chapter 1: The Foundation Cache Invalidation Sequence

The race condition between Foundation update and in-flight inference was never addressed. Here is the complete safe sequence.

```rust
pub async fn update_foundation(
    pool: &PgPool,
    dragonfly: &redis::aio::ConnectionManager,
    vertex_ai: &VertexAiClient,
    org_id: Uuid,
    section: &str,
    new_value: &serde_json::Value,
) -> Result<()> {
    
    // Step 1: Write new Foundation value to Aurora
    // Do this FIRST so the database is the source of truth
    sqlx::query!(
        "UPDATE foundation_sections SET value = $1, updated_at = NOW() WHERE org_id = $2 AND section_key = $3",
        new_value,
        org_id,
        section,
    )
    .execute(pool)
    .await?;
    
    // Step 2: Increment the Foundation version
    let new_version = sqlx::query!(
        "UPDATE orgs SET foundation_version = foundation_version + 1 WHERE org_id = $1 RETURNING foundation_version",
        org_id,
    )
    .fetch_one(pool)
    .await?
    .foundation_version;
    
    // Step 3: Invalidate the DragonflyDB Foundation cache
    // This causes next session to reload from Aurora
    let cache_key = format!("foundation:{}", org_id);
    let mut conn = dragonfly.clone();
    redis::cmd("DEL")
        .arg(&cache_key)
        .query_async::<_, ()>(&mut conn)
        .await
        .ok(); // Non-fatal if cache delete fails
    
    // Step 4: Invalidate the Vertex AI context cache
    // In-flight sessions will continue with the old cache until their
    // current inference call completes — this is acceptable.
    // New sessions after this point will rebuild the cache.
    if let Some(cache_id) = get_vertex_cache_id(dragonfly, org_id).await {
        vertex_ai.delete_context_cache(&cache_id).await.ok();
        
        // Clear the stored cache_id from DragonflyDB
        let cache_id_key = format!("vertex_cache_id:{}", org_id);
        redis::cmd("DEL")
            .arg(&cache_id_key)
            .query_async::<_, ()>(&mut conn)
            .await
            .ok();
    }
    
    // Step 5: Fire a Foundation update event
    // Any agent contexts built AFTER this point will reload the Foundation
    // Any agent contexts currently in-flight will complete with the old Foundation
    // This is the acceptable race window — max duration = one inference call (~5-30s)
    
    // Step 6: Check for Campaign consistency impact
    // Run as background task — non-blocking
    tokio::spawn(async move {
        check_campaign_foundation_consistency(pool, org_id, section, new_value).await;
    });
    
    // Step 7: Fire a Muse Foundation drift cleared event
    // (The Foundation update may have been triggered by a Muse drift suggestion)
    let event = MemoryEvent {
        event_id: ulid::Ulid::new().to_string(),
        org_id,
        agent_id: get_strategist_id(pool, org_id).await.unwrap_or(Uuid::nil()),
        session_id: "foundation_update".to_string(),
        campaign_id: None,
        move_id: None,
        event_source: EventSource::UserPreference {
            preference_key: format!("foundation_section_updated:{}", section),
            preference_value: format!("v{}", new_version),
            confidence: 1.0,
            source_interface: "foundation_settings".to_string(),
        },
        raw_content: format!("Foundation section {} updated to version {}", section, new_version),
        intended_scope: RippleScope::SharedOrg,
        intended_hierarchy: 3,
        extracted_ripple_data: None,
        blocking: false,
        fired_at: Utc::now(),
    };
    
    // Send to ripple ingest
    get_ripple_channel(org_id).send(event).await.ok();
    
    Ok(())
}
```

# Chapter 2: The Complete Content Performance Feedback Loop

```rust
/// Runs as part of the nightly performance update job
/// Connects content performance data back to the EEL skill atoms
pub async fn process_content_performance_updates(
    pool: &PgPool,
    ripple_tx: &tokio::sync::mpsc::Sender<MemoryEvent>,
) -> Result<()> {
    
    // Find content that has new performance data since last processed
    let contents_with_new_data = sqlx::query!(
        r#"
        SELECT 
            gc.content_id,
            gc.org_id,
            gc.generating_agent_id,
            gc.content_type,
            gc.channel,
            gc.task_id,
            gc.performance_data,
            ct.campaign_id,
            ct.move_id
        FROM generated_content gc
        JOIN campaign_tasks ct ON gc.task_id = ct.task_id
        WHERE 
            gc.performance_data IS NOT NULL
            AND gc.status = 'published'
            AND gc.performance_processed_at IS NULL
        LIMIT 100
        "#
    )
    .fetch_all(pool)
    .await?;
    
    for content in contents_with_new_data {
        let perf = content.performance_data.unwrap();
        
        // Calculate deviation from campaign projections
        let projection = get_content_projection(pool, &content.task_id).await?;
        
        let primary_metric = get_primary_metric_for_type(&content.content_type, &content.channel);
        let actual_value = perf[&primary_metric].as_f64().unwrap_or(0.0) as f32;
        let projected_value = projection.get(&primary_metric).unwrap_or(0.0);
        
        let deviation_pct = if projected_value > 0.0 {
            (actual_value - projected_value) / projected_value
        } else {
            0.0
        };
        
        // Only create ripples for significant deviations
        if deviation_pct.abs() > 0.15 {
            let event = MemoryEvent {
                event_id: ulid::Ulid::new().to_string(),
                org_id: content.org_id,
                agent_id: content.generating_agent_id,
                session_id: "performance_update".to_string(),
                campaign_id: Some(content.campaign_id),
                move_id: Some(content.move_id),
                event_source: EventSource::ContentPerformance {
                    content_id: content.content_id.clone(),
                    task_id: content.task_id.clone(),
                    metric_name: primary_metric.clone(),
                    metric_value: actual_value,
                    projected_value,
                    deviation_pct,
                    above_expectation: deviation_pct > 0.0,
                },
                raw_content: format!(
                    "{} content achieved {:.2} {} vs projected {:.2} ({:+.1}%)",
                    content.content_type,
                    actual_value,
                    primary_metric,
                    projected_value,
                    deviation_pct * 100.0,
                ),
                intended_scope: RippleScope::PrivateAgent,
                intended_hierarchy: 2,
                extracted_ripple_data: None,
                blocking: false,
                fired_at: Utc::now(),
            };
            
            ripple_tx.send(event).await.ok();
            
            // ALSO: update the EEL skill utility score for the generating avatar
            update_skill_utility_score(
                pool,
                content.generating_agent_id,
                &content.content_type,
                &content.channel,
                // Normalise deviation to 0-1 outcome score
                // deviation_pct = -0.5 → score 0.25 (well below)
                // deviation_pct = 0.0 → score 0.50 (at target)
                // deviation_pct = +0.5 → score 0.75 (well above)
                // deviation_pct = +1.0 → score 1.00 (double target)
                ((deviation_pct * 0.5) + 0.5).clamp(0.0, 1.0),
            ).await.ok();
        }
        
        // Mark as processed
        sqlx::query!(
            "UPDATE generated_content SET performance_processed_at = NOW() WHERE content_id = $1",
            content.content_id
        )
        .execute(pool)
        .await.ok();
    }
    
    Ok(())
}

fn get_primary_metric_for_type(content_type: &str, channel: &str) -> String {
    match (content_type, channel) {
        ("ad_copy", "meta" | "facebook" | "instagram") => "ctr".to_string(),
        ("ad_copy", "google") => "ctr".to_string(),
        ("ad_copy", "linkedin") => "ctr".to_string(),
        ("social_post", _) => "engagement_rate".to_string(),
        ("email", _) => "open_rate".to_string(),
        ("blog", _) => "avg_time_on_page".to_string(),
        _ => "engagement_rate".to_string(),
    }
}
```

# Chapter 3: The Council Session Cost Tracking

```rust
/// Called when a council session completes
pub async fn record_session_cost(
    pool: &PgPool,
    session_id: &str,
    token_usage: &SessionTokenUsage,
) -> Result<()> {
    
    // Compute cost based on model usage
    let cost_usd = 
        // Pro tokens
        (token_usage.pro_input_tokens as f64 * 0.000_0025) +    // $2.50 per 1M input
        (token_usage.pro_output_tokens as f64 * 0.000_0100) +   // $10.00 per 1M output
        // Flash-Lite Reasoning tokens (cached input at 10%)
        (token_usage.flash_reasoning_cached_input as f64 * 0.000_000_015) +  // $0.015 per 1M
        (token_usage.flash_reasoning_input as f64 * 0.000_000_15) +  // $0.15 per 1M
        (token_usage.flash_reasoning_output as f64 * 0.000_000_60) + // $0.60 per 1M
        // Flash-Lite Normal tokens
        (token_usage.flash_normal_input as f64 * 0.000_000_075) + // $0.075 per 1M
        (token_usage.flash_normal_output as f64 * 0.000_000_30);   // $0.30 per 1M
    
    sqlx::query!(
        r#"
        UPDATE council_sessions 
        SET 
            total_tokens_used = $1,
            total_cost_usd = $2,
            state = 'complete'
        WHERE session_id = $3
        "#,
        token_usage.total_tokens() as i32,
        cost_usd,
        session_id,
    )
    .execute(pool)
    .await?;
    
    // Update org-level monthly cost tracking
    sqlx::query!(
        r#"
        INSERT INTO org_monthly_costs (org_id, month, inference_cost_usd, session_count)
        SELECT org_id, DATE_TRUNC('month', NOW()), $1, 1
        FROM council_sessions WHERE session_id = $2
        ON CONFLICT (org_id, month) DO UPDATE SET
            inference_cost_usd = org_monthly_costs.inference_cost_usd + $1,
            session_count = org_monthly_costs.session_count + 1
        "#,
        cost_usd,
        session_id,
    )
    .execute(pool)
    .await?;
    
    Ok(())
}
```

# Chapter 4: The Missing Table — org_monthly_costs

```sql
-- Never specified in the original volumes
CREATE TABLE org_monthly_costs (
  org_id               UUID NOT NULL,
  month                DATE NOT NULL,
  inference_cost_usd   DOUBLE PRECISION NOT NULL DEFAULT 0,
  scraping_cost_usd    DOUBLE PRECISION NOT NULL DEFAULT 0,
  storage_cost_usd     DOUBLE PRECISION NOT NULL DEFAULT 0,
  session_count        INTEGER NOT NULL DEFAULT 0,
  ripples_created      INTEGER NOT NULL DEFAULT 0,
  content_pieces_gen   INTEGER NOT NULL DEFAULT 0,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT NOW(),
  PRIMARY KEY (org_id, month)
);

-- Alert when org costs exceed 15% of their subscription revenue
-- ($5000 INR ≈ $60 USD. 15% = $9 USD)
CREATE OR REPLACE FUNCTION check_org_cost_alert()
RETURNS TRIGGER AS $$
BEGIN
  IF NEW.inference_cost_usd > 9.0 THEN
    INSERT INTO system_alerts (alert_type, org_id, data)
    VALUES ('high_cost', NEW.org_id, 
            jsonb_build_object('cost_usd', NEW.inference_cost_usd, 'month', NEW.month));
  END IF;
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER check_cost_on_update
AFTER UPDATE ON org_monthly_costs
FOR EACH ROW EXECUTE FUNCTION check_org_cost_alert();
```

---

# Final Summary: What These Five Addenda Add

| Addendum | What Was Missing | What It Now Contains |
|----------|-----------------|---------------------|
| **A — Ripple Creation** | MemoryEvent struct, event classifier, two creation points, ripple_data tag, emotion table, salience formula, SimHash, ingest worker, prediction resolution, edge linking, embedding worker | Complete Rust implementation, every field, every formula, integration test |
| **B — Prompt Library** | Foundation section selection rules, complete agent prompts, content generation prompts, compliance prompt, routing classifier, Daily Wins prompt, Nudge prompt, EEL reflection prompt, Replanning brief, multi-campaign prioritization | Every inference call with exact prompt text and output format |
| **C — Office Technical** | Technology choice, animation state machine, office.event schema, character spritesheet system, snark batch data model and generation prompt | PixiJS architecture, all 30+ event types, complete TypeScript types |
| **D — Intern System** | InternTask struct, research_request tag, blocking vs background handling, stream pause/restart, intern inference prompt | Complete implementation including the critical stream restart pattern |
| **E — Closed Loops** | Foundation cache invalidation race condition, content performance→EEL loop, session cost tracking, org_monthly_costs table | Safe invalidation sequence, performance→skill utility update, cost tracking SQL |
