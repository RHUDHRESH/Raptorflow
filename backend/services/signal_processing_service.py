"""
Signal Processing Service - Clustering, deduplication, and freshness management
"""
import hashlib
import logging
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional, Tuple

from difflib import SequenceMatcher
from inference import InferenceProvider
from models.radar_models import (
    Signal,
    SignalCategory,
    SignalCluster,
    SignalFreshness,
    SignalStrength,
)

logger = logging.getLogger("raptorflow.signal_processing")


class SignalProcessingService:
    """
    Service for processing signals: clustering, deduplication, and freshness management.
    Turns raw signals into actionable intelligence.
    """

    def __init__(self):
        self.llm = InferenceProvider.get_model(model_tier="reasoning")
        
        # Enhanced clustering thresholds with semantic awareness
        self.similarity_thresholds = {
            SignalCategory.OFFER: 0.85,  # High precision for pricing
            SignalCategory.HOOK: 0.75,   # Medium for creative content
            SignalCategory.PROOF: 0.8,   # High for customer evidence
            SignalCategory.CTA: 0.9,     # Very high for action language
            SignalCategory.OBJECTION: 0.85, # High for pain points
            SignalCategory.TREND: 0.7,   # Lower for market movements
        }
        
        # Content weight factors for strength calculation
        self.content_weights = {
            "pricing_mention": 0.3,
            "quantitative_result": 0.25,
            "customer_evidence": 0.2,
            "urgency_language": 0.15,
            "authority_claim": 0.1,
        }

    async def process_signals(
        self, 
        signals: List[Signal], 
        tenant_id: str
    ) -> Tuple[List[Signal], List[SignalCluster]]:
        """
        Process a batch of signals: deduplicate, cluster, and update freshness.
        Returns processed signals and clusters.
        """
        try:
            # Step 1: Update freshness
            signals = self._update_signal_freshness(signals)
            
            # Step 2: Deduplicate signals
            deduplicated_signals = await self._deduplicate_signals(signals)
            
            # Step 3: Cluster similar signals
            clusters = await self._cluster_signals(deduplicated_signals, tenant_id)
            
            # Step 4: Update signal strength based on clusters
            processed_signals = self._update_signal_strength(deduplicated_signals, clusters)
            
            logger.info(f"Processed {len(signals)} signals -> {len(processed_signals)} unique, {len(clusters)} clusters")
            return processed_signals, clusters

        except Exception as e:
            logger.error(f"Error processing signals: {e}")
            return signals, []

    async def deduplicate_against_existing(
        self, 
        new_signals: List[Signal], 
        existing_signals: List[Signal]
    ) -> List[Signal]:
        """Deduplicate new signals against existing database signals."""
        unique_signals = []
        
        for new_signal in new_signals:
            is_duplicate = False
            
            for existing_signal in existing_signals:
                if self._are_signals_similar(new_signal, existing_signal):
                    logger.debug(f"Found duplicate signal: {new_signal.title}")
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                unique_signals.append(new_signal)
        
        return unique_signals

    def _update_signal_freshness(self, signals: List[Signal]) -> List[Signal]:
        """Update freshness status for all signals."""
        updated_signals = []
        
        for signal in signals:
            freshness = self._calculate_freshness(signal.created_at)
            signal.freshness = freshness
            updated_signals.append(signal)
        
        return updated_signals

    async def _deduplicate_signals(self, signals: List[Signal]) -> List[Signal]:
        """Remove duplicate signals within the batch."""
        deduplicated = []
        
        for i, signal in enumerate(signals):
            is_duplicate = False
            
            # Check against already processed signals
            for processed_signal in deduplicated:
                if self._are_signals_similar(signal, processed_signal):
                    # Merge evidence instead of creating duplicate
                    processed_signal.evidence.extend(signal.evidence)
                    is_duplicate = True
                    break
            
            if not is_duplicate:
                deduplicated.append(signal)
        
        return deduplicated

    async def _cluster_signals(
        self, 
        signals: List[Signal], 
        tenant_id: str
    ) -> List[SignalCluster]:
        """Cluster similar signals by category and content."""
        clusters = []
        
        # Group signals by category
        by_category = {}
        for signal in signals:
            if signal.category not in by_category:
                by_category[signal.category] = []
            by_category[signal.category].append(signal)
        
        # Cluster within each category
        for category, category_signals in by_category.items():
            category_clusters = await self._cluster_category_signals(
                category_signals, category, tenant_id
            )
            clusters.extend(category_clusters)
        
        return clusters

    async def _cluster_category_signals(
        self, 
        signals: List[Signal], 
        category: SignalCategory, 
        tenant_id: str
    ) -> List[SignalCluster]:
        """Cluster signals within a specific category."""
        clusters = []
        unclustered = signals.copy()
        
        while unclustered:
            # Start a new cluster with the first unclustered signal
            cluster_seed = unclustered.pop(0)
            cluster_signals = [cluster_seed]
            
            # Find similar signals for this cluster
            similar_signals = []
            for signal in unclustered:
                if self._are_signals_similar(cluster_seed, signal):
                    similar_signals.append(signal)
            
            # Remove similar signals from unclustered
            for signal in similar_signals:
                unclustered.remove(signal)
                cluster_signals.append(signal)
            
            # Create cluster if we have multiple signals
            if len(cluster_signals) > 1:
                cluster = await self._create_cluster(cluster_signals, category, tenant_id)
                clusters.append(cluster)
                
                # Update signals with cluster ID
                for signal in cluster_signals:
                    signal.cluster_id = cluster.id
        
        return clusters

    async def _create_cluster(
        self, 
        signals: List[Signal], 
        category: SignalCategory, 
        tenant_id: str
    ) -> SignalCluster:
        """Create a signal cluster from similar signals."""
        # Generate cluster theme using LLM
        signal_contents = [signal.content for signal in signals]
        prompt = f"""
        Analyze these similar signals and create a concise theme/title:
        
        Category: {category.value}
        Signals:
        {chr(10).join(f"- {content}" for content in signal_contents[:5])}
        
        Create a 3-5 word theme that captures the common pattern.
        """
        
        try:
            response = await self.llm.ainvoke(prompt)
            theme = response.content.strip()[:50]
        except Exception as e:
            logger.error(f"Error generating cluster theme: {e}")
            theme = f"{category.value.title()} Pattern"
        
        # Calculate cluster strength (max of member signals)
        cluster_strength = max(
            self._strength_to_numeric(signal.strength) for signal in signals
        )
        cluster_strength_enum = self._numeric_to_strength(cluster_strength)
        
        cluster = SignalCluster(
            tenant_id=tenant_id,
            category=category,
            theme=theme,
            signal_count=len(signals),
            strength=cluster_strength_enum,
            signals=[signal.id for signal in signals]
        )
        
        return cluster

    def _are_signals_similar(self, signal1: Signal, signal2: Signal) -> bool:
        """Enhanced similarity detection with multiple factors."""
        # Different categories can't be similar
        if signal1.category != signal2.category:
            return False
        
        # Content similarity (primary factor)
        content_similarity = SequenceMatcher(
            None, signal1.content.lower(), signal2.content.lower()
        ).ratio()
        
        # Source similarity (if from same competitor, more likely duplicates)
        source_similarity = 0.0
        if signal1.source_competitor and signal2.source_competitor:
            if signal1.source_competitor.lower() == signal2.source_competitor.lower():
                source_similarity = 0.2
        
        # Title similarity
        title_similarity = 0.0
        if signal1.title and signal2.title:
            title_similarity = SequenceMatcher(
                None, signal1.title.lower(), signal2.title.lower()
            ).ratio() * 0.1
        
        # Combined similarity score
        total_similarity = content_similarity + source_similarity + title_similarity
        
        # Get threshold for this category
        threshold = self.similarity_thresholds.get(signal1.category, 0.75)
        
        return total_similarity >= threshold

    def _update_signal_strength(
        self, 
        signals: List[Signal], 
        clusters: List[SignalCluster]
    ) -> List[Signal]:
        """Update signal strength based on clustering and evidence."""
        updated_signals = []
        
        # Create cluster lookup
        cluster_lookup = {cluster.id: cluster for cluster in clusters}
        
        for signal in signals:
            # Base strength from evidence
            evidence_strength = min(len(signal.evidence) * 0.2, 0.6)
            
            # Cluster bonus (signals in clusters get strength boost)
            cluster_bonus = 0.0
            if signal.cluster_id and signal.cluster_id in cluster_lookup:
                cluster = cluster_lookup[signal.cluster_id]
                cluster_bonus = min(cluster.signal_count * 0.1, 0.3)
            
            # Freshness factor
            freshness_factor = self._freshness_to_numeric(signal.freshness)
            
            # Calculate total strength
            total_strength = evidence_strength + cluster_bonus + freshness_factor
            
            # Convert to enum
            if total_strength >= 0.7:
                signal.strength = SignalStrength.HIGH
            elif total_strength >= 0.4:
                signal.strength = SignalStrength.MEDIUM
            else:
                signal.strength = SignalStrength.LOW
            
            updated_signals.append(signal)
        
        return updated_signals

    def _calculate_freshness(self, created_at: datetime) -> SignalFreshness:
        """Calculate signal freshness based on creation time."""
        age = datetime.utcnow() - created_at
        
        if age.days <= 7:
            return SignalFreshness.FRESH
        elif age.days <= 30:
            return SignalFreshness.WARM
        else:
            return SignalFreshness.STALE

    def _strength_to_numeric(self, strength: SignalStrength) -> float:
        """Convert strength enum to numeric value."""
        mapping = {
            SignalStrength.LOW: 0.3,
            SignalStrength.MEDIUM: 0.6,
            SignalStrength.HIGH: 0.9,
        }
        return mapping.get(strength, 0.5)

    def _numeric_to_strength(self, numeric: float) -> SignalStrength:
        """Convert numeric value to strength enum."""
        if numeric >= 0.7:
            return SignalStrength.HIGH
        elif numeric >= 0.4:
            return SignalStrength.MEDIUM
        else:
            return SignalStrength.LOW

    def _freshness_to_numeric(self, freshness: SignalFreshness) -> float:
        """Convert freshness enum to numeric value."""
        mapping = {
            SignalFreshness.FRESH: 0.3,
            SignalFreshness.WARM: 0.2,
            SignalFreshness.STALE: 0.1,
        }
        return mapping.get(freshness, 0.2)

    async def get_signal_summary(
        self, 
        signals: List[Signal], 
        clusters: List[SignalCluster]
    ) -> Dict[str, Any]:
        """Generate a summary of processed signals."""
        summary = {
            "total_signals": len(signals),
            "by_category": {},
            "by_strength": {},
            "by_freshness": {},
            "clusters": len(clusters),
            "top_themes": []
        }
        
        # Count by category
        for signal in signals:
            category = signal.category.value
            summary["by_category"][category] = summary["by_category"].get(category, 0) + 1
        
        # Count by strength
        for signal in signals:
            strength = signal.strength.value
            summary["by_strength"][strength] = summary["by_strength"].get(strength, 0) + 1
        
        # Count by freshness
        for signal in signals:
            freshness = signal.freshness.value
            summary["by_freshness"][freshness] = summary["by_freshness"].get(freshness, 0) + 1
        
        # Top cluster themes
        sorted_clusters = sorted(clusters, key=lambda c: c.signal_count, reverse=True)
        summary["top_themes"] = [
            {"theme": cluster.theme, "count": cluster.signal_count}
            for cluster in sorted_clusters[:5]
        ]
        
        return summary
