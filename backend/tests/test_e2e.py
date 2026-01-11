"""
End-to-end tests for RaptorFlow backend.
Tests complete user journeys and system workflows.
"""

import asyncio
import time
from typing import Any, Dict, List
from unittest.mock import AsyncMock, Mock, patch

import pytest


class TestEndToEndWorkflows:
    """Test suite for end-to-end workflows."""

    @pytest.fixture
    def mock_e2e_dependencies(self):
        """Mock end-to-end test dependencies."""
        db_client = Mock()
        redis_client = AsyncMock()
        memory_controller = AsyncMock()
        cognitive_engine = AsyncMock()
        agent_dispatcher = AsyncMock()

        # Mock database responses
        db_client.table.return_value.select.return_value.execute.return_value.data = [
            {"id": "workspace_1", "user_id": "user_1", "name": "Test Workspace"}
        ]
        db_client.table.return_value.insert.return_value.execute.return_value.data = [
            {"id": "new_record"}
        ]

        # Mock Redis responses
        redis_client.get.return_value = '{"test": "data"}'
        redis_client.setex.return_value = True
        redis_client.ping.return_value = True

        # Mock memory responses
        memory_controller.search.return_value = [
            {"content": "test memory", "score": 0.9, "memory_type": "foundation"}
        ]
        memory_controller.store.return_value = "memory_id"

        # Mock cognitive engine responses
        cognitive_engine.perception.perceive.return_value = Mock(
            intent="market_research",
            entities=[{"type": "company", "name": "Test Corp"}],
            confidence=0.9,
        )
        cognitive_engine.planning.plan.return_value = Mock(
            goal="Research market",
            steps=[{"action": "analyze", "duration": 60}],
            total_cost=0.5,
            risk_level="low",
        )
        cognitive_engine.reflection.reflect.return_value = Mock(
            quality_score=0.8, approved=True, feedback="Good quality"
        )

        # Mock agent responses
        agent = AsyncMock()
        agent.execute.return_value = {
            "success": True,
            "output": "Agent output",
            "tokens_used": 100,
        }
        agent_dispatcher.get_agent.return_value = agent

        return {
            "db_client": db_client,
            "redis_client": redis_client,
            "memory_controller": memory_controller,
            "cognitive_engine": cognitive_engine,
            "agent_dispatcher": agent_dispatcher,
        }

    @pytest.mark.asyncio
    async def test_complete_onboarding_journey(self, mock_e2e_dependencies):
        """Test complete onboarding journey from start to finish."""
        from backend.workflows.onboarding import OnboardingWorkflow

        workflow = OnboardingWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Evidence upload
        result = await workflow.execute_step(
            workspace_id=workspace_id,
            step="evidence_upload",
            data={
                "files": [
                    {
                        "filename": "business_plan.pdf",
                        "file_type": "pdf",
                        "file_size": 1024,
                    }
                ]
            },
        )

        assert result["success"] is True
        assert result["step"] == "evidence_upload"
        assert result["next_step"] == "evidence_extraction"

        # Step 2: Evidence extraction
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="evidence_extraction", data={}
        )

        assert result["success"] is True
        assert result["step"] == "evidence_extraction"
        assert result["next_step"] == "business_classification"

        # Step 3: Business classification
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="business_classification", data={}
        )

        assert result["success"] is True
        assert result["step"] == "business_classification"
        assert result["next_step"] == "industry_analysis"

        # Step 4: Industry analysis
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="industry_analysis", data={}
        )

        assert result["success"] is True
        assert result["step"] == "industry_analysis"
        assert result["next_step"] == "competitor_analysis"

        # Step 5: Competitor analysis
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="competitor_analysis", data={}
        )

        assert result["success"] is True
        assert result["step"] == "competitor_analysis"
        assert result["next_step"] == "value_proposition"

        # Step 6: Value proposition
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="value_proposition", data={}
        )

        assert result["success"] is True
        assert result["step"] == "value_proposition"
        assert result["next_step"] == "target_audience"

        # Step 7: Target audience
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="target_audience", data={}
        )

        assert result["success"] is True
        assert result["step"] == "target_audience"
        assert result["next_step"] == "messaging_framework"

        # Step 8: Messaging framework
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="messaging_framework", data={}
        )

        assert result["success"] is True
        assert result["step"] == "messaging_framework"
        assert result["next_step"] == "foundation_creation"

        # Step 9: Foundation creation
        result = await workflow.execute_step(
            workspace_id=workspace_id,
            step="foundation_creation",
            data={"business_name": "Test Business"},
        )

        assert result["success"] is True
        assert result["step"] == "foundation_creation"
        assert result["next_step"] == "icp_generation"

        # Step 10: ICP generation
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="icp_generation", data={}
        )

        assert result["success"] is True
        assert result["step"] == "icp_generation"
        assert result["next_step"] == "move_planning"

        # Step 11: Move planning
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="move_planning", data={}
        )

        assert result["success"] is True
        assert result["step"] == "move_planning"
        assert result["next_step"] == "campaign_setup"

        # Step 12: Campaign setup
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="campaign_setup", data={}
        )

        assert result["success"] is True
        assert result["step"] == "campaign_setup"
        assert result["next_step"] == "onboarding_complete"

        # Step 13: Onboarding complete
        result = await workflow.execute_step(
            workspace_id=workspace_id, step="onboarding_complete", data={}
        )

        assert result["success"] is True
        assert result["step"] == "onboarding_complete"
        assert result["next_step"] is None
        assert result["onboarding_complete"] is True

    @pytest.mark.asyncio
    async def test_move_execution_lifecycle(self, mock_e2e_dependencies):
        """Test complete move execution lifecycle."""
        from backend.workflows.move import MoveWorkflow

        workflow = MoveWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Create move
        result = await workflow.create_move(
            workspace_id=workspace_id,
            goal="Increase market share by 10%",
            move_type="strategic",
        )

        assert result["success"] is True
        move_id = result["move_id"]
        assert "plan" in result
        assert "tasks_created" in result

        # Step 2: Execute move
        result = await workflow.execute_move(move_id)

        assert result["success"] is True
        assert "execution_summary" in result
        assert "results" in result

        # Step 3: Complete move
        result = await workflow.complete_move(move_id)

        assert result["success"] is True
        assert "analysis" in result
        assert "insights" in result
        assert "recommendations" in result
        assert "completed_at" in result

    @pytest.mark.asyncio
    async def test_content_generation_pipeline(self, mock_e2e_dependencies):
        """Test complete content generation pipeline."""
        from backend.workflows.content import ContentWorkflow

        workflow = ContentWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Generate content
        result = await workflow.generate_content(
            workspace_id=workspace_id,
            request={
                "content_type": "blog",
                "title": "Test Blog Post",
                "topic": "Market Trends",
            },
        )

        assert result["success"] is True
        content_id = result["content_id"]
        assert "content" in result
        assert "quality_score" in result
        assert result["review_needed"] is not None

        # Step 2: Review content (if needed)
        if result["review_needed"]:
            review_result = await workflow.review_content(content_id)
            assert review_result["success"] is True
            assert "quality_score" in review_result
            assert "revision_needed" in review_result

            # Step 3: Revise content (if needed)
            if review_result["revision_needed"]:
                revision_result = await workflow.revise_content(
                    content_id, review_result["feedback"]
                )
                assert revision_result["success"] is True
                assert "revised_content" in revision_result
                assert "quality_score" in revision_result

        # Step 4: Publish content
        publish_result = await workflow.publish_content(
            content_id, {"channels": ["internal", "email"]}
        )

        assert publish_result["success"] is True
        assert "published_channels" in publish_result
        assert "published_at" in publish_result

    @pytest.mark.asyncio
    async def test_research_to_insights_workflow(self, mock_e2e_dependencies):
        """Test complete research to insights workflow."""
        from backend.workflows.research import ResearchWorkflow

        workflow = ResearchWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Conduct research
        result = await workflow.conduct_research(
            workspace_id=workspace_id,
            query="Competitor analysis for SaaS market",
            research_type="competitor",
        )

        assert result["success"] is True
        research_id = result["research_id"]
        assert "execution_results" in result
        assert "analysis" in result
        assert "insights" in result

        # Step 2: Store findings
        findings_result = await workflow.store_findings(
            workspace_id=workspace_id, findings=result["analysis"]
        )

        assert findings_result["success"] is True
        assert "findings_id" in findings_result

        # Step 3: Present results
        presentation_result = await workflow.present_results(research_id)

        assert presentation_result["success"] is True
        assert "presentation" in presentation_result
        assert "research_summary" in presentation_result

    @pytest.mark.asyncio
    async def test_blackbox_strategy_workflow(self, mock_e2e_dependencies):
        """Test complete blackbox strategy workflow."""
        from backend.workflows.blackbox import BlackboxWorkflow

        workflow = BlackboxWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Generate strategy
        result = await workflow.generate_strategy(workspace_id)

        assert result["success"] is True
        strategy_id = result["strategy_id"]
        assert "strategy" in result
        assert "risk_assessment" in result

        # Step 2: Review strategy
        review_result = await workflow.review_strategy(strategy_id)

        assert review_result["success"] is True
        assert "analysis" in review_result
        assert "feasibility" in review_result
        assert "conversion_ready" in review_result

        # Step 3: Convert to moves (if ready)
        if review_result["conversion_ready"]:
            conversion_result = await workflow.convert_to_move(strategy_id)

            assert conversion_result["success"] is True
            assert "moves_created" in conversion_result
            assert "move_ids" in conversion_result

    @pytest.mark.asyncio
    async def test_daily_wins_workflow(self, mock_e2e_dependencies):
        """Test complete daily wins workflow."""
        from backend.workflows.daily_wins import DailyWinsWorkflow

        workflow = DailyWinsWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Generate today's wins
        result = await workflow.generate_today(workspace_id)

        assert result["success"] is True
        daily_wins_id = result["daily_wins_id"]
        assert "wins" in result
        assert "context" in result

        # Step 2: Expand a win
        if result["wins"]:
            win_id = f"win_{daily_wins_id}"  # Mock win ID

            expansion_result = await workflow.expand_win(win_id)

            assert expansion_result["success"] is True
            assert "expanded_content" in expansion_result
            assert "quality_score" in expansion_result

            # Step 3: Schedule for publishing
            schedule_result = await workflow.schedule_win(
                win_id, "linkedin", {"publish_time": "2024-01-01 09:00:00"}
            )

            assert schedule_result["success"] is True
            assert "platform" in schedule_result
            assert "scheduled_at" in schedule_result

    @pytest.mark.asyncio
    async def test_campaign_lifecycle(self, mock_e2e_dependencies):
        """Test complete campaign lifecycle."""
        from backend.workflows.campaign import CampaignWorkflow

        workflow = CampaignWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Plan campaign
        result = await workflow.plan_campaign(
            workspace_id=workspace_id, goal="Launch Q1 product campaign"
        )

        assert result["success"] is True
        campaign_id = result["campaign_id"]
        assert "plan" in result
        assert "validation" in result

        # Step 2: Add moves to campaign
        moves = ["move_1", "move_2", "move_3"]
        add_result = await workflow.add_moves(campaign_id, moves)

        assert add_result["success"] is True
        assert add_result["moves_added"] == len(moves)

        # Step 3: Launch campaign
        launch_result = await workflow.launch_campaign(campaign_id)

        assert launch_result["success"] is True
        assert "execution_results" in launch_result
        assert "performance_metrics" in launch_result

        # Step 4: Generate results report
        report_result = await workflow.report_results(campaign_id)

        assert report_result["success"] is True
        assert "report" in report_result
        assert "generated_at" in report_result

    @pytest.mark.asyncio
    async def test_approval_workflow(self, mock_e2e_dependencies):
        """Test complete approval workflow."""
        from backend.workflows.approval import ApprovalWorkflow

        workflow = ApprovalWorkflow(**mock_e2e_dependencies)

        # Step 1: Submit for approval
        result = await workflow.submit_for_approval(
            output={
                "workspace_id": "test_workspace",
                "user_id": "test_user",
                "type": "content",
                "content": "Test content for approval",
            },
            risk_level="medium",
            reason="Content requires review",
        )

        assert result["success"] is True
        gate_id = result["gate_id"]
        assert result["status"] == "pending"

        # Step 2: Process approval
        process_result = await workflow.process_approval(
            gate_id, "approved", "Good quality content"
        )

        assert process_result["success"] is True
        assert process_result["decision"] == "approved"
        assert "approved_at" in process_result

        # Step 3: Test timeout handling
        timeout_result = await workflow.handle_timeout(gate_id)

        assert timeout_result["success"] is True
        assert "decision" in timeout_result

    @pytest.mark.asyncio
    async def test_feedback_integration(self, mock_e2e_dependencies):
        """Test complete feedback integration workflow."""
        from backend.workflows.feedback import FeedbackWorkflow

        workflow = FeedbackWorkflow(**mock_e2e_dependencies)
        workspace_id = "test_workspace"

        # Step 1: Collect feedback
        result = await workflow.collect_feedback(
            workspace_id=workspace_id,
            feedback_data={
                "content": "Great product, but UI could be improved",
                "type": "ui",
                "rating": 4,
                "metadata": {"feature": "dashboard"},
            },
            source="user",
        )

        assert result["success"] is True
        feedback_id = result["feedback_id"]
        assert result["source"] == "user"

        # Step 2: Analyze feedback
        analysis_result = await workflow.analyze_feedback(feedback_id)

        assert analysis_result["success"] is True
        assert "insights" in analysis_result
        assert "categorization" in analysis_result
        assert "sentiment" in analysis_result

        # Step 3: Integrate feedback
        integration_result = await workflow.integrate_feedback(feedback_id)

        assert integration_result["success"] is True
        assert "improvements" in integration_result
        assert "action_items" in integration_result


class TestSystemIntegration:
    """Test suite for complete system integration."""

    @pytest.mark.asyncio
    async def test_full_user_journey(self, mock_e2e_dependencies):
        """Test complete user journey from onboarding to campaign execution."""
        # Initialize all workflows
        from backend.workflows.campaign import CampaignWorkflow
        from backend.workflows.move import MoveWorkflow
        from backend.workflows.onboarding import OnboardingWorkflow

        onboarding = OnboardingWorkflow(**mock_e2e_dependencies)
        moves = MoveWorkflow(**mock_e2e_dependencies)
        campaigns = CampaignWorkflow(**mock_e2e_dependencies)

        workspace_id = "test_workspace"

        # Complete onboarding
        onboarding_result = await onboarding.execute_step(
            workspace_id=workspace_id,
            step="foundation_creation",
            data={"business_name": "Test Company"},
        )

        assert onboarding_result["success"] is True

        # Create strategic move
        move_result = await moves.create_move(
            workspace_id=workspace_id,
            goal="Establish market leadership",
            move_type="strategic",
        )

        assert move_result["success"] is True

        # Plan and launch campaign
        campaign_result = await campaigns.plan_campaign(
            workspace_id=workspace_id, goal="Q1 market leadership campaign"
        )

        assert campaign_result["success"] is True

        # Verify system state consistency
        assert onboarding_result["workspace_id"] == workspace_id
        assert move_result["workspace_id"] == workspace_id
        assert campaign_result["workspace_id"] == workspace_id

    @pytest.mark.asyncio
    async def test_error_recovery_flow(self, mock_e2e_dependencies):
        """Test error recovery and system resilience."""
        from backend.workflows.move import MoveWorkflow

        workflow = MoveWorkflow(**mock_e2e_dependencies)

        # Mock a failing move execution
        mock_e2e_dependencies[
            "agent_dispatcher"
        ].get_agent.return_value.execute.side_effect = Exception("Agent error")

        # Create move
        create_result = await workflow.create_move(
            workspace_id="test_workspace",
            goal="Test move with error",
            move_type="tactical",
        )

        assert create_result["success"] is True

        # Attempt execution (should handle error gracefully)
        execute_result = await workflow.execute_move(create_result["move_id"])

        # Should still return a result even with errors
        assert "execution_summary" in execute_result
        assert "results" in execute_result

    @pytest.mark.asyncio
    async def test_concurrent_workflows(self, mock_e2e_dependencies):
        """Test concurrent workflow execution."""
        from backend.workflows.content import ContentWorkflow
        from backend.workflows.research import ResearchWorkflow

        content_workflow = ContentWorkflow(**mock_e2e_dependencies)
        research_workflow = ResearchWorkflow(**mock_e2e_dependencies)

        workspace_id = "test_workspace"

        # Run multiple workflows concurrently
        tasks = [
            content_workflow.generate_content(
                workspace_id=workspace_id,
                request={"content_type": "blog", "title": "Test Blog"},
            ),
            research_workflow.conduct_research(
                workspace_id=workspace_id,
                query="Market research",
                research_type="market",
            ),
            content_workflow.generate_content(
                workspace_id=workspace_id,
                request={"content_type": "email", "title": "Test Email"},
            ),
        ]

        results = await asyncio.gather(*tasks, return_exceptions=True)

        # Verify all workflows completed successfully
        for result in results:
            if isinstance(result, Exception):
                pytest.fail(f"Concurrent workflow failed: {result}")
            else:
                assert result["success"] is True

    @pytest.mark.asyncio
    async def test_data_consistency(self, mock_e2e_dependencies):
        """Test data consistency across workflows."""
        from backend.integration.validation import ValidationService

        validation_service = ValidationService(
            db_client=mock_e2e_dependencies["db_client"],
            memory_controller=mock_e2e_dependencies["memory_controller"],
        )

        # Validate workspace consistency
        result = await validation_service.validate_workspace("test_workspace")

        assert "overall" in result
        assert "database" in result
        assert "memory" in result
        assert "cross_module" in result

        # Overall should be valid with mocked data
        assert result["overall"]["valid"] is True


if __name__ == "__main__":
    # Run end-to-end tests
    pytest.main([__file__, "-v", "-s"])
