"""Performance tests for payment system"""

import asyncio
import os
import statistics

# Import payment service components
import sys
import time
from concurrent.futures import ThreadPoolExecutor
from unittest.mock import Mock, patch

import pytest

sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", ".."))

from services.payment_service import PaymentRequest, PaymentService


class TestPaymentPerformance:
    """Performance tests for payment system"""

    @pytest.fixture
    def mock_supabase(self):
        """Mock Supabase client for performance testing"""
        mock_client = Mock()
        mock_client.table.return_value.insert.return_value.select.return_value.single.return_value.execute.return_value.data = {
            "id": "test-transaction-id",
            "workspace_id": "test-workspace-id",
            "merchant_order_id": "ORD20240128123456ABCDEF",
            "amount": 4900,
            "status": "pending",
        }
        return mock_client

    @pytest.fixture
    def payment_service_instance(self, mock_supabase):
        """Create PaymentService instance with mocked dependencies"""
        with patch(
            "services.payment_service.get_supabase_admin", return_value=mock_supabase
        ):
            with patch.dict(
                "os.environ",
                {
                    "PHONEPE_MERCHANT_ID": "test-merchant-id",
                    "PHONEPE_SALT_KEY": "test-salt-key",
                    "PHONEPE_SALT_INDEX": "1",
                    "PHONEPE_ENVIRONMENT": "sandbox",
                },
            ):
                return PaymentService()

    def test_payment_initiation_performance(self, payment_service_instance):
        """Test payment initiation performance"""

        # Mock PhonePe API response
        with patch("httpx.Client") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "data": {
                    "instrumentResponse": {
                        "redirectInfo": {"url": "https://api.phonepe.com/checkout"}
                    },
                    "merchantTransactionId": "TXN123456789",
                },
            }
            mock_httpx.return_value.__enter__.return_value.post.return_value = (
                mock_response
            )

            # Create payment request
            request = PaymentRequest(
                workspace_id="test-workspace-id",
                plan="starter",
                amount=4900,
                customer_email="test@example.com",
                customer_name="Test User",
            )

            # Measure performance
            times = []
            for _ in range(10):
                start_time = time.time()
                result = payment_service_instance.initiate_payment(request)
                end_time = time.time()

                assert result.success is True
                times.append(end_time - start_time)

            # Performance assertions
            avg_time = statistics.mean(times)
            max_time = max(times)
            min_time = min(times)

            print(f"Payment Initiation Performance:")
            print(f"  Average: {avg_time:.3f}s")
            print(f"  Min: {min_time:.3f}s")
            print(f"  Max: {max_time:.3f}s")

            # Performance requirements
            assert avg_time < 2.0, f"Average time {avg_time:.3f}s exceeds 2s limit"
            assert max_time < 3.0, f"Max time {max_time:.3f}s exceeds 3s limit"

    def test_payment_status_check_performance(self, payment_service_instance):
        """Test payment status check performance"""

        # Mock PhonePe API response
        with patch("httpx.Client") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "data": {"state": "COMPLETED", "transactionId": "TXN123456789"},
            }
            mock_httpx.return_value.__enter__.return_value.get.return_value = (
                mock_response
            )

            # Mock transaction lookup
            with patch.object(
                payment_service_instance, "_get_transaction"
            ) as mock_get_tx:
                mock_get_tx.return_value = {
                    "id": "test-transaction-id",
                    "workspace_id": "test-workspace-id",
                    "status": "pending",
                }

                # Measure performance
                times = []
                for _ in range(20):
                    start_time = time.time()
                    result = payment_service_instance.check_payment_status(
                        "ORD20240128123456ABCDEF"
                    )
                    end_time = time.time()

                    assert result.success is True
                    times.append(end_time - start_time)

                # Performance assertions
                avg_time = statistics.mean(times)
                max_time = max(times)
                min_time = min(times)

                print(f"Payment Status Check Performance:")
                print(f"  Average: {avg_time:.3f}s")
                print(f"  Min: {min_time:.3f}s")
                print(f"  Max: {max_time:.3f}s")

                # Performance requirements
                assert avg_time < 1.0, f"Average time {avg_time:.3f}s exceeds 1s limit"
                assert max_time < 2.0, f"Max time {max_time:.3f}s exceeds 2s limit"

    def test_webhook_validation_performance(self, payment_service_instance):
        """Test webhook validation performance"""

        body = '{"test": "data"}'
        salt_key = "test-salt-key"
        expected_signature = (
            payment_service_instance._generate_sha256_checksum(f"{body}{salt_key}")
            + "###1"
        )

        # Measure performance
        times = []
        for _ in range(100):
            start_time = time.time()
            result = payment_service_instance.validate_webhook(
                f"X-VERIFY {expected_signature}", body
            )
            end_time = time.time()

            assert result["valid"] is True
            times.append(end_time - start_time)

        # Performance assertions
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)

        print(f"Webhook Validation Performance:")
        print(f"  Average: {avg_time:.6f}s")
        print(f"  Min: {min_time:.6f}s")
        print(f"  Max: {max_time:.6f}s")

        # Performance requirements
        assert avg_time < 0.01, f"Average time {avg_time:.6f}s exceeds 10ms limit"
        assert max_time < 0.05, f"Max time {max_time:.6f}s exceeds 50ms limit"

    def test_concurrent_payment_initiation(self, payment_service_instance):
        """Test concurrent payment initiation performance"""

        # Mock PhonePe API response
        with patch("httpx.Client") as mock_httpx:
            mock_response = Mock()
            mock_response.status_code = 200
            mock_response.json.return_value = {
                "success": True,
                "data": {
                    "instrumentResponse": {
                        "redirectInfo": {"url": "https://api.phonepe.com/checkout"}
                    },
                    "merchantTransactionId": "TXN123456789",
                },
            }
            mock_httpx.return_value.__enter__.return_value.post.return_value = (
                mock_response
            )

            def initiate_payment():
                request = PaymentRequest(
                    workspace_id="test-workspace-id",
                    plan="starter",
                    amount=4900,
                    customer_email="test@example.com",
                    customer_name="Test User",
                )
                return payment_service_instance.initiate_payment(request)

            # Test with 10 concurrent requests
            start_time = time.time()

            with ThreadPoolExecutor(max_workers=10) as executor:
                futures = [executor.submit(initiate_payment) for _ in range(10)]
                results = [future.result() for future in futures]

            end_time = time.time()

            # Verify all requests succeeded
            assert all(result.success for result in results)

            total_time = end_time - start_time
            avg_time_per_request = total_time / 10

            print(f"Concurrent Payment Initiation Performance:")
            print(f"  Total time: {total_time:.3f}s")
            print(f"  Average per request: {avg_time_per_request:.3f}s")
            print(f"  Requests per second: {10/total_time:.1f}")

            # Performance requirements
            assert (
                total_time < 5.0
            ), f"Total time {total_time:.3f}s exceeds 5s limit for 10 concurrent requests"
            assert (
                avg_time_per_request < 2.0
            ), f"Average time {avg_time_per_request:.3f}s exceeds 2s limit"

    def test_plan_loading_performance(self, payment_service_instance):
        """Test plan loading performance"""

        # Measure performance
        times = []
        for _ in range(50):
            start_time = time.time()
            plans = payment_service_instance.get_payment_plans()
            end_time = time.time()

            assert len(plans) == 3
            times.append(end_time - start_time)

        # Performance assertions
        avg_time = statistics.mean(times)
        max_time = max(times)
        min_time = min(times)

        print(f"Plan Loading Performance:")
        print(f"  Average: {avg_time:.6f}s")
        print(f"  Min: {min_time:.6f}s")
        print(f"  Max: {max_time:.6f}s")

        # Performance requirements
        assert avg_time < 0.001, f"Average time {avg_time:.6f}s exceeds 1ms limit"
        assert max_time < 0.005, f"Max time {max_time:.6f}s exceeds 5ms limit"

    def test_utility_function_performance(self, payment_service_instance):
        """Test utility function performance"""

        # Test base64 encoding
        data = "test string for encoding"

        times = []
        for _ in range(1000):
            start_time = time.time()
            encoded = payment_service_instance._encode_base64(data)
            end_time = time.time()

            times.append(end_time - start_time)

        avg_time = statistics.mean(times)
        print(f"Base64 Encoding Performance:")
        print(f"  Average: {avg_time:.6f}s")
        assert avg_time < 0.001, f"Base64 encoding too slow: {avg_time:.6f}s"

        # Test SHA256 checksum
        data = "test string for checksum"

        times = []
        for _ in range(1000):
            start_time = time.time()
            checksum = payment_service_instance._generate_sha256_checksum(data)
            end_time = time.time()

            times.append(end_time - start_time)

        avg_time = statistics.mean(times)
        print(f"SHA256 Checksum Performance:")
        print(f"  Average: {avg_time:.6f}s")
        assert avg_time < 0.001, f"SHA256 checksum too slow: {avg_time:.6f}s"

    def test_memory_usage(self, payment_service_instance):
        """Test memory usage patterns"""

        import gc

        import psutil

        # Get initial memory usage
        process = psutil.Process()
        initial_memory = process.memory_info().rss / 1024 / 1024  # MB

        # Create many payment requests
        requests = []
        for i in range(1000):
            request = PaymentRequest(
                workspace_id=f"test-workspace-{i}",
                plan="starter",
                amount=4900,
                customer_email=f"test{i}@example.com",
                customer_name=f"Test User {i}",
            )
            requests.append(request)

        # Get memory after creating requests
        memory_after_requests = process.memory_info().rss / 1024 / 1024  # MB

        # Clear requests and force garbage collection
        del requests
        gc.collect()

        # Get memory after cleanup
        memory_after_cleanup = process.memory_info().rss / 1024 / 1024  # MB

        print(f"Memory Usage:")
        print(f"  Initial: {initial_memory:.1f} MB")
        print(f"  After requests: {memory_after_requests:.1f} MB")
        print(f"  After cleanup: {memory_after_cleanup:.1f} MB")
        print(f"  Peak increase: {memory_after_requests - initial_memory:.1f} MB")

        # Memory requirements
        peak_increase = memory_after_requests - initial_memory
        assert (
            peak_increase < 50
        ), f"Memory increase {peak_increase:.1f} MB exceeds 50MB limit"

        # Check memory is properly cleaned up
        cleanup_efficiency = (memory_after_requests - memory_after_cleanup) / (
            memory_after_requests - initial_memory
        )
        assert (
            cleanup_efficiency > 0.8
        ), f"Memory cleanup efficiency {cleanup_efficiency:.2f} below 80%"

    def test_error_handling_performance(self, payment_service_instance):
        """Test error handling performance"""

        # Test invalid plan error
        request = PaymentRequest(
            workspace_id="test-workspace-id",
            plan="invalid-plan",
            amount=4900,
            customer_email="test@example.com",
        )

        times = []
        for _ in range(100):
            start_time = time.time()
            try:
                payment_service_instance.initiate_payment(request)
            except Exception:
                pass  # Expected to fail
            end_time = time.time()

            times.append(end_time - start_time)

        avg_time = statistics.mean(times)
        print(f"Error Handling Performance:")
        print(f"  Average: {avg_time:.6f}s")
        assert avg_time < 0.01, f"Error handling too slow: {avg_time:.6f}s"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
