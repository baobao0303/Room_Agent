# Supervisor Skills Taxonomy - 4 Trụ Cột Vận Hành SLPC

Toàn bộ 23 skills của Supervisor (đã tích hợp đầy đủ năng lực PM) được phân loại thành 4 nhóm theo từng kịch bản sử dụng chuẩn:

```text
profiles/supervisor/skills/
├── intake-and-scope/           # 1. Tiếp nhận ý định, phân loại & thẩm định phạm vi
│   ├── systemone/              # Chấm điểm Feasibility/Alignment <50ms qua Kev System One
│   ├── ba/                     # Senior Business Analyst, đặc tả BDD & Acceptance Criteria
│   ├── to-spec/                # Chuyển requirements thô thành specification chuẩn
│   ├── to-tickets/             # Phân rã story thành các ticket công việc
│   ├── to-questionnaire/       # Sinh bộ câu hỏi làm rõ khúc mắc
│   ├── triage/                 # Phân luồng khẩn cấp bug & out-of-scope
│   ├── wait-what/              # Nhận diện giả định ngầm, làm rõ mơ hồ
│   ├── grilling/               # Phản biện dồn dập (stress-test) ý tưởng
│   ├── grill-me/               # Phỏng vấn stress-test trực tiếp với User
│   └── grill-with-docs/        # Phản biện đối chiếu tài liệu dự án
│
├── architecture-and-design/    # 2. Khảo sát kiến trúc & thử nghiệm ranh giới
│   ├── domain-modeling/        # Chuẩn hóa thuật ngữ miền (GLOSSARY) & lập Architecture Decision Record (ADR)
│   ├── prototype/              # Dựng mockup/throwaway prototype kiểm tra luồng logic
│   └── wayfinder/              # Khảo sát cấu trúc file, thư mục & định vị điểm chạm
│
├── loop-and-orchestration/     # 3. Kỹ thuật vòng lặp tự hành & điều phối đa Agent
│   ├── loop-engineering/      # [TRỌNG TÂM] Thiết kế Closed Loop, Maker-Checker, Mechanical Stop Gate, Turn Ceiling <= 3-5
│   ├── loop-me/                # Kích hoạt vòng lặp tự hành có kiểm soát cho tác vụ
│   ├── workflow-launch-exec/   # Khởi chạy pipeline tự hành xuyên suốt
│   ├── chief-of-staff/         # Sắp xếp ưu tiên Backlog & khống chế Concurrency Ceiling
│   ├── handoff/                # Giao thức đóng gói ngữ cảnh chuyển giao
│   ├── claude-handoff/         # Chuyển giao ngữ cảnh cho Claude Sub-agents
│   └── paseo-handoff/          # Chuyển giao ngữ cảnh trong Paseo Daemon
│
└── governance-and-retro/       # 4. Quản trị vận hành, nghiệm thu & đúc kết
    ├── harness-manager/        # Quản lý SDLC Backlog, Work Items, Kev System One & FSM (baobao0303/harness)
    ├── harness2-orchestrator/  # Điều phối Google Research Harness² (arXiv:2610.14224, Core Recursion, Substrates)
    ├── slpc-control-center/    # Dashboard điều hành trạng thái 4 vai trò & nhịp tim
    ├── doc-updater/            # Đồng bộ cập nhật specs, architecture docs sau khi xong Epic
    └── retro/                  # Hồi tưởng sau sự cố, đúc kết bài học nạp vào Harness Learn Store
```

