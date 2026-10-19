# Task #888: Screen 3 - Behavior Events Toggle & Form Field Mapping (`AC-MAP-05`, `AC-MAP-06`)

- **Files**: `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/behavior-form-mapping/behavior-form-mapping.component.{ts,html,scss,spec.ts}`
- **Requirements**:
  1. **4-Step Progress Stepper & Sub-navigation Tabs (`AC-MAP-05`)**:
     - Hiển thị 4 bước: `1. Chưa cấu hình` (`UNCONFIGURED`) ➔ `2. Đã cấu hình chung` (`GENERAL_DONE`) ➔ `3. Đang mapping` (`0/2 form đã map xong`, `MAPPING_IN_PROGRESS`) ➔ `4. Hoàn tất` (`COMPLETED`), hỗ trợ `getStepState` và `onSelectStep`.
     - Hiển thị 3 tab điều hướng con: `Cấu hình chung` (`general`), `Sự kiện hành vi (4)` (`behavior`, `behaviorEventsCount`), `Lịch sử hoạt động` (`history`) qua `onSelectSubTab`.
  2. **Behavior Events Table & Save-to-Profile Toggle (`AC-MAP-05`)**:
     - Hiển thị 4 sự kiện hành vi nhận về: `Gửi form` (`AutoFormSubmit`, 8 lượt), `Xem trang` (`PageView`, 3.281 lượt), `Nhấp chuột` (`AutoClick`, 2.089 lượt), `Tỷ lệ đọc trang` (`ScrollDepth`, 711 lượt), tổng `6.089` lượt sự kiện (`totalBehaviorEventOccurrences`, `enabledBehaviorEventsCount`, `formatNumber`, `trackByEventType`).
     - Checkbox `Lưu vào Hồ sơ KH` cập nhật tức thì qua `FieldMappingService.toggleBehaviorEvent(eventType)` (`onToggleBehaviorEvent`, `onSetBehaviorEventState`) và nút `Hoàn tất cấu hình` (`onCompleteBehaviorConfig`).
  3. **Detected Web Forms & Form Field Mapping Detail (`AC-MAP-06`)**:
     - Danh sách 2 form đã ghi nhận (`detectedForms`, `mappedFormsCount`, `mappedFormsProgressText`, `isFormFullyMapped`, `getMappedFieldsCount`, `getFormListSubmittedAt`, `trackByFormId`): `Form liên hệ` (`/lien-he.html`, `FORM-01`, 4 trường, 3/4 trường đã map) và `Form đăng ký dùng thử` (`/dang-ky-dung-thu.html`, `FORM-02`, 3 trường, 3/3 trường đã map) với nút `[Cấu hình mapping]` (`onSelectForm`).
     - Màn hình chi tiết Mapping Form liên hệ (`activeForm`, `onUpdateFormField`, `onCdpFieldChange`, `onNormalizationRuleChange`, `onConfidenceChange`, `getSuggestedRuleForCdpField`, `formatSampleValue`, `trackBySourceField`):
       - `form.tds-input-1` (`"0969733325"`) ➔ `phone` · `CH-SDT` · `Cao`
       - `form.tds-input-2` (`"Tấn "`) ➔ `name` · `CH-TEN` · `Cao`
       - `form.tds-input-3` (`"tansida@gmail.com"`) ➔ `email` · `CH-EMAIL` · `Cao`
       - `form.tds-input-4` (`"Quận 7"`) ➔ `null` (*Chưa chọn*)
       - Nút `‹ Quay lại` (`onBackToFormList`) và `[Lưu thay đổi]` (`onSaveFormMapping`).
