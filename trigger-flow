#!/usr/bin/env bash
# trigger-flow: CLI 1 chạm kích hoạt toàn bộ vòng đời SLPPC (PM -> Lead -> Peer -> QC)
set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$SCRIPT_DIR"

if [[ ! -f "$PROJECT_ROOT/scripts/run_pipeline.py" ]]; then
  PROJECT_ROOT="$(cd "$SCRIPT_DIR/.." && pwd)"
fi

PROMPT="${*:-"Nhiệm vụ kiểm tra và đồng bộ pipeline SLPPC"}"
cd "$PROJECT_ROOT"
python3 "$PROJECT_ROOT/scripts/run_pipeline.py" "$PROMPT"
