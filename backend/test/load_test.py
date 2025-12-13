from locust import HttpUser, task, between
import json
import os

class RaptorFlowUser(HttpUser):
    wait_time = between(1, 3)

    def on_start(self):
        """Setup before starting tasks"""
        self.token = os.getenv('TEST_JWT_TOKEN', 'test-token-123')
        self.headers = {
            'Authorization': f'Bearer {self.token}',
            'Content-Type': 'application/json'
        }

    @task(3)
    def test_plan_endpoint(self):
        """Test the /v2/plan endpoint"""
        payload = {
            "goal": "Create a marketing strategy for a SaaS startup",
            "context": {
                "campaign": {
                    "industry": "SaaS",
                    "target_market": "small businesses",
                    "budget": 25000
                },
                "icp": {
                    "demographics": "CTO/CFO of companies 50-200 employees",
                    "pain_points": ["inefficient processes", "high costs"]
                }
            }
        }

        with self.client.post("/v2/plan", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()  # Rate limited is expected under load
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def test_execute_endpoint(self):
        """Test the /v2/execute endpoint"""
        payload = {
            "plan_id": f"plan_{self.user_id}_{hash(str(self.environment.runner.stats))}",
            "priority": "balanced"
        }

        with self.client.post("/v2/execute", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code in [200, 202, 404]:  # 404 expected for mock plans
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def test_status_endpoint(self):
        """Test the /v2/status endpoint"""
        execution_id = f"exec_{self.user_id}_test"

        with self.client.get(f"/v2/status/{execution_id}", headers=self.headers, catch_response=True) as response:
            if response.status_code in [200, 404]:  # 404 expected for mock executions
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(2)
    def test_feedback_endpoint(self):
        """Test the /v2/feedback endpoint"""
        payload = {
            "execution_id": f"exec_{self.user_id}_feedback",
            "feedback_type": "positive",
            "feedback_text": "Great results, very helpful insights",
            "agent_outputs": {
                "market_intel_agent": {"confidence": 0.9, "insights": 5},
                "strategy_agent": {"recommendations": 8, "feasibility": 0.85}
            }
        }

        with self.client.post("/v2/feedback", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")

    @task(1)
    def test_advanced_orchestrate(self):
        """Test the advanced orchestration endpoint"""
        payload = {
            "goal": "Optimize our marketing funnel for better conversion rates",
            "context": {
                "current_performance": {
                    "awareness_rate": 0.15,
                    "consideration_rate": 0.08,
                    "conversion_rate": 0.03
                },
                "target_improvements": ["reduce bounce rate", "increase engagement"]
            }
        }

        with self.client.post("/v2/orchestrate", json=payload, headers=self.headers, catch_response=True) as response:
            if response.status_code == 200:
                response.success()
            elif response.status_code == 429:
                response.success()
            else:
                response.failure(f"Unexpected status code: {response.status_code}")


