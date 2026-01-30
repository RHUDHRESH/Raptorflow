#!/usr/bin/env python3
"""
Backend Route Extraction Script
Extracts all FastAPI routes from the backend codebase.
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Navigate to backend root for imports
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

# Routes catalog
ROUTES: List[Dict[str, Any]] = []
ENDPOINT_FILES: Dict[str, Dict] = {}
ENV_VARS: Dict[str, Dict] = {}
DB_TABLES: Dict[str, Dict] = []

def count_python_files(directory: str) -> int:
    """Count all Python files in directory recursively."""
    count = 0
    for root, dirs, files in os.walk(directory):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv', '.venv', 'dist', 'build']]
        for file in files:
            if file.endswith('.py'):
                count += 1
    return count

def list_backend_structure() -> Dict[str, Any]:
    """List backend directory structure."""
    structure = {
        'total_python_files': 0,
        'directories': {},
        'key_files': [],
        'router_count': 0
    }
    
    backend_path = backend_root / 'backend'
    if not backend_path.exists():
        return structure
    
    # Count files
    structure['total_python_files'] = count_python_files(str(backend_path))
    
    # List top-level directories
    for item in sorted(backend_path.iterdir()):
        if item.is_dir():
            py_count = count_python_files(str(item))
            structure['directories'][item.name] = {
                'python_files': py_count,
                'path': str(item)
            }
    
    # Key files at root level
    key_patterns = ['app.py', 'main.py', 'config*.py', 'database.py', 'dependencies.py', 'redis*.py']
    for pattern in key_patterns:
        matches = list(backend_path.glob(pattern))
        for match in matches:
            structure['key_files'].append(str(match))
    
    # Count routers
    api_v1_path = backend_path / 'api' / 'v1'
    if api_v1_path.exists():
        structure['router_count'] = len(list(api_v1_path.glob('*.py')))
    
    return structure

def extract_endpoints_static(filepath: str) -> List[Dict[str, Any]]:
    """Statically extract endpoints from a Python file."""
    endpoints = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # Check for FastAPI router decorators
            if isinstance(node, ast.Attribute):
                if node.attr in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                    # This is a decorator call
                    pass
            
            # Look for router method calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                        method = node.func.attr.upper()
                        path = None
                        name = None
                        
                        for arg in node.args:
                            if isinstance(arg, ast.Constant):
                                path = arg.value
                        
                        # Check keyword arguments
                        for kw in node.keywords:
                            if kw.arg == 'path':
                                if isinstance(kw.value, ast.Constant):
                                    path = kw.value.value
                            elif kw.arg == 'name':
                                if isinstance(kw.value, ast.Constant):
                                    name = kw.value.value
                        
                        if path:
                            endpoints.append({
                                'method': method,
                                'path': path,
                                'file': filepath,
                                'type': 'router_decorator'
                            })
                
                # Check for app.include_router
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'include_router':
                        for kw in node.keywords:
                            if kw.arg == 'prefix':
                                if isinstance(kw.value, ast.Constant):
                                    endpoints.append({
                                        'type': 'router_inclusion',
                                        'prefix': kw.value.value,
                                        'file': filepath
                                    })
    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return endpoints

def scan_all_routers() -> Tuple[List[Dict], Dict[str, Dict]]:
    """Scan all router files for endpoints."""
    all_endpoints = []
    file_info = {}
    
    api_v1_path = backend_root / 'backend' / 'api' / 'v1'
    
    if api_v1_path.exists():
        for py_file in sorted(api_v1_path.glob('*.py')):
            if py_file.name == '__init__.py':
                continue
            
            endpoints = extract_endpoints_static(str(py_file))
            file_info[py_file.name] = {
                'path': str(py_file),
                'endpoint_count': len(endpoints),
                'endpoints': endpoints
            }
            all_endpoints.extend(endpoints)
    
    return all_endpoints, file_info

def extract_env_vars() -> Dict[str, Dict]:
    """Extract environment variables from code."""
    env_vars = {}
    
    # Check .env file
    env_file = backend_root / 'backend' / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = {
                        'source': '.env file',
                        'value': value.strip() if len(value) < 50 else '<truncated>',
                        'required': True
                    }
    
    # Check config files for env var references
    config_files = [
        backend_root / 'backend' / 'config_clean.py',
        backend_root / 'backend' / 'config.py',
        backend_root / 'backend' / 'config_simple.py',
    ]
    
    for config_file in config_files:
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
                # Look for pydantic Field env references
                matches = re.findall(r'env\s*=\s*["\']([^"\']+)["\']', content)
                for match in matches:
                    if match not in env_vars:
                        env_vars[match] = {
                            'source': str(config_file),
                            'required': 'Field(' in content[max(0, content.find(match)-100):content.find(match)+100]
                        }
    
    return env_vars

def scan_db_tables() -> List[Dict[str, Any]]:
    """Scan for database table references."""
    tables = []
    
    # Common table name patterns in Supabase/Raptorflow
    known_tables = [
        'users', 'workspaces', 'workspace_members', 'profiles',
        'campaigns', 'moves', 'daily_wins', 'business_contexts',
        'subscriptions', 'payments', 'audit_logs', 'sessions',
        'agents', 'memories', 'icps', 'evolutions', 'foundations',
        'onboarding_sessions', 'payment_transactions'
    ]
    
    backend_path = backend_root / 'backend'
    
    for table in known_tables:
        for root, dirs, files in os.walk(backend_path):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if f'table("{table}"' in content or f"'{table}'" in content or f'"{table}"' in content:
                            tables.append({
                                'name': table,
                                'referenced_in': filepath,
                                'operation': 'read/write'
                            })
                    except:
                        pass
    
    # Remove duplicates by table name
    unique_tables = {}
    for table in tables:
        if table['name'] not in unique_tables:
            unique_tables[table['name']] = table
        else:
            if filepath not in unique_tables[table['name']]['referenced_in']:
                pass  # Already tracked
    
    return list(unique_tables.values())

def main():
    """Main function to run the audit."""
    print("=" * 60)
    print("BACKEND ROUTE EXTRACTION SCRIPT")
    print("=" * 60)
    
    # Step 1: Backend structure
    print("\n[1/5] Analyzing backend structure...")
    structure = list_backend_structure()
    print(f"  Total Python files: {structure['total_python_files']}")
    print(f"  Router files: {structure['router_count']}")
    print(f"  Key directories: {len(structure['directories'])}")
    
    # Step 2: Extract endpoints
    print("\n[2/5] Scanning for endpoints...")
    endpoints, file_info = scan_all_routers()
    print(f"  Found {len(endpoints)} endpoints")
    
    # Step 3: Extract env vars
    print("\n[3/5] Extracting environment variables...")
    env_vars = extract_env_vars()
    print(f"  Found {len(env_vars)} environment variables")
    
    # Step 4: Scan DB tables
    print("\n[4/5] Scanning for database tables...")
    tables = scan_db_tables()
    print(f"  Found references to {len(tables)} tables")
    
    # Step 5: Output results
    print("\n[5/5] Outputting results...")
    
    # Summary by method
    method_counts = {}
    for ep in endpoints:
        if 'method' in ep:
            method = ep['method']
            method_counts[method] = method_counts.get(method, 0) + 1
    
    print("\n" + "=" * 60)
    print("ROUTE SUMMARY BY METHOD")
    print("=" * 60)
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count}")
    
    print(f"\nTotal endpoints: {len(endpoints)}")
    
    # Save to JSON for further processing
    output = {
        'structure': structure,
        'endpoints': endpoints,
        'file_info': file_info,
        'env_vars': env_vars,
        'tables': tables,
        'method_counts': method_counts
    }
    
    output_file = backend_root / 'docs' / 'route_audit_output.json'
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nDetailed output saved to: {output_file}")
    
    return output

if __name__ == '__main__':
    main()
"""
Backend Route Extraction Script
Extracts all FastAPI routes from the backend codebase.
"""

import os
import sys
import json
import ast
import re
from pathlib import Path
from typing import Dict, List, Any, Optional, Tuple

# Navigate to backend root for imports
backend_root = Path(__file__).parent.parent.parent
sys.path.insert(0, str(backend_root))

# Routes catalog
ROUTES: List[Dict[str, Any]] = []
ENDPOINT_FILES: Dict[str, Dict] = {}
ENV_VARS: Dict[str, Dict] = {}
DB_TABLES: Dict[str, Dict] = []

def count_python_files(directory: str) -> int:
    """Count all Python files in directory recursively."""
    count = 0
    for root, dirs, files in os.walk(directory):
        # Skip common non-source directories
        dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git', 'node_modules', 'venv', '.venv', 'dist', 'build']]
        for file in files:
            if file.endswith('.py'):
                count += 1
    return count

def list_backend_structure() -> Dict[str, Any]:
    """List backend directory structure."""
    structure = {
        'total_python_files': 0,
        'directories': {},
        'key_files': [],
        'router_count': 0
    }
    
    backend_path = backend_root / 'backend'
    if not backend_path.exists():
        return structure
    
    # Count files
    structure['total_python_files'] = count_python_files(str(backend_path))
    
    # List top-level directories
    for item in sorted(backend_path.iterdir()):
        if item.is_dir():
            py_count = count_python_files(str(item))
            structure['directories'][item.name] = {
                'python_files': py_count,
                'path': str(item)
            }
    
    # Key files at root level
    key_patterns = ['app.py', 'main.py', 'config*.py', 'database.py', 'dependencies.py', 'redis*.py']
    for pattern in key_patterns:
        matches = list(backend_path.glob(pattern))
        for match in matches:
            structure['key_files'].append(str(match))
    
    # Count routers
    api_v1_path = backend_path / 'api' / 'v1'
    if api_v1_path.exists():
        structure['router_count'] = len(list(api_v1_path.glob('*.py')))
    
    return structure

def extract_endpoints_static(filepath: str) -> List[Dict[str, Any]]:
    """Statically extract endpoints from a Python file."""
    endpoints = []
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            content = f.read()
        
        tree = ast.parse(content)
        
        for node in ast.walk(tree):
            # Check for FastAPI router decorators
            if isinstance(node, ast.Attribute):
                if node.attr in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                    # This is a decorator call
                    pass
            
            # Look for router method calls
            if isinstance(node, ast.Call):
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr in ['get', 'post', 'put', 'patch', 'delete', 'options', 'head']:
                        method = node.func.attr.upper()
                        path = None
                        name = None
                        
                        for arg in node.args:
                            if isinstance(arg, ast.Constant):
                                path = arg.value
                        
                        # Check keyword arguments
                        for kw in node.keywords:
                            if kw.arg == 'path':
                                if isinstance(kw.value, ast.Constant):
                                    path = kw.value.value
                            elif kw.arg == 'name':
                                if isinstance(kw.value, ast.Constant):
                                    name = kw.value.value
                        
                        if path:
                            endpoints.append({
                                'method': method,
                                'path': path,
                                'file': filepath,
                                'type': 'router_decorator'
                            })
                
                # Check for app.include_router
                if isinstance(node.func, ast.Attribute):
                    if node.func.attr == 'include_router':
                        for kw in node.keywords:
                            if kw.arg == 'prefix':
                                if isinstance(kw.value, ast.Constant):
                                    endpoints.append({
                                        'type': 'router_inclusion',
                                        'prefix': kw.value.value,
                                        'file': filepath
                                    })
    
    except Exception as e:
        print(f"Error parsing {filepath}: {e}")
    
    return endpoints

def scan_all_routers() -> Tuple[List[Dict], Dict[str, Dict]]:
    """Scan all router files for endpoints."""
    all_endpoints = []
    file_info = {}
    
    api_v1_path = backend_root / 'backend' / 'api' / 'v1'
    
    if api_v1_path.exists():
        for py_file in sorted(api_v1_path.glob('*.py')):
            if py_file.name == '__init__.py':
                continue
            
            endpoints = extract_endpoints_static(str(py_file))
            file_info[py_file.name] = {
                'path': str(py_file),
                'endpoint_count': len(endpoints),
                'endpoints': endpoints
            }
            all_endpoints.extend(endpoints)
    
    return all_endpoints, file_info

def extract_env_vars() -> Dict[str, Dict]:
    """Extract environment variables from code."""
    env_vars = {}
    
    # Check .env file
    env_file = backend_root / 'backend' / '.env'
    if env_file.exists():
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = {
                        'source': '.env file',
                        'value': value.strip() if len(value) < 50 else '<truncated>',
                        'required': True
                    }
    
    # Check config files for env var references
    config_files = [
        backend_root / 'backend' / 'config_clean.py',
        backend_root / 'backend' / 'config.py',
        backend_root / 'backend' / 'config_simple.py',
    ]
    
    for config_file in config_files:
        if config_file.exists():
            with open(config_file, 'r') as f:
                content = f.read()
                # Look for pydantic Field env references
                matches = re.findall(r'env\s*=\s*["\']([^"\']+)["\']', content)
                for match in matches:
                    if match not in env_vars:
                        env_vars[match] = {
                            'source': str(config_file),
                            'required': 'Field(' in content[max(0, content.find(match)-100):content.find(match)+100]
                        }
    
    return env_vars

def scan_db_tables() -> List[Dict[str, Any]]:
    """Scan for database table references."""
    tables = []
    
    # Common table name patterns in Supabase/Raptorflow
    known_tables = [
        'users', 'workspaces', 'workspace_members', 'profiles',
        'campaigns', 'moves', 'daily_wins', 'business_contexts',
        'subscriptions', 'payments', 'audit_logs', 'sessions',
        'agents', 'memories', 'icps', 'evolutions', 'foundations',
        'onboarding_sessions', 'payment_transactions'
    ]
    
    backend_path = backend_root / 'backend'
    
    for table in known_tables:
        for root, dirs, files in os.walk(backend_path):
            dirs[:] = [d for d in dirs if d not in ['__pycache__', '.git']]
            for file in files:
                if file.endswith('.py'):
                    filepath = os.path.join(root, file)
                    try:
                        with open(filepath, 'r', encoding='utf-8') as f:
                            content = f.read()
                        if f'table("{table}"' in content or f"'{table}'" in content or f'"{table}"' in content:
                            tables.append({
                                'name': table,
                                'referenced_in': filepath,
                                'operation': 'read/write'
                            })
                    except:
                        pass
    
    # Remove duplicates by table name
    unique_tables = {}
    for table in tables:
        if table['name'] not in unique_tables:
            unique_tables[table['name']] = table
        else:
            if filepath not in unique_tables[table['name']]['referenced_in']:
                pass  # Already tracked
    
    return list(unique_tables.values())

def main():
    """Main function to run the audit."""
    print("=" * 60)
    print("BACKEND ROUTE EXTRACTION SCRIPT")
    print("=" * 60)
    
    # Step 1: Backend structure
    print("\n[1/5] Analyzing backend structure...")
    structure = list_backend_structure()
    print(f"  Total Python files: {structure['total_python_files']}")
    print(f"  Router files: {structure['router_count']}")
    print(f"  Key directories: {len(structure['directories'])}")
    
    # Step 2: Extract endpoints
    print("\n[2/5] Scanning for endpoints...")
    endpoints, file_info = scan_all_routers()
    print(f"  Found {len(endpoints)} endpoints")
    
    # Step 3: Extract env vars
    print("\n[3/5] Extracting environment variables...")
    env_vars = extract_env_vars()
    print(f"  Found {len(env_vars)} environment variables")
    
    # Step 4: Scan DB tables
    print("\n[4/5] Scanning for database tables...")
    tables = scan_db_tables()
    print(f"  Found references to {len(tables)} tables")
    
    # Step 5: Output results
    print("\n[5/5] Outputting results...")
    
    # Summary by method
    method_counts = {}
    for ep in endpoints:
        if 'method' in ep:
            method = ep['method']
            method_counts[method] = method_counts.get(method, 0) + 1
    
    print("\n" + "=" * 60)
    print("ROUTE SUMMARY BY METHOD")
    print("=" * 60)
    for method, count in sorted(method_counts.items()):
        print(f"  {method}: {count}")
    
    print(f"\nTotal endpoints: {len(endpoints)}")
    
    # Save to JSON for further processing
    output = {
        'structure': structure,
        'endpoints': endpoints,
        'file_info': file_info,
        'env_vars': env_vars,
        'tables': tables,
        'method_counts': method_counts
    }
    
    output_file = backend_root / 'docs' / 'route_audit_output.json'
    output_file.parent.mkdir(exist_ok=True)
    with open(output_file, 'w') as f:
        json.dump(output, f, indent=2, default=str)
    
    print(f"\nDetailed output saved to: {output_file}")
    
    return output

if __name__ == '__main__':
    main()

