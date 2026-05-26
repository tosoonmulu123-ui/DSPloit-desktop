#!/usr/bin/env python3
"""
DSPloit PC — PyInstaller build script.
Builds standalone executable for current platform.
"""

import sys
import subprocess
import platform


def build():
    """Build DSPloit PC executable."""
    system = platform.system().lower()
    print(f"Building DSPloit PC for {system}...")

    args = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",
        "--name", "DSPloit-PC",
        "--add-data", f"payloads{':' if system != 'windows' else ';'}payloads",
    ]

    if system == "windows":
        args.append("--windowed")
    elif system == "darwin":
        args.append("--windowed")

    args.append("main.py")

    result = subprocess.run(args, capture_output=False)
    if result.returncode == 0:
        print("\nBuild successful! Check dist/ folder.")
    else:
        print("\nBuild failed!")
        sys.exit(1)


if __name__ == "__main__":
    build()
