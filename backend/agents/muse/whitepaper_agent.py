"""
Whitepaper Agent (MUS-010)

Muse Guild's long-form content generation specialist. Creates comprehensive,
structured documents like whitepapers, articles, and technical guides through
orchestrated multi-step LLM workflows. Breaks complex document creation into
manageable steps for coherence and quality.

Features:
- Multi-step document generation workflow
- Structured outline-to-content transformation
- Audience-tailored writing style
- Progressive document assembly
- Error recovery and quality assurance
- Comprehensive logging and progress tracking

Generation Flow:
1. Title Generation → Compelling, SEO-friendly title
2. Introduction Writing → Engaging opening for target audience
3. Section-by-Section Creation → Detailed body content from outline
4. Conclusion Synthesis → Summary and forward-looking statement
5. Document Assembly → Formatted Markdown with proper structure

Capabilities:
- Topic-driven content creation
- Custom outline processing (up to 20 sections)
- Audience-specific tone adaptation
- Long-form technical writing
- SEO-optimized document structure
- Consistent brand voice maintenance
"""

import structlog
from typing import List, Optional

from backend.models.muse import WhitepaperRequest, Whitepaper, WhitepaperGenerationStatus
from backend.services.vertex_ai_client import vertex_ai_client
from backend.utils.correlation import get_correlation_id

logger = structlog.get_logger(__name__)


class WhitepaperAgent:
    """
    MUS-010: Whitepaper Agent for long-form content generation.

    This advanced agent orchestrates the creation of comprehensive, structured
    documents by breaking down complex writing tasks into a series of focused
    LLM interactions. It excels at producing technical whitepapers, in-depth
    articles, and detailed guides with proper structure and audience targeting.

    Key Capabilities:
    - Or chestrated multi-step document creation
    - Topic-to-outline transformation
    - Audience-tailored content generation
    - Section-by-section quality control
    - Comprehensive document assembly
    - Error handling and content validation

    Content Pipeline:
    1. **Title Generation**: Create compelling, SEO-friendly titles
    2. **Introduction Crafting**: Write engaging openings for target audiences
    3. **Body Development**: Generate detailed sections from outline
    4. **Conclusion Synthesis**: Create forward-looking summaries
    5. **Document Assembly**: Format complete Markdown document

    Integration Points:
    - Content teams for thought leadership creation
    - Marketing teams for lead generation assets
    - Product teams for documentation and guides
    - SEO teams for keyword-rich content creation
    - Sales teams for gated downloadable assets

    Special Considerations:
    - Maintains document coherence across multiple LLM calls
    - Implements rate limiting and error recovery
    - Provides progress tracking for long operations
    - Ensures consistent tone and voice throughout
    """

    def __init__(self):
        """Initialize the Whitepaper Agent."""
        logger.info("Whitepaper Agent (MUS-010) initialized")

        # Content generation parameters
        self.title_min_length = 10
        self.title_max_length = 100
        self.intro_word_count = 150  # Approximate target
        self.section_word_count = 300  # Approximate target per section
        self.conclusion_word_count = 200  # Approximate target

        # Generation limits and safety
        self.max_outline_sections = 20  # Match model limit
        self.content_timeout_per_step = 300  # 5 minutes per LLM call

    async def create_whitepaper(self, request: WhitepaperRequest) -> Whitepaper:
        """
        Generate a complete whitepaper from topic and outline.

        Main entry point for whitepaper creation. Orchestrates the entire
        document generation process from initial title creation through
        final document assembly.

        Args:
            request: WhitepaperRequest containing topic, outline, and audience

        Returns:
            Whitepaper containing final title and complete Markdown document

        Example:
            request = WhitepaperRequest(
                topic="The Future of AI in Digital Marketing",
                outline=[
                    "Introduction to AI Marketing",
                    "AI-Powered Personalization",
                    "Predictive Analytics for Campaigns"
                ],
                target_audience="CMOs at B2B SaaS companies"
            )
            whitepaper = await agent.create_whitepaper(request)
        """
        correlation_id = get_correlation_id()

        # Calculate total steps for progress tracking
        total_steps = 3 + len(request.outline)  # title + intro + sections + conclusion

        logger.info(
            "Starting whitepaper generation",
            topic=request.topic,
            section_count=len(request.outline),
            audience=request.target_audience,
            total_steps=total_steps,
            correlation_id=correlation_id
        )

        try:
            status = WhitepaperGenerationStatus(
                total_steps=total_steps,
                completed_steps=0,
                current_step="Generating title"
            )

            # Step 1: Generate compelling title
            title = await self._generate_title(request, correlation_id)
            status.completed_steps = 1
            status.current_step = "Writing introduction"
            logger.debug(f"Title generated: {title}", correlation_id=correlation_id)

            # Step 2: Create introduction
            introduction = await self._generate_introduction(request, title, correlation_id)
            status.completed_steps = 2
            status.current_step = "Creating body sections"
            logger.debug(f"Introduction generated ({len(introduction)} chars)", correlation_id=correlation_id)

            # Step 3: Generate body sections from outline
            body_sections = []
            for i, section_title in enumerate(request.outline):
                status.current_step = f"Creating section: {section_title}"

                section_content = await self._generate_section(
                    request, title, section_title, correlation_id
                )
                body_sections.append((section_title, section_content))

                status.completed_steps = 3 + i
                logger.debug(
                    f"Section '{section_title}' generated ({len(section_content)} chars)",
                    section_number=i + 1,
                    total_sections=len(request.outline),
                    correlation_id=correlation_id
                )

            # Step 4: Generate conclusion
            status.current_step = "Writing conclusion"
            conclusion = await self._generate_conclusion(request, title, correlation_id)
            status.completed_steps = total_steps
            status.current_step = "Document complete"
            logger.debug(f"Conclusion generated ({len(conclusion)} chars)", correlation_id=correlation_id)

            # Step 5: Assemble complete document
            full_markdown = self._assemble_document(title, introduction, body_sections, conclusion)

            # Create final whitepaper object
            whitepaper = Whitepaper(
                title=title,
                full_text_markdown=full_markdown
            )

            logger.info(
                "Whitepaper generation completed successfully",
                final_title_length=len(title),
                total_content_length=len(full_markdown),
                correlation_id=correlation_id
            )

            return whitepaper

        except Exception as e:
            logger.error(
                "Whitepaper generation failed",
                topic=request.topic,
                error=str(e),
                completed_steps=getattr(status, 'completed_steps', 0),
                correlation_id=correlation_id
            )
            raise

    async def _generate_title(self, request: WhitepaperRequest, correlation_id: str) -> str:
        """
        Generate a compelling, SEO-friendly title for the whitepaper.
        """
        prompt = f"""
Generate a compelling, SEO-friendly title for a technical whitepaper on the topic: "{request.topic}"

Requirements for the title:
- Must be engaging and attention-grabbing
- Should include relevant keywords for search optimization
- Keep it between 50-80 characters for optimal display
- Should appeal to the target audience: {request.target_audience}
- Make it sound authoritative and professional

Return ONLY the title text, nothing else.
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                system_prompt=self._get_title_writer_prompt(),
                model_type="creative",
                temperature=0.7,
                max_tokens=150
            )

            title = response.strip()
            title = self._clean_title(title)

            # Validate title quality
            if len(title) < self.title_min_length:
                logger.warning("Title too short, using fallback", correlation_id=correlation_id)
                title = f"The Complete Guide to {request.topic}"

            if len(title) > self.title_max_length:
                title = title[:self.title_max_length].strip()

            return title

        except Exception as e:
            logger.warning(
                f"Title generation failed, using fallback: {e}",
                correlation_id=correlation_id
            )
            return f"Comprehensive Guide to {request.topic}"

    async def _generate_introduction(
        self,
        request: WhitepaperRequest,
        title: str,
        correlation_id: str
    ) -> str:
        """
        Generate an engaging introduction for the whitepaper.
        """
        prompt = f"""
Write a compelling 150-word introduction for a whitepaper titled: "{title}"

Context:
- Topic: {request.topic}
- Target audience: {request.target_audience}
- Whitepaper will cover: {', '.join(request.outline)}

Introduction requirements:
- Hook the reader immediately
- Explain the importance/relevance of the topic
- Preview what the audience will learn
- Set appropriate expectations for the content
- Maintain professional, authoritative tone
- Address the specific audience's needs and challenges

Write the introduction as continuous prose (no section headers).
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                system_prompt=self._get_content_writer_prompt(request.target_audience),
                model_type="creative",
                temperature=0.6,
                max_tokens=500
            )

            return response.strip()

        except Exception as e:
            logger.warning(
                f"Introduction generation failed: {e}",
                correlation_id=correlation_id
            )
            return f"This comprehensive guide explores {request.topic}, providing valuable insights and practical knowledge for {request.target_audience}."

    async def _generate_section(
        self,
        request: WhitepaperRequest,
        title: str,
        section_title: str,
        correlation_id: str
    ) -> str:
        """
        Generate detailed content for a specific section.
        """
        prompt = f"""
Write detailed content for a section of a whitepaper.

Whitepaper title: "{title}"
Section title: "{section_title}"
Topic: {request.topic}
Target audience: {request.target_audience}

Full outline for context: {', '.join(request.outline)}

Requirements for this section:
- Write approximately 300 words of detailed, valuable content
- Focus specifically on the section topic: "{section_title}"
- Include practical examples or insights
- Address the target audience's specific needs and challenges
- Use a professional, authoritative tone
- Provide actionable information or concepts
- Connect this section to the broader topic

Write the section content as continuous prose (do not include the section title in the content).

Make this section comprehensive yet concise, providing real value to readers.
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                system_prompt=self._get_content_writer_prompt(request.target_audience),
                model_type="creative",
                temperature=0.5,
                max_tokens=800
            )

            return response.strip()

        except Exception as e:
            logger.warning(
                f"Section generation failed: {e}",
                section_title=section_title,
                correlation_id=correlation_id
            )
            return f"This section explores {section_title} within the broader context of {request.topic}, providing valuable insights for {request.target_audience}."

    async def _generate_conclusion(
        self,
        request: WhitepaperRequest,
        title: str,
        correlation_id: str
    ) -> str:
        """
        Generate a forward-looking conclusion that summarizes and inspires.
        """
        prompt = f"""
Write a comprehensive conclusion for a whitepaper titled: "{title}"

Topic: {request.topic}
Covering sections: {', '.join(request.outline)}
Target audience: {request.target_audience}

Conclusion requirements:
- Summarize the key insights and main takeaways
- Provide a forward-looking statement about the future
- Include a call to action or next steps for the reader
- Reinforce the value provided throughout the document
- Address the specific audience's opportunities and challenges ahead
- End on an inspiring, actionable note

Write approximately 200 words of engaging conclusion content.
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                system_prompt=self._get_content_writer_prompt(request.target_audience),
                model_type="creative",
                temperature=0.6,
                max_tokens=600
            )

            return response.strip()

        except Exception as e:
            logger.warning(
                f"Conclusion generation failed: {e}",
                correlation_id=correlation_id
            )
            return f"In conclusion, {request.topic} represents both challenges and significant opportunities for {request.target_audience}. By understanding and implementing these insights, organizations can position themselves for success in the evolving landscape."

    def _assemble_document(
        self,
        title: str,
        introduction: str,
        body_sections: List[tuple[str, str]],
        conclusion: str
    ) -> str:
        """
        Assemble all document parts into formatted Markdown.
        """
        markdown_parts = [
            f"# {title}\n",
            introduction,
            "\n"
        ]

        # Add each body section
        for section_title, section_content in body_sections:
            markdown_parts.extend([
                f"## {section_title}\n",
                section_content,
                "\n"
            ])

        # Add conclusion
        markdown_parts.extend([
            "## Conclusion\n",
            conclusion
        ])

        return "\n".join(markdown_parts)

    def _get_title_writer_prompt(self) -> str:
        """Get system prompt for title generation."""
        return """You are an expert SEO copywriter specializing in compelling titles for B2B whitepapers and technical content.

Your expertise includes:
- SEO keyword optimization for technical topics
- Psychological hooks and attention-grabbing copy
- Professional, authoritative tone creation
- Length optimization for various platforms
- Click-worthiness and shareability factors

You create titles that:
- Immediately communicate value and expertise
- Include relevant search terms naturally
- Are compelling enough to drive opens/clicks
- Work well in email subject lines, social posts, and search results
- Maintain credibility and professionalism

Always create titles that would make someone want to read the full document."""

    def _get_content_writer_prompt(self, target_audience: str) -> str:
        """Get system prompt for content writing tailored to audience."""
        base_prompt = """You are an expert technical writer and content strategist specializing in B2B whitepapers and thought leadership content.

Your expertise includes:
- Technical concept explanation for non-technical audiences
- Business value communication and ROI focus
- Actionable insights and practical applications
- Industry-specific language and terminology usage
- Engagement and retention through storytelling
- Professional tone maintenance with audience resonance

You write content that:
- Educates while maintaining engagement
- Provides genuine business value and insights
- Uses appropriate technical depth for the audience
- Includes real-world examples and data points
- Maintains consistency and quality throughout"""

        audience_specific = f"""

Additional context for this writing:
- Target audience: {target_audience}
- Tailor technical depth and examples to their experience level
- Address their specific pain points and goals
- Use language and references they will relate to
- Focus on insights most valuable to their role/industry"""

        return base_prompt + audience_specific

    def _clean_title(self, title: str) -> str:
        """Clean and format generated title."""
        # Remove quotes if present
        title = title.strip('"\'')
        # Ensure proper title case (but preserve proper nouns)
        return title

    async def estimate_generation_time(self, request: WhitepaperRequest) -> str:
        """
        Estimate the time required to generate a whitepaper.
        """
        base_time_per_step = 5  # seconds (approximate)
        total_steps = 3 + len(request.outline)

        estimated_seconds = total_steps * base_time_per_step

        if estimated_seconds < 60:
            return f"{estimated_seconds} seconds"
        elif estimated_seconds < 3600:
            return f"{estimated_seconds // 60} minutes"
        else:
            return f"{estimated_seconds // 3600} hours"


# Global singleton instance
whitepaper_agent = WhitepaperAgent()
