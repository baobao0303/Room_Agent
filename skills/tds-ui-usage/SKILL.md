---
name: tds-ui-usage
description: "Skill for developers using the tds-ui Angular component library. Helps find components, generate usage examples, troubleshoot issues. Use when a developer asks about tds-ui components, imports, or usage patterns."
---

# tds-ui Usage Skill

Help developers find, understand, and use tds-ui components in their Angular applications.

## When to Use

Invoke this skill when:
- Developer needs to install/setup tds-ui in a project (first-time integration)
- Developer asks about any tds-ui component (by name, selector, or class)
- Developer asks how to accomplish a UI task using tds-ui
- Developer needs import paths, inputs/outputs, or usage examples
- Developer has issues with a tds-ui component (troubleshooting)
- Developer mentions selectors like `tds-*`, `[tds-*]`, class names like `TDS*`
- Developer asks "how to" do something that involves tds-ui

## Language

- **Output to developer: Vietnamese (có dấu đầy đủ)**
- Code examples: English
- This file (instructions): English

## Commands

### /tds-find

Search for tds-ui components by name, feature, or use case.

**Usage:**
```
/tds-find modal
/tds-find dropdown with search
/tds-find form validation
```

**Implementation:**
1. Read `reference/components-index.md` to get full component catalog
2. Match query against: component name, selector, description, features
3. If a match is found in `reference/docs/{component}.md`, read it for more detail
4. Return results in this format (Vietnamese):

```
Kết quả tìm kiếm: "<query>"

→ Phù hợp nhất: TDS{Xxx}Module
  Import: import { TDS{Xxx}Module } from 'tds-ui/{xxx}';
  Selector: <tds-{xxx}>
  Mô tả: <mô tả ngắn gọn>

  Ví dụ nhanh:
  <tds-{xxx} [tdsSize]="'md'">...</tds-{xxx}>

Các lựa chọn khác:
  • TDS{Yyy}Module — <mô tả ngắn>
  • TDS{Zzz}Module — <mô tả ngắn>
```

**Red flags:**
- If no match found, suggest closest alternatives
- If query is too vague, ask developer to be more specific

### /tds-how

Get a guided code example for a specific task using tds-ui components.

**Usage:**
```
/tds-how form with validation
/tds-how table with pagination
/tds-how confirm dialog before delete
```

**Implementation:**
1. Parse the task intent
2. Check `recipes/` directory for a matching recipe file
3. If recipe found → read it and return the content
4. If no recipe → combine info from relevant `reference/docs/*.md` files
5. Return in this format (Vietnamese):

```
## <Tiêu đề task>

### 1. Import
import { TDS{Xxx}Module } from 'tds-ui/{xxx}';
import { TDS{Yyy}Module } from 'tds-ui/{yyy}';

### 2. Code
<working code example — full component template + TypeScript>

### 3. Giải thích
• Component A dùng để...
• Component B kết hợp với A bằng cách...

### Tips
• Tip quan trọng
• Xem thêm: reference/docs/{xxx}.md
```

**Red flags:**
- If task requires a component not in docs, note it and suggest checking the library directly
- If task is ambiguous, ask for clarification before generating code

## Auto-detection

When the developer mentions tds-ui without using a command, Claude should still help.

### Auto-respond (no command needed)

Trigger when developer:
- Mentions install: "cài tds-ui", "install tds-ui", "setup tds-ui", "how to add tds-ui to project"
- Mentions a selector: `tds-button`, `tds-select`, `[tds-tooltip]`, etc.
- Mentions a class: `TDSModalService`, `TDSButtonComponent`, `TDSSelectModule`, etc.
- Asks about import: "import tds-ui/...", "sao import không được"
- Asks a simple question about a specific component
- Mentions a CSS class: `tds-color-*`, `tds-theme-*`, `tds-custom-scroll`, `tds-panel-scroll`
- Asks about styling/theme: "how to change theme", "tds color classes", "cách đổi theme"

**Response style:** Short and direct. Include import + quick code snippet. No "Giải thích" or "Tips" sections for simple questions.

Example auto-response:
```
Import TDSButtonModule từ 'tds-ui/button':

import { TDSButtonModule } from 'tds-ui/button';

@Component({
  standalone: true,
  imports: [TDSButtonModule],
  template: `<button tds-button color="primary">OK</button>`
})
```

### Suggest command

When developer's question is complex:
- Needs multiple components → suggest `/tds-how`
- Needs to find the right component → suggest `/tds-find`

### Do NOT intervene

- Developer talks about general UI not related to tds-ui
- Developer is working on code that doesn't use tds-ui
- Developer is having a conversation unrelated to the library

## Reference Data

This skill uses:
- `reference/install-guide.md` — Setup tds-ui in Angular 18 project (install, Tailwind, styles, i18n, verify)
- `reference/components-index.md` — Full component catalog (~78 components)
- `reference/naming-conventions.md` — How to read tds-ui APIs
- `reference/import-guide.md` — Import patterns and service injection
- `reference/docs/*.md` — Per-component documentation (79 files)
- `recipes/*.md` — Task-oriented guides combining multiple components
- `troubleshooting.md` — Common issues and fixes
- `reference/css-utilities.md` — CSS utility classes, themes, scrollbar styles

## Important Notes

- First-time setup: see `reference/install-guide.md` before importing components
- Import **Module** (e.g., `TDSButtonModule`), not individual components
- Some components have special import paths — check `reference/import-guide.md`
- Services like `TDSMessageService` are `providedIn: 'root'`, inject directly
- Services like `TDSModalService` require importing the module first
- Not all inputs/outputs have the `tds` prefix — always check per-component docs

## For Other Skills

This skill exposes interfaces for other skills to use:
- `/tds-find` — Find tds-ui component by type/feature
- `/tds-how` — Generate code for UI tasks
- `reference/docs/*.md` — Per-component API documentation
- `recipes/*.md` — Multi-component task guides

`tds-ui-design` skill uses this skill for component lookup and code generation.
Future `tds-ui-figma` skill will call this skill to map Figma designs to tds-ui code.
