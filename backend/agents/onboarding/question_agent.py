"""
Question Agent - Generates contextual follow-up questions for onboarding.
"""

from typing import Dict, List, Optional, Any
import logging

from backend.config.settings import get_settings
from backend.config.prompts import ONBOARDING_SUPERVISOR_SYSTEM_PROMPT
from backend.services.openai_client import openai_client

logger = logging.getLogger(__name__)
settings = get_settings()


class QuestionAgent:
    """
    Generates dynamic, contextual questions for the onboarding flow.
    
    Responsibilities:
    - Determine entity type (Business, Personal Brand, Executive, Agency)
    - Generate relevant follow-up questions based on previous answers
    - Adapt question complexity based on user's expertise level
    - Ensure all critical information is captured
    """
    
    def __init__(self):
        self.question_modules = {
            "universal": [
                "What is your one-line clarity statement? (What you do and for whom)",
                "What are your primary marketing goals for the next 90 days?",
                "What marketing channels are you currently using or plan to use?",
                "What are your main constraints? (budget, time, team size, etc.)",
                "What tone should your content have? (professional, casual, inspirational, etc.)"
            ],
            "business": [
                "What industry does your business operate in?",
                "What is your company size and revenue range?",
                "What makes your solution different from competitors?",
                "What proof points do you have? (case studies, metrics, testimonials)",
                "Who is your ideal customer?"
            ],
            "personal_brand": [
                "What is your area of expertise or niche?",
                "What unique perspective do you bring?",
                "What are your main content pillars?",
                "How do you currently monetize or plan to monetize?",
                "What is your current audience size?"
            ],
            "executive": [
                "What is your role and company?",
                "What topics do you want to be known for as a thought leader?",
                "What speaking or publication experience do you have?",
                "What professional achievements should we highlight?",
                "What is your target audience for thought leadership?"
            ],
            "agency": [
                "Who is your client and what industry are they in?",
                "What are the campaign objectives?",
                "What are the reporting requirements?",
                "What is the approval workflow?",
                "What is the campaign budget and timeline?"
            ]
        }
    
    async def generate_next_question(
        self,
        entity_type: Optional[str],
        answers_so_far: List[Dict[str, str]],
        profile_completeness: Dict[str, bool]
    ) -> Dict[str, Any]:
        """
        Generates the next question based on conversation context.
        
        Args:
            entity_type: Type of entity (business, personal_brand, executive, agency)
            answers_so_far: List of previous Q&A pairs
            profile_completeness: Dict indicating which profile sections are complete
            
        Returns:
            Next question with metadata and guidance
        """
        # If entity type not determined, ask that first
        if not entity_type:
            return {
                "question_id": "entity_type",
                "question_text": "What best describes you?",
                "question_type": "single_choice",
                "options": [
                    {"value": "business", "label": "Business/Company", "description": "Promoting a product or service"},
                    {"value": "personal_brand", "label": "Personal Brand", "description": "Building your personal reputation"},
                    {"value": "executive", "label": "Executive/Thought Leader", "description": "Executive establishing thought leadership"},
                    {"value": "agency", "label": "Agency", "description": "Marketing for a client"}
                ],
                "required": True,
                "rationale": "This helps us tailor questions to your specific needs"
            }
        
        # Determine which sections still need completion
        incomplete_sections = [k for k, v in profile_completeness.items() if not v]
        
        if not incomplete_sections:
            return {
                "question_id": "complete",
                "question_text": None,
                "completed": True,
                "message": "Profile complete! Ready to generate your strategy."
            }
        
        # Use LLM to generate contextual follow-up
        conversation_history = "\n".join([
            f"Q: {qa['question_text']}\nA: {qa['answer']}"
            for qa in answers_so_far
        ])
        
        prompt = f"""
{ONBOARDING_SUPERVISOR_SYSTEM_PROMPT}

Entity Type: {entity_type}

Conversation so far:
{conversation_history}

Incomplete sections: {', '.join(incomplete_sections)}

Generate the next most important question to ask. The question should:
1. Be conversational and clear
2. Build on previous answers
3. Help complete the incomplete sections
4. Not be redundant with already answered questions

Available question modules for {entity_type}:
{self.question_modules.get(entity_type, [])}

Universal questions:
{self.question_modules['universal']}

Respond in JSON format:
{{
    "question_id": "unique_id",
    "question_text": "The question to ask",
    "question_type": "free_text|single_choice|multi_choice",
    "placeholder": "optional placeholder text",
    "options": [],  // if single_choice or multi_choice
    "required": true,
    "rationale": "Why this question is important",
    "validation": {{  // optional
        "min_length": 10,
        "max_length": 500
    }}
}}
"""
        
        try:
            messages = [
                {"role": "system", "content": ONBOARDING_SUPERVISOR_SYSTEM_PROMPT},
                {"role": "user", "content": prompt}
            ]
            
            response = await openai_client.chat_completion(
                messages=messages,
                temperature=0.7,
                response_format={"type": "json_object"}
            )
            
            import json
            next_question = json.loads(response)
            
            logger.info(f"Generated question: {next_question['question_id']}")
            return next_question
            
        except Exception as e:
            logger.error(f"Question generation failed: {e}")
            # Fallback to predefined questions
            return self._fallback_question(entity_type, incomplete_sections[0])
    
    def _fallback_question(self, entity_type: str, section: str) -> Dict[str, Any]:
        """Returns a predefined question as fallback."""
        fallback_questions = {
            "clarity_statement": {
                "question_id": "clarity_statement",
                "question_text": "In one sentence, what do you do and for whom?",
                "question_type": "free_text",
                "placeholder": "e.g., We help B2B sales teams close deals faster with AI insights",
                "required": True,
                "rationale": "This clarity statement guides all marketing messaging"
            },
            "goals": {
                "question_id": "primary_goal",
                "question_text": "What is your primary marketing goal for the next 90 days?",
                "question_type": "free_text",
                "placeholder": "e.g., Generate 100 qualified leads from enterprise segment",
                "required": True,
                "rationale": "Clear goals help us create a focused strategy"
            },
            "personas": {
                "question_id": "target_persona",
                "question_text": "Describe your ideal customer in a few sentences",
                "question_type": "free_text",
                "placeholder": "e.g., VP of Sales at mid-market companies, struggling with sales forecasting",
                "required": True,
                "rationale": "Understanding your audience shapes all content and targeting"
            }
        }
        
        return fallback_questions.get(
            section,
            {
                "question_id": section,
                "question_text": f"Please provide information about {section}",
                "question_type": "free_text",
                "required": True,
                "rationale": "This information helps complete your profile"
            }
        )
    
    def assess_profile_completeness(self, answers: List[Dict[str, str]], entity_type: str) -> Dict[str, bool]:
        """
        Assesses which sections of the profile are complete.
        
        Args:
            answers: List of answered questions
            entity_type: Type of entity
            
        Returns:
            Dict mapping section names to completion status
        """
        answered_ids = {qa["question_id"] for qa in answers}
        
        required_sections = {
            "entity_type": "entity_type" in answered_ids,
            "clarity_statement": any("clarity" in qid or "one-line" in qid for qid in answered_ids),
            "goals": any("goal" in qid for qid in answered_ids),
            "channels": any("channel" in qid for qid in answered_ids),
            "constraints": any("constraint" in qid or "budget" in qid for qid in answered_ids),
            "personas": any("persona" in qid or "customer" in qid or "audience" in qid for qid in answered_ids),
        }
        
        # Entity-specific requirements
        if entity_type == "business":
            required_sections["business_details"] = any(
                "industry" in qid or "company" in qid for qid in answered_ids
            )
        elif entity_type == "personal_brand":
            required_sections["personal_brand_details"] = any(
                "niche" in qid or "expertise" in qid for qid in answered_ids
            )
        
        return required_sections


# Global instance
question_agent = QuestionAgent()

