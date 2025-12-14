# Web Scraper
## Metadata
Description: Scrape content from web pages with optional CSS selectors
Category: scraping
Cost Estimate: $0.01
Timeout MS: 30000

## Parameters
url: string
selector: string (optional)
include_text: boolean (default: true)
include_html: boolean (default: false)

## Output Format
content: string
url: string
timestamp: string
status: string

## Implementation
```typescript
// Implementation would integrate with Cheerio/Puppeteer
const result = await scrapeWebsite(params);
return result;
```

## Examples
### Basic scraping
Input: { "url": "https://example.com", "include_text": true }
Output: { "content": "Page content...", "url": "https://example.com" }
Explanation: Basic content extraction

### Selector-based scraping
Input: { "url": "https://news.com", "selector": ".article-content" }
Output: { "content": "Article text...", "url": "https://news.com" }
Explanation: Extract specific content sections
