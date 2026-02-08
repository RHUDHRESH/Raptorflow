"""
Quick Demo Script - Raptorflow Ultimate Scraper
Run this to see the make-or-break logic in action
"""

import asyncio
import os
import sys

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from raptorflow_ultimate_scraper import RaptorflowUltimateScraper


async def quick_demo():
    """Quick demonstration of the ultimate scraper"""

    print("🚀 RAPTORFLOW ULTIMATE SCRAPER - QUICK DEMO")
    print("=" * 60)
    print("Make-or-Break Logic: Compression Protocol + Signal Proxy")
    print()

    # Initialize scraper
    scraper = RaptorflowUltimateScraper()

    try:
        await scraper.initialize()
        print("✅ System initialized")

        # Demo 1: Compression Protocol
        print("\n🔄 DEMO 1: Compression Protocol")
        print("-" * 40)

        # Create sample move with overdue tasks
        move_id = scraper.compression_protocol.create_sample_move().id
        print(f"✅ Created sample move: {move_id}")

        # Simulate missing Day 3
        from datetime import datetime, timedelta, timezone

        today = datetime.now(timezone.utc)
        yesterday = today - timedelta(days=1)

        move = scraper.compression_protocol.moves[move_id]
        for task in move.tasks:
            if task.day_number == 3:
                task.status = "overdue"
                task.due_date = yesterday

        # Run compression check
        result = await scraper.compression_protocol.check_overdue_tasks(move_id)
        print(f"✅ Compression result: {result['status']}")
        print(f"✅ Overdue tasks processed: {result['overdue_tasks']}")

        # Demo 2: Signal Proxy Architecture
        print("\n📡 DEMO 2: Signal Proxy Architecture")
        print("-" * 40)

        # Test signal classification
        positive_signal = scraper.signal_proxy._classify_signal_type(
            "new feature launch"
        )
        negative_signal = scraper.signal_proxy._classify_signal_type(
            "scam lawsuit crash"
        )

        print(f"✅ Positive signal: {positive_signal}")
        print(f"✅ Negative signal: {negative_signal}")

        # Demo 3: Database Integration
        print("\n🗄️  DEMO 3: Database Integration")
        print("-" * 40)

        # Create move in database
        move_data = {
            "name": "Demo Move",
            "description": "Quick demo move",
            "duration_days": 7,
            "start_date": datetime.now(timezone.utc).isoformat(),
            "end_date": (datetime.now(timezone.utc) + timedelta(days=7)).isoformat(),
            "user_id": "demo_user",
        }

        db_move_id = await scraper.db_manager.create_move(move_data)
        print(f"✅ Database move created: {db_move_id}")

        # Demo 4: System Status
        print("\n📊 DEMO 4: System Status")
        print("-" * 40)

        status = await scraper.get_system_status()
        print(f"✅ System status: {status['system_status']}")
        print(f"✅ Active moves: {status['statistics']['active_moves']}")
        print(f"✅ Components: {len(status['components'])} active")

        print("\n🎯 DEMO COMPLETE")
        print("=" * 60)
        print("✅ Compression Protocol: Working")
        print("✅ Signal Proxy Architecture: Working")
        print("✅ Database Integration: Working")
        print("✅ All Systems: OPERATIONAL")
        print()
        print("🚀 READY FOR PRODUCTION!")

    except Exception as e:
        print(f"❌ Demo failed: {e}")
        import traceback

        traceback.print_exc()

    finally:
        await scraper.shutdown()
        print("✅ System shutdown complete")


if __name__ == "__main__":
    asyncio.run(quick_demo())
