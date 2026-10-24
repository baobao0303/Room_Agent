#!/usr/bin/env bash
# ==============================================================================
# scripts/setup_rooms.sh - Idempotent Multi-Machine Room Worktree Provisioner
# Khởi tạo 4 phòng làm việc độc lập (Worktree) cho mô hình SLPPC:
# 1. room-pm    (Nhánh: room-pm)    - PM Agent (Feasibility & Alignment)
# 2. room-lead  (Nhánh: room-lead)  - Lead Dev (Technical Architecture & Tasks)
# 3. room-peer  (Nhánh: room-peer)  - Peer Dev (Code Execution & TDD)
# 4. room-qc    (Nhánh: room-qc)    - QC Gate (5-Stage ISTQB Testing)
# Branch chính `main`: Không gian của Supervisor (Scope & Intent Guard)
#
# Sử dụng:
#   ./scripts/setup_rooms.sh            # Khởi tạo / cập nhật idempotent (không mở trùng)
#   ./scripts/setup_rooms.sh --clean    # Xoá toàn bộ 4 room cũ và dựng lại từ đầu
#   ./scripts/setup_rooms.sh --teardown # Chỉ dọn dẹp xoá hết 4 room
# ==============================================================================
set -euo pipefail

# 1. Xác định Root Repository
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
ROOT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"
cd "$ROOT_DIR"

MODE="${1:-}"

echo "======================================================================"
echo "🏛️  [SLPPC MULTI-MACHINE WORKTREE & ROOM PROVISIONER]"
echo "======================================================================"
echo "📍 Repo Root: $ROOT_DIR"
echo "🌿 Current Branch: $(git rev-parse --abbrev-ref HEAD)"

# 2. Kiểm tra Git Clean / Repository Valid
if ! git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
    echo "❌ Lỗi: Thư mục hiện tại không phải là Git repository hợp lệ."
    exit 1
fi

# 3. Xác định thư mục chứa Worktree (Ưu tiên Orca workspace nếu có, fallback .worktrees)
REPO_NAME="$(basename "$ROOT_DIR")"
ORCA_AVAILABLE=false
if command -v orca >/dev/null 2>&1 && orca status --json >/dev/null 2>&1; then
    ORCA_AVAILABLE=true
fi

if [ -n "${WORKTREE_BASE_DIR:-}" ]; then
    WT_DIR="$WORKTREE_BASE_DIR"
elif [ "$ORCA_AVAILABLE" = true ]; then
    WT_DIR="$HOME/orca/workspaces/$REPO_NAME"
else
    WT_DIR="$ROOT_DIR/.worktrees"
fi

mkdir -p "$WT_DIR"
mkdir -p "$ROOT_DIR/bmad/rooms"/{supervisor,pm,lead,peer,qc,archive}

ROLES=("pm" "lead" "peer" "qc")
DESCRIPTIONS=(
    "PM Agent: Thẩm định Feasibility, Alignment Kev System One, Acceptance Criteria"
    "Lead Dev: Technical Architect, Phân rã Zero-Search Task, Code Review 5 tiêu chí"
    "Peer Dev: Thực thi mã nguồn, Single-Ownership Diff, Clean Code"
    "QC Verifier: 5-Stage ISTQB Unit Tests, Anti-leak Scan, Independent Gate"
)

# 4. Xử lý Teardown / Clean nếu có flag --clean hoặc --teardown
if [ "$MODE" = "--clean" ] || [ "$MODE" = "--recreate" ] || [ "$MODE" = "--teardown" ]; then
    echo "🧹 [TEARDOWN]: Đang dọn dẹp sạch sẽ 4 phòng làm việc cũ..."

    # Đóng terminal các room trong Orca
    if [ "$ORCA_AVAILABLE" = true ]; then
        TERMS_JSON=$(orca terminal list --json 2>/dev/null || echo "{}")
        for role in "${ROLES[@]}"; do
            HANDLES=$(echo "$TERMS_JSON" | grep -B 2 -A 5 "room-$role" | grep '"handle":' | sed -E 's/.*"handle": "([^"]+)".*/\1/' || true)
            for h in $HANDLES; do
                if [ -n "$h" ]; then
                    echo "   🛑 Đóng terminal $h trong room-$role..."
                    orca terminal close --terminal "$h" --json >/dev/null 2>&1 || true
                fi
            done
        done

        # Xoá worktrees trên Orca
        for role in "${ROLES[@]}"; do
            echo "   🗑️  Xoá Orca worktree: room-$role..."
            orca worktree rm --worktree "room-$role" --json >/dev/null 2>&1 || true
        done
    fi

    # Dọn dẹp git worktree và branch
    for role in "${ROLES[@]}"; do
        target_path="$WT_DIR/room-$role"
        git worktree remove --force "$target_path" >/dev/null 2>&1 || true
        git branch -D "room-$role" >/dev/null 2>&1 || true
        rm -rf "$target_path"
    done
    git worktree prune >/dev/null 2>&1 || true
    rm -rf "$ROOT_DIR/.rooms"

    echo "✨ Đã dọn dẹp hoàn tất."
    if [ "$MODE" = "--teardown" ]; then
        exit 0
    fi
    echo "──────────────────────────────────────────────────────────────────────"
fi

echo "📂 Thư mục Worktree đích: $WT_DIR"
echo "──────────────────────────────────────────────────────────────────────"

# 5. Khởi tạo từng phòng chuẩn SLPPC (Idempotent)
for i in "${!ROLES[@]}"; do
    role="${ROLES[$i]}"
    desc="${DESCRIPTIONS[$i]}"
    room_name="room-$role"
    branch_name="room-$role"
    target_path="$WT_DIR/$room_name"

    echo "⚙️  Đang kiểm tra: $room_name [$desc]..."

    if [ "$ORCA_AVAILABLE" = true ]; then
        ORCA_WTS=$(orca worktree list --json 2>/dev/null || echo "{}")
        if ! echo "$ORCA_WTS" | grep -q "\"displayName\":\"$room_name\""; then
            echo "   🐬 Khởi tạo Orca Worktree: $room_name..."
            orca worktree create \
                --name "$room_name" \
                --comment "SLPPC Room: $role ($desc)" \
                --parent-worktree "branch:main" \
                --base-branch "main" \
                --json >/dev/null 2>&1 || true
        else
            echo "   ✓ Đã có thẻ '$room_name' trên Orca Desktop Board."
        fi
    else
        # Headless Git Worktree fallback
        if ! git show-ref --verify --quiet "refs/heads/$branch_name"; then
            echo "   🌱 Tạo nhánh mới '$branch_name' từ HEAD..."
            git branch "$branch_name" HEAD
        else
            echo "   ✓ Nhánh '$branch_name' đã tồn tại."
        fi

        if git worktree list --porcelain | grep -q "^worktree $target_path$"; then
            echo "   ✓ Git worktree tại '$target_path' đã liên kết."
        elif [ -d "$target_path" ]; then
            echo "   ✓ Thư mục '$target_path' đã tồn tại."
        else
            echo "   🚀 Đang tạo Git worktree: $target_path -> $branch_name..."
            git worktree add "$target_path" "$branch_name"
        fi
    fi

    # Khởi tạo latest_handoff.md mặc định nếu chưa có
    handoff_file="$ROOT_DIR/bmad/rooms/$role/latest_handoff.md"
    if [ ! -f "$handoff_file" ]; then
        cat <<EOF > "$handoff_file"
# BIÊN BẢN BÀN GIAO: $(echo "$role" | tr '[:lower:]' '[:upper:]')
- **Mã Work Item**: #INIT - SLPPC Room Ready
- **Thời gian lập**: $(date "+%Y-%m-%d %H:%M:%S")
- **Agent bàn giao**: System Provisioner
- **Agent nhận tiếp**: $role

### 1. Việc Đã Hoàn Thành
- [x] Khởi tạo Git Worktree '$room_name' trên nhánh '$branch_name'.
- [x] Thiết lập phòng làm việc độc lập, chống đè mã nguồn.

### 2. File Tác Động
- Không có (Trạng thái phòng sạch sẽ).

### 3. Ngữ Cảnh Kỹ Thuật
- Branch: \`$branch_name\`
- Path: \`$target_path\`
- Status: Ready for Task.
EOF
        echo "   ✓ Tạo memo khởi tạo: bmad/rooms/$role/latest_handoff.md"
    fi
    echo ""
done

# 6. Tạo symlink tiện ích trong root repo
if [ ! -e "$ROOT_DIR/.rooms" ]; then
    ln -s "$WT_DIR" "$ROOT_DIR/.rooms" 2>/dev/null || true
fi

echo "======================================================================"
echo "🎉 [HOÀN TẤT THIẾT LẬP 4 ROOMS]:"
git worktree list
echo "======================================================================"
echo "👉 Supervisor: Quản trị tại thư mục gốc (branch 'main')"
echo "👉 PM Room   : $WT_DIR/room-pm   (branch 'room-pm')"
echo "👉 Lead Room : $WT_DIR/room-lead (branch 'room-lead')"
echo "👉 Peer Room : $WT_DIR/room-peer (branch 'room-peer')"
echo "👉 QC Room   : $WT_DIR/room-qc   (branch 'room-qc')"
echo "======================================================================"
