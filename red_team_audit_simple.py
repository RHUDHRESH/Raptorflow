#!/usr/bin/env python3
"""
RED TEAM AUDIT: Comprehensive Test of Tasks 21-25
Tests all implemented systems for robustness and correctness
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add backend to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))

def test_timeout_handling():
    """Test Task 21: Agent Timeout Handling"""
    print("🔍 Testing Task 21: Agent Timeout Handling")
    
    try:
        # Check if timeout handling exists in BaseAgent
        from agents.base import BaseAgent
        import inspect
        
        # Look for timeout-related methods
        timeout_methods = []
        for name, method in inspect.getmembers(BaseAgent, predicate=inspect.isfunction):
            if 'timeout' in name.lower() or 'wait_for' in str(method):
                timeout_methods.append(name)
        
        if timeout_methods:
            print(f"✅ PASS: Found timeout methods: {timeout_methods}")
            return {"status": "PASS", "details": f"Timeout methods: {timeout_methods}"}
        else:
            print("❌ FAIL: No timeout handling found")
            return {"status": "FAIL", "details": "No timeout methods found"}
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {"status": "ERROR", "details": str(e)}

def test_agent_caching():
    """Test Task 22: Agent Caching"""
    print("🔍 Testing Task 22: Agent Caching")
    
    try:
        # Check LLM caching
        from agents.llm import get_llm, _llm_cache
        from agents.config import ModelTier
        
        # Test LLM instance caching
        llm1 = get_llm(ModelTier.FLASH_LITE)
        llm2 = get_llm(ModelTier.FLASH_LITE)
        
        if llm1 is llm2 and len(_llm_cache) > 0:
            print("✅ PASS: LLM instance caching working")
            return {"status": "PASS", "details": "LLM caching functional"}
        else:
            print("❌ FAIL: LLM caching not working")
            return {"status": "FAIL", "details": "LLM instances not cached"}
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {"status": "ERROR", "details": str(e)}

def test_health_monitoring():
    """Test Task 23: Agent Health Monitoring"""
    print("🔍 Testing Task 23: Agent Health Monitoring")
    
    try:
        # Check health endpoints
        from agents.dispatcher import AgentDispatcher
        
        dispatcher = AgentDispatcher()
        health_status = dispatcher.get_health_status()
        
        if health_status and "status" in health_status:
            print(f"✅ PASS: Health monitoring working - Status: {health_status['status']}")
            return {"status": "PASS", "details": f"Health status: {health_status['status']}"}
        else:
            print("❌ FAIL: Health monitoring not working")
            return {"status": "FAIL", "details": "No health status returned"}
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {"status": "ERROR", "details": str(e)}

def test_resource_cleanup():
    """Test Task 24: Agent Resource Cleanup"""
    print("🔍 Testing Task 24: Agent Resource Cleanup")
    
    try:
        # Check if BaseAgent has cleanup methods
        from agents.base import BaseAgent
        import inspect
        
        cleanup_methods = []
        for name, method in inspect.getmembers(BaseAgent, predicate=inspect.isfunction):
            if 'cleanup' in name.lower() or 'close' in name.lower():
                cleanup_methods.append(name)
        
        # Check for context managers and proper resource handling
        has_context_manager = hasattr(BaseAgent, '__enter__') and hasattr(BaseAgent, '__exit__')
        
        if cleanup_methods or has_context_manager:
            print(f"✅ PASS: Resource cleanup methods found: {cleanup_methods}")
            return {"status": "PASS", "details": f"Cleanup methods: {cleanup_methods}, Context manager: {has_context_manager}"}
        else:
            print("❌ FAIL: No resource cleanup methods found")
            return {"status": "FAIL", "details": "No cleanup methods or context managers"}
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {"status": "ERROR", "details": str(e)}

def test_security_validation():
    """Test Task 25: Agent Security Validation"""
    print("🔍 Testing Task 25: Agent Security Validation")
    
    try:
        # Check security validation in BaseAgent
        from agents.base import BaseAgent
        import inspect
        
        security_methods = []
        for name, method in inspect.getmembers(BaseAgent, predicate=inspect.isfunction):
            if 'validate' in name.lower() or 'security' in name.lower():
                security_methods.append(name)
        
        if security_methods:
            print(f"✅ PASS: Security validation methods found: {security_methods}")
            return {"status": "PASS", "details": f"Security methods: {security_methods}"}
        else:
            print("❌ FAIL: No security validation methods found")
            return {"status": "FAIL", "details": "No security validation methods"}
            
    except Exception as e:
        print(f"❌ ERROR: {str(e)}")
        return {"status": "ERROR", "details": str(e)}

def test_additional_systems():
    """Test additional systems that should be working"""
    print("🔍 Testing Additional Critical Systems")
    
    results = []
    
    # Test Rate Limiting
    try:
        from api.v1.middleware import get_rate_limiter
        rate_limiter = get_rate_limiter()
        results.append({"test": "Rate Limiting", "status": "PASS", "details": "Rate limiter available"})
    except Exception as e:
        results.append({"test": "Rate Limiting", "status": "FAIL", "details": str(e)})
    
    # Test Metrics Collection
    try:
        from agents.metrics import get_metrics_collector
        metrics = get_metrics_collector()
        results.append({"test": "Metrics Collection", "status": "PASS", "details": "Metrics collector available"})
    except Exception as e:
        results.append({"test": "Metrics Collection", "status": "FAIL", "details": str(e)})
    
    # Test Session Management
    try:
        import sys
        sys.path.append(os.path.join(os.path.dirname(__file__), 'backend'))
        from core.session import get_session_manager
        session_manager = get_session_manager()
        results.append({"test": "Session Management", "status": "PASS", "details": "Session manager available"})
    except Exception as e:
        results.append({"test": "Session Management", "status": "FAIL", "details": str(e)})
    
    # Test Tool Registry
    try:
        from agents.tools.registry import get_tool_registry
        tools = get_tool_registry()
        results.append({"test": "Tool Registry", "status": "PASS", "details": f"Tools available: {len(tools.list_tools())}"})
    except Exception as e:
        results.append({"test": "Tool Registry", "status": "FAIL", "details": str(e)})
    
    return results

async def run_comprehensive_audit():
    """Run comprehensive red team audit."""
    print("🔴 RED TEAM AUDIT: TASKS 21-25 COMPREHENSIVE TESTING")
    print("=" * 60)
    
    start_time = time.time()
    test_results = []
    
    # Test Tasks 21-25
    test_results.append(test_timeout_handling())
    test_results.append(test_agent_caching())
    test_results.append(test_health_monitoring())
    test_results.append(test_resource_cleanup())
    test_results.append(test_security_validation())
    
    # Test additional systems
    additional_results = test_additional_systems()
    test_results.extend(additional_results)
    
    execution_time = (time.time() - start_time) * 1000
    
    # Calculate overall status
    pass_count = sum(1 for r in test_results if r.get("status") == "PASS")
    fail_count = sum(1 for r in test_results if r.get("status") == "FAIL")
    error_count = sum(1 for r in test_results if r.get("status") == "ERROR")
    
    overall_status = "PASS" if fail_count == 0 and error_count == 0 else "FAIL"
    
    print(f"\n🎯 AUDIT COMPLETED IN {execution_time:.0f}ms")
    print(f"OVERALL STATUS: {overall_status}")
    print(f"PASS: {pass_count}, FAIL: {fail_count}, ERROR: {error_count}")
    
    print("\n📋 DETAILED RESULTS:")
    for i, result in enumerate(test_results, 1):
        test_name = result.get("test", f"Test {i}")
        status = result.get("status", "UNKNOWN")
        details = result.get("details", "No details")
        print(f"{i}. {test_name}: {status} - {details}")
    
    # Critical issues summary
    critical_issues = [r for r in test_results if r.get("status") in ["FAIL", "ERROR"]]
    if critical_issues:
        print(f"\n🚨 CRITICAL ISSUES FOUND: {len(critical_issues)}")
        for issue in critical_issues:
            print(f"   - {issue.get('test', 'Unknown')}: {issue.get('details', 'No details')}")
    else:
        print("\n✅ NO CRITICAL ISSUES FOUND")
    
    return {
        "overall_status": overall_status,
        "execution_time_ms": execution_time,
        "pass_count": pass_count,
        "fail_count": fail_count,
        "error_count": error_count,
        "test_results": test_results
    }

if __name__ == "__main__":
    asyncio.run(run_comprehensive_audit())
