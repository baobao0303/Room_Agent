#!/usr/bin/env bash
# tools/orca_slpc.sh - Khởi chạy nhanh luồng điều phối 4-Agent SLPC trên Orca Engine
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
export PYTHONPATH="${PROJECT_ROOT}:${PROJECT_ROOT}/tools:${PYTHONPATH:-}"

EPIC_TITLE="${1:-"Nang cap va chuan hoa Module CDP"}"
TASK_TITLE="${2:-"[CDP] - Chuan hoa giao dien theo TDS Tokens"}"
TASK_SPEC="${3:-"Kiem tra css, thay the hex color bang token tds-color, bao dam 100% OnPush"}"

echo "================================================================="
echo "   SLPC MULTI-AGENT ORCHESTRATION PIPELINE ON ORCA ENGINE"
echo "================================================================="

# BƯỚC 1: SUPERVISOR INIT RUN
echo -e "\n[1/4] Supervisor khởi tạo Orchestration Run & Harness Epic..."
INIT_OUT=$(python3 "${PROJECT_ROOT}/tools/orca_slpc_bridge.py" init-run --name "SLPC-$(date +%s)" --title "$EPIC_TITLE")
echo "$INIT_OUT"
EPIC_ID=$(echo "$INIT_OUT" | grep -o 'Epic #[0-9]*' | grep -o '[0-9]*' | head -n1 || echo "1001")

# BƯỚC 2: LEAD CREATE TASK & GATE
echo -e "\n[2/4] Lead bóc tách Task & lập Decision Gate cho QC..."
TASK_OUT=$(python3 "${PROJECT_ROOT}/tools/orca_slpc_bridge.py" create-task --parent-id "$EPIC_ID" --title "$TASK_TITLE" --spec "$TASK_SPEC")
echo "$TASK_OUT"
TASK_ID=$(echo "$TASK_OUT" | grep -o 'Task #[0-9]*' | grep -o '[0-9]*' | head -n1 || echo "1002")

# BƯỚC 3: LEAD DISPATCH CHO PEER
echo -e "\n[3/4] Lead dispatch nhiệm vụ cho Peer Dev..."
python3 "${PROJECT_ROOT}/tools/orca_slpc_bridge.py" dispatch-peer --task-id "$TASK_ID" --prompt "$TASK_SPEC"

echo -e "\n[4/4] Pipeline sẵn sàng! Peer bắt đầu viết code trong sandbox: bmad/rooms/tasks/${TASK_ID}/"
echo "Quy trình chuyển giao tiếp theo chuẩn SLPC:"
echo "  1. Peer nộp code cho Lead Review:"
echo "     python3 tools/orca_slpc_bridge.py report-done --task-id $TASK_ID --files \"<files>\""
echo "  2. Lead Dev thẩm định kiến trúc (5-Point Checklist):"
echo "     python3 tools/orca_slpc_bridge.py lead-review --task-id $TASK_ID"
echo "  3. Khi Lead APPROVED -> Bàn giao sang QC nghiệm thu 5-Stage ISTQB:"
echo "     python3 tools/orca_slpc_bridge.py qc-verify --task-id $TASK_ID --source \"<source_file>\""
echo "================================================================="
