#!/usr/bin/env bash
# ==============================================================================
# setup.sh - SCRIPT CÀI ĐẶT 1 BƯỚC CHO HỆ THỐNG 4-ROOM SLPC (ROOM_AGENT)
# Kiến trúc 4 Phòng: Supervisor (main) | Lead (room-lead) | Peer (room-peer) | QC (room-qc)
#
# Cách sử dụng:
#   ./setup.sh                Cài đặt & đồng bộ toàn bộ cấu trúc thư mục, worktree, skills, profiles, DB
#   ./setup.sh --init-db      Khởi tạo mới bảng DynamoDB/S3 & seed dữ liệu mẫu trên Floci
#   ./setup.sh --launch       Cài đặt xong và tự động bật 2 Persistent Agents (Supervisor, Lead)
# ==============================================================================
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

echo "======================================================================"
echo "⚡ [SLPC 4-ROOM MULTI-AGENT SETUP - ONE-COMMAND ALL-IN-ONE] ⚡"
echo "======================================================================"
echo "📍 Thư mục gốc: $SCRIPT_DIR"

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

# 1b. Tự động tắt Linux GNOME/Cinnamon Screen Reader (/usr/bin/orca) để tránh xung đột tên lệnh 'orca'
if command -v gsettings &> /dev/null; then
    gsettings set org.gnome.desktop.a11y.applications screen-reader-enabled false 2>/dev/null || true
    gsettings set org.cinnamon.desktop.a11y.applications screen-reader-enabled false 2>/dev/null || true
fi
pkill -f "/usr/bin/orca" 2>/dev/null || true

# 2. Kiểm tra công cụ cơ sở
echo "🔍 [1/6] Kiểm tra công cụ cơ sở..."
for cmd in python3 git; do
    if ! command -v "$cmd" &> /dev/null; then
        echo "❌ Lỗi: Thiếu công cụ bắt buộc '$cmd'. Vui lòng cài đặt trước."
        exit 1
    fi
done

ORCA_BIN="$(which orca 2>/dev/null || true)"
if [ -n "$ORCA_BIN" ] && [ "$ORCA_BIN" != "/usr/bin/orca" ] && [ "$ORCA_BIN" != "/bin/orca" ]; then
    echo "  ✅ Tìm thấy Orca IDE CLI: $ORCA_BIN"
else
    echo "  ⚠️  Chưa tìm thấy Orca IDE CLI (Đã tự động vô hiệu hóa /usr/bin/orca GNOME Screen Reader)."
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
    echo "  ⚠️  Chưa cài đặt RTK."
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

# 4. Chuẩn hóa Format Folder 4-Room SLPC & Khởi tạo Orca/Git Worktrees
echo "📂 [3/6] Chuẩn hóa cấu trúc thư mục 4-Room SLPC (supervisor, lead, peer, qc)..."
mkdir -p ~/.hermes/skills ~/.hermes/profiles ~/.paseo/skills
mkdir -p "$SCRIPT_DIR/bmad/rooms/supervisor" \
         "$SCRIPT_DIR/bmad/rooms/lead" \
         "$SCRIPT_DIR/bmad/rooms/peer" \
         "$SCRIPT_DIR/bmad/rooms/qc" \
         "$SCRIPT_DIR/bmad/rooms/tasks" \
         "$SCRIPT_DIR/bmad/rooms/discussions" \
         "$SCRIPT_DIR/bmad/rooms/violations" \
         "$SCRIPT_DIR/bmad/rooms/archive" \
         "$SCRIPT_DIR/bmad/adrs" \
         "$SCRIPT_DIR/bmad/wiki"

if [ -f "$SCRIPT_DIR/scripts/setup_rooms.sh" ]; then
    bash "$SCRIPT_DIR/scripts/setup_rooms.sh" >/dev/null 2>&1 || true
    echo "  ✅ Đã đồng bộ các phòng Worktree độc lập (room-lead, room-peer, room-qc)."
fi

# 5. Đồng bộ Skills phân quyền theo 4 vai trò + shared
echo "🧩 [4/6] Đồng bộ hệ thống Skills RBAC (supervisor, lead, peer, qc, shared)..."
python3 -c "
import sys
sys.path.insert(0, '$SCRIPT_DIR')
from tools.skill_manager import sync_skills
res = sync_skills()
print(f'  ✅ Đã đồng bộ {res.get(\"synced_count\", 0)} Skills chuẩn vào {res.get(\"target_rooms_count\", 0)} đích.')
"

# 6. Đồng bộ 4 Profiles SLPC & Git Pre-commit Guard
echo "🤖 [5/6] Đồng bộ 4 Profiles SLPC (Supervisor, Lead, Peer, QC)..."
python3 "$SCRIPT_DIR/scripts/patch_paseo.py"

if [ -d "$SCRIPT_DIR/.git" ]; then
    mkdir -p "$SCRIPT_DIR/.git/hooks"
    cp -f "$SCRIPT_DIR/scripts/git_pre_commit_guard.py" "$SCRIPT_DIR/.git/hooks/pre-commit"
    chmod +x "$SCRIPT_DIR/.git/hooks/pre-commit"
    echo "  ✅ Đã cài đặt Git Pre-Commit Guard vào .git/hooks/pre-commit"
fi

# 7. Khởi tạo & Đồng bộ Harness Database
echo "📊 [6/6] Kiểm tra & Đồng bộ Harness Database..."
if [[ "$*" == *"--init-db"* ]]; then
    echo "  📦 Đang khởi tạo bảng DynamoDB/S3 & nạp dữ liệu mẫu trên Floci..."
    python3 "$SCRIPT_DIR/scripts/harness_init_db.py" || true
    python3 "$SCRIPT_DIR/scripts/harness_seed.py" || true
fi

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

echo "======================================================================"
echo "✨ SETUP HOÀN TẤT 100%! CẤU TRÚC THƯ MỤC CHUẨN 4-ROOM SLPC:"
echo "  • cli/        : agent-start | orca-review | trigger-flow"
echo "  • profiles/   : supervisor/ | lead/ | peer/ | qc/ (Self-contained PROFILE.md & skills)"
echo "  • bmad/rooms/ : supervisor/ | lead/ | peer/ | qc/ (+ tasks, archive, violations)"
echo "  • worktrees   : main (Supervisor) | room-lead | room-peer | room-qc"
echo "──────────────────────────────────────────────────────────────────────"
echo "  1. Khởi chạy / Xem trạng thái 4 Phòng Agent:     ./cli/agent-start (hoặc ./cli/agent-start status)"
echo "  2. Kích hoạt luồng tự động (SLPC):               ./cli/trigger-flow \"<Epic>\" \"<Mô tả>\""
echo "  3. Duyệt & Merge code từ nhánh Room về main:     ./cli/orca-review status"
echo "  4. Kiểm toán kỷ luật quy trình SLPC:             python3 tools/slppc_flow_guard.py audit"
echo "======================================================================"

if [[ "$*" == *"--launch"* || "$*" == *"-l"* ]]; then
    echo "🚀 Tự động kích hoạt Persistent Agent tabs (Supervisor, Lead) qua ./cli/agent-start..."
    bash "$SCRIPT_DIR/cli/agent-start" start
fi
