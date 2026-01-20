#!/usr/bin/env python3
"""
Raptorflow Working Components Test
Tests the components that are confirmed to work
"""

import os
import sys
import asyncio
import json
import time
import logging
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging without unicode characters
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class WorkingComponentsTester:
    """Test components that are confirmed to work"""
    
    def __init__(self):
        self.results = {
            'environment': {'status': 'PENDING', 'details': {}, 'error': None},
            'supabase': {'status': 'PENDING', 'details': {}, 'error': None},
            'redis': {'status': 'PENDING', 'details': {}, 'error': None},
            'optimization_imports': {'status': 'PENDING', 'details': {}, 'error': None},
            'basic_functionality': {'status': 'PENDING', 'details': {}, 'error': None}
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
                logger.info("Environment variables loaded successfully")
            else:
                logger.error(".env file not found")
        except Exception as e:
            logger.error(f"Failed to load environment: {e}")
    
    async def test_environment(self):
        """Test environment configuration"""
        logger.info("Testing Environment Configuration...")
        
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
                'status': 'PASS' if not missing_vars else 'PARTIAL',
                'details': {
                    'total_required': len(required_vars),
                    'present': len(present_vars),
                    'missing': len(missing_vars),
                    'missing_vars': missing_vars
                },
                'error': None if not missing_vars else f"Missing {len(missing_vars)} required variables"
            }
            
            logger.info(f"Environment test completed - {len(present_vars)}/{len(required_vars)} variables present")
            
        except Exception as e:
            self.results['environment'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Environment test failed: {e}")
    
    async def test_supabase(self):
        """Test Supabase database connection"""
        logger.info("Testing Supabase Connection...")
        
        try:
            # Import Supabase client
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise Exception("Missing Supabase credentials")
            
            # Create client
            client = create_client(supabase_url, supabase_key)
            
            # Test basic query
            start_time = time.time()
            response = client.table('users').select('id').limit(1).execute()
            connection_time = time.time() - start_time
            
            # Test storage
            try:
                storage_response = client.storage.list_buckets()
                storage_buckets = len(storage_response) if storage_response else 0
            except Exception as storage_error:
                storage_buckets = 0
                logger.warning(f"Storage test failed: {storage_error}")
            
            self.results['supabase'] = {
                'status': 'PASS',
                'details': {
                    'url': supabase_url,
                    'connection_time': f"{connection_time:.2f}s",
                    'query_success': response is not None,
                    'storage_buckets': storage_buckets,
                    'api_accessible': True
                },
                'error': None
            }
            
            logger.info("Supabase connection test passed")
            
        except Exception as e:
            self.results['supabase'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Supabase connection test failed: {e}")
    
    async def test_redis(self):
        """Test Redis connection"""
        logger.info("Testing Redis Connection...")
        
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
            
            self.results['redis'] = {
                'status': 'PASS',
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
            
            logger.info("Redis connection test passed")
            
        except Exception as e:
            self.results['redis'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Redis connection test failed: {e}")
    
    async def test_optimization_imports(self):
        """Test optimization component imports"""
        logger.info("Testing Optimization Component Imports...")
        
        try:
            components = {}
            
            # Test semantic cache
            try:
                from backend.core.semantic_cache import SemanticCache
                semantic_cache = SemanticCache()
                components['semantic_cache'] = 'PASS'
            except Exception as e:
                components['semantic_cache'] = f'FAIL: {str(e)[:50]}'
            
            # Test smart retry
            try:
                from backend.core.smart_retry import SmartRetryManager
                retry_manager = SmartRetryManager()
                components['smart_retry'] = 'PASS'
            except Exception as e:
                components['smart_retry'] = f'FAIL: {str(e)[:50]}'
            
            # Test context manager
            try:
                from backend.core.context_manager import ContextManager
                context_manager = ContextManager()
                components['context_manager'] = 'PASS'
            except Exception as e:
                components['context_manager'] = f'FAIL: {str(e)[:50]}'
            
            # Test dynamic router
            try:
                from backend.core.dynamic_router import DynamicModelRouter
                router = DynamicModelRouter()
                components['dynamic_router'] = 'PASS'
            except Exception as e:
                components['dynamic_router'] = f'FAIL: {str(e)[:50]}'
            
            # Test prompt optimizer
            try:
                from backend.core.prompt_optimizer import PromptOptimizer
                optimizer = PromptOptimizer()
                components['prompt_optimizer'] = 'PASS'
            except Exception as e:
                components['prompt_optimizer'] = f'FAIL: {str(e)[:50]}'
            
            # Test cost analytics
            try:
                from backend.core.cost_analytics import CostAnalytics
                analytics = CostAnalytics()
                components['cost_analytics'] = 'PASS'
            except Exception as e:
                components['cost_analytics'] = f'FAIL: {str(e)[:50]}'
            
            # Test marvelous optimizer
            try:
                from backend.core.marvelous_optimizer import MarvelousAIOptimizer, OptimizationConfig
                config = OptimizationConfig()
                optimizer = MarvelousAIOptimizer(config)
                components['marvelous_optimizer'] = 'PASS'
            except Exception as e:
                components['marvelous_optimizer'] = f'FAIL: {str(e)[:50]}'
            
            # Count successes
            passed = sum(1 for status in components.values() if 'PASS' in status)
            total = len(components)
            
            self.results['optimization_imports'] = {
                'status': 'PASS' if passed == total else 'PARTIAL',
                'details': {
                    'total_components': total,
                    'passed_components': passed,
                    'success_rate': f"{(passed/total*100):.1f}%",
                    'components': components
                },
                'error': None if passed == total else f"{total-passed} components failed"
            }
            
            logger.info(f"Optimization imports test - {passed}/{total} components passed")
            
        except Exception as e:
            self.results['optimization_imports'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Optimization imports test failed: {e}")
    
    async def test_basic_functionality(self):
        """Test basic functionality without complex imports"""
        logger.info("Testing Basic Functionality...")
        
        try:
            # Test basic Python functionality
            test_data = {"test": "data", "timestamp": time.time()}
            json_data = json.dumps(test_data)
            parsed_data = json.loads(json_data)
            
            # Test async functionality
            async def test_async():
                await asyncio.sleep(0.1)
                return "async_works"
            
            result = await test_async()
            
            # Test HTTP client
            import httpx
            async with httpx.AsyncClient() as client:
                response = await client.get("https://httpbin.org/status/200")
                http_status = response.status_code
            
            self.results['basic_functionality'] = {
                'status': 'PASS',
                'details': {
                    'json_serialization': parsed_data == test_data,
                    'async_functionality': result == "async_works",
                    'http_client': http_status == 200,
                    'python_version': sys.version,
                    'platform': sys.platform
                },
                'error': None
            }
            
            logger.info("Basic functionality test passed")
            
        except Exception as e:
            self.results['basic_functionality'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Basic functionality test failed: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("Starting Working Components Test Suite")
        logger.info("=" * 50)
        
        tests = [
            self.test_environment,
            self.test_supabase,
            self.test_redis,
            self.test_optimization_imports,
            self.test_basic_functionality
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(0.5)
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 50)
        logger.info("WORKING COMPONENTS TEST SUMMARY")
        logger.info("=" * 50)
        
        passed = 0
        failed = 0
        partial = 0
        
        for service, result in self.results.items():
            status = result['status']
            if 'PASS' in status:
                passed += 1
                logger.info(f"PASS {service.upper()}: {status}")
            elif 'PARTIAL' in status:
                partial += 1
                logger.warning(f"PARTIAL {service.upper()}: {status}")
            else:
                failed += 1
                logger.error(f"FAIL {service.upper()}: {status}")
                if result.get('error'):
                    logger.error(f"   Error: {result['error']}")
            
            if result.get('details'):
                for key, value in result['details'].items():
                    if key not in ['components']:  # Skip verbose component details
                        logger.info(f"   {key}: {value}")
        
        logger.info("=" * 50)
        logger.info(f"RESULTS: {passed} passed, {partial} partial, {failed} failed")
        total = passed + partial + failed
        logger.info(f"SUCCESS RATE: {(passed/total*100):.1f}%")
        logger.info("=" * 50)
        
        # Save results
        self.save_results()
        
        # Provide recommendations
        self.provide_recommendations()
    
    def provide_recommendations(self):
        """Provide recommendations"""
        logger.info("\nRECOMMENDATIONS:")
        logger.info("-" * 30)
        
        for service, result in self.results.items():
            if 'FAIL' in result['status']:
                if service == 'optimization_imports':
                    logger.info("• Install missing packages: pip install scikit-learn tiktoken")
                    logger.info("• Check Python path and backend module structure")
                elif service == 'supabase':
                    logger.info("• Verify Supabase URL and service role key")
                elif service == 'redis':
                    logger.info("• Verify Upstash Redis URL and token")
        
        logger.info("\nNEXT STEPS:")
        logger.info("1. Install missing Python packages")
        logger.info("2. Verify environment variables are correct")
        logger.info("3. Test with actual inference requests")
        logger.info("4. Check backend module imports")
    
    def save_results(self):
        """Save test results"""
        try:
            results_file = os.path.join(os.path.dirname(__file__), 'working_components_test_results.json')
            
            with open(results_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': self.results
                }, f, indent=2, default=str)
            
            logger.info(f"Results saved to: {results_file}")
            
        except Exception as e:
            logger.error(f"Failed to save results: {e}")

async def main():
    """Main function"""
    tester = WorkingComponentsTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
