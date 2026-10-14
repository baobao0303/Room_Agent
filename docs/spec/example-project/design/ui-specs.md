# UI/UX & Design Specification: Example Project

## 1. Design System & Theme
- **Theme Preset**: `default` / `blue`
- **Component Library**: `tds-ui` Angular Components

## 2. Component Mapping (Figma to TDS-UI)

| UI Element | TDS UI Component / Module | Utility & Styling Classes |
| :--- | :--- | :--- |
| Nút thêm mới | `button[tds-button]` (`TDSButtonModule`) | `color="primary"`, `size="md"` |
| Bảng dữ liệu | `tds-data-table` (`TDSDataTableModule`) | `tds-table-bordered` |
| Tìm kiếm | `tds-form-field` + `input[tds-input]` | `tds-input-search` |
| Phân trang | `tds-pagination` (`TDSPaginationModule`) | `[tdsPageSize]="10"` |
| Bộ lọc trạng thái | `tds-select` (`TDSSelectModule`) | Multi-select / Single |
| Avatar người dùng | `tds-avatar` (`TDSAvatarModule`) | `size="sm"` |
