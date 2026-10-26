#!/usr/bin/env python3
"""Forwarding wrapper for paseo_hooks.py moved to plugins/slpc-lifecycle-hooks/."""
import subprocess
import sys
from pathlib import Path

TARGET = Path(__file__).resolve().parent.parent / "plugins" / "slpc-lifecycle-hooks" / "paseo_hooks.py"

def main():
    if not TARGET.exists():
        sys.exit(f"Error: Target {TARGET} not found.")
    sys.exit(subprocess.call([sys.executable, str(TARGET)] + sys.argv[1:]))

if __name__ == "__main__":
    main()

