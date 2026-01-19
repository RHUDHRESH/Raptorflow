"""
RaptorFlow Competitive Intelligence Service
Phase 2.2.1: Competitor Analysis Engine

Analyzes competitors through web scraping, positioning analysis,
market share estimation, and competitive intelligence gathering.
"""

import asyncio
import re
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from bs4 import BeautifulSoup
import aiohttp
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from backend.services.llm_service import LLMService, ExtractionContext
from config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class CompetitorType(str, Enum):
    """Types of competitors."""
    DIRECT = "direct"
    INDIRECT = "indirect"
    POTENTIAL = "potential"
    SUBSTITUTE = "substitute"


class PositioningType(str, Enum):
    """Competitive positioning types."""
    PRICE_LEADER = "price_leader"
    PREMIUM = "premium"
    BUDGET = "budget"
    NICHE = "niche"
    MASS_MARKET = "mass_market"
    INNOVATOR = "innovator"


@dataclass
class CompetitorData:
    """Data about a competitor."""
    name: str
    url: str
    type: CompetitorType
    description: str
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None
    market_share: Optional[float] = None
    positioning: Dict
    features: List[Dict]
    pricing: Dict
    strengths: List[str]
    weaknesses: List[str]
    market_signals: Dict
    last_updated: datetime
    confidence_score: float


@dataclass
class CompetitiveAnalysis:
    """Complete competitive analysis result."""
    competitors: List[CompetitorData]
    positioning_matrix: Dict
    market_analysis: Dict
    recommendations: List[str]
    total_competitors: int
    analysis_timestamp: datetime
    confidence_score: float


class WebScraper:
    """Web scraping for competitive intelligence."""
    
    def __init__(self):
        self.session = None
        self.user_agent = "Mozilla/5.0 (compatible; RaptorFlow-Bot/1.0)"
        self.rate_limit_delay = 1.0  # seconds between requests
        
    async def _get_session(self):
        """Get HTTP session."""
        if self.session is None:
            self.session = aiohttp.ClientSession(
                headers={'User-Agent': self.user_agent},
                timeout=aiohttp.ClientTimeout(total=30)
            )
        return self.session
    
    async def scrape_competitor_data(self, competitor_url: str) -> Dict:
        """
        Scrape comprehensive competitor data.
        
        Args:
            competitor_url: URL of competitor website
            
        Returns:
            Scraped competitor data
        """
        try:
            session = await self._get_session()
            
            async with session.get(competitor_url) as response:
                if response.status != 200:
                    logger.warning(f"Failed to scrape {competitor_url}: {response.status}")
                    return {}
                
                html = await response.text()
                soup = BeautifulSoup(html, 'html.parser')
                
                # Extract comprehensive data
                data = {
                    'url': competitor_url,
                    'title': self._extract_title(soup),
                    'description': self._extract_description(soup),
                    'features': await self._extract_features(soup),
                    'pricing': await self._extract_pricing(soup),
                    'about_us': await self._extract_about_us(soup),
                    'team_info': await self._extract_team_info(soup),
                    'contact_info': await self._extract_contact_info(soup),
                    'social_links': await self._extract_social_links(soup),
                    'news_mentions': await self._extract_news_mentions(soup),
                    'scraped_at': datetime.utcnow().isoformat()
                }
                
                return data
                
        except Exception as e:
            logger.error(f"Error scraping {competitor_url}: {e}")
            return {}
    
    def _extract_title(self, soup: BeautifulSoup) -> str:
        """Extract page title."""
        title_tag = soup.find('title')
        if title_tag:
            return title_tag.get_text().strip()
        
        # Try meta title
        meta_title = soup.find('meta', property='og:title')
        if meta_title:
            return meta_title.get('content', '').strip()
        
        # Try h1 tag
        h1_tag = soup.find('h1')
        if h1_tag:
            return h1_tag.get_text().strip()
        
        return ""
    
    def _extract_description(self, soup: BeautifulSoup) -> str:
        """Extract page description."""
        # Try meta description
        meta_desc = soup.find('meta', name='description')
        if meta_desc:
            return meta_desc.get('content', '').strip()
        
        # Try og:description
        og_desc = soup.find('meta', property='og:description')
        if og_desc:
            return og_desc.get('content', '').strip()
        
        # Try first paragraph
        first_p = soup.find('p')
        if first_p:
            text = first_p.get_text().strip()
            return text[:200] + "..." if len(text) > 200 else text
        
        return ""
    
    async def _extract_features(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract product/service features."""
        features = []
        
        # Look for feature lists
        feature_selectors = [
            'ul.feature-list',
            'div.features',
            'div.product-features',
            'section.features',
            '.feature-item',
            '.product-feature'
        ]
        
        for selector in feature_selectors:
            elements = soup.select(selector)
            for element in elements:
                feature_text = element.get_text().strip()
                if feature_text and len(feature_text) > 10:
                    features.append({
                        'name': feature_text[:100],
                        'description': feature_text,
                        'source': selector
                    })
        
        return features[:10]  # Limit to top 10 features
    
    async def _extract_pricing(self, soup: BeautifulSoup) -> Dict:
        """Extract pricing information."""
        pricing = {
            'plans': [],
            'currency': 'USD',
            'price_range': None,
            'free_trial': False,
            'contact_required': False
        }
        
        # Look for pricing tables
        pricing_tables = soup.find_all('table', class_=re.compile(r'pricing|price'))
        for table in pricing_tables:
            rows = table.find_all('tr')
            for row in rows[1:]:  # Skip header
                cells = row.find_all(['td', 'th'])
                if len(cells) >= 2:
                    plan_name = cells[0].get_text().strip()
                    price_text = cells[1].get_text().strip()
                    
                    # Extract price
                    price = self._extract_price(price_text)
                    if price:
                        pricing['plans'].append({
                            'name': plan_name,
                            'price': price,
                            'price_text': price_text
                        })
        
        # Look for price mentions in text
        price_mentions = soup.find_all(text=re.compile(r'\$\d+|\$\d+,\d+|\d+\.\d+'))
        if price_mentions:
            prices = []
            for mention in price_mentions:
                price = self._extract_price(mention)
                if price:
                    prices.append(price)
            
            if prices:
                pricing['price_range'] = {
                    'min': min(prices),
                    'max': max(prices),
                    'average': np.mean(prices)
                }
        
        # Check for free trial
        free_trial_keywords = ['free trial', '14-day free', '30-day money back']
        page_text = soup.get_text().lower()
        pricing['free_trial'] = any(keyword in page_text for keyword in free_trial_keywords)
        
        # Check for contact required
        contact_keywords = ['contact us', 'call for pricing', 'enterprise pricing']
        pricing['contact_required'] = any(keyword in page_text for keyword in contact_keywords)
        
        return pricing
    
    def _extract_price(self, price_text: str) -> Optional[float]:
        """Extract numeric price from text."""
        # Remove currency symbols and extract numbers
        clean_text = re.sub(r'[^\d.,]', '', price_text)
        
        # Look for patterns like "$19.99", "19.99", "$1,999"
        price_match = re.search(r'(\d+(?:,\d+)*(?:\.\d+)?)', clean_text)
        
        if price_match:
            try:
                price_str = price_match.group(1).replace(',', '')
                return float(price_str)
            except ValueError:
                pass
        
        return None
    
    async def _extract_about_us(self, soup: BeautifulSoup) -> Dict:
        """Extract about us information."""
        about = {
            'company_description': '',
            'founded_year': None,
            'headquarters': '',
            'team_size': None
        }
        
        # Look for about section
        about_selectors = [
            'section.about',
            'div.about-us',
            'div.company-info',
            '.about-content',
            '.company-description'
        ]
        
        for selector in about_selectors:
            element = soup.select_one(selector)
            if element:
                text = element.get_text().strip()
                about['company_description'] = text[:500]  # Limit length
                
                # Extract founded year
                year_match = re.search(r'(?:founded|since|est\.?)\s*(\d{4})', text, re.IGNORECASE)
                if year_match:
                    about['founded_year'] = int(year_match.group(1))
                
                # Extract team size
                size_match = re.search(r'(\d+(?:\s*\+\s*\d+)*)\s*(?:employees|people|team)', text, re.IGNORECASE)
                if size_match:
                    # Handle ranges like "50-100 employees"
                    size_text = size_match.group(1)
                    if '-' in size_text:
                        parts = size_text.split('-')
                        try:
                            min_size = int(re.sub(r'[^\d]', '', parts[0]))
                            max_size = int(re.sub(r'[^\d]', '', parts[1]))
                            about['team_size'] = (min_size + max_size) // 2
                        except ValueError:
                            pass
                    else:
                        try:
                            about['team_size'] = int(re.sub(r'[^\d]', '', size_text))
                        except ValueError:
                            pass
                
                break
        
        return about
    
    async def _extract_team_info(self, soup: BeautifulSoup) -> Dict:
        """Extract team information."""
        team = {
            'executives': [],
            'founders': [],
            'board_members': []
        }
        
        # Look for team sections
        team_selectors = [
            'section.team',
            'div.leadership',
            'div.executives',
            '.team-members',
            '.founders'
        ]
        
        for selector in team_selectors:
            elements = soup.select(selector)
            for element in elements:
                text = element.get_text().strip()
                if len(text) > 10:
                    # Try to identify role
                    if any(keyword in text.lower() for keyword in ['ceo', 'founder', 'president']):
                        team['founders'].append(text[:100])
                    elif any(keyword in text.lower() for keyword in ['cto', 'director', 'vp']):
                        team['executives'].append(text[:100])
                    else:
                        team['board_members'].append(text[:100])
        
        return team
    
    async def _extract_contact_info(self, soup: BeautifulSoup) -> Dict:
        """Extract contact information."""
        contact = {
            'email': '',
            'phone': '',
            'address': '',
            'website': ''
        }
        
        # Extract email
        email_link = soup.find('a', href=re.compile(r'mailto:'))
        if email_link:
            contact['email'] = email_link.get('href').replace('mailto:', '')
        
        # Extract phone
        phone_patterns = [
            r'\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}',
            r'\+?1?[-.\s]?\d{3}[-.\s]?\d{3}[-.\s]?\d{4}'
        ]
        
        page_text = soup.get_text()
        for pattern in phone_patterns:
            match = re.search(pattern, page_text)
            if match:
                contact['phone'] = match.group()
                break
        
        # Extract address
        address_selectors = [
            'address',
            '.address',
            '.location',
            'div.contact-info'
        ]
        
        for selector in address_selectors:
            element = soup.select_one(selector)
            if element:
                address_text = element.get_text().strip()
                if len(address_text) > 20:
                    contact['address'] = address_text[:200]
                    break
        
        return contact
    
    async def _extract_social_links(self, soup: BeautifulSoup) -> Dict:
        """Extract social media links."""
        social = {
            'linkedin': '',
            'twitter': '',
            'facebook': '',
            'instagram': '',
            'youtube': ''
        }
        
        # Look for social links
        social_patterns = {
            'linkedin': r'linkedin\.com',
            'twitter': r'twitter\.com',
            'facebook': r'facebook\.com',
            'instagram': r'instagram\.com',
            'youtube': r'youtube\.com'
        }
        
        links = soup.find_all('a', href=True)
        for link in links:
            href = link.get('href', '')
            for platform, pattern in social_patterns.items():
                if re.search(pattern, href, re.IGNORECASE):
                    social[platform] = href
        
        return social
    
    async def _extract_news_mentions(self, soup: BeautifulSoup) -> List[Dict]:
        """Extract news mentions or press releases."""
        news = []
        
        # Look for news sections
        news_selectors = [
            'section.news',
            'div.press-releases',
            'div.news',
            '.news-item',
            '.press-release'
        ]
        
        for selector in news_selectors:
            elements = soup.select(selector)
            for element in elements:
                title = element.find(['h1', 'h2', 'h3', 'h4'])
                title_text = title.get_text().strip() if title else ''
                
                date_element = element.find(['time', 'span.date', 'div.date'])
                date_text = date_element.get_text().strip() if date_element else ''
                
                summary = element.get_text().strip()
                
                if title_text or date_text:
                    news.append({
                        'title': title_text[:100],
                        'date': date_text[:50],
                        'summary': summary[:300],
                        'source': selector
                    })
        
        return news[:5]  # Limit to 5 most recent


class MarketAnalyzer:
    """Market analysis and positioning calculations."""
    
    def __init__(self):
        self.llm_service = LLMService()
        
    async def analyze_positioning(self, competitor_data: List[CompetitorData], company_info: Dict) -> Dict:
        """
        Analyze competitive positioning.
        
        Args:
            competitor_data: List of competitor data
            company_info: Our company information
            
        Returns:
            Positioning analysis
        """
        try:
            # Prepare data for LLM analysis
            analysis_data = {
                'our_company': company_info,
                'competitors': [
                    {
                        'name': comp.name,
                        'description': comp.description,
                        'features': comp.features,
                        'pricing': comp.pricing,
                        'positioning': comp.positioning
                    }
                    for comp in competitor_data
                ]
            }
            
            # Use LLM for positioning analysis
            llm_result = await self.llm_service.generate_competitive_intelligence(company_info)
            
            if 'competitive_analysis' in llm_result:
                return llm_result['competitive_analysis']
            
            # Fallback to basic analysis
            return self._basic_positioning_analysis(competitor_data, company_info)
            
        except Exception as e:
            logger.error(f"Positioning analysis failed: {e}")
            return {}
    
    def _basic_positioning_analysis(self, competitors: List[CompetitorData], company_info: Dict) -> Dict:
        """Basic positioning analysis without LLM."""
        positioning = {
            'competitors': [],
            'market_gaps': [],
            'opportunities': []
        }
        
        # Analyze competitor positioning
        for comp in competitors:
            comp_positioning = {
                'name': comp.name,
                'type': comp.type.value,
                'strengths': comp.strengths,
                'weaknesses': comp.weaknesses,
                'market_share': comp.market_share or 0.0
            }
            positioning['competitors'].append(comp_positioning)
        
        # Identify market gaps
        all_features = set()
        for comp in competitors:
            all_features.update([f['name'] for f in comp.features])
        
        our_features = set([f['name'] for f in company_info.get('features', [])])
        market_gaps = list(all_features - our_features)
        positioning['market_gaps'] = market_gaps[:10]  # Top 10 gaps
        
        return positioning
    
    async def analyze_market(self, competitor_data: List[CompetitorData]) -> Dict:
        """
        Analyze market structure and dynamics.
        
        Args:
            competitor_data: List of competitor data
            
        Returns:
            Market analysis
        """
        market_analysis = {
            'market_size': 0,
            'growth_rate': 0.0,
            'competition_level': 'medium',
            'market_trends': [],
            'barriers_to_entry': []
        }
        
        # Calculate market metrics
        total_revenue = sum([comp.revenue or 0 for comp in competitor_data])
        avg_revenue = total_revenue / len(competitor_data) if competitor_data else 0
        
        # Estimate market size (simplified)
        if avg_revenue > 0:
            # Assume average company captures 5% of market
            market_analysis['market_size'] = avg_revenue * 20
        
        # Competition level based on number of competitors
        if len(competitor_data) > 10:
            market_analysis['competition_level'] = 'high'
        elif len(competitor_data) > 5:
            market_analysis['competition_level'] = 'medium'
        else:
            market_analysis['competition_level'] = 'low'
        
        # Common barriers to entry
        barriers = []
        for comp in competitor_data:
            if comp.market_share and comp.market_share > 0.1:  # >10% market share
                barriers.append(f"High market share by {comp.name}")
            if comp.revenue and comp.revenue > 1000000:  # >$1M revenue
                barriers.append(f"Established competitor: {comp.name}")
        
        market_analysis['barriers_to_entry'] = barriers[:5]
        
        return market_analysis


class CompetitiveService:
    """Main competitive intelligence service."""
    
    def __init__(self):
        self.web_scraper = WebScraper()
        self.market_analyzer = MarketAnalyzer()
        
    async def analyze_competitors(self, company_info: Dict) -> CompetitiveAnalysis:
        """
        Perform comprehensive competitive analysis.
        
        Args:
            company_info: Our company information
            
        Returns:
            Complete competitive analysis
        """
        try:
            # Identify competitors
            competitors = await self.identify_competitors(company_info)
            
            # Gather competitor data
            competitor_data = []
            for competitor in competitors:
                data = await self.web_scraper.scrape_competitor_data(competitor['url'])
                if data:
                    comp_data = CompetitorData(
                        name=competitor['name'],
                        url=competitor['url'],
                        type=competitor['type'],
                        description=data.get('description', ''),
                        founded_year=data.get('about_us', {}).get('founded_year'),
                        headquarters=data.get('about_us', {}).get('headquarters'),
                        employee_count=data.get('about_us', {}).get('team_size'),
                        revenue=None,  # Would need additional data sources
                        market_share=None,  # Would need market research
                        positioning=data.get('positioning', {}),
                        features=data.get('features', []),
                        pricing=data.get('pricing', {}),
                        strengths=[],
                        weaknesses=[],
                        market_signals=data,
                        last_updated=datetime.utcnow(),
                        confidence_score=0.7
                    )
                    competitor_data.append(comp_data)
            
            # Analyze positioning
            positioning_matrix = await self.market_analyzer.analyze_positioning(competitor_data, company_info)
            
            # Analyze market
            market_analysis = await self.market_analyzer.analyze_market(competitor_data)
            
            # Generate recommendations
            recommendations = await self.generate_recommendations(competitor_data, positioning_matrix, market_analysis)
            
            return CompetitiveAnalysis(
                competitors=competitor_data,
                positioning_matrix=positioning_matrix,
                market_analysis=market_analysis,
                recommendations=recommendations,
                total_competitors=len(competitor_data),
                analysis_timestamp=datetime.utcnow(),
                confidence_score=0.75
            )
            
        except Exception as e:
            logger.error(f"Competitive analysis failed: {e}")
            raise
    
    async def identify_competitors(self, company_info: Dict) -> List[Dict]:
        """
        Identify potential competitors based on company information.
        
        Args:
            company_info: Our company information
            
        Returns:
            List of potential competitors
        """
        competitors = []
        
        # Use LLM to identify competitors
        try:
            llm_result = await self.llm_service.generate_competitive_intelligence(company_info)
            
            if 'competitive_analysis' in llm_result:
                analysis = llm_result['competitive_analysis']
                if 'competitors' in analysis:
                    for comp in analysis['competitors']:
                        competitors.append({
                            'name': comp.get('name', ''),
                            'url': comp.get('url', ''),
                            'type': comp.get('type', 'direct'),
                            'reason': comp.get('reason', 'Market analysis')
                        })
            
            # Fallback: basic competitor identification
            if not competitors:
                competitors = await self._basic_competitor_identification(company_info)
            
        except Exception as e:
            logger.error(f"Competitor identification failed: {e}")
            competitors = await self._basic_competitor_identification(company_info)
        
        return competitors[:10]  # Limit to top 10
    
    async def _basic_competitor_identification(self, company_info: Dict) -> List[Dict]:
        """Basic competitor identification without LLM."""
        # This is a simplified fallback
        # In a real implementation, you'd use market research APIs
        industry = company_info.get('industry', '').lower()
        
        # Industry-specific competitor patterns
        industry_patterns = {
            'technology': [
                {'name': 'Microsoft', 'url': 'https://microsoft.com', 'type': 'direct'},
                {'name': 'Google', 'url': 'https://google.com', 'type': 'direct'},
                {'name': 'Amazon', 'url': 'https://amazon.com', 'type': 'direct'}
            ],
            'retail': [
                {'name': 'Walmart', 'url': 'https://walmart.com', 'type': 'direct'},
                {'name': 'Target', 'url': 'https://target.com', 'type': 'direct'},
                {'name': 'Amazon', 'url': 'https://amazon.com', 'type': 'direct'}
            ],
            'healthcare': [
                {'name': 'UnitedHealth', 'url': 'https://unitedhealth.com', 'type': 'direct'},
                {'name': 'Anthem', 'url': 'https://anthem.com', 'type': 'direct'},
                {'name': 'CVS Health', 'url': 'https://cvshealth.com', 'type': 'direct'}
            ]
        }
        
        return industry_patterns.get(industry, [])
    
    async def generate_recommendations(self, competitors: List[CompetitorData], positioning: Dict, market: Dict) -> List[str]:
        """Generate strategic recommendations based on analysis."""
        recommendations = []
        
        # Analyze competitive gaps
        if len(competitors) > 0:
            avg_features = len(np.mean([len(comp.features) for comp in competitors]))
            
            # Feature recommendations
            if avg_features > 5:
                recommendations.append("Consider expanding feature set to match market leaders")
            
            # Pricing recommendations
            pricing_strategies = [comp.pricing for comp in competitors if comp.pricing]
            if pricing_strategies:
                free_trial_count = sum(1 for p in pricing_strategies if p.get('free_trial', False))
                if free_trial_count > len(competitors) / 2:
                    recommendations.append("Consider offering free trial to increase conversion")
            
            # Market positioning recommendations
            if market.get('competition_level') == 'high':
                recommendations.append("Focus on differentiation and niche markets")
                recommendations.append("Consider strategic partnerships to increase market share")
            
            # Strength-based recommendations
            common_strengths = {}
            for comp in competitors:
                for strength in comp.strengths:
                    common_strengths[strength] = common_strengths.get(strength, 0) + 1
            
            if common_strengths:
                top_strengths = sorted(common_strengths.items(), key=lambda x: x[1], reverse=True)[:3]
                recommendations.append(f"Leverage strengths in: {', '.join([s[0] for s in top_strengths])}")
        
        # General strategic recommendations
        recommendations.extend([
            "Monitor competitor activities and respond quickly to market changes",
            "Focus on unique value proposition and customer experience",
            "Invest in innovation to create competitive advantages",
            "Develop strong brand identity and market positioning"
        ])
        
        return recommendations[:10]  # Limit to 10 recommendations


# Pydantic models for API responses
class CompetitorResponse(BaseModel):
    """Response model for competitor data."""
    name: str
    url: str
    type: str
    description: str
    founded_year: Optional[int] = None
    headquarters: Optional[str] = None
    employee_count: Optional[int] = None
    revenue: Optional[float] = None
    market_share: Optional[float] = None
    positioning: Dict
    features: List[Dict]
    pricing: Dict
    strengths: List[str]
    weaknesses: List[str]
    confidence_score: float


class CompetitiveAnalysisResponse(BaseModel):
    """Response model for competitive analysis."""
    competitors: List[CompetitorResponse]
    positioning_matrix: Dict
    market_analysis: Dict
    recommendations: List[str]
    total_competitors: int
    analysis_timestamp: datetime
    confidence_score: float


# Error classes
class CompetitiveError(Exception):
    """Base competitive intelligence error."""
    pass


class ScrapingError(CompetitiveError):
    """Web scraping error."""
    pass


class AnalysisError(CompetitiveError):
    """Analysis error during competitive intelligence."""
    pass
