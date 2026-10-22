#!/usr/bin/env python3
"""
scripts/setup_harness_v0114.py - Verification & Installation Script for Harness CLI v0.1.14

Verifies the integrity of scripts/bin/harness-cli using official SHA-256 checksum,
ensures execution permissions, and validates binary runtime output.
"""

import hashlib
import os
import stat
import subprocess
import sys
from pathlib import Path

# Canonical Release Info
EXPECTED_VERSION = "harness-cli 0.1.14"
EXPECTED_SHA256 = "66eb9e33ac0f4b4cb26d5dc175eb8b63debebb00935639aedae5d231fd272004"
DEFAULT_RELEASE_URL = (
    "https://github.com/baobao0303/harness/releases/download/harness-cli-v0.1.14/harness-cli-linux-x64"
)

BASE_DIR = Path(__file__).resolve().parent.parent
BIN_DIR = BASE_DIR / "scripts" / "bin"
TARGET_BIN = BIN_DIR / "harness-cli"
CHECKSUM_FILE = BIN_DIR / "harness-cli-linux-x64.sha256"


def compute_sha256(filepath: Path) -> str:
    h = hashlib.sha256()
    with open(filepath, "rb") as f:
        while chunk := f.read(65536):
            h.update(chunk)
    return h.hexdigest()


def verify_binary(binary_path: Path) -> bool:
    if not binary_path.is_file():
        print(f"❌ Binary file not found: {binary_path}", file=sys.stderr)
        return False

    current_hash = compute_sha256(binary_path)
    print(f"ℹ️ Computed SHA-256 : {current_hash}")
    print(f"ℹ️ Expected SHA-256 : {EXPECTED_SHA256}")

    if current_hash != EXPECTED_SHA256:
        print("❌ Checksum mismatch! Potential corrupted binary or untrusted source.", file=sys.stderr)
        return False
    print("✅ SHA-256 Checksum Verified Successfully.")

    # Ensure executable permission
    current_mode = os.stat(binary_path).st_mode
    os.chmod(binary_path, current_mode | stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH)
    print("✅ Executable permission granted (chmod +x).")

    # Run version check
    try:
        res = subprocess.run(
            [str(binary_path), "--version"],
            capture_output=True,
            text=True,
            check=True,
        )
        version_output = res.stdout.strip()
        print(f"ℹ️ Binary Version Output: {version_output}")
        if EXPECTED_VERSION not in version_output:
            print(f"❌ Version mismatch! Expected '{EXPECTED_VERSION}', got '{version_output}'", file=sys.stderr)
            return False
        print(f"✅ Runtime execution confirmed: {version_output}")
    except Exception as exc:
        print(f"❌ Failed to execute binary: {exc}", file=sys.stderr)
        return False

    return True


def main() -> int:
    print("=== Harness CLI v0.1.14 Verification & Setup ===")
    BIN_DIR.mkdir(parents=True, exist_ok=True)

    # Write checksum file if not present
    CHECKSUM_FILE.write_text(f"{EXPECTED_SHA256}  harness-cli-linux-x64\n")

    if not TARGET_BIN.is_file():
        # Fallback check from projects/harness/target/release
        alt_bin = BASE_DIR / "projects" / "harness" / "target" / "release" / "harness-cli"
        if alt_bin.is_file() and compute_sha256(alt_bin) == EXPECTED_SHA256:
            import shutil
            shutil.copy2(alt_bin, TARGET_BIN)
            print(f"ℹ️ Copied binary from {alt_bin} to {TARGET_BIN}")

    if not verify_binary(TARGET_BIN):
        return 1

    print("🎉 Setup and verification complete! Binary is ready for production use.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
