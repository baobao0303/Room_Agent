# Documentation & Specifications Index

Thư mục lưu trữ toàn bộ tài liệu đặc tả nghiệp vụ (BA), thiết kế giao diện (Design), và kiến trúc kỹ thuật (Dev) được phân tách theo từng dự án độc lập.

## Cấu trúc chuẩn cho mỗi dự án:

```text
docs/spec/<tên-dự-án>/
├── ba/          # User Stories, Use Cases, Acceptance Criteria (Lead/Peer BA)
├── design/      # Wireframes, Component Mapping, Design Tokens (Lead/Peer Design)
└── dev/         # Kiến trúc API, Database Schema, Task Breakdown (Lead/Peer Dev)
```

---

## Danh sách dự án & tài liệu kiến trúc hiện có:
- [ai-agent-4-concepts-spec.md](file:///Users/bao312/Desktop/Room_Agent/docs/spec/ai-agent-4-concepts-spec.md): Đặc tả Kiến trúc Tổng thể 12 Khái niệm AI Agent & Đối soát Mã nguồn `Room_Agent` (`ARCH-SPEC-AI-AGENT-12-CONCEPTS-2026-V2`).
- [spec-gap-hardening-execution-and-skills-spec.md](file:///Users/bao312/Desktop/Room_Agent/docs/spec/spec-gap-hardening-execution-and-skills-spec.md): Đặc tả Kỹ thuật Tổng kết Quy trình Reverse Engineering 12 Khái niệm AI Agent, Hardening Runtime 4-Role SLPC & Ma trận Skills Thực thi (`ARCH-SPEC-GAP-HARDENING-EXECUTION-SKILLS-2026-V1`).
- [enterprise-ai-4-pillars-architecture-spec.md](file:///Users/bao312/Desktop/Room_Agent/docs/spec/enterprise-ai-4-pillars-architecture-spec.md): Bản đặc tả kỹ thuật Hệ thống AI Doanh nghiệp — 4 Trụ cột Kiến trúc Thực chiến (`ARCH-SPEC-ENTERPRISE-AI-4-PILLARS-2026-V1`: RAG, Multi-Agent, 3-Tier Memory, EVOS & Guardrails).
- `crm/`: Hệ thống ACME Enterprise Customer Engagement & CDP Frontend Monorepo (`projects/crm-fe`).
- `example-project/`: Dự án mẫu minh họa cấu trúc tài liệu.
