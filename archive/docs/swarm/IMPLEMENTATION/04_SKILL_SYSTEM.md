# SKILL SYSTEM

> Skill Cards, Registry, Execution, and Agent Integration

---

## 1. SKILL ARCHITECTURE

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           SKILL SYSTEM                                      │
│                                                                             │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SKILL REGISTRY                                   │   │
│  │                                                                     │   │
│  │  Loads skill cards → Indexes by category → Semantic search         │   │
│  │  Hot reload on changes → Version management                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SKILL MATCHER                                   │   │
│  │                                                                     │   │
│  │  Intent → Semantic matching → Skill selection → Parameter mapping  │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SKILL EXECUTOR                                  │   │
│  │                                                                     │   │
│  │  Load skill → Inject context → Execute prompt → Validate output   │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                    │                                        │
│                                    ▼                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                     SKILL STORAGE                                   │   │
│  │                                                                     │   │
│  │  skills/                                                            │   │
│  │  ├── onboarding/                                                   │   │
│  │  │   ├── fact_extraction.md                                        │   │
│  │  │   ├── market_research.md                                        │   │
│  │  │   └── icp_generation.md                                         │   │
│  │  ├── moves/                                                        │   │
│  │  │   ├── move_planning.md                                          │   │
│  │  │   └── task_breakdown.md                                         │   │
│  │  └── muse/                                                         │   │
│  │      ├── email_writing.md                                          │   │
│  │      └── social_post.md                                            │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 2. SKILL CARD FORMAT

**Location**: `backend/skills/{category}/{skill_name}.md`

```markdown
---
# SKILL METADATA (YAML frontmatter)
id: move_planning
name: Marketing Move Planner
version: "1.0.0"
category: moves
description: Creates detailed 7-day marketing execution plans

# MODEL CONFIGURATION
model:
  name: gemini-2.0-flash
  temperature: 0.7
  max_tokens: 8000

# COST LIMITS
cost:
  max_tokens_per_execution: 10000
  max_cost_per_execution: 0.02

# TOOL ACCESS
tools:
  - web_search
  - get_foundation
  - get_icps

# INPUT SCHEMA
input_schema:
  type: object
  required:
    - category
    - goal
  properties:
    category:
      type: string
      enum: [ignite, capture, authority, repair, rally]
      description: Type of move
    goal:
      type: string
      description: What the move should achieve
    duration_days:
      type: integer
      default: 7
    time_commitment:
      type: string
      enum: [minimal, standard, intensive]
      default: standard
    target_icp:
      type: string
      description: Which ICP to target

# OUTPUT SCHEMA
output_schema:
  type: object
  required:
    - name
    - execution
  properties:
    name:
      type: string
    category:
      type: string
    execution:
      type: array
      items:
        type: object
        properties:
          day: { type: integer }
          theme: { type: string }
          tasks: { type: array }

# EVALUATION CRITERIA
evaluation:
  required_fields:
    - name
    - execution
  min_tasks_per_day: 2
  max_tasks_per_day: 8

# SKILL DEPENDENCIES
dependencies:
  - get_foundation
  - get_icps
---

# Move Planning Skill

You are a senior marketing strategist creating detailed execution plans.

## Context

You have access to the user's business foundation and ICP profiles.

### Foundation
{{foundation_summary}}

### Target ICP
{{icp_details}}

### Brand Voice
{{brand_voice}}

## Instructions

Create a {{duration_days}}-day marketing move with these requirements:

### Move Category: {{category}}
- **ignite**: Rapid awareness, buzz generation
- **capture**: Lead generation, conversion
- **authority**: Thought leadership, credibility
- **repair**: Reputation management, trust rebuilding
- **rally**: Community building, engagement

### User Goal
{{goal}}

### Time Commitment: {{time_commitment}}
- minimal: 30 min/day
- standard: 1-2 hours/day
- intensive: 3+ hours/day

## Output Requirements

For each day, provide:
1. **Theme**: What's the focus for this day?
2. **Tasks**: Specific, actionable items
   - Pillar tasks (main content)
   - Story tasks (supporting content)
   - Engagement tasks (interaction)
   - Admin tasks (behind the scenes)

Each task must have:
- Clear deliverable
- Estimated time
- Platform/channel
- Priority (must-do, should-do, nice-to-have)

## Contingency Planning

Include what to do if the user:
- Misses a day
- Wants to compress the timeline
- Needs to pause mid-way

## Quality Standards

- Tasks must be specific, not vague
- Deliverables must be clear
- Time estimates must be realistic
- Build momentum across days
- End with a strong close
```

---

## 3. SKILL REGISTRY

```python
# backend/skills/registry.py
import os
import yaml
import hashlib
from pathlib import Path
from dataclasses import dataclass, field
from typing import Any
from sentence_transformers import SentenceTransformer
import numpy as np

@dataclass
class SkillCard:
    """Parsed skill card."""
    id: str
    name: str
    version: str
    category: str
    description: str

    # Model config
    model_name: str
    temperature: float
    max_tokens: int

    # Cost limits
    max_tokens_per_execution: int
    max_cost_per_execution: float

    # Tool access
    tools: list[str]

    # Schemas
    input_schema: dict
    output_schema: dict

    # Evaluation
    evaluation: dict

    # Dependencies
    dependencies: list[str]

    # The prompt template
    prompt_template: str

    # For semantic matching
    embedding: np.ndarray | None = None

    # File path
    file_path: str = ""
    file_hash: str = ""

class SkillRegistry:
    """Central registry for all skills."""

    def __init__(self, skills_dir: str = "backend/skills"):
        self.skills_dir = Path(skills_dir)
        self.skills: dict[str, SkillCard] = {}
        self.encoder = SentenceTransformer("all-MiniLM-L6-v2")
        self._load_all_skills()

    def _load_all_skills(self):
        """Load all skill cards from directory."""
        for md_file in self.skills_dir.rglob("*.md"):
            try:
                skill = self._parse_skill_file(md_file)
                self.skills[skill.id] = skill
            except Exception as e:
                print(f"Failed to load skill {md_file}: {e}")

    def _parse_skill_file(self, file_path: Path) -> SkillCard:
        """Parse a skill markdown file."""
        content = file_path.read_text(encoding="utf-8")

        # Split frontmatter and content
        parts = content.split("---", 2)
        if len(parts) < 3:
            raise ValueError(f"Invalid skill file format: {file_path}")

        frontmatter = yaml.safe_load(parts[1])
        prompt_template = parts[2].strip()

        # Compute file hash for change detection
        file_hash = hashlib.md5(content.encode()).hexdigest()

        # Create embedding for semantic matching
        embedding_text = f"{frontmatter['name']} {frontmatter['description']}"
        embedding = self.encoder.encode(embedding_text)

        return SkillCard(
            id=frontmatter["id"],
            name=frontmatter["name"],
            version=frontmatter["version"],
            category=frontmatter["category"],
            description=frontmatter["description"],
            model_name=frontmatter["model"]["name"],
            temperature=frontmatter["model"]["temperature"],
            max_tokens=frontmatter["model"]["max_tokens"],
            max_tokens_per_execution=frontmatter["cost"]["max_tokens_per_execution"],
            max_cost_per_execution=frontmatter["cost"]["max_cost_per_execution"],
            tools=frontmatter.get("tools", []),
            input_schema=frontmatter["input_schema"],
            output_schema=frontmatter["output_schema"],
            evaluation=frontmatter.get("evaluation", {}),
            dependencies=frontmatter.get("dependencies", []),
            prompt_template=prompt_template,
            embedding=embedding,
            file_path=str(file_path),
            file_hash=file_hash
        )

    def get_skill(self, skill_id: str) -> SkillCard | None:
        """Get skill by ID."""
        return self.skills.get(skill_id)

    def get_skills_by_category(self, category: str) -> list[SkillCard]:
        """Get all skills in a category."""
        return [s for s in self.skills.values() if s.category == category]

    def search_skills(
        self,
        query: str,
        category: str | None = None,
        limit: int = 5
    ) -> list[tuple[SkillCard, float]]:
        """Semantic search for skills."""
        query_embedding = self.encoder.encode(query)

        candidates = self.skills.values()
        if category:
            candidates = [s for s in candidates if s.category == category]

        scores = []
        for skill in candidates:
            if skill.embedding is not None:
                similarity = np.dot(query_embedding, skill.embedding) / (
                    np.linalg.norm(query_embedding) * np.linalg.norm(skill.embedding)
                )
                scores.append((skill, similarity))

        scores.sort(key=lambda x: x[1], reverse=True)
        return scores[:limit]

    def hot_reload(self):
        """Check for skill file changes and reload."""
        for skill in list(self.skills.values()):
            file_path = Path(skill.file_path)
            if not file_path.exists():
                # Skill file deleted
                del self.skills[skill.id]
                continue

            content = file_path.read_text()
            new_hash = hashlib.md5(content.encode()).hexdigest()

            if new_hash != skill.file_hash:
                # File changed, reload
                try:
                    new_skill = self._parse_skill_file(file_path)
                    self.skills[new_skill.id] = new_skill
                except Exception as e:
                    print(f"Failed to reload skill {file_path}: {e}")

        # Check for new files
        for md_file in self.skills_dir.rglob("*.md"):
            skill_ids = [s.file_path for s in self.skills.values()]
            if str(md_file) not in skill_ids:
                try:
                    skill = self._parse_skill_file(md_file)
                    self.skills[skill.id] = skill
                except Exception as e:
                    print(f"Failed to load new skill {md_file}: {e}")


# Singleton instance
_registry: SkillRegistry | None = None

def get_skill_registry() -> SkillRegistry:
    global _registry
    if _registry is None:
        _registry = SkillRegistry()
    return _registry
```

---

## 4. SKILL EXECUTOR

```python
# backend/skills/executor.py
from langchain_google_vertexai import ChatVertexAI
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, ValidationError
import json
from typing import Any

from .registry import SkillCard, get_skill_registry
from ..memory.controller import MemoryController

class SkillExecutionResult(BaseModel):
    """Result of skill execution."""
    skill_id: str
    success: bool
    output: Any | None = None
    error: str | None = None

    # Metrics
    tokens_input: int = 0
    tokens_output: int = 0
    total_cost: float = 0.0
    latency_ms: int = 0

    # Validation
    validation_passed: bool = True
    validation_errors: list[str] = []

class SkillExecutor:
    """Executes skill cards with context injection."""

    def __init__(self, memory_controller: MemoryController):
        self.registry = get_skill_registry()
        self.memory = memory_controller

    async def execute(
        self,
        skill_id: str,
        inputs: dict[str, Any],
        workspace_id: str,
        session_id: str
    ) -> SkillExecutionResult:
        """Execute a skill with inputs."""
        import time
        start = time.time()

        # Get skill
        skill = self.registry.get_skill(skill_id)
        if not skill:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                error=f"Skill {skill_id} not found"
            )

        # Validate inputs
        input_errors = self._validate_inputs(skill, inputs)
        if input_errors:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                error="Input validation failed",
                validation_passed=False,
                validation_errors=input_errors
            )

        try:
            # Load context
            context = await self._load_context(skill, workspace_id, session_id)

            # Build prompt
            prompt = self._build_prompt(skill, inputs, context)

            # Get LLM
            llm = ChatVertexAI(
                model_name=skill.model_name,
                temperature=skill.temperature,
                max_tokens=skill.max_tokens
            )

            # Execute
            response = await llm.ainvoke(prompt)

            # Parse output
            output = self._parse_output(response.content, skill.output_schema)

            # Validate output
            output_errors = self._validate_output(skill, output)

            latency = int((time.time() - start) * 1000)

            # Estimate tokens and cost
            tokens_in = len(prompt) // 4
            tokens_out = len(response.content) // 4
            cost = self._calculate_cost(skill.model_name, tokens_in, tokens_out)

            return SkillExecutionResult(
                skill_id=skill_id,
                success=len(output_errors) == 0,
                output=output,
                tokens_input=tokens_in,
                tokens_output=tokens_out,
                total_cost=cost,
                latency_ms=latency,
                validation_passed=len(output_errors) == 0,
                validation_errors=output_errors
            )

        except Exception as e:
            return SkillExecutionResult(
                skill_id=skill_id,
                success=False,
                error=str(e),
                latency_ms=int((time.time() - start) * 1000)
            )

    def _validate_inputs(self, skill: SkillCard, inputs: dict) -> list[str]:
        """Validate inputs against schema."""
        errors = []
        schema = skill.input_schema

        # Check required fields
        for field in schema.get("required", []):
            if field not in inputs:
                errors.append(f"Missing required field: {field}")

        # Check types and enums
        for field, props in schema.get("properties", {}).items():
            if field in inputs:
                value = inputs[field]

                # Type check
                expected_type = props.get("type")
                if expected_type == "string" and not isinstance(value, str):
                    errors.append(f"Field {field} must be string")
                elif expected_type == "integer" and not isinstance(value, int):
                    errors.append(f"Field {field} must be integer")
                elif expected_type == "array" and not isinstance(value, list):
                    errors.append(f"Field {field} must be array")

                # Enum check
                if "enum" in props and value not in props["enum"]:
                    errors.append(f"Field {field} must be one of: {props['enum']}")

        return errors

    async def _load_context(
        self,
        skill: SkillCard,
        workspace_id: str,
        session_id: str
    ) -> dict:
        """Load required context for skill."""
        context = {}

        if "get_foundation" in skill.dependencies:
            # Get foundation from memory
            from ..core.database import get_supabase_client
            supabase = get_supabase_client()

            foundation = supabase.table("foundations").select(
                "summary, brand_voice"
            ).eq("workspace_id", workspace_id).single().execute()

            if foundation.data:
                context["foundation_summary"] = foundation.data.get("summary", "")
                context["brand_voice"] = foundation.data.get("brand_voice", "professional")

        if "get_icps" in skill.dependencies:
            from ..core.database import get_supabase_client
            supabase = get_supabase_client()

            icps = supabase.table("icp_profiles").select("*").eq(
                "workspace_id", workspace_id
            ).eq("is_primary", True).execute()

            if icps.data and len(icps.data) > 0:
                icp = icps.data[0]
                context["icp_details"] = f"""
Name: {icp['name']}
Demographics: {icp.get('demographics', {})}
Psychographics: {icp.get('psychographics', {})}
Behaviors: {icp.get('behaviors', {})}
"""
            else:
                context["icp_details"] = "No ICP defined"

        return context

    def _build_prompt(
        self,
        skill: SkillCard,
        inputs: dict,
        context: dict
    ) -> str:
        """Build final prompt from template."""
        prompt = skill.prompt_template

        # Replace context variables
        for key, value in context.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        # Replace input variables
        for key, value in inputs.items():
            prompt = prompt.replace(f"{{{{{key}}}}}", str(value))

        # Set defaults for missing variables
        schema = skill.input_schema
        for field, props in schema.get("properties", {}).items():
            placeholder = f"{{{{{field}}}}}"
            if placeholder in prompt:
                default = props.get("default", "")
                prompt = prompt.replace(placeholder, str(default))

        return prompt

    def _parse_output(self, raw_output: str, schema: dict) -> Any:
        """Parse LLM output according to schema."""
        # Try to extract JSON if present
        if "```json" in raw_output:
            json_start = raw_output.find("```json") + 7
            json_end = raw_output.find("```", json_start)
            json_str = raw_output[json_start:json_end].strip()
            return json.loads(json_str)

        # Try direct JSON parse
        try:
            return json.loads(raw_output)
        except:
            pass

        # Return as-is if can't parse
        return {"raw_output": raw_output}

    def _validate_output(self, skill: SkillCard, output: Any) -> list[str]:
        """Validate output against skill's evaluation criteria."""
        errors = []
        evaluation = skill.evaluation

        if not isinstance(output, dict):
            return errors

        # Check required fields
        for field in evaluation.get("required_fields", []):
            if field not in output:
                errors.append(f"Missing required output field: {field}")

        # Check min/max constraints
        if "execution" in output and isinstance(output["execution"], list):
            for day in output["execution"]:
                tasks = day.get("tasks", [])
                min_tasks = evaluation.get("min_tasks_per_day", 0)
                max_tasks = evaluation.get("max_tasks_per_day", 100)

                if len(tasks) < min_tasks:
                    errors.append(f"Day {day.get('day')} has fewer than {min_tasks} tasks")
                if len(tasks) > max_tasks:
                    errors.append(f"Day {day.get('day')} has more than {max_tasks} tasks")

        return errors

    def _calculate_cost(
        self,
        model_name: str,
        tokens_in: int,
        tokens_out: int
    ) -> float:
        """Calculate cost based on model and tokens."""
        PRICING = {
            "gemini-2.0-flash-lite": {"input": 0.000075, "output": 0.0003},
            "gemini-2.0-flash": {"input": 0.00015, "output": 0.0006},
            "gemini-2.0-pro": {"input": 0.00125, "output": 0.005}
        }

        prices = PRICING.get(model_name, PRICING["gemini-2.0-flash"])
        return (tokens_in * prices["input"] + tokens_out * prices["output"]) / 1000
```

---

## 5. HOW AGENTS USE SKILLS

```python
# backend/agents/base.py
from ..skills.executor import SkillExecutor, SkillExecutionResult
from ..skills.registry import get_skill_registry

class BaseAgent:
    """Base class for all agents."""

    def __init__(self, skill_executor: SkillExecutor):
        self.skill_executor = skill_executor
        self.registry = get_skill_registry()

    async def execute_skill(
        self,
        skill_id: str,
        inputs: dict,
        workspace_id: str,
        session_id: str
    ) -> SkillExecutionResult:
        """Execute a skill and return result."""
        return await self.skill_executor.execute(
            skill_id=skill_id,
            inputs=inputs,
            workspace_id=workspace_id,
            session_id=session_id
        )

    async def find_best_skill(
        self,
        intent: str,
        category: str | None = None
    ) -> str | None:
        """Find the best skill for an intent."""
        results = self.registry.search_skills(intent, category, limit=1)
        if results:
            return results[0][0].id
        return None


# Example: Moves Agent using skills
class MovesAgent(BaseAgent):
    """Agent for creating marketing moves."""

    async def create_move(
        self,
        workspace_id: str,
        session_id: str,
        category: str,
        goal: str,
        duration_days: int = 7,
        time_commitment: str = "standard",
        target_icp: str | None = None
    ) -> dict:
        """Create a new move using the move_planning skill."""

        result = await self.execute_skill(
            skill_id="move_planning",
            inputs={
                "category": category,
                "goal": goal,
                "duration_days": duration_days,
                "time_commitment": time_commitment,
                "target_icp": target_icp or "primary"
            },
            workspace_id=workspace_id,
            session_id=session_id
        )

        if not result.success:
            raise Exception(f"Move creation failed: {result.error}")

        return result.output


# Example: Muse Agent with multiple skills
class MuseAgent(BaseAgent):
    """Agent for creative content generation."""

    CONTENT_TYPE_SKILLS = {
        "email": "email_writing",
        "social": "social_post",
        "blog": "blog_writing",
        "ad": "ad_copy",
        "script": "video_script"
    }

    async def generate_content(
        self,
        workspace_id: str,
        session_id: str,
        content_type: str,
        **kwargs
    ) -> dict:
        """Generate content using appropriate skill."""

        skill_id = self.CONTENT_TYPE_SKILLS.get(content_type)
        if not skill_id:
            # Find skill semantically
            skill_id = await self.find_best_skill(
                f"generate {content_type} content",
                category="muse"
            )

        if not skill_id:
            raise ValueError(f"No skill found for content type: {content_type}")

        result = await self.execute_skill(
            skill_id=skill_id,
            inputs=kwargs,
            workspace_id=workspace_id,
            session_id=session_id
        )

        return result.output if result.success else {"error": result.error}
```

---

## 6. SKILL LIBRARY

### Categories and Skills

| Category | Skill ID | Description |
|----------|----------|-------------|
| **onboarding** | `fact_extraction` | Extract facts from documents |
| | `market_research` | Conduct market research |
| | `competitor_analysis` | Analyze competitors |
| | `icp_generation` | Generate ICP profiles |
| | `positioning_creation` | Create positioning statements |
| | `soundbite_generation` | Generate soundbites/taglines |
| **moves** | `move_planning` | Create move execution plans |
| | `task_breakdown` | Break tasks into steps |
| | `contingency_planning` | Plan for missed days |
| **campaigns** | `campaign_strategy` | High-level campaign strategy |
| | `phase_planning` | Break campaign into phases |
| | `resource_allocation` | Allocate resources |
| **muse** | `email_writing` | Write emails |
| | `social_post` | Create social posts |
| | `blog_writing` | Write blog content |
| | `ad_copy` | Write ad copy |
| | `video_script` | Write video scripts |
| | `carousel_content` | Create carousel slides |
| **blackbox** | `risk_assessment` | Assess strategy risk |
| | `trend_analysis` | Analyze market trends |
| | `virality_prediction` | Predict viral potential |
| | `strategy_synthesis` | Create strategic plays |
| **daily_wins** | `trend_scanning` | Scan for trends |
| | `content_matching` | Match trends to business |
| | `quick_generation` | Quick content generation |

---

## 7. CREATING NEW SKILLS

### Template

```markdown
---
id: new_skill_id
name: Human Readable Name
version: "1.0.0"
category: category_name
description: Brief description of what this skill does

model:
  name: gemini-2.0-flash
  temperature: 0.7
  max_tokens: 4000

cost:
  max_tokens_per_execution: 5000
  max_cost_per_execution: 0.01

tools: []

input_schema:
  type: object
  required:
    - required_field
  properties:
    required_field:
      type: string
      description: Description
    optional_field:
      type: string
      default: "default value"

output_schema:
  type: object
  properties:
    output_field:
      type: string

evaluation:
  required_fields:
    - output_field

dependencies:
  - get_foundation
---

# Skill Title

Your system prompt here.

## Context
{{foundation_summary}}

## Instructions
Based on {{required_field}}, generate output.

## Output Format
Return JSON with output_field.
```
