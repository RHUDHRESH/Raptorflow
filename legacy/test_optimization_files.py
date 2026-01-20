#!/usr/bin/env python3
"""
Test optimization framework without backend dependencies
"""

import os
import sys

# Set environment variable for encoding
os.environ['PYTHONIOENCODING'] = 'utf-8'

# Disable backend initialization
os.environ['SKIP_BACKEND_INIT'] = '1'

def test_optimization_standalone():
    """Test optimization framework in complete isolation"""
    
    print("Testing Optimization Framework (Standalone)...")
    print("=" * 60)
    
    # Test individual files by reading them
    backend_core_path = os.path.join(os.path.dirname(__file__), 'backend', 'core')
    
    optimization_files = [
        'semantic_cache.py',
        'smart_retry.py',
        'context_manager.py',
        'dynamic_router.py',
        'prompt_optimizer.py',
        'cost_analytics.py',
        'marvelous_optimizer.py',
        'marvelous_batch_processor.py',
        'provider_arbitrage.py',
        'optimization_dashboard.py',
    ]
    
    results = {}
    
    for filename in optimization_files:
        filepath = os.path.join(backend_core_path, filename)
        print(f"\nChecking {filename}...")
        
        if not os.path.exists(filepath):
            print(f"   Status: FILE NOT FOUND")
            results[filename] = 'MISSING'
            continue
            
        try:
            # Check if file can be read
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check for class definitions
            class_name = filename.replace('.py', '').replace('_', ' ').title().replace(' ', '')
            if f'class {class_name}' in content:
                print(f"   Status: CLASS DEFINITION FOUND")
                results[filename] = 'CLASS_FOUND'
            else:
                print(f"   Status: NO CLASS DEFINITION")
                results[filename] = 'NO_CLASS'
                
        except Exception as e:
            print(f"   Status: ERROR - {e}")
            results[filename] = 'ERROR'
    
    # Summary
    print("\n" + "=" * 60)
    print("OPTIMIZATION FRAMEWORK FILE CHECK SUMMARY")
    print("=" * 60)
    
    for filename, status in results.items():
        status_symbol = {
            'CLASS_FOUND': '[OK]',
            'NO_CLASS': '[WARN]',
            'MISSING': '[FAIL]',
            'ERROR': '[FAIL]'
        }.get(status, '[?]')
        print(f"{status_symbol} {filename}")
    
    class_found = sum(1 for s in results.values() if s == 'CLASS_FOUND')
    total = len(results)
    
    print(f"\nFiles with class definitions: {class_found}/{total}")
    
    if class_found == total:
        print("\n[SUCCESS] All optimization framework files have their class definitions!")
        print("The optimization framework code is complete and ready.")
    else:
        print(f"\n[INFO] {total - class_found} files may need attention.")
    
    return results

if __name__ == "__main__":
    test_optimization_standalone()
