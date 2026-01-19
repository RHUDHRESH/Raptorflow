"""
Business Context Manifest (BCM) Reducer

Transforms raw onboarding step data into versioned, compact JSON manifests
with checksums for integrity verification.
"""
import json
import hashlib
from typing import Dict, Any

class BCMReducer:
    def __init__(self):
        self.max_token_budget = 1200  # Hard cap for BCM tokens
        
    async def reduce(self, raw_step_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Reduce onboarding rawStepData into compact BCM JSON manifest.
        
        Args:
            raw_step_data: Raw onboarding data from Supabase
            
        Returns:
            Dictionary containing:
            - manifest: The compact JSON representation
            - version: Integer version counter
            - checksum: SHA-256 checksum of manifest
        """
        # First pass - extract and compact key business context
        foundation = self._extract_foundation(raw_step_data)
        icps = self._extract_icps(raw_step_data)
        competitive = self._extract_competitive(raw_step_data)
        messaging = self._extract_messaging(raw_step_data)
        
        # Assemble initial manifest
        manifest = {
            "foundation": foundation,
            "icps": icps,
            "competitive": competitive,
            "messaging": messaging,
            "meta": {
                "source": "onboarding",
                "token_budget": self.max_token_budget
            }
        }
        
        # Version and checksum
        version = 1  # TODO: Get next version from DB
        checksum = self._compute_checksum(manifest)
        
        return {
            "manifest": manifest,
            "version": version,
            "checksum": checksum
        }
    
    def _extract_foundation(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and compact foundation data."""
        return {
            "company": data.get("company", {}).get("name"),
            "mission": data.get("foundation", {}).get("mission"),
            "value_prop": data.get("foundation", {}).get("value_prop")
        }
    
    def _extract_icps(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and compact ICP data."""
        # Implementation omitted for brevity
        return {}
    
    def _extract_competitive(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and compact competitive data."""
        # Implementation omitted for brevity
        return {}
    
    def _extract_messaging(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Extract and compact messaging data."""
        # Implementation omitted for brevity
        return {}
    
    def _compute_checksum(self, manifest: Dict[str, Any]) -> str:
        """Compute SHA-256 checksum of manifest JSON."""
        manifest_str = json.dumps(manifest, sort_keys=True)
        return hashlib.sha256(manifest_str.encode()).hexdigest()
