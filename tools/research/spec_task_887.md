# Task #887: Screen 2 - General Configuration & JSON Field Mapping Stepper (`AC-MAP-03`, `AC-MAP-04`)

- **Files**: `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/general-config/general-config.component.{ts,html,scss,spec.ts}`
- **Requirements**:
  1. **4-Step Progress Stepper (`AC-MAP-03`)**:
     - Hiển thị 4 bước: `1. Chưa cấu hình` (`UNCONFIGURED`) ➔ `2. Đã cấu hình chung` (`GENERAL_DONE`) ➔ `3. Đang mapping` (`0/2 form đã map xong`, `MAPPING_IN_PROGRESS`) ➔ `4. Hoàn tất` (`COMPLETED`), hỗ trợ `getStepState` và `onSelectStep`.
  2. **Sub-navigation Tabs (`AC-MAP-03`)**:
     - Hiển thị 3 tab điều hướng con: `[Tab] Cấu hình chung` (`general`), `[Tab] Sự kiện hành vi (4)` (`behavior`, `behaviorEventsCount`), `[Tab] Lịch sử hoạt động` (`history`) qua `onSelectSubTab`.
  3. **Connection Info & JSON Field Mapping Table (`AC-MAP-03`)**:
     - Chọn `Nguồn dữ liệu` (`onSourceTypeChange`) và `Tên trang liên kết` (`onConnectedPageNameChange`).
     - `Trang liên kết` ➔ `site_id` (Locked icon, không cho sửa/xóa).
     - `Loại sự kiện` ➔ `data.system_event_type` (Locked icon, không cho sửa/xóa).
     - `Mã sự kiện` ➔ `event_id` (Cho phép chọn path / sửa `onUpdateMappingField` / xóa `onRemoveMapping`).
     - `Thời gian nhận` ➔ `received_at` (Cho phép chọn path / sửa `onUpdateMappingField` / xóa `onRemoveMapping`).
     - Nút `+ Thêm trường` (`onAddMapping`) và `[Lưu cấu hình]` (`onSaveConfig`).
  4. **Sample JSON Payload Preview & Live Event Preview Table (`AC-MAP-04`)**:
     - Tích hợp `<wicx-json-viewer>` hiển thị JSON mẫu chuẩn syntax highlighting (`formattedSampleJson`, `syntaxTokens`, `availableJsonPaths`), hỗ trợ nhận đường dẫn từ sự kiện `(pathCopy)` (`onJsonPathCopied`), `(valueCopy)` (`onJsonValueCopied`) và nút `[Copy Payload]` (`copyFullPayload`) sao chép toàn bộ chuỗi JSON.
     - Bảng `Dữ liệu trả về sau cấu hình` (`displayedLiveEvents`, `formatReceivedTime`, `formatNumber`): hiển thị 10 bản ghi mới nhất kèm phân trang `Hiển thị 1-10 trên 7.505 bản ghi` (`paginationRangeText`, `goToPage`).
