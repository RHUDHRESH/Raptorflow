import asyncio
import logging
from typing import Any, Dict, List, Optional

# Import the new SOTA Orchestrator from the services layer
try:
    from backend.services.search.orchestrator import SOTASearchOrchestrator
except ImportError:
    # Fallback for different directory structures in dev
    import sys
    import os
    sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../../..")))
    from backend.services.search.orchestrator import SOTASearchOrchestrator

logger = logging.getLogger("raptorflow.core.search.bridge")

class NativeSearch:
    """
    Bridge class that points to the industrial SOTA Search Orchestrator.
    Maintains backward compatibility with existing modules (e.g. onboarding).
    """

    def __init__(self):
        self.orchestrator = SOTASearchOrchestrator()
        logger.info("NativeSearch: Bridge initialized to SOTASearchOrchestrator")

    async def query(
        self, text: str, limit: int = 5, site: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Queries the SOTA cluster.
        """
        return await self.orchestrator.query(text, limit=limit, site=site)

    async def close(self):
        await self.orchestrator.close()