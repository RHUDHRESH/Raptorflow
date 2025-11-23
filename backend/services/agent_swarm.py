"""
Agent Swarm Service - Multi-agent collaborative decision making and debate.

Provides:
- Agent swarm coordination
- Multi-perspective debates
- Consensus building
- Collaborative problem solving
- Diverse viewpoint synthesis
"""

import structlog
from typing import Dict, List, Any, Optional, Literal
from datetime import datetime
import asyncio
from backend.services.vertex_ai_client import vertex_ai_client

logger = structlog.get_logger(__name__)


class AgentSwarmService:
    """
    Agent swarm service for multi-agent collaboration and debate.

    Features:
    - Multi-agent debate on strategic decisions
    - Diverse perspective generation
    - Consensus finding
    - Collective intelligence
    - Decision quality improvement through collaboration
    """

    def __init__(self):
        """Initialize agent swarm service."""
        self.max_agents = 5
        self.max_debate_rounds = 3
        logger.info("Agent swarm service initialized")

    async def debate(
        self,
        topic: str,
        context: Dict[str, Any],
        agent_roles: Optional[List[str]] = None,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run a multi-agent debate on a topic.

        Args:
            topic: Topic to debate
            context: Context information for the debate
            agent_roles: Roles for agents (optional, defaults to diverse perspectives)
            correlation_id: Correlation ID for tracking

        Returns:
            Debate results with arguments and consensus
        """
        try:
            # Define agent roles if not provided
            if not agent_roles:
                agent_roles = [
                    "conservative_marketer",  # Risk-averse, proven strategies
                    "innovative_disruptor",   # Bold, creative, experimental
                    "data_analyst",           # Focused on metrics and ROI
                    "customer_advocate",      # Prioritizes customer experience
                    "brand_strategist"        # Long-term brand building
                ]

            # Limit agents
            agent_roles = agent_roles[:self.max_agents]

            logger.info(
                "Starting agent debate",
                topic=topic,
                agent_count=len(agent_roles),
                correlation_id=correlation_id
            )

            # Run debate rounds
            debate_transcript = []
            arguments = {role: [] for role in agent_roles}

            for round_num in range(self.max_debate_rounds):
                logger.info(
                    f"Debate round {round_num + 1}",
                    correlation_id=correlation_id
                )

                # Each agent presents their argument
                round_arguments = await self._debate_round(
                    topic=topic,
                    context=context,
                    agent_roles=agent_roles,
                    previous_rounds=debate_transcript,
                    round_number=round_num,
                    correlation_id=correlation_id
                )

                # Store arguments
                for role, argument in round_arguments.items():
                    arguments[role].append(argument)

                debate_transcript.append({
                    "round": round_num + 1,
                    "arguments": round_arguments
                })

            # Build consensus
            consensus = await self._build_consensus(
                topic=topic,
                debate_transcript=debate_transcript,
                agent_roles=agent_roles,
                correlation_id=correlation_id
            )

            result = {
                "topic": topic,
                "agent_roles": agent_roles,
                "debate_rounds": len(debate_transcript),
                "transcript": debate_transcript,
                "arguments_by_agent": arguments,
                "consensus": consensus,
                "debated_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "Debate completed",
                topic=topic,
                consensus_reached=consensus.get("reached"),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                f"Agent debate failed: {e}",
                topic=topic,
                correlation_id=correlation_id
            )
            return {
                "topic": topic,
                "error": str(e),
                "debate_completed": False
            }

    async def collaborative_decision(
        self,
        decision_type: Literal["strategy", "content", "platform", "timing"],
        options: List[Dict[str, Any]],
        context: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Make a collaborative decision using agent swarm.

        Args:
            decision_type: Type of decision to make
            options: Available options to choose from
            context: Decision context
            correlation_id: Correlation ID for tracking

        Returns:
            Decision with rationale and agent votes
        """
        try:
            logger.info(
                "Starting collaborative decision",
                decision_type=decision_type,
                options_count=len(options),
                correlation_id=correlation_id
            )

            # Define decision-specific agent roles
            if decision_type == "strategy":
                agent_roles = ["growth_hacker", "brand_builder", "roi_optimizer"]
            elif decision_type == "content":
                agent_roles = ["content_creator", "seo_specialist", "engagement_expert"]
            elif decision_type == "platform":
                agent_roles = ["platform_specialist", "audience_analyst", "tech_strategist"]
            else:
                agent_roles = ["timing_expert", "data_scientist", "behavioral_psychologist"]

            # Each agent evaluates options
            agent_votes = {}

            for role in agent_roles:
                vote = await self._agent_evaluate_options(
                    role=role,
                    decision_type=decision_type,
                    options=options,
                    context=context,
                    correlation_id=correlation_id
                )
                agent_votes[role] = vote

            # Tally votes and determine winner
            option_scores = {i: 0 for i in range(len(options))}

            for role, vote in agent_votes.items():
                option_index = vote.get("chosen_option")
                if option_index is not None:
                    option_scores[option_index] += vote.get("confidence", 50)

            # Find winning option
            winning_index = max(option_scores.items(), key=lambda x: x[1])[0]
            winning_option = options[winning_index]

            result = {
                "decision_type": decision_type,
                "options_evaluated": len(options),
                "agent_votes": agent_votes,
                "option_scores": option_scores,
                "winning_option_index": winning_index,
                "winning_option": winning_option,
                "total_confidence": round(option_scores[winning_index] / len(agent_roles), 2),
                "decided_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "Collaborative decision completed",
                decision_type=decision_type,
                winning_option=winning_index,
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                f"Collaborative decision failed: {e}",
                decision_type=decision_type,
                correlation_id=correlation_id
            )
            return {
                "decision_type": decision_type,
                "error": str(e),
                "decision_made": False
            }

    async def synthesize_perspectives(
        self,
        question: str,
        context: Dict[str, Any],
        perspective_count: int = 3,
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate diverse perspectives on a question and synthesize them.

        Args:
            question: Question to answer
            context: Context information
            perspective_count: Number of perspectives to generate
            correlation_id: Correlation ID for tracking

        Returns:
            Multiple perspectives and synthesis
        """
        try:
            logger.info(
                "Generating perspectives",
                question=question,
                perspective_count=perspective_count,
                correlation_id=correlation_id
            )

            # Generate diverse perspectives
            perspectives = await self._generate_perspectives(
                question=question,
                context=context,
                count=perspective_count,
                correlation_id=correlation_id
            )

            # Synthesize perspectives
            synthesis = await self._synthesize_viewpoints(
                question=question,
                perspectives=perspectives,
                correlation_id=correlation_id
            )

            result = {
                "question": question,
                "perspectives": perspectives,
                "synthesis": synthesis,
                "perspective_count": len(perspectives),
                "synthesized_at": datetime.utcnow().isoformat()
            }

            logger.info(
                "Perspective synthesis completed",
                perspectives_count=len(perspectives),
                correlation_id=correlation_id
            )

            return result

        except Exception as e:
            logger.error(
                f"Perspective synthesis failed: {e}",
                question=question,
                correlation_id=correlation_id
            )
            return {
                "question": question,
                "error": str(e)
            }

    # ========== Helper Methods ==========

    async def _debate_round(
        self,
        topic: str,
        context: Dict[str, Any],
        agent_roles: List[str],
        previous_rounds: List[Dict[str, Any]],
        round_number: int,
        correlation_id: Optional[str] = None
    ) -> Dict[str, str]:
        """Execute one round of debate with all agents."""
        round_arguments = {}

        # Prepare context from previous rounds
        previous_context = ""
        if previous_rounds:
            previous_context = "\n\n".join([
                f"Round {r['round']}:\n" + "\n".join([
                    f"{role}: {arg}"
                    for role, arg in r['arguments'].items()
                ])
                for r in previous_rounds
            ])

        # Each agent makes their argument
        tasks = []
        for role in agent_roles:
            task = self._agent_argue(
                role=role,
                topic=topic,
                context=context,
                previous_arguments=previous_context,
                round_number=round_number,
                correlation_id=correlation_id
            )
            tasks.append((role, task))

        # Run agents in parallel
        for role, task in tasks:
            try:
                argument = await task
                round_arguments[role] = argument
            except Exception as e:
                logger.warning(f"Agent {role} failed to argue: {e}")
                round_arguments[role] = f"[Failed to generate argument: {str(e)}]"

        return round_arguments

    async def _agent_argue(
        self,
        role: str,
        topic: str,
        context: Dict[str, Any],
        previous_arguments: str,
        round_number: int,
        correlation_id: Optional[str] = None
    ) -> str:
        """Generate an agent's argument."""
        # Define role characteristics
        role_prompts = {
            "conservative_marketer": "You are a risk-averse marketer who values proven strategies and predictable outcomes.",
            "innovative_disruptor": "You are a bold innovator who pushes boundaries and tries experimental approaches.",
            "data_analyst": "You are a data-driven analyst who focuses on metrics, ROI, and quantifiable results.",
            "customer_advocate": "You are a customer experience expert who prioritizes user needs and satisfaction.",
            "brand_strategist": "You are a brand strategist focused on long-term reputation and brand equity."
        }

        role_prompt = role_prompts.get(role, f"You are a {role.replace('_', ' ')}.")

        prompt = f"""{role_prompt}

Debate Topic: {topic}

Context:
{context.get('description', 'No additional context provided.')}

{f"Previous Arguments:{previous_arguments}" if previous_arguments else "This is the first round of debate."}

Provide your argument on this topic (2-3 sentences). Be concise and focused on your role's perspective.
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                max_tokens=200,
                temperature=0.8,
                correlation_id=correlation_id
            )

            return response.get("text", "").strip()

        except Exception as e:
            logger.error(f"Failed to generate argument for {role}: {e}")
            return f"[Error generating argument]"

    async def _build_consensus(
        self,
        topic: str,
        debate_transcript: List[Dict[str, Any]],
        agent_roles: List[str],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Build consensus from debate transcript."""
        # Compile all arguments
        all_arguments = "\n\n".join([
            f"Round {round_data['round']}:\n" + "\n".join([
                f"{role}: {arg}"
                for role, arg in round_data['arguments'].items()
            ])
            for round_data in debate_transcript
        ])

        # Generate consensus summary
        prompt = f"""Based on the following multi-agent debate, synthesize the key points and areas of consensus.

Topic: {topic}

Debate Transcript:
{all_arguments}

Provide a synthesis that:
1. Identifies common ground between agents
2. Highlights key disagreements
3. Suggests a balanced approach that incorporates diverse viewpoints

Keep your response concise (3-4 sentences).
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                max_tokens=300,
                temperature=0.7,
                correlation_id=correlation_id
            )

            consensus_text = response.get("text", "").strip()

            # Simple consensus detection (in production use NLP)
            consensus_reached = "agree" in consensus_text.lower() or "consensus" in consensus_text.lower()

            return {
                "reached": consensus_reached,
                "synthesis": consensus_text,
                "agent_count": len(agent_roles),
                "rounds_conducted": len(debate_transcript)
            }

        except Exception as e:
            logger.error(f"Failed to build consensus: {e}")
            return {
                "reached": False,
                "error": str(e)
            }

    async def _agent_evaluate_options(
        self,
        role: str,
        decision_type: str,
        options: List[Dict[str, Any]],
        context: Dict[str, Any],
        correlation_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Agent evaluates options and votes."""
        # Format options for prompt
        options_text = "\n".join([
            f"Option {i}: {opt.get('name', f'Option {i}')} - {opt.get('description', '')}"
            for i, opt in enumerate(options)
        ])

        prompt = f"""As a {role.replace('_', ' ')}, evaluate the following options for {decision_type}.

Context:
{context.get('description', '')}

Options:
{options_text}

Choose the best option and provide your confidence score (0-100). Respond in format:
Chosen: <option_number>
Confidence: <score>
Reason: <brief reason>
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                max_tokens=150,
                temperature=0.7,
                correlation_id=correlation_id
            )

            # Parse response (simplified)
            response_text = response.get("text", "")

            # Extract option number
            chosen_option = 0
            if "Chosen:" in response_text:
                try:
                    chosen_option = int(response_text.split("Chosen:")[1].split()[0])
                except Exception:
                    pass

            # Extract confidence
            confidence = 50
            if "Confidence:" in response_text:
                try:
                    confidence = int(response_text.split("Confidence:")[1].split()[0])
                except Exception:
                    pass

            return {
                "chosen_option": chosen_option,
                "confidence": confidence,
                "reasoning": response_text
            }

        except Exception as e:
            logger.error(f"Agent evaluation failed for {role}: {e}")
            return {
                "chosen_option": 0,
                "confidence": 0,
                "error": str(e)
            }

    async def _generate_perspectives(
        self,
        question: str,
        context: Dict[str, Any],
        count: int,
        correlation_id: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """Generate diverse perspectives on a question."""
        perspective_styles = [
            "analytical and data-driven",
            "creative and innovative",
            "practical and execution-focused",
            "strategic and long-term",
            "customer-centric and empathetic"
        ]

        perspectives = []

        for i in range(min(count, len(perspective_styles))):
            style = perspective_styles[i]

            prompt = f"""Provide a {style} perspective on the following question:

Question: {question}

Context:
{context.get('description', '')}

Provide your perspective in 2-3 sentences.
"""

            try:
                response = await vertex_ai_client.generate_text(
                    prompt=prompt,
                    max_tokens=150,
                    temperature=0.8,
                    correlation_id=correlation_id
                )

                perspectives.append({
                    "style": style,
                    "perspective": response.get("text", "").strip()
                })

            except Exception as e:
                logger.warning(f"Failed to generate perspective {i}: {e}")

        return perspectives

    async def _synthesize_viewpoints(
        self,
        question: str,
        perspectives: List[Dict[str, Any]],
        correlation_id: Optional[str] = None
    ) -> str:
        """Synthesize multiple perspectives into a unified answer."""
        perspectives_text = "\n\n".join([
            f"{p['style'].title()} Perspective:\n{p['perspective']}"
            for p in perspectives
        ])

        prompt = f"""Synthesize the following diverse perspectives into a balanced, comprehensive answer.

Question: {question}

Perspectives:
{perspectives_text}

Provide a synthesis that incorporates insights from all perspectives (3-4 sentences).
"""

        try:
            response = await vertex_ai_client.generate_text(
                prompt=prompt,
                max_tokens=250,
                temperature=0.7,
                correlation_id=correlation_id
            )

            return response.get("text", "").strip()

        except Exception as e:
            logger.error(f"Perspective synthesis failed: {e}")
            return "Unable to synthesize perspectives."


# Global agent swarm instance
agent_swarm = AgentSwarmService()
