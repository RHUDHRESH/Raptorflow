use raptorflow_contracts::{AvatarRegistry, AvatarRegistryEntry};
use uuid::Uuid;

use crate::templates;

pub fn build_avatar_registry(org_id: Uuid) -> AvatarRegistry {
    let entries: Vec<AvatarRegistryEntry> = templates::all()
        .into_iter()
        .map(|t| AvatarRegistryEntry {
            org_id,
            avatar_key: t.avatar_key.to_string(),
            display_name: t.display_name.to_string(),
            role: t.role,
            support_domain: t.support_domain.map(String::from),
            office_zone_id: t.office_zone_id.to_string(),
            reflection_profile: t.reflection_profile.to_string(),
        })
        .collect();

    AvatarRegistry { entries }
}
