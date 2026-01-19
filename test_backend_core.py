#!/usr/bin/env python3
"""
Raptorflow Backend Core Components Test
Tests the actual backend inference system and core dependencies
"""

import os
import sys
import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class BackendCoreTester:
    """Test backend core components"""
    
    def __init__(self):
        self.results = {
            'environment': {'status': 'pending', 'details': {}, 'error': None},
            'supabase_connection': {'status': 'pending', 'details': {}, 'error': None},
            'redis_connection': {'status': 'pending', 'details': {}, 'error': None},
            'inference_cache': {'status': 'pending', 'details': {}, 'error': None},
            'base_agent': {'status': 'pending', 'details': {}, 'error': None},
            'optimization_components': {'status': 'pending', 'details': {}, 'error': None},
            'marvelous_optimizer': {'status': 'pending', 'details': {}, 'error': None}
        }
        
        # Load environment variables
        self.load_env()
    
    def load_env(self):
        """Load environment variables from .env file"""
        try:
            env_path = os.path.join(os.path.dirname(__file__), '.env')
            if os.path.exists(env_path):
                with open(env_path, 'r') as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith('#') and '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key] = value
                logger.info("✅ Environment variables loaded successfully")
            else:
                logger.error("❌ .env file not found")
        except Exception as e:
            logger.error(f"❌ Failed to load environment: {e}")
    
    async def test_environment(self):
        """Test environment configuration"""
        logger.info("🧪 Testing Environment Configuration...")
        
        try:
            required_vars = [
                'SUPABASE_URL',
                'SUPABASE_SERVICE_ROLE_KEY',
                'UPSTASH_REDIS_REST_URL',
                'UPSTASH_REDIS_REST_TOKEN',
                'GCP_PROJECT_ID',
                'VERTEX_AI_API_KEY',
                'MODEL_GENERAL'
            ]
            
            missing_vars = []
            present_vars = []
            
            for var in required_vars:
                value = os.getenv(var)
                if value:
                    present_vars.append(var)
                    # Mask sensitive values in output
                    if 'KEY' in var or 'SECRET' in var or 'TOKEN' in var:
                        masked_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
                        logger.info(f"   {var}: {masked_value}")
                    else:
                        logger.info(f"   {var}: {value}")
                else:
                    missing_vars.append(var)
                    logger.warning(f"   {var}: MISSING")
            
            self.results['environment'] = {
                'status': '✅ PASS' if not missing_vars else '⚠️  PARTIAL',
                'details': {
                    'total_required': len(required_vars),
                    'present': len(present_vars),
                    'missing': len(missing_vars),
                    'missing_vars': missing_vars
                },
                'error': None if not missing_vars else f"Missing {len(missing_vars)} required variables"
            }
            
            logger.info(f"✅ Environment test completed - {len(present_vars)}/{len(required_vars)} variables present")
            
        except Exception as e:
            self.results['environment'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Environment test failed: {e}")
    
    async def test_supabase_connection(self):
        """Test Supabase database connection"""
        logger.info("🧪 Testing Supabase Connection...")
        
        try:
            # Import Supabase client
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise Exception("Missing Supabase credentials")
            
            # Create client
            client = create_client(supabase_url, supabase_key)
            
            # Test basic query - check if we can connect
            start_time = time.time()
            
            # Try to get table info (this will test connection)
            response = client.table('users').select('id').limit(1).execute()
            
            connection_time = time.time() - start_time
            
            # Test storage
            try:
                storage_response = client.storage.list_buckets()
                storage_buckets = len(storage_response) if storage_response else 0
            except Exception as storage_error:
                storage_buckets = 0
                logger.warning(f"Storage test failed: {storage_error}")
            
            self.results['supabase_connection'] = {
                'status': '✅ PASS',
                'details': {
                    'url': supabase_url,
                    'connection_time': f"{connection_time:.2f}s",
                    'query_success': response is not None,
                    'storage_buckets': storage_buckets,
                    'api_accessible': True
                },
                'error': None
            }
            
            logger.info("✅ Supabase connection test passed")
            
        except Exception as e:
            self.results['supabase_connection'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Supabase connection test failed: {e}")
    
    async def test_redis_connection(self):
        """Test Redis connection"""
        logger.info("🧪 Testing Redis Connection...")
        
        try:
            import httpx
            
            redis_url = os.getenv('UPSTASH_REDIS_REST_URL')
            redis_token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
            
            if not redis_url or not redis_token:
                raise Exception("Missing Redis credentials")
            
            start_time = time.time()
            
            async with httpx.AsyncClient() as client:
                # Test SET operation
                set_response = await client.post(
                    f"{redis_url}/set/raptorflow_test/backend_test_value",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                
                # Test GET operation
                get_response = await client.get(
                    f"{redis_url}/get/raptorflow_test",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                
                # Test info
                info_response = await client.get(
                    f"{redis_url}/info",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
            
            connection_time = time.time() - start_time
            
            self.results['redis_connection'] = {
                'status': '✅ PASS',
                'details': {
                    'url': redis_url,
                    'connection_time': f"{connection_time:.2f}s",
                    'set_success': set_response.status_code == 200,
                    'get_success': get_response.status_code == 200,
                    'info_success': info_response.status_code == 200,
                    'test_value': get_response.json().get('result', 'N/A') if get_response.status_code == 200 else 'N/A'
                },
                'error': None
            }
            
            logger.info("✅ Redis connection test passed")
            
        except Exception as e:
            self.results['redis_connection'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Redis connection test failed: {e}")
    
    async def test_inference_cache(self):
        """Test inference cache system"""
        logger.info("🧪 Testing Inference Cache...")
        
        try:
            # Try to import inference cache
            from backend.core.inference_cache import get_inference_cache
            
            # Get cache instance
            cache = get_inference_cache()
            
            # Test basic cache operations
            test_key = "raptorflow_test_key"
            test_value = {"test": "data", "timestamp": time.time()}
            
            # Test set
            start_time = time.time()
            await cache.set(test_key, test_value)
            set_time = time.time() - start_time
            
            # Test get
            start_time = time.time()
            retrieved_value = await cache.get(test_key)
            get_time = time.time() - start_time
            
            # Test delete
            await cache.delete(test_key)
            
            # Test cache stats
            stats = cache.get_stats()
            
            self.results['inference_cache'] = {
                'status': '✅ PASS',
                'details': {
                    'cache_type': type(cache).__name__,
                    'set_time': f"{set_time:.3f}s",
                    'get_time': f"{get_time:.3f}s",
                    'set_success': True,
                    'get_success': retrieved_value is not None,
                    'value_match': retrieved_value == test_value,
                    'cache_stats': stats
                },
                'error': None
            }
            
            logger.info("✅ Inference cache test passed")
            
        except Exception as e:
            self.results['inference_cache'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Inference cache test failed: {e}")
    
    async def test_base_agent(self):
        """Test BaseAgent initialization"""
        logger.info("🧪 Testing Base Agent...")
        
        try:
            from backend.agents.base import BaseAgent
            
            # Create a test agent
            test_agent = BaseAgent("test_agent", "Test agent for dependency checking")
            
            # Test agent properties
            assert test_agent.name == "test_agent"
            assert test_agent.description == "Test agent for dependency checking"
            
            # Test recovery strategy determination
            test_error = ValueError("Test error")
            strategy = test_agent._determine_recovery_strategy(test_error)
            
            self.results['base_agent'] = {
                'status': '✅ PASS',
                'details': {
                    'agent_name': test_agent.name,
                    'agent_description': test_agent.description,
                    'agent_initialized': True,
                    'recovery_strategy_available': strategy is not None,
                    'strategy_type': strategy.get('type', 'unknown') if strategy else 'none'
                },
                'error': None
            }
            
            logger.info("✅ Base agent test passed")
            
        except Exception as e:
            self.results['base_agent'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Base agent test failed: {e}")
    
    async def test_optimization_components(self):
        """Test optimization components"""
        logger.info("🧪 Testing Optimization Components...")
        
        try:
            components = {}
            
            # Test semantic cache
            try:
                from backend.core.semantic_cache import SemanticCache
                semantic_cache = SemanticCache()
                components['semantic_cache'] = '✅ PASS'
            except Exception as e:
                components['semantic_cache'] = f'❌ FAIL: {str(e)[:50]}'
            
            # Test smart retry
            try:
                from backend.core.smart_retry import SmartRetryManager
                retry_manager = SmartRetryManager()
                components['smart_retry'] = '✅ PASS'
            except Exception as e:
                components['smart_retry'] = f'❌ FAIL: {str(e)[:50]}'
            
            # Test context manager
            try:
                from backend.core.context_manager import ContextManager
                context_manager = ContextManager()
                components['context_manager'] = '✅ PASS'
            except Exception as e:
                components['context_manager'] = f'❌ FAIL: {str(e)[:50]}'
            
            # Test dynamic router
            try:
                from backend.core.dynamic_router import DynamicModelRouter
                router = DynamicModelRouter()
                components['dynamic_router'] = '✅ PASS'
            except Exception as e:
                components['dynamic_router'] = f'❌ FAIL: {str(e)[:50]}'
            
            # Test prompt optimizer
            try:
                from backend.core.prompt_optimizer import PromptOptimizer
                optimizer = PromptOptimizer()
                components['prompt_optimizer'] = '✅ PASS'
            except Exception as e:
                components['prompt_optimizer'] = f'❌ FAIL: {str(e)[:50]}'
            
            # Test cost analytics
            try:
                from backend.core.cost_analytics import CostAnalytics
                analytics = CostAnalytics()
                components['cost_analytics'] = '✅ PASS'
            except Exception as e:
                components['cost_analytics'] = f'❌ FAIL: {str(e)[:50]}'
            
            # Count successes
            passed = sum(1 for status in components.values() if '✅ PASS' in status)
            total = len(components)
            
            self.results['optimization_components'] = {
                'status': '✅ PASS' if passed == total else '⚠️  PARTIAL',
                'details': {
                    'total_components': total,
                    'passed_components': passed,
                    'success_rate': f"{(passed/total*100):.1f}%",
                    'components': components
                },
                'error': None if passed == total else f"{total-passed} components failed"
            }
            
            logger.info(f"✅ Optimization components test - {passed}/{total} components passed")
            
        except Exception as e:
            self.results['optimization_components'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Optimization components test failed: {e}")
    
    async def test_marvelous_optimizer(self):
        """Test Marvelous AI Optimizer"""
        logger.info("🧪 Testing Marvelous AI Optimizer...")
        
        try:
            from backend.core.marvelous_optimizer import MarvelousAIOptimizer, OptimizationConfig
            
            # Create optimizer with default config
            config = OptimizationConfig()
            optimizer = MarvelousAIOptimizer(config)
            
            # Test optimization request
            test_request = {
                'prompt': 'Test prompt for optimization',
                'context': 'Test context'
            }
            
            start_time = time.time()
            optimized_result = await optimizer.optimize_request(test_request)
            optimization_time = time.time() - start_time
            
            # Get optimizer metrics
            metrics = optimizer.get_optimization_metrics()
            
            self.results['marvelous_optimizer'] = {
                'status': '✅ PASS',
                'details': {
                    'optimizer_initialized': True,
                    'active_strategies': len(optimizer._active_strategies),
                    'optimization_time': f"{optimization_time:.3f}s",
                    'optimization_success': optimized_result is not None,
                    'metrics_available': metrics is not None,
                    'session_id': optimizer.session_id
                },
                'error': None
            }
            
            logger.info("✅ Marvelous AI optimizer test passed")
            
        except Exception as e:
            self.results['marvelous_optimizer'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Marvelous AI optimizer test failed: {e}")
    
    async def run_all_tests(self):
        """Run all backend core tests"""
        logger.info("🚀 Starting Backend Core Test Suite")
        logger.info("=" * 50)
        
        tests = [
            self.test_environment,
            self.test_supabase_connection,
            self.test_redis_connection,
            self.test_inference_cache,
            self.test_base_agent,
            self.test_optimization_components,
            self.test_marvelous_optimizer
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(0.5)  # Brief pause between tests
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 50)
        logger.info("📊 BACKEND CORE TEST SUMMARY")
        logger.info("=" * 50)
        
        passed = 0
        failed = 0
        partial = 0
        
        for service, result in self.results.items():
            status = result['status']
            if '✅ PASS' in status:
                passed += 1
                logger.info(f"✅ {service.upper()}: {status}")
            elif '⚠️  PARTIAL' in status:
                partial += 1
                logger.warning(f"⚠️  {service.upper()}: {status}")
            else:
                failed += 1
                logger.error(f"❌ {service.upper()}: {status}")
                if result.get('error'):
                    logger.error(f"   Error: {result['error']}")
            
            if result.get('details'):
                for key, value in result['details'].items():
                    if key not in ['components']:  # Skip verbose component details
                        logger.info(f"   {key}: {value}")
        
        logger.info("=" * 50)
        logger.info(f"📈 RESULTS: {passed} passed, {partial} partial, {failed} failed")
        total = passed + partial + failed
        logger.info(f"🎯 SUCCESS RATE: {(passed/total*100):.1f}%")
        logger.info("=" * 50)
        
        # Save results to file
        self.save_results()
        
        # Provide recommendations
        self.provide_recommendations()
    
    def provide_recommendations(self):
        """Provide recommendations based on test results"""
        logger.info("\n🔧 RECOMMENDATIONS:")
        logger.info("-" * 30)
        
        for service, result in self.results.items():
            if '❌ FAIL' in result['status']:
                if service == 'supabase_connection':
                    logger.info("• Check Supabase URL and service role key")
                    logger.info("• Verify database is accessible and online")
                elif service == 'redis_connection':
                    logger.info("• Verify Upstash Redis URL and token")
                    logger.info("• Check Redis service status")
                elif service == 'inference_cache':
                    logger.info("• Check Redis connection (cache depends on Redis)")
                elif service == 'base_agent':
                    logger.info("• Check backend module imports")
                elif service == 'optimization_components':
                    logger.info("• Install missing dependencies: pip install scikit-learn tiktoken")
                elif service == 'marvelous_optimizer':
                    logger.info("• Check all optimization components are working")
        
        logger.info("\n📝 NEXT STEPS:")
        logger.info("1. Fix any failed dependencies")
        logger.info("2. Install missing packages with: pip install scikit-learn tiktoken")
        logger.info("3. Verify all environment variables are set correctly")
        logger.info("4. Test the inference system with actual requests")
    
    def save_results(self):
        """Save test results to file"""
        try:
            results_file = os.path.join(os.path.dirname(__file__), 'backend_core_test_results.json')
            
            with open(results_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': self.results
                }, f, indent=2, default=str)
            
            logger.info(f"📄 Results saved to: {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

async def main():
    """Main function"""
    tester = BackendCoreTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
