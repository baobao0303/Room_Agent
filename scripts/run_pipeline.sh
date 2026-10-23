#!/usr/bin/env bash
# scripts/run_pipeline.sh - Runner wrapper for SLPPC Real-Time Pipeline
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

PROMPT="${1:-"Nhiệm vụ kiểm tra và đồng bộ pipeline SLPPC"}"
python3 "$SCRIPT_DIR/scripts/run_pipeline.py" "$PROMPT"
