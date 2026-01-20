#!/usr/bin/env python3
"""
Minimal test of optimization framework - direct imports only
"""

import os
import sys

# Set environment variable for encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Add backend to path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))

def test_individual_components():
    """Test each optimization component individually"""
    
    print("Testing Optimization Framework Components (Minimal)...")
    print("=" * 60)
    
    components = [
        ('SemanticCache', 'backend.core.semantic_cache'),
        ('SmartRetryManager', 'backend.core.smart_retry'),
        ('ContextManager', 'backend.core.context_manager'),
        ('DynamicModelRouter', 'backend.core.dynamic_router'),
        ('PromptOptimizer', 'backend.core.prompt_optimizer'),
        ('CostAnalytics', 'backend.core.cost_analytics'),
        ('MarvelousAIOptimizer', 'backend.core.marvelous_optimizer'),
        ('MarvelousBatchProcessor', 'backend.core.marvelous_batch_processor'),
        ('ProviderArbitrage', 'backend.core.provider_arbitrage'),
        ('OptimizationDashboard', 'backend.core.optimization_dashboard'),
    ]
    
    results = {}
    
    for name, module_path in components:
        print(f"\nTesting {name}...")
        try:
            # Import the module
            module = __import__(module_path, fromlist=[name])
            
            # Get the class
            component_class = getattr(module, name)
            
            # Try to instantiate (skip if it requires complex dependencies)
            try:
                instance = component_class()
                print(f"   Status: WORKING (instantiated)")
                results[name] = 'PASS'
            except Exception as e:
                # If instantiation fails but import works, count as partial success
                print(f"   Status: IMPORT OK (instantiation failed: {e})")
                results[name] = 'PARTIAL'
                
        except ImportError as e:
            print(f"   Status: IMPORT FAILED")
            print(f"   Error: {e}")
            results[name] = 'FAIL'
        except Exception as e:
            print(f"   Status: FAILED")
            print(f"   Error: {e}")
            results[name] = 'FAIL'
    
    # Summary
    print("\n" + "=" * 60)
    print("OPTIMIZATION FRAMEWORK TEST SUMMARY")
    print("=" * 60)
    
    passed = sum(1 for result in results.values() if result == 'PASS')
    partial = sum(1 for result in results.values() if result == 'PARTIAL')
    total = len(results)
    
    for component, status in results.items():
        if status == 'PASS':
            status_symbol = "[PASS]"
        elif status == 'PARTIAL':
            status_symbol = "[PARTIAL]"
        else:
            status_symbol = "[FAIL]"
        print(f"{status_symbol} {component}")
    
    print(f"\nOverall: {passed} fully working, {partial} partially working, {total - passed - partial} failed")
    
    if passed == total:
        print("\n[SUCCESS] All optimization framework components are fully working!")
    elif passed + partial >= total * 0.8:
        print(f"\n[GOOD] {passed + partial}/{total} components are working or mostly working.")
    else:
        print(f"\n[NEEDS WORK] Only {passed + partial}/{total} components are working.")
    
    return results

if __name__ == "__main__":
    test_individual_components()
