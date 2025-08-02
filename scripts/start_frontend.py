#!/usr/bin/env python3
"""
Script to start the Streamlit frontend
"""
import os
import sys
import subprocess
from pathlib import Path

# Add the project root to Python path
project_root = Path(__file__).parent.parent
sys.path.insert(0, str(project_root))


def main():
    print("🎨 Starting Streamlit Frontend...")
    print("🌐 Frontend will be available at: http://127.0.0.1:8501")
    print("=" * 50)

    try:
        # Change to project root directory
        os.chdir(project_root)

        # Start Streamlit
        subprocess.run(
            [
                "python",
                "-m",
                "streamlit",
                "run",
                "frontend/streamlit_app.py",
                "--server.port",
                "8501",
                "--server.address",
                "0.0.0.0",
            ],
            check=True,
        )

    except KeyboardInterrupt:
        print("\n🛑 Frontend stopped")
    except subprocess.CalledProcessError as e:
        print(f"❌ Error starting frontend: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
