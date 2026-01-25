"""
Supabase Storage Path Utilities
Standardized path convention for all storage operations
"""

import uuid
from datetime import datetime
from typing import Optional


def generate_workspace_path(workspace_slug: str, category: str, filename: Optional[str] = None) -> str:
    """
    Generate standardized storage path for workspace files
    
    Format: workspace/<slug>/<category>/<YYYY>/<MM>/<DD>/<uuid>[-<filename>]
    
    Args:
        workspace_slug: Workspace identifier
        category: File category (uploads, exports, backups, assets, temp, logs)
        filename: Original filename (optional)
    
    Returns:
        Standardized storage path
    """
    date_path = datetime.now().strftime("%Y/%m/%d")
    unique_id = str(uuid.uuid4())
    
    if filename:
        # Sanitize filename and append UUID
        safe_filename = filename.replace(" ", "_").replace("/", "_")
        path = f"workspace/{workspace_slug}/{category}/{date_path}/{unique_id}-{safe_filename}"
    else:
        path = f"workspace/{workspace_slug}/{category}/{date_path}/{unique_id}"
    
    return path


def generate_user_path(user_id: str, category: str, filename: Optional[str] = None) -> str:
    """
    Generate standardized storage path for user files
    
    Format: users/<user_id>/<category>/<YYYY>/<MM>/<DD>/<uuid>[-<filename>]
    
    Args:
        user_id: User identifier
        category: File category (avatars, documents)
        filename: Original filename (optional)
    
    Returns:
        Standardized storage path
    """
    date_path = datetime.now().strftime("%Y/%m/%d")
    unique_id = str(uuid.uuid4())
    
    if filename:
        safe_filename = filename.replace(" ", "_").replace("/", "_")
        path = f"users/{user_id}/{category}/{date_path}/{unique_id}-{safe_filename}"
    else:
        path = f"users/{user_id}/{category}/{date_path}/{unique_id}"
    
    return path


def generate_intelligence_path(query_hash: str, filename: Optional[str] = None) -> str:
    """
    Generate standardized storage path for intelligence outputs
    
    Format: intelligence/<query_hash>/<YYYY>/<MM>/<DD>/<uuid>[-<filename>]
    
    Args:
        query_hash: Hash of the query for deduplication
        filename: Original filename (optional)
    
    Returns:
        Standardized storage path
    """
    date_path = datetime.now().strftime("%Y/%m/%d")
    unique_id = str(uuid.uuid4())
    
    if filename:
        safe_filename = filename.replace(" ", "_").replace("/", "_")
        path = f"intelligence/{query_hash}/{date_path}/{unique_id}-{safe_filename}"
    else:
        path = f"intelligence/{query_hash}/{date_path}/{unique_id}"
    
    return path


def parse_storage_path(path: str) -> dict:
    """
    Parse storage path to extract metadata
    
    Args:
        path: Storage path
    
    Returns:
        Dictionary with parsed metadata
    """
    parts = path.split('/')
    
    result = {
        'type': None,
        'owner_id': None,
        'category': None,
        'date_path': None,
        'unique_id': None,
        'filename': None
    }
    
    if len(parts) >= 6:
        result['type'] = parts[0]  # workspace, users, intelligence
        
        if result['type'] == 'workspace':
            result['owner_id'] = parts[1]  # workspace_slug
            result['category'] = parts[2]  # category
            result['date_path'] = "/".join(parts[3:6])  # YYYY/MM/DD
            result['unique_id'] = parts[6].split('-')[0] if len(parts) > 6 else None
            result['filename'] = "-".join(parts[6].split('-')[1:]) if len(parts) > 6 and '-' in parts[6] else None
        elif result['type'] == 'users':
            result['owner_id'] = parts[1]  # user_id
            result['category'] = parts[2]  # category
            result['date_path'] = "/".join(parts[3:6])  # YYYY/MM/DD
            result['unique_id'] = parts[6].split('-')[0] if len(parts) > 6 else None
            result['filename'] = "-".join(parts[6].split('-')[1:]) if len(parts) > 6 and '-' in parts[6] else None
        elif result['type'] == 'intelligence':
            result['owner_id'] = parts[1]  # query_hash
            result['category'] = 'intelligence'
            result['date_path'] = "/".join(parts[2:5])  # YYYY/MM/DD
            result['unique_id'] = parts[5].split('-')[0] if len(parts) > 5 else None
            result['filename'] = "-".join(parts[5].split('-')[1:]) if len(parts) > 5 and '-' in parts[5] else None
    
    return result


# Bucket mapping constants
BUCKET_MAPPING = {
    # Workspace buckets
    'uploads': 'workspace-uploads',
    'exports': 'workspace-exports', 
    'backups': 'workspace-backups',
    'assets': 'workspace-assets',
    'temp': 'workspace-temp',
    'logs': 'workspace-logs',
    
    # User buckets
    'avatars': 'user-avatars',
    'documents': 'user-documents',
    
    # Special buckets
    'intelligence': 'intelligence-vault',
    'exports': 'user-data',
    'gdpr': 'user-data'
}


def get_bucket_for_category(category: str) -> str:
    """
    Get Supabase bucket name for file category
    
    Args:
        category: File category
    
    Returns:
        Supabase bucket name
    """
    return BUCKET_MAPPING.get(category, 'workspace-uploads')
