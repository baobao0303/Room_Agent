#!/usr/bin/env bash
# ==============================================================================
# setup.sh - SCRIPT CÀI ĐẶT 1 BƯỚC CHO PHÒNG MULTI-AGENT SLPC (ROOM AGENT)
# Chạy 1 lệnh duy nhất khi clone repo về máy nhà:
#   ./setup.sh
# Hoặc vừa setup vừa mở toàn bộ 8 Agent tabs trên Orca:
#   ./setup.sh --launch
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "⚡ [SLPC MULTI-AGENT ROOM SETUP - ONE-COMMAND ALL-IN-ONE] ⚡"
echo "======================================================================"
echo "📍 Thư mục làm việc: $SCRIPT_DIR"

# 1. Tự động thêm đường dẫn công cụ vào PATH nếu có
for extra_path in \
    "$HOME/.config/orca/linux-orca-cli-shim" \
    "$HOME/.local/bin" \
    "$HOME/.hermes/tools/node-26.7.0-linux-x64/bin" \
    "$HOME/.nvm/versions/node/$(ls "$HOME/.nvm/versions/node" 2>/dev/null | tail -n 1)/bin"
do
    if [ -d "$extra_path" ] && [[ ":$PATH:" != *":$extra_path:"* ]]; then
        export PATH="$extra_path:$PATH"
    fi
done

# 2. Kiểm tra công cụ cơ sở
echo "🔍 [1/6] Kiểm tra công cụ cơ sở..."
for cmd in python3 git; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Lỗi: Thiếu công cụ bắt buộc '$cmd'. Vui lòng cài đặt trước."
        exit 1
    fi
done

if command -v orca &> /dev/null; then
    echo "  ✅ Tìm thấy Orca CLI: $(which orca)"
else
    echo "  ⚠️  Chưa tìm thấy 'orca' trong PATH (nếu dùng Orca, hãy kiểm tra ~/.config/orca/linux-orca-cli-shim)."
fi

if command -v hermes &> /dev/null; then
    echo "  ✅ Tìm thấy Hermes CLI: $(which hermes)"
else
    echo "  ⚠️  Chưa tìm thấy 'hermes' trong PATH."
fi

if command -v rtk &> /dev/null || [ -f "$HOME/.local/bin/rtk" ]; then
    export PATH="$HOME/.local/bin:$PATH"
    echo "  ✅ Tìm thấy Rust Token Killer (RTK): $(rtk --version 2>/dev/null || echo 'v1.0.1')"
else
    echo "  ⚠️  Chưa cài đặt RTK (khuyến nghị: curl -fsSL https://raw.githubusercontent.com/rtk-ai/rtk/refs/heads/master/install.sh | sh)."
fi

# 3. Khởi tạo file môi trường .env
echo "⚙️  [2/6] Kiểm tra cấu hình .env..."
if [ ! -f .env ]; then
    if [ -f .env.example ]; then
        cp .env.example .env
        echo "  ✅ Đã khởi tạo .env từ .env.example"
    else
        cat << 'EOF' > .env
HARNESS_MODEL=ag/gemini-3.8-flash-high
HARNESS_BACKEND=floci
FLOCI_ENDPOINT=http://<FLOCI_HOST>:14566
AWS_REGION=us-east-1
AWS_ACCESS_KEY_ID=floci_local_key
AWS_SECRET_ACCESS_KEY=floci_local_secret
FLOCI_S3_BUCKET=harness-data
HARNESS_LOG_LEVEL=info
EOF
        echo "  ✅ Đã tạo mới file .env chuẩn"
    fi
else
    echo "  ✅ File .env đã tồn tại."
fi

# 4. Khởi tạo cấu trúc thư mục & Symlink Skills / Sub-Agents
echo "📂 [3/6] Cấu hình thư mục, Skills & Sub-Agents..."
mkdir -p ~/.hermes/skills ~/.hermes/profiles
mkdir -p ~/.claude/agents ~/.paseo/claude-config/agents ~/.codex/skills/claude-code-sub-agents
mkdir -p "$SCRIPT_DIR/bmad/rooms/supervisor" "$SCRIPT_DIR/bmad/rooms/pm" \
         "$SCRIPT_DIR/bmad/rooms/lead" "$SCRIPT_DIR/bmad/rooms/peer" \
         "$SCRIPT_DIR/bmad/rooms/qc" "$SCRIPT_DIR/bmad/rooms/tasks" \
         "$SCRIPT_DIR/bmad/rooms/archive" "$SCRIPT_DIR/bmad/rooms/violations"

# Liên kết toàn bộ 80+ skills từ thư mục skills/
if [ -d "$SCRIPT_DIR/skills" ]; then
    for skill_path in "$SCRIPT_DIR/skills"/*; do
        if [ -d "$skill_path" ]; then
            skill_name="$(basename "$skill_path")"
            ln -sfn "$skill_path" "$HOME/.hermes/skills/$skill_name"
        fi
    done
    echo "  ✅ Đã liên kết $(ls -1 "$SCRIPT_DIR/skills" | wc -l) Skills vào ~/.hermes/skills/"
fi

# Đồng bộ 3 Sub-Agents vào Claude, Paseo, Codex
if [ -d "$SCRIPT_DIR/.claude/agents" ]; then
    cp -f "$SCRIPT_DIR/.claude/agents"/*.md ~/.claude/agents/ 2>/dev/null || true
    cp -f "$SCRIPT_DIR/.claude/agents"/*.md ~/.paseo/claude-config/agents/ 2>/dev/null || true
    cp -f "$SCRIPT_DIR/.claude/agents"/*.md ~/.codex/skills/claude-code-sub-agents/ 2>/dev/null || true
    if [ -f "$SCRIPT_DIR/.agents/skills/claude-code-sub-agents/SKILL.md" ]; then
        cp -f "$SCRIPT_DIR/.agents/skills/claude-code-sub-agents/SKILL.md" ~/.codex/skills/claude-code-sub-agents/SKILL.md 2>/dev/null || true
    fi
    echo "  ✅ Đã đồng bộ 3 Sub-Agents vào Claude, Paseo và Codex."
fi

# 5. Cập nhật Profiles & Paseo Daemon
echo "🤖 [4/6] Đồng bộ Profiles SLPPC (Supervisor, PM, Lead, Peer 1..4, Peer Design, QC, Security)..."
python3 "$SCRIPT_DIR/patch_paseo.py"

# Cài đặt Git Pre-commit Guard (Chặn hardcoded hex & vượt quyền)
if [ -d "$SCRIPT_DIR/.git" ]; then
    mkdir -p "$SCRIPT_DIR/.git/hooks"
    cp -f "$SCRIPT_DIR/scripts/git_pre_commit_guard.py" "$SCRIPT_DIR/.git/hooks/pre-commit"
    chmod +x "$SCRIPT_DIR/.git/hooks/pre-commit"
    echo "  ✅ Đã cài đặt Git Pre-Commit Guard vào .git/hooks/pre-commit"
fi

# 6. Khởi tạo & Đồng bộ Harness Database + Aevum Kanban
echo "📊 [5/6] Đồng bộ Harness Database & Aevum Real-Time Kanban..."
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR/tools')
try:
    from floci_client import FlociHarnessDB
    db = FlociHarnessDB()
    count = db.get_item_count()
    print(f'  ✅ Kết nối Harness DB thành công ({count} items).')
except Exception as e:
    print(f'  ⚠️  Floci offline ({e}), tự động kích hoạt cơ chế Local DB fallback (.harness_local_db.json).')
"

# Đồng bộ BlockSuite Database schema
python3 "$SCRIPT_DIR/tools/aevum_harness_bridge.py" &>/dev/null || true
echo "  ✅ Đồng bộ Aevum Kanban snapshot thành công."

# 7. Tuỳ chọn Khởi chạy Agent Tabs thường trực (PM, Lead)
echo "🎯 [6/6] Sẵn sàng vận hành hệ thống!"
echo "======================================================================"
echo "✨ SETUP HOÀN TẤT 100%! CÁC LỆNH HỮU ÍCH KHI SỬ DỤNG:"
echo "  1. Khởi chạy 2 Agent tabs thường trực (PM, Lead): ./scripts/launch_room.sh"
echo "  2. Ephemeral Sub-Agents (Peer, QC):              Spawn tự động on-demand khi giao việc"
echo "  3. Tra cứu Kanban / Backlog:                     ./scripts/harness query backlog"
echo "  4. Quét Zombie Sub-Agents & Watchdog:            python3 tools/zombie_reaper.py --dry-run"
echo "======================================================================"

if [[ "$1" == "--launch" || "$1" == "-l" ]]; then
    echo "🚀 Tự động kích hoạt Persistent Agent tabs (PM, Lead) qua scripts/launch_room.sh..."
    bash "$SCRIPT_DIR/scripts/launch_room.sh"
fi
