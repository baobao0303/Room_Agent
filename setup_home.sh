#!/bin/bash
set -e

echo "=== SETUP HERMES & PASEO SKILLS (HOME ENVIRONMENT - SLPC) ==="

# 1. Clone repos
echo "1. Đang tải các repo chứa profile và skill..."
cd ~
if [ ! -d "hermes-profiles" ]; then
    git clone https://github.com/magnus919/hermes-profiles.git
else
    echo "hermes-profiles đã tồn tại, đang git pull update..."
    cd hermes-profiles && git pull && cd ..
fi

if [ ! -d "storage" ]; then
    git clone https://github.com/hoangnb24/storage.git
else
    echo "storage đã tồn tại, đang git pull update..."
    cd storage && git pull && cd ..
fi

# 2. Setup thư mục Hermes & Symlink
echo "2. Khởi tạo thư mục ~/.hermes/skills và liên kết file..."
mkdir -p ~/.hermes/skills
mkdir -p ~/.hermes/profiles

ln -sf ~/hermes-profiles/skills/* ~/.hermes/skills/ 2>/dev/null || true
ln -sf ~/storage/* ~/.hermes/skills/ 2>/dev/null || true

# 3. Chạy python patch cấu hình Paseo CLI (SLPC: Supervisor, Lead, Peer, QC)
echo "3. Cập nhật cấu hình ~/.paseo/config.json (SLPC profiles)..."
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
python3 "$SCRIPT_DIR/patch_paseo.py"

echo "HOÀN TẤT! Khởi động lại Paseo để nhận skill và 4 profiles SLPC (Supervisor, Lead, Peer, QC)."
