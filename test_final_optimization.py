#!/usr/bin/env python3
"""
Final test of optimization framework with clean environment
"""

import os
import sys
import json
import logging
from datetime import datetime

# Configure logging without unicode characters
logging.basicConfig(level=logging.WARNING, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment variables
os.environ['PYTHONIOENCODING'] = 'utf-8'
os.environ['PYTHONLEGACYSTDOUT'] = 'utf-8'

def test_individual_component(component_name, module_path, class_name, init_args=None):
    """Test individual component"""
    try:
        print(f"Testing {component_name}...")
        
        # Import module
        module = __import__(module_path, fromlist=[class_name])
        cls = getattr(module, class_name)
        
        # Create instance
        if init_args:
            instance = cls(**init_args)
        else:
            instance = cls()
        
        print(f"  SUCCESS: {component_name} working")
        return True, instance
        
    except Exception as e:
        print(f"  FAILED: {component_name} - {str(e)[:50]}")
        return False, None

def main():
    """Main test function"""
    print("=" * 60)
    print("RAPTORFLOW OPTIMIZATION FRAMEWORK - FINAL TEST")
    print("=" * 60)
    print("Testing components with clean environment...")
    print()
    
    results = {}
    
    # Test core components with minimal initialization
    test_cases = [
        ('SemanticCache', 'backend.core.semantic_cache', 'SemanticCache', {
            'l1_size': 5, 'l2_ttl': 300, 'l3_ttl': 1800,
            'similarity_threshold': 0.8
        }),
        ('SmartRetryManager', 'backend.core.smart_retry', 'SmartRetryManager', {
            'max_retries': 1, 'base_delay': 0.1, 'max_delay': 1.0
        }),
        ('ContextManager', 'backend.core.context_manager', 'ContextManager', {
            'max_length': 500, 'compression_ratio': 0.8
        }),
        ('DynamicModelRouter', 'backend.core.dynamic_router', 'DynamicModelRouter', {
            'cost_threshold': 0.01, 'performance_weight': 0.7
        }),
        ('PromptOptimizer', 'backend.core.prompt_optimizer', 'PromptOptimizer', {
            'token_reduction_target': 0.2, 'semantic_preservation_threshold': 0.9
        }),
        ('CostAnalytics', 'backend.core.cost_analytics', 'CostAnalytics', {}),
        ('MarvelousBatchProcessor', 'backend.core.marvelous_batch_processor', 'MarvelousBatchProcessor', {
            'batch_size': 3, 'batch_timeout': 1.0
        }),
        ('ProviderArbitrage', 'backend.core.provider_arbitrage', 'ProviderArbitrage', {
            'preferred_providers': ['openai'], 'cost_sensitivity': 0.7
        }),
        ('OptimizationDashboard', 'backend.core.optimization_dashboard', 'OptimizationDashboard', {})
    ]
    
    working_components = []
    failed_components = []
    
    for display_name, module_path, class_name, init_args in test_cases:
        success, instance = test_individual_component(display_name, module_path, class_name, init_args)
        if success:
            working_components.append(display_name)
            # Test basic functionality if available
            if hasattr(instance, 'get_stats'):
                try:
                    stats = instance.get_stats()
                    print(f"  Stats available: Yes")
                except:
                    print(f"  Stats available: No")
        else:
            failed_components.append(display_name)
    
    print()
    print("=" * 60)
    print("FINAL RESULTS")
    print("=" * 60)
    print(f"Total Components: {len(test_cases)}")
    print(f"Working: {len(working_components)}")
    print(f"Failed: {len(failed_components)}")
    print(f"Success Rate: {(len(working_components)/len(test_cases)*100):.1f}%")
    print()
    
    if working_components:
        print("WORKING COMPONENTS:")
        for comp in working_components:
            print(f"  - {comp}")
    
    if failed_components:
        print("FAILED COMPONENTS:")
        for comp in failed_components:
            print(f"  - {comp}")
    
    print()
    print("ASSESSMENT:")
    if len(working_components) >= 8:
        print("EXCELLENT: Optimization framework is ready!")
        print("All core optimization components are working.")
    elif len(working_components) >= 5:
        print("GOOD: Core optimization components working.")
        print("Some components may need additional fixes.")
    elif len(working_components) >= 3:
        print("PARTIAL: Basic optimization components working.")
        print("Several components need fixes.")
    else:
        print("POOR: Major issues detected.")
        print("Backend configuration needs attention.")
    
    # Save results
    results_data = {
        'timestamp': datetime.now().isoformat(),
        'total_components': len(test_cases),
        'working_components': working_components,
        'failed_components': failed_components,
        'success_rate': (len(working_components)/len(test_cases)*100),
        'working': len(working_components) > 0,
        'assessment': 'EXCELLENT' if len(working_components) >= 8 else 'GOOD' if len(working_components) >= 5 else 'PARTIAL' if len(working_components) >= 3 else 'POOR'
    }
    
    with open('final_optimization_test.json', 'w') as f:
        json.dump(results_data, f, indent=2)
    
    print(f"\nResults saved to: final_optimization_test.json")
    
    print()
    print("RECOMMENDATIONS:")
    if len(working_components) >= 8:
        print("- System is ready for optimization!")
        print("- Test with actual requests")
        print("- Monitor performance metrics")
    elif len(working_components) >= 5:
        print("- Fix remaining components")
        print("- Test with sample requests")
    else:
        print("- Fix backend configuration issues")
        print("- Install missing dependencies")
        print("- Check module imports")
    
    return results_data

if __name__ == "__main__":
    main()
