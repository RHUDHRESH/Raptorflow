"""
RaptorFlow Contradiction Detection Service
Phase 2.1.1: Contradiction Detection Algorithm

Detects logical contradictions in extracted facts using semantic analysis,
LLM-based logical reasoning, and severity scoring with resolution suggestions.
"""

import asyncio
import numpy as np
from datetime import datetime
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import spacy

from backend.services.fact_extraction_service import ExtractedFact
from backend.services.llm_service import LLMService, ExtractionContext
from config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class ContradictionType(str, Enum):
    """Types of contradictions."""
    NUMERICAL = "numerical"
    TEMPORAL = "temporal"
    LOGICAL = "logical"
    CAUSAL = "causal"
    COMPARATIVE = "comparative"
    SCOPE = "scope"
    DEFINITIONAL = "definitional"


class SeverityLevel(str, Enum):
    """Severity levels for contradictions."""
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"


@dataclass
class Contradiction:
    """Individual contradiction detected."""
    id: str
    type: ContradictionType
    severity_score: float
    severity_level: SeverityLevel
    description: str
    conflicting_facts: List[str]
    topic: str
    context: Optional[Dict] = None
    resolution_suggestion: Optional[str] = None
    confidence: float
    created_at: datetime


@dataclass
class ContradictionAnalysis:
    """Complete contradiction analysis result."""
    contradictions: List[Contradiction]
    total_facts: int
    contradiction_rate: float
    analysis_timestamp: datetime
    topic_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    confidence_score: float


class SemanticAnalyzer:
    """Semantic similarity analysis for contradiction detection."""
    
    def __init__(self):
        self.nlp = None
        self.vectorizer = TfidfVectorizer(
            max_features=1000,
            stop_words='english',
            ngram_range=(1, 3)
        )
        
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not available for semantic analysis")
    
    async def find_semantic_conflicts(self, facts: List[ExtractedFact]) -> List[Dict]:
        """
        Find semantic conflicts using similarity analysis.
        
        Args:
            facts: List of facts to analyze
            
        Returns:
            List of semantic conflicts
        """
        if len(facts) < 2:
            return []
        
        # Group facts by topic
        topic_groups = await self._group_facts_by_topic(facts)
        conflicts = []
        
        for topic, topic_facts in topic_groups.items():
            if len(topic_facts) < 2:
                continue
            
            # Extract fact statements
            statements = [fact.statement for fact in topic_facts]
            
            # Create TF-IDF vectors
            try:
                tfidf_matrix = self.vectorizer.fit_transform(statements)
                similarity_matrix = cosine_similarity(tfidf_matrix)
                
                # Find high similarity pairs (potential contradictions)
                for i in range(len(topic_facts)):
                    for j in range(i + 1, len(topic_facts)):
                        similarity = similarity_matrix[i][j]
                        
                        # High similarity but different facts could indicate contradiction
                        if similarity > 0.8:  # Threshold for semantic similarity
                            fact1, fact2 = topic_facts[i], topic_facts[j]
                            
                            # Check if facts are actually contradictory
                            is_contradictory = await self._check_semantic_contradiction(
                                fact1.statement, fact2.statement
                            )
                            
                            if is_contradictory:
                                conflicts.append({
                                    'type': ContradictionType.SEMANTIC,
                                    'fact1_id': fact1.id,
                                    'fact2_id': fact2.id,
                                    'similarity': similarity,
                                    'statements': [fact1.statement, fact2.statement],
                                    'topic': topic,
                                    'confidence': min(fact1.confidence_score, fact2.confidence_score)
                                })
            
            except Exception as e:
                logger.error(f"Semantic analysis failed for topic {topic}: {e}")
                continue
        
        return conflicts
    
    async def _group_facts_by_topic(self, facts: List[ExtractedFact]) -> Dict[str, List[ExtractedFact]]:
        """Group facts by topic using entity extraction."""
        topic_groups = {}
        
        for fact in facts:
            # Extract key entities as topics
            if self.nlp:
                doc = self.nlp(fact.statement)
                entities = [ent.text for ent in doc.ents if ent.label_ in ['ORG', 'PRODUCT', 'PERSON', 'GPE']]
                
                if entities:
                    topic = entities[0]  # Use first entity as topic
                else:
                    # Use category as topic
                    topic = fact.category.value
            else:
                topic = fact.category.value
            
            if topic not in topic_groups:
                topic_groups[topic] = []
            
            topic_groups[topic].append(fact)
        
        return topic_groups
    
    async def _check_semantic_contradiction(self, statement1: str, statement2: str) -> bool:
        """Check if two statements are semantically contradictory."""
        # Look for contradictory pairs
        contradictory_pairs = [
            ('increase', 'decrease'),
            ('growth', 'decline'),
            ('profit', 'loss'),
            ('success', 'failure'),
            ('improve', 'worsen'),
            ('expand', 'shrink'),
            ('higher', 'lower'),
            ('more', 'less'),
            ('above', 'below'),
            ('over', 'under')
        ]
        
        stmt1_lower = statement1.lower()
        stmt2_lower = statement2.lower()
        
        for term1, term2 in contradictory_pairs:
            if term1 in stmt1_lower and term2 in stmt2_lower:
                return True
            if term2 in stmt1_lower and term1 in stmt2_lower:
                return True
        
        return False


class LogicalAnalyzer:
    """Logical contradiction analysis using LLM."""
    
    def __init__(self):
        self.llm_service = LLMService()
        
    async def analyze_logical_contradictions(self, facts: List[ExtractedFact]) -> List[Dict]:
        """
        Analyze logical contradictions using LLM reasoning.
        
        Args:
            facts: List of facts to analyze
            
        Returns:
            List of logical contradictions
        """
        if len(facts) < 2:
            return []
        
        # Group facts by topic for focused analysis
        topic_groups = {}
        for fact in facts:
            topic = fact.category.value
            if topic not in topic_groups:
                topic_groups[topic] = []
            topic_groups[topic].append(fact)
        
        contradictions = []
        
        for topic, topic_facts in topic_groups.items():
            if len(topic_facts) < 2:
                continue
            
            # Prepare fact data for LLM
            fact_data = []
            for fact in topic_facts:
                fact_data.append({
                    'statement': fact.statement,
                    'confidence': fact.confidence_score,
                    'source': fact.source_citation
                })
            
            try:
                # Use LLM to detect contradictions
                llm_result = await self.llm_service.detect_contradictions(fact_data)
                
                if 'contradictions' in llm_result:
                    for contradiction in llm_result['contradictions']:
                        contradictions.append({
                            'type': ContradictionType.LOGICAL,
                            'topic': topic,
                            'description': contradiction.get('description', ''),
                            'severity': contradiction.get('severity', 0.5),
                            'conflicting_facts': contradiction.get('conflicting_facts', []),
                            'resolution': contradiction.get('resolution', ''),
                            'confidence': 0.8  # LLM confidence
                        })
            
            except Exception as e:
                logger.error(f"Logical analysis failed for topic {topic}: {e}")
                continue
        
        return contradictions


class ContradictionMerger:
    """Merge and score contradictions from different analysis methods."""
    
    def __init__(self):
        self.type_weights = {
            ContradictionType.SEMANTIC: 0.3,
            ContradictionType.LOGICAL: 0.5,
            ContradictionType.NUMERICAL: 0.8,
            ContradictionType.TEMPORAL: 0.7,
            ContradictionType.CAUSAL: 0.6
        }
    
    async def merge_contradictions(self, semantic_conflicts: List[Dict], logical_conflicts: List[Dict]) -> List[Dict]:
        """
        Merge contradictions from different analysis methods.
        
        Args:
            semantic_conflicts: Conflicts from semantic analysis
            logical_conflicts: Conflicts from logical analysis
            
        Returns:
            Merged and scored contradictions
        """
        all_conflicts = semantic_conflicts + logical_conflicts
        
        # Group by fact pairs to avoid duplicates
        conflict_groups = {}
        
        for conflict in all_conflicts:
            # Create a key for fact pair
            fact_ids = tuple(sorted([conflict.get('fact1_id', ''), conflict.get('fact2_id', '')]))
            
            if fact_ids not in conflict_groups:
                conflict_groups[fact_ids] = []
            
            conflict_groups[fact_ids].append(conflict)
        
        merged_contradictions = []
        
        for fact_ids, conflicts in conflict_groups.items():
            if len(conflicts) == 1:
                # Single conflict, use as-is
                merged_contradictions.append(conflicts[0])
            else:
                # Multiple conflicts, merge them
                merged = await self._merge_multiple_conflicts(conflicts)
                merged_contradictions.append(merged)
        
        return merged_contradictions
    
    async def _merge_multiple_conflicts(self, conflicts: List[Dict]) -> Dict:
        """Merge multiple contradictions for the same fact pair."""
        if not conflicts:
            return {}
        
        # Calculate weighted severity
        total_severity = 0
        total_weight = 0
        all_types = set()
        all_descriptions = []
        all_conflicting_facts = []
        
        for conflict in conflicts:
            conflict_type = conflict.get('type', ContradictionType.LOGICAL)
            severity = conflict.get('severity', 0.5)
            confidence = conflict.get('confidence', 0.5)
            
            all_types.add(conflict_type)
            all_descriptions.append(conflict.get('description', ''))
            all_conflicting_facts.extend(conflict.get('conflicting_facts', []))
            
            weight = self.type_weights.get(conflict_type, 0.5)
            total_severity += severity * weight * confidence
            total_weight += weight * confidence
        
        # Calculate final severity
        final_severity = total_severity / total_weight if total_weight > 0 else 0
        
        # Determine severity level
        severity_level = self._determine_severity_level(final_severity)
        
        return {
            'type': 'merged',
            'severity': final_severity,
            'severity_level': severity_level,
            'description': '; '.join(filter(None, all_descriptions)),
            'conflicting_facts': list(set(all_conflicting_facts)),
            'confidence': np.mean([c.get('confidence', 0.5) for c in conflicts]),
            'source_types': list(all_types)
        }
    
    def _determine_severity_level(self, severity_score: float) -> SeverityLevel:
        """Determine severity level from score."""
        if severity_score >= 0.8:
            return SeverityLevel.CRITICAL
        elif severity_score >= 0.6:
            return SeverityLevel.HIGH
        elif severity_score >= 0.4:
            return SeverityLevel.MEDIUM
        else:
            return SeverityLevel.LOW


class ContradictionService:
    """Main contradiction detection service."""
    
    def __init__(self):
        self.semantic_analyzer = SemanticAnalyzer()
        self.logical_analyzer = LogicalAnalyzer()
        self.merger = ContradictionMerger()
        
    async def analyze_contradictions(self, facts: List[ExtractedFact]) -> ContradictionAnalysis:
        """
        Perform comprehensive contradiction analysis.
        
        Args:
            facts: List of extracted facts
            
        Returns:
            Complete contradiction analysis
        """
        if not facts or len(facts) < 2:
            return ContradictionAnalysis(
                contradictions=[],
                total_facts=0,
                contradiction_rate=0.0,
                analysis_timestamp=datetime.utcnow(),
                topic_distribution={},
                severity_distribution={},
                confidence_score=0.0
            )
        
        try:
            # Perform semantic and logical analysis in parallel
            semantic_task = self.semantic_analyzer.find_semantic_conflicts(facts)
            logical_task = self.logical_analyzer.analyze_logical_contradictions(facts)
            
            semantic_conflicts, logical_conflicts = await asyncio.gather(
                semantic_task, logical_task
            )
            
            # Merge contradictions
            merged_conflicts = await self.merger.merge_contradictions(
                semantic_conflicts, logical_conflicts
            )
            
            # Convert to Contradiction objects
            contradictions = []
            for i, conflict in enumerate(merged_conflicts):
                contradiction = Contradiction(
                    id=f"contradiction_{i}",
                    type=ContradictionType(conflict.get('type', 'logical')),
                    severity_score=conflict.get('severity', 0.5),
                    severity_level=conflict.get('severity_level', SeverityLevel.MEDIUM),
                    description=conflict.get('description', ''),
                    conflicting_facts=conflict.get('conflicting_facts', []),
                    topic=conflict.get('topic', 'unknown'),
                    context={
                        'analysis_method': 'merged_semantic_logical',
                        'confidence': conflict.get('confidence', 0.5)
                    },
                    resolution_suggestion=conflict.get('resolution', ''),
                    confidence=conflict.get('confidence', 0.5),
                    created_at=datetime.utcnow()
                )
                contradictions.append(contradiction)
            
            # Sort by severity
            contradictions.sort(key=lambda x: x.severity_score, reverse=True)
            
            # Calculate distributions
            topic_distribution = self._calculate_topic_distribution(contradictions)
            severity_distribution = self._calculate_severity_distribution(contradictions)
            overall_confidence = self._calculate_overall_confidence(contradictions)
            
            return ContradictionAnalysis(
                contradictions=contradictions,
                total_facts=len(facts),
                contradiction_rate=len(contradictions) / len(facts),
                analysis_timestamp=datetime.utcnow(),
                topic_distribution=topic_distribution,
                severity_distribution=severity_distribution,
                confidence_score=overall_confidence
            )
            
        except Exception as e:
            logger.error(f"Contradiction analysis failed: {e}")
            raise
    
    def _calculate_topic_distribution(self, contradictions: List[Contradiction]) -> Dict[str, int]:
        """Calculate distribution of contradictions by topic."""
        distribution = {}
        
        for contradiction in contradictions:
            topic = contradiction.topic
            distribution[topic] = distribution.get(topic, 0) + 1
        
        return distribution
    
    def _calculate_severity_distribution(self, contradictions: List[Contradiction]) -> Dict[str, int]:
        """Calculate distribution of contradictions by severity level."""
        distribution = {
            'low': 0,
            'medium': 0,
            'high': 0,
            'critical': 0
        }
        
        for contradiction in contradictions:
            level = contradiction.severity_level.value
            distribution[level] = distribution.get(level, 0) + 1
        
        return distribution
    
    def _calculate_overall_confidence(self, contradictions: List[Contradiction]) -> float:
        """Calculate overall confidence in contradiction analysis."""
        if not contradictions:
            return 0.0
        
        confidences = [c.confidence for c in contradictions]
        return np.mean(confidences)


# Pydantic models for API responses
class ContradictionResponse(BaseModel):
    """Response model for contradiction detection."""
    id: str
    type: str
    severity_score: float
    severity_level: str
    description: str
    conflicting_facts: List[str]
    topic: str
    resolution_suggestion: Optional[str] = None
    confidence: float


class ContradictionAnalysisResponse(BaseModel):
    """Response model for contradiction analysis."""
    contradictions: List[ContradictionResponse]
    total_facts: int
    contradiction_rate: float
    analysis_timestamp: datetime
    topic_distribution: Dict[str, int]
    severity_distribution: Dict[str, int]
    confidence_score: float


# Error classes
class ContradictionError(Exception):
    """Base contradiction detection error."""
    pass


class AnalysisError(ContradictionError):
    """Analysis error during contradiction detection."""
    pass


class MergerError(ContradictionError):
    """Error during contradiction merging."""
    pass
