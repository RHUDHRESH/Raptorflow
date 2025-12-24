from typing import List, TypedDict

from langgraph.graph import END, START, StateGraph

from backend.agents.specialists.strategy import ICPArchitectAgent, OfferArchitectAgent


class CampaignState(TypedDict):
    workspace_id: str
    goal: str
    timeline_days: int
    icps: List[dict]
    offer: dict
    channel_mix: List[str]
    assets: List[dict]
    status: str


async def define_audience(state: CampaignState):
    agent = ICPArchitectAgent()
    res = await agent.build_profile(state["goal"])
    return {"icps": [res.content], "status": "offer_creation"}


async def craft_offer(state: CampaignState):
    agent = OfferArchitectAgent()
    res = await agent.structure_offer(state["goal"])
    return {"offer": {"raw": res.content}, "status": "content_planning"}


async def build_content_calendar(state: CampaignState):
    # Logic to map offer + audience to 90-day timeline
    return {"assets": [{"day": 1, "type": "email"}], "status": "completed"}


def build_campaign_subgraph():
    """
    Sub-graph dedicated to 90-day strategic planning.
    Invoked by the main Spine when 'Campaign' intent is high.
    """
    workflow = StateGraph(CampaignState)

    workflow.add_node("audience", define_audience)
    workflow.add_node("offer", craft_offer)
    workflow.add_node("calendar", build_content_calendar)

    workflow.add_edge(START, "audience")
    workflow.add_edge("audience", "offer")
    workflow.add_edge("offer", "calendar")
    workflow.add_edge("calendar", END)

    return workflow.compile()
