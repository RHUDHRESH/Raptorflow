"""
Website scraping and AI analysis endpoint for auto-filling onboarding data.
"""
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, HttpUrl
import httpx
from bs4 import BeautifulSoup
import json
from typing import Optional, Dict, Any
from backend.services.vertex_ai_client import vertex_ai_client

router = APIRouter(prefix="/api/v1/scraper", tags=["scraper"])


class WebsiteAnalysisRequest(BaseModel):
    """Request model for website analysis."""
    url: HttpUrl


class WebsiteAnalysisResponse(BaseModel):
    """Response model for website analysis."""
    business_name: Optional[str] = None
    industry: Optional[str] = None
    description: Optional[str] = None
    value_proposition: Optional[str] = None
    target_audience: Optional[str] = None
    products_services: Optional[str] = None
    company_size: Optional[str] = None
    location: Optional[str] = None
    social_links: Dict[str, str] = {}
    meta_data: Dict[str, Any] = {}
    raw_text: Optional[str] = None


async def scrape_website(url: str) -> Dict[str, Any]:
    """
    Scrape website content using httpx and BeautifulSoup.
    
    Args:
        url: The website URL to scrape
        
    Returns:
        Dictionary containing scraped data
    """
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
    }
    
    try:
        async with httpx.AsyncClient(timeout=30.0, follow_redirects=True) as client:
            response = await client.get(url, headers=headers)
            response.raise_for_status()
            
        soup = BeautifulSoup(response.text, 'html.parser')
        
        # Extract metadata
        meta_data = {}
        for meta in soup.find_all('meta'):
            name = meta.get('name') or meta.get('property')
            content = meta.get('content')
            if name and content:
                meta_data[name] = content
        
        # Extract title
        title = soup.find('title')
        title_text = title.get_text().strip() if title else None
        
        # Extract headings
        h1_tags = [h.get_text().strip() for h in soup.find_all('h1')]
        h2_tags = [h.get_text().strip() for h in soup.find_all('h2')]
        
        # Extract paragraphs (limit to first 20 for performance)
        paragraphs = [p.get_text().strip() for p in soup.find_all('p')[:20]]
        
        # Extract social links
        social_links = {}
        social_platforms = {
            'twitter': ['twitter.com', 'x.com'],
            'linkedin': ['linkedin.com'],
            'facebook': ['facebook.com'],
            'instagram': ['instagram.com'],
            'youtube': ['youtube.com']
        }
        
        for link in soup.find_all('a', href=True):
            href = link['href']
            for platform, domains in social_platforms.items():
                if any(domain in href for domain in domains):
                    social_links[platform] = href
                    break
        
        # Combine text for AI analysis
        raw_text = f"""
        Title: {title_text}
        
        Main Headings: {', '.join(h1_tags[:5])}
        
        Subheadings: {', '.join(h2_tags[:10])}
        
        Content: {' '.join(paragraphs[:15])}
        
        Meta Description: {meta_data.get('description', '')}
        """
        
        return {
            'title': title_text,
            'h1_tags': h1_tags,
            'h2_tags': h2_tags,
            'paragraphs': paragraphs,
            'meta_data': meta_data,
            'social_links': social_links,
            'raw_text': raw_text.strip()
        }
        
    except httpx.HTTPError as e:
        raise HTTPException(status_code=400, detail=f"Failed to fetch website: {str(e)}")
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Error scraping website: {str(e)}")


async def analyze_with_ai(scraped_data: Dict[str, Any], url: str) -> Dict[str, Any]:
    """
    Use AI to analyze scraped website data and extract structured business information.
    
    Args:
        scraped_data: Raw scraped data from the website
        url: Original website URL
        
    Returns:
        Structured business information
    """
    prompt = f"""
You are analyzing a business website to extract key information for a customer profile.

Website URL: {url}
Website Content:
{scraped_data['raw_text']}

Meta Description: {scraped_data['meta_data'].get('description', 'N/A')}

Please analyze this website and extract the following information in JSON format:

{{
  "business_name": "The company/business name",
  "industry": "Primary industry (e.g., SaaS, E-commerce, Healthcare, Consulting, etc.)",
  "description": "A 2-3 sentence description of what the business does",
  "value_proposition": "The main value proposition or unique selling point",
  "target_audience": "Who their target customers/audience are",
  "products_services": "Main products or services offered",
  "company_size": "Estimated company size if mentioned (e.g., 'Startup', 'Small (1-50)', 'Medium (51-200)', 'Enterprise (200+)')",
  "location": "Company location/headquarters if mentioned"
}}

If any information is not clearly available, use "Unknown" or make a reasonable inference based on the content.
Be concise and accurate. Return ONLY valid JSON.
"""
    
    try:
        result = await vertex_ai_client.generate_json(
            prompt=prompt,
            model="gemini-2.5-flash-002",
            temperature=0.3
        )
        
        return result
        
    except Exception as e:
        print(f"AI analysis error: {str(e)}")
        # Fallback to basic extraction
        return {
            "business_name": scraped_data.get('title', 'Unknown'),
            "industry": "Unknown",
            "description": scraped_data['meta_data'].get('description', 'Unknown'),
            "value_proposition": "Unknown",
            "target_audience": "Unknown",
            "products_services": "Unknown",
            "company_size": "Unknown",
            "location": "Unknown"
        }


@router.post("/analyze-website", response_model=WebsiteAnalysisResponse)
async def analyze_website(request: WebsiteAnalysisRequest):
    """
    Scrape and analyze a website to extract business information.
    
    This endpoint:
    1. Scrapes the provided website URL
    2. Extracts metadata, content, and social links
    3. Uses AI to analyze the content and extract structured business data
    4. Returns comprehensive business information for auto-filling forms
    
    Args:
        request: WebsiteAnalysisRequest containing the URL to analyze
        
    Returns:
        WebsiteAnalysisResponse with extracted business information
    """
    url_str = str(request.url)
    
    # Scrape the website
    scraped_data = await scrape_website(url_str)
    
    # Analyze with AI
    ai_analysis = await analyze_with_ai(scraped_data, url_str)
    
    # Combine results
    response = WebsiteAnalysisResponse(
        business_name=ai_analysis.get('business_name'),
        industry=ai_analysis.get('industry'),
        description=ai_analysis.get('description'),
        value_proposition=ai_analysis.get('value_proposition'),
        target_audience=ai_analysis.get('target_audience'),
        products_services=ai_analysis.get('products_services'),
        company_size=ai_analysis.get('company_size'),
        location=ai_analysis.get('location'),
        social_links=scraped_data.get('social_links', {}),
        meta_data=scraped_data.get('meta_data', {}),
        raw_text=scraped_data.get('raw_text')
    )
    
    return response
