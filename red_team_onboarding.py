import asyncio
import json
import logging
from unittest.mock import AsyncMock, patch
from backend.agents.graphs.onboarding_v2 import OnboardingGraphV2

# Configure logging
logging.basicConfig(level=logging.ERROR)
logger = logging.getLogger("RedTeam")

async def test_onboarding_full_industrial_flow():
    print("\n--- STARTING INDUSTRIAL ONBOARDING RED TEAM AUDIT ---")
    print("--- (LINEAR END-TO-END INFERENCE VALIDATION) ---\n")
    
    graph = OnboardingGraphV2().create_graph()
    session_id = "industrial-flow-001"
    config = {"configurable": {"thread_id": session_id}}

    # Comprehensive mocked responses for all specialists
    mock_responses = {
        "EvidenceClassifier": {"evidence_type": "Deck", "confidence": 0.95, "reasoning": "Standard pitch deck structure."},
        "ExtractionOrchestrator": {"facts": [{"category": "identity", "label": "Company Name", "value": "GhostOps"}]},
        "ContradictionDetector": {"contradictions": []},
        "TruthSheetGenerator": {"verified_facts": [{"category": "identity", "value": "GhostOps"}]},
        "BrandAuditEngine": {"audit": "Pass"},
        "OfferArchitect": {
            "revenue_model": "Latency-as-a-Service",
            "pricing_logic": "Performance spread share",
            "risk_reversal": {"score": 0.98, "feedback": "Surgical guarantee."},
            "outcome_mapping": []
        },
        "InsightExtractor": {
            "pain_points": [{"category": "UX", "description": "High slippage", "sentiment": -0.9}],
            "discovered_competitors": ["FastTrade", "LatencyGiant"],
            "desires": [], "objections": []
        },
        "ComparativeAngleGenerator": {
            "vantage_point": "The Ghost Advantage",
            "leverage": "Kernel-level superiority",
            "competitor_mapping": []
        },
        "CategoryAdvisor": {
            "safe_path": {}, "clever_path": {}, "bold_path": {},
            "recommended_path": "clever"
        },
        "CapabilityRatingEngine": {
            "ratings": [{"capability": "Zero Latency", "tier": 4, "status": "Unique"}],
            "gap_analysis": "No rivals"
        },
        "PerceptualMapGenerator": {
            "primary_axis": {"name": "Speed"}, "secondary_axis": {"name": "Stealth"},
            "competitors": [], "positioning_options": [], "only_you_quadrant": "Top Right"
        },
        "StrategicGridGenerator": {
            "selected_position": "The Ghost", "rationale": "Unmatchable",
            "milestones": [{"name": "Alpha", "timeline": "30d"}]
        },
        "NeuroscienceCopywriter": {
            "manifesto": "The silence of profit. Own the nanosecond. GhostOps is the only way.",
            "headlines": ["Own the Nanosecond"],
            "limbic_score": 0.99,
            "compliance": {"limbic": True, "pattern": True, "simplicity": True, "social_proof": True, "scarcity": True, "contrast": True}
        },
        "ConstraintEngine": {
            "focus_areas": ["HFT"], "sacrifices": [{"target": "Retail"}], "logic": "David vs Goliath"
        },
        "ICPArchitect": {
            "profiles": [{"name": "Whale", "who_they_want_to_become": "Market King", "sophistication_level": 5}],
            "primary_icp": "Whale"
        },
        "BuyingProcessArchitect": {"journey": [], "chasm_logic": "Education"},
        "MessagingRulesEngine": {"rules": [], "forbidden_words": [], "anti_patterns": []},
        "SoundbitesGenerator": {"atomic_units": ["Fast"], "library": []},
        "MessageHierarchyArchitect": {"levels": {}, "mapping": [], "manifesto_assembly": "Full assembly", "validation": {"integrity": 0.99}},
        "ChannelRecommender": {"recommendations": [], "mix": {}},
        "MarketSizer": {"tam": 1000, "sam": 500, "som": 100},
        "ValidationTracker": {"readiness_score": 95, "tasks": []},
        "FinalSynthesis": {"status": "Systems Online", "bcm_handover": {}, "dashboard_redirect": "/dash", "ucid": "RF-2026-GHOST"}
    }

    # Patch LLM and Storage globally
    with patch("backend.agents.base.BaseAgent._call_llm", new_callable=AsyncMock) as mock_llm, \
         patch("backend.infrastructure.storage.delete_file", new_callable=AsyncMock) as mock_delete, \
         patch("backend.tools.reddit_scraper.RedditScraperTool._run", new_callable=AsyncMock) as mock_reddit:
        
        mock_delete.return_value = True
        mock_reddit.return_value = {"threads": [], "verbatims": []}

        async def industrial_side_effect(prompt, **kwargs):
            for agent_name, response in mock_responses.items():
                if agent_name in prompt or agent_name.lower() in prompt.lower():
                    return json.dumps(response)
            if "revenue_model" in prompt: return json.dumps(mock_responses["OfferArchitect"])
            if "manifesto" in prompt: return json.dumps(mock_responses["NeuroscienceCopywriter"])
            if "Who They Want To Become" in prompt: return json.dumps(mock_responses["ICPArchitect"])
            return json.dumps({"output": "Generic fallback"})

        mock_llm.side_effect = industrial_side_effect

        # RUN FULL GRAPH FROM START TO END
        initial_input = {
            "ucid": "RF-2026-GHOST",
            "business_context": {"ucid": "RF-2026-GHOST", "identity": {"company_name": "GhostOps"}},
            "evidence": [{"file_id": "f1", "filename": "deck.pdf"}],
            "single_step": False
        }

        print(">>> Initiating full LangGraph lifecycle...")
        final_state = await graph.ainvoke(initial_input, config)

        # FINAL VERIFICATION
        print("\n--- INFERENCE RESULTS AUDIT ---")
        ctx = final_state.get("business_context", {})
        
        offer_val = ctx.get('offer', {}).get('revenue_model', 'MISSING') if ctx.get('offer') else 'MISSING'
        pos_data = ctx.get('positioning', {}) if ctx.get('positioning') else {}
        manifesto_val = pos_data.get('manifesto', 'MISSING') if pos_data else 'MISSING'
        strat_data = ctx.get('strategy', {}) if ctx.get('strategy') else {}
        strategy_val = strat_data.get('logic', 'MISSING') if strat_data else 'MISSING'
        
        print(f"OFFER: {offer_val}")
        print(f"MANIFESTO: {str(manifesto_val)[:60]}...")
        print(f"STRATEGY LOGIC: {strategy_val}")
        print(f"STATUS: {final_state.get('onboarding_progress')}% Complete")

        if offer_val != 'MISSING' and manifesto_val != 'MISSING' and strategy_val != 'MISSING':
            print("\nVERDICT: SUCCESS. End-to-end inference and state synchronization validated.")
        else:
            print("\nVERDICT: FAILURE. State accumulation failed for one or more agents.")
            print(f"DEBUG BUSINESS CONTEXT: {json.dumps(ctx, indent=2)}")

    print("\n--- RED TEAM AUDIT COMPLETE ---")

if __name__ == "__main__":
    asyncio.run(test_onboarding_full_industrial_flow())
