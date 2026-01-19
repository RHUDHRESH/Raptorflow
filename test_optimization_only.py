#!/usr/bin/env python3
"""
Test Only Optimization Framework - Bypass backend initialization
"""

import os
import sys
import asyncio
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

# Set environment to prevent backend initialization
os.environ['SKIP_BACKEND_INIT'] = '1'

class OptimizationFrameworkTester:
    """Test optimization framework components directly"""
    
    def __init__(self):
        self.results = {}
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
        except Exception:
            pass
    
    def test_optimization_components(self):
        """Test optimization components"""
        print("Testing Optimization Framework Components...")
        print("-" * 50)
        
        components = {}
        
        # Test each component
        test_cases = [
            ('SemanticCache', 'backend.core.semantic_cache', 'SemanticCache', {}),
            ('SmartRetryManager', 'backend.core.smart_retry', 'SmartRetryManager', {}),
            ('ContextManager', 'backend.core.context_manager', 'ContextManager', {}),
            ('DynamicModelRouter', 'backend.core.dynamic_router', 'DynamicModelRouter', {}),
            ('PromptOptimizer', 'backend.core.prompt_optimizer', 'PromptOptimizer', {}),
            ('CostAnalytics', 'backend.core.cost_analytics', 'CostAnalytics', {}),
            ('MarvelousOptimizer', 'backend.core.marvelous_optimizer', 'MarvelousAIOptimizer', {}),
            ('BatchProcessor', 'backend.core.marvelous_batch_processor', 'MarvelousBatchProcessor', {}),
            ('ProviderArbitrage', 'backend.core.provider_arbitrage', 'ProviderArbitrage', {}),
            ('OptimizationDashboard', 'backend.core.optimization_dashboard', 'OptimizationDashboard', {})
        ]
        
        for display_name, module_path, class_name, init_args in test_cases:
            try:
                print(f"Testing {display_name}...")
                
                # Import module
                module = __import__(module_path, fromlist=[class_name])
                cls = getattr(module, class_name)
                
                # Create instance
                if display_name == 'SemanticCache':
                    instance = cls(l1_size=50, l2_ttl=1800, l3_ttl=3600)
                elif display_name == 'SmartRetryManager':
                    instance = cls(max_retries=2, base_delay=0.5)
                elif display_name == 'ContextManager':
                    instance = cls(max_length=1000, compression_ratio=0.7)
                elif display_name == 'DynamicModelRouter':
                    instance = cls(cost_threshold=0.005, performance_weight=0.8)
                elif display_name == 'PromptOptimizer':
                    instance = cls(token_reduction_target=0.3, semantic_preservation_threshold=0.85)
                elif display_name == 'CostAnalytics':
                    instance = cls()
                elif display_name == 'MarvelousOptimizer':
                    from backend.core.marvelous_optimizer import OptimizationConfig
                    config = OptimizationConfig()
                    instance = cls(config)
                elif display_name == 'BatchProcessor':
                    instance = cls(batch_size=5, batch_timeout=2.0)
                elif display_name == 'ProviderArbitrage':
                    instance = cls(preferred_providers=['openai'], cost_sensitivity=0.8)
                elif display_name == 'OptimizationDashboard':
                    instance = cls()
                else:
                    instance = cls(**init_args)
                
                # Test basic functionality
                if hasattr(instance, 'get_stats'):
                    stats = instance.get_stats()
                    components[display_name] = {'status': 'WORKING', 'stats': stats}
                    print(f"  Status: WORKING")
                    print(f"  Stats available: Yes")
                else:
                    components[display_name] = {'status': 'WORKING', 'stats': None}
                    print(f"  Status: WORKING")
                    print(f"  Stats available: No")
                
            except Exception as e:
                error_msg = str(e)[:100]
                components[display_name] = {'status': 'FAILED', 'error': error_msg}
                print(f"  Status: FAILED")
                print(f"  Error: {error_msg}")
            
            print()  # Empty line for readability
        
        self.results = components
        
        # Summary
        working = sum(1 for comp in components.values() if comp['status'] == 'WORKING')
        total = len(components)
        
        print("=" * 50)
        print("OPTIMIZATION FRAMEWORK SUMMARY")
        print("=" * 50)
        print(f"Total Components: {total}")
        print(f"Working: {working}")
        print(f"Failed: {total - working}")
        print(f"Success Rate: {(working/total*100):.1f}%")
        print()
        
        # List working components
        working_components = [name for name, comp in components.items() if comp['status'] == 'WORKING']
        if working_components:
            print("WORKING COMPONENTS:")
            for comp in working_components:
                print(f"  - {comp}")
        
        # List failed components
        failed_components = [(name, comp) for name, comp in components.items() if comp['status'] == 'FAILED']
        if failed_components:
            print("\nFAILED COMPONENTS:")
            for name, comp in failed_components:
                print(f"  - {name}: {comp.get('error', 'Unknown error')}")
        
        # Save results
        self.save_results()
        
        # Provide recommendations
        print("\nRECOMMENDATIONS:")
        if working == total:
            print("- All optimization components are working!")
            print("- Ready to integrate with backend system")
            print("- Test with actual optimization requests")
        elif working >= 7:
            print("- Most optimization components are working")
            print("- Fix failed components for full functionality")
        elif working >= 5:
            print("- Core optimization components are working")
            print("- Fix remaining components")
        else:
            print("- Major issues with optimization framework")
            print("- Check Python dependencies and imports")
            print("- Install missing packages: pip install scikit-learn tiktoken")
    
    def save_results(self):
        """Save results to file"""
        try:
            results_file = os.path.join(os.path.dirname(__file__), 'optimization_framework_test.json')
            
            with open(results_file, 'w') as f:
                import json
                json.dump({
                    'timestamp': datetime.now().isoformat(),
                    'results': self.results
                }, f, indent=2, default=str)
            
            print(f"\nResults saved to: {results_file}")
            
        except Exception as e:
            print(f"Failed to save results: {e}")

def main():
    """Main function"""
    print("RAPTORFLOW OPTIMIZATION FRAMEWORK TEST")
    print("=" * 50)
    print("Testing optimization components directly...")
    print()
    
    tester = OptimizationFrameworkTester()
    tester.test_optimization_components()

if __name__ == "__main__":
    main()
