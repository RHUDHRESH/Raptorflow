import logging
from typing import List, TypedDict, Optional
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field

logger = logging.getLogger("raptorflow.quality")

class BrandAlignment(BaseModel):
    """SOTA structured brand audit result."""
    is_aligned: bool
    score: float # 0 to 1
    tone_feedback: str
    violations: List[str]

class BrandGuardian:
    """
    SOTA Quality Control Node.
    Audits every asset against the RaptorFlow 'Founder-Operator' voice and core guidelines.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a ruthless editorial guardian. "
                       "Audit the following draft against the RaptorFlow Brand Kit. "
                       "VOICE: Founder-Operator (Calm, Expensive, Decisive). "
                       "NON-NEGOTIABLES: No emojis, no hype, no corporate fluff."),
            ("user", "Draft: {draft}\nGuidelines: {guidelines}")
        ])
        self.chain = self.prompt | llm.with_structured_output(BrandAlignment)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        draft = state.get("current_draft", "No content provided")
        guidelines = state.get("context_brief", {}).get("brand_kit", "Default RaptorFlow SOTA Rules")
        
        logger.info("Guardian is auditing brand alignment...")
        audit = await self.chain.ainvoke({"draft": draft, "guidelines": str(guidelines)})
        logger.info(f"Audit complete. Brand score: {audit.score}")
        
        return {
            "quality_score": audit.score,
            "brand_pass": audit.is_aligned,
            "messages": [f"Guardian: {audit.tone_feedback}"]
        }

class HypeLintResult(BaseModel):
    """SOTA structured hype detection result."""
    clean_content: str
    banned_words_found: List[str]
    hype_score: float # 0 to 1 (0 is best)

class HypeWordFilter:
    """
    SOTA Editorial Restraint Node.
    Penalizes and removes high-hype marketing speak (e.g., 'game-changer', 'revolutionary').
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of editorial restraint. "
                       "Identify and remove 'hype' words from the following draft. "
                       "BANNED: revolutionary, game-changing, cutting-edge, world-class, next-gen. "
                       "Replace them with precise, calm, and expensive alternatives."),
            ("user", "Draft: {draft}")
        ])
        self.chain = self.prompt | llm.with_structured_output(HypeLintResult)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        draft = state.get("current_draft", "No content")
        logger.info("Filtering hype words...")
        
        lint = await self.chain.ainvoke({"draft": draft})
        logger.info(f"Hype filtering complete. Found {len(lint.banned_words_found)} banned words.")
        
        return {
            "current_draft": lint.clean_content,
            "telemetry": [{"banned_words": lint.banned_words_found, "hype_score": lint.hype_score}]
        }

class ContentStats(BaseModel):
    """SOTA structured representation of content metrics."""
    reading_level: str
    word_count: int
    flow_score: float # 0 to 1

class StatsScorer:
    """
    SOTA Linguistic Metrics Node.
    Calculates reading level, word count, and flow quality for every asset.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a surgical linguistic analyst. "
                       "Calculate the reading level, word count, and overall flow score "
                       "for the following content."),
            ("user", "Content: {content}")
        ])
        self.chain = self.prompt | llm.with_structured_output(ContentStats)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        content = state.get("current_draft", "No content")
        logger.info("Calculating linguistic statistics...")
        
        stats = await self.chain.ainvoke({"content": content})
        logger.info(f"Statistics calculated. Flow Score: {stats.flow_score}")
        
        return {
            "telemetry": [stats.model_dump()]
        }

class EditorialCritique(BaseModel):
    """SOTA structured editorial feedback."""
    critique: str
    improvement_items: List[str]
    ready_for_refiner: bool

class EditorNode:
    """
    SOTA Recursive Refinement Node.
    Provides surgical 1st-pass critique of Creative outputs.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a ruthless editor-in-chief. "
                       "Critique the following creative draft for surgical precision, "
                       "impact, and brand alignment. Generate exactly 3-5 improvement items."),
            ("user", "Draft: {draft}")
        ])
        self.chain = self.prompt | llm.with_structured_output(EditorialCritique)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        draft = state.get("current_draft", "No content")
        logger.info("Editor is critiquing the draft...")
        
        output = await self.chain.ainvoke({"draft": draft})
        logger.info("Editorial critique complete.")
        
        return {
            "messages": [f"Editor: {item}" for item in output.improvement_items],
            "quality_score": 0.0, # Placeholder for overall score calculation node
            "status": "awaiting_refinement" if output.ready_for_refiner else "rejected"
        }

class RefinerNode:
    """
    SOTA Refinement Application Node.
    Surgically applies editorial feedback to the current draft.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a surgical creative refiner. "
                       "Apply the following editorial feedback to the draft. "
                       "Maintain the 'Calm, Expensive, Decisive' vibe."),
            ("user", "Draft: {draft}\nFeedback: {feedback}")
        ])
        self.llm = llm

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        draft = state.get("current_draft", "No content")
        feedback = state.get("messages", [])
        logger.info("Refining draft based on feedback...")
        
        res = await self.llm.ainvoke(self.prompt.format(draft=draft, feedback=str(feedback)))
        logger.info("Refinement complete.")
        
        return {
            "current_draft": res.content,
            "iteration_count": state.get("iteration_count", 0) + 1
        }

class StrategicRisk(BaseModel):
    """SOTA structured risk representation."""
    risk: str
    severity: float # 0 to 1
    impact: str

class RedTeamAnalysis(BaseModel):
    risks: List[StrategicRisk]

class RedTeamAgent:
    """
    SOTA Adversarial Vetting Node.
    Identifies strategic flaws, risks, and contradictory signals in the campaign.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of strategic risk management. "
                       "Try to 'break' the proposed campaign plan. "
                       "Find exactly 3 high-leverage risks or flaws."),
            ("user", "Plan: {arc}")
        ])
        self.chain = self.prompt | llm.with_structured_output(RedTeamAnalysis)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        arc = state.get("context_brief", {}).get("campaign_arc", {})
        logger.info("Red Teaming the strategic plan...")
        
        analysis = await self.chain.ainvoke({"arc": str(arc)})
        logger.info(f"Red Teaming complete. Found {len(analysis.risks)} strategic risks.")
        
        return {
            "telemetry": [{"risks": analysis.model_dump()["risks"]}]
        }

class ComplianceResult(BaseModel):
    """SOTA structured compliance result."""
    is_compliant: bool
    issues: List[str]
    risk_level: str # Low, Medium, High

class LegalComplianceGuard:
    """
    SOTA Risk Mitigation Node.
    Identifies prohibited marketing claims and regulatory risks in the draft.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of marketing compliance. "
                       "Audit the following draft for absolute, unsubstantiated claims "
                       "or prohibited language (e.g., 'guaranteed results')."),
            ("user", "Draft: {draft}")
        ])
        self.chain = self.prompt | llm.with_structured_output(ComplianceResult)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        draft = state.get("current_draft", "No content")
        logger.info("Auditing draft for legal compliance...")
        
        audit = await self.chain.ainvoke({"draft": draft})
        logger.info(f"Legal audit complete. Compliant: {audit.is_compliant}")
        
        return {
            "legal_pass": audit.is_compliant,
            "messages": [f"Legal: {issue}" for issue in audit.issues]
        }

class QualityGate:
    """
    SOTA Routing Node.
    Decides if the asset proceeds to 'finalize' or returns to 'refine' based on score.
    """
    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        score = state.get("quality_score", 0.0)
        brand_pass = state.get("brand_pass", False)
        legal_pass = state.get("legal_pass", False)
        
        logger.info(f"Quality Gate Evaluating: Score={score}, Brand={brand_pass}, Legal={legal_pass}")
        
        if score >= 0.8 and brand_pass and legal_pass:
            logger.info("Quality Gate PASSED.")
            return {"next_node": "finalize"}
        
        logger.warning("Quality Gate FAILED. Routing to refinement.")
        return {"next_node": "refine"}

class UIFeedbackIntegrator:
    """
    SOTA User Feedback Node.
    Processes manual user comments from the UI and generates pivot instructions.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a surgical creative coordinator. "
                       "Convert the user's feedback into exactly one technical instruction "
                       "for the specialist crew."),
            ("user", "User Feedback: {feedback}\nCurrent Draft: {draft}")
        ])
        self.llm = llm

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        # 'user_feedback' would be passed from UI via Command(resume=...)
        feedback = state.get("user_feedback", "No feedback provided")
        draft = state.get("current_draft", "")
        logger.info(f"Integrating UI feedback: {feedback[:50]}...")
        
        res = await self.llm.ainvoke(self.prompt.format(feedback=feedback, draft=draft))
        logger.info("Feedback integration complete.")
        
        return {
            "messages": [f"UI Feedback: {res.content}"],
            "next_node": "refine"
        }

class MemoryDecision(BaseModel):
    """SOTA structured representation of what to remember long-term."""
    should_remember: bool
    importance_score: float # 0 to 1
    extracted_fact: Optional[str]
    category: Optional[str]

class MemoryGovernor:
    """
    SOTA Intelligence Compounding Node.
    Decides if an insight or project result is worth storing in permanent semantic memory.
    """
    def __init__(self, llm: any):
        self.prompt = ChatPromptTemplate.from_messages([
            ("system", "You are a master of strategic knowledge management. "
                       "Identify if the provided asset contains a high-leverage brand insight "
                       "that must be remembered permanently (e.g., a new tone rule, a winning USP)."),
            ("user", "Asset: {asset}")
        ])
        self.chain = self.prompt | llm.with_structured_output(MemoryDecision)

    async def __call__(self, state: TypedDict):
        """Node execution logic."""
        asset = state.get("current_draft", "No asset")
        logger.info("Governing memory persistence...")
        
        decision = await self.chain.ainvoke({"asset": asset})
        logger.info(f"Memory decision complete. Should remember: {decision.should_remember}")
        
        if decision.should_remember:
            # We'd call save_memory here in production
            return {"messages": [f"System: Vaulted new insight - {decision.category}"]}
        
        return {}

def create_brand_guardian(llm: any):
    return BrandGuardian(llm)

def create_hype_filter(llm: any):
    return HypeWordFilter(llm)

def create_stats_scorer(llm: any):
    return StatsScorer(llm)

def create_editor_node(llm: any):
    return EditorNode(llm)

def create_refiner_node(llm: any):
    return RefinerNode(llm)

def create_red_team_agent(llm: any):
    return RedTeamAgent(llm)

def create_legal_guard(llm: any):
    return LegalComplianceGuard(llm)

def create_quality_gate():
    return QualityGate()

def create_feedback_integrator(llm: any):
    return UIFeedbackIntegrator(llm)

def create_memory_governor(llm: any):
    return MemoryGovernor(llm)
