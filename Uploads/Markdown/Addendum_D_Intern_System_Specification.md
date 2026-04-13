# RAPTORFLOW ADDENDUM D: THE INTERN SYSTEM COMPLETE SPECIFICATION

This addendum fills the critical gaps identified in RedTeam Audit Hole 4.

---

## 4A — InternTask Struct and Intern Types

```rust
// crates/harness/src/interns/mod.rs

use serde::{Deserialize, Serialize};
use uuid::Uuid;

pub struct InternSystem {
    pub tiers: HashMap<InternTier, InternTierConfig>,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InternTask {
    pub task_id: String,
    pub parent_agent_id: Uuid,
    pub parent_session_id: String,
    pub intern_tier: InternTier,
    pub task_type: InternTaskType,
    pub query: String,
    pub urgency: InternUrgency,
    pub status: InternTaskStatus,
    pub result: Option<InternResult>,
    pub created_at: DateTime<Utc>,
    pub completed_at: Option<DateTime<Utc>>,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum InternTier {
    ResearchIntern,      // Web search, competitive research
    DataIntern,          // Performance data analysis
    CreativeIntern,       // Content variants, copy tests
    TechIntern,          // Technical research, platform analysis
}

#[derive(Debug, Clone, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum InternTaskType {
    WebSearch,
    CompetitiveAnalysis,
    PerformanceAnalysis,
    ContentVariant,
    CopyTest,
    PlatformResearch,
    AudienceResearch,
}

#[derive(Debug, Clone, Copy, Serialize, Deserialize)]
#[serde(rename_all = "snake_case")]
pub enum InternUrgency {
    Blocking,  // Pauses parent agent's stream until result is available
    Background, // Runs in parallel, result available for Round 2 context
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub enum InternTaskStatus {
    Pending,
    Running,
    Completed,
    Failed,
    Cancelled,
}

#[derive(Debug, Clone, Serialize, Deserialize)]
pub struct InternResult {
    pub task_id: String,
    pub success: bool,
    pub findings: String,
    pub sources: Vec<String>,
    pub confidence: f64,
    pub processing_time_ms: u64,
}

pub struct InternTierConfig {
    pub tier: InternTier,
    pub model: String,
    pub max_tokens: u32,
    pub timeout_seconds: u64,
    pub system_prompt_template: String,
}

impl InternSystem {
    pub fn new() -> Self {
        Self {
            tiers: Self::default_tiers(),
        }
    }

    fn default_tiers() -> HashMap<InternTier, InternTierConfig> {
        maplit::hashmap! {
            InternTier::ResearchIntern => InternTierConfig {
                tier: InternTier::ResearchIntern,
                model: "gemini-2.0-flash-exp".to_string(),
                max_tokens: 2048,
                timeout_seconds: 30,
                system_prompt_template: INTERN_RESEARCH_PROMPT.to_string(),
            },
            InternTier::DataIntern => InternTierConfig {
                tier: InternTier::DataIntern,
                model: "gemini-2.0-flash-exp".to_string(),
                max_tokens: 1024,
                timeout_seconds: 20,
                system_prompt_template: INTERN_DATA_PROMPT.to_string(),
            },
            InternTier::CreativeIntern => InternTierConfig {
                tier: InternTier::CreativeIntern,
                model: "gemini-2.0-flash-exp".to_string(),
                max_tokens: 512,
                timeout_seconds: 15,
                system_prompt_template: INTERN_CREATIVE_PROMPT.to_string(),
            },
            InternTier::TechIntern => InternTierConfig {
                tier: InternTier::TechIntern,
                model: "gemini-2.0-flash-exp".to_string(),
                max_tokens: 1024,
                timeout_seconds: 25,
                system_prompt_template: INTERN_TECH_PROMPT.to_string(),
            },
        }
    }
}
```

---

## 4B — Blocking vs Background Task Handling

```rust
// The Stream Coordinator detects <research_request> tags in streaming output
// For BLOCKING requests: pause stream, spawn intern inference, inject result, resume
// For BACKGROUND requests: spawn task, result available for Round 2

pub struct StreamCoordinator {
    intern_system: InternSystem,
    inference_client: GCPClient,
}

impl StreamCoordinator {
    pub async fn process_stream(
        &self,
        agent_id: Uuid,
        session_id: &str,
        mut stream: StreamingResponse,
    ) -> Result<String> {
        let mut full_response = String::new();
        let mut pending_blocking_task: Option<InternTask> = None;

        while let Some(token) = stream.next().await? {
            full_response.push_str(&token);

            // Check for <research_request> tag
            if let Some(tag) = self.detect_research_request(&full_response) {
                let task = self.parse_intern_task(tag, agent_id, session_id)?;

                match task.urgency {
                    InternUrgency::Blocking => {
                        // Pause stream processing
                        stream.stop().await?;

                        // Run intern task synchronously
                        let result = self.run_intern_task(task.clone()).await?;

                        // Inject result into context and restart
                        let augmented_context = self.inject_intern_result(
                            &full_response,
                            &task,
                            &result,
                        );

                        // Restart stream with augmented context
                        stream = self.inference_client.stream(
                            augmented_context
                        ).await?;

                        pending_blocking_task = Some(task);
                    }
                    InternUrgency::Background => {
                        // Spawn task asynchronously
                        let task_clone = task.clone();
                        tokio::spawn(async move {
                            let _ = self.run_intern_task(task_clone).await;
                        });
                    }
                }
            }
        }

        Ok(full_response)
    }

    fn detect_research_request(&self, text: &str) -> Option<String> {
        let start = text.find("<research_request>")?;
        let end = text.find("</research_request>")?;
        Some(text[start..end].to_string())
    }

    fn inject_intern_result(
        &self,
        original_text: &str,
        task: &InternTask,
        result: &InternResult,
    ) -> String {
        let injection = format!(
            "\n\n[RESEARCH RESULT from {}]:\n{}\n\nSources: {}\n\nContinue your response incorporating this research.\n",
            task.intern_tier.display_name(),
            result.findings,
            result.sources.join(", ")
        );

        // Remove the research request tag and inject result
        let cleaned = self.remove_research_tag(original_text);
        format!("{}{}", cleaned, injection)
    }

    fn remove_research_tag(&self, text: &str) -> String {
        let re = regex::Regex::new(r"<research_request>.*?</research_request>").unwrap();
        re.replace_all(text, "").to_string()
    }
}
```

---

## 4C — Intern Inference Prompt Template

```rust
pub const INTERN_RESEARCH_PROMPT: &str = r#"You are a research intern working under the supervision of an expert marketing AI agent.

YOUR TASK:
{query}

CONTEXT FROM YOUR SUPERVISOR:
{context}

RESEARCH GUIDELINES:
1. Be thorough but concise — your supervisor needs actionable findings, not a literature review
2. Cite your sources with specific URLs where possible
3. Distinguish between facts and interpretations
4. Flag any uncertainty or conflicting information
5. Prioritize information relevant to marketing and competitive positioning

OUTPUT FORMAT:
Your response should be structured as follows:

## Key Findings
(Bullet points of the most important discoveries)

## Supporting Details
(Paragraph explaining the findings in context)

## Sources
(List of URLs or sources consulted)

## Confidence Assessment
(Your confidence that these findings are accurate and relevant: high/medium/low)"#;

pub const INTERN_DATA_PROMPT: &str = r#"You are a data analysis intern working under the supervision of an expert marketing AI agent.

YOUR TASK:
{query}

DATA CONTEXT:
{data_summary}

ANALYSIS GUIDELINES:
1. Focus on actionable insights, not just describing numbers
2. Identify patterns and trends
3. Flag anomalies or unexpected results
4. Connect findings to marketing implications

OUTPUT FORMAT:
## Analysis
(Your interpretation of the data)

## Key Metrics
(Most important numbers and what they mean)

## Implications
(What this means for marketing strategy)"#;

pub const INTERN_CREATIVE_PROMPT: &str = r#"You are a creative intern working under the supervision of an expert marketing agent.

YOUR TASK:
{query}

BRAND CONTEXT:
{brand_voice}

CREATIVE GUIDELINES:
1. Generate 3-5 variations of the requested content
2. Each variation should take a distinct approach
3. Be bold — your supervisor wants options, not safe choices
4. Match the brand voice precisely

OUTPUT FORMAT:
## Variations
(List each variation with its approach labeled)"#;

pub const INTERN_TECH_PROMPT: &str = r#"You are a technical research intern working under the supervision of an expert marketing AI agent.

YOUR TASK:
{query}

PLATFORM CONTEXT:
{platform_context}

RESEARCH GUIDELINES:
1. Focus on platform-specific features and capabilities
2. Identify technical requirements and limitations
3. Note any recent platform changes or announcements
4. Assess implications for marketing implementation

OUTPUT FORMAT:
## Technical Findings
(Bullet points of technical discoveries)

## Platform Requirements
(What would be needed to implement)

## Relevant Updates
(Any recent platform changes)"#;
```

---

## 4D — Intern Dispatch from Council Avatar Prompts

```rust
// Every Council avatar position prompt includes these instructions:

pub const INTERN_DISPATCH_INSTRUCTION: &str = r#"RESEARCH REQUEST INSTRUCTIONS:
If you need research to support your position, include a <research_request> tag in your response:

<research_request>
{
  "query": "specific question that needs research",
  "type": "web_search|competitive|performance|creative|platform",
  "urgency": "blocking|background"
}
</research_request>

- BLOCKING: Your stream will pause while the research runs. Use sparingly — only for critical information that will significantly change your position.
- BACKGROUND: The research runs in parallel. Your position will be generated without the result, which will be available for Round 2.

Do NOT request research on:
- Information you already have in your context
- Questions that don't directly affect your position
- Research that would take longer than 30 seconds

Example blocking request:
<research_request>
{
  "query": "What was DigitalGrow's Meta ad spend increase last month according to their disclosed advertising data?",
  "type": "competitive",
  "urgency": "blocking"
}
</research_request>

Example background request:
<research_request>
{
  "query": "Latest engagement rate benchmarks for D2C apparel brands on Instagram",
  "type": "performance",
  "urgency": "background"
}
</research_request>"#;
```

### Example: Ogilvy's Position with Research Request

```
[Position text discussing competitor advertising strategy...]

<research_request>
{
  "query": "DigitalGrow's recent Meta advertising strategy changes - what messaging angles are they using in their current active ads?",
  "type": "competitive",
  "urgency": "blocking"
}
</research_request>

[Continues position text...]

<ripple_data>
{
  "core_claim": "...",
  ...
}
</ripple_data>
```

When the Stream Coordinator detects this tag:

1. Stream pauses at the tag
2. Intern runs the competitive research
3. Result is injected after the tag
4. Stream resumes with the research incorporated

---

## 4E — Intern Tier Matching

```rust
impl InternSystem {
    pub fn select_tier(task_type: &InternTaskType) -> InternTier {
        match task_type {
            InternTaskType::WebSearch => InternTier::ResearchIntern,
            InternTaskType::CompetitiveAnalysis => InternTier::ResearchIntern,
            InternTaskType::AudienceResearch => InternTier::ResearchIntern,
            InternTaskType::PerformanceAnalysis => InternTier::DataIntern,
            InternTaskType::ContentVariant => InternTier::CreativeIntern,
            InternTaskType::CopyTest => InternTier::CreativeIntern,
            InternTaskType::PlatformResearch => InternTier::TechIntern,
        }
    }

    pub async fn run_intern_task(&self, task: InternTask) -> Result<InternResult> {
        let config = self.tiers.get(&task.intern_tier)
            .context("Unknown intern tier")?;

        let start = std::time::Instant::now();

        let prompt = self.build_intern_prompt(&task, &config);

        let response = tokio::time::timeout(
            Duration::from_secs(config.timeout_seconds),
            self.inference_client.generate(&prompt, config.max_tokens)
        )
        .await
        .context("Intern task timed out")??;

        let result = self.parse_intern_response(&response)?;

        Ok(InternResult {
            task_id: task.task_id,
            success: true,
            findings: result,
            sources: vec![],
            confidence: 0.8,
            processing_time_ms: start.elapsed().as_millis() as u64,
        })
    }

    fn build_intern_prompt(&self, task: &InternTask, config: &InternTierConfig) -> String {
        let template = &config.system_prompt_template;

        template
            .replace("{query}", &task.query)
            .replace("{context}", &format!("Session: {}", task.parent_session_id))
            .replace("{brand_voice}", "")
            .replace("{platform_context}", "")
            .replace("{data_summary}", "")
    }
}
```

---

## 4F — Round 2 Context Injection for Background Tasks

```rust
impl StreamCoordinator {
    pub async fn build_round2_context(
        &self,
        session_id: &str,
        round1_positions: &[AgentPosition],
    ) -> Result<String> {
        let mut context = String::new();

        // Add Round 1 positions
        for pos in round1_positions {
            context.push_str(&format!("[{} Round 1]: {}\n\n", pos.agent_key, pos.position_text));

            // Check for background intern results
            if let Some(result) = self.get_background_results(pos.agent_id, session_id).await? {
                context.push_str(&format!(
                    "[Research for {} from intern]: {}\n\n",
                    pos.agent_key,
                    result.findings
                ));
            }
        }

        Ok(context)
    }

    async fn get_background_results(
        &self,
        agent_id: Uuid,
        session_id: &str,
    ) -> Result<Option<InternResult>> {
        // Query DragonflyDB for completed background tasks
        let key = format!("intern:background:{}:{}", session_id, agent_id);
        let result: Option<String> = self.redis.get(&key).await?;

        match result {
            Some(json) => Ok(serde_json::from_str(&json).ok()),
            None => Ok(None),
        }
    }
}
```

---

## Summary

This addendum provides:

1. **InternTask struct** — complete definition with all fields
2. **InternTier types** — Research, Data, Creative, Tech with configurations
3. **Blocking vs background handling** — Stream Coordinator logic
4. **Intern inference prompt templates** — for each tier
5. **Dispatch instructions** — embedded in avatar prompts
6. **Round 2 context injection** — how background results reach Round 2

These specifications complete the Intern System gap identified in RedTeam Audit Hole 4.
