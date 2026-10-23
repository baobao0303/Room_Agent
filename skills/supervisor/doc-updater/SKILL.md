---
name: doc-updater
description: "Synchronize, format, and update project specifications, architecture documents, and skill catalogs across docs/spec/ and .agents/skills/."
---

# Documentation & Specification Updater Skill (`doc-updater`)

Bộ kỹ năng chuyên biệt cho các Agent (Lead BA, Lead Design, Lead Dev, Supervisor) dùng để cập nhật, đồng bộ và chuẩn hóa tài liệu kỹ thuật, đặc tả nghiệp vụ và danh mục skills trong workspace.

---

## 1. When to Use
Kích hoạt skill này khi:
- **Lead BA / Peer BA**: Cần cập nhật tài liệu nghiệp vụ, User Stories hoặc Acceptance Criteria vào `docs/spec/<project>/ba/`.
- **Lead Design / Peer Design**: Cần cập nhật danh mục token màu, component mapping hoặc UI/UX spec vào `docs/spec/<project>/design/`.
- **Lead Dev / Peer Dev**: Cần cập nhật API contracts, database schema, DTOs, hoặc tài liệu kiến trúc vào `docs/spec/<project>/dev/`.
- **Supervisor**: Cần cập nhật tài liệu handoff phiên làm việc hoặc báo cáo kiến trúc tổng quan.
- Bất kỳ Agent nào khi hoàn thành một tính năng mới cần cập nhật `README.md` và `AGENTS.md`.

---

## 2. Standard Document Structures

### A. Cấu trúc tài liệu BA (`docs/spec/<project>/ba/<task>-spec.md`)
```markdown
# Business Specification: [Task Name]

## 1. Overview & Business Value
- **Goal**: [Mục tiêu nghiệp vụ]
- **Target Users**: [Đối tượng sử dụng]

## 2. User Story (BDD)
As a [User Role],
I want [Action / Goal],
So that [Business Value].

## 3. Acceptance Criteria (AC)
- [ ] AC1: [Điều kiện nghiệm thu 1]
- [ ] AC2: [Điều kiện nghiệm thu 2]
```

### B. Cấu trúc tài liệu Design (`docs/spec/<project>/design/<task>-ui.md`)
```markdown
# UI/UX Specification: [Task Name]

## 1. TDS UI Component Mapping
| Figma Component | TDS Component | TDS Module | Class Utilities |
|---|---|---|---|
| Primary Button | `button[tds-button]` | `TDSButtonModule` | `color="primary"` |

## 2. Color Tokens
- Theme Preset: `default` / `blue`
- Primary: `bg-tds-color-primary-500-light`
```

### C. Cấu trúc tài liệu Dev (`docs/spec/<project>/dev/<task>-arch.md`)
```markdown
# Technical Architecture: [Task Name]

## 1. Data Transfer Objects (DTO)
```typescript
export interface ExampleDto {
  id: string;
  name: string;
}
```

## 2. API Endpoints & State Management
- `GET /api/v1/resource`: Fetch list
```

---

## 3. Automation Scripts
Chạy script tự động cập nhật và đồng bộ cấu trúc tài liệu:
```bash
python3 tools/doc_sync.py
```
