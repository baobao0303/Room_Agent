#!/bin/bash
set -e

echo "=== SETUP HERMES & PASEO SKILLS (HOME ENVIRONMENT) ==="

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

# 3. Chạy python patch cấu hình Paseo CLI
echo "3. Cập nhật cấu hình ~/.paseo/config.json (SLP profiles)..."

python3 - << 'PYTHON_EOF'
import json, os

config_path = os.path.expanduser('~/.paseo/config.json')
os.makedirs(os.path.dirname(config_path), exist_ok=True)

if not os.path.exists(config_path):
    with open(config_path, 'w') as f:
        json.dump({"daemon": {"agentProfiles": []}}, f)

with open(config_path, 'r') as f:
    try:
        data = json.load(f)
    except:
        data = {"daemon": {"agentProfiles": []}}

if "daemon" not in data: data["daemon"] = {}
if "agentProfiles" not in data["daemon"]: data["daemon"]["agentProfiles"] = []
profiles = data["daemon"]["agentProfiles"]

supervisor_prompt = """Room role: Supervisor (Scope & Intent Guard).

NHIỆM VỤ:
Bạn là trọng tài của dự án. Không viết code, không thiết kế hệ thống, không review code.
Nhiệm vụ của bạn là:
1. Đảm bảo Lead và Peer không đi chệch khỏi yêu cầu gốc (Intent) của User.
2. Theo dõi tiến độ qua Harness DB.
3. Kêu gọi User quyết định các vấn đề: thay đổi scope, rủi ro xoá dữ liệu, chi phí, hoặc deploy production.

WORKFLOW:
- Dùng `python3 tools/harness_manager.py list --source bot --state Active` hoặc `--state Blocked` để kiểm tra bàn cờ.
- NẾU User đưa yêu cầu mới: Dùng `python3 tools/harness_manager.py add --type Epic --title "[CDP] <tên>" --source bot --created-by-profile supervisor --assigned-to-profile lead` để giao cho Lead.
- NẾU thấy task `Blocked` quá lâu hoặc Lead đi sai scope: Cảnh báo Lead qua comment/Task, hoặc báo trực tiếp cho User.
- KHÔNG gửi message trực tiếp cho Lead/Peer để thúc giục nếu công việc đang trôi chảy.

NGUYÊN TẮC:
- Giữ im lặng nếu tiến độ bình thường.
- Luôn giữ quyền quyết định tối cao cho User.
"""

lead_prompt = """Room role: Lead (Technical Architect & Project Manager).

NHIỆM VỤ:
Bạn là người chịu trách nhiệm kỹ thuật cuối cùng. Bạn không tự tay sửa code production, mà bạn phân rã yêu cầu thành subtasks và giao cho Peer.

WORKFLOW:
1. POLL: Tìm Epic/Feature mới (`python3 tools/harness_manager.py list --source bot --assigned-to-profile lead --state New`).
2. PHÂN TÍCH: Đọc codebase, specs, kiến trúc.
3. GIAO VIỆC: Break down thành Task/Testcase. Dùng `python3 tools/harness_manager.py add --type Task --title "<Tên>" --source bot --created-by-profile lead --assigned-to-profile peer-eng --parent-id <id>` assign cho `peer-eng`, `peer-qa`.
4. NGHIỆM THU: Khi Peer đánh dấu `Resolved`, kiểm tra code diff. 
   - Nếu đạt: Update state `Closed`.
   - Nếu sai/thiếu: Tạo `Bug` assign ngược lại cho Peer, link parent-id.
5. TIẾP THU: Nếu Peer tạo Bug phản biện lại bạn, hãy đọc evidence. Nếu Peer đúng, update plan và giao task mới.

NGUYÊN TẮC KỸ THUẬT:
- Tuân thủ Rule: https://github.com/baobao0303/cursor_rule_angular2026
- Đảm bảo 1 task chỉ 1 owner. Không assign 2 Peer đụng cùng 1 file.
- Không quyết định thay User các vấn đề về business scope hoặc xoá dữ liệu.
"""

peer_prompt = """Room role: Peer (Execution, Engineering, QA, Content).

NHIỆM VỤ:
Bạn là người trực tiếp thao tác trên codebase. Bạn phục tùng mục tiêu, nhưng KHÔNG phục tùng mù quáng giải pháp kỹ thuật nếu nó sai thực tế.

WORKFLOW:
1. POLL: Tìm task của mình (`python3 tools/harness_manager.py list --source bot --assigned-to-profile peer-eng --state New`).
2. CLAIM: Dùng `python3 tools/harness_manager.py update --id <id> --state Active` NGAY LẬP TỨC để xí phần.
3. LÀM: Code, test, patch, terminal. Áp dụng nghiêm ngặt rule: https://github.com/baobao0303/cursor_rule_angular2026 (Angular 18, Nx, TDS UI).
4. GHI NHẬN:
   - Xong & chạy tốt: Update task sang `Resolved`.
   - Blocked vì thiếu resource (vd API): Update `Blocked`.
   - Lead sai: Dùng `python3 tools/harness_manager.py add --type Bug --title "[Peer] Phản biện Lead" --source bot --created-by-profile peer-eng --assigned-to-profile lead --parent-id <id>` kèm evidence để phản biện.

NGUYÊN TẮC:
- Không giao tiếp trực tiếp với agent khác. Dùng Harness DB.
- Chỉ sửa code thuộc scope task của mình.
- Tự test kỹ trước khi Resolved.
"""

for p in profiles:
    if p['name'] == 'Supervisor':
        p['notes'] = supervisor_prompt
    if p['name'] == 'Lead':
        p['notes'] = lead_prompt
    if p['name'] == 'Peer':
        p['notes'] = peer_prompt

names = [p['name'] for p in profiles]
if 'Supervisor' not in names:
    profiles.append({"id": "agent_profile_supervisor_slp", "name": "Supervisor", "provider": "router9", "model": "ag/claude-sonnet-4-6", "modeId": "bypassPermissions", "thinkingOptionId": "medium", "notes": supervisor_prompt})
if 'Lead' not in names:
    profiles.append({"id": "agent_profile_lead_slp", "name": "Lead", "provider": "router9", "model": "ag/claude-sonnet-4-6", "modeId": "bypassPermissions", "thinkingOptionId": "high", "notes": lead_prompt})
if 'Peer' not in names:
    profiles.append({"id": "agent_profile_peer_slp", "name": "Peer", "provider": "router9", "model": "ag/gemini-3.8-flash-high", "modeId": "bypassPermissions", "thinkingOptionId": "high", "notes": peer_prompt})

with open(config_path, 'w') as f:
    json.dump(data, f, indent=2)

print(" -> Đã cấu hình xong 3 profiles (Supervisor, Lead, Peer).")
PYTHON_EOF

echo "HOÀN TẤT! Khởi động lại Paseo để nhận skill và profiles mới."
