"""
Radar Integration Service - Maps signals to moves and generates actionable intelligence
"""
import logging
from datetime import datetime
from typing import Any, Dict, List, Optional

from inference import InferenceProvider
from models.radar_models import (
    Dossier,
    Signal,
    SignalCategory,
    SignalMoveMapping,
    MoveObjective,
    MoveStage,
)

logger = logging.getLogger("raptorflow.radar_integration")


class RadarIntegrationService:
    """
    Service for integrating Radar signals with campaign moves.
    Handles signal-to-move mapping, experiment generation, and dossier creation.
    """

    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="strategic")
        
        # Enhanced signal to objective mapping with weighted scoring
        self.objective_mapping = {
            SignalCategory.OFFER: {
                MoveObjective.ACQUIRE: 0.8,
                MoveObjective.MONETIZE: 0.9,
                MoveObjective.ACTIVATE: 0.3,
            },
            SignalCategory.HOOK: {
                MoveObjective.ACQUIRE: 0.9,
                MoveObjective.ACTIVATE: 0.4,
            },
            SignalCategory.PROOF: {
                MoveObjective.ACTIVATE: 0.8,
                MoveObjective.RETAIN: 0.7,
                MoveObjective.ACQUIRE: 0.6,
            },
            SignalCategory.CTA: {
                MoveObjective.ACQUIRE: 0.9,
                MoveObjective.CONVERT: 0.8,
                MoveObjective.ACTIVATE: 0.5,
            },
            SignalCategory.OBJECTION: {
                MoveObjective.RETAIN: 0.8,
                MoveObjective.ACTIVATE: 0.6,
            },
            SignalCategory.TREND: {
                MoveObjective.ACQUIRE: 0.7,
                MoveObjective.ACTIVATE: 0.8,
            },
        }
        
        # Enhanced channel mapping with priority scoring
        self.channel_mapping = {
            SignalCategory.OFFER: [
                {"channel": "landing_page", "priority": 0.9},
                {"channel": "pricing_page", "priority": 0.8},
                {"channel": "email", "priority": 0.6},
                {"channel": "sales_page", "priority": 0.7},
            ],
            SignalCategory.HOOK: [
                {"channel": "social", "priority": 0.9},
                {"channel": "linkedin", "priority": 0.8},
                {"channel": "twitter", "priority": 0.7},
                {"channel": "blog", "priority": 0.6},
            ],
            SignalCategory.PROOF: [
                {"channel": "case_study", "priority": 0.9},
                {"channel": "testimonial", "priority": 0.8},
                {"channel": "review_site", "priority": 0.7},
                {"channel": "social_proof", "priority": 0.6},
            ],
            SignalCategory.CTA: [
                {"channel": "website", "priority": 0.8},
                {"channel": "email", "priority": 0.7},
                {"channel": "ads", "priority": 0.6},
                {"channel": "landing_page", "priority": 0.8},
            ],
            SignalCategory.OBJECTION: [
                {"channel": "faq", "priority": 0.9},
                {"channel": "sales_page", "priority": 0.8},
                {"channel": "demo", "priority": 0.7},
                {"channel": "support", "priority": 0.6},
            ],
            SignalCategory.TREND: [
                {"channel": "blog", "priority": 0.8},
                {"channel": "content", "priority": 0.7},
                {"channel": "social", "priority": 0.6},
                {"channel": "newsletter", "priority": 0.5},
            ],
        }

    async def map_signals_to_moves(
        self, 
        signals: List[Signal], 
        campaign_objectives: List[MoveObjective],
        tenant_id: str
    ) -> List[SignalMoveMapping]:
        """
        Map signals to campaign objectives and stages.
        Returns relevance-scored mappings.
        """
        mappings = []
        
        for signal in signals:
            # Get weighted objectives for this signal category
            category_objectives = self.objective_mapping.get(signal.category, {})
            
            for objective in campaign_objectives:
                if objective in category_objectives:
                    # Calculate enhanced relevance score
                    base_relevance = category_objectives[objective]
                    signal_relevance = self._calculate_signal_relevance(signal, objective)
                    
                    # Combine base relevance with signal-specific factors
                    total_relevance = (base_relevance * 0.6) + (signal_relevance * 0.4)
                    
                    if total_relevance >= 0.5:  # Only include relevant mappings
                        mapping = SignalMoveMapping(
                            signal_id=signal.id,
                            move_id="",  # Will be populated when move is created
                            objective=objective,
                            stage=self._determine_stage(signal, objective),
                            channel=self._determine_channel(signal),
                            relevance_score=total_relevance
                        )
                        mappings.append(mapping)
        
        logger.info(f"Created {len(mappings)} signal-to-move mappings")
        return mappings

    async def generate_experiment_ideas(
        self, 
        signal: Signal, 
        objective: MoveObjective,
        stage: MoveStage,
        channel: str
    ) -> List[str]:
        """Generate experiment ideas based on a signal."""
        prompt = f"""
        Generate 3 specific experiment ideas based on this competitive signal:
        
        Signal: {signal.content}
        Category: {signal.category.value}
        Campaign Objective: {objective.value}
        Stage: {stage.value}
        Channel: {channel}
        
        Each experiment should be:
        - Specific and actionable
        - Testable within 2 weeks
        - Directly addresses the signal
        
        Return as JSON list:
        [
            "Experiment idea 1",
            "Experiment idea 2", 
            "Experiment idea 3"
        ]
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            ideas = self._parse_llm_response(response.content)
            return ideas[:3]  # Ensure max 3 ideas
        except Exception as e:
            logger.error(f"Error generating experiment ideas: {e}")
            return []

    async def create_dossier(
        self, 
        campaign_id: str,
        signals: List[Signal],
        tenant_id: str
    ) -> Dossier:
        """Create an intelligence dossier from signals."""
        try:
            # Group signals by category
            by_category = {}
            for signal in signals:
                if signal.category not in by_category:
                    by_category[signal.category] = []
                by_category[signal.category].append(signal)
            
            # Generate dossier summary
            summary = await self._generate_dossier_summary(signals, by_category)
            
            # Generate hypotheses
            hypotheses = await self._generate_hypotheses(signals, by_category)
            
            # Generate experiment recommendations
            experiments = await self._generate_experiment_recommendations(signals)
            
            # Extract copy snippets
            copy_snippets = await self._extract_copy_snippets(signals)
            
            # Generate market narrative
            market_narrative = await self._generate_market_narrative(signals, by_category)
            
            dossier = Dossier(
                tenant_id=tenant_id,
                campaign_id=campaign_id,
                title=f"Intelligence Dossier - {datetime.utcnow().strftime('%Y-%m-%d')}",
                summary=summary,
                pinned_signals=[signal.id for signal in signals],
                hypotheses=hypotheses,
                recommended_experiments=experiments,
                copy_snippets=copy_snippets,
                market_narrative=market_narrative
            )
            
            return dossier

        except Exception as e:
            logger.error(f"Error creating dossier: {e}")
            # Return basic dossier
            return Dossier(
                tenant_id=tenant_id,
                campaign_id=campaign_id,
                title=f"Basic Dossier - {datetime.utcnow().strftime('%Y-%m-%d')}",
                summary=["Error generating full dossier"],
                pinned_signals=[signal.id for signal in signals]
            )

    async def generate_action_suggestions(self, signal: Signal) -> List[str]:
        """Generate specific action suggestions for a signal."""
        prompt = f"""
        Generate 3 specific actions for this competitive signal:
        
        Signal: {signal.content}
        Category: {signal.category.value}
        Strength: {signal.strength.value}
        
        Actions should be:
        - Immediately actionable
        - Specific (not generic)
        - Appropriate for the signal strength
        
        Return as JSON list:
        [
            "Action 1: Specific task",
            "Action 2: Specific task",
            "Action 3: Specific task"
        ]
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            actions = self._parse_llm_response(response.content)
            return actions[:3]
        except Exception as e:
            logger.error(f"Error generating action suggestions: {e}")
            return []

    def _calculate_signal_relevance(self, signal: Signal, objective: MoveObjective) -> float:
        """Calculate relevance score between signal and objective."""
        base_relevance = 0.5
        
        # Category-objective alignment
        if objective in self.objective_mapping.get(signal.category, []):
            base_relevance += 0.3
        
        # Strength factor
        strength_factor = {
            "high": 0.2,
            "medium": 0.1,
            "low": 0.0,
        }.get(signal.strength.value, 0.1)
        
        # Freshness factor
        freshness_factor = {
            "fresh": 0.1,
            "warm": 0.05,
            "stale": 0.0,
        }.get(signal.freshness.value, 0.05)
        
        total_relevance = base_relevance + strength_factor + freshness_factor
        return min(total_relevance, 1.0)

    def _determine_stage(self, signal: Signal, objective: MoveObjective) -> MoveStage:
        """Determine the most relevant stage for a signal-objective pair."""
        stage_mapping = {
            SignalCategory.OFFER: MoveStage.CONVERSION,
            SignalCategory.HOOK: MoveStage.ATTENTION,
            SignalCategory.PROOF: MoveStage.CONSIDERATION,
            SignalCategory.CTA: MoveStage.CONVERSION,
            SignalCategory.OBJECTION: MoveStage.CONSIDERATION,
            SignalCategory.TREND: MoveStage.ATTENTION,
        }
        
        return stage_mapping.get(signal.category, MoveStage.ATTENTION)

    def _determine_channel(self, signal: Signal) -> str:
        """Determine the most relevant channel for a signal using priority scoring."""
        channel_options = self.channel_mapping.get(signal.category, [{"channel": "website", "priority": 0.5}])
        
        # Sort by priority and return the highest priority channel
        sorted_channels = sorted(channel_options, key=lambda x: x["priority"], reverse=True)
        return sorted_channels[0]["channel"]

    async def _generate_dossier_summary(
        self, 
        signals: List[Signal], 
        by_category: Dict[SignalCategory, List[Signal]]
    ) -> List[str]:
        """Generate dossier summary."""
        summary = []
        
        # Overall summary
        summary.append(f"Analyzed {len(signals)} signals across {len(by_category)} categories")
        
        # Category summaries
        for category, category_signals in by_category.items():
            high_strength = len([s for s in category_signals if s.strength.value == "high"])
            summary.append(f"{category.value.title()}: {len(category_signals)} signals, {high_strength} high strength")
        
        return summary

    async def _generate_hypotheses(
        self, 
        signals: List[Signal], 
        by_category: Dict[SignalCategory, List[Signal]]
    ) -> List[str]:
        """Generate strategic hypotheses from signals."""
        hypotheses = []
        
        for category, category_signals in by_category.items():
            if len(category_signals) >= 2:  # Only generate hypotheses with multiple signals
                prompt = f"""
                Based on these {category.value} signals, generate 1 strategic hypothesis:
                
                Signals:
                {chr(10).join(f"- {signal.content}" for signal in category_signals[:3])}
                
                Hypothesis should be:
                - Strategic and actionable
                - Based on the pattern in signals
                - Testable
                
                Return as a single sentence.
                """
                
                try:
                    response = await self.llm.ainvoke(prompt)
                    hypothesis = response.content.strip()
                    if len(hypothesis) > 20:  # Ensure meaningful hypothesis
                        hypotheses.append(hypothesis)
                except Exception as e:
                    logger.error(f"Error generating hypothesis: {e}")
        
        return hypotheses[:5]  # Max 5 hypotheses

    async def _generate_experiment_recommendations(self, signals: List[Signal]) -> List[str]:
        """Generate experiment recommendations from strongest signals."""
        # Get top 5 strongest signals
        strongest_signals = sorted(
            signals, 
            key=lambda s: self._strength_to_numeric(s.strength), 
            reverse=True
        )[:5]
        
        experiments = []
        for signal in strongest_signals:
            experiments.append(f"Test response to: {signal.content[:50]}...")
        
        return experiments

    async def _extract_copy_snippets(self, signals: List[Signal]) -> List[Dict[str, str]]:
        """Extract useful copy snippets from signals."""
        snippets = []
        
        for signal in signals:
            if signal.category in [SignalCategory.HOOK, SignalCategory.PROOF, SignalCategory.CTA]:
                snippet = {
                    "category": signal.category.value,
                    "content": signal.content[:200],
                    "source": signal.source_competitor or "Unknown",
                    "strength": signal.strength.value
                }
                snippets.append(snippet)
        
        return snippets[:10]  # Max 10 snippets

    async def _generate_market_narrative(
        self, 
        signals: List[Signal], 
        by_category: Dict[SignalCategory, List[Signal]]
    ) -> Dict[str, str]:
        """Generate market narrative from signals."""
        narrative = {
            "believing": "Market is stable with incremental changes.",
            "overhyped": "AI-driven automation claims are exaggerated.",
            "underrated": "Personal human touch in B2B sales."
        }
        
        # Analyze trends to update narrative
        if SignalCategory.TREND in by_category:
            trend_signals = by_category[SignalCategory.TREND]
            if len(trend_signals) > 3:
                narrative["believing"] = "Rapid market evolution with new entrants."
        
        return narrative

    def _parse_llm_response(self, response: str) -> List[str]:
        """Parse LLM response for list of strings."""
        try:
            import json
            
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

    def _strength_to_numeric(self, strength) -> float:
        """Convert strength to numeric value."""
        mapping = {
            "low": 0.3,
            "medium": 0.6,
            "high": 0.9,
        }
        return mapping.get(strength.value if hasattr(strength, 'value') else strength, 0.5)
