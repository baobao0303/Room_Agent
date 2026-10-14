# UI/UX & Design Specification: Example Project

## 1. Design System & Theme
- **Theme Preset**: `default` / `blue`
- **Component Library**: `ui-lib` Angular Components

## 2. Component Mapping (Figma to UI-Lib)

| UI Element | UI Lib Component / Module | Utility & Styling Classes |
| :--- | :--- | :--- |
| Nút thêm mới | `button[ui-button]` (`UIButtonModule`) | `color="primary"`, `size="md"` |
| Bảng dữ liệu | `ui-data-table` (`UIDataTableModule`) | `ui-table-bordered` |
| Tìm kiếm | `ui-form-field` + `input[ui-input]` | `ui-input-search` |
| Phân trang | `ui-pagination` (`UIPaginationModule`) | `[uiPageSize]="10"` |
| Bộ lọc trạng thái | `ui-select` (`UISelectModule`) | Multi-select / Single |
| Avatar người dùng | `ui-avatar` (`UIAvatarModule`) | `size="sm"` |
