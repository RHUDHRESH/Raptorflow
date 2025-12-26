"""
Direct Tool Integration Check.
Validates the actual current state of tool integration without imports.
"""

import os
import logging

logger = logging.getLogger("raptorflow.direct_validation")


def check_tool_files_exist():
    """Check if all tool files exist."""
    
    tool_files = [
        "backend/tools/search.py",
        "backend/tools/perplexity.py", 
        "backend/tools/tavily.py",
        "backend/tools/image_gen.py",
        "backend/tools/analytics.py",
        "backend/tools/crm_integration.py",
        "backend/tools/content_scheduler.py",
        "backend/tools/email_automation.py",
        "backend/tools/social_media_manager.py",
        "backend/tools/seo_optimization.py",
        "backend/tools/data_export.py",
        "backend/tools/notification_system.py"
    ]
    
    existing_files = []
    missing_files = []
    
    for file_path in tool_files:
        full_path = os.path.join(os.getcwd(), file_path)
        if os.path.exists(full_path):
            existing_files.append(file_path)
        else:
            missing_files.append(file_path)
    
    return {
        "total_tools": len(tool_files),
        "existing_files": existing_files,
        "missing_files": missing_files,
        "existence_status": "complete" if len(missing_files) == 0 else "incomplete"
    }


def check_registry_integration():
    """Check if tools are registered in registry.py."""
    
    registry_path = os.path.join(os.getcwd(), "backend/tools/registry.py")
    
    if not os.path.exists(registry_path):
        return {"status": "error", "message": "registry.py not found"}
    
    with open(registry_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for tool imports and registrations
    tool_checks = {
        "search": "from tools.search import",
        "perplexity": "from tools.perplexity import", 
        "tavily": "from tools.tavily import",
        "image_gen": "from tools.image_gen import",
        "analytics": "from tools.analytics import",
        "crm_integration": "from tools.crm_integration import",
        "content_scheduler": "from tools.content_scheduler import",
        "email_automation": "from tools.email_automation import",
        "social_media_manager": "from tools.social_media_manager import",
        "seo_optimization": "from tools.seo_optimization import",
        "data_export": "from tools.data_export import",
        "notification_system": "from tools.notification_system import"
    }
    
    registered_tools = []
    missing_registrations = []
    
    for tool, import_check in tool_checks.items():
        if import_check in content:
            registered_tools.append(tool)
        else:
            missing_registrations.append(tool)
    
    return {
        "status": "complete" if len(missing_registrations) == 0 else "incomplete",
        "registered_tools": registered_tools,
        "missing_registrations": missing_registrations,
        "total_registered": len(registered_tools)
    }


def check_frontend_integration():
    """Check if frontend has all tools integrated."""
    
    frontend_path = os.path.join(os.getcwd(), "raptorflow-app/src/components/moves/MoveToolbeltView.tsx")
    
    if not os.path.exists(frontend_path):
        return {"status": "error", "message": "MoveToolbeltView.tsx not found"}
    
    with open(frontend_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check for tool icons and verified tools
    expected_tools = ['Search', 'Copy', 'ImageGen', 'Analytics', 'CRM', 'Scheduler', 'Email', 'Social', 'SEO', 'Export', 'Notifications']
    
    found_tools = []
    missing_tools = []
    
    for tool in expected_tools:
        if tool in content:
            found_tools.append(tool)
        else:
            missing_tools.append(tool)
    
    return {
        "status": "complete" if len(missing_tools) == 0 else "incomplete",
        "found_tools": found_tools,
        "missing_tools": missing_tools,
        "total_found": len(found_tools)
    }


def check_agent_integration():
    """Check if agents have tool integration setup."""
    
    agent_files = [
        "backend/agents/base.py",
        "backend/agents/tool_integration.py",
        "backend/agents/specialists/campaign_planner.py",
        "backend/agents/specialists/copywriter.py"
    ]
    
    integration_status = {
        "base_agent_updated": False,
        "tool_integration_exists": False,
        "specialist_agents_updated": 0,
        "total_specialist_files": 0
    }
    
    # Check base agent
    base_agent_path = os.path.join(os.getcwd(), "backend/agents/base.py")
    if os.path.exists(base_agent_path):
        with open(base_agent_path, 'r', encoding='utf-8') as f:
            content = f.read()
        if "from agents.tool_integration import get_agent_tools" in content:
            integration_status["base_agent_updated"] = True
    
    # Check tool integration file
    tool_integration_path = os.path.join(os.getcwd(), "backend/agents/tool_integration.py")
    if os.path.exists(tool_integration_path):
        integration_status["tool_integration_exists"] = True
    
    # Check specialist agents
    specialist_files = [f for f in agent_files if "specialists" in f]
    integration_status["total_specialist_files"] = len(specialist_files)
    
    for agent_file in specialist_files:
        agent_path = os.path.join(os.getcwd(), agent_file)
        if os.path.exists(agent_path):
            with open(agent_path, 'r', encoding='utf-8') as f:
                content = f.read()
            if "auto_assign_tools=True" in content:
                integration_status["specialist_agents_updated"] += 1
    
    return integration_status


def run_direct_validation():
    """Run direct validation without imports."""
    
    print("=== DIRECT TOOL INTEGRATION VALIDATION ===\n")
    
    # Check tool files
    tool_files_check = check_tool_files_exist()
    print(f"TOOL FILES STATUS: {tool_files_check['existence_status'].upper()}")
    print(f"Total tools: {tool_files_check['total_tools']}")
    print(f"Existing files: {len(tool_files_check['existing_files'])}")
    print(f"Missing files: {len(tool_files_check['missing_files'])}")
    
    if tool_files_check['missing_files']:
        print("Missing tool files:")
        for file in tool_files_check['missing_files']:
            print(f"  - {file}")
    print()
    
    # Check registry integration
    registry_check = check_registry_integration()
    print(f"REGISTRY STATUS: {registry_check['status'].upper()}")
    print(f"Registered tools: {registry_check['total_registered']}")
    print(f"Missing registrations: {len(registry_check['missing_registrations'])}")
    
    if registry_check['missing_registrations']:
        print("Missing tool registrations:")
        for tool in registry_check['missing_registrations']:
            print(f"  - {tool}")
    print()
    
    # Check frontend integration
    frontend_check = check_frontend_integration()
    print(f"FRONTEND STATUS: {frontend_check['status'].upper()}")
    print(f"Tools found in frontend: {frontend_check['total_found']}")
    print(f"Missing frontend tools: {len(frontend_check['missing_tools'])}")
    
    if frontend_check['missing_tools']:
        print("Missing frontend tools:")
        for tool in frontend_check['missing_tools']:
            print(f"  - {tool}")
    print()
    
    # Check agent integration
    agent_check = check_agent_integration()
    print(f"AGENT INTEGRATION STATUS:")
    print(f"Base agent updated: {agent_check['base_agent_updated']}")
    print(f"Tool integration file exists: {agent_check['tool_integration_exists']}")
    print(f"Specialist agents updated: {agent_check['specialist_agents_updated']}/{agent_check['total_specialist_files']}")
    print()
    
    # Overall status
    all_checks = [
        tool_files_check['existence_status'] == "complete",
        registry_check['status'] == "complete", 
        frontend_check['status'] == "complete",
        agent_check['base_agent_updated'] and agent_check['tool_integration_exists']
    ]
    
    overall_status = "COMPLETE" if all(all_checks) else "PARTIAL"
    print(f"=== OVERALL INTEGRATION STATUS: {overall_status} ===")
    
    return {
        "tool_files": tool_files_check,
        "registry": registry_check,
        "frontend": frontend_check,
        "agents": agent_check,
        "overall_status": overall_status
    }


if __name__ == "__main__":
    run_direct_validation()
