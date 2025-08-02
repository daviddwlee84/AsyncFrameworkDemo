#!/usr/bin/env python3
"""
Script to start the worker system
"""
import os
import sys
import asyncio
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))

from workers.worker_manager import main as worker_main


def main():
    print("🔄 Starting Worker System...")
    print("👂 Workers will listen for PostgreSQL notifications")
    print("🔧 Available workers: StripeWorker")
    print("=" * 50)

    try:
        # Change to project root directory
        os.chdir(project_root)

        # Start the workers
        asyncio.run(worker_main())

    except KeyboardInterrupt:
        print("\n🛑 Workers stopped")
    except Exception as e:
        print(f"❌ Error starting workers: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
