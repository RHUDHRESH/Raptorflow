import { DynamicStructuredTool } from "@langchain/core/tools";
import { z } from "zod";
// Internal enrichment stubs (replace with in-house tools)
const clearbitLookup = async (domain: string) => {
  return {
    name: "Acme Corp",
    legalName: "Acme Corporation Inc.",
    domain: domain,
    metrics: {
      employees: 150,
      raised: 10000000,
      annualRevenue: 5000000
    },
    geo: {
      city: "San Francisco",
      country: "USA",
      countryCode: "US"
    },
    category: {
      industry: "Software",
      industryGroup: "Technology"
    },
    linkedin: {
      handle: "linkedin.com/company/acme-corp"
    },
    twitter: {
      handle: "acmecorp"
    }
  };
};

const BUILTWITH_API_URL = "https://api.builtwith.com/v20/api.json";

type BuiltWithTechnology = {
  name?: string;
  categories: string[];
  firstDetected?: string;
  lastDetected?: string;
};

const normalizeCategories = (rawCategories: any): string[] => {
  if (!rawCategories) return [];
  if (Array.isArray(rawCategories)) {
    return rawCategories
      .map((cat) => {
        if (typeof cat === "string") return cat;
        if (typeof cat?.Name === "string") return cat.Name;
        return undefined;
      })
      .filter((cat): cat is string => Boolean(cat));
  }
  if (typeof rawCategories === "string") return [rawCategories];
  if (typeof rawCategories?.Name === "string") return [rawCategories.Name];
  return [];
};

// BuiltWith-style tech detection with real API usage and graceful fallback
const builtwithLookup = async (domain: string) => {
  const apiKey = process.env.BUILTWITH_API_KEY;
  if (!apiKey) {
    return {
      domain,
      technologies: [],
      categories: [],
      error: "BUILTWITH_API_KEY not configured; skipping BuiltWith lookup."
    };
  }

  const url = new URL(BUILTWITH_API_URL);
  url.searchParams.set("KEY", apiKey);
  url.searchParams.set("LOOKUP", domain);

  try {
    const response = await fetch(url);
    if (!response.ok) {
      return {
        domain,
        technologies: [],
        categories: [],
        error: `BuiltWith API error: ${response.status}`
      };
    }

    const payload = await response.json();
    const technologies: BuiltWithTechnology[] = [];

    for (const result of payload?.Results ?? []) {
      for (const path of result?.Result?.Paths ?? []) {
        for (const tech of path?.Technologies ?? []) {
          technologies.push({
            name: tech?.Name,
            categories: normalizeCategories(tech?.Categories ?? tech?.Category),
            firstDetected: tech?.FirstDetected,
            lastDetected: tech?.LastDetected
          });
        }
      }
    }

    const categories = Array.from(
      new Set(
        technologies.flatMap((tech) => tech.categories ?? [])
      )
    );

    return {
      domain,
      technologies,
      categories
    };
  } catch (error) {
    return {
      domain,
      technologies: [],
      categories: [],
      error: `BuiltWith request failed: ${error instanceof Error ? error.message : String(error)}`
    };
  }
};

export const clearbitTool = new DynamicStructuredTool({
  name: "clearbit_company_lookup",
  description: "Fetch company data from Clearbit using the company domain.",
  schema: z.object({
    domain: z.string().describe("The company domain name (e.g. google.com)"),
  }),
  func: async ({ domain }) => {
    try {
      const data = await clearbitLookup(domain);
      return JSON.stringify(data);
    } catch (error) {
      return `Error fetching data from Clearbit: ${error}`;
    }
  },
});

export const builtwithTool = new DynamicStructuredTool({
  name: "builtwith_technology_lookup",
  description: "Fetch technology stack from BuiltWith using the company domain.",
  schema: z.object({
    domain: z.string().describe("The company domain name (e.g. google.com)"),
  }),
  func: async ({ domain }) => {
    try {
      const data = await builtwithLookup(domain);
      return JSON.stringify(data);
    } catch (error) {
      return `Error fetching data from BuiltWith: ${error}`;
    }
  },
});

export const linkedinTool = new DynamicStructuredTool({
  name: "linkedin_company_scrape",
  description: "Get LinkedIn company page data.",
  schema: z.object({
    domain: z.string().describe("The company domain name"),
  }),
  func: async ({ domain }) => {
    // Placeholder for LinkedIn scraping
    return JSON.stringify({
      url: `https://www.linkedin.com/company/${domain.split('.')[0]}`,
      employeeCount: 120
    });
  },
});
