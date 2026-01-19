#!/usr/bin/env python3
"""
Raptorflow Core Dependencies Test Script
Tests all external services and core dependencies for proper initialization
"""

import os
import sys
import asyncio
import json
import time
import logging
from datetime import datetime
from typing import Dict, Any, List
import traceback

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class CoreDependenciesTester:
    """Test all core dependencies and external services"""
    
    def __init__(self):
        self.results = {
            'supabase': {'status': 'pending', 'details': {}, 'error': None},
            'redis': {'status': 'pending', 'details': {}, 'error': None},
            'google_cloud': {'status': 'pending', 'details': {}, 'error': None},
            'vertex_ai': {'status': 'pending', 'details': {}, 'error': None},
            'phonepe': {'status': 'pending', 'details': {}, 'error': None},
            'email_service': {'status': 'pending', 'details': {}, 'error': None},
            'storage': {'status': 'pending', 'details': {}, 'error': None},
            'inference': {'status': 'pending', 'details': {}, 'error': None}
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
    
    async def test_supabase(self):
        """Test Supabase connection and storage"""
        logger.info("🧪 Testing Supabase...")
        
        try:
            # Test basic imports
            from supabase import create_client, Client
            
            # Get credentials
            supabase_url = os.getenv('SUPABASE_URL')
            supabase_key = os.getenv('SUPABASE_SERVICE_ROLE_KEY')
            
            if not supabase_url or not supabase_key:
                raise Exception("Missing Supabase credentials")
            
            # Test connection
            supabase: Client = create_client(supabase_url, supabase_key)
            
            # Test basic query
            start_time = time.time()
            response = supabase.table('users').select('count').execute()
            connection_time = time.time() - start_time
            
            # Test storage
            storage_response = supabase.storage.list_buckets()
            
            self.results['supabase'] = {
                'status': '✅ PASS',
                'details': {
                    'url': supabase_url,
                    'connection_time': f"{connection_time:.2f}s",
                    'query_success': response is not None,
                    'storage_buckets': len(storage_response.data) if storage_response.data else 0,
                    'api_version': 'v1'
                },
                'error': None
            }
            
            logger.info("✅ Supabase test passed")
            
        except Exception as e:
            self.results['supabase'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Supabase test failed: {e}")
    
    async def test_redis(self):
        """Test Redis connection"""
        logger.info("🧪 Testing Redis...")
        
        try:
            # Test Upstash Redis
            redis_url = os.getenv('UPSTASH_REDIS_REST_URL')
            redis_token = os.getenv('UPSTASH_REDIS_REST_TOKEN')
            
            if not redis_url or not redis_token:
                raise Exception("Missing Redis credentials")
            
            # Test basic Redis operations
            import httpx
            
            start_time = time.time()
            
            # Test SET operation
            async with httpx.AsyncClient() as client:
                # Set a test key
                set_response = await client.post(
                    f"{redis_url}/set/test_key/raptorflow_test_value",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                
                # Get the test key
                get_response = await client.get(
                    f"{redis_url}/get/test_key",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
                
                # Delete the test key
                del_response = await client.delete(
                    f"{redis_url}/del/test_key",
                    headers={"Authorization": f"Bearer {redis_token}"}
                )
            
            connection_time = time.time() - start_time
            
            self.results['redis'] = {
                'status': '✅ PASS',
                'details': {
                    'url': redis_url,
                    'connection_time': f"{connection_time:.2f}s",
                    'set_success': set_response.status_code == 200,
                    'get_success': get_response.status_code == 200,
                    'del_success': del_response.status_code == 200,
                    'test_value': get_response.json().get('result', 'N/A')
                },
                'error': None
            }
            
            logger.info("✅ Redis test passed")
            
        except Exception as e:
            self.results['redis'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Redis test failed: {e}")
    
    async def test_google_cloud(self):
        """Test Google Cloud Storage and credentials"""
        logger.info("🧪 Testing Google Cloud...")
        
        try:
            from google.cloud import storage
            from google.oauth2 import service_account
            
            # Get credentials path
            credentials_path = os.getenv('GOOGLE_APPLICATION_CREDENTIALS')
            project_id = os.getenv('GCP_PROJECT_ID')
            
            if not credentials_path or not project_id:
                raise Exception("Missing Google Cloud credentials")
            
            # Test storage client
            storage_client = storage.Client(project=project_id)
            
            # List buckets
            start_time = time.time()
            buckets = list(storage_client.list_buckets())
            connection_time = time.time() - start_time
            
            # Test specific buckets
            bucket_names = [
                'raptorflow-ingest-raw-481505',
                'raptorflow-gold-zone-481505',
                'raptorflow-model-registry-481505'
            ]
            
            existing_buckets = [bucket.name for bucket in buckets]
            found_buckets = [name for name in bucket_names if name in existing_buckets]
            
            self.results['google_cloud'] = {
                'status': '✅ PASS',
                'details': {
                    'project_id': project_id,
                    'credentials_path': credentials_path,
                    'connection_time': f"{connection_time:.2f}s",
                    'total_buckets': len(buckets),
                    'expected_buckets': len(bucket_names),
                    'found_buckets': found_buckets,
                    'bucket_list': existing_buckets[:5]  # Show first 5
                },
                'error': None
            }
            
            logger.info("✅ Google Cloud test passed")
            
        except Exception as e:
            self.results['google_cloud'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Google Cloud test failed: {e}")
    
    async def test_vertex_ai(self):
        """Test Vertex AI connection"""
        logger.info("🧪 Testing Vertex AI...")
        
        try:
            import httpx
            
            # Get API key
            api_key = os.getenv('VERTEX_AI_API_KEY')
            project_id = os.getenv('VERTEX_AI_PROJECT_ID')
            
            if not api_key or not project_id:
                raise Exception("Missing Vertex AI credentials")
            
            # Test Vertex AI API
            url = f"https://generativelanguage.googleapis.com/v1beta/models"
            
            start_time = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{url}?key={api_key}",
                    timeout=10.0
                )
            
            connection_time = time.time() - start_time
            
            if response.status_code == 200:
                models = response.json()
                model_count = len(models.get('models', []))
                
                # Test specific model
                test_model = "gemini-2.0-flash-exp"
                model_url = f"https://generativelanguage.googleapis.com/v1beta/models/{test_model}:generateContent?key={api_key}"
                
                test_payload = {
                    "contents": [{
                        "parts": [{"text": "Hello, this is a test."}]
                    }]
                }
                
                async with httpx.AsyncClient() as client:
                    model_response = await client.post(
                        model_url,
                        json=test_payload,
                        timeout=10.0
                    )
                
                self.results['vertex_ai'] = {
                    'status': '✅ PASS',
                    'details': {
                        'project_id': project_id,
                        'connection_time': f"{connection_time:.2f}s",
                        'available_models': model_count,
                        'test_model': test_model,
                        'test_model_status': model_response.status_code,
                        'api_version': 'v1beta'
                    },
                    'error': None
                }
                
                logger.info("✅ Vertex AI test passed")
            else:
                raise Exception(f"API returned status {response.status_code}: {response.text}")
                
        except Exception as e:
            self.results['vertex_ai'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Vertex AI test failed: {e}")
    
    async def test_phonepe(self):
        """Test PhonePe payment gateway"""
        logger.info("🧪 Testing PhonePe...")
        
        try:
            import httpx
            
            # Get credentials
            client_id = os.getenv('PHONEPE_CLIENT_ID')
            client_secret = os.getenv('PHONEPE_CLIENT_SECRET')
            environment = os.getenv('PHONEPE_ENV', 'UAT')
            
            if not client_id or not client_secret:
                raise Exception("Missing PhonePe credentials")
            
            # Test PhonePe API endpoints
            if environment == 'UAT':
                base_url = "https://api-preprod.phonepe.com/apis/pg-sandbox"
            else:
                base_url = "https://api.phonepe.com/apis/pg"
            
            # Test OAuth token generation
            oauth_url = f"{base_url}/oauth/token"
            oauth_data = {
                "client_id": client_id,
                "client_version": "1",
                "grant_type": "client_credentials"
            }
            
            start_time = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    oauth_url,
                    json=oauth_data,
                    auth=(client_id, client_secret),
                    timeout=10.0
                )
            
            connection_time = time.time() - start_time
            
            if response.status_code in [200, 201]:
                token_data = response.json()
                
                self.results['phonepe'] = {
                    'status': '✅ PASS',
                    'details': {
                        'environment': environment,
                        'client_id': client_id,
                        'base_url': base_url,
                        'connection_time': f"{connection_time:.2f}s",
                        'oauth_status': response.status_code,
                        'token_received': 'access_token' in token_data
                    },
                    'error': None
                }
                
                logger.info("✅ PhonePe test passed")
            else:
                raise Exception(f"PhonePe API returned {response.status_code}: {response.text}")
                
        except Exception as e:
            self.results['phonepe'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ PhonePe test failed: {e}")
    
    async def test_email_service(self):
        """Test email service (Resend)"""
        logger.info("🧪 Testing Email Service...")
        
        try:
            import httpx
            
            # Get API key
            api_key = os.getenv('RESEND_API_KEY')
            from_email = os.getenv('RESEND_FROM_EMAIL')
            
            if not api_key:
                raise Exception("Missing Resend API key")
            
            # Test Resend API
            url = "https://api.resend.com/domains"
            
            start_time = time.time()
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    url,
                    headers={"Authorization": f"Bearer {api_key}"},
                    timeout=10.0
                )
            
            connection_time = time.time() - start_time
            
            if response.status_code == 200:
                domains = response.json()
                domain_count = len(domains.get('data', []))
                
                self.results['email_service'] = {
                    'status': '✅ PASS',
                    'details': {
                        'from_email': from_email,
                        'connection_time': f"{connection_time:.2f}s",
                        'api_status': response.status_code,
                        'verified_domains': domain_count,
                        'service': 'Resend'
                    },
                    'error': None
                }
                
                logger.info("✅ Email service test passed")
            else:
                raise Exception(f"Resend API returned {response.status_code}: {response.text}")
                
        except Exception as e:
            self.results['email_service'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Email service test failed: {e}")
    
    async def test_storage_operations(self):
        """Test storage operations"""
        logger.info("🧪 Testing Storage Operations...")
        
        try:
            from google.cloud import storage
            
            # Get credentials
            project_id = os.getenv('GCP_PROJECT_ID')
            
            if not project_id:
                raise Exception("Missing project ID")
            
            # Test storage operations
            storage_client = storage.Client(project=project_id)
            
            # Test bucket operations
            test_bucket_name = f"raptorflow-test-{int(time.time())}"
            
            try:
                # Create test bucket
                bucket = storage_client.create_bucket(test_bucket_name)
                
                # Upload test file
                blob = bucket.blob('test-file.txt')
                blob.upload_from_string('Raptorflow test content')
                
                # Download test file
                content = blob.download_as_text()
                
                # Delete test file and bucket
                blob.delete()
                bucket.delete()
                
                self.results['storage'] = {
                    'status': '✅ PASS',
                    'details': {
                        'project_id': project_id,
                        'test_bucket': test_bucket_name,
                        'upload_success': True,
                        'download_success': content == 'Raptorflow test content',
                        'cleanup_success': True
                    },
                    'error': None
                }
                
                logger.info("✅ Storage operations test passed")
                
            except Exception as e:
                # Try cleanup
                try:
                    bucket = storage_client.get_bucket(test_bucket_name)
                    bucket.delete()
                except:
                    pass
                raise e
                
        except Exception as e:
            self.results['storage'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Storage operations test failed: {e}")
    
    async def test_inference_system(self):
        """Test inference system"""
        logger.info("🧪 Testing Inference System...")
        
        try:
            # Test backend inference modules
            sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
            
            # Try to import inference modules
            from backend.core.inference_cache import get_inference_cache
            from backend.agents.base import BaseAgent
            
            # Test cache initialization
            cache = get_inference_cache()
            
            # Test basic agent creation
            test_agent = BaseAgent("test_agent", "Test agent for dependency checking")
            
            # Test inference configuration
            model = os.getenv('MODEL_GENERAL', 'gemini-2.0-flash-exp')
            provider = os.getenv('INFERENCE_PROVIDER', 'google')
            
            self.results['inference'] = {
                'status': '✅ PASS',
                'details': {
                    'model': model,
                    'provider': provider,
                    'cache_initialized': cache is not None,
                    'agent_initialized': test_agent is not None,
                    'inference_modules_loaded': True
                },
                'error': None
            }
            
            logger.info("✅ Inference system test passed")
            
        except Exception as e:
            self.results['inference'] = {
                'status': '❌ FAIL',
                'details': {},
                'error': str(e)
            }
            logger.error(f"❌ Inference system test failed: {e}")
    
    async def run_all_tests(self):
        """Run all dependency tests"""
        logger.info("🚀 Starting Core Dependencies Test Suite")
        logger.info("=" * 50)
        
        tests = [
            self.test_supabase,
            self.test_redis,
            self.test_google_cloud,
            self.test_vertex_ai,
            self.test_phonepe,
            self.test_email_service,
            self.test_storage_operations,
            self.test_inference_system
        ]
        
        for test in tests:
            try:
                await test()
                await asyncio.sleep(1)  # Brief pause between tests
            except Exception as e:
                logger.error(f"Test {test.__name__} crashed: {e}")
        
        self.print_summary()
    
    def print_summary(self):
        """Print test summary"""
        logger.info("\n" + "=" * 50)
        logger.info("📊 CORE DEPENDENCIES TEST SUMMARY")
        logger.info("=" * 50)
        
        passed = 0
        failed = 0
        
        for service, result in self.results.items():
            status = result['status']
            if '✅ PASS' in status:
                passed += 1
                logger.info(f"✅ {service.upper()}: {status}")
            else:
                failed += 1
                logger.error(f"❌ {service.upper()}: {status}")
                if result.get('error'):
                    logger.error(f"   Error: {result['error']}")
            
            if result.get('details'):
                for key, value in result['details'].items():
                    logger.info(f"   {key}: {value}")
        
        logger.info("=" * 50)
        logger.info(f"📈 RESULTS: {passed} passed, {failed} failed")
        logger.info(f"🎯 SUCCESS RATE: {(passed/(passed+failed)*100):.1f}%")
        logger.info("=" * 50)
        
        # Save results to file
        self.save_results()
    
    def save_results(self):
        """Save test results to file"""
        try:
            results_file = os.path.join(os.path.dirname(__file__), 'dependency_test_results.json')
            
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
    tester = CoreDependenciesTester()
    await tester.run_all_tests()

if __name__ == "__main__":
    asyncio.run(main())
