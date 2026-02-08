# PHASE 2: THE SKILL COMPILER SYSTEM

---

## 2.1 Skill Card Format (Complete Specification)

Every skill is defined in a Markdown file with YAML frontmatter. This is the **source of truth** for agent behavior.

```markdown
---
# ===== METADATA =====
skill_id: "research.competitor.v1"
name: "Competitor Intelligence Agent"
description: "Deep competitive analysis with Indian market focus"
version: "1.0.0"
author: "Raptorflow"
category: "research"
tags: ["competitor", "analysis", "strategy", "indian-market"]

# ===== MODEL CONFIGURATION =====
model:
  primary: "gemini-2.0-flash"
  fallback: "gemini-2.0-pro"
  temperature: 0.7
  max_tokens: 4096
  top_p: 0.95

# ===== COST CONTROLS =====
limits:
  max_cost: 0.10           # USD - auto-kill if exceeded
  max_tokens: 50000        # Total tokens (input + output)
  timeout_seconds: 60      # Execution timeout
  max_tool_calls: 10       # Prevent infinite tool loops
  max_retries: 2           # Retry attempts on failure

# ===== TOOL ACCESS =====
tools:
  required:
    - "web_search"
    - "scraper"
  optional:
    - "database_writer"
    - "vision_analyzer"

# ===== INPUT SCHEMA =====
inputs:
  - name: "competitor_url"
    type: "string"
    required: true
    description: "URL of competitor website"
    validation:
      pattern: "^https?://.+"

  - name: "research_depth"
    type: "enum"
    required: false
    values: ["quick", "standard", "deep"]
    default: "standard"
    description: "How thorough the analysis should be"

  - name: "focus_areas"
    type: "array"
    required: false
    items: "string"
    default: ["pricing", "features", "positioning"]
    max_items: 5

# ===== OUTPUT SCHEMA =====
outputs:
  type: "object"
  required: ["company_name", "analysis", "recommendations"]
  properties:
    company_name:
      type: "string"
      description: "Name of the competitor"

    analysis:
      type: "object"
      properties:
        strengths:
          type: "array"
          items: "string"
          min_items: 1
          max_items: 10
        weaknesses:
          type: "array"
          items: "string"
        pricing:
          type: "object"
          properties:
            currency: "string"
            tiers: "array"

    recommendations:
      type: "array"
      items:
        type: "object"
        properties:
          action: "string"
          priority: "enum[high,medium,low]"
          rationale: "string"

# ===== EVALUATION CRITERIA =====
evaluation:
  min_quality_score: 70
  checks:
    - "output_matches_schema"
    - "no_hallucinated_urls"
    - "recommendations_are_actionable"
    - "pricing_in_correct_currency"

  retry_conditions:
    - "quality_score < 70"
    - "missing_required_fields"
    - "tool_call_failed"

# ===== DEPENDENCIES =====
dependencies:
  skills: []  # Other skills this can invoke
  data:
    - "foundation.business_description"
    - "foundation.icp_summaries"
    - "foundation.competitors"
---

# IDENTITY

You are an elite corporate intelligence analyst with 15 years of experience at top consulting firms (McKinsey, Bain, BCG). You specialize in competitive analysis for B2B SaaS companies, with deep expertise in the Indian market.

Your analysis is:
- **Data-driven**: Every claim backed by evidence
- **Actionable**: Recommendations can be executed immediately
- **Strategic**: Focuses on exploitable weaknesses
- **Culturally aware**: Understands Indian business dynamics

# CONTEXT INJECTION

## User's Business
{{ foundation.business_description }}

## Target Customers (ICPs)
{% for icp in foundation.icp_summaries %}
- **{{ icp.name }}**: {{ icp.summary }}
{% endfor %}

## Current Positioning
{{ foundation.positioning }}

## Known Competitors
{% for comp in foundation.competitors %}
- {{ comp.name }}: {{ comp.url }}
{% endfor %}

# MISSION

Analyze the provided competitor URL and generate comprehensive intelligence that will help **{{ foundation.company_name }}** win against this competitor in the Indian market.

Your analysis must answer:
1. What are they doing well that we should learn from?
2. Where are they weak that we can exploit?
3. How do they price, and can we undercut profitably?
4. What do their customers complain about?
5. What specific moves should we make this week?

# METHODOLOGY

Execute this analysis in phases:

## Phase 1: Surface Scan (Use `scraper` tool)
- Extract pricing page content
- Extract features/product page
- Extract about/team page
- Capture messaging and positioning

## Phase 2: Deep Dive (Use `web_search` tool)
- Search: "[competitor name] reviews"
- Search: "[competitor name] complaints"
- Search: "[competitor name] vs alternatives"
- Search: "[competitor name] pricing India"

## Phase 3: Gap Analysis
Compare findings against user's Foundation data:
- Feature gaps (they have, we don't)
- Pricing gaps (opportunity to undercut)
- Positioning gaps (unoccupied territory)

## Phase 4: Recommendations
Generate 3-5 specific, actionable moves prioritized by:
- Impact (high/medium/low)
- Effort (high/medium/low)
- Timeline (this week / this month / this quarter)

# RULES

1. **VERIFY EVERYTHING**: Cross-reference claims from multiple sources. If unverified, mark as `[UNVERIFIED]`.

2. **INDIAN CONTEXT**:
   - Convert all pricing to INR when possible
   - Note if competitor has India-specific features
   - Consider Indian business culture in recommendations

3. **BE SPECIFIC**:
   - ❌ "They have good pricing"
   - ✅ "Their starter plan is ₹2,999/mo vs our ₹3,999/mo, 25% cheaper"

4. **NO HALLUCINATION**: If you can't find information, say "Not found" rather than guessing.

5. **ACTIONABLE OUTPUT**: Every recommendation must be executable this week.

# TOOL USAGE

## web_search
Use for finding reviews, news, and public sentiment.
```
web_search(query="[competitor] customer complaints India", num_results=10)
```

## scraper
Use for extracting website content.
```
scraper(url="https://competitor.com/pricing", extract=["pricing_tiers", "features"])
```

## database_writer (optional)
Save findings for future reference.
```
database_writer(table="competitor_intel", data={...})
```

# OUTPUT FORMAT

Return a JSON object matching the output schema exactly. Example structure:

```json
{
  "company_name": "CompetitorCo",
  "analysis": {
    "strengths": ["Strong brand recognition", "Lower pricing"],
    "weaknesses": ["Poor customer support", "No Hindi support"],
    "pricing": {
      "currency": "INR",
      "tiers": [
        {"name": "Starter", "price": 2999, "features": ["..."]}
      ]
    }
  },
  "recommendations": [
    {
      "action": "Launch Hindi language support within 2 weeks",
      "priority": "high",
      "rationale": "Competitor has 500+ negative reviews mentioning lack of Hindi support"
    }
  ]
}
```

# SELF-CORRECTION

Before submitting your output:
1. Did I verify all factual claims?
2. Is pricing converted to INR?
3. Are recommendations specific and actionable?
4. Does output match the required schema?
5. Would a marketing executive find this useful TODAY?
```

---

## 2.2 Skill Compiler

```python
# backend/skills/compiler.py
from typing import Dict, Any, List, Optional, Type
from pydantic import BaseModel, create_model, Field
from pathlib import Path
import frontmatter
import yaml
import json
import hashlib
import logging
from datetime import datetime
from jinja2 import Template, Environment, BaseLoader

logger = logging.getLogger(__name__)


class SkillConfig(BaseModel):
    """Parsed skill configuration from YAML frontmatter."""
    skill_id: str
    name: str
    description: str
    version: str
    author: str
    category: str
    tags: List[str] = []

    # Model config
    model_primary: str
    model_fallback: Optional[str] = None
    temperature: float = 0.7
    max_tokens: int = 4096

    # Limits
    max_cost: float = 0.10
    max_total_tokens: int = 50000
    timeout_seconds: int = 60
    max_tool_calls: int = 10
    max_retries: int = 2

    # Tools
    required_tools: List[str] = []
    optional_tools: List[str] = []

    # Schemas
    input_schema: Dict[str, Any]
    output_schema: Dict[str, Any]

    # Evaluation
    min_quality_score: int = 70
    evaluation_checks: List[str] = []
    retry_conditions: List[str] = []

    # Dependencies
    skill_dependencies: List[str] = []
    data_dependencies: List[str] = []


class CompiledSkill(BaseModel):
    """A fully compiled, ready-to-execute skill."""
    config: SkillConfig
    system_prompt: str
    input_model: Any  # Pydantic model
    output_model: Any  # Pydantic model
    version_hash: str
    compiled_at: datetime
    source_path: str


class SkillCompiler:
    """
    Compiles Markdown skill definitions into executable skill objects.

    Features:
    - YAML frontmatter parsing
    - Pydantic model generation from schemas
    - Jinja2 template compilation
    - Version hashing for cache invalidation
    - Hot-reload support
    """

    def __init__(self, skills_dir: str = "backend/skills/definitions"):
        self.skills_dir = Path(skills_dir)
        self.jinja_env = Environment(loader=BaseLoader())
        self._compiled_cache: Dict[str, CompiledSkill] = {}

    def compile(self, skill_path: Path) -> CompiledSkill:
        """
        Compile a single skill file into an executable skill.
        """
        logger.info(f"Compiling skill: {skill_path}")

        # Read and parse markdown
        with open(skill_path, 'r', encoding='utf-8') as f:
            post = frontmatter.load(f)

        # Extract configuration
        config = self._parse_config(post.metadata)

        # Extract and compile system prompt
        system_prompt = post.content

        # Generate Pydantic models from schemas
        input_model = self._generate_pydantic_model(
            f"{config.skill_id}_Input",
            config.input_schema
        )
        output_model = self._generate_pydantic_model(
            f"{config.skill_id}_Output",
            config.output_schema
        )

        # Calculate version hash
        version_hash = self._calculate_hash(skill_path)

        compiled = CompiledSkill(
            config=config,
            system_prompt=system_prompt,
            input_model=input_model,
            output_model=output_model,
            version_hash=version_hash,
            compiled_at=datetime.utcnow(),
            source_path=str(skill_path)
        )

        # Cache it
        self._compiled_cache[config.skill_id] = compiled

        logger.info(f"Compiled skill: {config.skill_id} (hash: {version_hash[:8]})")
        return compiled

    def compile_all(self) -> Dict[str, CompiledSkill]:
        """
        Compile all skills in the skills directory.
        """
        compiled_skills = {}

        for md_file in self.skills_dir.rglob("*.md"):
            try:
                skill = self.compile(md_file)
                compiled_skills[skill.config.skill_id] = skill
            except Exception as e:
                logger.error(f"Failed to compile {md_file}: {e}")

        return compiled_skills

    def _parse_config(self, metadata: Dict[str, Any]) -> SkillConfig:
        """
        Parse YAML frontmatter into SkillConfig.
        """
        model_config = metadata.get("model", {})
        limits = metadata.get("limits", {})
        tools = metadata.get("tools", {})
        evaluation = metadata.get("evaluation", {})
        dependencies = metadata.get("dependencies", {})

        return SkillConfig(
            skill_id=metadata["skill_id"],
            name=metadata["name"],
            description=metadata["description"],
            version=metadata["version"],
            author=metadata.get("author", "Raptorflow"),
            category=metadata.get("category", "general"),
            tags=metadata.get("tags", []),

            model_primary=model_config.get("primary", "gemini-2.0-flash"),
            model_fallback=model_config.get("fallback"),
            temperature=model_config.get("temperature", 0.7),
            max_tokens=model_config.get("max_tokens", 4096),

            max_cost=limits.get("max_cost", 0.10),
            max_total_tokens=limits.get("max_tokens", 50000),
            timeout_seconds=limits.get("timeout_seconds", 60),
            max_tool_calls=limits.get("max_tool_calls", 10),
            max_retries=limits.get("max_retries", 2),

            required_tools=tools.get("required", []),
            optional_tools=tools.get("optional", []),

            input_schema=self._parse_inputs(metadata.get("inputs", [])),
            output_schema=metadata.get("outputs", {}),

            min_quality_score=evaluation.get("min_quality_score", 70),
            evaluation_checks=evaluation.get("checks", []),
            retry_conditions=evaluation.get("retry_conditions", []),

            skill_dependencies=dependencies.get("skills", []),
            data_dependencies=dependencies.get("data", [])
        )

    def _parse_inputs(self, inputs: List[Dict]) -> Dict[str, Any]:
        """
        Convert input list to JSON schema format.
        """
        properties = {}
        required = []

        for inp in inputs:
            name = inp["name"]
            prop = {"type": inp["type"]}

            if inp.get("description"):
                prop["description"] = inp["description"]
            if inp.get("default") is not None:
                prop["default"] = inp["default"]
            if inp.get("values"):
                prop["enum"] = inp["values"]
            if inp.get("validation"):
                prop.update(inp["validation"])

            properties[name] = prop

            if inp.get("required", False):
                required.append(name)

        return {
            "type": "object",
            "properties": properties,
            "required": required
        }

    def _generate_pydantic_model(
        self,
        model_name: str,
        schema: Dict[str, Any]
    ) -> Type[BaseModel]:
        """
        Dynamically generate a Pydantic model from JSON schema.
        """
        if schema.get("type") != "object":
            # Simple type, wrap in object
            return create_model(model_name, value=(Any, ...))

        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        fields = {}
        for prop_name, prop_schema in properties.items():
            python_type = self._json_type_to_python(prop_schema)

            if prop_name in required:
                fields[prop_name] = (python_type, ...)
            else:
                default = prop_schema.get("default")
                fields[prop_name] = (Optional[python_type], default)

        return create_model(model_name, **fields)

    def _json_type_to_python(self, schema: Dict[str, Any]) -> type:
        """
        Convert JSON schema type to Python type.
        """
        type_map = {
            "string": str,
            "integer": int,
            "number": float,
            "boolean": bool,
            "array": list,
            "object": dict,
        }

        json_type = schema.get("type", "string")

        if json_type == "enum":
            return str  # Handle as string with validation

        return type_map.get(json_type, Any)

    def _calculate_hash(self, file_path: Path) -> str:
        """
        Calculate content hash for cache invalidation.
        """
        with open(file_path, 'rb') as f:
            return hashlib.sha256(f.read()).hexdigest()

    def hydrate_prompt(
        self,
        skill: CompiledSkill,
        inputs: Dict[str, Any],
        foundation: Dict[str, Any]
    ) -> str:
        """
        Inject Foundation context and inputs into the skill template.
        """
        template = self.jinja_env.from_string(skill.system_prompt)

        return template.render(
            foundation=foundation,
            inputs=inputs,
            timestamp=datetime.utcnow().isoformat(),
            skill_version=skill.config.version
        )


# Singleton instance
skill_compiler = SkillCompiler()
```

---

## 2.3 Skill Registry with Hot-Reload

```python
# backend/skills/registry.py
from typing import Dict, List, Optional
from pathlib import Path
import asyncio
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging

from .compiler import SkillCompiler, CompiledSkill

logger = logging.getLogger(__name__)


class SkillFileHandler(FileSystemEventHandler):
    """
    Watches for changes to skill files and triggers recompilation.
    """

    def __init__(self, registry: 'SkillRegistry'):
        self.registry = registry

    def on_modified(self, event):
        if event.src_path.endswith('.md'):
            logger.info(f"Skill file modified: {event.src_path}")
            asyncio.create_task(self.registry.reload_skill(Path(event.src_path)))

    def on_created(self, event):
        if event.src_path.endswith('.md'):
            logger.info(f"New skill file: {event.src_path}")
            asyncio.create_task(self.registry.reload_skill(Path(event.src_path)))


class SkillRegistry:
    """
    Central registry for all compiled skills.

    Features:
    - Hot-reload: Skills update without restart
    - Semantic search: Find skills by description
    - Version management: Track skill versions
    - Dependency resolution: Load dependent skills
    """

    def __init__(self, skills_dir: str = "backend/skills/definitions"):
        self.skills_dir = Path(skills_dir)
        self.compiler = SkillCompiler(skills_dir)
        self.skills: Dict[str, CompiledSkill] = {}
        self._observer: Optional[Observer] = None
        self._embeddings: Dict[str, list] = {}  # For semantic search

    async def load_all_skills(self):
        """
        Load and compile all skills from the skills directory.
        """
        logger.info(f"Loading skills from {self.skills_dir}")

        self.skills = self.compiler.compile_all()

        # Build embeddings for semantic search
        await self._build_embeddings()

        logger.info(f"Loaded {len(self.skills)} skills")

    async def reload_skill(self, skill_path: Path):
        """
        Reload a single skill (for hot-reload).
        """
        try:
            skill = self.compiler.compile(skill_path)

            # Check if this is an update or new skill
            old_skill = self.skills.get(skill.config.skill_id)

            if old_skill:
                logger.info(
                    f"Updated skill: {skill.config.skill_id} "
                    f"(v{old_skill.config.version} -> v{skill.config.version})"
                )
            else:
                logger.info(f"New skill registered: {skill.config.skill_id}")

            self.skills[skill.config.skill_id] = skill

            # Update embeddings
            await self._update_embedding(skill)

        except Exception as e:
            logger.error(f"Failed to reload skill {skill_path}: {e}")

    def get_skill(self, skill_id: str) -> Optional[CompiledSkill]:
        """
        Get a compiled skill by ID.
        """
        return self.skills.get(skill_id)

    def get_skills_by_category(self, category: str) -> List[CompiledSkill]:
        """
        Get all skills in a category.
        """
        return [
            skill for skill in self.skills.values()
            if skill.config.category == category
        ]

    def get_skills_by_tag(self, tag: str) -> List[CompiledSkill]:
        """
        Get all skills with a specific tag.
        """
        return [
            skill for skill in self.skills.values()
            if tag in skill.config.tags
        ]

    def get_skill_summaries(self) -> List[Dict]:
        """
        Get summaries of all skills for the Queen Router.
        """
        return [
            {
                "skill_id": skill.config.skill_id,
                "name": skill.config.name,
                "description": skill.config.description,
                "category": skill.config.category,
                "tags": skill.config.tags,
                "required_tools": skill.config.required_tools,
                "estimated_cost": skill.config.max_cost
            }
            for skill in self.skills.values()
        ]

    async def search_skills(self, query: str, top_k: int = 5) -> List[CompiledSkill]:
        """
        Semantic search for skills matching a query.
        """
        from cognition.context_manager import embedder

        query_embedding = await embedder.embed(query)

        # Calculate similarities
        scores = []
        for skill_id, embedding in self._embeddings.items():
            similarity = self._cosine_similarity(query_embedding, embedding)
            scores.append((skill_id, similarity))

        # Sort by similarity
        scores.sort(key=lambda x: x[1], reverse=True)

        # Return top-k skills
        return [
            self.skills[skill_id]
            for skill_id, _ in scores[:top_k]
            if skill_id in self.skills
        ]

    def start_hot_reload(self):
        """
        Start watching for skill file changes.
        """
        if self._observer is not None:
            return

        handler = SkillFileHandler(self)
        self._observer = Observer()
        self._observer.schedule(handler, str(self.skills_dir), recursive=True)
        self._observer.start()

        logger.info("Skill hot-reload enabled")

    def stop_hot_reload(self):
        """
        Stop watching for skill file changes.
        """
        if self._observer:
            self._observer.stop()
            self._observer.join()
            self._observer = None

    async def _build_embeddings(self):
        """
        Build embeddings for all skills for semantic search.
        """
        from cognition.context_manager import embedder

        for skill_id, skill in self.skills.items():
            text = f"{skill.config.name} {skill.config.description} {' '.join(skill.config.tags)}"
            self._embeddings[skill_id] = await embedder.embed(text)

    async def _update_embedding(self, skill: CompiledSkill):
        """
        Update embedding for a single skill.
        """
        from cognition.context_manager import embedder

        text = f"{skill.config.name} {skill.config.description} {' '.join(skill.config.tags)}"
        self._embeddings[skill.config.skill_id] = await embedder.embed(text)

    def _cosine_similarity(self, a: list, b: list) -> float:
        import numpy as np
        a = np.array(a)
        b = np.array(b)
        return float(np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b)))


# Singleton instance
skill_registry = SkillRegistry()
```

---

## 2.4 TypeScript Type Generator

```python
# backend/skills/codegen.py
from typing import Dict, Any, List
from pathlib import Path
import json
import logging

from .registry import skill_registry
from .compiler import CompiledSkill

logger = logging.getLogger(__name__)


class TypeScriptGenerator:
    """
    Generates TypeScript interfaces from skill schemas.
    Ensures frontend and backend stay in sync.

    Run this as a pre-commit hook or build step.
    """

    def __init__(self, output_dir: str = "frontend/src/types/skills"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def generate_all(self):
        """
        Generate TypeScript types for all skills.
        """
        for skill_id, skill in skill_registry.skills.items():
            self.generate_skill_types(skill)

        # Generate index file
        self._generate_index()

        logger.info(f"Generated TypeScript types for {len(skill_registry.skills)} skills")

    def generate_skill_types(self, skill: CompiledSkill):
        """
        Generate TypeScript interfaces for a single skill.
        """
        skill_name = self._skill_id_to_name(skill.config.skill_id)

        # Generate input interface
        input_interface = self._schema_to_interface(
            f"{skill_name}Input",
            skill.config.input_schema
        )

        # Generate output interface
        output_interface = self._schema_to_interface(
            f"{skill_name}Output",
            skill.config.output_schema
        )

        # Generate skill metadata
        metadata = f"""
export const {skill_name}Metadata = {{
  skillId: "{skill.config.skill_id}",
  name: "{skill.config.name}",
  description: "{skill.config.description}",
  version: "{skill.config.version}",
  category: "{skill.config.category}",
  tags: {json.dumps(skill.config.tags)},
  estimatedCost: {skill.config.max_cost},
  timeoutSeconds: {skill.config.timeout_seconds},
}} as const;
"""

        # Write to file
        output_file = self.output_dir / f"{skill_name}.ts"
        with open(output_file, 'w') as f:
            f.write(f"// Auto-generated from {skill.config.skill_id}\n")
            f.write(f"// Do not edit manually\n\n")
            f.write(input_interface)
            f.write("\n\n")
            f.write(output_interface)
            f.write("\n\n")
            f.write(metadata)

        logger.debug(f"Generated types for {skill.config.skill_id}")

    def _schema_to_interface(self, name: str, schema: Dict[str, Any]) -> str:
        """
        Convert JSON schema to TypeScript interface.
        """
        if schema.get("type") != "object":
            return f"export type {name} = {self._json_type_to_ts(schema)};"

        properties = schema.get("properties", {})
        required = set(schema.get("required", []))

        lines = [f"export interface {name} {{"]

        for prop_name, prop_schema in properties.items():
            ts_type = self._json_type_to_ts(prop_schema)
            optional = "" if prop_name in required else "?"
            description = prop_schema.get("description", "")

            if description:
                lines.append(f"  /** {description} */")

            lines.append(f"  {prop_name}{optional}: {ts_type};")

        lines.append("}")

        return "\n".join(lines)

    def _json_type_to_ts(self, schema: Dict[str, Any]) -> str:
        """
        Convert JSON schema type to TypeScript type.
        """
        json_type = schema.get("type", "any")

        type_map = {
            "string": "string",
            "integer": "number",
            "number": "number",
            "boolean": "boolean",
            "null": "null",
        }

        if json_type in type_map:
            return type_map[json_type]

        if json_type == "array":
            items = schema.get("items", {})
            item_type = self._json_type_to_ts(items) if isinstance(items, dict) else "any"
            return f"{item_type}[]"

        if json_type == "object":
            # Inline object type
            properties = schema.get("properties", {})
            if not properties:
                return "Record<string, unknown>"

            props = []
            for prop_name, prop_schema in properties.items():
                ts_type = self._json_type_to_ts(prop_schema)
                props.append(f"{prop_name}: {ts_type}")

            return "{ " + "; ".join(props) + " }"

        if json_type == "enum" or "enum" in schema:
            values = schema.get("enum", schema.get("values", []))
            return " | ".join(f'"{v}"' for v in values)

        return "any"

    def _skill_id_to_name(self, skill_id: str) -> str:
        """
        Convert skill_id to PascalCase name.
        e.g., "research.competitor.v1" -> "ResearchCompetitorV1"
        """
        parts = skill_id.replace(".", "_").split("_")
        return "".join(part.capitalize() for part in parts)

    def _generate_index(self):
        """
        Generate index.ts exporting all skill types.
        """
        exports = []

        for skill_id in skill_registry.skills.keys():
            name = self._skill_id_to_name(skill_id)
            exports.append(f'export * from "./{name}";')

        index_file = self.output_dir / "index.ts"
        with open(index_file, 'w') as f:
            f.write("// Auto-generated skill type exports\n")
            f.write("// Do not edit manually\n\n")
            f.write("\n".join(sorted(exports)))


# CLI command
def generate_skill_types():
    """
    Generate TypeScript types from skills.
    Run: python -m backend.skills.codegen
    """
    generator = TypeScriptGenerator()
    generator.generate_all()
    print("TypeScript types generated successfully")


if __name__ == "__main__":
    generate_skill_types()
```

---

## 2.5 Initial 20 Skill Definitions

### Category: Research (5 skills)

| Skill ID | Name | Description | Model |
|----------|------|-------------|-------|
| `research.competitor.v1` | Competitor Intelligence | Deep competitive analysis | Flash |
| `research.market.v1` | Market Research | Market size and trends | Flash |
| `research.seo.v1` | SEO Analysis | Keyword research and opportunities | Flash |
| `research.news.v1` | News Monitor | Industry news aggregation | Flash-Lite |
| `research.social.v1` | Social Listening | Social media sentiment | Flash-Lite |

### Category: Content (5 skills)

| Skill ID | Name | Description | Model |
|----------|------|-------------|-------|
| `content.blog.v1` | Blog Writer | Long-form SEO content | Flash |
| `content.linkedin.v1` | LinkedIn Posts | Hook-driven professional posts | Flash |
| `content.email.v1` | Email Sequences | Multi-touch email campaigns | Flash |
| `content.twitter.v1` | Twitter Threads | Viral thread creation | Flash-Lite |
| `content.ad_copy.v1` | Ad Copywriter | Google/Meta ad copy | Flash |

### Category: Campaigns (5 skills)

| Skill ID | Name | Description | Model |
|----------|------|-------------|-------|
| `campaign.launch.v1` | Product Launch | Launch campaign planning | Pro |
| `campaign.diwali.v1` | Diwali Campaign | Festival marketing | Flash |
| `campaign.eofy.v1` | EOFY Campaign | End of Financial Year | Flash |
| `campaign.leadgen.v1` | Lead Generation | Lead gen campaign | Flash |
| `campaign.awareness.v1` | Brand Awareness | Awareness campaign | Flash |

### Category: Indian Market (5 skills)

| Skill ID | Name | Description | Model |
|----------|------|-------------|-------|
| `indian.justdial.v1` | JustDial Scraper | Local business leads | Flash-Lite |
| `indian.indiamart.v1` | IndiaMART Intel | B2B supplier data | Flash-Lite |
| `indian.linkedin_india.v1` | LinkedIn India | Indian professional targeting | Flash |
| `indian.gst_invoice.v1` | GST Invoice | GST-compliant invoicing | Flash-Lite |
| `indian.regional_content.v1` | Regional Content | Hindi/Tamil/Telugu | Flash |
