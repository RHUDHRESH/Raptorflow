from typing import Optional
from uuid import UUID

from backend.core.vault import Vault
from backend.models.foundation import BrandKit, FoundationState, Positioning


class FoundationService:
    """
    Service for managing RaptorFlow Foundation: Brand Kits,
    Positioning, and Voice/Tone.
    """

    def __init__(self, vault: Vault):
        self.vault = vault

    async def save_state(self, state: FoundationState) -> FoundationState:
        """Upserts the universal foundation state JSON."""
        session = self.vault.get_session()
        payload = state.model_dump(mode="json")
        # Upsert logic for Supabase (using tenant_id as unique key for state)
        result = (
            session.table("foundation_state")
            .upsert(payload, on_conflict="tenant_id")
            .execute()
        )
        return FoundationState(**result.data[0])

    async def get_state(self, tenant_id: UUID) -> Optional[FoundationState]:
        """Retrieves the universal foundation state JSON."""
        session = self.vault.get_session()
        result = (
            session.table("foundation_state")
            .select("*")
            .eq("tenant_id", str(tenant_id))
            .execute()
        )
        if not result.data:
            return None
        return FoundationState(**result.data[0])

    async def create_brand_kit(self, brand_kit: BrandKit) -> BrandKit:
        """Persists a new brand kit to Supabase."""
        session = self.vault.get_session()
        data = brand_kit.model_dump(mode="json")
        result = session.table("foundation_brand_kit").insert(data).execute()
        return BrandKit(**result.data[0])

    async def get_brand_kit(self, brand_kit_id: UUID) -> Optional[BrandKit]:
        """Retrieves a brand kit by ID."""
        session = self.vault.get_session()
        result = (
            session.table("foundation_brand_kit")
            .select("*")
            .eq("id", str(brand_kit_id))
            .execute()
        )
        if not result.data:
            return None
        return BrandKit(**result.data[0])

    async def update_brand_kit(self, brand_kit_id: UUID, updates: dict) -> BrandKit:
        """Updates an existing brand kit."""
        session = self.vault.get_session()
        result = (
            session.table("foundation_brand_kit")
            .update(updates)
            .eq("id", str(brand_kit_id))
            .execute()
        )
        return BrandKit(**result.data[0])

    async def create_positioning(self, positioning: Positioning) -> Positioning:
        """Persists positioning data."""
        session = self.vault.get_session()
        data = positioning.model_dump(mode="json")
        result = session.table("foundation_positioning").insert(data).execute()
        return Positioning(**result.data[0])

    async def get_active_positioning(self, brand_kit_id: UUID) -> Optional[Positioning]:
        """Retrieves the latest positioning for a brand kit."""
        session = self.vault.get_session()
        result = (
            session.table("foundation_positioning")
            .select("*")
            .eq("brand_kit_id", str(brand_kit_id))
            .order("created_at", desc=True)
            .limit(1)
            .execute()
        )
        if not result.data:
            return None
        return Positioning(**result.data[0])

    async def validate_brand_kit(self, brand_kit_id: UUID) -> bool:
        """Verifies if a brand kit is complete and valid for execution."""
        bk = await self.get_brand_kit(brand_kit_id)
        if not bk:
            return False
        # Industrial-grade validation logic: ensure colors and names are set
        if not bk.primary_color or not bk.name:
            return False
        return True
