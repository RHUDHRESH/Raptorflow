# Company Enricher
## Metadata
Description: Enrich company data from domain or name
Category: enrichment
Cost Estimate: $0.005
Timeout MS: 10000

## Parameters
domain: string
include_social: boolean (default: false)
include_tech_stack: boolean (default: true)

## Output Format
company_name: string
domain: string
industry: string
description: string
social_links: object (optional)
tech_stack: array (optional)

## Implementation
```typescript
// Integration with Clearbit/BuiltWith APIs
const enriched = await enrichCompany(params);
return enriched;
```

## Examples
### Basic enrichment
Input: { "domain": "openai.com" }
Output: { "company_name": "OpenAI", "industry": "AI" }
Explanation: Standard company data enrichment
