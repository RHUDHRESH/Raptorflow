"""
Seed BCM: Load fixture files, run reducer, store in Supabase.

Usage:
    python scripts/seed_bcm.py --all --workspace-id 85be9cfb-7aef-4930-9303-d70551db9f0f
    python scripts/seed_bcm.py --fixture backend/fixtures/business_context_saas.json --workspace-id <uuid>
"""

import argparse
import json
import os
import pathlib
import sys

PROJECT_ROOT = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT))

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / "backend" / ".env")
load_dotenv(PROJECT_ROOT / ".env")

# Fallback env vars if not set
if not os.getenv("SUPABASE_URL"):
    os.environ["SUPABASE_URL"] = "https://vpwwzsanuyhpkvgorcnc.supabase.co"
if not os.getenv("SUPABASE_SERVICE_ROLE_KEY"):
    os.environ["SUPABASE_SERVICE_ROLE_KEY"] = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6InZwd3d6c2FudXlocGt2Z29yY25jIiwicm9sZSI6InNlcnZpY2Vfcm9sZSIsImlhdCI6MTc2MjM5OTU5MSwiZXhwIjoyMDc3OTc1NTkxfQ.6Q7hAvurQR04cYXg0MZPv7-OMBTMqNKV1N02rC_OOnw"

from backend.services.bcm_reducer import reduce_business_context
from backend.core.supabase_mgr import get_supabase_client

FIXTURES_DIR = PROJECT_ROOT / "backend" / "fixtures"


def seed_one(fixture_path: pathlib.Path, workspace_id: str) -> dict:
    """Seed a single business context fixture."""
    print(f"\n📄 Loading: {fixture_path.name}")
    with open(fixture_path, "r", encoding="utf-8") as f:
        business_context = json.load(f)

    client = get_supabase_client()

    # Get next version
    result = (
        client.table("business_context_manifests")
        .select("version")
        .eq("workspace_id", workspace_id)
        .order("version", desc=True)
        .limit(1)
        .execute()
    )
    version = (result.data[0]["version"] + 1) if result.data else 1

    # Run reducer
    manifest = reduce_business_context(
        business_context=business_context,
        workspace_id=workspace_id,
        version=version,
        source="seed",
    )

    # Store in Supabase
    row = {
        "workspace_id": workspace_id,
        "version": version,
        "manifest": manifest,
        "source_context": business_context,
        "checksum": manifest.get("checksum", ""),
        "token_estimate": manifest.get("meta", {}).get("token_estimate", 0),
    }
    result = client.table("business_context_manifests").insert(row).execute()
    if not result.data:
        print(f"  ✗ Failed to store BCM")
        return {}

    stored = result.data[0]
    manifest_json = json.dumps(manifest, separators=(",", ":"))
    company = manifest.get("foundation", {}).get("company", "Unknown")

    print(f"  ✓ {company}")
    print(f"    Version:  {version}")
    print(f"    Checksum: {manifest.get('checksum', 'N/A')}")
    print(f"    Tokens:   ~{manifest.get('meta', {}).get('token_estimate', 0)}")
    print(f"    Size:     {len(manifest_json)} bytes")
    print(f"    ICPs:     {manifest.get('meta', {}).get('icps_count', 0)}")

    # Also hydrate foundations table
    intel = business_context.get("intelligence", {})
    messaging = intel.get("messaging", {})
    company_profile = business_context.get("company_profile", {})

    foundation_row = {
        "workspace_id": workspace_id,
        "company_info": company_profile,
        "mission": company_profile.get("description", ""),
        "value_proposition": intel.get("positioning", {}).get("uvp", ""),
        "brand_voice": messaging.get("brandVoice", {}),
        "messaging": {
            "oneLiner": messaging.get("oneLiner", ""),
            "positioningStatement": messaging.get("positioningStatement", ""),
            "valueProps": messaging.get("valueProps", []),
            "soundbites": messaging.get("soundbites", []),
        },
        "status": "active",
    }
    client.table("foundations").upsert(foundation_row, on_conflict="workspace_id").execute()

    # Hydrate ICP profiles
    for icp in intel.get("icps", []):
        icp_row = {
            "workspace_id": workspace_id,
            "name": icp.get("name", ""),
            "description": icp.get("demographics", {}).get("role", ""),
            "demographics": icp.get("demographics", {}),
            "psychographics": icp.get("psychographics", {}),
            "pain_points": icp.get("painPoints", []),
            "goals": icp.get("goals", []),
            "objections": icp.get("objections", []),
            "market_sophistication": icp.get("marketSophistication", 3),
        }
        client.table("icp_profiles").insert(icp_row).execute()

    return stored


def main():
    parser = argparse.ArgumentParser(description="Seed BCM from fixture files")
    parser.add_argument("--fixture", type=str, help="Path to a single fixture file")
    parser.add_argument("--all", action="store_true", help="Seed all fixtures")
    parser.add_argument("--workspace-id", type=str, required=True, help="Workspace UUID")
    args = parser.parse_args()

    if not args.fixture and not args.all:
        parser.error("Specify --fixture <path> or --all")

    print(f"🎯 Workspace: {args.workspace_id}")

    if args.all:
        fixtures = sorted(FIXTURES_DIR.glob("business_context_*.json"))
        if not fixtures:
            print(f"✗ No fixtures found in {FIXTURES_DIR}")
            sys.exit(1)
        print(f"📦 Found {len(fixtures)} fixtures")
        for f in fixtures:
            seed_one(f, args.workspace_id)
    else:
        path = pathlib.Path(args.fixture)
        if not path.exists():
            print(f"✗ File not found: {path}")
            sys.exit(1)
        seed_one(path, args.workspace_id)

    print("\n✅ Seeding complete!")


if __name__ == "__main__":
    main()
