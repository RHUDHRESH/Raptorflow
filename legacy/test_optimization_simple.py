#!/usr/bin/env python3
"""
Simple test for optimization framework without unicode characters
"""

import os
import sys
import asyncio
import time

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment to prevent unicode issues
os.environ['PYTHONIOENCODING'] = 'utf-8'

def test_optimization_framework():
    """Test optimization framework components"""
    print("Testing Optimization Framework...")
    print("-" * 40)
    
    results = {}
    
    # Test components
    components = [
        ('SemanticCache', 'backend.core.semantic_cache', 'SemanticCache'),
        ('SmartRetryManager', 'backend.core.smart_retry', 'SmartRetryManager'),
        ('ContextManager', 'backend.core.context_manager', 'ContextManager'),
        ('DynamicModelRouter', 'backend.core.dynamic_router', 'DynamicModelRouter'),
        ('PromptOptimizer', 'backend.core.prompt_optimizer', 'PromptOptimizer'),
        ('CostAnalytics', 'backend.core.cost_analytics', 'CostAnalytics'),
        ('MarvelousOptimizer', 'backend.core.marvelous_optimizer', 'MarvelousAIOptimizer'),
        ('BatchProcessor', 'backend.core.marvelous_batch_processor', 'MarvelousBatchProcessor'),
        ('ProviderArbitrage', 'backend.core.provider_arbitrage', 'ProviderArbitrage'),
        ('OptimizationDashboard', 'backend.core.optimization_dashboard', 'OptimizationDashboard')
    ]
    
    working = 0
    failed = 0
    
    for display_name, module_path, class_name in components:
        try:
            print(f"Testing {display_name}...")
            
            # Import module
            module = __import__(module_path, fromlist=[class_name])
            cls = getattr(module, class_name)
            
            # Create instance with minimal parameters
            if display_name == 'SemanticCache':
                instance = cls(l1_size=10, l2_ttl=300, l3_ttl=1800)
            elif display_name == 'SmartRetryManager':
                instance = cls(max_retries=1, base_delay=0.1)
            elif display_name == 'ContextManager':
                instance = cls(max_length=500, compression_ratio=0.8)
            elif display_name == 'DynamicModelRouter':
                instance = cls(cost_threshold=0.01, performance_weight=0.7)
            elif display_name == 'PromptOptimizer':
                instance = cls(token_reduction_target=0.2, semantic_preservation_threshold=0.9)
            elif display_name == 'CostAnalytics':
                instance = cls()
            elif display_name == 'MarvelousOptimizer':
                from backend.core.marvelous_optimizer import OptimizationConfig
                config = OptimizationConfig()
                instance = cls(config)
            elif display_name == 'BatchProcessor':
                instance = cls(batch_size=3, batch_timeout=1.0)
            elif display_name == 'ProviderArbitrage':
                instance = cls(preferred_providers=['openai'], cost_sensitivity=0.7)
            elif display_name == 'OptimizationDashboard':
                instance = cls()
            else:
                instance = cls()
            
            working += 1
            results[display_name] = 'SUCCESS'
            print(f"  Status: SUCCESS")
            
        except Exception as e:
            failed += 1
            error_msg = str(e)[:100]
            results[display_name] = f'FAILED: {error_msg}'
            print(f"  Status: FAILED")
            print(f"  Error: {error_msg}")
    
    print("-" * 40)
    print(f"RESULTS: {working} working, {failed} failed")
    print(f"Success Rate: {(working/(working+failed)*100):.1f}%")
    
    # Save results
    import json
    from datetime import datetime
    
    with open('optimization_test_results.json', 'w') as f:
        json.dump({
            'timestamp': datetime.now().isoformat(),
            'results': results,
            'working': working,
            'failed': failed,
            'success_rate': (working/(working+failed)*100)
        }, f, indent=2)
    
    print("Results saved to: optimization_test_results.json")
    
    return working, failed

if __name__ == "__main__":
    test_optimization_framework()
