#!/usr/bin/env python3
"""
Script to start the GraphQL backend server
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    print("🚀 Starting GraphQL Backend Server...")
    print("📊 Server will be available at: http://127.0.0.1:8000/graphql")
    print("🔍 GraphQL Playground: http://127.0.0.1:8000/graphql")
    print("=" * 50)

    try:
        # Change to project root directory
        os.chdir(project_root)

        # Start the backend using uvicorn
        subprocess.run(
            [
                "python",
                "-m",
                "uvicorn",
                "backend.main:app",
                "--host",
                "0.0.0.0",
                "--port",
                "8000",
                "--reload",
            ],
            check=True,
        )

    except KeyboardInterrupt:
        print("\n🛑 Backend server stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting backend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
