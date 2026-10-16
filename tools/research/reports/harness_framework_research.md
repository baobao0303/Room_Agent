# Technical Research: Harness Operating Framework (`baobao0303/harness`)

> Generated on 2026-10-08

## 1. Tổng quan & Bản chất của Harness
`harness` là một hệ điều hành cấp repository (Operating Framework) viết bằng **Rust**, quản lý toàn bộ vòng đời phát triển phần mềm (SDLC) và điều phối Autonomous AI Agents theo các tiêu chuẩn khắt khe (ISO/IEC 27001, DDD-COMPANY-2026).

---

## 2. Kiến trúc cốt lõi

### A. Kiến trúc Hexagonal / Layered (Crate `harness-cli`)
- **`domain/`**: Logic nghiệp vụ thuần túy, entities (`WorkItem`, `Story`, `Decision`, `Trace`, `Tool`), scoring entropy và luật validation (State Machine & Title Syntax).
- **`application/`**: Use cases (`HarnessService`), DTOs điều phối persistence và domain rules.
- **`infrastructure/`**: Tương tác ngoại vi: SQLite (`harness.db`, WAL mode), migration `001` -> `006`, Git worktree, Brownfield parser.
- **`interface/`**: CLI adapter qua `clap` (subcommands: `work-item`, `query`, `tool`, `migrate`).

### B. Cấu trúc Phân cấp Work Item (Portfolio Hierarchy)
```text
Epic (CPO) 
  └── Feature (BA) 
        ├── User Story (BA) ➔ Tasks, Bugs, Testcases
        └── Technical Story (Dev) ➔ Tasks, Bugs
```

### C. Quy tắc Cú pháp Bắt buộc (Title & Description Syntax)
- **User Story Title**: `[Module] – [Vai trò] có thể [hành động]`
- **User Story Description**: Chuẩn BDD:
  ```text
  As a [User Role],
  I want [Action / Goal],
  So that [Business Value].
  ```
- **Bug Title**: `[Module]: [Error message] when [reason]` (kèm Repro steps, Actual/Expected result, Severity).
- **Testcase Title**: `[Module]: [Expected result] when [condition]`

---

## 3. Hệ thống Chuyển đổi Trạng thái (State Machine Matrix)
- **User Story**: `New` ➔ `Accepted` (BA duyệt) ➔ `Active` (Dev kéo vào Sprint) ➔ `Resolved` (Pass PR, test) ➔ `Closed` (Sprint Review).
- **Task**: `New` ➔ `Active` ➔ `Resolved` ➔ `Closed`.
- **Bug**: `New` ➔ `Active` ➔ `Resolved` ➔ `Closed` (Tester verify).

---

## 4. Mục tiêu Xây dựng Tool Quản lý Harness cho Agent
Tạo một bộ wrapper tool Python/TS trực tiếp tương tác với `harness-cli` hoặc SQLite database `harness.db` giúp các Agent (BA, Design, Dev, Supervisor) tự động:
1. Tạo đúng cú pháp Work Item theo vai trò.
2. Kiểm tra State Machine hợp lệ trước khi chuyển trạng thái.
3. Truy vấn nhanh bảng phân cấp, truy vết ma trận kiểm thử (`query matrix`, `query stats`).
