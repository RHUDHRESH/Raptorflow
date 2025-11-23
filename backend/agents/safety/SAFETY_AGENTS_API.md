# Safety Agents API Documentation

This document provides comprehensive guidance on using the enhanced **CriticAgent** and **GuardianAgent** for content quality evaluation and safety enforcement.

## Table of Contents

1. [CriticAgent API](#criticagent-api)
2. [GuardianAgent API](#guardianagent-api)
3. [Integration Examples](#integration-examples)
4. [Database Schema Requirements](#database-schema-requirements)
5. [Best Practices](#best-practices)

---

## CriticAgent API

The **CriticAgent** provides multi-dimensional content quality evaluation with AI-powered critique and memory-based learning.

### Main Method: `critique_content()`

This is the primary API for content evaluation.

#### Signature

```python
async def critique_content(
    self,
    content: str,
    content_type: str,
    target_icp: Optional[Dict] = None,
    brand_voice: Optional[Dict] = None,
    workspace_id: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | `str` | Yes | The text content to critique |
| `content_type` | `str` | Yes | Type of content: `"blog"`, `"email"`, `"social_post"`, `"landing_page"`, `"ad"`, etc. |
| `target_icp` | `Dict` | No | Target audience profile for relevance checking |
| `brand_voice` | `Dict` | No | Brand voice guidelines and requirements |
| `workspace_id` | `str` | No | Workspace ID for memory storage and retrieval |
| `correlation_id` | `str` | No | Request correlation ID for distributed tracing |

#### Return Value

Returns a detailed critique dictionary:

```python
{
    "overall_score": 82.5,  # float (0-100)
    "dimensions": {
        "clarity": {
            "score": 8.5,  # float (0-10)
            "issues": ["Long sentences in paragraph 2", "Technical jargon not explained"],
            "suggestions": ["Break up complex sentences", "Add definitions for technical terms"]
        },
        "brand_alignment": {
            "score": 9.0,
            "issues": [],
            "suggestions": ["Consider using brand tagline in conclusion"]
        },
        "audience_fit": {...},
        "engagement": {...},
        "factual_accuracy": {...},
        "seo_optimization": {...},
        "readability": {
            "score": 7.5,
            "flesch_reading_ease": 65.3,
            "grade_level": "High School (9-12th grade)",
            "issues": ["Some paragraphs are too long"],
            "suggestions": ["Use shorter sentences for better readability"]
        },
        "grammar": {...},
        "value": {...}
    },
    "approval_recommendation": "approve_with_revisions",  # "approve", "approve_with_revisions", "reject"
    "priority_fixes": [
        "Fix grammar errors in paragraph 3",
        "Add SEO meta description",
        "Include statistics to support claims"
    ],
    "optional_improvements": [
        "Add more compelling examples",
        "Consider using bullet points",
        "Include call-to-action"
    ],
    "critique_metadata": {
        "content_type": "blog",
        "models_used": ["gemini-reasoning", "claude-creative"],
        "similar_critiques": 5,
        "timestamp": "2025-11-22T10:30:00Z",
        "correlation_id": "abc-123"
    }
}
```

#### Usage Example

```python
from backend.agents.safety.critic_agent import critic_agent

# Critique a blog post
critique = await critic_agent.critique_content(
    content="""
    Your blog post content here...
    Lorem ipsum dolor sit amet, consectetur adipiscing elit.
    """,
    content_type="blog",
    target_icp={
        "industry": "SaaS",
        "role": "Marketing Manager",
        "company_size": "50-200 employees"
    },
    brand_voice={
        "tone": "professional",
        "style": "conversational",
        "avoid": ["jargon", "overly technical language"]
    },
    workspace_id="workspace_123"
)

# Make decisions based on the critique
if critique["approval_recommendation"] == "approve":
    print("Content approved! Ready to publish.")
    publish_content(content)

elif critique["approval_recommendation"] == "approve_with_revisions":
    print(f"Score: {critique['overall_score']}/100")
    print("Priority fixes needed:")
    for fix in critique["priority_fixes"]:
        print(f"  - {fix}")

    # Apply fixes
    revised_content = apply_fixes(content, critique["priority_fixes"])

else:  # reject
    print("Content rejected. Major revisions needed.")
    print("Issues found:")
    for dimension, details in critique["dimensions"].items():
        if details["score"] < 6.0:
            print(f"  {dimension}: {details['score']}/10")
            for issue in details["issues"]:
                print(f"    - {issue}")
```

### Evaluation Dimensions

The CriticAgent evaluates content across **9 key dimensions**:

1. **Clarity** (weight: 1.2)
   - Logical flow
   - Jargon usage
   - Sentence complexity

2. **Brand Alignment** (weight: 1.5)
   - Tone consistency
   - Messaging alignment
   - Visual style

3. **Audience Fit** (weight: 1.3)
   - Relevance to target audience
   - Pain point addressing
   - Language appropriateness

4. **Engagement** (weight: 1.2)
   - Hook strength
   - Storytelling quality
   - Emotional resonance

5. **Factual Accuracy** (weight: 1.4)
   - Claim verification
   - Source credibility
   - Statistical validity

6. **SEO Optimization** (weight: 1.0)
   - Keyword usage
   - Meta data
   - Header structure
   - Internal links

7. **Readability** (weight: 1.1)
   - Flesch Reading Ease score
   - Grade level (Flesch-Kincaid)
   - Paragraph structure

8. **Grammar** (weight: 1.0)
   - Spelling
   - Grammar
   - Punctuation
   - Consistency

9. **Value** (weight: 1.3)
   - Actionability
   - Insights provided
   - Practical application

### Legacy Method: `review_content()`

For backward compatibility with existing code.

```python
async def review_content(
    content: str,
    content_type: str,
    target_icp: Optional[Dict] = None,
    brand_voice: Optional[Dict] = None,
    correlation_id: str = None
) -> Dict[str, Any]
```

**Note:** New code should use `critique_content()` instead. This method converts the new format to the legacy format.

---

## GuardianAgent API

The **GuardianAgent** provides comprehensive safety and compliance enforcement with multi-layered checks.

### Main Method: `guard_content()`

This is the primary API for content safety validation.

#### Signature

```python
async def guard_content(
    self,
    content: str,
    content_type: str,
    workspace_config: Optional[Dict] = None,
    industry: Optional[str] = None,
    target_region: Optional[str] = None,
    correlation_id: Optional[str] = None
) -> Dict[str, Any]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `content` | `str` | Yes | The text content to validate |
| `content_type` | `str` | Yes | Type of content: `"ad"`, `"blog"`, `"email"`, `"social_post"`, etc. |
| `workspace_config` | `Dict` | No | Workspace-specific safety configuration (see below) |
| `industry` | `str` | No | Industry type: `"healthcare"`, `"finance"`, `"legal"`, etc. |
| `target_region` | `str` | No | Target region: `"US"`, `"EU"`, `"CA"`, etc. for compliance checks |
| `correlation_id` | `str` | No | Request correlation ID for tracking |

#### Workspace Configuration

```python
workspace_config = {
    "prohibited_terms": ["competitor_name", "blacklisted_word"],
    "competitor_names": ["CompetitorCo", "RivalBrand"],
    "required_disclosures": ["#ad", "#sponsored"],
    "brand_guidelines": {
        "tone": "professional",
        "avoid_topics": ["politics", "religion"]
    }
}
```

#### Return Value

Returns a detailed safety assessment:

```python
{
    "safety_status": "flagged",  # "approved", "flagged", or "blocked"
    "confidence": 0.85,  # float (0-1)
    "checks": {
        "security": {
            "passed": True,
            "violations": []
        },
        "legal_compliance": {
            "passed": False,
            "violations": [
                {
                    "type": "medical_claim",
                    "severity": "high",
                    "description": "Unverified medical claim detected: 'cure'",
                    "guidance": "Remove claim or add disclaimer: 'Consult a healthcare professional before making medical decisions'"
                }
            ]
        },
        "copyright": {"passed": True, "violations": []},
        "brand_safety": {"passed": True, "violations": []},
        "competitor_policy": {"passed": True, "violations": []},
        "inclusive_language": {
            "passed": False,
            "violations": [
                {
                    "type": "non_inclusive_language",
                    "severity": "low",
                    "description": "Non-inclusive language: 'guys'",
                    "guidance": "Consider using 'everyone/folks/team' instead",
                    "position": 145
                }
            ]
        },
        "data_privacy": {"passed": True, "violations": []},
        "industry_regulations": {"passed": True, "violations": []}
    },
    "required_actions": [
        "Remove claim or add disclaimer: 'Consult a healthcare professional before making medical decisions'"
    ],
    "recommended_actions": [
        "Consider using 'everyone/folks/team' instead"
    ],
    "metadata": {
        "content_type": "blog",
        "checks_performed": 8,
        "total_violations": 2,
        "critical_violations": 0,
        "high_violations": 1,
        "timestamp": "2025-11-22T10:30:00Z",
        "correlation_id": "xyz-789"
    }
}
```

#### Usage Example

```python
from backend.agents.safety.guardian_agent import guardian_agent

# Validate healthcare marketing content
result = await guardian_agent.guard_content(
    content="""
    Our revolutionary supplement can help treat chronic pain.
    Join thousands of satisfied customers who have seen results!
    Limited time offer - act now!
    """,
    content_type="advertisement",
    workspace_config={
        "prohibited_terms": ["scam", "fake"],
        "competitor_names": ["CompetitorBrand"]
    },
    industry="healthcare",
    target_region="US"
)

# Make decisions based on safety status
if result["safety_status"] == "approved":
    print("Content is safe to publish!")
    publish_content()

elif result["safety_status"] == "flagged":
    print("⚠️ Content has warnings. Review recommended.")
    print(f"Confidence: {result['confidence']}")

    print("\nRequired actions:")
    for action in result["required_actions"]:
        print(f"  ❗ {action}")

    print("\nRecommended improvements:")
    for action in result["recommended_actions"]:
        print(f"  💡 {action}")

    # Proceed with caution or fix issues

else:  # blocked
    print("🚫 Content BLOCKED due to critical violations!")
    print("\nCritical issues that MUST be fixed:")
    for action in result["required_actions"]:
        print(f"  🛑 {action}")

    # Must fix before proceeding
```

### Safety Checks Performed

The GuardianAgent performs **8 comprehensive safety checks**:

1. **Security**
   - Prompt injection attempts
   - Unauthorized API calls
   - System command injection

2. **Legal Compliance**
   - Unverified medical claims
   - Unverified financial advice
   - Advertising regulation violations (FTC)
   - Required disclosure checks

3. **Copyright**
   - Copyright symbol detection
   - Potential plagiarism indicators
   - *(Production: integrate with Copyscape/Grammarly APIs)*

4. **Brand Safety**
   - Prohibited terms
   - Controversial topics
   - Hate speech detection

5. **Competitor Policy**
   - Competitor name mentions
   - Comparison fairness checks

6. **Inclusive Language**
   - Non-inclusive terminology
   - Discriminatory language
   - Suggested alternatives

7. **Data Privacy**
   - PII detection (SSN, credit cards, emails)
   - GDPR compliance (EU)
   - CCPA compliance (California)

8. **Industry Regulations**
   - Healthcare: HIPAA
   - Finance: SOX, PCI-DSS
   - Legal: Attorney-client privilege

### Action Validation Method: `validate_action()`

Validates agent actions before execution with role-based permissions.

#### Signature

```python
def validate_action(
    self,
    action: str,
    context: Dict[str, Any],
    user_role: Optional[str] = None
) -> Dict[str, Any]
```

#### Parameters

| Parameter | Type | Required | Description |
|-----------|------|----------|-------------|
| `action` | `str` | Yes | Action type (e.g., `"publish_post"`, `"delete_campaign"`) |
| `context` | `Dict` | Yes | Action context including parameters |
| `user_role` | `str` | No | User's role: `"admin"`, `"editor"`, `"viewer"` |

#### Usage Example

```python
# Validate a publish action
validation = guardian_agent.validate_action(
    action="publish_post",
    context={
        "post_id": "post_123",
        "user_confirmed": True
    },
    user_role="editor"
)

if validation["is_allowed"]:
    proceed_with_action()
else:
    print("Action blocked:")
    for violation in validation["violations"]:
        print(f"  - {violation['description']}")
```

#### Permission Matrix

| Action | Required Roles | Requires Confirmation |
|--------|---------------|----------------------|
| `fetch_analytics` | admin, editor, viewer | No |
| `generate_content` | admin, editor | No |
| `publish_post` | admin, editor | **Yes** |
| `delete_campaign` | admin only | **Yes** |
| `change_permissions` | admin only | **Yes** |

---

## Integration Examples

### Example 1: Content Publishing Pipeline

```python
from backend.agents.safety.critic_agent import critic_agent
from backend.agents.safety.guardian_agent import guardian_agent

async def publish_pipeline(content, content_type, workspace_id):
    """Complete content validation and critique pipeline."""

    # Step 1: Safety validation (blocking)
    print("Step 1: Safety validation...")
    safety = await guardian_agent.guard_content(
        content=content,
        content_type=content_type,
        workspace_config=get_workspace_config(workspace_id),
        industry="technology",
        target_region="US"
    )

    if safety["safety_status"] == "blocked":
        return {
            "status": "rejected",
            "reason": "safety_violation",
            "details": safety["required_actions"]
        }

    # Step 2: Quality critique (advisory)
    print("Step 2: Quality critique...")
    critique = await critic_agent.critique_content(
        content=content,
        content_type=content_type,
        workspace_id=workspace_id
    )

    # Step 3: Decision making
    if critique["overall_score"] >= 85 and safety["safety_status"] == "approved":
        return {
            "status": "approved",
            "score": critique["overall_score"],
            "safety": safety["safety_status"]
        }

    elif critique["overall_score"] >= 70:
        return {
            "status": "needs_revision",
            "score": critique["overall_score"],
            "priority_fixes": critique["priority_fixes"],
            "safety_warnings": safety.get("recommended_actions", [])
        }

    else:
        return {
            "status": "rejected",
            "reason": "quality_issues",
            "score": critique["overall_score"],
            "details": critique["priority_fixes"]
        }

# Usage
result = await publish_pipeline(
    content="Your marketing copy...",
    content_type="blog",
    workspace_id="workspace_123"
)

if result["status"] == "approved":
    publish_content()
elif result["status"] == "needs_revision":
    request_revisions(result["priority_fixes"])
else:
    reject_content(result["reason"])
```

### Example 2: Iterative Content Improvement

```python
async def improve_until_approved(content, content_type, max_iterations=3):
    """Iteratively improve content until it passes all checks."""

    for iteration in range(max_iterations):
        print(f"\nIteration {iteration + 1}/{max_iterations}")

        # Critique current version
        critique = await critic_agent.critique_content(
            content=content,
            content_type=content_type
        )

        # Safety check
        safety = await guardian_agent.guard_content(
            content=content,
            content_type=content_type
        )

        # Check if approved
        if (critique["approval_recommendation"] == "approve" and
            safety["safety_status"] == "approved"):
            print(f"✅ Content approved! Score: {critique['overall_score']}/100")
            return {"status": "success", "content": content, "iterations": iteration + 1}

        # Generate improved version
        if iteration < max_iterations - 1:
            print("Applying improvements...")
            content = await generate_improved_version(
                content,
                critique["priority_fixes"],
                safety.get("required_actions", [])
            )

    return {"status": "failed", "reason": "max_iterations_reached"}
```

---

## Database Schema Requirements

To enable memory functionality in CriticAgent, create the following table:

```sql
CREATE TABLE content_critiques (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    workspace_id UUID NOT NULL,
    content_type VARCHAR(50) NOT NULL,
    content_hash VARCHAR(255),
    overall_score FLOAT,
    approval_recommendation VARCHAR(50),
    common_issues TEXT[],
    dimension_scores JSONB,
    created_at TIMESTAMP DEFAULT NOW(),

    INDEX idx_workspace_content_type (workspace_id, content_type),
    INDEX idx_created_at (created_at DESC)
);
```

---

## Best Practices

### 1. Always Run Safety Checks First

Safety checks should be **blocking** - don't proceed if content is blocked.

```python
# ✅ Good
safety = await guardian_agent.guard_content(...)
if safety["safety_status"] == "blocked":
    return error_response()

critique = await critic_agent.critique_content(...)

# ❌ Bad - don't skip safety checks
critique = await critic_agent.critique_content(...)
publish(content)  # Dangerous!
```

### 2. Use Workspace IDs for Memory

Always pass `workspace_id` to enable learning from past critiques:

```python
# ✅ Good - enables memory
critique = await critic_agent.critique_content(
    content=content,
    content_type="blog",
    workspace_id=workspace_id  # Enables memory
)

# ❌ Less effective - no memory
critique = await critic_agent.critique_content(
    content=content,
    content_type="blog"
)
```

### 3. Handle All Three Safety Statuses

```python
if safety["safety_status"] == "approved":
    # Proceed normally
    pass
elif safety["safety_status"] == "flagged":
    # Log warnings, proceed with caution
    log_warnings(safety["recommended_actions"])
    proceed_with_review()
else:  # blocked
    # Must fix violations before proceeding
    return fix_required(safety["required_actions"])
```

### 4. Provide Context for Better Results

More context leads to better evaluation:

```python
# ✅ Better - rich context
critique = await critic_agent.critique_content(
    content=content,
    content_type="blog",
    target_icp={"industry": "SaaS", "role": "VP Marketing"},
    brand_voice={"tone": "professional", "style": "conversational"},
    workspace_id=workspace_id
)

# ❌ Basic - minimal context
critique = await critic_agent.critique_content(
    content=content,
    content_type="blog"
)
```

### 5. Log Correlation IDs for Debugging

```python
from backend.utils.correlation import get_correlation_id

correlation_id = get_correlation_id()

critique = await critic_agent.critique_content(
    content=content,
    content_type="blog",
    correlation_id=correlation_id
)

safety = await guardian_agent.guard_content(
    content=content,
    content_type="blog",
    correlation_id=correlation_id
)

# All related logs will share the same correlation_id
```

### 6. Industry and Region-Specific Checks

Always specify industry and region for compliance:

```python
# Healthcare content in EU
safety = await guardian_agent.guard_content(
    content=healthcare_content,
    content_type="blog",
    industry="healthcare",  # Enables HIPAA checks
    target_region="EU"      # Enables GDPR checks
)

# Financial content in California
safety = await guardian_agent.guard_content(
    content=financial_content,
    content_type="email",
    industry="finance",     # Enables SOX, PCI-DSS checks
    target_region="CA"      # Enables CCPA checks
)
```

---

## Error Handling

Both agents provide fallback responses on errors:

```python
try:
    critique = await critic_agent.critique_content(...)

    if "error" in critique.get("critique_metadata", {}):
        # System error occurred
        log_error(critique["critique_metadata"]["error"])
        # overall_score will be 0, approval_recommendation will be "reject"

except Exception as e:
    # Unexpected error
    log_exception(e)
    # Use safe defaults
```

---

## Migration from Legacy APIs

### CriticAgent Migration

```python
# Old code
review = await critic_agent.review_content(content, content_type)
if review["recommendation"] == "approve":
    publish()

# New code
critique = await critic_agent.critique_content(content, content_type)
if critique["approval_recommendation"] == "approve":
    publish()
```

### GuardianAgent Migration

```python
# Old code
validation = guardian_agent.validate_content(content)
if validation["is_safe"]:
    publish()

# New code
safety = await guardian_agent.guard_content(content, content_type)
if safety["safety_status"] == "approved":
    publish()
```

---

## Support and Feedback

For questions or issues:
- File issues on the project repository
- Contact the platform team
- Review example implementations in `/examples/safety_agents/`

---

**Last Updated:** 2025-11-22
**Version:** 2.0.0
