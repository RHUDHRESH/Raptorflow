"""
Content-related executable skills.
"""

import logging
import re
from typing import Any, Dict, List
from datetime import datetime

from ..base import Skill, SkillCategory, SkillLevel

logger = logging.getLogger(__name__)


class ContentGenerationSkill(Skill):
    """Skill for generating content using LLM."""

    def __init__(self):
        super().__init__(
            name="content_generation",
            category=SkillCategory.CONTENT,
            level=SkillLevel.INTERMEDIATE,
            description="Generate various types of content using LLM capabilities",
            tools_required=[],  # LLM is inherent to the agent
            capabilities=[
                "Create blog posts",
                "Write social media content", 
                "Generate email campaigns"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute content generation.
        
        Context requires:
        - prompt: str - The generation prompt
        - system_prompt: str - The system prompt
        - agent: BaseAgent - The calling agent (to use its LLM)
        """
        agent = context.get("agent")
        prompt = context.get("prompt")
        system_prompt = context.get("system_prompt")
        
        if not agent or not prompt:
            raise ValueError("Agent and prompt are required for content generation")

        logger.info(f"Executing ContentGenerationSkill with agent {agent.name}")
        
        # Use the agent's LLM to generate content
        # This replaces the monolithic _call_llm inside the agent
        content = await agent._call_llm(prompt, system_prompt=system_prompt)
        
        return {
            "content": content,
            "generated_by": "ContentGenerationSkill",
            "model": agent.model_tier.value
        }


class SEOAnalysisSkill(Skill):
    """Advanced skill for comprehensive SEO analysis and optimization."""

    def __init__(self):
        super().__init__(
            name="seo_optimization",
            category=SkillCategory.CONTENT,
            level=SkillLevel.ADVANCED,
            description="Comprehensive SEO analysis with competitor comparison and SERP analysis",
            tools_required=["web_search"],
            capabilities=[
                "Keyword density analysis",
                "Readability scoring", 
                "Content structure analysis",
                "Meta tag optimization",
                "Competitor comparison",
                "SERP feature analysis",
                "Technical SEO audit",
                "Content optimization suggestions"
            ]
        )

    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute comprehensive SEO analysis.
        
        Context requires:
        - content: str - The content to analyze
        - keywords: List[str] - Target keywords
        - agent: BaseAgent - The calling agent
        - target_url: str (optional) - URL for page-specific analysis
        """
        content = context.get("content", "")
        keywords = context.get("keywords", [])
        target_url = context.get("target_url")
        agent = context.get("agent")
        
        if not content:
            return {"score": 0.0, "suggestions": ["No content provided"], "analysis": {}}
        
        logger.info(f"Executing comprehensive SEO analysis for {len(content)} characters")
        
        try:
            # 1. Basic Content Analysis
            content_analysis = await self._analyze_content_structure(content)
            
            # 2. Advanced Keyword Analysis
            keyword_analysis = await self._analyze_keywords_advanced(content, keywords)
            
            # 3. Readability Assessment
            readability_score = await self._calculate_readability(content)
            
            # 4. Technical SEO Analysis
            technical_seo = await self._analyze_technical_seo(content)
            
            # 5. Competitor Analysis (if keywords provided)
            competitor_analysis = {}
            if keywords and target_url:
                competitor_analysis = await self._analyze_competitors(keywords, agent)
            
            # 6. SERP Feature Analysis
            serp_analysis = {}
            if keywords:
                serp_analysis = await self._analyze_serp_features(keywords, agent)
            
            # 7. Meta Tag Optimization
            meta_optimization = await self._generate_meta_optimization(content, keywords)
            
            # 8. Calculate Overall SEO Score
            seo_score = self._calculate_comprehensive_seo_score(
                content_analysis, keyword_analysis, readability_score, 
                technical_seo, competitor_analysis, serp_analysis
            )
            
            # 9. Generate Actionable Recommendations
            recommendations = await self._generate_seo_recommendations(
                content_analysis, keyword_analysis, readability_score,
                technical_seo, competitor_analysis, serp_analysis
            )
            
            return {
                "seo_score": seo_score,
                "analysis": {
                    "content_structure": content_analysis,
                    "keywords": keyword_analysis,
                    "readability": readability_score,
                    "technical_seo": technical_seo,
                    "competitor_analysis": competitor_analysis,
                    "serp_features": serp_analysis,
                    "meta_optimization": meta_optimization
                },
                "recommendations": recommendations,
                "score_breakdown": {
                    "content_score": content_analysis.get("structure_score", 0),
                    "keyword_score": keyword_analysis.get("density_score", 0),
                    "readability_score": readability_score,
                    "technical_score": technical_seo.get("score", 0),
                    "competitor_score": competitor_analysis.get("score", 0) if competitor_analysis else 0,
                    "serp_score": serp_analysis.get("score", 0) if serp_analysis else 0
                },
                "analyzed_at": content_analysis.get("analyzed_at"),
                "word_count": content_analysis.get("word_count", 0)
            }
            
        except Exception as e:
            logger.error(f"SEO analysis failed: {e}")
            return {
                "score": 0.0,
                "error": str(e),
                "suggestions": ["SEO analysis encountered an error"]
            }
    
    # Helper Methods for Comprehensive SEO Analysis
    
    async def _analyze_content_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure and organization."""
        try:
            # Basic metrics
            word_count = len(content.split())
            char_count = len(content)
            sentences = re.split(r'[.!?]+', content)
            sentence_count = len([s for s in sentences if s.strip()])
            
            # Heading analysis
            headings = {
                "h1": len(re.findall(r'^# (.+)$', content, re.MULTILINE)),
                "h2": len(re.findall(r'^## (.+)$', content, re.MULTILINE)),
                "h3": len(re.findall(r'^### (.+)$', content, re.MULTILINE))
            }
            
            # Paragraph analysis
            paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]
            paragraph_count = len(paragraphs)
            avg_paragraph_length = sum(len(p.split()) for p in paragraphs) / paragraph_count if paragraph_count > 0 else 0
            
            # Structure score (0-100)
            structure_score = 0
            if headings["h1"] > 0: structure_score += 20
            if headings["h2"] > 0: structure_score += 15
            if headings["h3"] > 0: structure_score += 10
            if 50 <= avg_paragraph_length <= 200: structure_score += 20
            elif 200 < avg_paragraph_length <= 300: structure_score += 15
            elif avg_paragraph_length > 300: structure_score -= 10
            
            return {
                "word_count": word_count,
                "char_count": char_count,
                "sentence_count": sentence_count,
                "paragraph_count": paragraph_count,
                "avg_paragraph_length": avg_paragraph_length,
                "headings": headings,
                "structure_score": min(100, max(0, structure_score)),
                "analyzed_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Content structure analysis failed: {e}")
            return {"structure_score": 0, "analyzed_at": datetime.now().isoformat()}
    
    async def _analyze_keywords_advanced(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Advanced keyword analysis with density and positioning."""
        try:
            content_lower = content.lower()
            words = content_lower.split()
            word_count = len(words)
            
            if word_count == 0:
                return {"density_score": 0, "keyword_density": {}, "positioning": {}}
            
            # Calculate keyword density
            density_map = {}
            for keyword in keywords:
                keyword_lower = keyword.lower()
                count = content_lower.count(keyword_lower)
                density = (count / word_count) * 100 if word_count > 0 else 0
                density_map[keyword] = {
                    "count": count,
                    "density": density,
                    "frequency": "high" if density > 3 else "medium" if density > 1 else "low"
                }
            
            # Keyword positioning analysis
            positioning = {}
            content_lines = content.split('\n')
            
            for keyword in keywords:
                keyword_lower = keyword.lower()
                positions = []
                
                # Find keyword positions in content
                for i, line in enumerate(content_lines):
                    if keyword_lower in line.lower():
                        positions.append({
                            "line": i + 1,
                            "position": line.lower().find(keyword_lower),
                            "context": line.strip()
                        })
                
                positioning[keyword] = {
                    "positions": positions,
                    "in_title": keyword_lower in content_lines[0].lower() if content_lines else False,
                    "in_first_paragraph": keyword_lower in ' '.join(content_lines[:3]).lower() if len(content_lines) >= 3 else False,
                    "total_mentions": len(positions)
                }
            
            # Calculate density score (0-100)
            avg_density = sum(d["density"] for d in density_map.values()) / len(density_map) if density_map else 0
            density_score = min(100, max(0, 100 - abs(avg_density - 2.5) * 20))  # Optimal around 2.5%
            
            return {
                "density_score": density_score,
                "keyword_density": density_map,
                "positioning": positioning,
                "avg_density": avg_density,
                "total_keywords": len(keywords)
            }
            
        except Exception as e:
            logger.error(f"Advanced keyword analysis failed: {e}")
            return {"density_score": 0, "keyword_density": {}, "positioning": {}}
    
    async def _calculate_readability(self, content: str) -> float:
        """Calculate readability score using multiple metrics."""
        try:
            sentences = re.split(r'[.!?]+', content)
            if not sentences or not any(s.strip() for s in sentences):
                return 0.0
            
            words = content.split()
            word_count = len(words)
            
            # Average sentence length
            avg_sentence_length = word_count / len(sentences)
            
            # Average word length
            avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
            
            # Percentage of complex words (3+ syllables)
            complex_words = sum(1 for word in words if self._count_syllables(word) >= 3)
            complex_word_percentage = (complex_words / word_count) * 100 if word_count > 0 else 0
            
            # Readability score (0-100, higher is better)
            readability_score = 100
            
            # Penalize for long sentences
            if avg_sentence_length > 20:
                readability_score -= 20
            elif avg_sentence_length > 15:
                readability_score -= 10
            
            # Penalize for long words
            if avg_word_length > 6:
                readability_score -= 15
            elif avg_word_length > 5:
                readability_score -= 5
            
            # Penalize for complex words
            if complex_word_percentage > 20:
                readability_score -= 20
            elif complex_word_percentage > 15:
                readability_score -= 10
            elif complex_word_percentage > 10:
                readability_score -= 5
            
            return max(0, min(100, readability_score))
            
        except Exception as e:
            logger.error(f"Readability calculation failed: {e}")
            return 0.0
    
    def _count_syllables(self, word: str) -> int:
        """Count syllables in a word (simplified implementation)."""
        word = word.lower()
        vowels = "aeiouy"
        syllable_count = 0
        prev_char_was_vowel = False
        
        for char in word:
            if char in vowels:
                if not prev_char_was_vowel:
                    syllable_count += 1
                prev_char_was_vowel = True
            else:
                prev_char_was_vowel = False
        
        return max(1, syllable_count)
    
    async def _analyze_technical_seo(self, content: str) -> Dict[str, Any]:
        """Analyze technical SEO factors."""
        try:
            # Meta tags check
            title_match = re.search(r'<title[^>]*>([^<]+)</title>', content, re.IGNORECASE)
            description_match = re.search(r'<meta[^>]*name=["\']description["\'][^>]*content=["\']([^"\']+)["\']', content, re.IGNORECASE)
            h1_match = re.search(r'<h1[^>]*>([^<]+)</h1>', content, re.IGNORECASE)
            
            # Image alt text analysis
            img_matches = re.findall(r'<img[^>]*alt=["\']([^"\']*)["\']', content, re.IGNORECASE)
            images_with_alt = len(img_matches)
            total_images = len(re.findall(r'<img', content, re.IGNORECASE))
            
            # Internal/external links
            internal_links = len(re.findall(r'href=["\'][^"\']*://[^"\']*["\'][^"\']*\.html?', content, re.IGNORECASE))
            external_links = len(re.findall(r'href=["\']http[^"\']*["\']', content, re.IGNORECASE))
            
            # Technical score (0-100)
            tech_score = 0
            
            if title_match and len(title_match.group(1)) > 30:
                tech_score += 15
            elif title_match and len(title_match.group(1)) > 10:
                tech_score += 10
            
            if description_match and len(description_match.group(1)) > 120:
                tech_score += 15
            elif description_match and len(description_match.group(1)) > 50:
                tech_score += 10
            
            if h1_match:
                tech_score += 10
            
            if total_images > 0:
                alt_text_ratio = images_with_alt / total_images
                tech_score += alt_text_ratio * 20
            
            if internal_links > 0:
                tech_score += 10
            
            return {
                "score": min(100, tech_score),
                "has_title": bool(title_match),
                "has_description": bool(description_match),
                "has_h1": bool(h1_match),
                "images_total": total_images,
                "images_with_alt": images_with_alt,
                "internal_links": internal_links,
                "external_links": external_links,
                "title_length": len(title_match.group(1)) if title_match else 0,
                "description_length": len(description_match.group(1)) if description_match else 0
            }
            
        except Exception as e:
            logger.error(f"Technical SEO analysis failed: {e}")
            return {"score": 0, "error": str(e)}
    
    async def _analyze_competitors(self, keywords: List[str], agent) -> Dict[str, Any]:
        """Analyze competitors for target keywords."""
        try:
            web_search_tool = agent.tool_registry.get("web_search")
            if not web_search_tool:
                return {"error": "Web search tool not available"}
            
            competitor_data = []
            
            for keyword in keywords[:3]:  # Limit to top 3 keywords
                try:
                    # Search for keyword + "competitor" or related terms
                    search_query = f"{keyword} competitors analysis"
                    search_results = await web_search_tool.arun(query=search_query, limit=5)
                    
                    if search_results.get("success"):
                        for result in search_results.get("data", [])[:3]:
                            competitor_data.append({
                                "keyword": keyword,
                                "competitor": result.get("title", "Unknown"),
                                "url": result.get("url", ""),
                                "snippet": result.get("snippet", ""),
                                "position": result.get("position", 0)
                            })
                
                except Exception as e:
                    logger.warning(f"Failed to analyze competitors for '{keyword}': {e}")
            
            # Calculate competitor score
            score = min(100, len(competitor_data) * 20)  # More data = better analysis
            
            return {
                "score": score,
                "competitors": competitor_data,
                "keywords_analyzed": keywords[:3],
                "total_competitors": len(competitor_data)
            }
            
        except Exception as e:
            logger.error(f"Competitor analysis failed: {e}")
            return {"score": 0, "error": str(e)}
    
    async def _analyze_serp_features(self, keywords: List[str], agent) -> Dict[str, Any]:
        """Analyze SERP features for target keywords."""
        try:
            web_search_tool = agent.tool_registry.get("web_search")
            if not web_search_tool:
                return {"error": "Web search tool not available"}
            
            serp_features = {
                "featured_snippets": [],
                "knowledge_panel": False,
                "local_results": False,
                "video_results": False,
                "image_results": False,
                "news_results": False,
                "shopping_results": False
            }
            
            for keyword in keywords[:2]:  # Limit to top 2 keywords
                try:
                    search_query = keyword
                    search_results = await web_search_tool.arun(query=search_query, limit=10)
                    
                    if search_results.get("success"):
                        results = search_results.get("data", [])
                        
                        # Check for various SERP features
                        for result in results:
                            if result.get("featured"):
                                serp_features["featured_snippets"].append({
                                    "keyword": keyword,
                                    "snippet": result.get("snippet", ""),
                                    "url": result.get("url", "")
                                })
                            
                            if result.get("knowledge_panel"):
                                serp_features["knowledge_panel"] = True
                            
                            if result.get("local_result"):
                                serp_features["local_results"] = True
                            
                            if result.get("video_result"):
                                serp_features["video_results"] = True
                            
                            if result.get("image_result"):
                                serp_features["image_results"] = True
                            
                            if result.get("news_result"):
                                serp_features["news_results"] = True
                            
                            if result.get("shopping_result"):
                                serp_features["shopping_results"] = True
                
                except Exception as e:
                    logger.warning(f"Failed to analyze SERP for '{keyword}': {e}")
            
            # Calculate SERP feature score
            feature_count = sum([
                len(serp_features["featured_snippets"]),
                1 if serp_features["knowledge_panel"] else 0,
                1 if serp_features["local_results"] else 0,
                1 if serp_features["video_results"] else 0,
                1 if serp_features["image_results"] else 0,
                1 if serp_features["news_results"] else 0,
                1 if serp_features["shopping_results"] else 0
            ])
            
            score = min(100, feature_count * 10)  # More features = better SERP analysis
            
            return {
                "score": score,
                "features": serp_features,
                "keywords_analyzed": keywords[:2],
                "total_features": feature_count
            }
            
        except Exception as e:
            logger.error(f"SERP analysis failed: {e}")
            return {"score": 0, "error": str(e)}
    
    async def _generate_meta_optimization(self, content: str, keywords: List[str]) -> Dict[str, Any]:
        """Generate optimized meta tags."""
        try:
            # Extract first paragraph for description
            sentences = re.split(r'[.!?]+', content)
            first_sentence = sentences[0].strip() if sentences else content[:150]
            
            # Generate optimized title
            title = content.split('\n')[0][:60]  # First line, max 60 chars
            if keywords and keywords[0].lower() not in title.lower():
                title = f"{keywords[0]}: {title}"[:60]
            
            # Generate meta description
            description = first_sentence[:160]  # Max 160 chars for SEO
            
            # Generate keywords meta tag
            meta_keywords = ", ".join(keywords[:10])  # Max 10 keywords
            
            return {
                "title": title,
                "description": description,
                "keywords": meta_keywords,
                "title_length": len(title),
                "description_length": len(description),
                "optimized_for_keywords": keywords
            }
            
        except Exception as e:
            logger.error(f"Meta optimization failed: {e}")
            return {"error": str(e)}
    
    def _calculate_comprehensive_seo_score(
        self, content_analysis: Dict, keyword_analysis: Dict, 
        readability_score: float, technical_seo: Dict, 
        competitor_analysis: Dict, serp_analysis: Dict
    ) -> float:
        """Calculate comprehensive SEO score from all analysis components."""
        try:
            # Weight different components
            weights = {
                "content_structure": 0.15,
                "keywords": 0.25,
                "readability": 0.20,
                "technical": 0.20,
                "competitors": 0.10,
                "serp_features": 0.10
            }
            
            # Get individual scores
            content_score = content_analysis.get("structure_score", 0)
            keyword_score = keyword_analysis.get("density_score", 0)
            tech_score = technical_seo.get("score", 0)
            competitor_score = competitor_analysis.get("score", 0)
            serp_score = serp_analysis.get("score", 0)
            
            # Calculate weighted score
            total_score = (
                content_score * weights["content_structure"] +
                keyword_score * weights["keywords"] +
                readability_score * weights["readability"] +
                tech_score * weights["technical"] +
                competitor_score * weights["competitors"] +
                serp_score * weights["serp_features"]
            )
            
            return min(100, max(0, total_score))
            
        except Exception as e:
            logger.error(f"SEO score calculation failed: {e}")
            return 0.0
    
    async def _generate_seo_recommendations(
        self, content_analysis: Dict, keyword_analysis: Dict,
        readability_score: float, technical_seo: Dict,
        competitor_analysis: Dict, serp_analysis: Dict
    ) -> List[str]:
        """Generate actionable SEO recommendations."""
        try:
            recommendations = []
            
            # Content structure recommendations
            structure_score = content_analysis.get("structure_score", 0)
            if structure_score < 50:
                recommendations.append("Add more headings (H1, H2, H3) to improve content structure")
            if content_analysis.get("avg_paragraph_length", 0) > 200:
                recommendations.append("Break long paragraphs into shorter ones for better readability")
            
            # Keyword recommendations
            density_score = keyword_analysis.get("density_score", 0)
            if density_score < 30:
                recommendations.append("Increase keyword density naturally, aim for 2-3% per keyword")
            elif density_score > 80:
                recommendations.append("Reduce keyword density to avoid stuffing penalties")
            
            # Readability recommendations
            if readability_score < 60:
                recommendations.append("Improve readability with shorter sentences and simpler words")
            elif readability_score < 80:
                recommendations.append("Use more transition words and vary sentence structure")
            
            # Technical SEO recommendations
            tech_score = technical_seo.get("score", 0)
            if not technical_seo.get("has_title"):
                recommendations.append("Add a compelling title tag (50-60 characters)")
            if not technical_seo.get("has_description"):
                recommendations.append("Add a meta description (150-160 characters)")
            if technical_seo.get("images_total", 0) > technical_seo.get("images_with_alt", 0):
                recommendations.append("Add alt text to all images for accessibility and SEO")
            
            # Competitor recommendations
            if competitor_analysis.get("score", 0) < 50:
                recommendations.append("Analyze top competitors for keyword gaps and opportunities")
            
            # SERP recommendations
            if serp_analysis.get("score", 0) < 30:
                recommendations.append("Optimize content to appear in featured snippets and knowledge panels")
            
            return recommendations[:10]  # Limit to top 10 recommendations
            
        except Exception as e:
            logger.error(f"SEO recommendations generation failed: {e}")
            return ["Error generating SEO recommendations"]
    
    class CopyPolisherSkill(Skill):
        """Skill for polishing and improving content quality."""
        
        def __init__(self):
            super().__init__(
                name="copy_polisher",
                category=SkillCategory.CONTENT,
                level=SkillLevel.INTERMEDIATE,
                description="Polish and improve content for clarity, engagement, and professionalism",
                tools_required=["web_search"],  # For research and style references
                capabilities=[
                    "Grammar and spelling correction",
                    "Style and tone adjustment",
                    "Readability improvement",
                    "Clarity enhancement",
                    "Engagement optimization",
                    "SEO optimization",
                    "Brand voice consistency",
                    "Formatting and structure improvement"
                ]
            )
        
        async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
            """
            Execute content polishing.
            
            Context requires:
            - content: str - The content to polish
            - polish_type: str - Type of polishing (grammar, style, readability, all)
            - tone: str - Target tone (professional, casual, friendly, etc.)
            - target_audience: str - Target audience for content
            - agent: BaseAgent - The calling agent (to use its LLM)
            """
            content = context.get("content", "")
            polish_type = context.get("polish_type", "all")
            tone = context.get("tone", "professional")
            target_audience = context.get("target_audience", "general")
            agent = context.get("agent")
            
            if not content or not agent:
                raise ValueError("Content and agent are required for copy polishing")
            
            logger.info(f"Executing CopyPolisherSkill for {len(content)} characters")
            
            try:
                # Step 1: Analyze content quality
                content_analysis = await self._analyze_content_quality(content)
                
                # Step 2: Research best practices (if needed)
                research_data = {}
                if polish_type in ["all", "style", "seo"]:
                    research_data = await self._research_best_practices(content, target_audience, agent)
                
                # Step 3: Generate polishing strategy
                strategy = await self._generate_polishing_strategy(
                    content_analysis, research_data, polish_type, tone, target_audience
                )
                
                # Step 4: Execute polishing
                polished_content = await self._polish_content(
                    content, strategy, agent, polish_type
                )
                
                # Step 5: Quality assessment
                quality_score = await self._assess_content_quality(polished_content)
                
                # Step 6: Generate improvement suggestions
                suggestions = await self._generate_improvement_suggestions(
                    content, polished_content, content_analysis, quality_score
                )
                
                return {
                    "original_content": content,
                    "polished_content": polished_content,
                    "polish_type": polish_type,
                    "tone": tone,
                    "target_audience": target_audience,
                    "content_analysis": content_analysis,
                    "research_data": research_data,
                    "strategy": strategy,
                    "quality_score": quality_score,
                    "improvement_suggestions": suggestions,
                    "polished_by": "CopyPolisherSkill",
                    "model": agent.model_tier.value
                }
                
            except Exception as e:
                logger.error(f"Copy polishing failed: {e}")
                return {
                    "error": str(e),
                    "polished_by": "CopyPolisherSkill",
                    "original_content": content
                }
        
        async def _analyze_content_quality(self, content: str) -> Dict[str, Any]:
            """Analyze content for quality issues."""
            try:
                import re
                
                # Basic metrics
                word_count = len(content.split())
                sentence_count = len(re.split(r'[.!?]+', content))
                paragraph_count = len([p.strip() for p in content.split('\n\n') if p.strip()])
                
                # Readability analysis
                avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
                avg_word_length = sum(len(word) for word in content.split()) / word_count if word_count > 0 else 0
                
                # Grammar and spelling checks (simplified)
                potential_issues = []
                
                # Check for common grammar issues
                if re.search(r'\b(is|are|was|were)\b', content, re.IGNORECASE):
                    potential_issues.append("Passive voice detected")
                
                # Check for spelling patterns (basic)
                if re.search(r'\b(a lot|alot|alright|allright)\b', content, re.IGNORECASE):
                    potential_issues.append("Informal contractions detected")
                
                # Check for sentence structure
                if avg_sentence_length > 25:
                    potential_issues.append("Very long sentences detected")
                elif avg_sentence_length < 10:
                    potential_issues.append("Very short sentences detected")
                
                # Check paragraph structure
                if paragraph_count > 0:
                    avg_paragraph_length = word_count / paragraph_count
                    if avg_paragraph_length > 150:
                        potential_issues.append("Very long paragraphs detected")
                
                return {
                    "word_count": word_count,
                    "sentence_count": sentence_count,
                    "paragraph_count": paragraph_count,
                    "avg_sentence_length": avg_sentence_length,
                    "avg_word_length": avg_word_length,
                    "potential_issues": potential_issues,
                    "readability_score": self._calculate_readability_score(avg_sentence_length, avg_word_length)
                }
                
            except Exception as e:
                logger.error(f"Content analysis failed: {e}")
                return {"error": str(e)}
        
        def _calculate_readability_score(self, avg_sentence_length: float, avg_word_length: float) -> float:
            """Calculate readability score (0-100)."""
            score = 100
            
            # Penalize overly long sentences
            if avg_sentence_length > 20:
                score -= 20
            elif avg_sentence_length > 15:
                score -= 10
            
            # Penalize overly complex words
            if avg_word_length > 6:
                score -= 15
            elif avg_word_length > 5:
                score -= 5
            
            # Bonus for optimal ranges
            if 10 <= avg_sentence_length <= 15:
                score += 10
            if 3 <= avg_word_length <= 5:
                score += 10
                
            return max(0, min(100, score))
        
        async def _research_best_practices(self, content: str, target_audience: str, agent) -> Dict[str, Any]:
            """Research best practices for content type and audience."""
            try:
                # Use web search to research best practices
                web_search_tool = agent.tool_registry.get("web_search")
                
                if not web_search_tool:
                    return {"error": "Web search tool not available"}
                
                # Research queries based on content type and audience
                research_queries = [
                    f"content writing best practices for {target_audience}",
                    f"professional writing style guide",
                    f"engagement techniques for {target_audience} audience",
                    "SEO content optimization tips"
                ]
                
                research_results = {}
                
                for query in research_queries:
                    try:
                        search_result = await web_search_tool.arun(query=query, limit=5)
                        if search_result.get("success"):
                            research_results[query] = search_result.get("data", [])
                    except Exception as e:
                        logger.warning(f"Research query failed: {query} - {e}")
                        research_results[query] = []
                
                return {
                    "research_queries": research_queries,
                    "research_results": research_results,
                    "best_practices": self._extract_best_practices(research_results)
                }
                
            except Exception as e:
                logger.error(f"Best practices research failed: {e}")
                return {"error": str(e)}
        
        def _extract_best_practices(self, research_results: Dict[str, Any]) -> List[str]:
            """Extract best practices from research results."""
            practices = []
            
            for query, results in research_results.items():
                for result in results[:3]:  # Top 3 results per query
                    if isinstance(result, dict) and "snippet" in result:
                        practices.append(result["snippet"])
            
            # Remove duplicates and limit
            unique_practices = list(set(practices))[:10]
            return unique_practices
        
        async def _generate_polishing_strategy(
            self, content_analysis: Dict[str, Any], research_data: Dict[str, Any],
            polish_type: str, tone: str, target_audience: str
        ) -> Dict[str, Any]:
            """Generate comprehensive polishing strategy."""
            try:
                strategy = {
                    "polish_type": polish_type,
                    "target_tone": tone,
                    "target_audience": target_audience,
                    "focus_areas": [],
                    "improvements": [],
                    "best_practices": research_data.get("best_practices", [])
                }
                
                # Determine focus areas based on analysis
                issues = content_analysis.get("potential_issues", [])
                
                if "Passive voice detected" in issues:
                    strategy["focus_areas"].append("Convert passive voice to active voice")
                    strategy["improvements"].append("Use stronger, more direct language")
                
                if "Informal contractions detected" in issues:
                    strategy["focus_areas"].append("Replace informal contractions with formal alternatives")
                    strategy["improvements"].append("Use professional language")
                
                if "Very long sentences detected" in issues:
                    strategy["focus_areas"].append("Break down long sentences")
                    strategy["improvements"].append("Vary sentence structure")
                
                if "Very short sentences detected" in issues:
                    strategy["focus_areas"].append("Combine short sentences")
                    strategy["improvements"].append("Add more detail and context")
                
                if "Very long paragraphs detected" in issues:
                    strategy["focus_areas"].append("Break up long paragraphs")
                    strategy["improvements"].append("Use subheadings and bullet points")
                
                # Add general improvements based on polish type
                if polish_type in ["all", "readability"]:
                    strategy["focus_areas"].append("Improve readability and flow")
                    strategy["improvements"].extend([
                        "Use transition words",
                        "Vary sentence structure",
                        "Ensure logical flow"
                    ])
                
                if polish_type in ["all", "style"]:
                    strategy["focus_areas"].append("Enhance writing style")
                    strategy["improvements"].extend([
                        "Maintain consistent tone",
                        "Use stronger verbs",
                        "Eliminate redundant phrases"
                    ])
                
                if polish_type in ["all", "seo"]:
                    strategy["focus_areas"].append("Optimize for search engines")
                    strategy["improvements"].extend([
                        "Include relevant keywords naturally",
                        "Optimize meta descriptions",
                        "Use proper heading structure"
                    ])
                
                return strategy
                
            except Exception as e:
                logger.error(f"Strategy generation failed: {e}")
                return {"error": str(e)}
        
        async def _polish_content(self, content: str, strategy: Dict[str, Any], agent, polish_type: str) -> str:
            """Execute content polishing using LLM."""
            try:
                # Create comprehensive polishing prompt
                system_prompt = self._create_polishing_system_prompt(strategy, polish_type, tone)
                
                user_prompt = f"""
                Please polish the following content according to the strategy and best practices provided.
                
                Original Content:
                {content}
                
                Strategy:
                {strategy}
                
                Focus Areas: {', '.join(strategy.get('focus_areas', []))}
                
                Best Practices: {', '.join(strategy.get('best_practices', []))}
                
                Target Tone: {tone}
                Target Audience: {strategy.get('target_audience', 'general')}
                
                Polishing Type: {polish_type}
                
                Instructions:
                1. Improve clarity, readability, and engagement
                2. Maintain the original meaning and core message
                3. Apply the specified tone consistently
                4. Incorporate best practices naturally
                5. Ensure proper grammar, spelling, and punctuation
                6. Structure content logically with appropriate formatting
                7. Optimize for the target audience
                8. Return only the polished content without explanations
                """
                
                # Use agent's LLM to polish content
                polished_content = await agent._call_llm(user_prompt, system_prompt)
                
                return polished_content.strip()
                
            except Exception as e:
                logger.error(f"Content polishing failed: {e}")
                return content  # Return original content if polishing fails
        
        def _create_polishing_system_prompt(self, strategy: Dict[str, Any], polish_type: str, tone: str) -> str:
            """Create system prompt for content polishing."""
            focus_areas = strategy.get('focus_areas', [])
            best_practices = strategy.get('best_practices', [])
            
            prompt = f"""You are an expert content editor and copywriter specializing in polishing content for maximum clarity, engagement, and professionalism.
            
            Your task is to polish content according to specific requirements while maintaining the original meaning and improving quality.
            
            POLISHING REQUIREMENTS:
            - Target Tone: {tone}
            - Polishing Type: {polish_type}
            - Focus Areas: {', '.join(focus_areas)}
            - Best Practices to Apply: {', '.join(best_practices)}
            
            CONTENT POLISHING PRINCIPLES:
            1. Clarity Above All: Content must be crystal clear and easy to understand
            2. Maintain Original Intent: Preserve the core message and meaning
            3. Professional Excellence: Use precise language, proper grammar, and correct spelling
            4. Engagement Optimization: Make content more compelling and engaging
            5. Audience Appropriateness: Tailor language and complexity to target audience
            6. Structural Integrity: Ensure logical flow and proper organization
            7. SEO Optimization: Incorporate relevant keywords naturally when applicable
            8. Consistency: Maintain consistent tone and style throughout
            
            GRAMMAR AND STYLE RULES:
            - Use active voice instead of passive voice
            - Vary sentence length and structure for better flow
            - Eliminate redundant words and phrases
            - Use strong, specific verbs instead of weak ones
            - Ensure proper punctuation and formatting
            - Check for and correct spelling errors
            - Maintain professional tone without informal contractions
            
            Return ONLY the polished content without any explanations or meta-commentary.
                """
            
            return prompt
        
        async def _assess_content_quality(self, content: str) -> Dict[str, Any]:
            """Assess the quality of polished content."""
            try:
                # Re-analyze polished content
                analysis = await self._analyze_content_quality(content)
                
                # Compare with original (if available)
                improvement_score = 0
                if analysis.get("readability_score", 0) > 70:
                    improvement_score += 20
                if len(analysis.get("potential_issues", [])) == 0:
                    improvement_score += 20
                if 10 <= analysis.get("avg_sentence_length", 0) <= 20:
                    improvement_score += 15
                if 3 <= analysis.get("avg_word_length", 0) <= 6:
                    improvement_score += 15
                
                # Calculate overall quality score
                quality_score = min(100, improvement_score)
                
                return {
                    "quality_score": quality_score,
                    "readability_score": analysis.get("readability_score", 0),
                    "issue_count": len(analysis.get("potential_issues", [])),
                    "word_count": analysis.get("word_count", 0),
                    "sentence_count": analysis.get("sentence_count", 0),
                    "paragraph_count": analysis.get("paragraph_count", 0),
                    "improvement_areas": [
                        "Grammar and spelling",
                        "Readability and flow",
                        "Structure and organization"
                    ]
                }
                
            except Exception as e:
                logger.error(f"Quality assessment failed: {e}")
                return {"error": str(e)}
        
        async def _generate_improvement_suggestions(
            self, original_content: str, polished_content: str, 
            content_analysis: Dict[str, Any], quality_score: Dict[str, Any]
        ) -> List[str]:
            """Generate specific improvement suggestions."""
            try:
                suggestions = []
                
                # Compare original and polished content
                original_issues = content_analysis.get("potential_issues", [])
                polished_analysis = await self._analyze_content_quality(polished_content)
                remaining_issues = polished_analysis.get("potential_issues", [])
                
                # Identify improvements
                if len(original_issues) > len(remaining_issues):
                    suggestions.append("Successfully resolved grammar and style issues")
                
                if polished_analysis.get("readability_score", 0) > content_analysis.get("readability_score", 0):
                    suggestions.append("Improved readability and sentence flow")
                
                if polished_analysis.get("avg_sentence_length", 0) < content_analysis.get("avg_sentence_length", 0):
                    suggestions.append("Better sentence structure and length variety")
                
                # Add specific suggestions based on improvements
                if quality_score.get("quality_score", 0) > 70:
                    suggestions.append("High-quality content with professional polish")
                    suggestions.append("Enhanced engagement and clarity")
                
                # Add general suggestions
                suggestions.extend([
                    "Consider adding relevant examples or case studies",
                    "Include a clear call-to-action if appropriate",
                    "Ensure consistent formatting and structure",
                    "Review for SEO optimization opportunities"
                ])
                
                return suggestions[:10]  # Limit to top 10 suggestions
                
            except Exception as e:
                logger.error(f"Suggestion generation failed: {e}")
                return ["Error generating improvement suggestions"]
    
    class ViralHookSkill(Skill):
        """Skill for generating viral hooks and social media content."""
        
        def __init__(self):
            super().__init__(
                name="viral_hook_generator",
                category=SkillCategory.CONTENT,
                level=SkillLevel.INTERMEDIATE,
                description="Generate viral hooks and social media content for maximum engagement",
                tools_required=["web_search"],  # For trend research and viral content analysis
                capabilities=[
                    "Viral hook generation",
                    "Social media content creation",
                    "Trend analysis",
                    "Engagement optimization",
                    "Hashtag strategy",
                    "Call-to-action optimization",
                    "Emotional trigger identification",
                    "Shareability enhancement",
                    "Platform-specific content adaptation"
                ]
            )
        
        async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
            """
            Execute viral hook generation.
            
            Context requires:
            - content: str - The content to create viral hooks for
            - platform: str - Target platform (twitter, instagram, tiktok, linkedin, facebook)
            - hook_type: str - Type of hooks (question, challenge, statement, story)
            - target_audience: str - Target audience demographics
            - agent: BaseAgent - The calling agent (to use its LLM)
            """
            content = context.get("content", "")
            platform = context.get("platform", "twitter")
            hook_type = context.get("hook_type", "question")
            target_audience = context.get("target_audience", "general")
            agent = context.get("agent")
            
            if not content or not agent:
                raise ValueError("Content and agent are required for viral hook generation")
            
            logger.info(f"Executing ViralHookSkill for {platform} - {hook_type}")
            
            try:
                # Step 1: Analyze content for viral potential
                content_analysis = await self._analyze_viral_potential(content, platform)
                
                # Step 2: Research viral trends and patterns
                trend_research = await self._research_viral_trends(content, platform, target_audience, agent)
                
                # Step 3: Generate viral hook strategy
                strategy = await self._generate_viral_strategy(
                    content_analysis, trend_research, hook_type, platform, target_audience
                )
                
                # Step 4: Generate viral hooks
                viral_hooks = await self._generate_viral_hooks(
                    content, strategy, hook_type, platform, target_audience, agent
                )
                
                # Step 5: Optimize for engagement
                optimized_hooks = await self._optimize_for_engagement(viral_hooks, agent)
                
                # Step 6: Generate hashtags and CTA
                hashtags = await self._generate_hashtags(viral_hooks, platform, target_audience)
                ctas = await self._generate_ctas(viral_hooks, platform, target_audience)
                
                return {
                    "original_content": content,
                    "viral_hooks": viral_hooks,
                    "optimized_hooks": optimized_hooks,
                    "hashtags": hashtags,
                    "call_to_actions": ctas,
                    "platform": platform,
                    "hook_type": hook_type,
                    "target_audience": target_audience,
                    "content_analysis": content_analysis,
                    "trend_research": trend_research,
                    "viral_strategy": strategy,
                    "generated_by": "ViralHookSkill",
                    "model": agent.model_tier.value
                }
                
            except Exception as e:
                logger.error(f"Viral hook generation failed: {e}")
                return {
                    "error": str(e),
                    "generated_by": "ViralHookSkill",
                    "original_content": content
                }
        
        async def _analyze_viral_potential(self, content: str, platform: str) -> Dict[str, Any]:
            """Analyze content for viral potential."""
            try:
                # Content characteristics
                word_count = len(content.split())
                char_count = len(content)
                
                # Viral indicators analysis
                viral_indicators = {
                    "has_question": "?" in content,
                    "has_exclamation": "!" in content,
                    "has_emoji": bool(re.search(r'[\U0001F600-\U0001F900-\U0001F9FF-\U0001FAF0-\U0001F80F-\U0001FAD6-\U0001F200-\U0001F2FF]', content)),
                    "has_capitalization": content != content.lower(),
                    "has_numbers": bool(re.search(r'\d+', content)),
                    "has_trending_topics": self._check_trending_topics(content),
                    "emotional_words": self._count_emotional_words(content),
                    "shareability_score": self._calculate_shareability(content)
                }
                
                # Platform-specific analysis
                platform_analysis = self._analyze_platform_suitability(content, platform)
                
                # Calculate viral potential score
                viral_score = self._calculate_viral_score(viral_indicators, platform_analysis)
                
                return {
                    "word_count": word_count,
                    "char_count": char_count,
                    "viral_indicators": viral_indicators,
                    "platform_analysis": platform_analysis,
                    "viral_score": viral_score,
                    "viral_potential": "high" if viral_score >= 70 else "medium" if viral_score >= 40 else "low"
                }
                
            except Exception as e:
                logger.error(f"Viral analysis failed: {e}")
                return {"error": str(e)}
        
        def _check_trending_topics(self, content: str) -> List[str]:
            """Check for trending topics in content."""
            trending_topics = [
                "AI", "artificial intelligence", "machine learning", "blockchain",
                "cryptocurrency", "NFT", "metaverse", "Web3", "sustainability",
                "climate change", "remote work", "startup", "innovation",
                "technology", "digital transformation", "future of work",
                "social media", "influencer", "creator economy", "gaming"
            ]
            
            content_lower = content.lower()
            found_topics = []
            
            for topic in trending_topics:
                if topic in content_lower:
                    found_topics.append(topic)
            
            return found_topics
        
        def _count_emotional_words(self, content: str) -> int:
            """Count emotional words in content."""
            emotional_words = [
                "amazing", "awesome", "incredible", "unbelievable", "mind-blowing",
                "game-changer", "revolutionary", "breakthrough", "epic",
                "stunning", "spectacular", "extraordinary", "phenomenal",
                "life-changing", "historic", "monumental", "legendary",
                "viral", "trending", "sensational", "shocking",
                "insane", "crazy", "unreal", "impossible"
            ]
            
            content_lower = content.lower()
            count = sum(1 for word in emotional_words if word in content_lower)
            return count
        
        def _calculate_shareability(self, content: str) -> float:
            """Calculate shareability score (0-100)."""
            score = 50  # Base score
            
            # Factors that increase shareability
            if len(content) > 50 and len(content) < 500:
                score += 20  # Good length for sharing
            if len(content) >= 500 and len(content) < 1000:
                score += 15  # Very shareable length
            
            # Check for shareable elements
            if "?" in content:
                score += 15  # Questions encourage engagement
            if "!" in content:
                score += 10  # Excitement encourages sharing
            
            # Check for visual elements (emojis increase shareability)
            emoji_count = len(re.findall(r'[\U0001F600-\U0001F900-\U0001F9FF-\U0001FAF0-\U0001F80F-\U0001FAD6-\U0001F200-\U0001F2FF]', content))
            if emoji_count > 0:
                score += min(10, emoji_count * 2)  # Emojis increase visual appeal
            
            # Check for actionable content
            actionable_words = ["how", "guide", "tutorial", "tips", "steps", "learn", "discover", "check out"]
            if any(word in content.lower() for word in actionable_words):
                score += 10
            
            # Check for relatable content
            relatable_words = ["you", "your", "we", "us", "our", "everyone", "people", "struggle", "experience"]
            if any(word in content.lower() for word in relatable_words):
                score += 10
            
            return min(100, max(0, score))
        
        def _analyze_platform_suitability(self, content: str, platform: str) -> Dict[str, Any]:
            """Analyze content suitability for specific platform."""
            platform_requirements = {
                "twitter": {
                    "max_length": 280,
                    "ideal_length": 100-200,
                    "hashtag_limit": 3,
                    "media_types": ["text", "images", "videos", "gifs"],
                    "engagement_factors": ["timeliness", "retweets", "likes", "replies"]
                },
                "instagram": {
                    "max_length": 2200,
                    "ideal_length": 138-150,
                    "hashtag_limit": 30,
                    "media_types": ["images", "videos", "stories", "reels", "carousels"],
                    "engagement_factors": ["likes", "comments", "shares", "saves", "views"]
                },
                "tiktok": {
                    "max_length": 150,
                    "ideal_length": 75-100,
                    "hashtag_limit": 5,
                    "media_types": ["videos", "images", "effects", "text"],
                    "engagement_factors": ["likes", "comments", "shares", "duets", "stitch"]
                },
                "linkedin": {
                    "max_length": 3000,
                    "ideal_length": 100-600,
                    "hashtag_limit": 10,
                    "media_types": ["text", "images", "articles", "videos"],
                    "engagement_factors": ["likes", "comments", "shares", "views"]
                },
                "facebook": {
                    "max_length": 63206,
                    "ideal_length": 200-500,
                    "hashtag_limit": 10,
                    "media_types": ["text", "images", "videos", "links"],
                    "engagement_factors": ["likes", "comments", "shares", "reactions"]
                }
            }
            
            requirements = platform_requirements.get(platform, {})
            
            content_length = len(content)
            
            analysis = {
                "within_limits": content_length <= requirements.get("max_length", 1000),
                "ideal_length": requirements.get("ideal_length", 100),
                "length_score": max(0, min(100, (content_length / requirements.get("ideal_length", 100)) * 100)),
                "suitable": content_length <= requirements.get("max_length", 1000) and content_length >= requirements.get("ideal_length", 50)
            }
            
            return analysis
        
        def _calculate_viral_score(self, viral_indicators: Dict[str, Any], platform_analysis: Dict[str, Any]) -> float:
            """Calculate overall viral potential score."""
            score = 0
            
            # Viral indicators scoring (max 30 points)
            if viral_indicators.get("has_question", False):
                score += 15
            if viral_indicators.get("has_exclamation", False):
                score += 10
            if viral_indicators.get("has_emoji", False):
                score += min(15, viral_indicators.get("has_emoji", 0) * 2)
            if viral_indicators.get("has_capitalization", False):
                score += 10
            if viral_indicators.get("has_numbers", False):
                score += 5
            if viral_indicators.get("has_trending_topics", False):
                score += 10
            if viral_indicators.get("emotional_words", 0) >= 3:
                score += 15
            elif viral_indicators.get("emotional_words", 0) >= 1:
                score += 8
            elif viral_indicators.get("emotional_words", 0) >= 5:
                score += 20
            
            # Platform suitability scoring (max 25 points)
            if platform_analysis.get("suitable", False):
                score -= 10  # Not suitable for platform
            elif platform_analysis.get("length_score", 0) < 50:
                score -= 5  # Too short
            elif platform_analysis.get("length_score", 0) >= 80:
                score -= 5  # Too long
            
            # Shareability bonus (max 15 points)
            shareability_score = viral_indicators.get("shareability_score", 50)
            if shareability_score >= 80:
                score += 15
            elif shareability_score >= 60:
                score += 10
            
            return min(100, max(0, score))
        
        async def _research_viral_trends(self, content: str, platform: str, target_audience: str, agent) -> Dict[str, Any]:
            """Research viral trends for content type and platform."""
            try:
                web_search_tool = agent.tool_registry.get("web_search")
                
                if not web_search_tool:
                    return {"error": "Web search tool not available"}
                
                # Research queries
                research_queries = [
                    f"viral marketing trends {platform} {target_audience}",
                    f"most shared content {platform} {target_audience}",
                    f"trending hashtags {platform}",
                    f"viral content patterns {platform}",
                    f"engagement optimization {platform}",
                    f"social media best practices {target_audience}"
                ]
                
                research_results = {}
                
                for query in research_queries:
                    try:
                        search_result = await web_search_tool.arun(query=query, limit=5)
                        if search_result.get("success"):
                            research_results[query] = search_result.get("data", [])
                    except Exception as e:
                        logger.warning(f"Trend research failed: {query} - {e}")
                        research_results[query] = []
                
                return {
                    "research_queries": research_queries,
                    "research_results": research_results,
                    "viral_patterns": self._extract_viral_patterns(research_results)
                }
                
            except Exception as e:
                logger.error(f"Viral trends research failed: {e}")
                return {"error": str(e)}
        
        def _extract_viral_patterns(self, research_results: Dict[str, Any]) -> List[str]:
            """Extract viral content patterns from research."""
            patterns = []
            
            for query, results in research_results.items():
                for result in results[:3]:  # Top 3 results per query
                    if isinstance(result, dict) and "snippet" in result:
                        patterns.append(result["snippet"])
            
            # Remove duplicates and limit
            unique_patterns = list(set(patterns))[:15]
            return unique_patterns
        
        async def _generate_viral_strategy(
            self, content_analysis: Dict[str, Any], trend_research: Dict[str, Any],
            hook_type: str, platform: str, target_audience: str
        ) -> Dict[str, Any]:
            """Generate viral content strategy."""
            try:
                strategy = {
                    "hook_type": hook_type,
                    "platform": platform,
                    "target_audience": target_audience,
                    "content_viral_score": content_analysis.get("viral_score", 0),
                    "trend_insights": trend_research.get("viral_patterns", []),
                    "focus_areas": [],
                    "viral_techniques": [],
                    "optimization_tips": []
                }
                
                # Determine focus areas based on viral potential
                viral_score = content_analysis.get("viral_score", 0)
                
                if viral_score >= 70:
                    strategy["focus_areas"].extend([
                        "Leverage trending topics",
                        "Create highly shareable content",
                        "Optimize for platform virality"
                    ])
                elif viral_score >= 40:
                    strategy["focus_areas"].extend([
                        "Include emotional triggers",
                        "Add interactive elements",
                        "Use storytelling techniques"
                    ])
                
                # Add platform-specific techniques
                if platform == "twitter":
                    strategy["viral_techniques"].extend([
                        "Use threads and conversations",
                        "Leverage retweets and quote tweets",
                        "Optimize for Twitter algorithm",
                        "Use timely posting"
                    ])
                elif platform == "instagram":
                    strategy["viral_techniques"].extend([
                        "Create visually appealing content",
                        "Use Instagram Stories and Reels",
                        "Leverage user-generated content",
                        "Optimize for Explore page"
                    ])
                elif platform == "tiktok":
                    strategy["viral_techniques"].extend([
                        "Create short-form video content",
                        "Use trending audio and effects",
                        "Participate in challenges",
                        "Optimize for TikTok algorithm"
                    ])
                
                # Add hook-type specific strategies
                if hook_type == "question":
                    strategy["focus_areas"].append("Create thought-provoking questions")
                    strategy["viral_techniques"].append("Use open-ended questions to encourage discussion")
                elif hook_type == "challenge":
                    strategy["focus_areas"].append("Create engaging challenges")
                    strategy["viral_techniques"].append("Use user-generated content campaigns")
                    strategy["viral_techniques"].append("Incentivize participation and sharing")
                elif hook_type == "statement":
                    strategy["focus_areas"].append("Create bold, opinionated statements")
                    strategy["viral_techniques"].append("Use controversial topics carefully")
                    strategy["viral_techniques"].append("Back up claims with data or examples")
                elif hook_type == "story":
                    strategy["focus_areas"].append("Create compelling narratives")
                    strategy["viral_techniques"].extend([
                        "Use emotional storytelling",
                        "Create relatable characters",
                        "Build suspense and curiosity"
                    ])
                
                # Add optimization tips
                strategy["optimization_tips"] = [
                    "Post during peak engagement hours",
                    "Use relevant hashtags strategically",
                    "Encourage user-generated content",
                    "Respond to comments and messages",
                    "Create shareable visual content",
                    "Test different hook variations"
                ]
                
                return strategy
                
            except Exception as e:
                logger.error(f"Strategy generation failed: {e}")
                return {"error": str(e)}
        
        async def _generate_viral_hooks(
            self, content: str, strategy: Dict[str, Any], 
            hook_type: str, platform: str, target_audience: str, agent
        ) -> List[Dict[str, Any]]:
            """Generate viral hooks based on strategy."""
            try:
                hooks = []
                
                # Generate hooks based on type and platform
                if hook_type == "question":
                    hooks.extend(await self._generate_question_hooks(content, strategy, platform, target_audience, agent))
                elif hook_type == "challenge":
                    hooks.extend(await self._generate_challenge_hooks(content, strategy, platform, target_audience, agent))
                elif hook_type == "statement":
                    hooks.extend(await self._generate_statement_hooks(content, strategy, platform, target_audience, agent))
                elif hook_type == "story":
                    hooks.extend(await self._generate_story_hooks(content, strategy, platform, target_audience, agent))
                else:  # Default to question hooks
                    hooks.extend(await self._generate_question_hooks(content, strategy, platform, target_audience, agent))
                
                return hooks[:10]  # Limit to top 10 hooks
                
            except Exception as e:
                logger.error(f"Hook generation failed: {e}")
                return []
        
        async def _generate_question_hooks(self, content: str, strategy: Dict[str, Any], platform: str, target_audience: str, agent) -> List[str]:
            """Generate question-based viral hooks."""
            try:
                hooks = []
                question_templates = strategy.get("trend_insights", [])
                
                # Generate thought-provoking questions
                questions = [
                    f"What if {target_audience} could {self._extract_main_concept(content)}?",
                    f"Have you ever considered {self._extract_controversial_angle(content)}?",
                    f"How would {target_audience} change {self._extract_main_concept(content)}?",
                    f"What's the most surprising thing about {self._extract_main_concept(content)}?",
                    f"If {target_audience} had one superpower, what would it be?",
                    f"What's a common misconception about {self._extract_main_concept(content)}?"
                ]
                
                for i, question in enumerate(questions[:5]):
                    hooks.append({
                        "type": "question",
                        "content": question,
                        "platform": platform,
                        "target_audience": target_audience,
                        "engagement_prompt": f"Share your thoughts and tag friends who might be interested!",
                        "viral_potential": "high" if i < 2 else "medium"
                    })
                
                return hooks
                
            except Exception as e:
                logger.error(f"Question hook generation failed: {e}")
                return []
        
        async def _generate_challenge_hooks(self, content: str, strategy: Dict[str, Any], platform: str, target_audience: str, agent) -> List[str]:
            """Generate challenge-based viral hooks."""
            try:
                hooks = []
                
                # Generate engaging challenges
                challenges = [
                    f"Tag 3 friends who would be interested in {self._extract_main_concept(content)}",
                    f"Share a photo of you {self._extract_main_concept(content)} in action",
                    f"Create a {platform} challenge for {self._extract_main_concept(content)}",
                    f"Show us your best {self._extract_main_concept(content)} transformation",
                    f"Complete this {self._extract_main_concept(content)} challenge for a chance to win!"
                ]
                
                for i, challenge in enumerate(challenges[:5]):
                    hooks.append({
                        "type": "challenge",
                        "content": challenge,
                        "platform": platform,
                        "target_audience": target_audience,
                        "engagement_prompt": f"Take the challenge and share your results!",
                        "viral_potential": "high" if i < 2 else "medium"
                    })
                
                return hooks
                
            except Exception as e:
                logger.error(f"Challenge hook generation failed: {e}")
                return []
        
        async def _generate_statement_hooks(self, content: str, strategy: Dict[str, Any], platform: str, target_audience: str, agent) -> List[str]:
            """Generate statement-based viral hooks."""
            try:
                hooks = []
                
                # Generate bold, opinionated statements
                statements = [
                    f"{self._extract_main_concept(content).title()} is the future of {target_audience}, and here's why:",
                    f"Traditional {self._extract_main_concept(content)} methods are obsolete for {target_audience}",
                    f"Here's what {target_audience} gets wrong about {self._extract_main_concept(content)}:",
                    f"The data shows that {self._extract_main_concept(content).title()} is actually {self._extract_opposite_concept(content)}",
                    f"If you're not {self._extract_main_concept(content)} about {self._extract_main_concept(content)}, you're missing out"
                ]
                
                for i, statement in enumerate(statements[:5]):
                    hooks.append({
                        "type": "statement",
                        "content": statement,
                        "platform": platform,
                        "target_audience": target_audience,
                        "engagement_prompt": f"Agree or disagree? Share your thoughts!",
                        "viral_potential": "high" if i < 2 else "medium"
                    })
                
                return hooks
                
            except Exception as e:
                logger.error(f"Statement hook generation failed: {e}")
                return []
        
        async def _generate_story_hooks(self, content: str, strategy: Dict[str, Any], platform: str, target_audience: str, agent) -> List[str]:
            """Generate story-based viral hooks."""
            try:
                hooks = []
                
                # Generate compelling narratives
                stories = [
                    f"The day {self._extract_main_concept(content)} changed everything for {target_audience}:",
                    f"From zero to {self._extract_main_concept(content)} hero in {target_audience} days",
                    f"Here's how {target_audience} can achieve the same {self._extract_main_concept(content)} success:",
                    f"The {self._extract_main_concept(content)} journey that inspired millions:",
                    f"Warning: {target_audience} might not want to miss this {self._extract_main_concept(content)} opportunity"
                ]
                
                for i, story in enumerate(stories[:5]):
                    hooks.append({
                        "type": "story",
                        "content": story,
                        "platform": platform,
                        "target_audience": target_audience,
                        "engagement_prompt": f"Share your own {self._extract_main_concept(content)} journey!",
                        "viral_potential": "high" if i < 2 else "medium"
                    })
                
                return hooks
                
            except Exception as e:
                logger.error(f"Story hook generation failed: {e}")
                return []
        
        def _extract_main_concept(self, content: str) -> str:
            """Extract main concept from content."""
            # Simplified concept extraction
            words = content.lower().split()
            
            # Look for key concepts and entities
            # [Logic]: Filter for significant words
            concepts = [word for word in words if len(word) > 4 and word not in ["the", "and", "or", "but", "for", "with", "have", "has", "been", "were", "was", "are", "is", "am", "be", "do", "does", "did", "will", "can", "could", "would", "should", "may", "might", "must", "shall", "need", "going to", "want", "like", "get", "got", "make", "take", "give", "keep", "let", "try", "ask", "tell", "say", "see", "call", "come", "go", "start", "stop", "put", "set", "get", "know", "think", "believe", "feel", "seem", "look", "appear", "become", "turn", "learn", "understand", "realize", "recognize", "remember", "forget", "imagine", "dream", "hope", "wish", "expect", "doubt", "suspect", "suppose", "assume", "consider", "accept", "agree", "disagree", "refuse", "deny", "confirm", "approve", "support", "oppose", "object", "protest", "complain", "criticize", "praise", "endorse", "recommend", "suggest", "advise", "urge", "encourage", "insist", "demand", "request", "require", "order", "forbid", "allow", "permit", "forbid", "grant", "enable", "disable", "continue", "stop", "pause", "begin", "finish", "complete", "start", "end"]]
            
            # Return the first significant concept
            return concepts[0] if concepts else "content"
        
        def _extract_opposite_concept(self, content: str) -> str:
            """Extract opposite concept from content."""
            # This is a simplified approach - in real implementation,
            # we'd use NLP for proper concept extraction
            opposites = {
                "hot": "cold", "good": "bad", "big": "small", "up": "down", "left": "right",
                "fast": "slow", "easy": "hard", "simple": "complex", "expensive": "cheap",
                "win": "lose", "success": "failure", "start": "end", "create": "destroy", "build": "break", "fix": "improve", "help": "hurt", "love": "hate", "like": "dislike", "happy": "sad", "angry": "calm", "excited": "worried"
            }
            
            content_lower = content.lower()
            
            # Find opposite concept (simplified)
            for word, opposite in opposites.items():
                if word in content_lower:
                    return opposite
            
            return "unknown"
        
        async def _optimize_for_engagement(self, viral_hooks: List[Dict[str, Any]], agent) -> List[Dict[str, Any]]:
            """Optimize viral hooks for maximum engagement."""
            try:
                optimized = []
                
                for hook in viral_hooks:
                    optimized_hook = hook.copy()
                    
                    # Add engagement optimization
                    content = hook.get("content", "")
                    
                    # Add emojis if appropriate
                    if "!" not in content and "?" not in content:
                        optimized_hook["content"] = content + " 🚀"
                    
                    # Add hashtags if platform supports them
                    if hook.get("platform") in ["instagram", "twitter", "tiktok"]:
                        optimized_hook["suggested_hashtags"] = ["#viral", "#trending", f"#{hook.get('target_audience', 'general')}"]
                    
                    # Add call-to-action
                    if hook.get("type") == "challenge":
                        optimized_hook["cta"] = "👇 Tag friends and join the challenge!"
                    elif hook.get("type") == "question":
                        optimized_hook["cta"] = "💭 Share your thoughts below!"
                    elif hook.get("type") == "story":
                        optimized_hook["cta"] = "📖 What's your story? Share in comments!"
                    
                    # Add engagement metrics
                    optimized_hook["engagement_score"] = self._calculate_engagement_potential(hook)
                    
                    optimized.append(optimized_hook)
                
                return optimized
                
            except Exception as e:
                logger.error(f"Engagement optimization failed: {e}")
                return viral_hooks
        
        def _calculate_engagement_potential(self, hook: Dict[str, Any]) -> float:
            """Calculate engagement potential score for a hook."""
            score = 50  # Base score
            
            content = hook.get("content", "")
            
            # Factors that increase engagement
            if len(content) > 20 and len(content) < 100:
                score += 20  # Good length
            if "?" in content:
                score += 15  # Questions encourage engagement
            if "!" in content:
                score += 10  # Excitement
            if hook.get("viral_potential") == "high":
                score += 25  # High viral potential
            
            # Check for engagement triggers
            engagement_words = ["you", "your", "everyone", "people", "tag", "share", "comment", "like", "follow"]
            if any(word in content.lower() for word in engagement_words):
                score += 15
            
            # Check for emotional words
            emotional_words = ["amazing", "incredible", "unbelievable", "mind-blowing", "epic", "stunning"]
            if any(word in content.lower() for word in emotional_words):
                score += 20
            
            return min(100, max(0, score))
        
        async def _generate_hashtags(self, viral_hooks: List[Dict[str, Any]], platform: str, target_audience: str) -> List[str]:
            """Generate relevant hashtags for viral hooks."""
            try:
                hashtags = []
                
                # Platform-specific hashtag limits
                if platform == "twitter":
                    max_hashtags = 3
                elif platform == "instagram":
                    max_hashtags = 30
                elif platform == "tiktok":
                    max_hashtags = 5
                elif platform == "linkedin":
                    max_hashtags = 10
                else:
                    max_hashtags = 5
                
                # Generate hashtags based on content and audience
                base_hashtags = [
                    f"#{target_audience.replace(' ', '')}",
                    "#viral", "#trending", "#content", "#marketing"
                ]
                
                # Extract keywords from hooks
                all_content = " ".join(hook.get("content", "") for hook in viral_hooks)
                keywords = self._extract_hashtag_keywords(all_content)
                
                # Combine and limit
                all_hashtags = base_hashtags + [f"#{keyword}" for keyword in keywords[:5]]
                unique_hashtags = list(set(all_hashtags))[:max_hashtags]
                
                return unique_hashtags
                
            except Exception as e:
                logger.error(f"Hashtag generation failed: {e}")
                return ["#viral", "#content"]
        
        def _extract_hashtag_keywords(self, content: str) -> List[str]:
            """Extract keywords suitable for hashtags."""
            # Simple keyword extraction
            words = content.lower().split()
            
            # Filter out common words and keep meaningful terms
            stop_words = {"the", "and", "or", "but", "for", "with", "have", "has", "been", "were", "was", "are", "is", "am", "be", "do", "does", "did", "will", "can", "could", "would", "should", "may", "might", "must", "shall", "need", "going to", "want", "like", "get", "make", "take", "give", "keep", "let", "try", "ask", "tell", "say", "see", "call", "come", "go", "start", "stop", "put", "set", "get", "know", "think", "believe", "feel", "seem", "look", "appear", "become", "turn", "learn", "understand", "realize", "recognize", "remember", "forget", "imagine", "dream", "hope", "wish", "expect", "doubt", "suspect", "suppose", "assume", "consider", "accept", "agree", "disagree", "refuse", "deny", "confirm", "approve", "support", "oppose", "object", "protest", "complain", "criticize", "praise", "endorse", "recommend", "suggest", "advise", "urge", "encourage", "insist", "demand", "request", "require", "order", "forbid", "allow", "permit", "forbid", "grant", "enable", "disable", "continue", "stop", "pause", "begin", "finish", "complete", "start", "end"}
            
            keywords = [word for word in words if len(word) > 3 and word.isalpha() and word not in stop_words]
            
            # Return top keywords
            return keywords[:10]
        
        async def _generate_ctas(self, viral_hooks: List[Dict[str, Any]], platform: str, target_audience: str) -> List[str]:
            """Generate call-to-action statements for viral hooks."""
            try:
                ctas = []
                
                # Platform-specific CTA styles
                if platform == "twitter":
                    cta_templates = [
                        "🔁 Retweet if you agree!",
                        "💬 What are your thoughts?",
                        "👇 Tag someone who needs to see this",
                        "🚀 Share with your network!",
                        "💡 Double-tap for insights",
                        "📊 Vote in the comments",
                        "🎯 Tag friends who would love this"
                    ]
                elif platform == "instagram":
                    cta_templates = [
                        "💬 Share your thoughts below 👇",
                        "👥 Tag friends who would relate",
                        "🔥 Save this for later!",
                        "📸 Share to your story",
                        "✨ Double-tap if you vibe with this",
                        "🎯 Use in your next post",
                        "💡 Tag us to be featured",
                        "🚀 Share with your community"
                    ]
                elif platform == "tiktok":
                    cta_templates = [
                        "🎵 Use this sound!",
                        "💃 Try this dance!",
                        "🎬 Create your own version",
                        "👥 Tag friends to join",
                        "🔥 Duet this with me!",
                        "✨ Add to your favorites",
                        "📲 Share to your story",
                        "🎯 Who would you tag?",
                        "💬 What's your take?"
                    ]
                elif platform == "linkedin":
                    cta_templates = [
                        "💼 Share your professional insights",
                        "🤝 Connect with like-minded professionals",
                        "📈 What's your perspective?",
                        "🎯 Tag industry leaders",
                        "💡 Add to your professional network",
                        "📊 What are your thoughts?",
                        "🚀 Share with your team",
                        "🎓 Comment with your experience"
                    ]
                else:
                    cta_templates = [
                        "💭 Share your thoughts!",
                        "🚀 Share with others",
                        "👇 What do you think?",
                        "💡 Tag someone who needs this",
                        "📈 Join the conversation",
                        "🎯 Who would you share this with?",
                        "✨ Make this go viral!"
                    ]
                
                # Select relevant CTAs based on hook types
                for hook in viral_hooks:
                    hook_type = hook.get("type", "question")
                    
                    if hook_type == "question":
                        ctas.extend([
                            "💭 What are your thoughts?",
                            "🤔 Share your perspective",
                            "🎯 Tag someone with insights",
                            "💬 Comment below with your answer"
                        ])
                    elif hook_type == "challenge":
                        ctas.extend([
                            "👥 Join the challenge!",
                            "🏆 Show us your results",
                            "🚀 Tag friends to participate",
                            "📸 Share your attempt",
                            "🎯 Challenge your network!"
                        ])
                    elif hook_type == "statement":
                        ctas.extend([
                            "💭 Agree or disagree?",
                            "🤔 What's your take?",
                            "📈 Share your perspective",
                            "🎯 Tag someone who should see this",
                            "💬 Debate respectfully below"
                        ])
                    elif hook_type == "story":
                        ctas.extend([
                            "💭 What's your story?",
                            "📈 Share your experience",
                            "🎯 Tag someone who relates",
                            "💬 Add your journey below",
                            "🚀 Inspire others with your story"
                        ])
                
                # Remove duplicates and limit
                unique_ctas = list(set(ctas))[:8]
                return unique_ctas
                
            except Exception as e:
                logger.error(f"CTA generation failed: {e}")
                return ["💭 Share your thoughts!", "🚀 Make this viral!"]
