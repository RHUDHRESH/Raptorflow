"""
Business Context Manifest (BCM) Reducer

Transforms raw onboarding step data into versioned, compact JSON manifests
with checksums for integrity verification using comprehensive JSON schema.
"""

import json
import hashlib
import logging
from datetime import datetime
from typing import Dict, Any, List, Optional, Union

try:
    import tiktoken

    TIKTOKEN_AVAILABLE = True
except ImportError:
    TIKTOKEN_AVAILABLE = False
    logging.warning("tiktoken not available, token counting will be disabled")

from ..schemas.bcm_schema import (
    BusinessContextManifest,
    CompanyInfo,
    ICPProfile,
    ICPPainPoint,
    ICPGoal,
    ICPObjection,
    ICPTriggerEvent,
    CompetitorInfo,
    PositioningDelta,
    BrandValues,
    BrandPersonality,
    MessagingValueProp,
    Tagline,
    KeyMessage,
    Soundbite,
    MarketSizing,
    ChannelInfo,
    Goal,
    KPI,
    Contradiction,
    RecentWin,
    Risk,
    IndustryType,
    CompanyStage,
    ChannelType,
    BCMVersion,
)

# Configure logging
logger = logging.getLogger(__name__)


class BCMReducer:
    def __init__(self):
        self.max_token_budget = 1200  # Hard cap for BCM tokens
        self.tokenizer = None

        # Initialize tiktoken tokenizer if available
        if TIKTOKEN_AVAILABLE:
            try:
                self.tokenizer = tiktoken.get_encoding("cl100k_base")  # GPT-4 tokenizer
                logger.info("TikToken tokenizer initialized successfully")
            except Exception as e:
                logger.error(f"Failed to initialize TikToken tokenizer: {e}")
                self.tokenizer = None
        else:
            logger.warning("Token counting disabled - tiktoken not available")

    async def reduce(self, raw_step_data: Dict[str, Any]) -> BusinessContextManifest:
        """
        Reduce onboarding rawStepData into compact BCM JSON manifest.

        Args:
            raw_step_data: Raw onboarding data from Redis session

        Returns:
            BusinessContextManifest: Validated BCM manifest with checksum
        """
        # Extract metadata
        metadata = raw_step_data.get("metadata", {})
        workspace_id = metadata.get("workspace_id", "unknown")
        user_id = metadata.get("user_id")

        # Calculate completion percentage
        total_steps = 23
        completed_steps = len(
            [k for k in raw_step_data.keys() if k.startswith("step_")]
        )
        completion_percentage = (completed_steps / total_steps) * 100

        # Extract and build all components
        company = self._extract_company_info(raw_step_data)
        icps = self._extract_icps(raw_step_data)
        competitors_data = self._extract_competitive_data(raw_step_data)
        brand_data = self._extract_brand_data(raw_step_data)
        market_data = self._extract_market_data(raw_step_data)
        messaging_data = self._extract_messaging_data(raw_step_data)
        channels_data = self._extract_channels_data(raw_step_data)
        goals_data = self._extract_goals_data(raw_step_data)
        issues_data = self._extract_issues_data(raw_step_data)

        # Build complete manifest
        manifest = BusinessContextManifest(
            version=BCMVersion.V2_0,
            generated_at=datetime.utcnow().isoformat(),
            workspace_id=workspace_id,
            user_id=user_id,
            company=company,
            icps=icps,
            competitors=competitors_data.get("competitors", {}),
            direct_competitors=competitors_data.get("direct_competitors", []),
            indirect_competitors=competitors_data.get("indirect_competitors", []),
            positioning_delta=competitors_data.get("positioning_delta", []),
            brand=brand_data.get("brand", {}),
            values=brand_data.get("values", []),
            personality=brand_data.get("personality", []),
            tone=brand_data.get("tone", []),
            positioning=brand_data.get("positioning"),
            market=market_data.get("market", MarketSizing()),
            verticals=market_data.get("verticals", []),
            geography=market_data.get("geography", []),
            messaging=messaging_data.get("messaging", {}),
            value_prop=messaging_data.get("value_prop", MessagingValueProp(primary="")),
            taglines=messaging_data.get("taglines", []),
            key_messages=messaging_data.get("key_messages", []),
            soundbites=messaging_data.get("soundbites", []),
            channels=channels_data.get("channels", {}),
            primary_channels=channels_data.get("primary_channels", []),
            secondary_channels=channels_data.get("secondary_channels", []),
            strategy_summary=channels_data.get("strategy_summary"),
            goals=goals_data.get("goals", {}),
            short_term_goals=goals_data.get("short_term_goals", []),
            long_term_goals=goals_data.get("long_term_goals", []),
            kpis=goals_data.get("kpis", []),
            contradictions=issues_data.get("contradictions", []),
            recent_wins=issues_data.get("recent_wins", []),
            risks=issues_data.get("risks", []),
            links={
                "raw_step_ids": [
                    k for k in raw_step_data.keys() if k.startswith("step_")
                ]
            },
            raw_step_ids=[k for k in raw_step_data.keys() if k.startswith("step_")],
            completion_percentage=completion_percentage,
        )

        # Log token usage for monitoring
        if self.tokenizer:
            token_count = self._count_tokens(manifest.dict())
            logger.info(
                f"BCM generated with {token_count} tokens (budget: {self.max_token_budget})"
            )

            if token_count > self.max_token_budget:
                logger.warning(
                    f"BCM exceeds token budget: {token_count} > {self.max_token_budget}"
                )
                # Apply compression if needed
                compressed_manifest = self._compress_to_budget(manifest)
                compressed_tokens = self._count_tokens(compressed_manifest.dict())
                logger.info(f"BCM compressed to {compressed_tokens} tokens")
                manifest = compressed_manifest

        # Add checksum for data integrity
        manifest_dict = manifest.dict()
        checksum = self._compute_checksum(manifest_dict)

        # Add checksum to manifest metadata
        manifest_dict["checksum"] = checksum
        manifest.checksum = checksum  # Add to manifest object if schema supports

        logger.info(f"BCM checksum computed: {checksum[:16]}...")

        return manifest

    def _extract_foundation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract comprehensive foundation data from all 23 onboarding steps.

        This method aggregates core company profile, intelligence, and foundation
        information from across the entire onboarding journey.

        Args:
            data: Raw onboarding step data

        Returns:
            Dict containing foundation data with validation
        """
        foundation = {
            "company_profile": {},
            "intelligence": {
                "evidence_count": 0,
                "facts": [],
                "icps": [],
                "positioning": {},
                "messaging": {},
            },
            "validation": {
                "missing_fields": [],
                "warnings": [],
                "completeness_score": 0.0,
            },
        }

        # Track evidence and facts across all steps
        evidence_count = 0
        facts = []
        missing_fields = []
        warnings = []

        # Step 1: Basic Company Information
        step_1 = self._get_step_data(data, 1) or {}
        if step_1:
            company_name = step_1.get("company_name")
            if company_name:
                foundation["company_profile"]["name"] = company_name
                facts.append(f"Company name: {company_name}")
                evidence_count += 1
            else:
                missing_fields.append("step_1.company_name")
                warnings.append("Company name missing from step 1")

            foundation["company_profile"].update(
                {
                    "website": step_1.get("website", ""),
                    "industry": step_1.get("industry", "other"),
                    "stage": step_1.get("stage", "seed"),
                    "description": step_1.get("description", ""),
                    "founded_year": step_1.get("founded_year"),
                    "employee_count": step_1.get("employee_count"),
                    "revenue_range": step_1.get("revenue_range"),
                    "headquarters": step_1.get("headquarters"),
                }
            )
        else:
            missing_fields.append("step_1")
            warnings.append("Step 1 (company info) not found")

        # Step 2: Value Proposition
        step_2 = self._get_step_data(data, 2) or {}
        if step_2:
            value_prop = step_2.get("value_proposition")
            if value_prop:
                foundation["company_profile"]["value_proposition"] = value_prop
                facts.append(f"Value proposition: {value_prop}")
                evidence_count += 1
            else:
                missing_fields.append("step_2.value_proposition")
                warnings.append("Value proposition missing from step 2")

        # Step 3: Business Contradictions
        step_3 = self._get_step_data(data, 3) or {}
        if step_3:
            contradictions = step_3.get("contradictions", [])
            if contradictions:
                foundation["company_profile"]["contradictions"] = contradictions
                facts.append(
                    f"Business contradictions identified: {len(contradictions)}"
                )
                evidence_count += len(contradictions)

        # Step 4: Target Audience
        step_4 = self._get_step_data(data, 4) or {}
        if step_4:
            target_audience = step_4.get("target_audience")
            if target_audience:
                foundation["company_profile"]["target_audience"] = target_audience
                facts.append(f"Target audience defined: {target_audience}")
                evidence_count += 1

        # Step 5: Problem Statement
        step_5 = self._get_step_data(data, 5) or {}
        if step_5:
            problem_statement = step_5.get("problem_statement")
            if problem_statement:
                foundation["company_profile"]["problem_statement"] = problem_statement
                facts.append(f"Problem statement: {problem_statement}")
                evidence_count += 1

        # Step 6: Solution Overview
        step_6 = self._get_step_data(data, 6) or {}
        if step_6:
            solution = step_6.get("solution")
            if solution:
                foundation["company_profile"]["solution"] = solution
                facts.append(f"Solution defined: {solution}")
                evidence_count += 1

        # Step 7: Competitive Landscape
        step_7 = self._get_step_data(data, 7) or {}
        if step_7:
            competitors = step_7.get("competitors", [])
            if competitors:
                foundation["intelligence"]["competitive_analysis"] = competitors
                facts.append(f"Competitors identified: {len(competitors)}")
                evidence_count += len(competitors)

        # Step 8: Market Positioning
        step_8 = self._get_step_data(data, 8) or {}
        if step_8:
            positioning = step_8.get("positioning")
            if positioning:
                foundation["intelligence"]["positioning"] = positioning
                facts.append(f"Market positioning defined")
                evidence_count += 1

        # Step 9: Revenue Model
        step_9 = self._get_step_data(data, 9) or {}
        if step_9:
            revenue_model = step_9.get("revenue_model")
            if revenue_model:
                foundation["company_profile"]["revenue_model"] = revenue_model
                facts.append(f"Revenue model: {revenue_model}")
                evidence_count += 1

        # Step 10: Pricing Strategy
        step_10 = self._get_step_data(data, 10) or {}
        if step_10:
            pricing = step_10.get("pricing_strategy")
            if pricing:
                foundation["company_profile"]["pricing_strategy"] = pricing
                facts.append(f"Pricing strategy defined")
                evidence_count += 1

        # Step 11: Go-to-Market Strategy
        step_11 = self._get_step_data(data, 11) or {}
        if step_11:
            gtm = step_11.get("go_to_market")
            if gtm:
                foundation["company_profile"]["go_to_market_strategy"] = gtm
                facts.append(f"Go-to-market strategy defined")
                evidence_count += 1

        # Step 12: Brand Values
        step_12 = self._get_step_data(data, 12) or {}
        if step_12:
            brand_values = step_12.get("values", [])
            if brand_values:
                foundation["intelligence"]["brand_values"] = brand_values
                facts.append(f"Brand values: {len(brand_values)} defined")
                evidence_count += len(brand_values)

        # Step 13: Brand Personality
        step_13 = self._get_step_data(data, 13) or {}
        if step_13:
            personality = step_13.get("personality")
            if personality:
                foundation["intelligence"]["brand_personality"] = personality
                facts.append(f"Brand personality defined")
                evidence_count += 1

        # Step 14: ICP/Cohorts (Critical for intelligence)
        step_14 = self._get_step_data(data, 14) or {}
        if step_14:
            icps = step_14.get("icps", [])
            if icps:
                foundation["intelligence"]["icps"] = icps
                facts.append(f"ICPs defined: {len(icps)}")
                evidence_count += len(icps) * 3  # Weight ICPs heavily
            else:
                missing_fields.append("step_14.icps")
                warnings.append("No ICPs defined in step 14")

        # Step 15: Customer Pain Points
        step_15 = self._get_step_data(data, 15) or {}
        if step_15:
            pain_points = step_15.get("pain_points", [])
            if pain_points:
                foundation["intelligence"]["pain_points"] = pain_points
                facts.append(f"Customer pain points: {len(pain_points)} identified")
                evidence_count += len(pain_points)

        # Step 16: Customer Goals
        step_16 = self._get_step_data(data, 16) or {}
        if step_16:
            goals = step_16.get("goals", [])
            if goals:
                foundation["intelligence"]["customer_goals"] = goals
                facts.append(f"Customer goals: {len(goals)} identified")
                evidence_count += len(goals)

        # Step 17: Messaging Framework
        step_17 = self._get_step_data(data, 17) or {}
        if step_17:
            messaging = step_17.get("messaging")
            if messaging:
                foundation["intelligence"]["messaging"] = messaging
                facts.append(f"Messaging framework defined")
                evidence_count += 1

        # Step 18: Content Strategy
        step_18 = self._get_step_data(data, 18) or {}
        if step_18:
            content_strategy = step_18.get("content_strategy")
            if content_strategy:
                foundation["company_profile"]["content_strategy"] = content_strategy
                facts.append(f"Content strategy defined")
                evidence_count += 1

        # Step 19: Sales Strategy
        step_19 = self._get_step_data(data, 19) or {}
        if step_19:
            sales_strategy = step_19.get("sales_strategy")
            if sales_strategy:
                foundation["company_profile"]["sales_strategy"] = sales_strategy
                facts.append(f"Sales strategy defined")
                evidence_count += 1

        # Step 20: Channel Strategy
        step_20 = self._get_step_data(data, 20) or {}
        if step_20:
            channels = step_20.get("channels", [])
            if channels:
                foundation["company_profile"]["channel_strategy"] = channels
                facts.append(f"Channels: {len(channels)} identified")
                evidence_count += len(channels)

        # Step 21: Market Sizing
        step_21 = self._get_step_data(data, 21) or {}
        if step_21:
            market_sizing = step_21.get("market_sizing", {})
            if market_sizing:
                foundation["company_profile"]["market_sizing"] = market_sizing
                facts.append(f"Market sizing defined")
                evidence_count += 1

        # Step 22: Goals & KPIs
        step_22 = self._get_step_data(data, 22) or {}
        if step_22:
            goals = step_22.get("goals", [])
            kpis = step_22.get("kpis", [])
            if goals:
                foundation["company_profile"]["goals"] = goals
                facts.append(f"Business goals: {len(goals)} defined")
                evidence_count += len(goals)
            if kpis:
                foundation["company_profile"]["kpis"] = kpis
                facts.append(f"KPIs: {len(kpis)} defined")
                evidence_count += len(kpis)

        # Step 23: Team & Resources
        step_23 = self._get_step_data(data, 23) or {}
        if step_23:
            team = step_23.get("team")
            resources = step_23.get("resources")
            if team:
                foundation["company_profile"]["team"] = team
                facts.append(f"Team information defined")
                evidence_count += 1
            if resources:
                foundation["company_profile"]["resources"] = resources
                facts.append(f"Resources identified")
                evidence_count += 1

        # Calculate completeness score
        total_possible_fields = 23  # One key field per step
        completed_fields = total_possible_fields - len(missing_fields)
        completeness_score = (completed_fields / total_possible_fields) * 100

        # Update foundation with validation results
        foundation["intelligence"]["evidence_count"] = evidence_count
        foundation["intelligence"]["facts"] = facts
        foundation["validation"]["missing_fields"] = missing_fields
        foundation["validation"]["warnings"] = warnings
        foundation["validation"]["completeness_score"] = completeness_score

        # Log validation results
        if warnings:
            logger.warning(f"Foundation extraction warnings: {warnings}")
        if missing_fields:
            logger.warning(f"Foundation extraction missing fields: {missing_fields}")

        logger.info(
            f"Foundation extraction complete: {completeness_score:.1f}% complete, {evidence_count} evidence points"
        )

        return foundation

    def _extract_company_info(self, data: Dict[str, Any]) -> CompanyInfo:
        """Extract company information from step data."""
        # Get foundation data first for comprehensive company info
        foundation = self._extract_foundation(data)
        company_profile = foundation.get("company_profile", {})

        # Get step data for fallback
        step_data = self._get_step_data(data, 1) or {}
        foundation_data = self._get_step_data(data, "foundation") or {}

        # Map industry string to enum
        industry_str = step_data.get(
            "industry", foundation_data.get("industry", "other")
        )
        try:
            industry = IndustryType(industry_str.lower().replace(" ", "_"))
        except ValueError:
            industry = IndustryType.OTHER

        # Map stage string to enum
        stage_str = step_data.get("stage", foundation_data.get("stage", "seed"))
        try:
            stage = CompanyStage(stage_str.lower().replace(" ", "_"))
        except ValueError:
            stage = CompanyStage.SEED

        return CompanyInfo(
            name=step_data.get("company_name", foundation_data.get("company_name", "")),
            website=step_data.get("website", foundation_data.get("website")),
            industry=industry,
            sub_industry=step_data.get("sub_industry"),
            description=step_data.get(
                "description", foundation_data.get("description", "")
            ),
            stage=stage,
            founded_year=step_data.get("founded_year"),
            employee_count=step_data.get("employee_count"),
            revenue_range=step_data.get("revenue_range"),
            headquarters=step_data.get("headquarters"),
        )

    def _extract_icps(self, data: Dict[str, Any]) -> List[ICPProfile]:
        """
        Extract ICP profiles from onboarding data with validation and prioritization.

        This method extracts ICPs from step 14 or cohorts step, validates structure,
        applies prioritization logic, and handles missing data gracefully.

        Args:
            data: Raw onboarding step data

        Returns:
            List of validated and prioritized ICPProfile objects
        """
        icps = []
        validation_warnings = []

        # Get ICP data from step 14 or cohorts step
        step_data = (
            self._get_step_data(data, 14) or self._get_step_data(data, "cohorts") or {}
        )

        if not step_data:
            logger.warning("No ICP data found in step 14 or cohorts step")
            return icps

        # Handle multiple ICP formats
        icp_list = step_data.get("icps", [])
        if isinstance(icp_list, dict):
            icp_list = [icp_list]
        elif not isinstance(icp_list, list):
            validation_warnings.append(f"Invalid ICP data format: {type(icp_list)}")
            logger.warning(f"Invalid ICP data format: {type(icp_list)}")
            return icps

        # Process each ICP
        for idx, icp_data in enumerate(icp_list):
            try:
                # Validate required fields
                if not icp_data.get("name"):
                    validation_warnings.append(f"ICP {idx}: Missing name field")
                    continue

                if not icp_data.get("description"):
                    validation_warnings.append(
                        f"ICP {icp_data.get('name', idx)}: Missing description"
                    )
                    # Continue with empty description

                # Extract and validate pains
                pains = []
                pain_data = icp_data.get("pains", [])
                if isinstance(pain_data, list):
                    for pain in pain_data:
                        if isinstance(pain, dict):
                            pains.append(
                                ICPPainPoint(
                                    category=pain.get("category", "general"),
                                    description=pain.get("description", ""),
                                    severity=self._validate_severity(
                                        pain.get("severity", 5)
                                    ),
                                    frequency=pain.get("frequency", "occasional"),
                                )
                            )
                        else:
                            validation_warnings.append(
                                f"ICP {icp_data.get('name')}: Invalid pain format"
                            )

                # Extract and validate goals
                goals = []
                goal_data = icp_data.get("goals", [])
                if isinstance(goal_data, list):
                    for goal in goal_data:
                        if isinstance(goal, dict):
                            goals.append(
                                ICPGoal(
                                    category=goal.get("category", "business"),
                                    description=goal.get("description", ""),
                                    priority=self._validate_priority(
                                        goal.get("priority", "medium")
                                    ),
                                    timeline=goal.get("timeline"),
                                )
                            )
                        else:
                            validation_warnings.append(
                                f"ICP {icp_data.get('name')}: Invalid goal format"
                            )

                # Extract and validate objections
                objections = []
                objection_data = icp_data.get("objections", [])
                if isinstance(objection_data, list):
                    for objection in objection_data:
                        if isinstance(objection, dict):
                            objections.append(
                                ICPObjection(
                                    type=objection.get("type", "price"),
                                    description=objection.get("description", ""),
                                    response=objection.get("response"),
                                )
                            )
                        else:
                            validation_warnings.append(
                                f"ICP {icp_data.get('name')}: Invalid objection format"
                            )

                # Extract and validate triggers
                triggers = []
                trigger_data = icp_data.get("triggers", [])
                if isinstance(trigger_data, list):
                    for trigger in trigger_data:
                        if isinstance(trigger, dict):
                            triggers.append(
                                ICPTriggerEvent(
                                    event=trigger.get("event", ""),
                                    timing=trigger.get("timing", ""),
                                    impact=trigger.get("impact", ""),
                                )
                            )
                        else:
                            validation_warnings.append(
                                f"ICP {icp_data.get('name')}: Invalid trigger format"
                            )

                # Calculate confidence score
                confidence_score = self._calculate_confidence_score(
                    icp_data, pains, goals, objections, triggers
                )

                # Create ICP profile
                icp_profile = ICPProfile(
                    name=icp_data.get("name", ""),
                    description=icp_data.get("description", ""),
                    company_size=icp_data.get("company_size"),
                    vertical=icp_data.get("vertical"),
                    geography=icp_data.get("geography", []),
                    pains=pains,
                    goals=goals,
                    objections=objections,
                    triggers=triggers,
                    confidence_score=confidence_score,
                )

                icps.append(icp_profile)

            except Exception as e:
                validation_warnings.append(f"ICP {idx}: Processing error - {str(e)}")
                logger.error(f"Error processing ICP {idx}: {str(e)}")
                continue

        # Apply prioritization
        prioritized_icps = self._prioritize_icps(icps)

        # Log validation warnings
        if validation_warnings:
            logger.warning(f"ICP extraction warnings: {validation_warnings}")

        logger.info(f"Extracted {len(prioritized_icps)} ICPs with validation")

        return prioritized_icps

    def _validate_severity(self, severity: Any) -> int:
        """Validate and normalize pain severity."""
        try:
            if isinstance(severity, int):
                return max(1, min(10, severity))  # Clamp between 1-10
            elif isinstance(severity, str):
                severity_map = {
                    "low": 3,
                    "mild": 3,
                    "medium": 5,
                    "moderate": 5,
                    "high": 8,
                    "severe": 8,
                    "critical": 10,
                    "extreme": 10,
                }
                return severity_map.get(severity.lower(), 5)
            else:
                return 5  # Default medium
        except Exception:
            return 5

    def _validate_priority(self, priority: Any) -> str:
        """Validate and normalize goal priority."""
        if isinstance(priority, str):
            valid_priorities = ["low", "medium", "high", "critical"]
            normalized = priority.lower()
            return normalized if normalized in valid_priorities else "medium"
        else:
            return "medium"

    def _calculate_confidence_score(
        self, icp_data: Dict, pains: List, goals: List, objections: List, triggers: List
    ) -> float:
        """
        Calculate confidence score for ICP based on data completeness.

        Args:
            icp_data: Raw ICP data
            pains: Extracted pains
            goals: Extracted goals
            objections: Extracted objections
            triggers: Extracted triggers

        Returns:
            Confidence score between 0.0 and 1.0
        """
        score = 0.0
        max_score = 6.0  # Maximum possible score

        # Base fields (0.5 points each)
        if icp_data.get("name"):
            score += 0.5
        if icp_data.get("description"):
            score += 0.5
        if icp_data.get("company_size"):
            score += 0.5
        if icp_data.get("vertical"):
            score += 0.5

        # Enrichment fields (0.5-1.5 points each)
        if pains:
            score += min(1.5, len(pains) * 0.5)  # Max 1.5 points for pains
        if goals:
            score += min(1.5, len(goals) * 0.5)  # Max 1.5 points for goals
        if objections:
            score += min(1.0, len(objections) * 0.3)  # Max 1.0 points for objections
        if triggers:
            score += min(1.0, len(triggers) * 0.3)  # Max 1.0 points for triggers

        # Normalize to 0-1 range
        normalized_score = min(1.0, score / max_score)

        # Round to 2 decimal places
        return round(normalized_score, 2)

    def _prioritize_icps(self, icps: List[ICPProfile]) -> List[ICPProfile]:
        """
        Prioritize ICPs based on confidence score and business rules.

        Args:
            icps: List of ICP profiles

        Returns:
            Prioritized list of ICP profiles (max 3)
        """
        if not icps:
            return icps

        # Sort by confidence score (descending), then by name for consistency
        sorted_icps = sorted(icps, key=lambda x: (-x.confidence_score, x.name))

        # Apply business rules for prioritization
        # 1. Keep top 3 ICPs maximum
        prioritized = sorted_icps[:3]

        # 2. Ensure minimum confidence threshold
        min_confidence = 0.3
        prioritized = [
            icp for icp in prioritized if icp.confidence_score >= min_confidence
        ]

        # 3. If no ICPs meet threshold, keep the highest scoring one
        if not prioritized and sorted_icps:
            prioritized = [sorted_icps[0]]

        logger.info(f"Prioritized {len(prioritized)} ICPs from {len(icps)} total")

        return prioritized

    def _extract_competitive_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract comprehensive competitive landscape data with validation.

        This method extracts competitor profiles, positioning data, and market analysis
        from steps 7-8 with validation and error handling.

        Args:
            data: Raw onboarding step data

        Returns:
            Dict containing competitive intelligence with validation metadata
        """
        competitive_intel = {
            "competitors": {},
            "direct_competitors": [],
            "indirect_competitors": [],
            "positioning_delta": [],
            "market_landscape": {},
            "competitive_advantages": [],
            "validation": {
                "missing_fields": [],
                "warnings": [],
                "completeness_score": 0.0,
            },
        }

        validation_warnings = []
        missing_fields = []
        evidence_count = 0

        # Get competitor data from step 7 or competitive step
        step_data = (
            self._get_step_data(data, 7)
            or self._get_step_data(data, "competitive")
            or {}
        )

        if not step_data:
            validation_warnings.append("No competitive data found in step 7")
            logger.warning("No competitive data found in step 7")
        else:
            # Extract direct competitors with validation
            direct_competitors = step_data.get("direct_competitors", [])
            if isinstance(direct_competitors, list):
                for idx, comp in enumerate(direct_competitors):
                    if isinstance(comp, dict):
                        # Validate required fields
                        if not comp.get("name"):
                            validation_warnings.append(
                                f"Direct competitor {idx}: Missing name"
                            )
                            continue

                        competitor_info = CompetitorInfo(
                            name=comp.get("name", ""),
                            website=comp.get("website"),
                            type="direct",
                            strengths=self._validate_list_field(
                                comp.get("strengths", [])
                            ),
                            weaknesses=self._validate_list_field(
                                comp.get("weaknesses", [])
                            ),
                            market_share=comp.get("market_share"),
                            pricing_model=comp.get("pricing_model"),
                            target_segments=self._validate_list_field(
                                comp.get("target_segments", [])
                            ),
                        )
                        competitive_intel["direct_competitors"].append(competitor_info)
                        evidence_count += 1
                    else:
                        validation_warnings.append(
                            f"Direct competitor {idx}: Invalid format"
                        )

            # Extract indirect competitors with validation
            indirect_competitors = step_data.get("indirect_competitors", [])
            if isinstance(indirect_competitors, list):
                for idx, comp in enumerate(indirect_competitors):
                    if isinstance(comp, dict):
                        if not comp.get("name"):
                            validation_warnings.append(
                                f"Indirect competitor {idx}: Missing name"
                            )
                            continue

                        competitor_info = CompetitorInfo(
                            name=comp.get("name", ""),
                            website=comp.get("website"),
                            type="indirect",
                            strengths=self._validate_list_field(
                                comp.get("strengths", [])
                            ),
                            weaknesses=self._validate_list_field(
                                comp.get("weaknesses", [])
                            ),
                            market_share=comp.get("market_share"),
                            pricing_model=comp.get("pricing_model"),
                            target_segments=self._validate_list_field(
                                comp.get("target_segments", [])
                            ),
                        )
                        competitive_intel["indirect_competitors"].append(
                            competitor_info
                        )
                        evidence_count += 1
                    else:
                        validation_warnings.append(
                            f"Indirect competitor {idx}: Invalid format"
                        )

            # Extract positioning deltas with validation
            positioning_deltas = step_data.get("positioning_delta", [])
            if isinstance(positioning_deltas, list):
                for idx, delta in enumerate(positioning_deltas):
                    if isinstance(delta, dict):
                        if not delta.get("axis"):
                            validation_warnings.append(
                                f"Positioning delta {idx}: Missing axis"
                            )
                            continue

                        positioning_delta = PositioningDelta(
                            axis=delta.get("axis", ""),
                            our_position=delta.get("our_position", ""),
                            competitor_position=delta.get("competitor_position", ""),
                            differentiation=delta.get("differentiation", ""),
                        )
                        competitive_intel["positioning_delta"].append(positioning_delta)
                        evidence_count += 1
                    else:
                        validation_warnings.append(
                            f"Positioning delta {idx}: Invalid format"
                        )

            # Extract market landscape data
            market_landscape = step_data.get("market_landscape", {})
            if isinstance(market_landscape, dict):
                competitive_intel["market_landscape"] = {
                    "market_size": market_landscape.get("market_size"),
                    "growth_rate": market_landscape.get("growth_rate"),
                    "market_trends": self._validate_list_field(
                        market_landscape.get("market_trends", [])
                    ),
                    "barriers_to_entry": self._validate_list_field(
                        market_landscape.get("barriers_to_entry", [])
                    ),
                    "key_success_factors": self._validate_list_field(
                        market_landscape.get("key_success_factors", [])
                    ),
                }
                evidence_count += len([k for k, v in market_landscape.items() if v])

            # Extract competitive advantages
            advantages = step_data.get("competitive_advantages", [])
            if isinstance(advantages, list):
                competitive_intel["competitive_advantages"] = [
                    advantage
                    for advantage in advantages
                    if isinstance(advantage, str) and advantage.strip()
                ]
                evidence_count += len(competitive_intel["competitive_advantages"])

        # Get positioning data from step 8
        step_8_data = self._get_step_data(data, 8) or {}
        if step_8_data:
            positioning = step_8_data.get("positioning", {})
            if isinstance(positioning, dict):
                competitive_intel["positioning"] = {
                    "unique_value": positioning.get("unique_value", ""),
                    "market_segment": positioning.get("market_segment", ""),
                    "price_positioning": positioning.get("price_positioning", ""),
                    "quality_positioning": positioning.get("quality_positioning", ""),
                    "service_positioning": positioning.get("service_positioning", ""),
                }
                evidence_count += len([k for k, v in positioning.items() if v])
        else:
            missing_fields.append("step_8.positioning")
            validation_warnings.append("No positioning data found in step 8")

        # Calculate completeness score
        total_possible_fields = 8  # direct_comp, indirect_comp, positioning_delta, market_landscape, advantages, positioning (5 fields)
        completed_fields = total_possible_fields - len(missing_fields)
        completeness_score = (completed_fields / total_possible_fields) * 100

        # Update validation metadata
        competitive_intel["validation"]["missing_fields"] = missing_fields
        competitive_intel["validation"]["warnings"] = validation_warnings
        competitive_intel["validation"]["completeness_score"] = completeness_score
        competitive_intel["validation"]["evidence_count"] = evidence_count

        # Log validation results
        if validation_warnings:
            logger.warning(f"Competitive extraction warnings: {validation_warnings}")

        logger.info(
            f"Competitive extraction complete: {completeness_score:.1f}% complete, {evidence_count} evidence points"
        )

        return competitive_intel

    def _validate_list_field(self, field: Any) -> List[str]:
        """Validate and normalize list fields."""
        if isinstance(field, list):
            return [
                str(item) for item in field if item is not None and str(item).strip()
            ]
        elif isinstance(field, str):
            return [field] if field.strip() else []
        else:
            return []

    def _extract_brand_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract brand and positioning data."""
        # Get brand data from step 12 or brand step
        step_data = (
            self._get_step_data(data, 12) or self._get_step_data(data, "brand") or {}
        )

        # Extract values
        values = []
        for value in step_data.get("values", []):
            values.append(
                BrandValues(
                    value=value.get("value", ""),
                    description=value.get("description", ""),
                )
            )

        # Extract personality traits
        personality = []
        for trait in step_data.get("personality", []):
            personality.append(
                BrandPersonality(
                    trait=trait.get("trait", ""),
                    description=trait.get("description", ""),
                )
            )

        return {
            "brand": step_data.get("brand", {}),
            "values": values,
            "personality": personality,
            "tone": step_data.get("tone", []),
            "positioning": step_data.get("positioning"),
        }

    def _extract_market_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract market sizing and targeting data."""
        # Get market data from step 21 or market step
        step_data = (
            self._get_step_data(data, 21) or self._get_step_data(data, "market") or {}
        )

        # Build market sizing
        market_sizing = MarketSizing(
            tam=step_data.get("tam"),
            sam=step_data.get("sam"),
            som=step_data.get("som"),
            currency=step_data.get("currency", "USD"),
            year=step_data.get("year"),
        )

        return {
            "market": market_sizing,
            "verticals": step_data.get("verticals", []),
            "geography": step_data.get("geography", []),
        }

    def _extract_messaging_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract comprehensive messaging and communication data with validation.

        This method extracts value propositions, brand voice, messaging frameworks,
        and communication guidelines from step 17 with validation.

        Args:
            data: Raw onboarding step data

        Returns:
            Dict containing messaging intelligence with validation metadata
        """
        messaging_intel = {
            "messaging": {},
            "value_prop": None,
            "taglines": [],
            "key_messages": [],
            "soundbites": [],
            "brand_voice": {},
            "communication_guidelines": {},
            "validation": {
                "missing_fields": [],
                "warnings": [],
                "completeness_score": 0.0,
            },
        }

        validation_warnings = []
        missing_fields = []
        evidence_count = 0

        # Get messaging data from step 17 or messaging step
        step_data = (
            self._get_step_data(data, 17)
            or self._get_step_data(data, "messaging")
            or {}
        )

        if not step_data:
            validation_warnings.append("No messaging data found in step 17")
            logger.warning("No messaging data found in step 17")
        else:
            # Extract and validate value proposition
            value_prop_data = step_data.get("value_prop", {})
            if isinstance(value_prop_data, dict):
                value_prop = MessagingValueProp(
                    primary=value_prop_data.get("primary", ""),
                    secondary=value_prop_data.get("secondary"),
                    supporting_points=self._validate_list_field(
                        value_prop_data.get("supporting_points", [])
                    ),
                )
                messaging_intel["value_prop"] = value_prop

                if value_prop.primary:
                    evidence_count += 1
                else:
                    missing_fields.append("value_prop.primary")
                    validation_warnings.append("Primary value proposition missing")
            else:
                validation_warnings.append("Invalid value proposition format")

            # Extract and validate taglines
            taglines_data = step_data.get("taglines", [])
            if isinstance(taglines_data, list):
                for idx, tagline in enumerate(taglines_data):
                    if isinstance(tagline, dict):
                        if not tagline.get("text"):
                            validation_warnings.append(f"Tagline {idx}: Missing text")
                            continue

                        tagline_obj = Tagline(
                            text=tagline.get("text", ""),
                            context=tagline.get("context"),
                            variants=self._validate_list_field(
                                tagline.get("variants", [])
                            ),
                        )
                        messaging_intel["taglines"].append(tagline_obj)
                        evidence_count += 1
                    else:
                        validation_warnings.append(f"Tagline {idx}: Invalid format")

            # Extract and validate key messages
            key_messages_data = step_data.get("key_messages", [])
            if isinstance(key_messages_data, list):
                for idx, message in enumerate(key_messages_data):
                    if isinstance(message, dict):
                        if not message.get("title") and not message.get("content"):
                            validation_warnings.append(
                                f"Key message {idx}: Missing title and content"
                            )
                            continue

                        key_message = KeyMessage(
                            title=message.get("title", ""),
                            content=message.get("content", ""),
                            audience=message.get("audience", ""),
                            priority=self._validate_priority(
                                message.get("priority", "medium")
                            ),
                        )
                        messaging_intel["key_messages"].append(key_message)
                        evidence_count += 1
                    else:
                        validation_warnings.append(f"Key message {idx}: Invalid format")

            # Extract and validate soundbites
            soundbites_data = step_data.get("soundbites", [])
            if isinstance(soundbites_data, list):
                for idx, soundbite in enumerate(soundbites_data):
                    if isinstance(soundbite, dict):
                        if not soundbite.get("text"):
                            validation_warnings.append(f"Soundbite {idx}: Missing text")
                            continue

                        soundbite_obj = Soundbite(
                            text=soundbite.get("text", ""),
                            context=soundbite.get("context", ""),
                            length=self._validate_soundbite_length(
                                soundbite.get("length", "medium")
                            ),
                        )
                        messaging_intel["soundbites"].append(soundbite_obj)
                        evidence_count += 1
                    else:
                        validation_warnings.append(f"Soundbite {idx}: Invalid format")

            # Extract brand voice and tone
            brand_voice = step_data.get("brand_voice", {})
            if isinstance(brand_voice, dict):
                messaging_intel["brand_voice"] = {
                    "personality_traits": self._validate_list_field(
                        brand_voice.get("personality_traits", [])
                    ),
                    "tone_attributes": self._validate_list_field(
                        brand_voice.get("tone_attributes", [])
                    ),
                    "communication_style": brand_voice.get("communication_style", ""),
                    "formality_level": self._validate_formality(
                        brand_voice.get("formality_level", "professional")
                    ),
                    "emotional_tone": brand_voice.get("emotional_tone", ""),
                }
                evidence_count += len([k for k, v in brand_voice.items() if v])

            # Extract communication guidelines
            comm_guidelines = step_data.get("communication_guidelines", {})
            if isinstance(comm_guidelines, dict):
                messaging_intel["communication_guidelines"] = {
                    "do_say": self._validate_list_field(
                        comm_guidelines.get("do_say", [])
                    ),
                    "dont_say": self._validate_list_field(
                        comm_guidelines.get("dont_say", [])
                    ),
                    "preferred_channels": self._validate_list_field(
                        comm_guidelines.get("preferred_channels", [])
                    ),
                    "content_preferences": self._validate_list_field(
                        comm_guidelines.get("content_preferences", [])
                    ),
                    "timing_considerations": comm_guidelines.get(
                        "timing_considerations", ""
                    ),
                }
                evidence_count += len([k for k, v in comm_guidelines.items() if v])

            # Extract messaging framework
            messaging_framework = step_data.get("messaging_framework", {})
            if isinstance(messaging_framework, dict):
                messaging_intel["messaging"] = {
                    "framework_type": messaging_framework.get("framework_type", ""),
                    "core_message": messaging_framework.get("core_message", ""),
                    "supporting_points": self._validate_list_field(
                        messaging_framework.get("supporting_points", [])
                    ),
                    "proof_points": self._validate_list_field(
                        messaging_framework.get("proof_points", [])
                    ),
                    "call_to_action": messaging_framework.get("call_to_action", ""),
                }
                evidence_count += len([k for k, v in messaging_framework.items() if v])

        # Calculate completeness score
        total_possible_fields = 7  # value_prop, taglines, key_messages, soundbites, brand_voice, comm_guidelines, messaging_framework
        completed_fields = total_possible_fields - len(missing_fields)
        completeness_score = (completed_fields / total_possible_fields) * 100

        # Update validation metadata
        messaging_intel["validation"]["missing_fields"] = missing_fields
        messaging_intel["validation"]["warnings"] = validation_warnings
        messaging_intel["validation"]["completeness_score"] = completeness_score
        messaging_intel["validation"]["evidence_count"] = evidence_count

        # Log validation results
        if validation_warnings:
            logger.warning(f"Messaging extraction warnings: {validation_warnings}")

        logger.info(
            f"Messaging extraction complete: {completeness_score:.1f}% complete, {evidence_count} evidence points"
        )

        return messaging_intel

    def _validate_soundbite_length(self, length: Any) -> str:
        """Validate and normalize soundbite length."""
        if isinstance(length, str):
            valid_lengths = ["short", "medium", "long"]
            normalized = length.lower()
            return normalized if normalized in valid_lengths else "medium"
        else:
            return "medium"

    def _validate_formality(self, formality: Any) -> str:
        """Validate and normalize formality level."""
        if isinstance(formality, str):
            valid_formalities = ["casual", "professional", "formal", "technical"]
            normalized = formality.lower()
            return normalized if normalized in valid_formalities else "professional"
        else:
            return "professional"

    def _extract_channels_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract channel and distribution data."""
        # Get channels data from step 20 or channels step
        step_data = (
            self._get_step_data(data, 20) or self._get_step_data(data, "channels") or {}
        )

        # Extract primary channels
        primary_channels = []
        for channel in step_data.get("primary_channels", []):
            try:
                channel_type = ChannelType(
                    channel.get("type", "website").lower().replace(" ", "_")
                )
            except ValueError:
                channel_type = ChannelType.WEBSITE

            primary_channels.append(
                ChannelInfo(
                    type=channel_type,
                    name=channel.get("name", ""),
                    description=channel.get("description"),
                    effectiveness=channel.get("effectiveness"),
                    cost_efficiency=channel.get("cost_efficiency"),
                    target_audience=channel.get("target_audience"),
                )
            )

        # Extract secondary channels
        secondary_channels = []
        for channel in step_data.get("secondary_channels", []):
            try:
                channel_type = ChannelType(
                    channel.get("type", "website").lower().replace(" ", "_")
                )
            except ValueError:
                channel_type = ChannelType.WEBSITE

            secondary_channels.append(
                ChannelInfo(
                    type=channel_type,
                    name=channel.get("name", ""),
                    description=channel.get("description"),
                    effectiveness=channel.get("effectiveness"),
                    cost_efficiency=channel.get("cost_efficiency"),
                    target_audience=channel.get("target_audience"),
                )
            )

        return {
            "channels": step_data.get("channels", {}),
            "primary_channels": primary_channels,
            "secondary_channels": secondary_channels,
            "strategy_summary": step_data.get("strategy_summary"),
        }

    def _extract_goals_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract goals and KPIs data."""
        # Get goals data from step 22 or goals step
        step_data = (
            self._get_step_data(data, 22) or self._get_step_data(data, "goals") or {}
        )

        # Extract short-term goals
        short_term_goals = []
        for goal in step_data.get("short_term_goals", []):
            short_term_goals.append(
                Goal(
                    title=goal.get("title", ""),
                    description=goal.get("description", ""),
                    timeframe=goal.get("timeframe", ""),
                    metrics=goal.get("metrics", []),
                    priority=goal.get("priority", ""),
                )
            )

        # Extract long-term goals
        long_term_goals = []
        for goal in step_data.get("long_term_goals", []):
            long_term_goals.append(
                Goal(
                    title=goal.get("title", ""),
                    description=goal.get("description", ""),
                    timeframe=goal.get("timeframe", ""),
                    metrics=goal.get("metrics", []),
                    priority=goal.get("priority", ""),
                )
            )

        # Extract KPIs
        kpis = []
        for kpi in step_data.get("kpis", []):
            kpis.append(
                KPI(
                    name=kpi.get("name", ""),
                    description=kpi.get("description", ""),
                    target=kpi.get("target"),
                    current=kpi.get("current"),
                    unit=kpi.get("unit"),
                    frequency=kpi.get("frequency", ""),
                )
            )

        return {
            "goals": step_data.get("goals", {}),
            "short_term_goals": short_term_goals,
            "long_term_goals": long_term_goals,
            "kpis": kpis,
        }

    def _extract_issues_data(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract contradictions, wins, and risks data."""
        issues = {"contradictions": [], "recent_wins": [], "risks": []}

        # Extract contradictions from step 3
        contradiction_data = self._get_step_data(data, 3) or {}
        for contradiction in contradiction_data.get("contradictions", []):
            issues["contradictions"].append(
                Contradiction(
                    type=contradiction.get("type", ""),
                    description=contradiction.get("description", ""),
                    severity=contradiction.get("severity", ""),
                    resolution=contradiction.get("resolution"),
                )
            )

        # Extract recent wins from various steps
        for step_key in data.keys():
            if step_key.startswith("step_"):
                step_data = data[step_key]
                if isinstance(step_data, dict) and "recent_wins" in step_data:
                    for win in step_data["recent_wins"]:
                        issues["recent_wins"].append(
                            RecentWin(
                                title=win.get("title", ""),
                                description=win.get("description", ""),
                                date=win.get("date", datetime.utcnow().isoformat()),
                                impact=win.get("impact", ""),
                                customer=win.get("customer"),
                            )
                        )

        # Extract risks from various steps
        for step_key in data.keys():
            if step_key.startswith("step_"):
                step_data = data[step_key]
                if isinstance(step_data, dict) and "risks" in step_data:
                    for risk in step_data["risks"]:
                        issues["risks"].append(
                            Risk(
                                title=risk.get("title", ""),
                                description=risk.get("description", ""),
                                probability=risk.get("probability", ""),
                                impact=risk.get("impact", ""),
                                mitigation=risk.get("mitigation"),
                            )
                        )

        return issues

    def _get_step_data(
        self, data: Dict[str, Any], step_identifier: Union[str, int]
    ) -> Optional[Dict[str, Any]]:
        """Get step data by step number or identifier."""
        if isinstance(step_identifier, int):
            step_key = f"step_{step_identifier}"
        else:
            step_key = step_identifier

        step_data = data.get(step_key)
        if step_data and isinstance(step_data, dict):
            return step_data.get("data", step_data)

        return None

    def _count_tokens(self, text: Union[str, Dict, List]) -> int:
        """
        Count tokens in text using TikToken GPT-4 tokenizer.

        Args:
            text: Text to count tokens for (string, dict, or list)

        Returns:
            Number of tokens
        """
        if not self.tokenizer:
            # Fallback estimation: ~4 chars per token
            if isinstance(text, str):
                return len(text) // 4
            elif isinstance(text, (dict, list)):
                json_str = json.dumps(text, separators=(",", ":"))
                return len(json_str) // 4
            else:
                return 0

        try:
            if isinstance(text, str):
                return len(self.tokenizer.encode(text))
            elif isinstance(text, dict):
                # Convert dict to JSON and count tokens
                json_str = json.dumps(text, separators=(",", ":"))
                return len(self.tokenizer.encode(json_str))
            elif isinstance(text, list):
                # Count tokens for each list item
                total_tokens = 0
                for item in text:
                    total_tokens += self._count_tokens(item)
                return total_tokens
            else:
                # Convert other types to string
                return len(self.tokenizer.encode(str(text)))
        except Exception as e:
            logger.error(f"Error counting tokens: {e}")
            # Fallback to character-based estimation
            if isinstance(text, str):
                return len(text) // 4
            else:
                json_str = json.dumps(text, separators=(",", ":"))
                return len(json_str) // 4

    def _count_manifest_tokens(
        self, manifest: BusinessContextManifest
    ) -> Dict[str, int]:
        """
        Count tokens for each section of the BCM manifest.

        Args:
            manifest: BCM manifest to analyze

        Returns:
            Dict with token counts per section
        """
        token_counts = {
            "total": 0,
            "company": 0,
            "icps": 0,
            "competitors": 0,
            "brand": 0,
            "market": 0,
            "messaging": 0,
            "channels": 0,
            "goals": 0,
            "issues": 0,
        }

        try:
            # Count tokens for each section
            manifest_dict = manifest.dict()

            # Company info
            if manifest.company:
                token_counts["company"] = self._count_tokens(manifest.company.dict())

            # ICPs
            if manifest.icps:
                icp_tokens = sum(
                    self._count_tokens(icp.dict()) for icp in manifest.icps
                )
                token_counts["icps"] = icp_tokens

            # Competitors
            competitor_data = {
                "competitors": manifest.competitors,
                "direct_competitors": manifest.direct_competitors,
                "indirect_competitors": manifest.indirect_competitors,
                "positioning_delta": manifest.positioning_delta,
            }
            token_counts["competitors"] = self._count_tokens(competitor_data)

            # Brand
            brand_data = {
                "brand": manifest.brand,
                "values": manifest.values,
                "personality": manifest.personality,
                "tone": manifest.tone,
                "positioning": manifest.positioning,
            }
            token_counts["brand"] = self._count_tokens(brand_data)

            # Market
            market_data = {
                "market": manifest.market,
                "verticals": manifest.verticals,
                "geography": manifest.geography,
            }
            token_counts["market"] = self._count_tokens(market_data)

            # Messaging
            messaging_data = {
                "messaging": manifest.messaging,
                "value_prop": manifest.value_prop,
                "taglines": manifest.taglines,
                "key_messages": manifest.key_messages,
                "soundbites": manifest.soundbites,
            }
            token_counts["messaging"] = self._count_tokens(messaging_data)

            # Channels
            channel_data = {
                "channels": manifest.channels,
                "primary_channels": manifest.primary_channels,
                "secondary_channels": manifest.secondary_channels,
                "strategy_summary": manifest.strategy_summary,
            }
            token_counts["channels"] = self._count_tokens(channel_data)

            # Goals
            goals_data = {
                "goals": manifest.goals,
                "short_term_goals": manifest.short_term_goals,
                "long_term_goals": manifest.long_term_goals,
                "kpis": manifest.kpis,
            }
            token_counts["goals"] = self._count_tokens(goals_data)

            # Issues (contradictions, wins, risks)
            issues_data = {
                "contradictions": manifest.contradictions,
                "recent_wins": manifest.recent_wins,
                "risks": manifest.risks,
            }
            token_counts["issues"] = self._count_tokens(issues_data)

            # Calculate total
            token_counts["total"] = sum(
                count for section, count in token_counts.items() if section != "total"
            )

        except Exception as e:
            logger.error(f"Error counting manifest tokens: {e}")
            # Fallback to counting entire manifest
            token_counts["total"] = self._count_tokens(manifest.dict())

        return token_counts

    def _compress_to_budget(
        self, manifest: BusinessContextManifest
    ) -> BusinessContextManifest:
        """
        Compress BCM manifest to stay within token budget while preserving critical information.

        This method uses intelligent compression strategies based on priority:
        1. ICPs (highest priority) - Keep all ICPs, compress descriptions
        2. Messaging (high priority) - Keep primary messages, compress secondary
        3. Competitive (medium priority) - Keep key competitors, compress details
        4. Brand (medium priority) - Keep core values, compress personality
        5. Market/Channels (low priority) - Aggressive compression

        Args:
            manifest: Original BCM manifest

        Returns:
            Compressed BCM manifest within token budget
        """
        if not self.tokenizer:
            logger.warning("Cannot compress without tokenizer")
            return manifest

        current_tokens = self._count_tokens(manifest.dict())
        if current_tokens <= self.max_token_budget:
            return manifest

        logger.info(
            f"Compressing BCM from {current_tokens} to {self.max_token_budget} tokens"
        )

        # Create a copy for compression
        compressed_manifest = manifest

        # Compression strategy based on token budget overrun
        overrun_percentage = (
            current_tokens - self.max_token_budget
        ) / self.max_token_budget

        if overrun_percentage <= 0.1:  # <= 10% overrun - light compression
            compressed_manifest = self._apply_light_compression(compressed_manifest)
        elif overrun_percentage <= 0.25:  # <= 25% overrun - medium compression
            compressed_manifest = self._apply_medium_compression(compressed_manifest)
        elif overrun_percentage <= 0.5:  # <= 50% overrun - heavy compression
            compressed_manifest = self._apply_heavy_compression(compressed_manifest)
        else:  # > 50% overrun - aggressive compression
            compressed_manifest = self._apply_aggressive_compression(
                compressed_manifest
            )

        # Final check and adjustment
        final_tokens = self._count_tokens(compressed_manifest.dict())
        if final_tokens > self.max_token_budget:
            logger.warning(
                f"Still over budget after compression: {final_tokens} > {self.max_token_budget}"
            )
            compressed_manifest = self._apply_emergency_compression(compressed_manifest)

        # Log compression statistics
        compression_ratio = (current_tokens - final_tokens) / current_tokens * 100
        logger.info(
            f"Compression complete: {current_tokens} -> {final_tokens} tokens ({compression_ratio:.1f}% reduction)"
        )

        return compressed_manifest

    def _apply_light_compression(
        self, manifest: BusinessContextManifest
    ) -> BusinessContextManifest:
        """Apply light compression (<= 10% reduction)."""
        # Compress long descriptions in ICPs
        compressed_icps = []
        for icp in manifest.icps:
            if icp.description and len(icp.description) > 200:
                # Keep first 200 chars + "..."
                icp.description = icp.description[:197] + "..."

            # Compress pain points descriptions
            compressed_pains = []
            for pain in icp.pains:
                if pain.description and len(pain.description) > 100:
                    pain.description = pain.description[:97] + "..."
                compressed_pains.append(pain)
            icp.pains = compressed_pains

            compressed_icps.append(icp)

        manifest.icps = compressed_icps

        # Compress key messages
        compressed_messages = []
        for message in manifest.key_messages:
            if message.content and len(message.content) > 150:
                message.content = message.content[:147] + "..."
            compressed_messages.append(message)
        manifest.key_messages = compressed_messages

        return manifest

    def _apply_medium_compression(
        self, manifest: BusinessContextManifest
    ) -> BusinessContextManifest:
        """Apply medium compression (<= 25% reduction)."""
        # Apply light compression first
        manifest = self._apply_light_compression(manifest)

        # Reduce ICPs to top 2 by confidence score
        if len(manifest.icps) > 2:
            manifest.icps = sorted(
                manifest.icps, key=lambda x: x.confidence_score, reverse=True
            )[:2]

        # Compress competitor information
        compressed_direct = []
        for comp in manifest.direct_competitors[:3]:  # Keep top 3
            # Keep only name and key strengths
            comp.strengths = comp.strengths[:2] if comp.strengths else []
            comp.weaknesses = []  # Remove weaknesses
            comp.market_share = None  # Remove market share
            compressed_direct.append(comp)
        manifest.direct_competitors = compressed_direct

        # Remove indirect competitors
        manifest.indirect_competitors = []

        # Compress messaging
        if manifest.key_messages:
            # Keep only top 3 messages
            manifest.key_messages = manifest.key_messages[:3]

        # Remove soundbites (lower priority)
        manifest.soundbites = []

        return manifest

    def _apply_heavy_compression(
        self, manifest: BusinessContextManifest
    ) -> BusinessContextManifest:
        """Apply heavy compression (<= 50% reduction)."""
        # Apply medium compression first
        manifest = self._apply_medium_compression(manifest)

        # Keep only top ICP
        if manifest.icps:
            manifest.icps = [max(manifest.icps, key=lambda x: x.confidence_score)]

            # Further compress ICP description
            icp = manifest.icps[0]
            if icp.description and len(icp.description) > 100:
                icp.description = icp.description[:97] + "..."

            # Keep only top 2 pain points
            icp.pains = icp.pains[:2] if icp.pains else []
            icp.goals = icp.goals[:2] if icp.goals else []
            icp.objections = []  # Remove objections
            icp.triggers = []  # Remove triggers

        # Keep only top 2 competitors
        manifest.direct_competitors = manifest.direct_competitors[:2]

        # Simplify competitor data
        for comp in manifest.direct_competitors:
            comp.strengths = comp.strengths[:1] if comp.strengths else []
            comp.weaknesses = []
            comp.pricing_model = None
            comp.target_segments = []

        # Compress brand information
        if manifest.values:
            manifest.values = manifest.values[:3]  # Keep top 3 values

        # Remove brand personality and tone
        manifest.personality = []
        manifest.tone = []

        # Keep only primary value proposition
        if manifest.value_prop:
            manifest.value_prop.secondary = None
            manifest.value_prop.supporting_points = []

        # Keep only top 2 key messages
        manifest.key_messages = (
            manifest.key_messages[:2] if manifest.key_messages else []
        )

        # Remove taglines
        manifest.taglines = []

        return manifest

    def _apply_aggressive_compression(
        self, manifest: BusinessContextManifest
    ) -> BusinessContextManifest:
        """Apply aggressive compression (> 50% reduction)."""
        # Apply heavy compression first
        manifest = self._apply_heavy_compression(manifest)

        # Keep only essential ICP information
        if manifest.icps:
            icp = manifest.icps[0]
            # Keep only name and core description
            if icp.description and len(icp.description) > 50:
                icp.description = icp.description[:47] + "..."

            # Remove most detailed information
            icp.pains = icp.pains[:1] if icp.pains else []
            icp.goals = []
            icp.objections = []
            icp.triggers = []
            icp.company_size = None
            icp.geography = []

        # Keep only top competitor
        if manifest.direct_competitors:
            comp = manifest.direct_competitors[0]
            # Keep only name
            comp.strengths = []
            comp.weaknesses = []
            comp.market_share = None
            comp.pricing_model = None
            comp.target_segments = []
            comp.website = None
            manifest.direct_competitors = [comp]

        # Minimal brand information
        if manifest.values:
            manifest.values = manifest.values[:2]  # Keep top 2 values

        # Remove most brand info
        manifest.personality = []
        manifest.tone = []
        manifest.brand = {}

        # Minimal messaging
        if manifest.value_prop:
            # Keep only primary value prop, truncate if needed
            if manifest.value_prop.primary and len(manifest.value_prop.primary) > 100:
                manifest.value_prop.primary = manifest.value_prop.primary[:97] + "..."
            manifest.value_prop.secondary = None
            manifest.value_prop.supporting_points = []

        # Keep only top key message
        manifest.key_messages = (
            manifest.key_messages[:1] if manifest.key_messages else []
        )

        # Remove all other messaging
        manifest.taglines = []
        manifest.soundbites = []
        manifest.messaging = {}

        # Minimal channel information
        if manifest.primary_channels:
            manifest.primary_channels = manifest.primary_channels[:2]  # Keep top 2
        manifest.secondary_channels = []
        manifest.channels = {}
        manifest.strategy_summary = None

        # Minimal goals
        if manifest.short_term_goals:
            manifest.short_term_goals = manifest.short_term_goals[:2]  # Keep top 2
        manifest.long_term_goals = []
        manifest.kpis = manifest.kpis[:3] if manifest.kpis else []  # Keep top 3 KPIs

        # Remove most issues
        manifest.contradictions = []
        manifest.recent_wins = []
        manifest.risks = (
            manifest.risks[:2] if manifest.risks else []
        )  # Keep top 2 risks

        # Remove market information
        manifest.market = None
        manifest.verticals = []
        manifest.geography = []

        return manifest

    def _apply_emergency_compression(
        self, manifest: BusinessContextManifest
    ) -> BusinessContextManifest:
        """Apply emergency compression for extreme cases."""
        # This is the absolute minimum - keep only the most critical information

        # Keep only ICP name
        if manifest.icps:
            icp = manifest.icps[0]
            icp.description = icp.name if icp.name else ""
            icp.pains = []
            icp.goals = []
            icp.objections = []
            icp.triggers = []
            icp.company_size = None
            icp.vertical = None
            icp.geography = []
            icp.confidence_score = 1.0
            manifest.icps = [icp]

        # Keep only competitor name
        if manifest.direct_competitors:
            comp = manifest.direct_competitors[0]
            comp.strengths = []
            comp.weaknesses = []
            comp.market_share = None
            comp.pricing_model = None
            comp.target_segments = []
            comp.website = None
            comp.type = "direct"
            manifest.direct_competitors = [comp]

        # Minimal company info
        if manifest.company:
            manifest.company.website = None
            manifest.company.sub_industry = None
            manifest.company.founded_year = None
            manifest.company.employee_count = None
            manifest.company.revenue_range = None
            manifest.company.headquarters = None

        # Keep only primary value prop name
        if manifest.value_prop and manifest.value_prop.primary:
            manifest.value_prop.primary = (
                manifest.value_prop.primary[:30] + "..."
                if len(manifest.value_prop.primary) > 30
                else manifest.value_prop.primary
            )
            manifest.value_prop.secondary = None
            manifest.value_prop.supporting_points = []

        # Remove everything else
        manifest.indirect_competitors = []
        manifest.positioning_delta = []
        manifest.values = []
        manifest.personality = []
        manifest.tone = []
        manifest.brand = {}
        manifest.positioning = None
        manifest.market = None
        manifest.verticals = []
        manifest.geography = []
        manifest.messaging = {}
        manifest.taglines = []
        manifest.key_messages = []
        manifest.soundbites = []
        manifest.channels = {}
        manifest.primary_channels = []
        manifest.secondary_channels = []
        manifest.strategy_summary = None
        manifest.goals = {}
        manifest.short_term_goals = []
        manifest.long_term_goals = []
        manifest.kpis = []
        manifest.contradictions = []
        manifest.recent_wins = []
        manifest.risks = []

        return manifest

    def _compute_checksum(self, manifest: Dict[str, Any]) -> str:
        """
        Compute SHA-256 checksum of manifest JSON for data integrity verification.

        Args:
            manifest: BCM manifest as dictionary

        Returns:
            SHA-256 checksum as hex string
        """
        try:
            # Create a normalized JSON representation for consistent hashing
            # Sort keys and remove whitespace for deterministic output
            manifest_str = json.dumps(manifest, sort_keys=True, separators=(",", ":"))

            # Compute SHA-256 hash
            checksum = hashlib.sha256(manifest_str.encode("utf-8")).hexdigest()

            return checksum
        except Exception as e:
            logger.error(f"Error computing checksum: {e}")
            # Return empty string on error (or could raise exception)
            return ""

    def _verify_checksum(
        self, manifest: Dict[str, Any], expected_checksum: str
    ) -> bool:
        """
        Verify that a manifest matches its expected checksum.

        Args:
            manifest: BCM manifest as dictionary
            expected_checksum: Expected SHA-256 checksum

        Returns:
            True if checksums match, False otherwise
        """
        try:
            computed_checksum = self._compute_checksum(manifest)
            is_valid = computed_checksum == expected_checksum

            if not is_valid:
                logger.warning(
                    f"Checksum verification failed: expected {expected_checksum[:16]}..., got {computed_checksum[:16]}..."
                )
            else:
                logger.debug("Checksum verification successful")

            return is_valid
        except Exception as e:
            logger.error(f"Error verifying checksum: {e}")
            return False

    def _add_checksum_to_manifest(
        self, manifest: BusinessContextManifest
    ) -> BusinessContextManifest:
        """
        Add checksum to manifest metadata.

        Args:
            manifest: BCM manifest

        Returns:
            Manifest with checksum added to metadata
        """
        try:
            manifest_dict = manifest.dict()
            checksum = self._compute_checksum(manifest_dict)

            # Add checksum to links metadata (temporary solution)
            # In a full implementation, this would be a dedicated field in the schema
            if not manifest.links:
                manifest.links = {}
            manifest.links["checksum"] = checksum
            manifest.links["checksum_algorithm"] = "sha256"
            manifest.links["checksum_timestamp"] = datetime.utcnow().isoformat()

            logger.debug(f"Added checksum to manifest: {checksum[:16]}...")

            return manifest
        except Exception as e:
            logger.error(f"Error adding checksum to manifest: {e}")
            return manifest
