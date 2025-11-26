/**
 * Website scraping and AI analysis service
 * Automatically extracts business information from websites
 */

const API_BASE_URL = (import.meta as any).env?.VITE_API_URL || 'http://localhost:8000';

/**
 * Get authentication token from localStorage
 */
function getAuthToken() {
    return localStorage.getItem('supabase.auth.token');
}

/**
 * Website analysis response interface
 */
export interface WebsiteAnalysis {
    business_name: string | null;
    industry: string | null;
    description: string | null;
    value_proposition: string | null;
    target_audience: string | null;
    products_services: string | null;
    company_size: string | null;
    location: string | null;
    social_links: Record<string, string>;
    meta_data: Record<string, any>;
    raw_text: string | null;
}

/**
 * Analyze a website and extract business information using AI
 * 
 * @param url - The website URL to analyze
 * @returns Promise<WebsiteAnalysis> - Extracted business information
 */
export async function analyzeWebsite(url: string): Promise<WebsiteAnalysis> {
    const token = getAuthToken();

    const response = await fetch(`${API_BASE_URL}/api/v1/scraper/analyze-website`, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            ...(token && { 'Authorization': `Bearer ${token}` })
        },
        body: JSON.stringify({ url })
    });

    if (!response.ok) {
        const error = await response.json().catch(() => ({ detail: 'Failed to analyze website' }));
        throw new Error(error.detail || 'Failed to analyze website');
    }

    return response.json();
}

/**
 * Check if a URL is valid
 */
export function isValidUrl(urlString: string): boolean {
    try {
        const url = new URL(urlString);
        return url.protocol === 'http:' || url.protocol === 'https:';
    } catch {
        return false;
    }
}

/**
 * Normalize URL by adding protocol if missing
 */
export function normalizeUrl(url: string): string {
    if (!url) return '';

    // Remove whitespace
    url = url.trim();

    // Add https:// if no protocol specified
    if (!url.match(/^https?:\/\//i)) {
        url = 'https://' + url;
    }

    return url;
}
