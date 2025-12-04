import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
import * as cheerio from "cheerio";

// Simple scraper using fetch and cheerio
const scrapeWebsite = async (url: string) => {
  try {
    if (!url.startsWith('http')) {
        url = 'https://' + url;
    }
    const response = await fetch(url);
    const html = await response.text();
    const $ = cheerio.load(html);
    
    // Extract text content
    const text = $('body').text().replace(/\s+/g, ' ').trim().slice(0, 5000); // Limit content
    const title = $('title').text();
    const metaDescription = $('meta[name="description"]').attr('content') || '';
    
    return {
      title,
      description: metaDescription,
      content: text
    };
  } catch (error) {
    console.error(`Failed to scrape ${url}:`, error);
    return { error: "Failed to scrape website" };
  }
};

const googleSearch = async (query: string) => {
  // Placeholder for Google Search
  // Would require SERP API key
  console.warn("Google Search API not configured. Returning mock results.");
  return [
    { title: `${query} - Result 1`, snippet: "Mock search result snippet 1..." },
    { title: `${query} - Result 2`, snippet: "Mock search result snippet 2..." }
  ];
};

const g2Scraper = async (productName: string) => {
    // Placeholder
    return {
        rating: 4.5,
        reviews: ["Great product", "Good value"]
    };
};

export const webScraperTool = new DynamicStructuredTool({
  name: "web_scraper",
  description: "Fetch and parse competitor websites to extract messaging and features.",
  schema: z.object({
    url: z.string().describe("The URL of the website to scrape"),
  }),
  func: async ({ url }) => {
    const data = await scrapeWebsite(url);
    return JSON.stringify(data);
  },
});

export const googleSearchTool = new DynamicStructuredTool({
  name: "google_search",
  description: "Search for competitor pricing, reviews, and comparisons.",
  schema: z.object({
    query: z.string().describe("The search query"),
  }),
  func: async ({ query }) => {
    const data = await googleSearch(query);
    return JSON.stringify(data);
  },
});

export const g2ScraperTool = new DynamicStructuredTool({
  name: "g2_scraper",
  description: "Get G2 Crowd reviews and comparisons.",
  schema: z.object({
    productName: z.string().describe("The name of the product to search on G2"),
  }),
  func: async ({ productName }) => {
    const data = await g2Scraper(productName);
    return JSON.stringify(data);
  },
});
