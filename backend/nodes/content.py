#!/usr/bin/env python3
"""
Content Node - Generates marketing content
Converted from 200-line ContentCreator class to 20-line function
"""

import logging
from datetime import datetime
import sys
import os

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(__file__)))

from synapse import brain
from schemas import NodeInput, NodeOutput

logger = logging.getLogger("content")

@brain.register("content_creator")
async def content_node(context: dict) -> dict:
    """Generate marketing content"""
    start_time = datetime.now()
    
    try:
        task = context.get("task", "Generate content")
        logger.info(f"📝 Content Node: {task}")
        
        # Simple content generation (no complex class needed)
        if "blog" in task.lower():
            content = f"# {task}\n\nThis is a comprehensive blog post about {task}.\n\n## Key Points\n- Important point 1\n- Important point 2\n- Important point 3\n\n## Conclusion\n{task} is essential for modern businesses."
        elif "email" in task.lower():
            content = f"Subject: {task}\n\nHi there,\n\nI wanted to reach out about {task}.\n\nBest regards,\nYour Name"
        elif "social" in task.lower():
            content = f"🚀 {task}\n\nTransform your business with innovative solutions.\n\n#marketing #innovation"
        else:
            content = f"Generated content about: {task}"
        
        execution_time = (datetime.now() - start_time).total_seconds()
        
        return {
            "status": "success",
            "data": {
                "content": content,
                "content_type": "generated",
                "word_count": len(content.split()),
                "created_at": datetime.now().isoformat()
            },
            "next_step": "seo_check",
            "execution_time": execution_time
        }
        
    except Exception as e:
        logger.error(f"Content Node Error: {e}")
        return {
            "status": "error",
            "error": str(e),
            "execution_time": (datetime.now() - start_time).total_seconds()
        }
