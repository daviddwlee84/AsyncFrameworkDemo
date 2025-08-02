#!/usr/bin/env python3
"""
Script to set up the demo environment
"""
import os
import sys
import subprocess
from pathlib import Path

project_root = Path(__file__).parent.parent


def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(
            command,
            shell=True,
            check=True,
            cwd=project_root,
            capture_output=True,
            text=True,
        )
        print(f"✅ {description} completed")
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed: {e}")
        if e.stdout:
            print("STDOUT:", e.stdout)
        if e.stderr:
            print("STDERR:", e.stderr)
        return False


def main():
    print("🎬 Setting up Async Framework Demo...")
    print("=" * 50)

    # Check if we're in the right directory
    if not (project_root / "pyproject.toml").exists():
        print(
            "❌ Error: pyproject.toml not found. Please run this script from the project root."
        )
        sys.exit(1)

    # Install dependencies
    if not run_command("uv sync", "Installing dependencies"):
        print("⚠️ Failed to install dependencies. Please run 'uv sync' manually.")
        return False

    # Start Supabase (if available)
    print("\n📊 Setting up Supabase...")
    if run_command("supabase start", "Starting Supabase services"):
        print("✅ Supabase started successfully")
        print("🗄️ Database migrations will be applied automatically")
    else:
        print(
            "⚠️ Failed to start Supabase. Make sure Supabase CLI is installed and Docker is running."
        )
        print(
            "   You can install Supabase CLI from: https://supabase.com/docs/guides/cli"
        )
        return False

    # Apply migrations
    if not run_command("supabase db reset", "Applying database migrations"):
        print("⚠️ Failed to apply migrations. Please check your Supabase setup.")
        return False

    print("\n" + "=" * 50)
    print("🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Copy environment.example to .env and configure your settings")
    print("2. Set your Stripe API keys (optional - will work in simulation mode)")
    print("3. Run the demo using the provided scripts")
    print("\n🚀 To start the demo:")
    print("   Terminal 1: python scripts/start_backend.py")
    print("   Terminal 2: python scripts/start_workers.py")
    print("   Terminal 3: python scripts/start_frontend.py")

    return True


if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)
