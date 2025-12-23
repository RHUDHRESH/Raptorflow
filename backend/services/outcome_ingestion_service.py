import logging
from typing import Any, Dict

from backend.core.vault import Vault
from backend.models.blackbox import BlackboxOutcome

logger = logging.getLogger("raptorflow.outcomes")


class OutcomeIngestionService:
    """
    Service for ingesting business outcomes from external webhooks.
    """

    def __init__(self, vault: Vault):
        self.vault = vault

    def ingest_webhook_payload(self, payload: Dict[str, Any]) -> BlackboxOutcome:
        """
        Parses external payload into a BlackboxOutcome and persists it.
        Example Payload: {"source": "linkedin_ads", "conversion_value": 150.0, "confidence": 0.9}
        """
        source = payload.get("source", "unknown")
        # Support various field names from different providers
        value = float(payload.get("conversion_value", payload.get("value", 0.0)))
        confidence = float(payload.get("confidence", 1.0))

        # Attribution fields
        campaign_id = payload.get("campaign_id")
        move_id = payload.get("move_id")

        outcome = BlackboxOutcome(
            source=source,
            value=value,
            confidence=confidence,
            campaign_id=campaign_id,
            move_id=move_id,
        )

        # Persist to database
        session = self.vault.get_session()
        data = outcome.model_dump(mode="json")
        session.table("blackbox_outcomes_industrial").insert(data).execute()

        logger.info(f"Ingested outcome from {source}: ${value}")
        return outcome
