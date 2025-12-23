import logging
from typing import Literal, TypedDict
from pydantic import BaseModel, Field
from langchain_core.prompts import ChatPromptTemplate

logger = logging.getLogger("raptorflow.classifier")

class Intent(BaseModel):
    """SOTA structured intent classification."""
    classification: Literal["move", "campaign", "chat", "ambiguous"] = Field(
        description="The type of marketing request: "
                    "'move' for single execution packets, "
                    "'campaign' for 90-day strategic arcs, "
                    "'chat' for general brand Q&A, "
                    "'ambiguous' if the prompt is too vague to classify."
    )
    confidence: float = Field(description="Confidence score between 0 and 1.")
    reasoning: str = Field(description="Brief explanation of why this classification was chosen.")

class IntentClassifier:
    """
    SOTA Intent Recognition Node.
    Ensures user prompts are routed to the correct tactical engine.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a tactical marketing intake specialist. "
                       "Classify the user's request with surgical precision."),
            ("user", "{input}")
        ])
        self.chain = self.prompt | llm.with_structured_output(Intent)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        user_input = state.get("raw_prompt", "")
        logger.info(f"Classifying intent for: {user_input[:50]}...")
        
        intent = await self.chain.ainvoke({"input": user_input})
        logger.info(f"Intent classified as '{intent.classification}' with {intent.confidence*100}% confidence.")
        
        return {"next_node": intent.classification, "context_brief": {"intent": intent.model_dump()}}

class AmbiguityResolver:
    """
    SOTA Ambiguity Resolver Node.
    Generates surgical clarifying questions for vague prompts.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a surgical marketing strategist. The user's prompt is too vague. "
                       "Generate exactly 3 specific clarifying questions to help us move forward."),
            ("user", "{input}")
        ])
        self.llm = llm

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        user_input = state.get("raw_prompt", "")
        logger.info(f"Resolving ambiguity for: {user_input[:50]}...")
        
        response = await self.llm.ainvoke(self.prompt.format(input=user_input))
        logger.info("Ambiguity resolution questions generated.")
        
        return {"final_output": response.content, "status": "awaiting_clarification"}

def create_intent_classifier(llm: any):
    return IntentClassifier(llm)

def create_ambiguity_resolver(llm: any):
    return AmbiguityResolver(llm)
