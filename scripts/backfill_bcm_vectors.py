import argparse
import asyncio
import json
import sys

sys.path.append("backend")

from services.bcm_backfill_service import BCMVectorBackfillService


async def main():
    parser = argparse.ArgumentParser(
        description="Backfill BCM vectors into semantic memory"
    )
    parser.add_argument(
        "--table",
        choices=["bcm_manifests", "business_context_manifests", "both"],
        default="both",
    )
    parser.add_argument("--batch-size", type=int, default=50)
    parser.add_argument("--max-records", type=int, default=0)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    service = BCMVectorBackfillService()
    result = await service.backfill(
        table=args.table,
        batch_size=args.batch_size,
        max_records=args.max_records,
        dry_run=args.dry_run,
    )

    print(json.dumps(result))


if __name__ == "__main__":
    asyncio.run(main())
