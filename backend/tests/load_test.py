"""
Load Testing Framework for Raptorflow Payment System
Uses Locust for performance testing of payment endpoints
"""

import json
import random
import uuid
from datetime import datetime, timedelta
from typing import Dict, Any, List
import logging

from locust import HttpUser, task, between, events
from locust.env import Environment
from locust.stats import stats_printer, stats_history
from locust.log import setup_logging

# Setup logging
setup_logging("INFO", None)
logger = logging.getLogger(__name__)

class PaymentLoadTest(HttpUser):
    """
    Load testing user for payment endpoints
    Simulates realistic user behavior with payment flows
    """
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between requests
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.user_id = f"user_{uuid.uuid4().hex[:8]}"
        self.auth_token = None
        self.active_transactions = []
        
    def on_start(self):
        """Called when a simulated user starts"""
        logger.info(f"User {self.user_id} starting load test")
        # Simulate user authentication
        self.authenticate()
    
    def authenticate(self):
        """Simulate user authentication"""
        auth_data = {
            "email": f"test_{self.user_id}@example.com",
            "password": "test_password_123"
        }
        
        response = self.client.post("/api/v1/auth/login", json=auth_data)
        if response.status_code == 200:
            data = response.json()
            self.auth_token = data.get("access_token")
            self.client.headers.update({
                "Authorization": f"Bearer {self.auth_token}"
            })
            logger.info(f"User {self.user_id} authenticated successfully")
        else:
            logger.warning(f"User {self.user_id} authentication failed")
    
    @task(3)
    def initiate_payment(self):
        """Initiate a new payment transaction"""
        if not self.auth_token:
            return
            
        payment_data = {
            "amount": random.choice([100, 500, 1000, 2500, 5000]),
            "merchant_order_id": f"MO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}",
            "redirect_url": "https://example.com/payment/success",
            "callback_url": "https://example.com/payment/callback",
            "customer_info": {
                "id": self.user_id,
                "email": f"test_{self.user_id}@example.com",
                "phone": f"+91{random.randint(6000000000, 9999999999)}",
                "name": f"Test User {self.user_id}"
            },
            "metadata": {
                "source": "load_test",
                "user_agent": "Locust Load Tester"
            }
        }
        
        with self.client.post(
            "/api/v1/payments/initiate",
            json=payment_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                transaction_id = data.get("transaction_id")
                if transaction_id:
                    self.active_transactions.append({
                        "transaction_id": transaction_id,
                        "amount": payment_data["amount"],
                        "created_at": datetime.now()
                    })
                response.success()
                logger.info(f"Payment initiated: {transaction_id}")
            else:
                response.failure(f"Payment initiation failed: {response.status_code}")
                logger.error(f"Payment initiation failed: {response.text}")
    
    @task(2)
    def check_payment_status(self):
        """Check status of active transactions"""
        if not self.auth_token or not self.active_transactions:
            return
            
        # Get a random active transaction
        transaction = random.choice(self.active_transactions)
        transaction_id = transaction["transaction_id"]
        
        with self.client.get(
            f"/api/v1/payments/{transaction_id}/status",
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                status = data.get("status")
                
                # Remove completed transactions from active list
                if status in ["SUCCESS", "FAILED", "CANCELLED"]:
                    self.active_transactions.remove(transaction)
                
                response.success()
                logger.info(f"Payment status checked: {transaction_id} -> {status}")
            else:
                response.failure(f"Status check failed: {response.status_code}")
                logger.error(f"Status check failed: {response.text}")
    
    @task(1)
    def process_refund(self):
        """Process refund for completed transactions"""
        if not self.auth_token:
            return
            
        # Simulate refund for a random amount
        refund_data = {
            "merchant_order_id": f"MO{datetime.now().strftime('%Y%m%d%H%M%S')}{uuid.uuid4().hex[:8]}",
            "refund_amount": random.choice([100, 500, 1000]),
            "refund_reason": "Load test refund"
        }
        
        with self.client.post(
            "/api/v1/payments/refund",
            json=refund_data,
            catch_response=True
        ) as response:
            if response.status_code == 200:
                data = response.json()
                refund_id = data.get("refund_id")
                response.success()
                logger.info(f"Refund processed: {refund_id}")
            else:
                response.failure(f"Refund failed: {response.status_code}")
                logger.error(f"Refund failed: {response.text}")
    
    @task(1)
    def get_payment_history(self):
        """Get payment history for user"""
        if not self.auth_token:
            return
            
        with self.client.get(
            "/api/v1/payments/history",
            params={"limit": 10, "offset": 0},
            catch_response=True
        ) as response:
            if response.status_code == 200:
                response.success()
                logger.info("Payment history retrieved")
            else:
                response.failure(f"History retrieval failed: {response.status_code}")
                logger.error(f"History retrieval failed: {response.text}")


class PaymentStressTest(PaymentLoadTest):
    """
    Stress testing user with higher frequency requests
    """
    wait_time = between(0.1, 0.5)  # Very short wait time for stress testing
    
    @task(5)
    def initiate_payment_stress(self):
        """High frequency payment initiation for stress testing"""
        self.initiate_payment()


class PaymentSpikeTest(PaymentLoadTest):
    """
    Spike testing user to simulate sudden traffic spikes
    """
    wait_time = between(0.01, 0.1)  # Minimal wait time for spike testing


# Custom event handlers for detailed metrics
@events.request.add_listener
def on_request(request_type, name, response_time, response_length, exception, **kwargs):
    """
    Custom request event handler for detailed logging
    """
    if exception:
        logger.error(f"Request failed: {name} - {exception}")
    else:
        logger.info(f"Request: {name} - {response_time}ms")


@events.test_start.add_listener
def on_test_start(environment, **kwargs):
    """
    Called when the load test starts
    """
    logger.info("Load test started")
    logger.info(f"Target host: {environment.host}")


@events.test_stop.add_listener
def on_test_stop(environment, **kwargs):
    """
    Called when the load test stops
    """
    logger.info("Load test completed")
    
    # Print summary statistics
    stats = environment.stats
    logger.info(f"Total requests: {stats.total.num_requests}")
    logger.info(f"Failures: {stats.total.num_failures}")
    logger.info(f"Average response time: {stats.total.avg_response_time}ms")
    logger.info(f"Median response time: {stats.total.median_response_time}ms")
    logger.info(f"95th percentile: {stats.total.get_response_time_percentile(0.95)}ms")


class LoadTestRunner:
    """
    Utility class to run load tests programmatically
    """
    
    def __init__(self, target_host: str):
        self.target_host = target_host
        self.environment = Environment(user_classes=[PaymentLoadTest])
        self.environment.host = target_host
    
    def run_load_test(self, num_users: int = 10, spawn_rate: int = 2, duration: int = 300):
        """
        Run a standard load test
        
        Args:
            num_users: Number of concurrent users to simulate
            spawn_rate: Rate at which users are spawned
            duration: Test duration in seconds
        """
        logger.info(f"Starting load test: {num_users} users, {spawn_rate}/s spawn rate, {duration}s duration")
        
        # Create environment
        env = Environment(user_classes=[PaymentLoadTest])
        env.host = self.target_host
        
        # Create greenlet runner
        from locust import runners
        runner = runners.LocalRunner(env)
        
        # Start the test
        runner.start(num_users=num_users, spawn_rate=spawn_rate)
        
        # Run for specified duration
        import gevent
        gevent.sleep(duration)
        
        # Stop the test
        runner.stop()
        
        # Print results
        stats_printer(env.stats)
        
        return env.stats
    
    def run_stress_test(self, num_users: int = 50, spawn_rate: int = 10, duration: int = 600):
        """
        Run a stress test with high load
        
        Args:
            num_users: Number of concurrent users to simulate
            spawn_rate: Rate at which users are spawned
            duration: Test duration in seconds
        """
        logger.info(f"Starting stress test: {num_users} users, {spawn_rate}/s spawn rate, {duration}s duration")
        
        env = Environment(user_classes=[PaymentStressTest])
        env.host = self.target_host
        
        runner = runners.LocalRunner(env)
        runner.start(num_users=num_users, spawn_rate=spawn_rate)
        
        import gevent
        gevent.sleep(duration)
        
        runner.stop()
        stats_printer(env.stats)
        
        return env.stats
    
    def run_spike_test(self, num_users: int = 100, spawn_rate: int = 50, duration: int = 120):
        """
        Run a spike test to simulate sudden traffic spikes
        
        Args:
            num_users: Number of concurrent users to simulate
            spawn_rate: Rate at which users are spawned
            duration: Test duration in seconds
        """
        logger.info(f"Starting spike test: {num_users} users, {spawn_rate}/s spawn rate, {duration}s duration")
        
        env = Environment(user_classes=[PaymentSpikeTest])
        env.host = self.target_host
        
        runner = runners.LocalRunner(env)
        runner.start(num_users=num_users, spawn_rate=spawn_rate)
        
        import gevent
        gevent.sleep(duration)
        
        runner.stop()
        stats_printer(env.stats)
        
        return env.stats


if __name__ == "__main__":
    # Example usage
    import sys
    
    if len(sys.argv) < 2:
        print("Usage: python load_test.py <target_host> [test_type]")
        print("test_type: load, stress, spike (default: load)")
        sys.exit(1)
    
    target_host = sys.argv[1]
    test_type = sys.argv[2] if len(sys.argv) > 2 else "load"
    
    runner = LoadTestRunner(target_host)
    
    if test_type == "stress":
        runner.run_stress_test()
    elif test_type == "spike":
        runner.run_spike_test()
    else:
        runner.run_load_test()
