#!/usr/bin/env python3
"""
Final Dependency Check for Raptorflow
Clean test without unicode characters to avoid encoding issues
"""

import os
import sys
import asyncio
import json
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

class FinalDependencyChecker:
    """Final dependency status checker"""
    
    def __init__(self):
        self.status = {
            'environment': 'UNKNOWN',
            'supabase': 'UNKNOWN', 
            'redis': 'UNKNOWN',
            'optimization_framework': 'UNKNOWN',
            'overall': 'UNKNOWN'
        }
        
        # Load environment
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
                print("Environment variables loaded")
        except Exception as e:
            print(f"Failed to load environment: {e}")
    
    async def check_environment(self):
        """Check environment variables"""
        print("Checking Environment Variables...")
        
        required_vars = [
            'SUPABASE_URL', 'SUPABASE_SERVICE_ROLE_KEY',
            'UPSTASH_REDIS_REST_URL', 'UPSTASH_REDIS_REST_TOKEN',
            'GCP_PROJECT_ID', 'VERTEX_AI_API_KEY', 'MODEL_GENERAL'
        ]
        
        present = sum(1 for var in required_vars if os.getenv(var))
        
        if present == len(required_vars):
            self.status['environment'] = 'WORKING'
            print(f"Environment: WORKING ({present}/{len(required_vars)} variables)")
        else:
            self.status['environment'] = 'PARTIAL'
            print(f"Environment: PARTIAL ({present}/{len(required_vars)} variables)")
            print(f"Missing: {[var for var in required_vars if not os.getenv(var)]}")
    
    async def check_supabase(self):
        """Check Supabase connection"""
        print("Checking Supabase...")
        
        try:
            from supabase import create_client
            
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                self.status['supabase'] = 'FAIL - Missing credentials'
                return
            
            client = create_client(supabase_url, supabase_key)
            
            start_time = time.time()
            response = client.table('users').select('id').limit(1).execute()
            connection_time = time.time() - start_time
            
            if response:
                self.status['supabase'] = f'WORKING (Connection time: {connection_time:.2f}s)'
                print(f"Supabase: WORKING (Connection time: {connection_time:.2f}s)")
            else:
                self.status['supabase'] = 'FAIL - Query failed'
                print("Supabase: FAIL - Query failed")
                
        except Exception as e:
            self.status['supabase'] = f'FAIL - {str(e)[:50]}'
            print(f"Supabase: FAIL - {str(e)[:50]}")
    
    async def check_redis(self):
        """Check Redis connection"""
        print("Checking Redis...")
        
        try:
            import httpx
            
            redis_url = os.getenv('UPSTASH_REDIS_REST_URL')
            redis_token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
            print(f"DEBUG: Using URL: {redis_url}")
            print(f"DEBUG: Using Token: [{redis_token}]")
            
            if not redis_url or not redis_token:
                self.status['redis'] = 'FAIL - Missing credentials'
                return
            
            start_time = time.time()
            
            async with httpx.AsyncClient() as client:
                set_response = await client.post(
                    f"{redis_url}/set/final_check/test_value",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                print(f"DEBUG: Redis SET status: {set_response.status_code}")
                print(f"DEBUG: Redis SET body: {set_response.text}")
                
                get_response = await client.get(
                    f"{redis_url}/get/final_check",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                print(f"DEBUG: Redis GET status: {get_response.status_code}")
                print(f"DEBUG: Redis GET body: {get_response.text}")
            
            connection_time = time.time() - start_time
            
            if set_response.status_code == 200 and get_response.status_code == 200:
                self.status['redis'] = f'WORKING (Connection time: {connection_time:.2f}s)'
                print(f"Redis: WORKING (Connection time: {connection_time:.2f}s)")
            else:
                self.status['redis'] = 'FAIL - API error'
                print("Redis: FAIL - API error")
                
        except Exception as e:
            self.status['redis'] = f'FAIL - {str(e)[:50]}'
            print(f"Redis: FAIL - {str(e)[:50]}")
    
    async def check_optimization_framework(self):
        """Check optimization framework"""
        print("Checking Optimization Framework...")
        
        try:
            # Test imports without instantiation to avoid backend initialization
            modules_to_test = [
                'backend.core.semantic_cache',
                'backend.core.smart_retry', 
                'backend.core.context_manager',
                'backend.core.dynamic_router',
                'backend.core.prompt_optimizer',
                'backend.core.cost_analytics',
                'backend.core.marvelous_optimizer',
                'backend.core.marvelous_batch_processor',
                'backend.core.provider_arbitrage',
                'backend.core.optimization_dashboard'
            ]
            
            working_modules = []
            failed_modules = []
            
            for module_path in modules_to_test:
                try:
                    __import__(module_path)
                    working_modules.append(module_path.split('.')[-1])
                except Exception as e:
                    failed_modules.append(f"{module_path.split('.')[-1]}: {str(e)[:30]}")
            
            if working_modules:
                self.status['optimization_framework'] = f'WORKING ({len(working_modules)}/{len(modules_to_test)} modules)'
                print(f"Optimization Framework: WORKING ({len(working_modules)}/{len(modules_to_test)} modules)")
                print(f"Working: {', '.join(working_modules)}")
                if failed_modules:
                    print(f"Failed: {len(failed_modules)} modules")
            else:
                self.status['optimization_framework'] = f'FAIL - All modules failed'
                print("Optimization Framework: FAIL - All modules failed")
                print(f"Errors: {failed_modules[:3]}")
                
        except Exception as e:
            self.status['optimization_framework'] = f'FAIL - {str(e)[:50]}'
            print(f"Optimization Framework: FAIL - {str(e)[:50]}")
    
    def calculate_overall_status(self):
        """Calculate overall status"""
        working_count = 0
        total_count = 0
        
        for key, status in self.status.items():
            if key == 'overall':
                continue
            total_count += 1
            if 'WORKING' in status:
                working_count += 1
        
        if working_count == total_count:
            self.status['overall'] = 'EXCELLENT - All components working'
        elif working_count >= 3:
            self.status['overall'] = 'GOOD - Most components working'
        elif working_count >= 2:
            self.status['overall'] = 'PARTIAL - Some components working'
        else:
            self.status['overall'] = 'POOR - Major issues'
    
    async def run_checks(self):
        """Run all dependency checks"""
        print("=" * 60)
        print("RAPTORFLOW DEPENDENCY STATUS CHECK")
        print("=" * 60)
        
        await self.check_environment()
        await self.check_supabase()
        await self.check_redis()
        await self.check_optimization_framework()
        
        self.calculate_overall_status()
        
        print("\n" + "=" * 60)
        print("FINAL STATUS SUMMARY")
        print("=" * 60)
        
        for key, status in self.status.items():
            print(f"{key.upper()}: {status}")
        
        print("\n" + "=" * 60)
        print("RECOMMENDATIONS")
        print("=" * 60)
        
        # Provide specific recommendations
        if 'FAIL' in self.status.get('supabase', ''):
            print("- Check Supabase URL and service role key")
            print("- Verify database is online and accessible")
        
        if 'FAIL' in self.status.get('redis', ''):
            print("- Check Upstash Redis URL and token")
            print("- Verify Redis service status")
        
        if 'FAIL' in self.status.get('optimization_framework', ''):
            print("- Install missing packages: pip install scikit-learn tiktoken")
            print("- Check Python path and backend module structure")
            print("- Fix any import errors in optimization modules")
        
        if self.status.get('environment') == 'PARTIAL':
            print("- Add missing environment variables to .env file")
        
        print("\nNEXT STEPS:")
        if self.status.get('overall', '').startswith('EXCELLENT'):
            print("- System is ready for development")
            print("- Test with actual inference requests")
        elif self.status.get('overall', '').startswith('GOOD'):
            print("- Fix any failing components")
            print("- Test with actual requests after fixes")
        else:
            print("- Fix core dependencies first (Supabase, Redis)")
            print("- Install missing Python packages")
            print("- Verify environment configuration")
        
        # Save results
        self.save_results()
    
    def save_results(self):
        """Save results to file"""
        try:
            results_file = os.path.join(os.path.dirname(__file__), 'dependency_status.json')
            
            with open(results_file, 'w') as f:
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'status': self.status
                }, f, indent=2)
            
            print(f"\nResults saved to: {results_file}")
            
        except Exception as e:
            print(f"Failed to save results: {e}")

async def main():
    """Main function"""
    checker = FinalDependencyChecker()
    await checker.run_checks()

if __name__ == "__main__":
    asyncio.run(main())
