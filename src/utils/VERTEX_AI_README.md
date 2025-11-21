# Vertex AI Model Selection Utility

This utility provides intelligent model selection for different AI tasks across the Raptorflow application.

## Overview

Instead of hardcoding a single model, we dynamically select the most appropriate model based on the task type. This ensures optimal performance, cost, and quality for each use case.

## Available Models

### 🔍 **OCR & Document Processing**
- **Model**: `pixtral-large-2411` (Mistral)
- **Task Type**: `TASK_TYPES.OCR`
- **Use Cases**: Text extraction, document analysis, image understanding
- **Context Window**: 128K tokens

### ⚡ **Fast Creative Generation**
- **Model**: `claude-3-5-haiku-20241022` (Anthropic)
- **Task Type**: `TASK_TYPES.CREATIVE_FAST`
- **Use Cases**: Quick creative responses, fast content generation
- **Context Window**: 200K tokens
- **Strengths**: Speed, cost efficiency, creative writing

### 🎨 **Creative Reasoning**
- **Model**: `claude-3-7-sonnet-20250219` (Anthropic)
- **Task Type**: `TASK_TYPES.CREATIVE_REASONING`
- **Use Cases**: Deep creative analysis, complex reasoning, strategic thinking
- **Context Window**: 200K tokens
- **Strengths**: Nuanced reasoning, creative problem solving

### 🌟 **General Purpose** (Default)
- **Model**: `gemini-2.0-flash-exp` (Google)
- **Task Type**: `TASK_TYPES.GENERAL_PURPOSE`
- **Use Cases**: Balanced tasks, general Q&A, standard processing
- **Context Window**: 1M tokens
- **Strengths**: Versatility, speed, multimodal support

### 🧠 **Advanced Reasoning**
- **Model**: `gemini-2.5-pro-preview-03-25` (Google)
- **Task Type**: `TASK_TYPES.REASONING`
- **Use Cases**: Complex analysis, advanced reasoning, code generation
- **Context Window**: 2M tokens
- **Strengths**: Deep reasoning, technical analysis

### 🔄 **Fallback Reasoning**
- **Model**: `gemini-2.0-flash-thinking-exp-01-21` (Google)
- **Task Type**: `TASK_TYPES.REASONING_FALLBACK`
- **Use Cases**: Chain-of-thought reasoning, transparent problem solving
- **Context Window**: 32K tokens
- **Strengths**: Fast inference, transparent reasoning

## Usage

### Basic Usage

```javascript
import { getVertexAIUrl, TASK_TYPES } from '../utils/vertexAI';

// Get URL for general purpose task
const url = getVertexAIUrl(TASK_TYPES.GENERAL_PURPOSE);

// Get URL for OCR task
const ocrUrl = getVertexAIUrl(TASK_TYPES.OCR);

// Get URL for creative reasoning
const creativeUrl = getVertexAIUrl(TASK_TYPES.CREATIVE_REASONING);
```

### Advanced Usage

```javascript
import {
  getVertexAIUrl,
  getModelForTask,
  getModelInfo,
  TASK_TYPES
} from '../utils/vertexAI';

// Get model name for a task
const model = getModelForTask(TASK_TYPES.REASONING);
// Returns: 'gemini-2.5-pro-preview-03-25'

// Get full model information
const info = getModelInfo(TASK_TYPES.OCR);
// Returns: { model, name, useCase, strengths, contextWindow }

// Use specific model directly (bypass task mapping)
const customUrl = getVertexAIUrl('claude-3-7-sonnet-20250219');
```

### Making API Calls

```javascript
import { getVertexAIUrl, TASK_TYPES } from '../utils/vertexAI';

async function generateContent(taskType, prompt) {
  const url = getVertexAIUrl(taskType);

  const response = await fetch(url, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      contents: [{
        parts: [{ text: prompt }]
      }],
      generationConfig: {
        temperature: 0.7,
        maxOutputTokens: 2048
      }
    })
  });

  return response.json();
}

// Example: Generate strategic questions
const result = await generateContent(
  TASK_TYPES.GENERAL_PURPOSE,
  "Analyze this business and suggest follow-up questions..."
);
```

## Task Selection Guidelines

### When to use which model:

#### Use **OCR** for:
- Extracting text from images
- Analyzing scanned documents
- Processing receipts, invoices, forms
- Visual content understanding

#### Use **CREATIVE_FAST** for:
- Quick content generation
- Simple creative writing
- Fast responses where quality can be slightly lower
- Cost-sensitive operations

#### Use **CREATIVE_REASONING** for:
- Strategic planning and analysis
- Complex creative projects
- Brand strategy and positioning
- Deep user insights
- Marketing strategy development

#### Use **GENERAL_PURPOSE** for:
- Standard Q&A
- General data processing
- Balanced speed/quality needs
- Multi-turn conversations
- Default choice when unsure

#### Use **REASONING** for:
- Complex technical problems
- Advanced code generation
- Deep analytical tasks
- Research and synthesis
- Multi-step reasoning chains

#### Use **REASONING_FALLBACK** for:
- When primary reasoning model fails
- Tasks requiring transparent thought process
- Debugging complex logic
- Educational explanations

## Current Implementations

### Onboarding Flow
- **Task**: Generate strategic follow-up questions
- **Model Used**: `GENERAL_PURPOSE` (Gemini 2.0 Flash)
- **Location**: `src/components/Onboarding.jsx:100`
- **Rationale**: Balanced performance for analyzing user inputs and generating contextual questions

### Future Implementations

Consider using different models for:
- **Cohorts Builder**: `CREATIVE_REASONING` for ICP analysis
- **Market Position**: `REASONING` for competitive analysis
- **Document Upload**: `OCR` for processing business documents
- **Quick Chat**: `CREATIVE_FAST` for rapid user interactions
- **Strategic Reports**: `CREATIVE_REASONING` for deep insights

## Configuration

### Environment Variables

Set these in your `.env.local` file:

```bash
VITE_VERTEX_AI_API_KEY=your_api_key_here
VITE_VERTEX_AI_ENDPOINT=us-central1-aiplatform.googleapis.com
```

**Note**: Model selection is automatic based on task type. No need to specify models in environment variables.

### Changing Default Models

To change which model is used for a task type, edit `src/utils/vertexAI.js`:

```javascript
export const VERTEX_AI_MODELS = {
  GENERAL_PURPOSE: 'gemini-2.0-flash-exp', // Change this
  // ... other models
};
```

## Error Handling

The utility includes built-in error handling:

```javascript
try {
  const url = getVertexAIUrl(TASK_TYPES.REASONING);
  // Make API call...
} catch (error) {
  if (error.message.includes('API key not configured')) {
    // Handle missing API key
    console.error('Please configure VITE_VERTEX_AI_API_KEY');
  }
}
```

## Testing

The model selection utility can be tested independently:

```javascript
import { getModelForTask, TASK_TYPES } from '../utils/vertexAI';

// Unit test
expect(getModelForTask(TASK_TYPES.OCR)).toBe('pixtral-large-2411');
expect(getModelForTask(TASK_TYPES.CREATIVE_FAST)).toBe('claude-3-5-haiku-20241022');
```

## Cost Optimization

Model selection impacts costs:

1. **Lowest Cost**: `CREATIVE_FAST` (Claude Haiku)
2. **Medium Cost**: `GENERAL_PURPOSE` (Gemini Flash)
3. **Higher Cost**: `CREATIVE_REASONING` (Claude Sonnet), `REASONING` (Gemini Pro)

Choose based on:
- Task complexity
- Quality requirements
- Response time needs
- Budget constraints

## Performance Characteristics

| Model | Speed | Quality | Cost | Context | Best For |
|-------|-------|---------|------|---------|----------|
| Mistral OCR | Fast | High (OCR) | Low | 128K | Document processing |
| Claude Haiku | Very Fast | Good | Low | 200K | Quick responses |
| Claude Sonnet | Fast | Excellent | Medium | 200K | Creative tasks |
| Gemini Flash | Very Fast | Good | Low | 1M | General purpose |
| Gemini Pro | Medium | Excellent | High | 2M | Complex reasoning |
| Gemini Thinking | Fast | Good | Medium | 32K | Transparent reasoning |

## Troubleshooting

### API Key Issues
```javascript
// Check if API key is configured
import { getVertexAIConfig } from '../utils/vertexAI';
const config = getVertexAIConfig();
console.log('API Key configured:', !!config.apiKey);
```

### Model Availability
Ensure your Vertex AI account has access to:
- Anthropic models (Claude)
- Google models (Gemini)
- Mistral models (Pixtral)

### Rate Limits
Different models have different rate limits. Implement retry logic:

```javascript
async function callWithRetry(taskType, payload, maxRetries = 3) {
  for (let i = 0; i < maxRetries; i++) {
    try {
      const url = getVertexAIUrl(taskType);
      const response = await fetch(url, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(payload)
      });

      if (response.ok) return await response.json();

      // If rate limited, wait and retry
      if (response.status === 429) {
        await new Promise(r => setTimeout(r, Math.pow(2, i) * 1000));
        continue;
      }

      throw new Error(`API error: ${response.status}`);
    } catch (error) {
      if (i === maxRetries - 1) throw error;
    }
  }
}
```

## Future Enhancements

Planned improvements:
- [ ] Automatic fallback if primary model fails
- [ ] Usage tracking and analytics
- [ ] A/B testing different models
- [ ] Cost monitoring and alerts
- [ ] Response quality scoring
- [ ] Dynamic model selection based on user plan tier
