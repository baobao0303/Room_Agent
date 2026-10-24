#!/usr/bin/env bash
# =========================================================================
# scripts/start_orca.sh - Launch Orca Desktop from Source Code
# =========================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
exec bash "$DIR/projects/orca/start-dev.sh" "$@"
