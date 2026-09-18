#!/usr/bin/env python3
"""
Application Launcher for Student Performance Tracker
Runs the Streamlit application with proper configurations
"""
import sys
import os
import subprocess

if sys.platform == "win32" and hasattr(sys.stdout, "reconfigure"):
    try:
        sys.stdout.reconfigure(encoding="utf-8", errors="replace")
    except Exception:
        pass

def main():
    print("=" * 60)
    print("🎓 Launching Student Performance Tracker...")
    print("=" * 60)

    # Ensure current directory is in path
    project_root = os.path.dirname(os.path.abspath(__file__))
    os.chdir(project_root)

    app_path = os.path.join(project_root, "app.py")

    # Command to run streamlit through the active python interpreter
    cmd = [
        sys.executable,
        "-m",
        "streamlit",
        "run",
        app_path,
        "--browser.gatherUsageStats=false",
        *sys.argv[1:]
    ]

    try:
        subprocess.run(cmd, check=True)
    except KeyboardInterrupt:
        print("\n👋 Student Performance Tracker stopped.")
    except Exception as e:
        print(f"\n❌ Error launching application: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
