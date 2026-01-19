#!/usr/bin/env python3
"""
Add missing get_memory_pool function to resource_pool.py
"""

import os
import sys

# Read the resource_pool.py file
resource_pool_path = os.path.join(os.path.dirname(__file__), 'backend', 'core', 'resource_pool.py')

with open(resource_pool_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Check if get_memory_pool already exists
if 'def get_memory_pool' not in content:
    # Add the missing function at the end
    get_memory_pool_code = """

# Global memory pool instance
_memory_pool: Optional[ResourcePool] = None


def get_memory_pool() -> Optional[ResourcePool]:
    \"\"\"Get the global memory pool instance.\"\"\"
    global _memory_pool
    if _memory_pool is None:
        # Create a memory pool with default settings
        from .resource_init import MemoryResource
        _memory_pool = ResourcePool(
            pool_name="memory_pool",
            factory=MemoryResource,
            max_size=100,
            min_size=10,
            timeout=30.0
        )
    return _memory_pool
"""
    
    # Append to the file
    with open(resource_pool_path, 'a', encoding='utf-8') as f:
        f.write(get_memory_pool_code)
    
    print("Added get_memory_pool function to resource_pool.py")
else:
    print("get_memory_pool function already exists")
