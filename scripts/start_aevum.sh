#!/usr/bin/env bash
# =========================================================================
# Quick Launcher for Aevum from Workspace Root
# =========================================================================
set -e

DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$DIR/projects/Aevum"
bash ./scripts/start-aevum.sh "$@"
