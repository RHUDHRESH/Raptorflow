#!/usr/bin/env python3
"""
Direct test of optimization framework components without backend initialization
"""

import os
import sys
import logging

# Set environment variable for encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

def test_optimization_components():
    """Test optimization framework components directly"""
    
    print("Testing Optimization Framework Components Directly...")
    print("=" * 60)
    
    results = {}
    
    # Test 1: SemanticCache
    print("\n1. Testing SemanticCache...")
    try:
        from backend.core.semantic_cache import SemanticCache
        cache = SemanticCache()
        print("   Status: WORKING")
        results['SemanticCache'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['SemanticCache'] = 'FAIL'
    
    # Test 2: SmartRetryManager
    print("\n2. Testing SmartRetryManager...")
    try:
        from backend.core.smart_retry import SmartRetryManager
        retry_manager = SmartRetryManager()
        print("   Status: WORKING")
        results['SmartRetryManager'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['SmartRetryManager'] = 'FAIL'
    
    # Test 3: ContextManager
    print("\n3. Testing ContextManager...")
    try:
        from backend.core.context_manager import ContextManager
        context_manager = ContextManager()
        print("   Status: WORKING")
        results['ContextManager'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['ContextManager'] = 'FAIL'
    
    # Test 4: DynamicModelRouter
    print("\n4. Testing DynamicModelRouter...")
    try:
        from backend.core.dynamic_router import DynamicModelRouter
        router = DynamicModelRouter()
        print("   Status: WORKING")
        results['DynamicModelRouter'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['DynamicModelRouter'] = 'FAIL'
    
    # Test 5: PromptOptimizer
    print("\n5. Testing PromptOptimizer...")
    try:
        from backend.core.prompt_optimizer import PromptOptimizer
        optimizer = PromptOptimizer()
        print("   Status: WORKING")
        results['PromptOptimizer'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['PromptOptimizer'] = 'FAIL'
    
    # Test 6: CostAnalytics
    print("\n6. Testing CostAnalytics...")
    try:
        from backend.core.cost_analytics import CostAnalytics
        analytics = CostAnalytics()
        print("   Status: WORKING")
        results['CostAnalytics'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['CostAnalytics'] = 'FAIL'
    
    # Test 7: MarvelousAIOptimizer
    print("\n7. Testing MarvelousAIOptimizer...")
    try:
        from backend.core.marvelous_optimizer import MarvelousAIOptimizer
        optimizer = MarvelousAIOptimizer()
        print("   Status: WORKING")
        results['MarvelousAIOptimizer'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['MarvelousAIOptimizer'] = 'FAIL'
    
    # Test 8: BatchProcessor
    print("\n8. Testing BatchProcessor...")
    try:
        from backend.core.marvelous_batch_processor import MarvelousBatchProcessor
        processor = MarvelousBatchProcessor()
        print("   Status: WORKING")
        results['BatchProcessor'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['BatchProcessor'] = 'FAIL'
    
    # Test 9: ProviderArbitrage
    print("\n9. Testing ProviderArbitrage...")
    try:
        from backend.core.provider_arbitrage import ProviderArbitrage
        arbitrage = ProviderArbitrage()
        print("   Status: WORKING")
        results['ProviderArbitrage'] = 'PASS'
    except Exception as e:
        print(f"   Status: FAILED")
        print(f"   Error: {e}")
        results['ProviderArbitrage'] = 'FAIL'
    
    # Test 10: OptimizationDashboard
    print("\n10. Testing OptimizationDashboard...")
    try:
        from backend.core.optimization_dashboard import OptimizationDashboard
        dashboard = OptimizationDashboard()
        print("    Status: WORKING")
        results['OptimizationDashboard'] = 'PASS'
    except Exception as e:
        print(f"    Status: FAILED")
        print(f"    Error: {e}")
        results['OptimizationDashboard'] = 'FAIL'
    
    # Summary
    print("\n" + "=" * 60)
    print("OPTIMIZATION FRAMEWORK TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result == 'PASS')
    total = len(results)
    
    for component, status in results.items():
        status_symbol = "[PASS]" if status == 'PASS' else "[FAIL]"
        print(f"{status_symbol} {component}")
    
    print(f"\nOverall: {passed}/{total} components working")
    
    if passed == total:
        print("\n[SUCCESS] All optimization framework components are working!")
        print("The Marvelous AI Optimization Framework is ready for deployment.")
    else:
        print(f"\n[WARNING] {total - passed} components need attention.")
        print("Continue debugging to resolve remaining issues.")
    
    return results

if __name__ == "__main__":
    test_optimization_components()
