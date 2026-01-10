"""
Emergency System Health Check and Recovery
Monitors critical system components and auto-recovers from failures
"""

import asyncio
import subprocess
import time
from datetime import datetime

import aiohttp


class SystemHealthMonitor:
    def __init__(self):
        self.frontend_url = "http://localhost:3000"
        self.backend_url = "http://localhost:8080"
        self.health_status = {
            "frontend": False,
            "backend": False,
            "database": False,
            "last_check": None,
        }

    async def check_service(self, url: str, service_name: str) -> bool:
        """Check if a service is responding"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(
                    url, timeout=aiohttp.ClientTimeout(total=5)
                ) as response:
                    if response.status == 200:
                        print(f"✅ {service_name}: HEALTHY")
                        return True
                    else:
                        print(f"❌ {service_name}: HTTP {response.status}")
                        return False
        except Exception as e:
            print(f"❌ {service_name}: {str(e)}")
            return False

    async def check_database(self) -> bool:
        """Check database connectivity"""
        try:
            # Test Supabase connection
            import os

            from dotenv import load_dotenv

            load_dotenv("frontend/.env.local")

            from supabase import create_client

            supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
            supabase_key = os.getenv("NEXT_PUBLIC_SUPABASE_ANON_KEY")

            if supabase_url and supabase_key:
                client = create_client(supabase_url, supabase_key)
                # Try to access auth endpoint
                response = client.auth.get_session()
                print("✅ Database: CONNECTED")
                return True
            else:
                print("❌ Database: Missing credentials")
                return False
        except Exception as e:
            print(f"❌ Database: {str(e)}")
            return False

    async def restart_backend(self):
        """Restart the backend service"""
        print("🔄 Restarting backend service...")
        try:
            # Kill existing backend processes
            subprocess.run(
                ["taskkill", "/F", "/IM", "python.exe"], capture_output=True, text=True
            )

            # Wait a moment
            await asyncio.sleep(2)

            # Start backend
            subprocess.Popen(
                ["python", "test_backend.py"],
                cwd="c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\backend",
            )

            # Wait for startup
            await asyncio.sleep(5)

            # Check if it's healthy
            if await self.check_service(self.backend_url, "Backend"):
                print("✅ Backend restart: SUCCESS")
                return True
            else:
                print("❌ Backend restart: FAILED")
                return False
        except Exception as e:
            print(f"❌ Backend restart error: {e}")
            return False

    async def restart_frontend(self):
        """Restart the frontend service"""
        print("🔄 Restarting frontend service...")
        try:
            # Kill Node processes
            subprocess.run(
                ["taskkill", "/F", "/IM", "node.exe"], capture_output=True, text=True
            )

            # Wait a moment
            await asyncio.sleep(2)

            # Start frontend
            subprocess.Popen(
                ["npm", "run", "dev"],
                cwd="c:\\Users\\hp\\OneDrive\\Desktop\\Raptorflow\\frontend",
            )

            # Wait for startup
            await asyncio.sleep(10)

            # Check if it's healthy
            if await self.check_service(self.frontend_url, "Frontend"):
                print("✅ Frontend restart: SUCCESS")
                return True
            else:
                print("❌ Frontend restart: FAILED")
                return False
        except Exception as e:
            print(f"❌ Frontend restart error: {e}")
            return False

    async def run_health_check(self):
        """Run comprehensive health check and auto-recovery"""
        print(
            f"\n🏥 SYSTEM HEALTH CHECK - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        print("=" * 60)

        # Check all services
        frontend_healthy = await self.check_service(self.frontend_url, "Frontend")
        backend_healthy = await self.check_service(self.backend_url, "Backend")
        database_healthy = await self.check_database()

        # Update status
        self.health_status = {
            "frontend": frontend_healthy,
            "backend": backend_healthy,
            "database": database_healthy,
            "last_check": datetime.now(),
        }

        # Auto-recovery if needed
        recovery_needed = not all([frontend_healthy, backend_healthy])

        if recovery_needed:
            print("\n🚨 SYSTEM RECOVERY INITIATED")
            print("=" * 60)

            if not backend_healthy:
                await self.restart_backend()

            if not frontend_healthy:
                await self.restart_frontend()

            # Re-check after recovery
            print("\n🔄 POST-RECOVERY VERIFICATION")
            print("=" * 60)
            await self.check_service(self.frontend_url, "Frontend")
            await self.check_service(self.backend_url, "Backend")
            await self.check_database()

        # Final status
        all_healthy = all([frontend_healthy, backend_healthy, database_healthy])

        print(f"\n{'='*60}")
        if all_healthy:
            print("🎉 SYSTEM STATUS: ALL SERVICES HEALTHY")
        else:
            print("⚠️  SYSTEM STATUS: SOME SERVICES UNHEALTHY")
        print(f"{'='*60}\n")

        return all_healthy


async def main():
    """Main health monitor function"""
    monitor = SystemHealthMonitor()

    while True:
        try:
            await monitor.run_health_check()
            # Check every 30 seconds
            await asyncio.sleep(30)
        except KeyboardInterrupt:
            print("\n🛑 Health monitor stopped by user")
            break
        except Exception as e:
            print(f"❌ Health monitor error: {e}")
            await asyncio.sleep(10)


if __name__ == "__main__":
    print("🏥 RAPTORFLOW SYSTEM HEALTH MONITOR")
    print("Press Ctrl+C to stop\n")
    asyncio.run(main())
