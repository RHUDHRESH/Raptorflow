# Language Excellence Engine

A comprehensive, multi-layer language optimization system that provides obsessive quality control for grammar, style, readability, tone, and linguistic diversity.

## 🎯 Overview

The Language Excellence Engine analyzes content through five specialized modules that run in parallel, aggregating results into actionable recommendations:

1. **Grammar Orchestrator** - Multi-engine grammar checking
2. **Style Enforcer** - Brand style guide compliance
3. **Readability Optimizer** - Multi-metric readability analysis
4. **Tone Adapter** - Tone analysis and adaptation
5. **Linguistic Diversity Analyzer** - Vocabulary richness and variety

## 📦 Modules

### 1. Grammar Orchestrator (`grammar_orchestrator.py`)

Runs content through multiple grammar engines in parallel and aggregates results.

**Features:**
- **Multiple Engines**: LanguageTool, LLM-based checking, custom rules, basic patterns
- **Parallel Execution**: All engines run concurrently for speed
- **Deduplication**: Removes duplicate issues from multiple sources
- **Prioritization**: Sorts by severity (Critical → Important → Suggestion)
- **Auto-fixes**: Generates automatic fix suggestions for top issues

**Usage:**
```python
from backend.language import grammar_orchestrator

result = await grammar_orchestrator.check_grammar(
    content="Your text here",
    language="en-US"
)

print(f"Total issues: {result['total_issues']}")
print(f"Critical: {result['critical_count']}")
print(f"Auto-fixes: {len(result['auto_fixes'])}")
```

**Custom Rules Included:**
- Passive voice detection
- Weak verb usage (very, really, just)
- Wordiness patterns
- Double spacing
- Contraction consistency

### 2. Style Enforcer (`style_enforcer.py`)

Enforces brand style guidelines and writing standards.

**Features:**
- **Oxford Comma**: Enforce or prohibit Oxford comma usage
- **Sentence Starters**: Detect forbidden sentence starters (But, And, So, Because)
- **Paragraph Length**: Check min/max sentence counts per paragraph
- **Word Choice**: Flag forbidden words with suggested replacements
- **Contractions**: Control contraction usage based on style guide
- **Brand Terminology**: Enforce brand-specific terms
- **Tense Consistency**: Check for tense consistency

**Usage:**
```python
from backend.language import style_enforcer, BrandStyleGuide

# Create custom style guide
guide = BrandStyleGuide(
    name="company_guide",
    voice="professional",
    tense="present",
    use_oxford_comma=True,
    allow_contractions=False,
    forbidden_words={"utilize": "use", "leverage": "use"},
    brand_terminology={"AI": "Artificial Intelligence"}
)

result = await style_enforcer.enforce_style(content, guide)
```

**Violation Types:**
- Voice, Tense, Oxford Comma, Sentence Starters
- Paragraph Length, Word Choice, Terminology
- Formatting, Contractions

### 3. Readability Optimizer (`readability_optimizer.py`)

Calculates multiple readability metrics and provides improvement suggestions.

**Metrics Calculated:**
- **Flesch Reading Ease** (0-100, higher = easier)
- **Flesch-Kincaid Grade Level**
- **Gunning Fog Index**
- **SMOG Index**
- **Coleman-Liau Index**
- **Automated Readability Index (ARI)**

**Features:**
- Average grade level across all metrics
- Reading ease interpretation (Very Easy → Very Difficult)
- Target grade level comparison
- Specific suggestions to meet target

**Usage:**
```python
from backend.language import readability_optimizer

result = await readability_optimizer.analyze_readability(
    content="Your text here",
    target_grade_level=10  # Optional target
)

print(f"Average Grade Level: {result['average_grade_level']}")
print(f"Flesch Score: {result['metrics']['flesch_reading_ease']}")
print(f"Meets Target: {result['meets_target']}")
```

**Text Statistics:**
- Total sentences, words, syllables, characters
- Average sentence length, word length, syllables per word
- Complex word count and percentage

### 4. Tone Adapter (`tone_adapter.py`)

Analyzes current tone and adapts content to target tone profiles.

**Predefined Tone Profiles:**

| Profile | Formality | Contractions | Emoji | Jargon | Use Case |
|---------|-----------|--------------|-------|--------|----------|
| Professional | 8/10 | No | None | Moderate | Business communication |
| Conversational | 4/10 | Yes | Minimal | Minimal | Casual content |
| Thought Leadership | 7/10 | No | None | Moderate | Industry insights |
| Friendly | 3/10 | Yes | Moderate | None | Social media |
| Educational | 6/10 | No | None | Minimal | Training content |
| Persuasive | 5/10 | Yes | Minimal | Minimal | Sales copy |
| Empathetic | 4/10 | Yes | Minimal | None | Support content |
| Technical | 7/10 | No | None | Heavy | Documentation |

**Features:**
- **Tone Analysis**: Detect formality, contractions, emoji usage, jargon density
- **Profile Matching**: Match content against 8 predefined profiles
- **Tone Adaptation**: Rewrite content to match target tone
- **LLM-Powered**: Uses LLM for intelligent tone transformation

**Usage:**
```python
from backend.language import tone_adapter

# Analyze current tone
analysis = await tone_adapter.analyze_tone(content)
print(f"Best match: {analysis['best_match']['profile']}")

# Adapt to target tone
result = await tone_adapter.adapt_tone(
    content="Your text here",
    target_tone="conversational"
)

print(f"Original: {result['original_content']}")
print(f"Adapted: {result['adapted_content']}")
```

### 5. Linguistic Diversity Analyzer (`linguistic_diversity.py`)

Measures vocabulary richness, sentence variety, and rhetorical sophistication.

**Analysis Dimensions:**

**Vocabulary Metrics:**
- Total words, unique words, lexical diversity (Type-Token Ratio)
- Rare vs. common word ratio
- Most frequently used words
- Vocabulary sophistication level

**Sentence Variety:**
- Sentence length distribution (short/medium/long)
- Sentence length standard deviation
- Sentence starter diversity
- Variety score (0-100)

**Repetition Analysis:**
- Overused words (frequency > threshold)
- Repeated phrases (bigrams, trigrams)
- Repeated sentence starters
- Repetition score (0-100)

**Rhetorical Devices:**
- Alliteration detection
- Rhetorical questions
- Parallel structure
- Emphatic statements

**Usage:**
```python
from backend.language import linguistic_diversity_analyzer

result = await linguistic_diversity_analyzer.analyze_diversity(content)

print(f"Diversity Score: {result['diversity_score']}/100")
print(f"Lexical Diversity: {result['vocabulary_metrics']['lexical_diversity']}")
print(f"Sentence Variety: {result['sentence_variety']['variety_score']}")
print(f"Repetition Score: {result['repetition_analysis']['repetition_score']}")
```

## 🚀 Unified API

### `optimize_language()`

The main entry point that runs all engines and returns comprehensive analysis.

**Parameters:**
- `content` (str): Text to analyze
- `target_tone` (Optional[str]): Target tone for adaptation
- `style_guide` (Optional[BrandStyleGuide]): Custom style guide
- `target_grade_level` (Optional[int]): Target reading level (1-18)
- `run_grammar` (bool): Run grammar check (default: True)
- `run_style` (bool): Run style enforcement (default: True)
- `run_readability` (bool): Run readability analysis (default: True)
- `run_tone` (bool): Run tone analysis (default: True)
- `run_diversity` (bool): Run diversity analysis (default: True)
- `correlation_id` (Optional[str]): Request correlation ID

**Returns:**
```python
{
    "overall_score": 85,  # 0-100
    "executive_summary": {
        "overall_quality": "good",
        "key_strengths": ["Clean grammar with minimal errors", ...],
        "key_issues": ["Content may be too complex for general audience", ...],
        "top_recommendations": ["Review and fix grammar issues", ...]
    },
    "results": {
        "grammar": {...},
        "style": {...},
        "readability": {...},
        "tone": {...},
        "diversity": {...}
    },
    "aggregated_suggestions": [
        {
            "source": "grammar",
            "type": "auto_fix",
            "priority": "high",
            "issue": "...",
            "suggestion": "..."
        },
        ...
    ],
    "metadata": {
        "content_length": 1234,
        "engines_run": {...},
        "duration_ms": 567,
        "analyzed_at": "2025-11-22T...",
        "correlation_id": "..."
    }
}
```

**Example Usage:**
```python
from backend.language import optimize_language

# Full analysis
result = await optimize_language(
    content="Your marketing content here...",
    target_tone="professional",
    target_grade_level=10
)

print(f"Overall Score: {result['overall_score']}/100")
print(f"Quality: {result['executive_summary']['overall_quality']}")

# Process suggestions
for suggestion in result['aggregated_suggestions'][:5]:
    print(f"[{suggestion['priority']}] {suggestion['issue']}")
    print(f"   → {suggestion['suggestion']}")
```

## 🔗 CriticAgent Integration

The Language Excellence Engine is integrated into the CriticAgent for enhanced content review.

**Enhanced Features:**
- Automatic language analysis during content review
- Language metrics added to review scores
- Analysis history stored in memory for learning
- Language context included in LLM review prompts

**Usage:**
```python
from backend.agents.safety.critic_agent import CriticAgent
from backend.language import BrandStyleGuide

critic = CriticAgent(enable_language_engine=True)

review = await critic.review_content(
    content="Your content here",
    content_type="blog",
    style_guide=BrandStyleGuide(...),
    target_grade_level=10
)

# Review includes language analysis
language_analysis = review.get('language_analysis')
print(f"Language Score: {language_analysis['overall_score']}/100")
```

## 🧪 Testing

Comprehensive test suite with 50+ test cases covering:

- Individual module functionality
- Error detection and handling
- Custom configurations
- Integration scenarios
- Real-world use cases (blog posts, emails)
- Performance metrics

**Run Tests:**
```bash
cd /home/user/Raptorflow/backend
pytest tests/test_language_engine.py -v
```

## 📊 Performance

**Parallel Execution:**
- All grammar engines run concurrently
- Overall analysis typically completes in < 2 seconds
- Performance metrics tracked in metadata

**Scalability:**
- Handles content from 100 to 10,000+ words
- Efficient deduplication and aggregation
- Configurable engine selection for performance tuning

## 🔧 Dependencies

```
language-tool-python>=2.7.1  # Grammar checking
textstat>=0.7.3              # Readability metrics (optional)
```

Install dependencies:
```bash
pip install -r backend/requirements.txt
```

## 📝 Configuration

### Custom Style Guide

```python
from backend.language import BrandStyleGuide

custom_guide = BrandStyleGuide(
    name="my_brand",
    voice="professional",
    tense="present",
    use_oxford_comma=True,
    allow_contractions=False,
    forbidden_sentence_starters=["But", "And", "So"],
    min_paragraph_sentences=2,
    max_paragraph_sentences=6,
    forbidden_words={
        "utilize": "use",
        "leverage": "use",
        "synergy": "collaboration"
    },
    brand_terminology={
        "AI": "Artificial Intelligence",
        "ML": "Machine Learning"
    },
    max_sentence_length=25,
    heading_style="title_case"
)
```

### Custom Tone Profile

```python
from backend.language import ToneProfile

custom_tone = ToneProfile(
    name="startup_casual",
    description="Casual but professional startup voice",
    formality_level=5,
    allow_contractions=True,
    emoji_usage="minimal",
    jargon_level="moderate",
    require_citations=False,
    sentence_style="varied",
    vocabulary_level="intermediate",
    person="second",
    examples=[
        "We're building something amazing...",
        "Here's what we learned...",
        "You'll love this feature..."
    ]
)
```

## 🎯 Use Cases

### 1. Blog Post Quality Check
```python
result = await optimize_language(
    content=blog_post,
    target_grade_level=12,
    run_grammar=True,
    run_readability=True,
    run_diversity=True
)
```

### 2. Email Tone Adaptation
```python
result = await optimize_language(
    content=email_draft,
    target_tone="professional",
    run_grammar=True,
    run_tone=True
)
```

### 3. Marketing Copy Optimization
```python
result = await optimize_language(
    content=marketing_copy,
    target_tone="persuasive",
    style_guide=brand_guide,
    target_grade_level=10
)
```

### 4. Technical Documentation Review
```python
result = await optimize_language(
    content=documentation,
    target_tone="technical",
    target_grade_level=14,
    run_readability=True,
    run_style=True
)
```

## 🔍 Detailed Analysis Example

```python
from backend.language import optimize_language

content = """
The modern marketing landscape requires a data-driven approach. Companies that
leverage analytics and customer insights consistently outperform their competitors.
"""

result = await optimize_language(content)

# Overall Assessment
print(f"Overall Score: {result['overall_score']}/100")
print(f"Quality: {result['executive_summary']['overall_quality']}")

# Grammar Analysis
grammar = result['results']['grammar']
print(f"\nGrammar Issues: {grammar['total_issues']}")
print(f"Critical: {grammar['critical_count']}")

# Readability Analysis
readability = result['results']['readability']
print(f"\nGrade Level: {readability['average_grade_level']}")
print(f"Flesch Score: {readability['metrics']['flesch_reading_ease']}")

# Diversity Analysis
diversity = result['results']['diversity']
print(f"\nDiversity Score: {diversity['diversity_score']}/100")
print(f"Lexical Diversity: {diversity['vocabulary_metrics']['lexical_diversity']}")

# Top Suggestions
print("\nTop Suggestions:")
for i, suggestion in enumerate(result['aggregated_suggestions'][:5], 1):
    print(f"{i}. [{suggestion['priority']}] {suggestion['issue']}")
```

## 🚦 Score Interpretation

**Overall Score (0-100):**
- **85-100**: Excellent - Publication ready
- **70-84**: Good - Minor improvements needed
- **50-69**: Fair - Moderate revision required
- **< 50**: Needs Improvement - Major revision required

**Readability (Flesch Reading Ease):**
- **90-100**: Very Easy (5th grade)
- **80-89**: Easy (6th grade)
- **70-79**: Fairly Easy (7th grade)
- **60-69**: Standard (8th-9th grade)
- **50-59**: Fairly Difficult (10th-12th grade)
- **30-49**: Difficult (College)
- **0-29**: Very Difficult (College graduate)

**Diversity Score:**
- **70-100**: High diversity - Rich vocabulary
- **50-69**: Medium diversity - Adequate variety
- **< 50**: Low diversity - Repetitive content

## 📚 API Reference

See module docstrings for detailed API documentation:

```python
from backend.language import (
    optimize_language,
    grammar_orchestrator,
    style_enforcer,
    readability_optimizer,
    tone_adapter,
    linguistic_diversity_analyzer,
    BrandStyleGuide,
    ToneProfile
)

# Get help on any function/class
help(optimize_language)
help(BrandStyleGuide)
```

## 🎓 Best Practices

1. **Always run all engines** for comprehensive analysis unless performance is critical
2. **Set target grade level** based on your audience (10-12 for general audience)
3. **Define custom style guides** for brand consistency
4. **Use tone adaptation** to maintain consistent voice across content
5. **Monitor diversity scores** to avoid repetitive content
6. **Review top 5-10 suggestions** for quick wins
7. **Store analysis results** in memory for learning and improvement

## 🔮 Future Enhancements

Potential improvements for future iterations:

- Integration with external grammar APIs (Grammarly, ProWritingAid)
- Thesaurus API for synonym suggestions
- Sentiment analysis integration
- Multi-language support
- Custom dictionary/terminology management
- A/B testing for tone variations
- Machine learning-based learning from feedback
- Real-time collaborative editing suggestions

## 📄 License

Part of the RaptorFlow 2.0 Backend - Enterprise Multi-Agent Marketing OS

---

**Built with ❤️ for linguistic excellence**
