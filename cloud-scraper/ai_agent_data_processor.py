"""
AI Agent Data Processing Pipeline - Optimal Format for Post-Scrape Intelligence
"""

import asyncio
import json
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from enum import Enum
from typing import Any, Dict, List, Optional


class DataFormat(Enum):
    """Optimal data formats for AI agent processing"""

    STRUCTURED_JSON = "structured_json"
    KNOWLEDGE_GRAPH = "knowledge_graph"
    VECTOR_EMBEDDINGS = "vector_embeddings"
    SEMANTIC_CHUNKS = "semantic_chunks"
    BUSINESS_INTELLIGENCE = "business_intelligence"


@dataclass
class ScrapedData:
    """Standardized scraped data structure"""

    url: str
    timestamp: datetime
    title: str
    content: str
    metadata: Dict[str, Any]
    business_context: Dict[str, Any]
    extracted_entities: Dict[str, List[str]]
    semantic_analysis: Dict[str, Any]
    performance_metrics: Dict[str, Any]


class AIAgentDataProcessor:
    """Optimal data processor for AI agent consumption"""

    def __init__(self):
        self.processing_formats = [
            DataFormat.STRUCTURED_JSON,
            DataFormat.KNOWLEDGE_GRAPH,
            DataFormat.VECTOR_EMBEDDINGS,
            DataFormat.SEMANTIC_CHUNKS,
            DataFormat.BUSINESS_INTELLIGENCE,
        ]

    async def process_scraped_data(
        self, raw_scrape_result: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Process scraped data into optimal AI agent formats"""

        # Create standardized data structure
        scraped_data = ScrapedData(
            url=raw_scrape_result.get("url", ""),
            timestamp=datetime.now(timezone.utc),
            title=raw_scrape_result.get("title", ""),
            content=raw_scrape_result.get("readable_text", ""),
            metadata=self._extract_metadata(raw_scrape_result),
            business_context=self._extract_business_context(raw_scrape_result),
            extracted_entities=self._extract_entities(raw_scrape_result),
            semantic_analysis=self._perform_semantic_analysis(raw_scrape_result),
            performance_metrics=self._extract_performance_metrics(raw_scrape_result),
        )

        # Process into all optimal formats
        processed_data = {
            "structured_json": self._create_structured_json(scraped_data),
            "knowledge_graph": self._create_knowledge_graph(scraped_data),
            "vector_embeddings": self._create_vector_embeddings(scraped_data),
            "semantic_chunks": self._create_semantic_chunks(scraped_data),
            "business_intelligence": self._create_business_intelligence(scraped_data),
            "agent_ready_summary": self._create_agent_summary(scraped_data),
        }

        return processed_data

    def _extract_metadata(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract structured metadata"""
        return {
            "content_length": raw_data.get("content_length", 0),
            "processing_time": raw_data.get("processing_time", 0),
            "strategy_used": raw_data.get("strategy_used", "unknown"),
            "links_count": len(raw_data.get("links", [])),
            "scrape_timestamp": raw_data.get("timestamp", ""),
            "cost": raw_data.get("ultra_cost", {}).get("estimated_cost", 0),
            "success_status": raw_data.get("status", "unknown"),
            "language": "en",  # Would be detected in production
            "content_type": "text/html",
            "domain": self._extract_domain(raw_data.get("url", "")),
        }

    def _extract_business_context(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract business-relevant context"""
        content = raw_data.get("readable_text", "").lower()

        # Business type detection
        business_types = {
            "food_beverage": ["food", "beverage", "restaurant", "snack", "drink"],
            "technology": ["technology", "software", "digital", "tech", "innovation"],
            "manufacturing": ["manufacturing", "production", "industrial", "factory"],
            "services": ["services", "solutions", "consulting", "professional"],
            "retail": ["retail", "store", "shop", "consumer", "product"],
            "healthcare": ["healthcare", "medical", "pharmaceutical", "health"],
            "finance": ["finance", "banking", "insurance", "investment"],
        }

        detected_types = []
        for btype, keywords in business_types.items():
            if any(keyword in content for keyword in keywords):
                detected_types.append(btype)

        # Company characteristics
        characteristics = []
        if "global" in content or "worldwide" in content:
            characteristics.append("global_presence")
        if "innov" in content:
            characteristics.append("innovation_focused")
        if "sustain" in content:
            characteristics.append("sustainability_focused")
        if "quality" in content:
            characteristics.append("quality_focused")
        if "customer" in content:
            characteristics.append("customer_centric")
        if "franchise" in content:
            characteristics.append("franchise_model")

        return {
            "business_types": detected_types,
            "characteristics": characteristics,
            "company_size": self._estimate_company_size(content),
            "market_focus": self._estimate_market_focus(content),
            "value_proposition": self._extract_value_proposition(content),
            "target_audience": self._estimate_target_audience(content),
        }

    def _extract_entities(self, raw_data: Dict[str, Any]) -> Dict[str, List[str]]:
        """Extract named entities for AI processing"""
        content = raw_data.get("readable_text", "")

        # In production, would use NLP libraries like spaCy
        # For now, extract basic entities
        import re

        entities = {
            "emails": list(
                set(
                    re.findall(
                        r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", content
                    )
                )
            ),
            "phones": list(set(re.findall(r"\b\d{3}[-.]?\d{3}[-.]?\d{4}\b", content))),
            "social_media": [],
            "products": [],
            "locations": [],
            "organizations": [],
            "people": [],
            "technologies": [],
        }

        # Extract social media links
        links = raw_data.get("links", [])
        for link in links:
            url = link.get("url", "").lower()
            if any(
                social in url
                for social in [
                    "facebook",
                    "twitter",
                    "linkedin",
                    "instagram",
                    "youtube",
                ]
            ):
                entities["social_media"].append(url)

        # Extract common business terms
        business_terms = [
            "ceo",
            "cto",
            "cfo",
            "director",
            "manager",
            "team",
            "department",
        ]
        for term in business_terms:
            if term in content.lower():
                entities["organizations"].append(term)

        return {k: list(set(v)) for k, v in entities.items()}

    def _perform_semantic_analysis(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Perform semantic analysis for AI understanding"""
        content = raw_data.get("readable_text", "")

        # Sentiment analysis (simplified)
        positive_words = [
            "innovative",
            "quality",
            "excellent",
            "leading",
            "global",
            "sustainable",
        ]
        negative_words = ["problem", "issue", "challenge", "difficult", "complex"]

        positive_count = sum(1 for word in positive_words if word in content.lower())
        negative_count = sum(1 for word in negative_words if word in content.lower())

        sentiment_score = (positive_count - negative_count) / max(
            positive_count + negative_count, 1
        )

        # Topic modeling (simplified)
        topics = {
            "innovation": ["innov", "technology", "digital", "future"],
            "sustainability": ["sustain", "environment", "green", "eco"],
            "quality": ["quality", "excellence", "premium", "best"],
            "growth": ["growth", "expansion", "global", "worldwide"],
            "customer": ["customer", "client", "service", "experience"],
        }

        detected_topics = []
        for topic, keywords in topics.items():
            if any(keyword in content.lower() for keyword in keywords):
                detected_topics.append(topic)

        return {
            "sentiment_score": max(-1, min(1, sentiment_score)),
            "sentiment_label": (
                "positive"
                if sentiment_score > 0.1
                else "negative" if sentiment_score < -0.1 else "neutral"
            ),
            "topics": detected_topics,
            "complexity_score": len(content.split()) / 1000,  # Simplified complexity
            "readability_score": 100
            - (len(content.split()) / 100),  # Simplified readability
            "key_phrases": self._extract_key_phrases(content),
            "summary": self._generate_summary(content),
        }

    def _extract_performance_metrics(self, raw_data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract performance metrics for optimization"""
        return {
            "processing_time": raw_data.get("processing_time", 0),
            "cost": raw_data.get("ultra_cost", {}).get("estimated_cost", 0),
            "speed_score": raw_data.get("ultra_performance", {}).get("speed_score", 0),
            "success_rate": 1.0 if raw_data.get("status") == "success" else 0.0,
            "content_quality": self._assess_content_quality(raw_data),
            "data_completeness": self._assess_data_completeness(raw_data),
            "efficiency_score": self._calculate_efficiency_score(raw_data),
        }

    def _create_structured_json(self, data: ScrapedData) -> Dict[str, Any]:
        """Create structured JSON format for AI agents"""
        return {
            "source": {
                "url": data.url,
                "timestamp": data.timestamp.isoformat(),
                "title": data.title,
                "domain": self._extract_domain(data.url),
            },
            "content": {
                "full_text": data.content,
                "length": len(data.content),
                "language": data.metadata.get("language", "en"),
                "format": "text",
            },
            "business_context": data.business_context,
            "entities": data.extracted_entities,
            "semantic_analysis": data.semantic_analysis,
            "metadata": data.metadata,
            "performance": data.performance_metrics,
            "processing_info": {
                "format_version": "1.0",
                "processor": "AI_Agent_Data_Processor",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    def _create_knowledge_graph(self, data: ScrapedData) -> Dict[str, Any]:
        """Create knowledge graph format for AI reasoning"""
        return {
            "nodes": [
                {
                    "id": "company",
                    "type": "organization",
                    "properties": {
                        "name": data.title,
                        "url": data.url,
                        "business_types": data.business_context.get(
                            "business_types", []
                        ),
                        "characteristics": data.business_context.get(
                            "characteristics", []
                        ),
                    },
                },
                {
                    "id": "content",
                    "type": "document",
                    "properties": {
                        "title": data.title,
                        "length": len(data.content),
                        "topics": data.semantic_analysis.get("topics", []),
                        "sentiment": data.semantic_analysis.get(
                            "sentiment_label", "neutral"
                        ),
                    },
                },
            ],
            "relationships": [
                {
                    "source": "company",
                    "target": "content",
                    "type": "HAS_CONTENT",
                    "properties": {
                        "timestamp": data.timestamp.isoformat(),
                        "content_type": "web_page",
                    },
                }
            ],
            "graph_metadata": {
                "format": "knowledge_graph",
                "version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
            },
        }

    def _create_vector_embeddings(self, data: ScrapedData) -> Dict[str, Any]:
        """Create vector embeddings format for ML/AI processing"""
        # In production, would use actual embedding models
        return {
            "text_embeddings": {
                "content_vector": [0.1] * 384,  # Placeholder for actual embeddings
                "title_vector": [0.2] * 384,
                "summary_vector": [0.15] * 384,
                "model": "sentence-transformers/all-MiniLM-L6-v2",
                "dimension": 384,
            },
            "metadata_embeddings": {
                "business_type_vector": [0.3] * 128,
                "topic_vector": [0.25] * 128,
                "sentiment_vector": [data.semantic_analysis.get("sentiment_score", 0)],
                "model": "custom_business_encoder",
                "dimension": 128,
            },
            "embedding_metadata": {
                "format": "vector_embeddings",
                "version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "total_vectors": 4,
            },
        }

    def _create_semantic_chunks(self, data: ScrapedData) -> Dict[str, Any]:
        """Create semantic chunks for contextual AI processing"""
        content = data.content
        chunk_size = 500  # characters
        overlap = 50  # characters

        chunks = []
        for i in range(0, len(content), chunk_size - overlap):
            chunk_text = content[i : i + chunk_size]
            if len(chunk_text) > 100:  # Only include meaningful chunks
                chunks.append(
                    {
                        "chunk_id": f"chunk_{i // (chunk_size - overlap)}",
                        "text": chunk_text,
                        "start_position": i,
                        "end_position": min(i + chunk_size, len(content)),
                        "word_count": len(chunk_text.split()),
                        "entities": self._extract_chunk_entities(chunk_text),
                        "topics": self._extract_chunk_topics(chunk_text),
                        "sentiment": self._analyze_chunk_sentiment(chunk_text),
                    }
                )

        return {
            "chunks": chunks,
            "chunking_metadata": {
                "strategy": "fixed_size_with_overlap",
                "chunk_size": chunk_size,
                "overlap": overlap,
                "total_chunks": len(chunks),
                "format": "semantic_chunks",
                "version": "1.0",
            },
        }

    def _create_business_intelligence(self, data: ScrapedData) -> Dict[str, Any]:
        """Create business intelligence format for strategic AI agents"""
        return {
            "company_profile": {
                "name": data.title,
                "domain": self._extract_domain(data.url),
                "business_types": data.business_context.get("business_types", []),
                "characteristics": data.business_context.get("characteristics", []),
                "estimated_size": data.business_context.get("company_size", "unknown"),
                "market_focus": data.business_context.get("market_focus", "unknown"),
            },
            "strategic_insights": {
                "value_proposition": data.business_context.get("value_proposition", ""),
                "competitive_advantages": data.business_context.get(
                    "characteristics", []
                ),
                "target_markets": data.business_context.get("target_audience", []),
                "growth_indicators": self._extract_growth_indicators(data.content),
                "innovation_signals": self._extract_innovation_signals(data.content),
            },
            "operational_intelligence": {
                "digital_presence": {
                    "website_quality": self._assess_website_quality(data),
                    "social_media_presence": len(
                        data.extracted_entities.get("social_media", [])
                    ),
                    "contact_channels": len(data.extracted_entities.get("emails", []))
                    + len(data.extracted_entities.get("phones", [])),
                },
                "content_strategy": {
                    "primary_topics": data.semantic_analysis.get("topics", []),
                    "sentiment_tone": data.semantic_analysis.get(
                        "sentiment_label", "neutral"
                    ),
                    "content_complexity": data.semantic_analysis.get(
                        "complexity_score", 0
                    ),
                    "key_messages": data.semantic_analysis.get("key_phrases", []),
                },
            },
            "performance_metrics": data.performance_metrics,
            "bi_metadata": {
                "format": "business_intelligence",
                "version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "confidence_score": self._calculate_confidence_score(data),
            },
        }

    def _create_agent_summary(self, data: ScrapedData) -> Dict[str, Any]:
        """Create agent-ready summary for quick AI processing"""
        return {
            "quick_facts": {
                "company_name": data.title,
                "url": data.url,
                "business_type": data.business_context.get(
                    "business_types", ["unknown"]
                ),
                "main_characteristics": data.business_context.get(
                    "characteristics", []
                ),
                "key_topics": data.semantic_analysis.get("topics", []),
                "sentiment": data.semantic_analysis.get("sentiment_label", "neutral"),
            },
            "actionable_insights": {
                "business_model": self._infer_business_model(data),
                "market_position": self._infer_market_position(data),
                "growth_potential": self._assess_growth_potential(data),
                "partnership_opportunities": self._identify_partnership_opportunities(
                    data
                ),
                "competitive_threats": self._identify_competitive_threats(data),
            },
            "recommendations": {
                "follow_up_actions": self._suggest_follow_up_actions(data),
                "data_enrichment_needs": self._identify_data_gaps(data),
                "monitoring_points": self._suggest_monitoring_points(data),
            },
            "summary_metadata": {
                "format": "agent_summary",
                "version": "1.0",
                "created_at": datetime.now(timezone.utc).isoformat(),
                "processing_confidence": self._calculate_confidence_score(data),
            },
        }

    # Helper methods (simplified implementations)
    def _extract_domain(self, url: str) -> str:
        from urllib.parse import urlparse

        try:
            return urlparse(url).netloc
        except:
            return "unknown"

    def _estimate_company_size(self, content: str) -> str:
        if "global" in content.lower() or "worldwide" in content.lower():
            return "enterprise"
        elif "team" in content.lower() or "small" in content.lower():
            return "small"
        else:
            return "medium"

    def _estimate_market_focus(self, content: str) -> str:
        if "global" in content.lower() or "international" in content.lower():
            return "global"
        elif "local" in content.lower() or "community" in content.lower():
            return "local"
        else:
            return "regional"

    def _extract_value_proposition(self, content: str) -> str:
        # Simplified extraction - would use NLP in production
        sentences = content.split(".")
        for sentence in sentences:
            if any(
                word in sentence.lower()
                for word in ["provide", "offer", "deliver", "create"]
            ):
                return sentence.strip()[:200]
        return ""

    def _estimate_target_audience(self, content: str) -> List[str]:
        audiences = []
        content_lower = content.lower()
        if "consumer" in content_lower or "customer" in content_lower:
            audiences.append("consumers")
        if "business" in content_lower or "enterprise" in content_lower:
            audiences.append("businesses")
        if "partner" in content_lower:
            audiences.append("partners")
        return audiences

    def _extract_key_phrases(self, content: str) -> List[str]:
        # Simplified key phrase extraction
        import re

        sentences = content.split(".")
        key_phrases = []
        for sentence in sentences[:10]:  # First 10 sentences
            words = sentence.strip().split()
            if len(words) > 5 and len(words) < 15:
                key_phrases.append(sentence.strip())
        return key_phrases[:5]

    def _generate_summary(self, content: str) -> str:
        # Simplified summary generation
        sentences = content.split(".")
        return ". ".join(sentences[:3]) + "."

    def _assess_content_quality(self, raw_data: Dict[str, Any]) -> float:
        content_length = raw_data.get("content_length", 0)
        readable_length = len(raw_data.get("readable_text", ""))
        return min(readable_length / max(content_length, 1), 1.0)

    def _assess_data_completeness(self, raw_data: Dict[str, Any]) -> float:
        fields = ["title", "content", "links", "readable_text"]
        complete_fields = sum(1 for field in fields if raw_data.get(field))
        return complete_fields / len(fields)

    def _calculate_efficiency_score(self, raw_data: Dict[str, Any]) -> float:
        processing_time = raw_data.get("processing_time", 1)
        content_length = raw_data.get("content_length", 1)
        return min(content_length / (processing_time * 1000), 1.0)

    def _extract_chunk_entities(self, chunk: str) -> List[str]:
        # Simplified entity extraction for chunks
        import re

        emails = re.findall(
            r"\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b", chunk
        )
        return emails

    def _extract_chunk_topics(self, chunk: str) -> List[str]:
        # Simplified topic extraction for chunks
        topics = {
            "business": ["business", "company", "service", "product"],
            "technology": ["tech", "software", "digital", "innovation"],
            "quality": ["quality", "excellence", "best", "premium"],
        }
        detected = []
        chunk_lower = chunk.lower()
        for topic, keywords in topics.items():
            if any(keyword in chunk_lower for keyword in keywords):
                detected.append(topic)
        return detected

    def _analyze_chunk_sentiment(self, chunk: str) -> str:
        positive = ["good", "great", "excellent", "innovative", "quality"]
        negative = ["bad", "poor", "problem", "issue", "difficult"]
        chunk_lower = chunk.lower()

        pos_count = sum(1 for word in positive if word in chunk_lower)
        neg_count = sum(1 for word in negative if word in chunk_lower)

        if pos_count > neg_count:
            return "positive"
        elif neg_count > pos_count:
            return "negative"
        else:
            return "neutral"

    def _extract_growth_indicators(self, content: str) -> List[str]:
        indicators = []
        content_lower = content.lower()
        if "growth" in content_lower:
            indicators.append("growth_mentioned")
        if "expansion" in content_lower:
            indicators.append("expansion_plans")
        if "new" in content_lower:
            indicators.append("new_initiatives")
        return indicators

    def _extract_innovation_signals(self, content: str) -> List[str]:
        signals = []
        content_lower = content.lower()
        if "innov" in content_lower:
            signals.append("innovation_focus")
        if "technology" in content_lower:
            signals.append("technology_driven")
        if "research" in content_lower:
            signals.append("research_investment")
        return signals

    def _assess_website_quality(self, data: ScrapedData) -> float:
        # Simplified quality assessment
        score = 0.0
        if data.title and len(data.title) > 5:
            score += 0.3
        if len(data.content) > 1000:
            score += 0.3
        if len(data.extracted_entities.get("links", [])) > 5:
            score += 0.2
        if data.extracted_entities.get("emails"):
            score += 0.2
        return score

    def _infer_business_model(self, data: ScrapedData) -> str:
        content = data.content.lower()
        if "franchise" in content:
            return "franchise"
        elif "subscription" in content:
            return "subscription"
        elif "retail" in content:
            return "retail"
        else:
            return "traditional"

    def _infer_market_position(self, data: ScrapedData) -> str:
        content = data.content.lower()
        if "leading" in content or "leader" in content:
            return "market_leader"
        elif "innov" in content:
            return "innovator"
        else:
            return "participant"

    def _assess_growth_potential(self, data: ScrapedData) -> str:
        indicators = self._extract_growth_indicators(data.content)
        if len(indicators) >= 2:
            return "high"
        elif len(indicators) >= 1:
            return "medium"
        else:
            return "low"

    def _identify_partnership_opportunities(self, data: ScrapedData) -> List[str]:
        opportunities = []
        content = data.content.lower()
        if "partner" in content:
            opportunities.append("partnership_program")
        if "collabor" in content:
            opportunities.append("collaboration_opportunities")
        return opportunities

    def _identify_competitive_threats(self, data: ScrapedData) -> List[str]:
        # Simplified - would use competitive analysis in production
        return []

    def _suggest_follow_up_actions(self, data: ScrapedData) -> List[str]:
        actions = []
        if not data.extracted_entities.get("emails"):
            actions.append("extract_contact_information")
        if len(data.content) < 1000:
            actions.append("deep_scrape_for_more_content")
        return actions

    def _identify_data_gaps(self, data: ScrapedData) -> List[str]:
        gaps = []
        if not data.business_context.get("business_types"):
            gaps.append("business_classification")
        if not data.extracted_entities.get("social_media"):
            gaps.append("social_media_profiles")
        return gaps

    def _suggest_monitoring_points(self, data: ScrapedData) -> List[str]:
        points = ["content_changes", "new_products", "leadership_changes"]
        if "innovation" in data.content.lower():
            points.append("innovation_updates")
        return points

    def _calculate_confidence_score(self, data: ScrapedData) -> float:
        # Simplified confidence calculation
        score = 0.0
        if data.title:
            score += 0.2
        if len(data.content) > 500:
            score += 0.3
        if data.business_context.get("business_types"):
            score += 0.2
        if data.semantic_analysis.get("topics"):
            score += 0.2
        if data.extracted_entities.get("emails"):
            score += 0.1
        return score


# Example usage and demonstration
async def demonstrate_ai_agent_processing():
    """Demonstrate how AI agents would use the processed data"""

    processor = AIAgentDataProcessor()

    # Example scraped data (simulated)
    example_scrape_result = {
        "url": "https://www.pepsico.com/en/",
        "title": "PepsiCo | Food and Drinks to Smile About",
        "status": "success",
        "processing_time": 1.23,
        "content_length": 281176,
        "readable_text": "About usDiscover how we use our global reach to spark joy & smiles...",
        "links": [
            {"url": "https://externalinnovation.pepsico.com/", "text": "Submit Ideas"},
            {"url": "https://design.pepsico.com/", "text": "PepsiCo Design"},
        ],
        "strategy_used": "async",
        "timestamp": "2026-01-02T12:00:00Z",
        "ultra_cost": {"estimated_cost": 0.000061},
        "ultra_performance": {"speed_score": 100.0},
    }

    # Process the data
    processed_data = await processor.process_scraped_data(example_scrape_result)

    print("🤖 AI Agent Data Processing Demonstration")
    print("=" * 50)

    # Show how different AI agents would use different formats
    print("\n📊 1. Business Intelligence Agent Usage:")
    bi_data = processed_data["business_intelligence"]
    print(f'   Company: {bi_data["company_profile"]["name"]}')
    print(f'   Business Type: {bi_data["company_profile"]["business_types"]}')
    print(
        f'   Market Position: {bi_data["strategic_insights"]["competitive_advantages"]}'
    )

    print("\n🔍 2. Knowledge Graph Agent Usage:")
    kg_data = processed_data["knowledge_graph"]
    print(f'   Nodes: {len(kg_data["nodes"])}')
    print(f'   Relationships: {len(kg_data["relationships"])}')
    print(f'   Company Node: {kg_data["nodes"][0]["properties"]["business_types"]}')

    print("\n📝 3. Semantic Analysis Agent Usage:")
    semantic_data = processed_data["semantic_chunks"]
    print(f'   Total Chunks: {semantic_data["chunking_metadata"]["total_chunks"]}')
    if semantic_data["chunks"]:
        print(f'   First Chunk Topics: {semantic_data["chunks"][0]["topics"]}')
        print(f'   First Chunk Sentiment: {semantic_data["chunks"][0]["sentiment"]}')

    print("\n🎯 4. Quick Decision Agent Usage:")
    summary_data = processed_data["agent_ready_summary"]
    print(f'   Business Model: {summary_data["actionable_insights"]["business_model"]}')
    print(
        f'   Growth Potential: {summary_data["actionable_insights"]["growth_potential"]}'
    )
    print(
        f'   Recommended Actions: {summary_data["recommendations"]["follow_up_actions"]}'
    )

    print("\n💾 5. Vector Search Agent Usage:")
    vector_data = processed_data["vector_embeddings"]
    print(
        f'   Content Embedding Dimension: {vector_data["text_embeddings"]["dimension"]}'
    )
    print(f'   Total Vectors: {vector_data["embedding_metadata"]["total_vectors"]}')
    print(f'   Model Used: {vector_data["text_embeddings"]["model"]}')

    print("\n🎉 AI Agent Processing Complete!")
    print("All formats are optimized for different AI agent types:")
    print("• Business Intelligence: Strategic analysis")
    print("• Knowledge Graph: Relationship mapping")
    print("• Semantic Chunks: Contextual understanding")
    print("• Vector Embeddings: Similarity search")
    print("• Agent Summary: Quick decision making")


if __name__ == "__main__":
    asyncio.run(demonstrate_ai_agent_processing())
