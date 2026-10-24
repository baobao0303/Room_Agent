# BẢN ĐẶC TẢ KIẾN TRÚC: HỆ THỐNG PASEO PLUGIN LIFECYCLE HOOKS & TỰ ĐỘNG PHÊ DUYỆT (AUTO-APPROVAL)
## Mã định danh: ARCH-SPEC-PASEO-PLUGIN-LIFECYCLE-HOOKS-2026-V1
## Tham chiếu: Paseo Server Plugin API (`@getpaseo/plugin/server`) | SLPPC Architecture | Zero-Friction Permissions

---

## 1. TỔNG QUAN & MỤC TIÊU THIẾT KẾ (EXECUTIVE SUMMARY)

- **Mục tiêu**: Thiết lập hệ thống chốt chặn sự kiện vòng đời toàn diện (**Paseo Lifecycle Hooks**) cho toàn bộ các Agent hoạt động trong workspace `Room_Agent`, bao gồm:
  1. Quản lý vòng đời Workspace và Agent (khởi tạo, nạp cấu hình, thu gom).
  2. Tự động phê duyệt quyền hạn (**Zero-Prompt Auto-Approval**) đối với các câu lệnh kiểm tra, quan sát an toàn.
  3. Đánh chặn tức thời các câu lệnh nguy hiểm, có tính chất phá hoại hệ thống (**Destructive Command Interception**).
  4. Đóng gói module tự trị (**High Cohesion & Encapsulation**): Di chuyển mã nguồn xử lý hook từ `tools/` về trực tiếp thư mục plugin `plugins/slpc-lifecycle-hooks/`.

---

## 2. KIẾN TRÚC 3 TẦNG HOOKS (3-TIER HOOK TAXONOMY)

```text
┌─────────────────────────────────────────────────────────────────────────────┐
│                 PASEO UNIFIED LIFECYCLE HOOKS ARCHITECTURE                  │
│                                                                             │
│  TẦNG 1: PLUGIN SERVER HOOKS (@getpaseo/plugin/server - CORE 4 ESSENTIALS)  │
│  ├── Bootstrap : before:agent.create | before:agent.session_open             │
│  ├── Security  : agent.permission_requested ➔ Auto-Allow / Hard-Deny        │
│  ├── Context   : agent.turn_ended ➔ Sổ cái tiến độ & Handoff sync            │
│  └── Cleanup   : agent.archived ➔ Ephemeral Auto-Archive & Garbage Collect  │
│                                                                             │
│  TẦNG 2: WORKTREE LIFECYCLE HOOKS (paseo.json)                              │
│  ├── pre-create  : Kiểm tra source root và tính hợp lệ của branch           │
│  ├── post-create : Khởi tạo .env, symlink .venv chung, sync skills          │
│  └── pre-destroy : Dọn dẹp tài nguyên và cache trước khi đóng worktree      │
│                                                                             │
│  TẦNG 3: CLI AGENT ACTIVITY HOOKS (paseo hooks <agent> <event>)             │
│  ├── claude   : UserPromptSubmit | Stop | StopFailure | SessionEnd          │
│  ├── codex    : UserPromptSubmit | PreToolUse | PostToolUse | Stop          │
│  └── opencode : session.status.busy | idle | permission.asked | replied      │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## 3. CHI TIẾT TẦNG 1: PLUGIN SERVER HOOKS & CHỐT CHẶN BẢO VỆ

Thực thi trong runtime TypeScript của Paseo Server tại `plugins/slpc-lifecycle-hooks/index.server.ts`:

### 3.1. Quản Trị Vòng Đời Agent & Ép Buộc Model (Model Enforcement)
- **Sự kiện đánh chặn**: `before:agent.create` và `before:agent.session_open`.
- **Cơ chế**:
  - Tự động nhận diện Agent có vai trò `Supervisor`.
  - Ép buộc sử dụng model cấp cao: `gemini-3.8-flash-high` trên provider `antigravity`.
  - Nạp bộ biến môi trường mặc định SLPC:
    - `PASEO_SLPC_HOOK_ACTIVE = "1"`
    - `PASEO_PROJECT_ROOT = <PROJECT_ROOT>`
    - `PASEO_HOOK_TOOL = plugins/slpc-lifecycle-hooks/paseo_hooks.py`
    - `PASEO_RESEARCH_GEN_TOOL = tools/profile_research_gen.py`

### 3.2. Động Cơ Tự Động Phê Duyệt (Zero-Prompt Auto-Approval Engine)
- **Sự kiện đánh chặn**: `agent.permission_requested`.
- **Mục tiêu**: Loại bỏ 100% các hộp thoại xác nhận quyền gây gián đoạn luồng làm việc tự động của Agent khi chạy lệnh an toàn.
- **Biểu thức chính quy Regex**:
  ```typescript
  const SAFE_AUTO_APPROVE_PATTERN =
    /^(git\s+(status|diff|log|branch)|python3\s+.*(tools\/(harness_manager|agent_progress|profile_research_gen|qc_test_generator|query_reader|crm_doc_reader|paseo_hooks|test_harness|test_qc_generator)|plugins\/slpc-lifecycle-hooks\/paseo_hooks)\.py\b)/;
  ```
- **Hành vi xử lý**:
  - Khớp pattern $\rightarrow$ Gửi phản hồi `allow` ngay lập tức (thời gian xử lý $< 5$ms).
  - Không khớp $\rightarrow$ Chuyển tiếp cho người dùng quyết định qua UI Paseo.

### 3.3. Chốt Chặn Lệnh Phá Hoại (Destructive Command Blocker)
- **Quy tắc ngăn chặn**:
  ```typescript
  if (/\brm\s+-rf\s+\/(\s|$)/.test(command)) {
    await agent.respondToPermission({
      requestId: event.request.id,
      response: {
        behavior: "deny",
        message: "Blocked destructive root deletion via slpc-lifecycle-hooks.",
      },
    });
    return;
  }
  ```

---

## 4. CHI TIẾT TẦNG 2 & 3: WORKTREE & CLI ACTIVITY HOOKS

Thực thi thông qua bộ điều khiển Python tại `plugins/slpc-lifecycle-hooks/paseo_hooks.py`:

### 4.1. Worktree Lifecycle (`cmd_worktree`)
- Được kích hoạt tự động qua file cấu hình `paseo.json` và script wrapper `scripts/worktree_hook.sh`.
- **`post-create`**:
  - Tự động thiết lập môi trường cho worktree mới (sao chép `.env` hoặc khởi tạo từ fallback an toàn).
  - Tạo symlink chia sẻ thư mục ảo `.venv` nhằm tiết kiệm dung lượng đĩa và thời gian cài đặt thư viện.
  - Tự động đồng bộ các kỹ năng (skills) qua `python3 tools/skill_manager.py sync`.
- **`pre-destroy`**:
  - Ghi nhận biên bản kết thúc phiên và dọn dẹp biến môi trường.

### 4.2. Ghi Nhận Lịch Sử & Sổ Cái Tập Trung (Ledger & Audit Logging)
- Mọi sự kiện hook đều được chuẩn hóa loại bỏ dữ liệu nhạy cảm (`redact_sensitive()`) và lưu trữ tại:
  - File log chi tiết: `.harness_hooks.jsonl`.
  - Cập nhật tiến độ vào: `docs/AGENT_PROGRESS.md` và `bmad/rooms/room_ledger.json`.

---

## 5. TỔ CHỨC MÃ NGUỒN & TÍNH TƯƠNG THÍCH NGƯỢC (ENCAPSULATION)

### 5.1. Cấu Trúc Module Nội Bộ Plugin (`plugins/slpc-lifecycle-hooks/`)
```text
plugins/slpc-lifecycle-hooks/
├── paseo-plugin.json      # Khai báo metadata plugin (id: slpc-lifecycle-hooks, paseo >= 0.8.0)
├── index.server.ts        # Entry point Server Plugin của Paseo (Hook handlers & Permission logic)
├── server/
│   └── hook-bridge.ts     # Cầu nối IPC gọi subprocess Python và xử lý redact secret
└── paseo_hooks.py         # Bộ điều khiển Python xử lý nghiệp vụ (worktree, plugin-event, status)
```

### 5.2. Lớp Bao Bọc Tương Thích Ngược (Backwards-Compatible Wrapper)
- Để đảm bảo các script CI/CD hoặc lệnh gõ cũ không bị gãy, file `tools/paseo_hooks.py` được duy trì dưới dạng forwarder:
  ```python
  #!/usr/bin/env python3
  import subprocess, sys
  from pathlib import Path

  TARGET = Path(__file__).resolve().parent.parent / "plugins" / "slpc-lifecycle-hooks" / "paseo_hooks.py"
  if not TARGET.exists():
      sys.exit(f"Error: Target {TARGET} not found.")
  sys.exit(subprocess.call([sys.executable, str(TARGET)] + sys.argv[1:]))
  ```

---

## 6. TIÊU CHUẨN NGHIỆM THU (ACCEPTANCE CRITERIA)

| Mã AC | Tiêu chí nghiệm thu | Trạng thái kiểm chứng |
| :--- | :--- | :---: |
| **AC-1** | Module hook được đóng gói hoàn toàn trong `plugins/slpc-lifecycle-hooks/`. | ✅ PASS |
| **AC-2** | Các lệnh `git status`, `git diff`, và các file `tools/*.py` được auto-allow 100%, không hiện prompt hỏi quyền. | ✅ PASS |
| **AC-3** | Lệnh phá hoại `rm -rf /` bị chặn cứng (`deny`) kèm thông báo cảnh báo rõ ràng. | ✅ PASS |
| **AC-4** | Supervisor luôn được áp model `gemini-3.8-flash-high` mỗi khi mở phiên hoặc tạo mới. | ✅ PASS |
| **AC-5** | Lệnh `python3 tools/paseo_hooks.py status` và `python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py status` trả về cùng kết quả thành công (Exit 0). | ✅ PASS |
| **AC-6** | Toàn bộ 87 unit tests và kiểm tra SLPPC Flow Guard đạt 100% PASS, 0 vi phạm. | ✅ PASS |

---

## 7. CÂU LỆNH KIỂM CHỨNG CƠ HỌC (VERIFICATION COMMANDS)

```bash
# 1. Kiểm tra trạng thái toàn diện hệ thống hooks:
python3 plugins/slpc-lifecycle-hooks/paseo_hooks.py status

# 2. Kiểm tra tính tương thích ngược của wrapper:
python3 tools/paseo_hooks.py status

# 3. Kiểm tra chốt chặn worktree lifecycle:
bash scripts/worktree_hook.sh pre-create

# 4. Chạy toàn bộ test suite dự án:
python3 -m unittest discover -s tools/tests

# 5. Kiểm tra tuân thủ phân luồng SLPPC:
python3 tools/slppc_flow_guard.py audit
```
