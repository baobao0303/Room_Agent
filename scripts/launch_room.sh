#!/usr/bin/env bash
# ==============================================================================
# scripts/launch_room.sh - Khởi chạy và liên kết 8 Agent Tabs trong Orca Workspace
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$SCRIPT_DIR"

echo "=== [ORCA SLPC MULTI-AGENT ROOM LAUNCHER] ==="

if ! command -v orca &> /dev/null; then
    echo "⚠️  Lệnh 'orca' chưa có trong PATH. Hãy thêm ~/.config/orca/linux-orca-cli-shim hoặc mở Orca Desktop."
    exit 1
fi

echo "🔍 Kiểm tra trạng thái Orca Runtime..."
if ! orca status --json &> /dev/null; then
    echo "🚀 Đang mở Orca Desktop..."
    orca open || true
    sleep 2
fi

# Đăng ký thông tin terminals
REG_FILE="$SCRIPT_DIR/bmad/rooms/agent_terminals.json"
HB_FILE="$SCRIPT_DIR/bmad/rooms/heartbeats.json"
mkdir -p "$SCRIPT_DIR/bmad/rooms"

# Khai báo 8 agent cần spawn dưới Supervisor (Supervisor chính là terminal hiện tại hoặc launcher)
declare -A AGENTS=(
    ["pm"]="[PM Agent] Product Manager & Decision Arbiter in SLPPC. Chuyên trách đánh giá Feasibility và Alignment qua Kev System One (<50ms), kiểm soát AC và kiểm tra bẫy lỗi cũ từ Harness Learn."
    ["lead"]="[Lead Dev] Architect & PM. Chuyên trách kiến trúc, phân rã task và review code qua 5 tiêu chí."
    ["peer"]="[Peer Dev 1] Code Executor. Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ["peer2"]="[Peer Dev 2] Code Executor. Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ["peer3"]="[Peer Dev 3] Code Executor. Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ["peer4"]="[Peer Dev 4] Code Executor. Chuyên trách thực thi task mã nguồn theo điều phối của Lead."
    ["design"]="[Peer Design] UI/UX & Tokens. Chuyên trách tra cứu token TDS, Figma node mapping, SCSS/CSS design tokens."
    ["qc"]="[QC] 5-Stage ISTQB Verifier. Chuyên trách sinh test matrix, nghiệm thu độc lập và đóng task."
)

declare -A TITLES=(
    ["pm"]="[PM] Feasibility & Alignment"
    ["lead"]="[Lead Dev] Architect & PM"
    ["peer"]="[Peer Dev 1 - Low] Code Executor"
    ["peer2"]="[Peer Dev 2 - Medium] Code Executor"
    ["peer3"]="[Peer Dev 3 - High] Code Executor"
    ["peer4"]="[Peer Dev 4 - Extra] Code Executor"
    ["design"]="[Peer Design] UI/UX & Tokens"
    ["qc"]="[QC] 5-Stage ISTQB Verifier"
)

declare -A MODELS=(
    ["pm"]="ag/gemini-3.8-flash-high"
    ["lead"]="ag/gemini-3.8-flash-high"
    ["peer"]="ag/gemini-3.8-flash-low"
    ["peer2"]="ag/gemini-3.8-flash-medium"
    ["peer3"]="ag/gemini-3.8-flash-high"
    ["peer4"]="ag/gemini-3.8-flash-high"
    ["design"]="ag/gemini-3.8-flash-high"
    ["qc"]="ag/gemini-3.8-flash-high"
)

declare -A REASONINGS=(
    ["pm"]="high"
    ["lead"]="high"
    ["peer"]="low"
    ["peer2"]="medium"
    ["peer3"]="high"
    ["peer4"]="max"
    ["design"]="high"
    ["qc"]="high"
)

# Đọc registry hiện tại nếu có
if [ -f "$REG_FILE" ]; then
    cp "$REG_FILE" "${REG_FILE}.bak" || true
fi

python3 -c "
import json
from pathlib import Path
reg = Path('$REG_FILE')
if not reg.exists():
    reg.write_text('{}')
"

echo "🚀 Bắt đầu khởi động các Agent Tabs..."

for role in pm lead peer peer2 peer3 peer4 design qc; do
    prompt="${AGENTS[$role]}"
    title="${TITLES[$role]}"
    echo "--- Khởi chạy: $title ($role) ---"

    # Spawn qua orca agent launch
    res=$(orca agent launch --worktree active --agent hermes --prompt "$prompt" --json 2>/dev/null || true)
    
    handle=$(echo "$res" | python3 -c "import sys, json; data=json.load(sys.stdin); print(data.get('result', {}).get('outcome', {}).get('handle') or '')" 2>/dev/null || true)
    tab_id=$(echo "$res" | python3 -c "import sys, json; data=json.load(sys.stdin); pk=data.get('result', {}).get('outcome', {}).get('paneKey') or ''; print(pk.split(':')[0] if ':' in pk else pk)" 2>/dev/null || true)

    if [ -n "$handle" ] && [ "$handle" != "" ]; then
        echo "  ✅ Handle: $handle (Tab: $tab_id)"
        
        # Đổi title tab và pane
        orca terminal rename --terminal "$handle" --title "$title" --json &>/dev/null || true
        orca terminal set-pane-title --terminal "$handle" --title "$title" --json &>/dev/null || true
        
        # Gán /title vào Hermes session
        orca terminal send --terminal "$handle" --text "/title $title" --enter &>/dev/null || true
        
        # Cấu hình model & reasoning tier
        model="${MODELS[$role]}"
        reasoning="${REASONINGS[$role]}"
        if [ -n "$model" ]; then
            orca terminal send --terminal "$handle" --text "/model $model" --enter &>/dev/null || true
        fi
        if [ -n "$reasoning" ]; then
            orca terminal send --terminal "$handle" --text "/reasoning $reasoning" --enter &>/dev/null || true
        fi

        # Lưu registry
        python3 -c "
import json
from pathlib import Path
reg = Path('$REG_FILE')
data = json.loads(reg.read_text()) if reg.exists() else {}
data['$role'] = {'handle': '$handle', 'tabId': '$tab_id'}
reg.write_text(json.dumps(data, indent=2))
"
    else
        echo "  ⚠️  Agent $role đã mở hoặc không trả handle mới."
    fi
    sleep 1
done

# Lưu supervisor nếu có
CURRENT_HANDLE=$(orca terminal list --json 2>/dev/null | python3 -c "
import sys, json
try:
    data = json.load(sys.stdin)
    terms = data.get('result', {}).get('terminals', [])
    for t in terms:
        if 'supervisor' in t.get('title', '').lower() or 'scope' in t.get('title', '').lower():
            print(t.get('handle'))
            break
except:
    pass
" || true)

if [ -n "$CURRENT_HANDLE" ]; then
    python3 -c "
import json
from pathlib import Path
reg = Path('$REG_FILE')
data = json.loads(reg.read_text()) if reg.exists() else {}
data['supervisor'] = {'handle': '$CURRENT_HANDLE', 'tabId': ''}
reg.write_text(json.dumps(data, indent=2))
"
fi

echo ""
echo "🎉 HOÀN TẤT KHỞI CHẠY MULTI-AGENT ROOM!"
echo "📋 Danh sách Agent hiện hành trong bmad/rooms/agent_terminals.json:"
cat "$REG_FILE"
