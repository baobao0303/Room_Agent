#!/bin/bash
set -e

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

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

# 3. Đồng bộ Sub-Agents (031_claude_code_sub_agents + slpc-qc-verifier) cho 4 Role SLPC
echo "3. Đồng bộ 031_claude_code_sub_agents + slpc-qc-verifier vào Claude, Paseo & Codex..."
mkdir -p ~/.claude/agents ~/.paseo/claude-config/agents ~/.codex/skills/claude-code-sub-agents
if [ -d "$HOME/storage/031_claude_code_sub_agents" ]; then
    cp -f "$HOME/storage/031_claude_code_sub_agents"/*.md "$SCRIPT_DIR/.claude/agents/" 2>/dev/null || true
fi
cp -f "$SCRIPT_DIR/.claude/agents"/*.md ~/.claude/agents/ 2>/dev/null || true
cp -f "$SCRIPT_DIR/.claude/agents"/*.md ~/.paseo/claude-config/agents/ 2>/dev/null || true
cp -f "$SCRIPT_DIR/.claude/agents"/*.md ~/.codex/skills/claude-code-sub-agents/ 2>/dev/null || true
cp -f "$SCRIPT_DIR/.agents/skills/claude-code-sub-agents/SKILL.md" ~/.codex/skills/claude-code-sub-agents/SKILL.md 2>/dev/null || true

# 4. Chạy python patch cấu hình Paseo CLI (SLPC: Supervisor, Lead, Peer, QC)
echo "4. Cập nhật cấu hình ~/.paseo/config.json (SLPC profiles)..."
python3 "$SCRIPT_DIR/patch_paseo.py"

echo "HOÀN TẤT! Khởi động lại Paseo để nhận skill và các profiles SLPPC (Supervisor, PM, Lead, Peer, QC)."
