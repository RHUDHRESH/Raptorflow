"""
Signal Extraction Service - Extracts meaningful signals from scraped content
"""
import hashlib
import logging
import re
from datetime import datetime, timedelta
from difflib import SequenceMatcher
from typing import Any, Dict, List, Optional, Tuple

from core.crawler_advanced import AdvancedCrawler
from core.crawl_cache import content_hash, normalize_url
from inference import InferenceProvider
from models.radar_models import (
    Evidence,
    EvidenceType,
    Signal,
    SignalCategory,
    SignalFreshness,
    SignalStrength,
)

logger = logging.getLogger("raptorflow.signal_extraction")


class SignalExtractionService:
    """
    Service for extracting competitive signals from web content.
    Handles change detection, signal categorization, and strength scoring.
    """

    def __init__(self):
        self.crawler = AdvancedCrawler()
        self.llm = InferenceProvider.get_model(model_tier="reasoning")
        
        # Enhanced signal pattern matching with more sophisticated regex
        self.signal_patterns = {
            SignalCategory.OFFER: [
                # Pricing patterns
                r"(?i)(pricing|plans?|tiers?|packages?|subscription|cost|price)",
                r"(?i)\$\d+\.?\d*\/(month|year|mo|yr|week|day)",
                r"(?i)\$\d+\.?\d*\s*(per|/)\s*(month|year|mo|yr)",
                # Plan names
                r"(?i)(free|trial|demo|starter|basic|pro|professional|enterprise|premium|plus|ultimate)",
                # Value propositions
                r"(?i)(save \d+%|discount \d+|\d+% off)",
                r"(?i)(money.back guarantee|refund|cancellation)",
            ],
            SignalCategory.HOOK: [
                # Superlatives and exclusivity
                r"(?i)(the only|never|always|first|last|only|best|worst|#1|top rated)",
                # Pain points and solutions
                r"(?i)(stop wasting|eliminate|destroy|crush|dominate|conquer|master)",
                r"(?i)(struggle with|tired of|sick of|hate|can't stand)",
                # Secret/revelation language
                r"(?i)(secret|hack|trick|blueprint|formula|system|method|technique)",
                r"(?i)(revealed|uncovered|discovered|exposed|finally)",
                # Authority and social proof
                r"(?i)(guaranteed|proven|tested|validated|certified)",
            ],
            SignalCategory.PROOF: [
                # Customer evidence
                r"(?i)(customer|client|testimonial|review|rating|stars|feedback)",
                r"(?i)(case study|success story|results|outcome|achievement)",
                # Quantitative results
                r"(?i)(\d+%|\d+x increase|saved \d+|reduced by \d+|improved by \d+)",
                r"(?i)(ROI|return on investment|payback|break.even)",
                # Social proof indicators
                r"(?i)(trusted by|used by|chosen by|serving|helping)",
                r"(?i)(over \d+ customers|\d+ users|\d+ businesses)",
            ],
            SignalCategory.CTA: [
                # Action verbs
                r"(?i)(get started|sign up|register|join|begin|start)",
                r"(?i)(buy now|purchase|order|add to cart|checkout)",
                r"(?i)(contact us|reach out|talk to|schedule|book)",
                # Urgency and scarcity
                r"(?i)(limited time|only \d+ left|ending soon|don't miss)",
                r"(?i)(claim your|get your|reserve your|secure your)",
                # Low friction actions
                r"(?i)(learn more|discover|explore|find out|see how)",
            ],
            SignalCategory.OBJECTION: [
                # Price objections
                r"(?i)(too expensive|costly|pricey|budget|afford|can't afford)",
                r"(?i)(worth it|value for money|good value|reasonable price)",
                # Complexity objections
                r"(?i)(complicated|complex|difficult|hard to use|confusing)",
                r"(?i)(easy to use|simple|straightforward|intuitive)",
                # Time and effort objections
                r"(?i)(time consuming|slow|takes too long|quick|fast)",
                r"(?i)(setup|installation|implementation|onboarding)",
                # Risk and trust objections
                r"(?i)(risk|risky|scam|legit|trust|reliable|secure)",
            ],
            SignalCategory.TREND: [
                # New launches and updates
                r"(?i)(new|launch|release|announce|introduce|unveil|reveal)",
                r"(?i)(update|upgrade|improve|enhance|evolve|modernize)",
                # Business changes
                r"(?i)(integration|partnership|acquisition|merger|joint venture)",
                r"(?i)(funding|investment|raise|series [ABC]|round)",
                # Market movements
                r"(?i)(expanding|growing|scaling|entering|moving into)",
                r"(?i)(pivot|shift|change|transform|rebrand)",
            ],
        }

    async def extract_signals_from_source(
        self, 
        source_url: str, 
        previous_content: Optional[str] = None,
        tenant_id: str = "default"
    ) -> List[Signal]:
        """
        Extract signals from a source URL, comparing with previous content if available.
        """
        try:
            # Scrape current content
            scrape_result = await self.crawler.scrape_semantic(source_url)
            if not scrape_result:
                logger.warning(f"Failed to scrape {source_url}")
                return []

            current_content = scrape_result.get("content", "")
            current_title = scrape_result.get("title", "")
            
            # Generate evidence
            evidence = Evidence(
                type=EvidenceType.URL,
                source=source_url,
                url=source_url,
                content=current_content[:1000],  # First 1000 chars as evidence
                confidence=0.9,
                metadata={
                    "title": current_title,
                    "scrape_source": scrape_result.get("source", "unknown"),
                    "content_length": len(current_content)
                }
            )

            # Extract signals based on content analysis
            if previous_content:
                # Change detection mode
                signals = await self._extract_change_signals(
                    previous_content, current_content, source_url, evidence, tenant_id
                )
            else:
                # Full content analysis mode
                signals = await self._extract_content_signals(
                    current_content, source_url, evidence, tenant_id
                )

            logger.info(f"Extracted {len(signals)} signals from {source_url}")
            return signals

        except Exception as e:
            logger.error(f"Error extracting signals from {source_url}: {e}")
            return []

    async def _extract_change_signals(
        self,
        old_content: str,
        new_content: str,
        source_url: str,
        evidence: Evidence,
        tenant_id: str
    ) -> List[Signal]:
        """Extract signals based on content changes."""
        signals = []

        # Calculate content similarity
        similarity = SequenceMatcher(None, old_content, new_content).ratio()
        
        if similarity > 0.95:  # Very similar, likely no meaningful changes
            return signals

        # Find significant changes
        changes = self._detect_content_changes(old_content, new_content)
        
        for change_type, changed_content in changes:
            # Categorize the change
            category = self._categorize_content(changed_content)
            if not category:
                continue

            # Extract signal from change
            signal = await self._create_signal_from_content(
                changed_content, category, source_url, evidence, tenant_id
            )
            
            if signal:
                signals.append(signal)

        return signals

    async def _extract_content_signals(
        self,
        content: str,
        source_url: str,
        evidence: Evidence,
        tenant_id: str
    ) -> List[Signal]:
        """Extract signals from full content analysis."""
        signals = []

        # Use LLM to identify potential signals
        prompt = f"""
        Analyze this web content for competitive intelligence signals:
        
        Content: {content[:2000]}
        
        Identify 3-5 significant signals that would be valuable for competitive analysis.
        For each signal, provide:
        1. Category (offer/hook/proof/cta/objection/trend)
        2. Brief description
        3. Why it matters
        
        Return as JSON list:
        [
            {{
                "category": "offer",
                "description": "Changed pricing from $299 to $399",
                "significance": "Price increase indicates market positioning shift"
            }}
        ]
        """

        try:
            response = await self.llm.ainvoke(prompt)
            llm_signals = self._parse_llm_response(response.content)
            
            for signal_data in llm_signals:
                category = SignalCategory(signal_data.get("category", "trend"))
                description = signal_data.get("description", "")
                significance = signal_data.get("significance", "")
                
                signal = Signal(
                    tenant_id=tenant_id,
                    category=category,
                    title=f"Signal: {category.value.title()}",
                    content=description,
                    strength=self._calculate_strength(description, 1, 1.0),
                    freshness=self._calculate_freshness(),
                    evidence=[evidence],
                    action_suggestion=significance,
                    source_url=source_url
                )
                signals.append(signal)

        except Exception as e:
            logger.error(f"LLM signal extraction failed: {e}")
            # Fallback to pattern matching
            signals = self._extract_pattern_signals(content, source_url, evidence, tenant_id)

        return signals

    def _detect_content_changes(self, old_content: str, new_content: str) -> List[Tuple[str, str]]:
        """Detect and categorize content changes."""
        changes = []
        
        # Split content into sections for comparison
        old_sections = self._split_content(old_content)
        new_sections = self._split_content(new_content)
        
        # Find added/modified sections
        for section in new_sections:
            if section not in old_sections:
                # New content detected
                if any(pattern in section.lower() for patterns in self.signal_patterns.values() for pattern in patterns):
                    changes.append(("new_content", section))
        
        # Find removed sections
        for section in old_sections:
            if section not in new_sections:
                # Removed content detected
                if any(pattern in section.lower() for patterns in self.signal_patterns.values() for pattern in patterns):
                    changes.append(("removed_content", section))
        
        return changes

    def _split_content(self, content: str) -> List[str]:
        """Split content into meaningful sections."""
        # Split by paragraphs and major headings
        sections = []
        
        # Split by double newlines (paragraphs)
        paragraphs = content.split('\n\n')
        
        for paragraph in paragraphs:
            paragraph = paragraph.strip()
            if len(paragraph) > 50:  # Only keep substantial paragraphs
                sections.append(paragraph)
        
        return sections

    def _categorize_content(self, content: str) -> Optional[SignalCategory]:
        """Categorize content based on pattern matching."""
        content_lower = content.lower()
        
        for category, patterns in self.signal_patterns.items():
            for pattern in patterns:
                if re.search(pattern, content_lower):
                    return category
        
        return None

    async def _create_signal_from_content(
        self,
        content: str,
        category: SignalCategory,
        source_url: str,
        evidence: Evidence,
        tenant_id: str
    ) -> Optional[Signal]:
        """Create a signal from content."""
        try:
            # Generate action suggestion using LLM
            prompt = f"""
            Analyze this competitive signal and suggest an action:
            
            Signal: {content}
            Category: {category.value}
            
            Suggest a specific, actionable response (max 50 words).
            """
            
            response = await self.llm.ainvoke(prompt)
            action_suggestion = response.content.strip()[:200]
            
            signal = Signal(
                tenant_id=tenant_id,
                category=category,
                title=f"{category.value.title()}: {content[:50]}...",
                content=content,
                strength=self._calculate_strength(content, 1, 0.8),
                freshness=self._calculate_freshness(),
                evidence=[evidence],
                action_suggestion=action_suggestion,
                source_url=source_url
            )
            
            return signal

        except Exception as e:
            logger.error(f"Error creating signal: {e}")
            return None

    def _extract_pattern_signals(
        self,
        content: str,
        source_url: str,
        evidence: Evidence,
        tenant_id: str
    ) -> List[Signal]:
        """Fallback pattern-based signal extraction."""
        signals = []
        
        for category, patterns in self.signal_patterns.items():
            for pattern in patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                
                for match in matches:
                    # Extract context around the match
                    start = max(0, match.start() - 100)
                    end = min(len(content), match.end() + 100)
                    context = content[start:end].strip()
                    
                    signal = Signal(
                        tenant_id=tenant_id,
                        category=category,
                        title=f"{category.value.title()}: Pattern Match",
                        content=context,
                        strength=self._calculate_strength(context, 1, 0.6),
                        freshness=self._calculate_freshness(),
                        evidence=[evidence],
                        source_url=source_url
                    )
                    signals.append(signal)
        
        return signals

    def _calculate_strength(
        self, 
        content: str, 
        evidence_count: int, 
        confidence: float
    ) -> SignalStrength:
        """Calculate signal strength based on evidence and confidence."""
        # Evidence weight (max 0.6)
        evidence_weight = min(evidence_count * 0.2, 0.6)
        
        # Confidence weight (max 0.4)
        confidence_weight = confidence * 0.4
        
        # Content quality factors
        content_length = len(content)
        length_weight = min(content_length / 1000, 0.2)
        
        # Calculate total score
        total_score = evidence_weight + confidence_weight + length_weight
        
        if total_score >= 0.7:
            return SignalStrength.HIGH
        elif total_score >= 0.4:
            return SignalStrength.MEDIUM
        else:
            return SignalStrength.LOW

    def _calculate_freshness(self, created_at: Optional[datetime] = None) -> SignalFreshness:
        """Calculate signal freshness based on age."""
        if created_at is None:
            created_at = datetime.utcnow()
        
        age = datetime.utcnow() - created_at
        
        if age.days <= 7:
            return SignalFreshness.FRESH
        elif age.days <= 30:
            return SignalFreshness.WARM
        else:
            return SignalFreshness.STALE

    def _parse_llm_response(self, response: str) -> List[Dict[str, Any]]:
        """Parse LLM response for signal data."""
        try:
            import json
            
            # Extract JSON from response
            if "```json" in response:
                json_str = response.split("```json")[1].split("```")[0]
            elif "```" in response:
                json_str = response.split("```")[1].split("```")[0]
            else:
                json_str = response
            
            return json.loads(json_str)
            
        except Exception as e:
            logger.error(f"Failed to parse LLM response: {e}")
            return []
