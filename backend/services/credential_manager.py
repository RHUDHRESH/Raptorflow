"""
Secure Credential Storage with Encryption
Provides encrypted storage for sensitive payment credentials and API keys
"""

import asyncio
import json
import logging
import os
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass, asdict
from enum import Enum
import uuid
from pathlib import Path
import secrets
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.backends import default_backend
import redis.asyncio as redis
import hashlib

logger = logging.getLogger(__name__)

class CredentialType(Enum):
    """Types of credentials"""
    API_KEY = "api_key"
    CLIENT_SECRET = "client_secret"
    PRIVATE_KEY = "private_key"
    CERTIFICATE = "certificate"
    WEBHOOK_SECRET = "webhook_secret"
    DATABASE_PASSWORD = "database_password"
    ENCRYPTION_KEY = "encryption_key"

@dataclass
class CredentialRecord:
    """Encrypted credential record"""
    id: str
    name: str
    type: CredentialType
    encrypted_value: str
    algorithm: str
    key_id: str
    created_at: datetime
    updated_at: datetime
    expires_at: Optional[datetime] = None
    description: Optional[str] = None
    tags: List[str] = None
    metadata: Dict[str, Any] = None
    is_active: bool = True
    access_count: int = 0
    last_accessed: Optional[datetime] = None

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.metadata is None:
            self.metadata = {}

class CredentialManager:
    """
    Secure credential manager with encryption and access tracking
    """
    
    def __init__(self, storage_dir: str = "secure_credentials"):
        self.storage_dir = Path(storage_dir)
        self.storage_dir.mkdir(exist_ok=True)
        
        # Redis for distributed credential cache
        self.redis_client: Optional[redis.Redis] = None
        self.redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        
        # Master encryption key
        self.master_key = self._get_or_create_master_key()
        self.cipher = Fernet(self.master_key)
        
        # Key rotation settings
        self.key_rotation_interval = timedelta(days=90)
        self.max_keys = 10  # Keep last 10 keys for decryption of old data
        
        # Access tracking
        self.access_log: List[Dict[str, Any]] = []
        self.max_log_entries = 10000
        
        # Initialize key management
        self._initialize_key_management()

    def _get_or_create_master_key(self) -> bytes:
        """Get or create master encryption key"""
        key_file = self.storage_dir / "master_key.enc"
        
        if key_file.exists():
            try:
                with open(key_file, "rb") as f:
                    key_data = json.loads(f.read())
                    key_created = datetime.fromisoformat(key_data["created_at"])
                    
                    # Check if key needs rotation
                    if (datetime.now() - key_created) < self.key_rotation_interval:
                        return base64.b64decode(key_data["key"])
            except Exception as e:
                logger.warning(f"Failed to load master key: {e}")
        
        # Generate new master key
        master_key = Fernet.generate_key()
        
        # Save key with metadata
        key_data = {
            "key": base64.b64encode(master_key).decode(),
            "created_at": datetime.now().isoformat(),
            "algorithm": "FERNET",
            "version": "1.0"
        }
        
        with open(key_file, "w") as f:
            json.dump(key_data, f)
        
        # Set secure permissions
        key_file.chmod(0o600)
        
        logger.info("Master encryption key generated and stored securely")
        return master_key

    def _initialize_key_management(self):
        """Initialize key management system"""
        self.keys_dir = self.storage_dir / "keys"
        self.keys_dir.mkdir(exist_ok=True)
        
        # Generate key derivation salt
        salt_file = self.keys_dir / "key_salt.bin"
        if not salt_file.exists():
            salt = os.urandom(32)
            with open(salt_file, "wb") as f:
                f.write(salt)
            salt_file.chmod(0o600)

    def _derive_key(self, credential_id: str, purpose: str = "encryption") -> bytes:
        """Derive unique key for credential using PBKDF2"""
        salt_file = self.keys_dir / "key_salt.bin"
        with open(salt_file, "rb") as f:
            salt = f.read()
        
        # Use credential ID + purpose for key derivation
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
            backend=default_backend()
        )
        
        key_material = f"{credential_id}:{purpose}".encode()
        return kdf.derive(key_material)

    def _encrypt_credential(self, value: str, credential_id: str) -> tuple[str, str]:
        """Encrypt credential value and return encrypted value + key ID"""
        # Derive unique key for this credential
        key = self._derive_key(credential_id, "encryption")
        cipher = Fernet(base64.urlsafe_b64encode(key))
        
        # Encrypt the value
        encrypted_value = cipher.encrypt(value.encode()).decode()
        
        # Generate key ID for tracking
        key_id = hashlib.sha256(f"{credential_id}:{datetime.now().isoformat()}".encode()).hexdigest()[:16]
        
        return encrypted_value, key_id

    def _decrypt_credential(self, encrypted_value: str, credential_id: str, key_id: str) -> str:
        """Decrypt credential value"""
        # Derive the same key used for encryption
        key = self._derive_key(credential_id, "encryption")
        cipher = Fernet(base64.urlsafe_b64encode(key))
        
        # Decrypt the value
        decrypted_value = cipher.decrypt(encrypted_value.encode()).decode()
        return decrypted_value

    async def initialize(self):
        """Initialize Redis connection"""
        try:
            self.redis_client = redis.from_url(
                self.redis_url,
                encoding="utf-8",
                decode_responses=True
            )
            await self.redis_client.ping()
            logger.info("Credential manager connected to Redis")
        except Exception as e:
            logger.warning(f"Redis not available for credential manager: {e}")
            self.redis_client = None

    async def store_credential(
        self,
        name: str,
        credential_type: CredentialType,
        value: str,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> str:
        """Store encrypted credential"""
        credential_id = str(uuid.uuid4())
        
        # Encrypt the credential value
        encrypted_value, key_id = self._encrypt_credential(value, credential_id)
        
        # Create credential record
        record = CredentialRecord(
            id=credential_id,
            name=name,
            type=credential_type,
            encrypted_value=encrypted_value,
            algorithm="FERNET_PBKDF2",
            key_id=key_id,
            created_at=datetime.now(),
            updated_at=datetime.now(),
            expires_at=expires_at,
            description=description,
            tags=tags or [],
            metadata=metadata or {}
        )
        
        # Store in Redis if available
        if self.redis_client:
            try:
                record_data = json.dumps(asdict(record), default=str)
                ttl = int((expires_at - datetime.now()).total_seconds()) if expires_at else None
                
                if ttl:
                    await self.redis_client.setex(f"cred:{credential_id}", ttl, record_data)
                else:
                    await self.redis_client.set(f"cred:{credential_id}", record_data)
                
                # Add to index
                await self.redis_client.sadd("cred:index", credential_id)
                await self.redis_client.sadd(f"cred:type:{credential_type.value}", credential_id)
                
                for tag in tags or []:
                    await self.redis_client.sadd(f"cred:tag:{tag}", credential_id)
                    
            except Exception as e:
                logger.error(f"Failed to store credential in Redis: {e}")
        
        # Store in local file as backup
        await self._store_credential_file(record)
        
        # Log access
        await self._log_access(credential_id, "store", {"name": name, "type": credential_type.value})
        
        return credential_id

    async def _store_credential_file(self, record: CredentialRecord):
        """Store credential in encrypted file"""
        file_path = self.storage_dir / f"credential_{record.id}.enc"
        
        # Encrypt the entire record
        record_data = json.dumps(asdict(record), default=str)
        encrypted_data = self.cipher.encrypt(record_data.encode()).decode()
        
        with open(file_path, "w") as f:
            f.write(encrypted_data)
        
        # Set secure permissions
        file_path.chmod(0o600)

    async def get_credential(self, credential_id: str) -> Optional[CredentialRecord]:
        """Get credential by ID"""
        # Try Redis first
        if self.redis_client:
            try:
                record_data = await self.redis_client.get(f"cred:{credential_id}")
                if record_data:
                    record_dict = json.loads(record_data)
                    record = CredentialRecord(**record_dict)
                    
                    # Check if expired
                    if record.expires_at and record.expires_at < datetime.now():
                        await self.delete_credential(credential_id)
                        return None
                    
                    # Update access tracking
                    await self._update_access_tracking(credential_id)
                    
                    return record
            except Exception as e:
                logger.error(f"Failed to get credential from Redis: {e}")
        
        # Fallback to file storage
        file_path = self.storage_dir / f"credential_{credential_id}.enc"
        if file_path.exists():
            try:
                with open(file_path, "r") as f:
                    encrypted_data = f.read()
                
                record_data = self.cipher.decrypt(encrypted_data.encode()).decode()
                record_dict = json.loads(record_data)
                record = CredentialRecord(**record_dict)
                
                # Check if expired
                if record.expires_at and record.expires_at < datetime.now():
                    await self.delete_credential(credential_id)
                    file_path.unlink()  # Delete expired file
                    return None
                
                # Update access tracking
                await self._update_access_tracking(credential_id)
                
                return record
                
            except Exception as e:
                logger.error(f"Failed to read credential file: {e}")
        
        return None

    async def get_credential_value(self, credential_id: str) -> Optional[str]:
        """Get decrypted credential value"""
        record = await self.get_credential(credential_id)
        if not record:
            return None
        
        try:
            # Decrypt the value
            decrypted_value = self._decrypt_credential(
                record.encrypted_value,
                credential_id,
                record.key_id
            )
            
            # Log access
            await self._log_access(credential_id, "access", {"name": record.name})
            
            return decrypted_value
            
        except Exception as e:
            logger.error(f"Failed to decrypt credential {credential_id}: {e}")
            return None

    async def update_credential(
        self,
        credential_id: str,
        value: Optional[str] = None,
        name: Optional[str] = None,
        description: Optional[str] = None,
        tags: Optional[List[str]] = None,
        expires_at: Optional[datetime] = None,
        metadata: Optional[Dict[str, Any]] = None
    ) -> bool:
        """Update credential"""
        record = await self.get_credential(credential_id)
        if not record:
            return False
        
        # Update fields
        if value is not None:
            encrypted_value, key_id = self._encrypt_credential(value, credential_id)
            record.encrypted_value = encrypted_value
            record.key_id = key_id
        
        if name is not None:
            record.name = name
        
        if description is not None:
            record.description = description
        
        if tags is not None:
            record.tags = tags
        
        if expires_at is not None:
            record.expires_at = expires_at
        
        if metadata is not None:
            record.metadata.update(metadata)
        
        record.updated_at = datetime.now()
        
        # Store updated record
        if self.redis_client:
            try:
                record_data = json.dumps(asdict(record), default=str)
                ttl = int((record.expires_at - datetime.now()).total_seconds()) if record.expires_at else None
                
                if ttl:
                    await self.redis_client.setex(f"cred:{credential_id}", ttl, record_data)
                else:
                    await self.redis_client.set(f"cred:{credential_id}", record_data)
                    
            except Exception as e:
                logger.error(f"Failed to update credential in Redis: {e}")
        
        # Update file storage
        await self._store_credential_file(record)
        
        # Log access
        await self._log_access(credential_id, "update", {"name": record.name})
        
        return True

    async def delete_credential(self, credential_id: str) -> bool:
        """Delete credential"""
        # Remove from Redis
        if self.redis_client:
            try:
                record = await self.get_credential(credential_id)
                if record:
                    # Remove from indexes
                    await self.redis_client.srem("cred:index", credential_id)
                    await self.redis_client.srem(f"cred:type:{record.type.value}", credential_id)
                    
                    for tag in record.tags:
                        await self.redis_client.srem(f"cred:tag:{tag}", credential_id)
                
                await self.redis_client.delete(f"cred:{credential_id}")
            except Exception as e:
                logger.error(f"Failed to delete credential from Redis: {e}")
        
        # Remove file storage
        file_path = self.storage_dir / f"credential_{credential_id}.enc"
        if file_path.exists():
            try:
                file_path.unlink()
            except Exception as e:
                logger.error(f"Failed to delete credential file: {e}")
        
        # Log access
        await self._log_access(credential_id, "delete", {})
        
        return True

    async def list_credentials(
        self,
        credential_type: Optional[CredentialType] = None,
        tags: Optional[List[str]] = None,
        active_only: bool = True
    ) -> List[CredentialRecord]:
        """List credentials with optional filtering"""
        credentials = []
        
        if self.redis_client:
            try:
                # Get from index
                if credential_type:
                    credential_ids = await self.redis_client.smembers(f"cred:type:{credential_type.value}")
                else:
                    credential_ids = await self.redis_client.smembers("cred:index")
                
                for credential_id in credential_ids:
                    record = await self.get_credential(credential_id)
                    if record:
                        # Apply filters
                        if active_only and not record.is_active:
                            continue
                        
                        if tags and not any(tag in record.tags for tag in tags):
                            continue
                        
                        credentials.append(record)
                        
            except Exception as e:
                logger.error(f"Failed to list credentials from Redis: {e}")
        
        # Fallback to file system
        if not credentials:
            try:
                for file_path in self.storage_dir.glob("credential_*.enc"):
                    credential_id = file_path.stem.replace("credential_", "")
                    record = await self.get_credential(credential_id)
                    
                    if record:
                        # Apply filters
                        if credential_type and record.type != credential_type:
                            continue
                        
                        if active_only and not record.is_active:
                            continue
                        
                        if tags and not any(tag in record.tags for tag in tags):
                            continue
                        
                        credentials.append(record)
                        
            except Exception as e:
                logger.error(f"Failed to list credentials from files: {e}")
        
        return credentials

    async def rotate_keys(self) -> Dict[str, Any]:
        """Rotate encryption keys"""
        start_time = datetime.now()
        rotated_count = 0
        
        try:
            # Generate new master key
            new_master_key = Fernet.generate_key()
            
            # Backup old key
            old_key = self.master_key
            self.master_key = new_master_key
            self.cipher = Fernet(new_master_key)
            
            # Save new master key
            key_file = self.storage_dir / "master_key.enc"
            key_data = {
                "key": base64.b64encode(new_master_key).decode(),
                "created_at": datetime.now().isoformat(),
                "algorithm": "FERNET",
                "version": "1.0",
                "rotated_from": base64.b64encode(old_key).decode()
            }
            
            with open(key_file, "w") as f:
                json.dump(key_data, f)
            key_file.chmod(0o600)
            
            # Re-encrypt all active credentials
            credentials = await self.list_credentials(active_only=True)
            for credential in credentials:
                try:
                    # Get current value
                    current_value = await self.get_credential_value(credential.id)
                    if current_value:
                        # Re-encrypt with new key
                        await self.update_credential(credential.id, value=current_value)
                        rotated_count += 1
                except Exception as e:
                    logger.error(f"Failed to rotate credential {credential.id}: {e}")
            
            duration = (datetime.now() - start_time).total_seconds()
            
            return {
                "success": True,
                "rotated_count": rotated_count,
                "duration_seconds": duration,
                "new_key_created_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "duration_seconds": (datetime.now() - start_time).total_seconds()
            }

    async def _update_access_tracking(self, credential_id: str):
        """Update access tracking for credential"""
        record = await self.get_credential(credential_id)
        if record:
            record.access_count += 1
            record.last_accessed = datetime.now()
            record.updated_at = datetime.now()
            
            # Update in Redis
            if self.redis_client:
                try:
                    record_data = json.dumps(asdict(record), default=str)
                    ttl = int((record.expires_at - datetime.now()).total_seconds()) if record.expires_at else None
                    
                    if ttl:
                        await self.redis_client.setex(f"cred:{credential_id}", ttl, record_data)
                    else:
                        await self.redis_client.set(f"cred:{credential_id}", record_data)
                        
                except Exception as e:
                    logger.error(f"Failed to update access tracking: {e}")

    async def _log_access(self, credential_id: str, action: str, metadata: Dict[str, Any]):
        """Log credential access"""
        log_entry = {
            "credential_id": credential_id,
            "action": action,
            "timestamp": datetime.now().isoformat(),
            "metadata": metadata
        }
        
        self.access_log.append(log_entry)
        
        # Keep log size manageable
        if len(self.access_log) > self.max_log_entries:
            self.access_log = self.access_log[-self.max_log_entries // 2:]

    async def get_access_log(
        self,
        credential_id: Optional[str] = None,
        action: Optional[str] = None,
        limit: int = 100
    ) -> List[Dict[str, Any]]:
        """Get access log with optional filtering"""
        filtered_log = []
        
        for entry in reversed(self.access_log):
            if credential_id and entry["credential_id"] != credential_id:
                continue
            
            if action and entry["action"] != action:
                continue
            
            filtered_log.append(entry)
            
            if len(filtered_log) >= limit:
                break
        
        return filtered_log

    async def health_check(self) -> Dict[str, Any]:
        """Health check for credential manager"""
        try:
            # Test encryption/decryption
            test_value = "test_value_12345"
            test_id = str(uuid.uuid4())
            encrypted, key_id = self._encrypt_credential(test_value, test_id)
            decrypted = self._decrypt_credential(encrypted, test_id, key_id)
            
            encryption_working = decrypted == test_value
            
            # Count credentials
            total_credentials = len(await self.list_credentials())
            active_credentials = len(await self.list_credentials(active_only=True))
            
            return {
                "status": "healthy" if encryption_working else "unhealthy",
                "encryption_working": encryption_working,
                "total_credentials": total_credentials,
                "active_credentials": active_credentials,
                "redis_connected": self.redis_client is not None,
                "master_key_age_days": (datetime.now() - datetime.fromisoformat(json.loads(open(self.storage_dir / "master_key.enc").read())["created_at"])).days
            }
            
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e)
            }

# Global credential manager instance
credential_manager = CredentialManager()
