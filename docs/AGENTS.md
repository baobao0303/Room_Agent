# docs/AGENTS.md - Specification & Domain Modeling Directives

Chỉ thị dành cho Agent phân tích & thiết kế (Lead BA, Peer BA, Lead Design, Peer Design) khi làm việc trong thư mục `docs/`.

---

## 1. Cấu trúc đặc tả
Mọi dự án nằm trong `docs/spec/<project-name>/` với 3 phân vùng độc lập:
- `ba/`: Tài liệu User Stories, Acceptance Criteria (BDD/Gherkin).
- `design/`: Tài liệu UI/UX specs, Figma token mapping, CSS utilities.
- `dev/`: Tài liệu Architecture specs, API contracts, DTO schemas.

---

## 2. Kỹ năng áp dụng
1. **Business Analysis (BA)**:
   - Sử dụng `mattpocock-skills/skills/engineering/grill-with-docs/SKILL.md` để phỏng vấn sâu và làm rõ yêu cầu.
   - Chuẩn hóa mô hình nghiệp vụ qua `mattpocock-skills/skills/engineering/domain-modeling/SKILL.md`.
   - Chuyển thảo luận thành tài liệu đặc tả qua `mattpocock-skills/skills/engineering/to-spec/SKILL.md`.
   - Đồng bộ User Stories lên Harness qua `tools/harness_manager.py add ...`.
2. **UI/UX Design**:
   - Sử dụng `ui-lib-figma/SKILL.md` để mapping component Figma sang UI Angular và tra cứu color tokens.
