"""
Reinforcement Learning Optimization for OCR
Implements unit test reward-based optimization following OlmOCR approach
"""

import asyncio
import json
import random
import time
from typing import Dict, List, Optional, Tuple, Any, Union
from dataclasses import dataclass, asdict
from datetime import datetime
import numpy as np
from collections import defaultdict, deque

from .models import OCRModelResult, ModelCapabilities, DocumentCharacteristics
from .model_implementations import ModelFactory


@dataclass
class TestCase:
    """Test case for OCR optimization."""
    id: str
    document_data: bytes
    filename: str
    expected_text: str
    language: str
    complexity: str
    document_type: str
    metadata: Dict[str, Any]


@dataclass
class TestResult:
    """Result of OCR model on test case."""
    test_case_id: str
    model_name: str
    extracted_text: str
    confidence: float
    processing_time: float
    reward: float
    passed: bool
    error_message: Optional[str]


@dataclass
class OptimizationState:
    """State of optimization process."""
    model_name: str
    generation: int
    population_size: int
    mutation_rate: float
    crossover_rate: float
    elite_size: int
    best_fitness: float
    average_fitness: float
    convergence_threshold: float
    max_generations: int


class UnitTestGenerator:
    """Generates synthetic test cases for OCR optimization."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_templates = self._initialize_test_templates()
        self.language_distributions = self._initialize_language_distributions()
        self.complexity_levels = ["simple", "moderate", "complex", "very_complex"]
        self.document_types = ["pdf", "image", "form", "invoice", "receipt"]

    def _initialize_test_templates(self) -> Dict[str, Dict]:
        """Initialize test case templates."""
        return {
            "simple_text": {
                "patterns": ["Hello world", "Test document", "Sample text"],
                "length_range": (10, 100),
                "complexity": "simple"
            },
            "business_document": {
                "patterns": ["Invoice #", "Date:", "Total:", "Amount:"],
                "length_range": (50, 500),
                "complexity": "moderate"
            },
            "technical_document": {
                "patterns": ["Algorithm", "Function", "Variable", "Parameter"],
                "length_range": (100, 1000),
                "complexity": "complex"
            },
            "multilingual": {
                "patterns": ["Hello", "Bonjour", "Hola", "Guten Tag"],
                "length_range": (50, 300),
                "complexity": "moderate"
            },
            "tabular_data": {
                "patterns": ["| Name | Age |", "| John | 25 |", "| Jane | 30 |"],
                "length_range": (100, 800),
                "complexity": "complex"
            }
        }

    def _initialize_language_distributions(self) -> Dict[str, float]:
        """Initialize language probability distributions."""
        return {
            "eng": 0.4,
            "spa": 0.15,
            "fra": 0.1,
            "deu": 0.1,
            "chi_sim": 0.1,
            "jpn": 0.05,
            "kor": 0.05,
            "ara": 0.03,
            "hin": 0.02
        }

    async def generate_test_cases(self, domain_documents: List[Dict[str, Any]], count: int = 100) -> List[TestCase]:
        """Generate synthetic test cases based on domain documents."""
        test_cases = []
        
        for i in range(count):
            # Select template
            template_name = random.choice(list(self.test_templates.keys()))
            template = self.test_templates[template_name]
            
            # Generate content
            content = self._generate_content(template)
            
            # Select language
            language = self._select_language()
            
            # Create test case
            test_case = TestCase(
                id=f"test_{i}_{int(time.time())}",
                document_data=self._create_synthetic_document(content, template),
                filename=f"synthetic_{i}.pdf",
                expected_text=content,
                language=language,
                complexity=template["complexity"],
                document_type=random.choice(self.document_types),
                metadata={
                    "template": template_name,
                    "generation_time": datetime.utcnow().isoformat(),
                    "content_length": len(content)
                }
            )
            
            test_cases.append(test_case)
        
        return test_cases

    def _generate_content(self, template: Dict[str, Any]) -> str:
        """Generate synthetic content based on template."""
        patterns = template["patterns"]
        min_length, max_length = template["length_range"]
        
        content_parts = []
        current_length = 0
        
        while current_length < min_length:
            pattern = random.choice(patterns)
            content_parts.append(pattern)
            current_length += len(pattern)
            
            # Add some variation
            if random.random() < 0.3:
                content_parts.append(f" {random.randint(1, 1000)}")
                current_length += 8
        
        # Trim to max length if needed
        content = " ".join(content_parts)
        if len(content) > max_length:
            content = content[:max_length].rsplit(" ", 1)[0]
        
        return content

    def _select_language(self) -> str:
        """Select language based on distribution."""
        languages = list(self.language_distributions.keys())
        weights = list(self.language_distributions.values())
        return np.random.choice(languages, p=weights)

    def _create_synthetic_document(self, content: str, template: Dict[str, Any]) -> bytes:
        """Create synthetic document data (placeholder)."""
        # In production, would use actual document generation
        # For now, return content as bytes
        return content.encode('utf-8')


class BinaryRewardCalculator:
    """Calculates binary rewards for OCR optimization."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.accuracy_weight = config.get("accuracy_weight", 0.7)
       .speed_weight = config.get("speed_weight", 0.2)
       .confidence_weight = config.get("confidence_weight", 0.1)
        self.accuracy_threshold = config.get("accuracy_threshold", 0.8)
        self.speed_threshold = config.get("speed_threshold", 5.0)  # seconds

    def calculate_reward(self, test_case: TestCase, result: OCRModelResult) -> float:
        """Calculate binary reward for OCR result."""
        # Calculate accuracy
        accuracy = self._calculate_accuracy(test_case.expected_text, result.extracted_text)
        
        # Calculate speed score
        speed_score = self._calculate_speed_score(result.processing_time)
        
        # Calculate confidence score
        confidence_score = result.confidence_score
        
        # Combine scores
        reward = (
            accuracy * self.accuracy_weight +
            speed_score * self.speed_weight +
            confidence_score * self.confidence_weight
        )
        
        return reward

    def _calculate_accuracy(self, expected: str, actual: str) -> float:
        """Calculate accuracy between expected and actual text."""
        if not expected and not actual:
            return 1.0
        if not expected or not actual:
            return 0.0
        
        # Simple character-level accuracy
        expected_chars = set(expected.lower())
        actual_chars = set(actual.lower())
        
        intersection = expected_chars.intersection(actual_chars)
        union = expected_chars.union(actual_chars)
        
        return len(intersection) / len(union) if union else 0.0

    def _calculate_speed_score(self, processing_time: float) -> float:
        """Calculate speed score based on processing time."""
        if processing_time <= self.speed_threshold:
            return 1.0
        else:
            # Linear decay after threshold
            return max(0.0, 1.0 - (processing_time - self.speed_threshold) / self.speed_threshold)


class GroupRelativePolicyOptimization:
    """Group Relative Policy Optimization for OCR model improvement."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.population_size = config.get("population_size", 28)
        self.elite_size = config.get("elite_size", 4)
        self.mutation_rate = config.get("mutation_rate", 0.1)
        self.crossover_rate = config.get("crossover_rate", 0.8)
        self.max_generations = config.get("max_generations", 100)
        self.convergence_threshold = config.get("convergence_threshold", 0.001)

    async def optimize_model(self, base_model: str, test_cases: List[TestCase]) -> Dict[str, Any]:
        """Optimize OCR model using GRPO."""
        optimization_state = OptimizationState(
            model_name=base_model,
            generation=0,
            population_size=self.population_size,
            mutation_rate=self.mutation_rate,
            crossover_rate=self.crossover_rate,
            elite_size=self.elite_size,
            best_fitness=0.0,
            average_fitness=0.0,
            convergence_threshold=self.convergence_threshold,
            max_generations=self.max_generations
        )
        
        # Initialize population
        population = self._initialize_population(base_model)
        
        # Evolution loop
        for generation in range(self.max_generations):
            optimization_state.generation = generation
            
            # Evaluate population
            fitness_scores = await self._evaluate_population(population, test_cases)
            
            # Update statistics
            optimization_state.best_fitness = max(fitness_scores)
            optimization_state.average_fitness = np.mean(fitness_scores)
            
            # Check convergence
            if self._check_convergence(fitness_scores, optimization_state):
                break
            
            # Selection and reproduction
            population = self._evolve_population(population, fitness_scores)
        
        return {
            "optimized_model": population[0],  # Best individual
            "final_fitness": optimization_state.best_fitness,
            "generations": optimization_state.generation,
            "converged": optimization_state.generation < self.max_generations
        }

    def _initialize_population(self, base_model: str) -> List[Dict[str, Any]]:
        """Initialize population of model configurations."""
        population = []
        
        for i in range(self.population_size):
            # Create individual with mutations
            individual = self._create_individual(base_model, i)
            population.append(individual)
        
        return population

    def _create_individual(self, base_model: str, index: int) -> Dict[str, Any]:
        """Create individual model configuration."""
        # Base configuration
        base_config = {
            "model_name": base_model,
            "confidence_threshold": 0.8,
            "preprocessing_enabled": True,
            "enhancement_level": "medium",
            "timeout_seconds": 30,
            "retry_attempts": 3
        }
        
        # Apply mutations
        if index > 0:  # Keep first individual as baseline
            mutations = self._apply_mutations(base_config)
            base_config.update(mutations)
        
        return base_config

    def _apply_mutations(self, config: Dict[str, Any]) -> Dict[str, Any]:
        """Apply random mutations to configuration."""
        mutations = {}
        
        # Mutate confidence threshold
        if random.random() < self.mutation_rate:
            mutations["confidence_threshold"] = np.clip(
                config["confidence_threshold"] + np.random.normal(0, 0.1),
                0.5, 1.0
            )
        
        # Mutate preprocessing
        if random.random() < self.mutation_rate:
            mutations["preprocessing_enabled"] = not config["preprocessing_enabled"]
        
        # Mutate enhancement level
        if random.random() < self.mutation_rate:
            levels = ["low", "medium", "high"]
            current_level = config.get("enhancement_level", "medium")
            mutations["enhancement_level"] = random.choice(
                [l for l in levels if l != current_level]
            )
        
        # Mutate timeout
        if random.random() < self.mutation_rate:
            mutations["timeout_seconds"] = np.clip(
                config["timeout_seconds"] + np.random.normal(0, 5),
                10, 60
            )
        
        return mutations

    async def _evaluate_population(self, population: List[Dict[str, Any]], test_cases: List[TestCase]) -> List[float]:
        """Evaluate fitness of entire population."""
        fitness_scores = []
        
        for individual in population:
            # Evaluate individual on test cases
            individual_fitness = await self._evaluate_individual(individual, test_cases)
            fitness_scores.append(individual_fitness)
        
        return fitness_scores

    async def _evaluate_individual(self, individual: Dict[str, Any], test_cases: List[TestCase]) -> float:
        """Evaluate fitness of individual configuration."""
        total_reward = 0.0
        evaluated_cases = 0
        
        # Sample test cases for efficiency
        sample_size = min(len(test_cases), 20)
        sampled_cases = random.sample(test_cases, sample_size)
        
        for test_case in sampled_cases:
            try:
                # Simulate OCR processing with individual configuration
                result = await self._simulate_ocr_processing(test_case, individual)
                
                # Calculate reward
                reward_calculator = BinaryRewardCalculator(self.config)
                reward = reward_calculator.calculate_reward(test_case, result)
                
                total_reward += reward
                evaluated_cases += 1
                
            except Exception as e:
                # Penalize configurations that cause errors
                total_reward -= 0.5
                evaluated_cases += 1
        
        return total_reward / evaluated_cases if evaluated_cases > 0 else 0.0

    async def _simulate_ocr_processing(self, test_case: TestCase, config: Dict[str, Any]) -> OCRModelResult:
        """Simulate OCR processing with configuration."""
        # Simulate processing time based on configuration
        base_time = 2.0
        if config.get("preprocessing_enabled", True):
            base_time += 0.5
        
        enhancement_level = config.get("enhancement_level", "medium")
        if enhancement_level == "high":
            base_time += 1.0
        elif enhancement_level == "low":
            base_time -= 0.3
        
        # Simulate confidence based on threshold
        base_confidence = 0.8
        confidence_threshold = config.get("confidence_threshold", 0.8)
        
        # Add some noise
        confidence = np.clip(
            base_confidence + np.random.normal(0, 0.1),
            confidence_threshold - 0.1, 1.0
        )
        
        # Simulate text extraction
        extracted_text = test_case.expected_text
        if confidence < 0.7:
            # Add errors for low confidence
            extracted_text = self._introduce_errors(extracted_text, confidence)
        
        return OCRModelResult(
            model_name=config["model_name"],
            extracted_text=extracted_text,
            confidence_score=confidence,
            processing_time=base_time,
            structured_data=None,
            page_count=1,
            detected_language=test_case.language,
            metadata=config
        )

    def _introduce_errors(self, text: str, confidence: float) -> str:
        """Introduce OCR errors based on confidence."""
        error_rate = (1.0 - confidence) * 0.2  # Max 20% error rate
        
        words = text.split()
        for i in range(len(words)):
            if random.random() < error_rate:
                # Introduce error
                if random.random() < 0.5:
                    # Character substitution
                    words[i] = self._substitute_characters(words[i])
                else:
                    # Word omission
                    if i < len(words) - 1:
                        words[i] = ""
        
        return " ".join(words).strip()

    def _substitute_characters(self, word: str) -> str:
        """Substitute characters to simulate OCR errors."""
        substitutions = {
            'o': '0', 'l': '1', 'i': '1', 's': '5', 'e': '3',
            'b': '8', 'g': '9', 'z': '2', 'a': '4'
        }
        
        result = []
        for char in word.lower():
            if char in substitutions and random.random() < 0.3:
                result.append(substitutions[char])
            else:
                result.append(char)
        
        return "".join(result)

    def _check_convergence(self, fitness_scores: List[float], state: OptimizationState) -> bool:
        """Check if optimization has converged."""
        if len(fitness_scores) < 2:
            return False
        
        # Check if improvement is minimal
        max_fitness = max(fitness_scores)
        if max_fitness - state.best_fitness < state.convergence_threshold:
            return True
        
        # Check if variance is low
        variance = np.var(fitness_scores)
        if variance < state.convergence_threshold:
            return True
        
        return False

    def _evolve_population(self, population: List[Dict[str, Any]], fitness_scores: List[float]) -> List[Dict[str, Any]]:
        """Evolve population using selection, crossover, and mutation."""
        # Sort by fitness
        sorted_indices = np.argsort(fitness_scores)[::-1]
        
        # Select elite
        elite_indices = sorted_indices[:self.elite_size]
        new_population = [population[i] for i in elite_indices]
        
        # Generate offspring
        while len(new_population) < self.population_size:
            # Tournament selection
            parent1 = self._tournament_selection(population, fitness_scores)
            parent2 = self._tournament_selection(population, fitness_scores)
            
            # Crossover
            if random.random() < self.crossover_rate:
                offspring = self._crossover(parent1, parent2)
            else:
                offspring = parent1.copy()
            
            # Mutation
            offspring = self._apply_mutations(offspring)
            new_population.append(offspring)
        
        return new_population[:self.population_size]

    def _tournament_selection(self, population: List[Dict[str, Any]], fitness_scores: List[float], tournament_size: int = 3) -> Dict[str, Any]:
        """Tournament selection."""
        tournament_indices = random.sample(range(len(population)), min(tournament_size, len(population)))
        tournament_fitness = [fitness_scores[i] for i in tournament_indices]
        winner_index = tournament_indices[np.argmax(tournament_fitness)]
        return population[winner_index].copy()

    def _crossover(self, parent1: Dict[str, Any], parent2: Dict[str, Any]) -> Dict[str, Any]:
        """Crossover two parent configurations."""
        offspring = {}
        
        # Uniform crossover for each parameter
        for key in parent1.keys():
            if key == "model_name":
                offspring[key] = parent1[key]  # Keep same model
            elif random.random() < 0.5:
                offspring[key] = parent1[key]
            else:
                offspring[key] = parent2[key]
        
        return offspring


class RLOCROptimizer:
    """Reinforcement Learning OCR Optimizer using unit test rewards."""

    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.test_generator = UnitTestGenerator(config.get("test_generator", {}))
        self.reward_calculator = BinaryRewardCalculator(config.get("reward_calculator", {}))
        self.optimizer = GroupRelativePolicyOptimization(config.get("optimizer", {}))
        
        # Optimization history
        self.optimization_history = []
        self.best_configurations = {}

    async def optimize_model(self, base_model: str, domain_documents: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Optimize OCR model for specific domain using RL."""
        start_time = time.time()
        
        try:
            # Generate test cases
            test_cases = await self.test_generator.generate_test_cases(domain_documents)
            
            # Run optimization
            optimization_result = await self.optimizer.optimize_model(base_model, test_cases)
            
            # Record optimization
            optimization_record = {
                "model_name": base_model,
                "domain": self._infer_domain(domain_documents),
                "test_cases_count": len(test_cases),
                "best_fitness": optimization_result["final_fitness"],
                "generations": optimization_result["generations"],
                "converged": optimization_result["converged"],
                "optimized_config": optimization_result["optimized_model"],
                "optimization_time": time.time() - start_time,
                "timestamp": datetime.utcnow().isoformat()
            }
            
            self.optimization_history.append(optimization_record)
            self.best_configurations[f"{base_model}_{optimization_record['domain']}"] = optimization_result["optimized_model"]
            
            return optimization_record
            
        except Exception as e:
            raise Exception(f"Optimization failed for model {base_model}: {str(e)}")

    def _infer_domain(self, domain_documents: List[Dict[str, Any]]) -> str:
        """Infer domain from documents."""
        # Simple heuristic based on document content
        if not domain_documents:
            return "general"
        
        # Check for domain-specific keywords
        content = str(domain_documents).lower()
        
        if any(keyword in content for keyword in ["invoice", "bill", "payment", "total"]):
            return "financial"
        elif any(keyword in content for keyword in ["medical", "patient", "diagnosis", "treatment"]):
            return "medical"
        elif any(keyword in content for keyword in ["legal", "contract", "agreement", "court"]):
            return "legal"
        elif any(keyword in content for keyword in ["technical", "engineering", "algorithm", "specification"]):
            return "technical"
        else:
            return "general"

    def get_optimization_history(self) -> List[Dict[str, Any]]:
        """Get optimization history."""
        return self.optimization_history.copy()

    def get_best_configuration(self, model_name: str, domain: str) -> Optional[Dict[str, Any]]:
        """Get best configuration for model and domain."""
        key = f"{model_name}_{domain}"
        return self.best_configurations.get(key)

    def calculate_optimization_metrics(self) -> Dict[str, Any]:
        """Calculate optimization metrics."""
        if not self.optimization_history:
            return {}
        
        total_optimizations = len(self.optimization_history)
        successful_optimizations = sum(1 for record in self.optimization_history if record["converged"])
        
        average_fitness = np.mean([record["best_fitness"] for record in self.optimization_history])
        average_generations = np.mean([record["generations"] for record in self.optimization_history])
        average_time = np.mean([record["optimization_time"] for record in self.optimization_history])
        
        return {
            "total_optimizations": total_optimizations,
            "success_rate": successful_optimizations / total_optimizations,
            "average_fitness": average_fitness,
            "average_generations": average_generations,
            "average_optimization_time": average_time,
            "domains_covered": len(set(record["domain"] for record in self.optimization_history)),
            "models_optimized": len(set(record["model_name"] for record in self.optimization_history))
        }
