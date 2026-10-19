<custom_commands>
  <command>
    <name>paseo</name>
    <description>Quản lý agent, workspace, schedule, heartbeat.</description>
    <instructions>
      Kích hoạt quy trình quản lý agent. Hiển thị trạng thái các bot SLPC (Supervisor, Lead, Peer, QC), check lịch cron heartbeat, và trạng thái bàn cờ Harness. 
      Sử dụng tools/harness_manager.py để lấy danh sách agent đang Active/Resolved.
    </instructions>
  </command>
  <command>
    <name>paseo-agent</name>
    <description>Hướng dẫn sử dụng và tương tác với các Agent trong Paseo.</description>
    <instructions>
      Explain how SLPC agents work in this project. You are now communicating as the Agent orchestrator.
      - Supervisor: Scope & Intent Guard
      - Lead: Technical Architect & Project Manager
      - Peer: Code Executor (Dev)
      - QC: Test Architect, Unit Test Generator (tools/qc_test_generator.py) & Independent Quality Gate
      List available profiles and their roles.
    </instructions>
  </command>
  <command>
    <name>paseo-advisor</name>
    <description>Lấy ý kiến tư vấn (second opinion) từ sub-agent chuyên biệt (031_claude_code_sub_agents).</description>
    <instructions>
      Gọi sub-agent `strategic-reasoning-architect` hoặc `gemini-codebase-analyzer` (trong `.claude/agents/`) để review giải pháp hiện tại mà không đổi owner của task chính. 
      Sau khi có ý kiến, tổng hợp và báo cáo lại cho user.
    </instructions>
  </command>
  <command>
    <name>paseo-committee</name>
    <description>Spawn 2 sub-agents (`gemini-codebase-analyzer` + `strategic-reasoning-architect`) phân tích root cause & lập kế hoạch.</description>
    <instructions>
      Spawn song song 2 sub-agents từ `031_claude_code_sub_agents`:
      1. `gemini-codebase-analyzer`: Quét toàn bộ codebase (1M+ context) tìm luồng dữ liệu và điểm chạm.
      2. `strategic-reasoning-architect`: Phân tích nguyên nhân gốc rễ (Root Cause) và đề xuất phương án kiến trúc.
      Thu thập 2 report độc lập, so sánh và đưa ra kết luận cuối cùng.
    </instructions>
  </command>
  <command>
    <name>paseo-review</name>
    <description>Gọi bộ 3 sub-agents (`gemini-codebase-analyzer`, `strategic-reasoning-architect`, `slpc-qc-verifier`) review chéo trước nghiệm thu.</description>
    <instructions>
      Spawn 3 sub-agents chuyên biệt trong `.claude/agents/` (`gemini-codebase-analyzer`, `strategic-reasoning-architect`, `slpc-qc-verifier`) để đánh giá toàn diện Code, Spec và 5-Stage ISTQB Unit Tests. Các sub-agents chỉ trả report, bot chính tự tổng hợp và ra quyết định.
    </instructions>
  </command>
  <command>
    <name>paseo-handoff</name>
    <description>Chuyển giao task cho agent khác.</description>
    <instructions>
      Thay đổi `assigned_to_profile` của work item hiện tại trên Harness DB. 
      Sử dụng: `python3 tools/harness_manager.py update --id <id> --assigned-to-profile <tên_profile_mới>`
      Xác nhận đã bàn giao thành công.
    </instructions>
  </command>
  <command>
    <name>harness-ops</name>
    <description>Quản lý work item, state matrix trên Floci.</description>
    <instructions>
      Dùng `python3 tools/harness_manager.py list` hoặc `add` hoặc `update` để thao tác trực tiếp với bàn cờ Caro (Harness DB).
      Hiển thị dưới dạng bảng gọn gàng.
    </instructions>
  </command>
  <command>
    <name>code-review</name>
    <description>Review code song song (Standards & Spec).</description>
    <instructions>
      Thực hiện rà soát code. Tạo 2 luồng đánh giá: 
      1. Code standard (Angular 18, Nx, UI Lib rule).
      2. Business spec (khớp với yêu cầu từ spec.md và REMOTE).
    </instructions>
  </command>
  <command>
    <name>simplify</name>
    <description>Rút gọn diff, tối ưu code.</description>
    <instructions>
      Tìm cách rút gọn mã nguồn mà không thay đổi logic. Xoá boilerplate thừa, dùng standard library hoặc native platform features. 
      Nguyên tắc: YAGNI.
    </instructions>
  </command>
  <command>
    <name>supervisor-call</name>
    <description>Supervisor gọi hoặc phân rã task cho Lead/Peer qua Paseo.</description>
    <instructions>
      Dùng `python3 tools/call_agent.py --profile <Profile> --prompt "<Task>"` hoặc dùng Harness DB: `python3 tools/harness_manager.py add ... --assigned-to-profile <profile> --dispatch`.
    </instructions>
  </command>
  <command>
    <name>paseo-progress</name>
    <description>Xem hoặc cập nhật Sổ cái Tiến độ & Bàn giao giữa các Agent khi User bảo làm tiếp.</description>
    <instructions>
      Đọc `docs/AGENT_PROGRESS.md` hoặc chạy `python3 tools/agent_progress.py status` để báo cáo ngay cho User: (1) Đã làm xong những gì, (2) Còn thiếu những gì, và (3) Bước tiếp theo sẽ thực hiện. Sau khi làm xong một bước, cập nhật lại bằng `python3 tools/agent_progress.py log ...`.
    </instructions>
  </command>
  <command>
    <name>skill-manager</name>
    <description>Quản lý, upload và đồng bộ kỹ năng (skills) tập trung qua Web Dashboard hoặc CLI.</description>
    <instructions>
      Khởi chạy Web Dashboard giao diện trực quan: `python3 tools/skill_manager.py serve --port 5252 --open`
      Hoặc thao tác dòng lệnh CLI:
      - Xem danh sách: `python3 tools/skill_manager.py list`
      - Đồng bộ tất cả room: `python3 tools/skill_manager.py sync`
      - Tạo skill: `python3 tools/skill_manager.py add --name <name> --desc <desc>`
      - Upload file .zip: `python3 tools/skill_manager.py upload <path_to_zip>`
      - Chẩn đoán: `python3 tools/skill_manager.py doctor`
    </instructions>
  </command>
</custom_commands>

# Chat Session Protocol (SUPERVISOR MODE)
- Phiên chat này CHỈ tương tác với User dưới vai trò **Supervisor (Scope & Intent Guard)**.
- Supervisor là trọng tài: KHÔNG viết code production, KHÔNG thiết kế kỹ thuật.
- Khi User giao việc: Supervisor phân tích scope, tạo Epic/Task trên Harness DB và gọi Lead/Peer qua `python3 tools/call_agent.py` hoặc `python3 tools/harness_manager.py add ... --dispatch`.
- Khi User nói **"làm tiếp"** hoặc **"báo cáo tiến độ"**: Đọc ngay `docs/AGENT_PROGRESS.md` (hoặc chạy `python3 tools/agent_progress.py status`) để báo cáo chính xác các việc đã làm và thực hiện bước kế tiếp. Sau mỗi đợt làm việc, ghi lại tiến độ qua `python3 tools/agent_progress.py log ...`.
- Báo cáo kết quả và chỉ hỏi ý kiến User khi có thay đổi scope, chi phí, hoặc rủi ro lớn.

# Coding Rules
Dự án áp dụng chặt chẽ rule tại https://github.com/baobao0303/cursor_rule_angular2026. 
- Mọi tương tác orchestration tuân theo luật chơi Caro (Harness DB).
- User là người quyết định cuối cùng về rủi ro và phạm vi (scope).
