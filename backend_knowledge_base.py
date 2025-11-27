# backend/knowledge_base.py
# RaptorFlow Codex - Knowledge Base Management
# Week 3 Wednesday - Document Templates & Knowledge Organization

from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from datetime import datetime
from enum import Enum
import logging

logger = logging.getLogger(__name__)

# ============================================================================
# KNOWLEDGE CATEGORIES
# ============================================================================

class KnowledgeCategory(str, Enum):
    """Knowledge base document categories"""
    CAMPAIGN = "campaign"
    STRATEGY = "strategy"
    RESEARCH = "research"
    TEMPLATE = "template"
    GUIDELINE = "guideline"
    CASE_STUDY = "case_study"
    TOOL = "tool"
    API = "api"
    BEST_PRACTICE = "best_practice"
    COMPETITOR_ANALYSIS = "competitor_analysis"

# ============================================================================
# KNOWLEDGE TEMPLATES
# ============================================================================

@dataclass
class KnowledgeTemplate:
    """Template for knowledge documents"""
    name: str
    category: KnowledgeCategory
    description: str
    structure: Dict[str, str]
    tags: List[str]
    required_fields: List[str]

class KnowledgeTemplates:
    """Pre-built knowledge document templates"""

    CAMPAIGN_TEMPLATE = KnowledgeTemplate(
        name="Campaign Brief",
        category=KnowledgeCategory.CAMPAIGN,
        description="Template for campaign planning documents",
        structure={
            "overview": "Campaign overview and objectives",
            "target_audience": "Audience segments and personas",
            "messaging": "Key messages and value propositions",
            "channels": "Distribution channels and tactics",
            "timeline": "Campaign timeline and milestones",
            "budget": "Budget allocation and resource planning",
            "metrics": "Success metrics and KPIs"
        },
        tags=["campaign", "planning", "marketing"],
        required_fields=["overview", "target_audience", "messaging"]
    )

    STRATEGY_TEMPLATE = KnowledgeTemplate(
        name="Strategic Plan",
        category=KnowledgeCategory.STRATEGY,
        description="Template for strategic planning documents",
        structure={
            "situation_analysis": "Market and competitive analysis",
            "goals": "Strategic goals and objectives",
            "positioning": "Brand positioning statement",
            "tactics": "Strategic tactics and initiatives",
            "timeline": "Implementation timeline",
            "success_criteria": "Measures of success",
            "risks": "Risk assessment and mitigation"
        },
        tags=["strategy", "planning", "business"],
        required_fields=["situation_analysis", "goals", "positioning"]
    )

    RESEARCH_TEMPLATE = KnowledgeTemplate(
        name="Research Report",
        category=KnowledgeCategory.RESEARCH,
        description="Template for research findings",
        structure={
            "research_question": "The research question",
            "methodology": "Research methodology",
            "findings": "Key findings",
            "analysis": "Analysis and interpretation",
            "conclusions": "Conclusions",
            "recommendations": "Recommended actions",
            "sources": "Research sources and citations"
        },
        tags=["research", "analysis", "insights"],
        required_fields=["research_question", "methodology", "findings"]
    )

    GUIDELINE_TEMPLATE = KnowledgeTemplate(
        name="Brand Guideline",
        category=KnowledgeCategory.GUIDELINE,
        description="Template for brand and content guidelines",
        structure={
            "scope": "Guideline scope and applicability",
            "principles": "Core principles and values",
            "dos": "Do's and best practices",
            "donts": "Don'ts and anti-patterns",
            "examples": "Examples of correct usage",
            "exceptions": "Exceptions and special cases",
            "approval": "Approval process and contacts"
        },
        tags=["guidelines", "standards", "brand"],
        required_fields=["scope", "principles", "dos", "donts"]
    )

    CASE_STUDY_TEMPLATE = KnowledgeTemplate(
        name="Case Study",
        category=KnowledgeCategory.CASE_STUDY,
        description="Template for case studies",
        structure={
            "situation": "Initial situation and challenge",
            "approach": "Approach and solution",
            "implementation": "Implementation details",
            "results": "Results and outcomes",
            "metrics": "Quantified metrics and ROI",
            "lessons_learned": "Key lessons and takeaways",
            "applicability": "How to apply to similar situations"
        },
        tags=["case_study", "success", "learning"],
        required_fields=["situation", "approach", "results"]
    )

    TEMPLATES = {
        KnowledgeCategory.CAMPAIGN: CAMPAIGN_TEMPLATE,
        KnowledgeCategory.STRATEGY: STRATEGY_TEMPLATE,
        KnowledgeCategory.RESEARCH: RESEARCH_TEMPLATE,
        KnowledgeCategory.GUIDELINE: GUIDELINE_TEMPLATE,
        KnowledgeCategory.CASE_STUDY: CASE_STUDY_TEMPLATE,
    }

    @staticmethod
    def get_template(category: KnowledgeCategory) -> Optional[KnowledgeTemplate]:
        """Get template for category"""
        return KnowledgeTemplates.TEMPLATES.get(category)

    @staticmethod
    def get_all_templates() -> List[KnowledgeTemplate]:
        """Get all templates"""
        return list(KnowledgeTemplates.TEMPLATES.values())

# ============================================================================
# KNOWLEDGE DOCUMENT MANAGER
# ============================================================================

class KnowledgeBaseManager:
    """Manages knowledge base documents and organization"""

    def __init__(self, chroma_rag):
        """Initialize knowledge base manager"""
        self.chroma_rag = chroma_rag
        self.document_index: Dict[str, Dict[str, Any]] = {}

    async def create_document(
        self,
        title: str,
        content: str,
        category: KnowledgeCategory,
        workspace_id: str,
        owner_id: str,
        tags: List[str] = None,
        metadata: Dict[str, Any] = None
    ) -> str:
        """
        Create knowledge document.

        Args:
            title: Document title
            content: Document content
            category: Document category
            workspace_id: Workspace context
            owner_id: Document owner
            tags: Document tags
            metadata: Additional metadata

        Returns:
            Document ID
        """
        from chroma_db import Document
        import uuid

        doc_id = str(uuid.uuid4())

        document = Document(
            id=doc_id,
            title=title,
            content=content,
            category=category.value,
            metadata={
                "tags": tags or [],
                "version": 1,
                **(metadata or {})
            },
            created_at=datetime.utcnow().isoformat(),
            updated_at=datetime.utcnow().isoformat(),
            workspace_id=workspace_id,
            owner_id=owner_id
        )

        # Add to RAG system
        await self.chroma_rag.add_document(document)

        # Index document
        self.document_index[doc_id] = {
            "title": title,
            "category": category.value,
            "tags": tags or [],
            "workspace_id": workspace_id,
            "owner_id": owner_id
        }

        logger.info(f"📝 Knowledge document created: {title} ({doc_id})")
        return doc_id

    async def create_from_template(
        self,
        template_name: str,
        title: str,
        content_sections: Dict[str, str],
        workspace_id: str,
        owner_id: str,
        tags: List[str] = None
    ) -> str:
        """
        Create document from template.

        Args:
            template_name: Template to use
            title: Document title
            content_sections: Sections filled in from template
            workspace_id: Workspace context
            owner_id: Document owner
            tags: Document tags

        Returns:
            Document ID
        """
        # Find template
        template = None
        for t in KnowledgeTemplates.get_all_templates():
            if t.name == template_name:
                template = t
                break

        if not template:
            raise ValueError(f"Unknown template: {template_name}")

        # Validate required fields
        for required in template.required_fields:
            if required not in content_sections:
                raise ValueError(f"Missing required field: {required}")

        # Build content from template structure
        content_parts = []
        for key, description in template.structure.items():
            if key in content_sections:
                content_parts.append(f"## {key.replace('_', ' ').title()}\n{content_sections[key]}")

        full_content = "\n\n".join(content_parts)

        # Create document
        return await self.create_document(
            title=title,
            content=full_content,
            category=template.category,
            workspace_id=workspace_id,
            owner_id=owner_id,
            tags=tags or template.tags,
            metadata={"template": template.name}
        )

    async def get_related_documents(
        self,
        document_id: str,
        workspace_id: str,
        limit: int = 5
    ) -> List[Dict[str, Any]]:
        """
        Get documents related to a document.

        Args:
            document_id: Document to find relations for
            workspace_id: Workspace context
            limit: Max results

        Returns:
            List of related documents
        """
        if document_id not in self.document_index:
            return []

        doc_info = self.document_index[document_id]

        # Find documents with similar tags
        related = []
        doc_tags = set(doc_info.get("tags", []))

        for other_id, other_info in self.document_index.items():
            if other_id == document_id:
                continue
            if other_info.get("workspace_id") != workspace_id:
                continue

            # Calculate tag overlap
            other_tags = set(other_info.get("tags", []))
            overlap = len(doc_tags & other_tags)

            if overlap > 0:
                related.append({
                    "id": other_id,
                    "title": other_info["title"],
                    "category": other_info["category"],
                    "relevance": overlap / (len(doc_tags) + len(other_tags))
                })

        # Sort by relevance
        related.sort(key=lambda x: x["relevance"], reverse=True)
        return related[:limit]

    async def search_documents(
        self,
        query: str,
        workspace_id: str,
        category: Optional[KnowledgeCategory] = None,
        tags: Optional[List[str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Search knowledge base.

        Args:
            query: Search query
            workspace_id: Workspace context
            category: Optional category filter
            tags: Optional tag filter

        Returns:
            Search results
        """
        results = await self.chroma_rag.search(
            query=query,
            workspace_id=workspace_id,
            category=category.value if category else None,
            limit=10
        )

        # Filter by tags if provided
        if tags:
            filtered = []
            for result in results:
                doc_tags = self.document_index.get(
                    result["metadata"].get("document_id", ""),
                    {}
                ).get("tags", [])
                if any(tag in doc_tags for tag in tags):
                    filtered.append(result)
            results = filtered

        return results

    async def get_statistics(self, workspace_id: str) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        stats = await self.chroma_rag.get_statistics(workspace_id)

        # Add index statistics
        workspace_docs = {
            k: v for k, v in self.document_index.items()
            if v.get("workspace_id") == workspace_id
        }

        categories = {}
        for doc in workspace_docs.values():
            cat = doc.get("category", "uncategorized")
            categories[cat] = categories.get(cat, 0) + 1

        return {
            **stats,
            "indexed_documents": len(workspace_docs),
            "categories_in_index": categories,
            "templates_available": len(KnowledgeTemplates.get_all_templates())
        }

# ============================================================================
# INITIAL KNOWLEDGE BASE CONTENT
# ============================================================================

INITIAL_KNOWLEDGE_BASE = [
    {
        "title": "RaptorFlow Marketing Strategy Framework",
        "category": KnowledgeCategory.GUIDELINE,
        "content": """
RaptorFlow uses a multi-channel marketing approach with the following framework:

**Core Principles:**
1. Data-driven decision making
2. Continuous optimization
3. Customer-centric messaging
4. Multi-channel coordination
5. Performance tracking

**Key Components:**
- Audience segmentation and personas
- Message architecture and positioning
- Channel selection and tactics
- Campaign sequencing and timing
- Performance metrics and KPIs

**Best Practices:**
- Always validate assumptions with data
- Test messaging with small segments first
- Optimize based on performance metrics
- Maintain brand consistency across channels
- Document learning and insights
""",
        "tags": ["strategy", "framework", "best-practice"]
    },
    {
        "title": "Content Creation Guidelines",
        "category": KnowledgeCategory.GUIDELINE,
        "content": """
Guidelines for creating marketing content in RaptorFlow:

**Copywriting Principles:**
- Clear, concise language
- Action-oriented messaging
- Benefit-focused (not feature-focused)
- Audience-specific tone and style
- Social proof and credibility signals

**Design Standards:**
- Brand color palette adherence
- Typography hierarchy
- Whitespace and visual balance
- Accessibility compliance
- Mobile-first responsive design

**Quality Checklist:**
- ✓ Grammar and spelling check
- ✓ Brand voice consistency
- ✓ Call-to-action clarity
- ✓ Link validation
- ✓ Compliance review

**Review Process:**
1. Initial creation
2. Internal review (grammar, brand)
3. Compliance check
4. Approval by campaign owner
5. Publication
""",
        "tags": ["content", "guidelines", "quality"]
    },
    {
        "title": "Campaign Performance Metrics",
        "category": KnowledgeCategory.BEST_PRACTICE,
        "content": """
Key metrics for evaluating campaign performance:

**Awareness Metrics:**
- Impressions and reach
- Click-through rate (CTR)
- Cost per impression (CPI)
- Brand awareness lift

**Engagement Metrics:**
- Time on page / Dwell time
- Scroll depth
- Video completion rate
- Social shares and comments

**Conversion Metrics:**
- Conversion rate
- Cost per acquisition (CPA)
- Return on ad spend (ROAS)
- Lifetime value (LTV)

**Brand Metrics:**
- Sentiment analysis
- Brand lift
- Customer satisfaction
- Net promoter score (NPS)

**Dashboard Setup:**
- Real-time monitoring
- Anomaly alerts
- Comparative analysis (vs. benchmarks)
- Attribution modeling
""",
        "tags": ["metrics", "analytics", "performance"]
    }
]

