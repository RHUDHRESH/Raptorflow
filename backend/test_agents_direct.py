#!/usr/bin/env python3
"""
RED TEAM TEST: Find actual flaws in agents system
No imports, no dependencies - just raw code analysis
"""

import os
import sys

# Add current directory to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

def test_imports():
    """Test what actually imports"""
    results = {}
    
    # Test 1: Base classes
    try:
        from agents.base import BaseAgent
        results['base_agent'] = 'PASS'
    except Exception as e:
        results['base_agent'] = f'FAIL: {e}'
    
    # Test 2: Skills registry
    try:
        from agents.skills.registry import get_skills_registry
        results['skills_registry'] = 'PASS'
    except Exception as e:
        results['skills_registry'] = f'FAIL: {e}'
    
    # Test 3: Specialist agents
    try:
        from agents.specialists.content_creator import ContentCreator
        results['content_creator'] = 'PASS'
    except Exception as e:
        results['content_creator'] = f'FAIL: {e}'
    
    # Test 4: LangGraph
    try:
        from langgraph.graph import StateGraph
        results['langgraph'] = 'PASS'
    except Exception as e:
        results['langgraph'] = f'FAIL: {e}'
    
    # Test 5: Main app
    try:
        from main import app
        results['main_app'] = 'PASS'
    except Exception as e:
        results['main_app'] = f'FAIL: {e}'
    
    return results

def test_file_structure():
    """Check if files actually exist"""
    required_files = [
        'agents/base.py',
        'agents/specialists/content_creator.py', 
        'agents/skills/registry.py',
        'main.py',
        'requirements.txt'
    ]
    
    results = {}
    for file_path in required_files:
        if os.path.exists(file_path):
            results[file_path] = 'EXISTS'
        else:
            results[file_path] = 'MISSING'
    
    return results

def main():
    print("=== RED TEAM: AGENTS SYSTEM AUDIT ===")
    
    print("\n1. FILE STRUCTURE CHECK:")
    structure = test_file_structure()
    for file_path, status in structure.items():
        print(f"   {file_path}: {status}")
    
    print("\n2. IMPORT TEST:")
    imports = test_imports()
    for component, status in imports.items():
        print(f"   {component}: {status}")
    
    # Calculate success rate
    total_tests = len(structure) + len(imports)
    passed = len([s for s in structure.values() if s == 'EXISTS'])
    passed += len([s for s in imports.values() if s == 'PASS'])
    
    success_rate = (passed / total_tests) * 100
    print(f"\n=== SUCCESS RATE: {success_rate:.1f}% ===")
    
    if success_rate < 80:
        print("❌ CRITICAL FLAWS DETECTED")
        return False
    else:
        print("✅ SYSTEM IS VIABLE")
        return True

if __name__ == "__main__":
    main()
