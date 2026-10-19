# Figma to tds-ui Component Map

Start with this map, then verify exact APIs through `tds-ui-usage` docs when implementing.

| Figma concept | tds-ui target | Import path |
|---|---|---|
| Button, primary, secondary, ghost | `tds-button` | `tds-ui/button` |
| Input, text field | `tds-input`, `tds-form-field` | `tds-ui/input`, `tds-ui/form-field` |
| Dropdown, select | `tds-select` | `tds-ui/select` |
| Modal, dialog | `TDSModalService`, modal module | `tds-ui/modal` |
| Toast, notification | `TDSMessageService` | `tds-ui/message` |
| Table, data grid | `tds-table` or data-table docs | `tds-ui/table`, verify docs |
| Tag, status chip | `tds-tag` | `tds-ui/tag` |
| Badge, count indicator | `tds-badge` | `tds-ui/badge` |
| Avatar | `tds-avatar` | `tds-ui/avatar` |
| Avatar with small channel icon/badge in TPage | `chatomni-picture-channel` with `sizeIcon` | Project component, TPage only |
| Spinner, loading | `tds-spinner` | `tds-ui/spinner` |
| Tooltip | `tds-tooltip` or tooltip directive | `tds-ui/tooltip` |
| Popover | `tds-popover` or popover directive | `tds-ui/popover` |
| Dropdown menu | dropdown directive/menu | `tds-ui/dropdown` |
| Switch, toggle | `tds-switch` | `tds-ui/switch` |
| Checkbox | `tds-checkbox` | `tds-ui/checkbox` |
| Radio group | `tds-radio` | `tds-ui/radio` |
| Date picker | `tds-date-picker` | `tds-ui/date-picker` |
| Pagination | `tds-pagination` | `tds-ui/pagination` |
| Upload | `tds-upload` | `tds-ui/upload` |
| Empty state | `tds-empty` | `tds-ui/empty` |
| Drawer, side panel | `tds-drawer` or drawer service | `tds-ui/drawer` |

## Table and Pagination

When the Figma design contains a table/data grid, also read `table-pagination-rules.md` before implementing. Default to page-index/page-size pagination when the API contract is not known yet, then switch only when the real API or UX proves another pattern.

## Rules

- Import modules from sub-paths only. Do not import from root `tds-ui`.
- Do not recreate a tds-ui primitive with raw HTML/CSS when a public component exists.
- Do not override tds-ui internals for colors, spacing, or radius; prefer component inputs and design tokens.
- If the Figma design uses a component not listed here, search `tds-ui-usage/reference/components-index.md` before choosing custom markup.


---
## 📚 Điều Hướng: TDS Figma Rules & Setup
- **Mục lục chính:** [[SKILL]]
◀️ **Trước:** [[figma-to-tds-ui-rules]] | ▶️ **Tiếp:** [[figma-framelink-mcp-setup]]
