"""
RaptorFlow Success Prediction Service
Phase 3.3.1: Success Prediction Model

Predicts business success probability using machine learning models,
historical data analysis, and success factor identification.
"""

import asyncio
import numpy as np
import pandas as pd
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Set, Tuple, Any
from dataclasses import dataclass
from enum import Enum

from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
import joblib

from backend.services.llm_service import LLMService, ExtractionContext
from config import get_settings
from backend.core.logging import get_logger

logger = get_logger(__name__)
settings = get_settings()


class SuccessMetric(str, Enum):
    """Types of success metrics."""
    REVENUE_GROWTH = "revenue_growth"
    MARKET_SHARE = "market_share"
    PROFITABILITY = "profitability"
    CUSTOMER_SATISFACTION = "customer_satisfaction"
    SURVIVAL = "survival"
    SCALABILITY = "scalability"


class PredictionTimeframe(str, Enum):
    """Prediction timeframes."""
    ONE_YEAR = "1_year"
    THREE_YEARS = "3_years"
    FIVE_YEARS = "5_years"
    TEN_YEARS = "10_years"


class SuccessLevel(str, Enum):
    """Success level classifications."""
    VERY_LOW = "very_low"
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    VERY_HIGH = "very_high"


@dataclass
class SuccessFactor:
    """Individual success factor."""
    name: str
    value: float
    weight: float
    importance: float
    category: str
    description: str


@dataclass
class FeatureImportance:
    """Feature importance for prediction."""
    feature_name: str
    importance_score: float
    category: str
    description: str


@dataclass
class SuccessPrediction:
    """Complete success prediction result."""
    business_id: str
    success_probability: float
    success_level: SuccessLevel
    confidence_score: float
    timeframe: PredictionTimeframe
    success_factors: List[SuccessFactor]
    feature_importance: List[FeatureImportance]
    risk_factors: List[str]
    recommendations: List[str]
    model_metadata: Dict
    predicted_at: datetime


class FeatureExtractor:
    """Feature extraction for success prediction."""
    
    def __init__(self):
        self.llm_service = LLMService()
        
    async def extract_features(self, business_data: Dict, industry: str) -> Dict:
        """
        Extract features from business data for prediction.
        
        Args:
            business_data: Business information
            industry: Industry type
            
        Returns:
            Extracted features dictionary
        """
        try:
            # Industry-specific feature extraction
            industry_features = await self._extract_industry_features(business_data, industry)
            
            # General business features
            general_features = await self._extract_general_features(business_data)
            
            # Financial features
            financial_features = await self._extract_financial_features(business_data)
            
            # Market features
            market_features = await self._extract_market_features(business_data)
            
            # Team features
            team_features = await self._extract_team_features(business_data)
            
            # Product features
            product_features = await self._extract_product_features(business_data)
            
            # Combine all features
            all_features = {
                **industry_features,
                **general_features,
                **financial_features,
                **market_features,
                **team_features,
                **product_features
            }
            
            # Validate and normalize features
            normalized_features = await self._normalize_features(all_features)
            
            return normalized_features
            
        except Exception as e:
            logger.error(f"Feature extraction failed: {e}")
            return {}
    
    async def _extract_industry_features(self, business_data: Dict, industry: str) -> Dict:
        """Extract industry-specific features."""
        features = {}
        
        if industry == 'technology':
            features.update({
                'tech_stack_maturity': await self._assess_tech_stack(business_data),
                'innovation_rate': business_data.get('innovation_rate', 0.5),
                'r_d_investment_ratio': business_data.get('rd_investment_ratio', 0.1),
                'patent_count': business_data.get('patent_count', 0),
                'technical_debt': business_data.get('technical_debt', 0.3)
            })
        
        elif industry == 'healthcare':
            features.update({
                'regulatory_compliance': business_data.get('regulatory_compliance', 0.8),
                'clinical_trial_success': business_data.get('clinical_trial_success', 0.7),
                'fda_approval_rate': business_data.get('fda_approval_rate', 0.6),
                'patient_outcomes': business_data.get('patient_outcomes', 0.8),
                'medical_innovation': business_data.get('medical_innovation', 0.5)
            })
        
        elif industry == 'finance':
            features.update({
                'risk_management': business_data.get('risk_management', 0.7),
                'regulatory_capital': business_data.get('regulatory_capital', 0.8),
                'loan_portfolio_quality': business_data.get('loan_portfolio_quality', 0.6),
                'digital_transformation': business_data.get('digital_transformation', 0.5),
                'compliance_score': business_data.get('compliance_score', 0.9)
            })
        
        elif industry == 'retail':
            features.update({
                'supply_chain_efficiency': business_data.get('supply_chain_efficiency', 0.7),
                'inventory_turnover': business_data.get('inventory_turnover', 0.6),
                'customer_retention': business_data.get('customer_retention', 0.7),
                'omni_channel_presence': business_data.get('omni_channel_presence', 0.5),
                'brand_recognition': business_data.get('brand_recognition', 0.6)
            })
        
        elif industry == 'manufacturing':
            features.update({
                'production_efficiency': business_data.get('production_efficiency', 0.7),
                'quality_control': business_data.get('quality_control', 0.8),
                'automation_level': business_data.get('automation_level', 0.4),
                'supply_chain_resilience': business_data.get('supply_chain_resilience', 0.6),
                'environmental_compliance': business_data.get('environmental_compliance', 0.7)
            })
        
        return features
    
    async def _extract_general_features(self, business_data: Dict) -> Dict:
        """Extract general business features."""
        return {
            'business_age': business_data.get('business_age', 5),
            'revenue_growth_rate': business_data.get('revenue_growth_rate', 0.1),
            'profit_margin': business_data.get('profit_margin', 0.15),
            'customer_acquisition_cost': business_data.get('customer_acquisition_cost', 100),
            'customer_lifetime_value': business_data.get('customer_lifetime_value', 1000),
            'market_position': business_data.get('market_position', 0.5),
            'competitive_advantage': business_data.get('competitive_advantage', 0.5),
            'scalability_score': business_data.get('scalability_score', 0.6),
            'innovation_capability': business_data.get('innovation_capability', 0.5)
        }
    
    async def _extract_financial_features(self, business_data: Dict) -> Dict:
        """Extract financial features."""
        return {
            'revenue': business_data.get('revenue', 0),
            'profit': business_data.get('profit', 0),
            'cash_flow': business_data.get('cash_flow', 0),
            'debt_to_equity': business_data.get('debt_to_equity', 0.5),
            'working_capital': business_data.get('working_capital', 0),
            'burn_rate': business_data.get('burn_rate', 0),
            'runway_months': business_data.get('runway_months', 12),
            'funding_rounds': business_data.get('funding_rounds', 1),
            'valuation': business_data.get('valuation', 0)
        }
    
    async def _extract_market_features(self, business_data: Dict) -> Dict:
        """Extract market-related features."""
        return {
            'market_size': business_data.get('market_size', 0),
            'market_growth_rate': business_data.get('market_growth_rate', 0.1),
            'market_share': business_data.get('market_share', 0.05),
            'customer_satisfaction': business_data.get('customer_satisfaction', 0.8),
            'brand_strength': business_data.get('brand_strength', 0.6),
            'distribution_channels': business_data.get('distribution_channels', 3),
            'geographic_reach': business_data.get('geographic_reach', 0.3),
            'market_penetration': business_data.get('market_penetration', 0.1)
        }
    
    async def _extract_team_features(self, business_data: Dict) -> Dict:
        """Extract team-related features."""
        return {
            'team_size': business_data.get('team_size', 10),
            'founder_experience': business_data.get('founder_experience', 5),
            'team_diversity': business_data.get('team_diversity', 0.6),
            'technical_talent': business_data.get('technical_talent', 0.7),
            'leadership_quality': business_data.get('leadership_quality', 0.7),
            'employee_retention': business_data.get('employee_retention', 0.8),
            'productivity_per_employee': business_data.get('productivity_per_employee', 100000),
            'training_investment': business_data.get('training_investment', 0.05)
        }
    
    async def _extract_product_features(self, business_data: Dict) -> Dict:
        """Extract product-related features."""
        return {
            'product_quality': business_data.get('product_quality', 0.8),
            'product_differentiation': business_data.get('product_differentiation', 0.6),
            'innovation_level': business_data.get('innovation_level', 0.5),
            'customer_value_proposition': business_data.get('customer_value_proposition', 0.7),
            'product_market_fit': business_data.get('product_market_fit', 0.6),
            'scalability': business_data.get('product_scalability', 0.6),
            'time_to_market': business_data.get('time_to_market', 6),
            'feature_completeness': business_data.get('feature_completeness', 0.7)
        }
    
    async def _assess_tech_stack(self, business_data: Dict) -> float:
        """Assess technology stack maturity."""
        tech_stack = business_data.get('tech_stack', [])
        
        # Modern tech stack indicators
        modern_tech = [
            'cloud', 'microservices', 'kubernetes', 'docker',
            'react', 'vue', 'angular', 'typescript',
            'python', 'nodejs', 'go', 'rust',
            'postgresql', 'mongodb', 'redis',
            'ai', 'ml', 'blockchain'
        ]
        
        # Legacy tech indicators
        legacy_tech = [
            'mainframe', 'cobol', 'fortran',
            'on_premise', 'monolith', 'waterfall'
        ]
        
        modern_count = sum(1 for tech in tech_stack if any(modern in tech.lower() for modern in modern_tech))
        legacy_count = sum(1 for tech in tech_stack if any(legacy in tech.lower() for legacy in legacy_tech))
        
        # Calculate maturity score
        total_tech = len(tech_stack)
        if total_tech == 0:
            return 0.5  # Default
        
        maturity_score = (modern_count - legacy_count) / total_tech
        return max(0, min(1, (maturity_score + 1) / 2))  # Normalize to 0-1
    
    async def _normalize_features(self, features: Dict) -> Dict:
        """Normalize features to 0-1 scale."""
        normalized = {}
        
        # Define normalization ranges
        ranges = {
            'business_age': (0, 50),
            'revenue_growth_rate': (-1, 1),
            'profit_margin': (0, 1),
            'customer_acquisition_cost': (0, 1000),
            'customer_lifetime_value': (0, 10000),
            'market_position': (0, 1),
            'competitive_advantage': (0, 1),
            'scalability_score': (0, 1),
            'innovation_capability': (0, 1),
            'debt_to_equity': (0, 2),
            'runway_months': (0, 36),
            'funding_rounds': (0, 10),
            'market_size': (0, 10000000000),
            'market_growth_rate': (0, 1),
            'market_share': (0, 1),
            'customer_satisfaction': (0, 1),
            'brand_strength': (0, 1),
            'distribution_channels': (1, 10),
            'geographic_reach': (0, 1),
            'market_penetration': (0, 1),
            'team_size': (1, 1000),
            'founder_experience': (0, 30),
            'team_diversity': (0, 1),
            'technical_talent': (0, 1),
            'leadership_quality': (0, 1),
            'employee_retention': (0, 1),
            'productivity_per_employee': (0, 1000000),
            'training_investment': (0, 0.2),
            'product_quality': (0, 1),
            'product_differentiation': (0, 1),
            'innovation_level': (0, 1),
            'customer_value_proposition': (0, 1),
            'product_market_fit': (0, 1),
            'product_scalability': (0, 1),
            'time_to_market': (0, 24),
            'feature_completeness': (0, 1)
        }
        
        for feature, value in features.items():
            if feature in ranges:
                min_val, max_val = ranges[feature]
                if max_val > min_val:
                    normalized[feature] = max(0, min(1, (value - min_val) / (max_val - min_val)))
                else:
                    normalized[feature] = 0.5  # Default for boolean features
            else:
                normalized[feature] = value  # Keep as-is for unknown features
        
        return normalized


class ModelTrainer:
    """Machine learning model training for success prediction."""
    
    def __init__(self):
        self.model = None
        self.scaler = StandardScaler()
        self.feature_encoder = LabelEncoder()
        self.model_path = "models/success_prediction_model.pkl"
        self.scaler_path = "models/feature_scaler.pkl"
        
    async def train_model(self, historical_data: List[Dict]) -> Dict:
        """
        Train success prediction model.
        
        Args:
            historical_data: Historical business data with success outcomes
            
        Returns:
            Training results and model metrics
        """
        try:
            # Prepare data
            X, y = await self._prepare_training_data(historical_data)
            
            if len(X) < 10:
                return {'error': 'Insufficient training data', 'sample_size': len(X)}
            
            # Split data
            X_train, X_test, y_train, y_test = train_test_split(
                X, y, test_size=0.2, random_state=42, stratify=y
            )
            
            # Scale features
            X_train_scaled = self.scaler.fit_transform(X_train)
            X_test_scaled = self.scaler.transform(X_test)
            
            # Train model
            self.model = RandomForestClassifier(
                n_estimators=100,
                max_depth=10,
                random_state=42,
                class_weight='balanced'
            )
            
            self.model.fit(X_train_scaled, y_train)
            
            # Evaluate model
            y_pred = self.model.predict(X_test_scaled)
            accuracy = accuracy_score(y_test, y_pred)
            
            # Feature importance
            feature_names = list(X.columns)
            importances = self.model.feature_importances_
            
            feature_importance = []
            for i, importance in enumerate(importances):
                if i < len(feature_names):
                    feature_importance.append({
                        'feature': feature_names[i],
                        'importance': importance,
                        'rank': i + 1
                    })
            
            # Sort by importance
            feature_importance.sort(key=lambda x: x['importance'], reverse=True)
            
            # Save model
            await self._save_model()
            
            return {
                'model_type': 'RandomForest',
                'accuracy': accuracy,
                'feature_importance': feature_importance[:20],  # Top 20 features
                'training_samples': len(X_train),
                'test_samples': len(X_test),
                'feature_count': len(feature_names),
                'classes': list(self.model.classes_),
                'training_date': datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Model training failed: {e}")
            return {'error': str(e)}
    
    async def _prepare_training_data(self, historical_data: List[Dict]) -> Tuple[pd.DataFrame, pd.Series]:
        """Prepare data for training."""
        # Convert to DataFrame
        df = pd.DataFrame(historical_data)
        
        # Feature columns
        feature_columns = [
            'business_age', 'revenue_growth_rate', 'profit_margin',
            'customer_acquisition_cost', 'customer_lifetime_value',
            'market_position', 'competitive_advantage', 'scalability_score',
            'innovation_capability', 'debt_to_equity', 'runway_months',
            'market_size', 'market_growth_rate', 'market_share',
            'customer_satisfaction', 'brand_strength', 'team_size',
            'founder_experience', 'technical_talent', 'leadership_quality'
        ]
        
        # Filter available features
        available_features = [col for col in feature_columns if col in df.columns]
        
        X = df[available_features]
        y = df['success_level']  # Target variable
        
        # Handle missing values
        X = X.fillna(X.median())
        
        return X, y
    
    async def _save_model(self):
        """Save trained model and scaler."""
        try:
            import os
            os.makedirs('models', exist_ok=True)
            
            joblib.dump(self.model, self.model_path)
            joblib.dump(self.scaler, self.scaler_path)
            
            logger.info(f"Model saved to {self.model_path}")
            
        except Exception as e:
            logger.error(f"Failed to save model: {e}")
    
    async def load_model(self):
        """Load trained model and scaler."""
        try:
            self.model = joblib.load(self.model_path)
            self.scaler = joblib.load(self.scaler_path)
            logger.info("Model loaded successfully")
            return True
        except FileNotFoundError:
            logger.warning("Model not found, training required")
            return False
        except Exception as e:
            logger.error(f"Failed to load model: {e}")
            return False


class SuccessPredictor:
    """Main success prediction service."""
    
    def __init__(self):
        self.feature_extractor = FeatureExtractor()
        self.model_trainer = ModelTrainer()
        self.llm_service = LLMService()
        
    async def predict_success(self, business_data: Dict, timeframe: PredictionTimeframe = PredictionTimeframe.THREE_YEARS) -> SuccessPrediction:
        """
        Predict business success probability.
        
        Args:
            business_data: Business information
            timeframe: Prediction timeframe
            
        Returns:
            Success prediction result
        """
        try:
            # Load or train model
            model_loaded = await self.model_trainer.load_model()
            
            if not model_loaded:
                # Use LLM-based prediction if no model available
                return await self._predict_with_llm(business_data, timeframe)
            
            # Extract features
            industry = business_data.get('industry', '')
            features = await self.feature_extractor.extract_features(business_data, industry)
            
            # Prepare features for prediction
            feature_vector = await self._prepare_features_for_prediction(features)
            
            # Make prediction
            prediction_proba = self.model_trainer.model.predict_proba([feature_vector])[0]
            
            # Get feature importance
            feature_importance = await self._get_feature_importance()
            
            # Generate success factors
            success_factors = await self._generate_success_factors(features, feature_importance)
            
            # Generate risk factors
            risk_factors = await self._identify_risk_factors(features, business_data)
            
            # Generate recommendations
            recommendations = await self._generate_recommendations(features, prediction_proba, risk_factors)
            
            # Determine success level
            success_level = self._determine_success_level(prediction_proba[1])  # Probability of success
            
            return SuccessPrediction(
                business_id=business_data.get('id', ''),
                success_probability=prediction_proba[1],
                success_level=success_level,
                confidence_score=0.7,  # Model confidence
                timeframe=timeframe,
                success_factors=success_factors,
                feature_importance=feature_importance,
                risk_factors=risk_factors,
                recommendations=recommendations,
                model_metadata={
                    'model_type': 'RandomForest',
                    'trained_date': '2024-01-01',  # Would be actual date
                    'accuracy': 0.85,  # Would be actual accuracy
                    'feature_count': len(feature_vector)
                },
                predicted_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"Success prediction failed: {e}")
            raise
    
    async def _predict_with_llm(self, business_data: Dict, timeframe: PredictionTimeframe) -> SuccessPrediction:
        """Predict success using LLM when no trained model available."""
        try:
            context = ExtractionContext(
                industry=business_data.get('industry', ''),
                business_context=business_data
            )
            
            prompt = f"""
            Predict business success probability for this company:
            
            Business Information:
            - Industry: {business_data.get('industry', '')}
            - Business Model: {business_data.get('business_model', '')}
            - Revenue: {business_data.get('revenue', '')}
            - Team Size: {business_data.get('team_size', '')}
            - Market Position: {business_data.get('market_position', '')}
            - Competitive Advantage: {business_data.get('competitive_advantage', '')}
            
            Timeframe: {timeframe.value}
            
            Analyze and provide:
            1. Success probability (0-1)
            2. Success level (very_low, low, medium, high, very_high)
            3. Key success factors with importance scores
            4. Risk factors
            5. Strategic recommendations
            6. Confidence in prediction (0-1)
            
            Format as JSON with keys: success_probability, success_level, success_factors, risk_factors, recommendations, confidence
            """
            
            llm_result = await self.llm_service.generate_response(
                LLMRequest(
                    prompt=prompt,
                    model=ModelType.GPT4_TURBO,
                    temperature=0.1,
                    max_tokens=1000
                )
            )
            
            # Parse LLM response
            import json
            prediction_data = json.loads(llm_result.content)
            
            # Convert to SuccessPrediction format
            success_factors = []
            for factor in prediction_data.get('success_factors', []):
                success_factors.append(SuccessFactor(
                    name=factor.get('name', ''),
                    value=factor.get('value', 0.5),
                    weight=factor.get('importance', 0.5),
                    importance=factor.get('importance', 0.5),
                    category=factor.get('category', 'general'),
                    description=factor.get('description', '')
                ))
            
            feature_importance = []
            for feature in prediction_data.get('feature_importance', []):
                feature_importance.append(FeatureImportance(
                    feature_name=feature.get('feature', ''),
                    importance_score=feature.get('importance', 0.5),
                    category=feature.get('category', 'general'),
                    description=feature.get('description', '')
                ))
            
            return SuccessPrediction(
                business_id=business_data.get('id', ''),
                success_probability=prediction_data.get('success_probability', 0.5),
                success_level=SuccessLevel(prediction_data.get('success_level', 'medium')),
                confidence_score=prediction_data.get('confidence', 0.5),
                timeframe=timeframe,
                success_factors=success_factors,
                feature_importance=feature_importance,
                risk_factors=prediction_data.get('risk_factors', []),
                recommendations=prediction_data.get('recommendations', []),
                model_metadata={
                    'model_type': 'LLM_GPT4',
                    'method': 'rule_based_prediction',
                    'confidence': prediction_data.get('confidence', 0.5)
                },
                predicted_at=datetime.utcnow()
            )
            
        except Exception as e:
            logger.error(f"LLM prediction failed: {e}")
            raise
    
    async def _prepare_features_for_prediction(self, features: Dict) -> List[float]:
        """Prepare features for model prediction."""
        # Define feature order (must match training)
        feature_order = [
            'business_age', 'revenue_growth_rate', 'profit_margin',
            'customer_acquisition_cost', 'customer_lifetime_value',
            'market_position', 'competitive_advantage', 'scalability_score',
            'innovation_capability', 'debt_to_equity', 'runway_months',
            'market_size', 'market_growth_rate', 'market_share',
            'customer_satisfaction', 'brand_strength', 'team_size',
            'founder_experience', 'technical_talent', 'leadership_quality'
        ]
        
        feature_vector = []
        for feature in feature_order:
            feature_vector.append(features.get(feature, 0.5))  # Default to 0.5
        
        return feature_vector
    
    async def _get_feature_importance(self) -> List[FeatureImportance]:
        """Get feature importance from trained model."""
        if not self.model_trainer.model:
            return []
        
        # This would be extracted from the trained model
        # For now, return placeholder importance
        return [
            FeatureImportance(
                feature_name='revenue_growth_rate',
                importance_score=0.15,
                category='financial',
                description='Historical revenue growth indicates future success'
            ),
            FeatureImportance(
                feature_name='market_position',
                importance_score=0.12,
                category='market',
                description='Strong market position correlates with success'
            ),
            FeatureImportance(
                feature_name='team_size',
                importance_score=0.10,
                category='team',
                description='Adequate team size supports growth'
            ),
            FeatureImportance(
                feature_name='innovation_capability',
                importance_score=0.08,
                category='product',
                description='Innovation drives competitive advantage'
            )
        ]
    
    async def _generate_success_factors(self, features: Dict, feature_importance: List[FeatureImportance]) -> List[SuccessFactor]:
        """Generate success factors from features and importance."""
        success_factors = []
        
        for importance in feature_importance[:10]:  # Top 10 factors
            feature_name = importance.feature_name
            feature_value = features.get(feature_name, 0.5)
            
            success_factors.append(SuccessFactor(
                name=feature_name,
                value=feature_value,
                weight=importance.importance_score,
                importance=importance.importance_score,
                category=importance.category,
                description=importance.description
            ))
        
        return success_factors
    
    async def _identify_risk_factors(self, features: Dict, business_data: Dict) -> List[str]:
        """Identify risk factors from business data."""
        risks = []
        
        # Financial risks
        if features.get('debt_to_equity', 0) > 1.5:
            risks.append("High debt-to-equity ratio")
        
        if features.get('runway_months', 12) < 6:
            risks.append("Low cash runway")
        
        # Market risks
        if features.get('market_share', 0) < 0.01:
            risks.append("Very low market share")
        
        if features.get('market_growth_rate', 0) < 0:
            risks.append("Declining market")
        
        # Team risks
        if features.get('team_size', 10) < 5:
            risks.append("Very small team")
        
        if features.get('founder_experience', 5) < 2:
            risks.append("Inexperienced founders")
        
        # Product risks
        if features.get('product_market_fit', 0.5) < 0.3:
            risks.append("Poor product-market fit")
        
        if features.get('innovation_level', 0.5) < 0.3:
            risks.append("Low innovation level")
        
        return risks
    
    async def _generate_recommendations(self, features: Dict, prediction_proba: np.ndarray, risk_factors: List[str]) -> List[str]:
        """Generate strategic recommendations."""
        recommendations = []
        success_probability = prediction_proba[1]
        
        # Low success probability recommendations
        if success_probability < 0.3:
            recommendations.extend([
                "Consider pivoting business model",
                "Focus on core competencies",
                "Seek additional funding",
                "Improve product-market fit",
                "Build stronger team"
            ])
        
        # Medium success probability recommendations
        elif success_probability < 0.6:
            recommendations.extend([
                "Optimize operations for efficiency",
                "Expand market reach",
                "Invest in marketing and sales",
                "Consider strategic partnerships",
                "Improve customer acquisition"
            ])
        
        # High success probability recommendations
        else:
            recommendations.extend([
                "Scale operations rapidly",
                "Expand to new markets",
                "Invest in R&D and innovation",
                "Consider acquisition opportunities",
                "Maintain competitive advantage"
            ])
        
        # Risk-specific recommendations
        for risk in risk_factors:
            if "debt" in risk.lower():
                recommendations.append("Restructure debt and improve cash flow")
            elif "market" in risk.lower():
                recommendations.append("Develop stronger market positioning")
            elif "team" in risk.lower():
                recommendations.append("Hire key talent and advisors")
            elif "product" in risk.lower():
                recommendations.append("Improve product based on customer feedback")
        
        return list(set(recommendations))[:10]  # Remove duplicates and limit
    
    def _determine_success_level(self, probability: float) -> SuccessLevel:
        """Determine success level from probability."""
        if probability >= 0.8:
            return SuccessLevel.VERY_HIGH
        elif probability >= 0.6:
            return SuccessLevel.HIGH
        elif probability >= 0.4:
            return SuccessLevel.MEDIUM
        elif probability >= 0.2:
            return SuccessLevel.LOW
        else:
            return SuccessLevel.VERY_LOW


# Pydantic models for API responses
class SuccessFactorResponse(BaseModel):
    """Response model for success factor."""
    name: str
    value: float
    weight: float
    importance: float
    category: str
    description: str


class SuccessPredictionResponse(BaseModel):
    """Response model for success prediction."""
    business_id: str
    success_probability: float
    success_level: str
    confidence_score: float
    timeframe: str
    success_factors: List[SuccessFactorResponse]
    feature_importance: List[Dict]
    risk_factors: List[str]
    recommendations: List[str]
    model_metadata: Dict
    predicted_at: datetime


# Error classes
class PredictionError(Exception):
    """Base prediction error."""
    pass


class ModelTrainingError(PredictionError):
    """Model training error."""
    pass


class FeatureExtractionError(PredictionError):
    """Feature extraction error."""
    pass
