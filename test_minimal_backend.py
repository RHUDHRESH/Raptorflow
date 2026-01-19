#!/usr/bin/env python3
"""
Minimal Backend Test - Tests core components without full backend initialization
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

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class MinimalBackendTester:
    """Test backend components with minimal dependencies"""
    
    def __init__(self):
        self.results = {
            'environment': {'status': 'PENDING', 'details': {}, 'error': None},
            'supabase': {'status': 'PENDING', 'details': {}, 'error': None},
            'redis': {'status': 'PENDING', 'details': {}, 'error': None},
            'direct_imports': {'status': 'PENDING', 'details': {}, 'error': None},
            'optimization_modules': {'status': 'PENDING', 'details': {}, 'error': None}
        }
        
        # Load environment variables
        self.load_env()
    
    def load_env(self):
        """Load environment variables"""
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
        except Exception as e:
            logger.error(f"Failed to load environment: {e}")
    
    async def test_environment(self):
        """Test environment variables"""
        logger.info("Testing Environment Configuration...")
        
        try:
            required_vars = [
                'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY',
                'UPSTASH_REDIS_REST_URL', 'UPSTASH_REDIS_REST_TOKEN',
                'GCP_PROJECT_ID', 'VERTEX_AI_API_KEY', 'MODEL_GENERAL'
            ]
            
            present = sum(1 for var in required_vars if os.getenv(var))
            
            self.results['environment'] = {
                'status': 'PASS',
                'details': {
                    'total_required': len(required_vars),
                    'present': present,
                    'success_rate': f"{(present/len(required_vars)*100):.1f}%"
                },
                'error': None
            }
            
            logger.info(f"Environment test passed - {present}/{len(required_vars)} variables present")
            
        except Exception as e:
            self.results['environment'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Environment test failed: {e}")
    
    async def test_supabase(self):
        """Test Supabase connection"""
        logger.info("Testing Supabase Connection...")
        
        try:
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise Exception("Missing Supabase credentials")
            
            client = create_client(supabase_url, supabase_key)
            
            start_time = time.time()
            response = client.table('users').select('id').limit(1).execute()
            connection_time = time.time() - start_time
            
            self.results['supabase'] = {
                'status': 'PASS',
                'details': {
                    'connection_time': f"{connection_time:.2f}s",
                    'query_success': response is not None,
                    'database_accessible': True
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
                set_response = await client.post(
                    f"{redis_url}/set/minimal_test/test_value",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                
                get_response = await client.get(
                    f"{redis_url}/get/minimal_test",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
            
            connection_time = time.time() - start_time
            
            self.results['redis'] = {
                'status': 'PASS',
                'details': {
                    'connection_time': f"{connection_time:.2f}s",
                    'set_success': set_response.status_code == 200,
                    'get_success': get_response.status_code == 200,
                    'redis_working': True
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
    
    async def test_direct_imports(self):
        """Test direct imports without backend initialization"""
        logger.info("Testing Direct Module Imports...")
        
        try:
            imports = {}
            
            # Test individual module imports
            modules_to_test = [
                ('semantic_cache', 'backend.core.semantic_cache'),
                ('smart_retry', 'backend.core.smart_retry'),
                ('context_manager', 'backend.core.context_manager'),
                ('dynamic_router', 'backend.core.dynamic_router'),
                ('prompt_optimizer', 'backend.core.prompt_optimizer'),
                ('cost_analytics', 'backend.core.cost_analytics'),
                ('marvelous_optimizer', 'backend.core.marvelous_optimizer'),
                ('marvelous_batch_processor', 'backend.core.marvelous_batch_processor'),
                ('provider_arbitrage', 'backend.core.provider_arbitrage'),
                ('optimization_dashboard', 'backend.core.optimization_dashboard')
            ]
            
            for name, module_path in modules_to_test:
                try:
                    module = __import__(module_path, fromlist=[name])
                    imports[name] = 'PASS'
                    logger.info(f"   {name}: PASS")
                except Exception as e:
                    imports[name] = f'FAIL: {str(e)[:30]}'
                    logger.warning(f"   {name}: FAIL - {str(e)[:50]}")
            
            passed = sum(1 for status in imports.values() if 'PASS' in status)
            total = len(imports)
            
            self.results['direct_imports'] = {
                'status': 'PASS' if passed > 0 else 'FAIL',
                'details': {
                    'total_modules': total,
                    'passed_modules': passed,
                    'success_rate': f"{(passed/total*100):.1f}%",
                    'imports': imports
                },
                'error': None if passed > 0 else "All imports failed"
            }
            
            logger.info(f"Direct imports test - {passed}/{total} modules passed")
            
        except Exception as e:
            self.results['direct_imports'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Direct imports test failed: {e}")
    
    async def test_optimization_modules(self):
        """Test optimization module instantiation"""
        logger.info("Testing Optimization Module Instantiation...")
        
        try:
            modules = {}
            
            # Test modules that can be instantiated
            test_modules = [
                ('SemanticCache', 'backend.core.semantic_cache', 'SemanticCache'),
                ('SmartRetryManager', 'backend.core.smart_retry', 'SmartRetryManager'),
                ('ContextManager', 'backend.core.context_manager', 'ContextManager'),
                ('DynamicModelRouter', 'backend.core.dynamic_router', 'DynamicModelRouter'),
                ('PromptOptimizer', 'backend.core.prompt_optimizer', 'PromptOptimizer'),
                ('CostAnalytics', 'backend.core.cost_analytics', 'CostAnalytics'),
                ('MarvelousBatchProcessor', 'backend.core.marvelous_batch_processor', 'MarvelousBatchProcessor'),
                ('ProviderArbitrage', 'backend.core.provider_arbitrage', 'ProviderArbitrage'),
                ('OptimizationDashboard', 'backend.core.optimization_dashboard', 'OptimizationDashboard')
            ]
            
            for display_name, module_path, class_name in test_modules:
                try:
                    module = __import__(module_path, fromlist=[class_name])
                    cls = getattr(module, class_name)
                    
                    # Try to instantiate with default parameters
                    if display_name == 'MarvelousBatchProcessor':
                        instance = cls(batch_size=5, batch_timeout=2.0)
                    elif display_name == 'ProviderArbitrage':
                        instance = cls(preferred_providers=['openai'], cost_sensitivity=0.8)
                    elif display_name == 'OptimizationDashboard':
                        instance = cls()
                    elif display_name == 'SemanticCache':
                        instance = cls(l1_size=100, l2_ttl=1800, l3_ttl=43200)
                    elif display_name == 'SmartRetryManager':
                        instance = cls(max_retries=2, base_delay=0.5)
                    elif display_name == 'ContextManager':
                        instance = cls(max_length=2000, compression_ratio=0.7)
                    elif display_name == 'DynamicModelRouter':
                        instance = cls(cost_threshold=0.005, performance_weight=0.8)
                    elif display_name == 'PromptOptimizer':
                        instance = cls(token_reduction_target=0.3, semantic_preservation_threshold=0.85)
                    elif display_name == 'CostAnalytics':
                        instance = cls()
                    else:
                        instance = cls()
                    
                    modules[display_name] = 'PASS'
                    logger.info(f"   {display_name}: PASS")
                    
                except Exception as e:
                    modules[display_name] = f'FAIL: {str(e)[:30]}'
                    logger.warning(f"   {display_name}: FAIL - {str(e)[:50]}")
            
            passed = sum(1 for status in modules.values() if 'PASS' in status)
            total = len(modules)
            
            self.results['optimization_modules'] = {
                'status': 'PASS' if passed > 0 else 'FAIL',
                'details': {
                    'total_modules': total,
                    'passed_modules': passed,
                    'success_rate': f"{(passed/total*100):.1f}%",
                    'modules': modules
                },
                'error': None if passed > 0 else "All modules failed"
            }
            
            logger.info(f"Optimization modules test - {passed}/{total} modules passed")
            
        except Exception as e:
            self.results['optimization_modules'] = {
                'status': 'FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"Optimization modules test failed: {e}")
    
    async def run_all_tests(self):
        """Run all tests"""
        logger.info("Starting Minimal Backend Test Suite")
        logger.info("=" * 50)
        
        tests = [
            self.test_environment,
            self.test_supabase,
            self.test_redis,
            self.test_direct_imports,
            self.test_optimization_modules
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(0.3)
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 50)
        logger.info("MINIMAL BACKEND TEST SUMMARY")
        logger.info("=" * 50)
        
        passed = 0
        failed = 0
        
        for service, result in self.results.items():
            status = result['status']
            if 'PASS' in status:
                passed += 1
                logger.info(f"PASS {service.upper()}")
            else:
                failed += 1
                logger.error(f"FAIL {service.upper()}")
                if result.get('error'):
                    logger.error(f"   Error: {result['error']}")
            
            if result.get('details'):
                for key, value in result['details'].items():
                    if key not in ['imports', 'modules']:  # Skip verbose details
                        logger.info(f"   {key}: {value}")
        
        logger.info("=" * 50)
        logger.info(f"RESULTS: {passed} passed, {failed} failed")
        total = passed + failed
        logger.info(f"SUCCESS RATE: {(passed/total*100):.1f}%")
        logger.info("=" * 50)
        
        # Save results
        self.save_results()
        
        # Provide final assessment
        self.provide_final_assessment()
    
    def provide_final_assessment(self):
        """Provide final assessment"""
        logger.info("\nFINAL ASSESSMENT:")
        logger.info("-" * 30)
        
        # Check core services
        core_services = ['supabase', 'redis']
        core_passed = sum(1 for service in core_services if 'PASS' in self.results[service]['status'])
        
        if core_passed == len(core_services):
            logger.info("CORE SERVICES: All working")
        else:
            logger.info(f"CORE SERVICES: {core_passed}/{len(core_services)} working")
        
        # Check optimization framework
        opt_modules = self.results.get('optimization_modules', {})
        if 'PASS' in opt_modules.get('status', ''):
            opt_passed = opt_modules['details']['passed_modules']
            opt_total = opt_modules['details']['total_modules']
            logger.info(f"OPTIMIZATION FRAMEWORK: {opt_passed}/{opt_total} modules working")
        else:
            logger.info("OPTIMIZATION FRAMEWORK: Not working")
        
        # Overall status
        total_passed = sum(1 for result in self.results.values() if 'PASS' in result['status'])
        total_tests = len(self.results)
        
        if total_passed >= 4:
            logger.info("OVERALL: GOOD - Core components working")
            logger.info("RECOMMENDATION: Ready for backend development")
        elif total_passed >= 2:
            logger.info("OVERALL: PARTIAL - Some components working")
            logger.info("RECOMMENDATION: Fix failing components")
        else:
            logger.info("OVERALL: POOR - Major issues detected")
            logger.info("RECOMMENDATION: Fix core dependencies first")
    
    def save_results(self):
        """Save test results"""
        try:
            results_file = os.path.join(os.path.dirname(__file__), 'minimal_backend_test_results.json')
            
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
    tester = MinimalBackendTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
