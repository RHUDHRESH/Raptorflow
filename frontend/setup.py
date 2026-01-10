# Frontend setup script
import os
import subprocess
from pathlib import Path


def install_frontend_dependencies():
    """Install frontend dependencies."""
    print("📦 Installing frontend dependencies...")

    try:
        # Install recharts for charts
        subprocess.run(["npm", "install", "recharts@^2.12.0"], check=True)
        print("✅ Recharts installed")

        # Remove problematic motion library
        subprocess.run(["npm", "uninstall", "motion"], check=True)
        print("✅ Removed motion library")

        print("✅ Frontend dependencies ready")

    except subprocess.CalledProcessError as e:
        print(f"❌ Error installing dependencies: {e}")
        print("👉 Run manually: npm install recharts@^2.12.0 && npm uninstall motion")


def create_env_file():
    """Create .env.local file for frontend."""
    print("📝 Creating frontend .env.local...")

    env_content = """# Frontend Environment Variables
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_APP_NAME=RaptorFlow
NEXT_PUBLIC_APP_VERSION=1.0.0
"""

    env_path = Path(".env.local")
    env_path.write_text(env_content)
    print("✅ .env.local created")


def main():
    """Run frontend setup."""
    print("🔧 Setting up RaptorFlow Frontend...")

    create_env_file()
    install_frontend_dependencies()

    print("\n🎉 Frontend setup complete!")
    print("\nNext steps:")
    print("1. npm run dev")
    print("2. Open http://localhost:3000")
    print("3. Click 'Log In' to see dashboard")


if __name__ == "__main__":
    main()
