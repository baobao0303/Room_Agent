# Business Analysis Specification: Example Project

## 1. Overview & Business Goal
- **Mục tiêu**: Xây dựng module quản lý người dùng chuẩn hóa.
- **Phạm vi**: Xem danh sách, tìm kiếm, tạo mới và phân quyền người dùng.

## 2. User Stories & Acceptance Criteria

### US-01: Quản lý danh sách người dùng
- **Là**: Quản trị viên hệ thống.
- **Tôi muốn**: Xem danh sách tất cả người dùng kèm phân trang và bộ lọc trạng thái.
- **Để**: Kiểm soát và theo dõi tài khoản trong hệ thống.

**Acceptance Criteria (AC)**:
1. Hiển thị bảng dữ liệu gồm: ID, Avatar, Họ tên, Email, Vai trò, Trạng thái (Active/Inactive), Ngày tạo.
2. Hỗ trợ phân trang: Mặc định 10 dòng/trang, tùy chọn 20/50/100.
3. Hỗ trợ tìm kiếm realtime theo Họ tên hoặc Email (debounce 300ms).
4. Có bộ lọc Dropdown theo Trạng thái và Vai trò.
