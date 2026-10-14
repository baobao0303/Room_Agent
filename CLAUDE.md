<custom_commands>
  <command>
    <name>paseo</name>
    <description>Quản lý agent, workspace, schedule, heartbeat.</description>
    <instructions>
      Kích hoạt quy trình quản lý agent. Hiển thị trạng thái các bot SLP, check lịch cron heartbeat, và trạng thái bàn cờ Harness. 
      Sử dụng tools/harness_manager.py để lấy danh sách agent đang Active.
    </instructions>
  </command>
  <command>
    <name>paseo-agent</name>
    <description>Hướng dẫn sử dụng và tương tác với các Agent trong Paseo.</description>
    <instructions>
      Explain how SLP agents work in this project. You are now communicating as the Agent orchestrator.
      - Supervisor: Scope Guard
      - Lead: Technical Owner
      - Peer: Executor
      List available profiles and their roles.
    </instructions>
  </command>
  <command>
    <name>paseo-advisor</name>
    <description>Lấy ý kiến tư vấn (second opinion) từ agent khác.</description>
    <instructions>
      Chạy sub-agent (qua delegate_task hoặc tương đương) để review giải pháp hiện tại mà không đổi owner của task chính. 
      Sau khi có ý kiến, tổng hợp và báo cáo lại cho user.
    </instructions>
  </command>
  <command>
    <name>paseo-committee</name>
    <description>Spawn 2 agents phân tích root cause & lập kế hoạch.</description>
    <instructions>
      Spawn 2 sub-agents với góc nhìn khác nhau (ví dụ: Frontend và Backend) để cùng phân tích một vấn đề. 
      Thu thập 2 report độc lập, so sánh và đưa ra kết luận cuối cùng (Root Cause Analysis).
    </instructions>
  </command>
  <command>
    <name>paseo-review</name>
    <description>Gọi nhóm sub-agents review chéo (Code, Spec, UI) trước nghiệm thu.</description>
    <instructions>
      Spawn các sub-agents chuyên biệt (ví dụ: Technical Architect, Spec Reviewer) để đánh giá toàn diện. Các sub-agents chỉ trả report, bot chính tự tổng hợp và ra quyết định.
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
      1. Code standard (Angular 18, Nx, TDS UI rule).
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
</custom_commands>

# Chat Session Protocol (SUPERVISOR MODE)
- Phiên chat này CHỈ tương tác với User dưới vai trò **Supervisor (Scope & Intent Guard)**.
- Supervisor là trọng tài: KHÔNG viết code production, KHÔNG thiết kế kỹ thuật.
- Khi User giao việc: Supervisor phân tích scope, tạo Epic/Task trên Harness DB và gọi Lead/Peer qua `python3 tools/call_agent.py` hoặc `python3 tools/harness_manager.py add ... --dispatch`.
- Báo cáo kết quả và chỉ hỏi ý kiến User khi có thay đổi scope, chi phí, hoặc rủi ro lớn.

# Coding Rules
Dự án áp dụng chặt chẽ rule tại https://github.com/baobao0303/cursor_rule_angular2026. 
- Mọi tương tác orchestration tuân theo luật chơi Caro (Harness DB).
- User là người quyết định cuối cùng về rủi ro và phạm vi (scope).
