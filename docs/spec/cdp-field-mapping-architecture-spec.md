# CDP ADMIN - FIELD MAPPING UI: TECHNICAL ARCHITECTURE, ROUTING & SIGNAL STATE SPECIFICATION

> **Document ID**: `ARCH-CDP-MAPPING-2026-V1`  
> **Parent Epic**: `#883 - [CDP-MAPPING] Field Mapping & Data Event Administration UI`  
> **Architecture Task**: `#884 - [Lead] Technical Architecture & Routing Design for CDP Field Mapping`  
> **Downstream Tasks**: `#885 (Peer - JSON Viewer Selection & Path Copy)`, `#886 (Peer - Overview Dashboard & Connected Pages)`, `#887 (Peer - General Config & JSON Stepper)`, `#888 (Peer - Behavior Events & Form Mapping)`, `#889 (Peer - Version History Diff & Rollback)`, `#890 (QC - 5-Stage ISTQB Test Suite)`  
> **Source SRS**: `docs/spec/cdp-field-mapping-ui-spec.md` (`SPEC-CDP-MAPPING-2026-V1`)  
> **Target Module**: `projects/wicx-crm-fe/apps/mfe-cdp` & `projects/wicx-crm-fe/libs/wicx-core`  
> **Author**: `Lead (Technical Architect & PM in SLPC)`

---

## 1. ARCHITECTURAL OVERVIEW & NAVIGATION HIERARCHY

### 1.1. Module Federation & Host Integration (`app-shell` ➔ `mfe-cdp`)
Trong kiến trúc Module Federation 2.0 (Rsbuild + Angular 18), `app-shell` nạp động remote `mfe-cdp` tại nhánh định tuyến `/:id/data-raw` (và redirect `/:id/customers/data-raw` ➔ `/:id/data-raw`). Bên trong `mfe-cdp`, phân hệ **Dữ liệu sự kiện (Event Data)** bao gồm 2 phân vùng chính:
1. **[Tab 1] Dữ liệu thô (`RawEventListComponent`)**: Danh sách sự kiện thô gửi về từ các connector (`path: ''` và `path: 'data-raw'`).
2. **[Tab 2] Mapping dữ liệu (`Field Mapping UI`)**: Hệ thống quản trị cấu hình ánh xạ sự kiện và form vào Hồ sơ khách hàng CDP (`path: 'field-mapping'` và các route con tương ứng với 4 màn hình chức năng).

### 1.2. Routing Architecture (`apps/mfe-cdp/src/app/remote-entry/entry.routes.ts`)
Thiết kế định tuyến `remoteRoutes` trong `projects/wicx-crm-fe/apps/mfe-cdp/src/app/remote-entry/entry.routes.ts` hỗ trợ cả điều hướng theo URL trực tiếp (Deep-linking) lẫn điều hướng theo Tab/State bên trong `FieldMappingOverviewComponent`:

```typescript
import { Route } from '@angular/router';
import { i18nResolver, provideWII18n } from '@wicx/core';
import { RawEventListComponent } from '../pages/data-raw/raw-event-list.component';

const cdpI18nProviders = provideWII18n({
  remoteName: 'mfe-cdp',
  modules: ['raw-event-data', 'cdp'],
});

export const remoteRoutes: Route[] = [
  {
    path: '',
    pathMatch: 'full',
    title: 'CDP.RAW_EVENT_DATA.TITLE',
    providers: cdpI18nProviders,
    resolve: { i18n: i18nResolver },
    component: RawEventListComponent,
  },
  {
    path: 'data-raw',
    title: 'CDP.RAW_EVENT_DATA.TITLE',
    providers: cdpI18nProviders,
    resolve: { i18n: i18nResolver },
    component: RawEventListComponent,
  },
  {
    path: 'field-mapping',
    title: 'CDP.FIELD_MAPPING.TITLE',
    providers: cdpI18nProviders,
    resolve: { i18n: i18nResolver },
    children: [
      {
        path: '',
        pathMatch: 'full',
        loadComponent: () =>
          import('../pages/field-mapping/components/event-overview/event-overview.component').then(
            (m) => m.EventOverviewComponent
          ),
      },
      {
        path: 'pages/:pageId/general',
        loadComponent: () =>
          import('../pages/field-mapping/components/general-config/general-config.component').then(
            (m) => m.GeneralConfigComponent
          ),
      },
      {
        path: 'pages/:pageId/behavior',
        loadComponent: () =>
          import('../pages/field-mapping/components/behavior-form-mapping/behavior-form-mapping.component').then(
            (m) => m.BehaviorFormMappingComponent
          ),
      },
      {
        path: 'pages/:pageId/forms/:formId/history',
        loadComponent: () =>
          import('../pages/field-mapping/components/version-history/version-history.component').then(
            (m) => m.VersionHistoryComponent
          ),
      },
    ],
  },
  {
    path: '**',
    redirectTo: '/error/not-found',
  },
];
```

---

## 2. COMPONENT FOLDER ORGANIZATION & SINGLE-OWNERSHIP MATRIX

### 2.1. Directory Structure (`projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping`)

```text
projects/wicx-crm-fe/
├── libs/wicx-core/src/libs/json-viewer/
│   ├── json-viewer.component.ts                           # [Task #885] 1-click JSON path copy & text selection
│   ├── json-viewer.component.html                         # [Task #885] Copy path button & segment DOM
│   ├── json-viewer.component.scss                         # [Task #885] user-select: text !important; cursor: text
│   └── json-viewer.component.spec.ts                      # [Task #885 / #890] Unit tests for AC-MAP-09, AC-MAP-10
└── apps/mfe-cdp/src/app/
    ├── remote-entry/
    │   └── entry.routes.ts                                # [Task #886] Route registration for field-mapping & children
    └── pages/field-mapping/
        ├── models/
        │   └── field-mapping.model.ts                     # [Task #886] Domain contracts, DTOs & Signal state interfaces
        ├── services/
        │   ├── field-mapping.service.ts                   # [Task #886] Angular Signals Store & Business Logic Service
        │   └── field-mapping.service.spec.ts              # [Task #886 / #890] Unit tests for AC-MAP-01..08
        └── components/
            ├── event-overview/                            # [Task #886] Screen 1: Overview KPI & Connected Pages
            │   ├── event-overview.component.ts
            │   ├── event-overview.component.html
            │   ├── event-overview.component.scss
            │   └── event-overview.component.spec.ts
            ├── general-config/                            # [Task #887] Screen 2: 4-Step Stepper & JSON Field Mapping
            │   ├── general-config.component.ts
            │   ├── general-config.component.html
            │   ├── general-config.component.scss
            │   └── general-config.component.spec.ts
            ├── behavior-form-mapping/                     # [Task #888] Screen 3: Behavior Events Toggle & Form Mapping
            │   ├── behavior-form-mapping.component.ts
            │   ├── behavior-form-mapping.component.html
            │   ├── behavior-form-mapping.component.scss
            │   └── behavior-form-mapping.component.spec.ts
            └── version-history/                           # [Task #889] Screen 4: Version Diff & 1-Click Rollback
                ├── version-history.component.ts
                ├── version-history.component.html
                ├── version-history.component.scss
                └── version-history.component.spec.ts
```

### 2.2. Single-Ownership File Isolation Matrix (One Task, One Owner)
Để đảm bảo không có bất kỳ xung đột ghi file (write conflict) nào khi nhiều `Peer` thực thi song song:

| Work Item | Owner | Exclusive Write Scope (Target Files) | Covered ACs |
| :--- | :--- | :--- | :--- |
| **Task #885 / Bug #1173 / Bug #1508 / Bug #2103** | `peer` | `libs/wicx-core/src/libs/json-viewer/json-viewer.component.{ts,html,scss,spec.ts}` | `AC-MAP-09`, `AC-MAP-10`, `Bug #1173`, `Bug #1508`, `Bug #2103` |
| **Task #886** | `peer` | `apps/mfe-cdp/src/app/remote-entry/entry.routes.ts`<br>`apps/mfe-cdp/src/app/pages/field-mapping/models/field-mapping.model.ts`<br>`apps/mfe-cdp/src/app/pages/field-mapping/services/field-mapping.service.{ts,spec.ts}`<br>`apps/mfe-cdp/src/app/pages/field-mapping/components/event-overview/event-overview.component.{ts,html,scss,spec.ts}` | `AC-MAP-01`, `AC-MAP-02` |
| **Task #887** | `peer` | `apps/mfe-cdp/src/app/pages/field-mapping/components/general-config/general-config.component.{ts,html,scss,spec.ts}` | `AC-MAP-03`, `AC-MAP-04` |
| **Task #888** | `peer` | `apps/mfe-cdp/src/app/pages/field-mapping/components/behavior-form-mapping/behavior-form-mapping.component.{ts,html,scss,spec.ts}` | `AC-MAP-05`, `AC-MAP-06` |
| **Task #889** | `peer` | `apps/mfe-cdp/src/app/pages/field-mapping/components/version-history/version-history.component.{ts,html,scss,spec.ts}`<br>`apps/mfe-cdp/src/app/remote-entry/entry.routes.ts` (route `pages/:pageId/forms/:formId/history`) | `AC-MAP-07`, `AC-MAP-08` |
| **Task #890** | `qc` | Chạy `tools/qc_test_generator.py --sync-harness` và kiểm thử nghiệm thu độc lập toàn bộ `*.spec.ts` của `#885..#889`, `#1173`, `#1508` và `#2103` | `AC-MAP-01..10`, `Bug #1173`, `Bug #1508`, `Bug #2103` |

---

## 3. DATA CONTRACTS & SIGNAL STATE MODELS (`models/field-mapping.model.ts` & `services/field-mapping.service.ts`)

### 3.1. Domain Data Contracts (`models/field-mapping.model.ts`)
Tuân thủ 100% mục 4 của `docs/spec/cdp-field-mapping-ui-spec.md`:

```typescript
export type TimeRangeCycle = 30 | 90 | 180;

export type ConfigurationStepStatus =
  | 'UNCONFIGURED'      // Bước 1: Chưa cấu hình
  | 'GENERAL_DONE'      // Bước 2: Đã cấu hình chung
  | 'MAPPING_IN_PROGRESS' // Bước 3: Đang mapping (0/2 form đã map xong)
  | 'COMPLETED';        // Bước 4: Hoàn tất

export interface ConnectedPageSummary {
  id: string;
  name: string;
  category: 'CENTRALFLOW' | 'SOCIAL_NETWORK';
  platformType: 'crm' | 'facebook' | 'zalo' | 'website';
  identifier: string; // page_id, site_id, zalo_id
  status: 'receiving' | 'paused' | 'error';
  totalEvents: number;
  identifiedCustomers: number;
  lastReceivedAt: string; // ISO date
}

export interface OverviewKpiMetrics {
  totalEvents: number;         // e.g. 9737
  activePagesCount: number;    // e.g. 4
  totalPagesCount: number;     // e.g. 4
  activePagesRatio: string;    // e.g. '4 / 4'
  identifiedCustomers: number; // e.g. 549
}

export interface JsonFieldMappingItem {
  cdpField: string;
  jsonPath: string;
  isLocked: boolean;
  description?: string;
}

export interface JsonFieldMappingConfig {
  pageId: string;
  sourceType: string;
  connectedPageName: string;
  mappings: JsonFieldMappingItem[];
  sampleJson: Record<string, any>;
}

export interface LivePreviewEventRecord {
  connectedPage: string;
  eventType: string;
  eventId: string;
  receivedAt: string;
}

export interface BehaviorEventConfig {
  eventType: string; // 'AutoFormSubmit' | 'PageView' | 'AutoClick' | 'ScrollDepth'
  eventName: string;
  eventCount: number;
  description: string;
  saveToCustomerProfile: boolean;
}

export type NormalizationRuleCode = 'CH-SDT' | 'CH-TEN' | 'CH-EMAIL' | null;
export type FieldConfidenceLevel = 'Cao' | 'Trung bình' | 'Thấp' | null;

export interface FormMappingItem {
  sourceField: string; // e.g. 'form.tds-input-1'
  sampleValue: string;
  cdpField: string | null; // e.g. 'phone' | 'name' | 'email'
  normalizationRule: NormalizationRuleCode;
  confidence: FieldConfidenceLevel;
}

export interface FormMappingDefinition {
  formId: string;          // e.g. 'FORM-01', 'FORM-02'
  formName: string;        // e.g. 'Form liên hệ', 'Form đăng ký dùng thử'
  pageUrl: string;         // e.g. '/lien-he.html', '/dang-ky-dung-thu.html'
  sourceCode?: string;     // e.g. 'WEB-01 · CRM'
  lastSubmittedAt: string;
  fields: FormMappingItem[];
}

export interface MappingVersionDiff {
  type: 'added' | 'modified' | 'unmapped';
  field: string;
  detail: string;
  note?: string;
}

export interface MappingVersionRecord {
  version: number;
  status: 'active' | 'archived';
  authorName: string;
  savedAt: string;
  changeCount: number;
  diffs: MappingVersionDiff[];
}
```

### 3.2. Reactive Signal Store (`services/field-mapping.service.ts`)
`FieldMappingService` (`@Injectable({ providedIn: 'root' })`) quản lý toàn bộ trạng thái bằng **Angular 18 Signals** (`signal`, `computed`) để chia sẻ xuyên suốt 4 màn hình mà không cần reload dữ liệu hay prop-drilling:

- **Core Signals**:
  - `readonly selectedCycleDays = signal<TimeRangeCycle>(30);`
  - `readonly searchQuery = signal<string>('');`
  - `readonly selectedPageId = signal<string>('p1');`
  - `readonly currentStepIndex = signal<number>(2);` (tương ứng Bước 3: `Đang mapping (0/2 form đã map xong)`)
  - `readonly connectedPages = signal<ConnectedPageSummary[]>(DEFAULT_CONNECTED_PAGES);`
  - `readonly jsonConfig = signal<JsonFieldMappingConfig>(DEFAULT_JSON_MAPPING_CONFIG);`
  - `readonly behaviorEvents = signal<BehaviorEventConfig[]>(DEFAULT_BEHAVIOR_EVENTS);`
  - `readonly detectedForms = signal<FormMappingDefinition[]>(DEFAULT_DETECTED_FORMS);`
  - `readonly activeFormId = signal<string | null>(null);`
  - `readonly versions = signal<MappingVersionRecord[]>(DEFAULT_VERSION_RECORDS);`
  - `readonly selectedVersionNumber = signal<number>(3);`

- **Computed Selectors**:
  - `readonly kpiSummary = computed<OverviewKpiMetrics>(() => this.getKpiSummary());`
    - Tính tổng `totalEvents = 9737`, `activePagesRatio = '4 / 4'`, `identifiedCustomers = 549`.
  - `readonly filteredPages = computed<ConnectedPageSummary[]>(() => this.filterConnectedPages(this.searchQuery()));`
  - `readonly centralFlowPages = computed(() => this.filteredPages().filter(p => p.category === 'CENTRALFLOW'));`
  - `readonly socialNetworkPages = computed(() => this.filteredPages().filter(p => p.category === 'SOCIAL_NETWORK'));`
  - `readonly selectedVersion = computed(() => this.versions().find(v => v.version === this.selectedVersionNumber()) ?? this.versions()[this.versions().length - 1]);`

- **State Mutation & Business Rules Methods**:
  1. `getKpiSummary(): OverviewKpiMetrics` (`AC-MAP-01`)
  2. `filterConnectedPages(query: string): ConnectedPageSummary[]` (`AC-MAP-02`): Lọc tức thì không phân biệt hoa thường theo `name`, `identifier` (`site_id`, `page_id`, `zalo_id`), hoặc `category`.
  3. `validateJsonMappings(config: JsonFieldMappingConfig): boolean` (`AC-MAP-03`): Kiểm tra 2 trường bắt buộc `site_id` (`Trang liên kết`) và `data.system_event_type` (`Loại sự kiện`) phải luôn tồn tại và có `isLocked === true`. Nếu bị mở khóa hoặc thiếu, ném lỗi `Error`.
  4. `addJsonFieldMapping(cdpField: string, jsonPath: string): void` & `removeJsonFieldMapping(index: number): void` (`AC-MAP-03`): Không cho phép xóa dòng có `isLocked === true`.
  5. `toggleBehaviorEvent(eventType: string): boolean` (`AC-MAP-05`): Đảo trạng thái `saveToCustomerProfile` tức thì cho `AutoFormSubmit`, `PageView`, `AutoClick`, `ScrollDepth`.
  6. `updateFormFieldMapping(formId: string, sourceField: string, patch: Partial<FormMappingItem>): FormMappingDefinition` (`AC-MAP-06`): Cập nhật `cdpField` (`phone`, `name`, `email`), `normalizationRule` (`CH-SDT`, `CH-TEN`, `CH-EMAIL`) và `confidence` (`Cao`, `Trung bình`, `Thấp`).
  7. `rollbackToVersion(targetVersionNumber: number, author?: string): MappingVersionRecord` (`AC-MAP-08`): Chuyển phiên bản `active` hiện tại sang `archived`, tạo một bản ghi phiên bản mới `version = maxVersion + 1` với `status: 'active'` sao chép `diffs` từ `targetVersionNumber` mà không xóa bất kỳ lịch sử cũ nào.

---

## 4. DETAILED SCREEN & COMPONENT SPECIFICATIONS (TASKS #885..#889)

### 4.1. Task #885, Bug #1173, Bug #1508 & Bug #2103: `wicx-json-viewer` Text Selection, 1-Click Copy Path (Scoped Key Hover), 1-Click Copy Value (Scoped Value Hover) & Auto-Dismiss Copy Badge (`AC-MAP-09`, `AC-MAP-10`, `Bug #1173`, `Bug #1508`, `Bug #2103`)
- **Files**: `projects/wicx-crm-fe/libs/wicx-core/src/libs/json-viewer/json-viewer.component.{ts,html,scss,spec.ts}`
- **Requirements**:
  1. **`AC-MAP-09` (Bôi đen văn bản tự do - Free Text Selection)**:
     - Trong `json-viewer.component.scss`, loại bỏ hoặc ghi đè hành vi chặn bôi đen của thẻ `<button>` bằng quy tắc:
       ```scss
       .segment-key,
       .segment-value,
       .segment-primitive {
         user-select: text !important;
         -webkit-user-select: text !important;
         cursor: text;
       }
       .toggler {
         user-select: none;
         cursor: pointer;
       }
       ```
     - Khi người dùng bôi đen văn bản (`window.getSelection()?.toString().length > 0`) trên dòng JSON, sự kiện click trên `<button>` không được vô tình đóng/mở nhánh JSON làm mất vùng bôi đen.
  2. **`AC-MAP-10`, `Bug #1173`, `Bug #1508` & `Bug #2103` (Tách bạch rõ nút 1-Click Copy Path cạnh Key và 1-Click Copy Value cạnh Value, dùng `position: absolute` overlay không chiếm diện tích layout, tách biệt vùng hover Key vs Value và tự động tắt badge sau 1.5s–2s)**:
     - **Nút Copy Path (`button.segment-copy-path-btn` — Đặt ngay cạnh Key, trước dấu `:`)**:
       - **Vị trí DOM**: Đặt ngay sau thẻ `<button [id]="nodeId" class="segment-key-btn">` chứa `.segment-key` / `.segment-label` và **trước** `<span class="segment-colon">:</span>` trong `.segment-main` để tuân thủ quy luật lân cận thị giác (Gestalt Proximity với Key) và đảm bảo thứ tự DOM (`keyBtnIdx < copyPathBtnIdx < colonIdx`).
       - **Điều kiện hiển thị**: `@if (enableCopyPath() && segment.path)`.
       - **Thuộc tính & Nhãn xác nhận**:
         - `class="segment-copy-path-btn"`, `[class.copied]="copiedPath() === segment.path"`
         - `[attr.data-path]="segment.path"`, `[attr.data-copy-kind]="'path'"`
         - `[attr.data-label]="copiedPath() === segment.path ? 'Đã chép path' : 'Copy path'"`
         - `[attr.title]="copiedPath() === segment.path ? 'Đã chép path: ' + segment.path : 'Copy path: ' + segment.path"`
         - `[attr.aria-label]="'Copy JSON path ' + segment.path"`
         - `(click)="copyPath(segment, $event)"`
       - **Hành vi `copyPath(segmentOrPath, event)`**: Sao chép đường dẫn Dot/Bracket notation (`data.system_event_type`, `items[0].id`) vào `navigator.clipboard.writeText(path)`, cập nhật `copiedPath.set(path)`, xóa `copiedValuePath.set(null)`, kích hoạt `scheduleCopyFeedbackReset()` (tự động reset về `null` sau `1800ms`), và phát sự kiện `pathCopy` / `onPathCopy` (bao gồm truyền ngược từ node con lên node gốc qua `(pathCopy)="onChildPathCopy($event)"`).
     - **Nút Copy Value (`button.segment-copy-value-btn` — Đặt ngay cạnh Value)**:
       - **Vị trí DOM**: Đặt ngay sau `.segment-preview-container` (hoặc sau giá trị hiển thị khi `!expandable || !segment.expanded`) trong `.segment-main` để nằm sát bên phải Value (`copyValBtnIdx === previewIdx + 1`).
       - **Điều kiện hiển thị**: `@if (enableCopyValue() && segment.path && (!expandable || !segment.expanded))` với input `readonly enableCopyValue = input<boolean>(true);` (và truyền `[enableCopyValue]="enableCopyValue()"` xuống `<wicx-json-viewer>` đệ quy).
       - **Thuộc tính & Nhãn xác nhận**:
         - `class="segment-copy-value-btn"`, `[class.copied]="copiedValuePath() === segment.path"`
         - `[attr.data-path]="segment.path"`, `[attr.data-copy-kind]="'value'"`
         - `[attr.data-label]="copiedValuePath() === segment.path ? 'Đã chép giá trị' : 'Copy value'"`
         - `[attr.title]="copiedValuePath() === segment.path ? 'Đã chép giá trị: ' + formatSegmentValue(segment) : 'Copy value: ' + formatSegmentValue(segment)"`
         - `[attr.aria-label]="'Copy JSON value ' + segment.path"`
         - `(click)="copyValue(segment, $event)"`
       - **Hành vi `copyValue(segment, event)` & `formatSegmentValue(segment)`**:
         - Chuyển đổi giá trị thực của `segment` sang chuỗi chuẩn để copy (`string` lấy giá trị thô không bọc dấu nháy kép `""`, ví dụ `'https://crm.example.com/lien-he.html'`, `'AutoFormSubmit'`; `Date` lấy `toISOString()`; `null` -> `'null'`; `undefined` -> `'undefined'`; `object`/`array` -> `JSON.stringify(segment.value)`; `number`/`boolean` -> `String(segment.value)`).
         - Ghi vào `navigator.clipboard.writeText(formattedValue)`, cập nhật signal `copiedValuePath.set(segment.path)`, xóa `copiedPath.set(null)`, kích hoạt `scheduleCopyFeedbackReset()` (tự động reset về `null` sau `1800ms`), và phát sự kiện `readonly valueCopy = output<string>()` cùng `readonly onValueCopy = output<string>()` (truyền ngược từ node con qua `(valueCopy)="onChildValueCopy($event)"` và `(valuePathCopy)="onChildValuePathCopy($event)"`).
     - **Styling, Hover Scoping & Auto-Dismiss (`json-viewer.component.scss` & `json-viewer.component.ts` — Khắc phục triệt để `Bug #1508` & `Bug #2103`)**:
       - `.segment-main` phải khai báo `position: relative;` làm gốc tọa độ.
       - `.segment-copy-path-btn` và `.segment-copy-value-btn` bắt buộc sử dụng **`position: absolute;`** kết hợp `opacity: 0; pointer-events: none; z-index: 10;` ở trạng thái mặc định và cầu nối hover vô hình `&::before { content: ''; position: absolute; top: -4px; bottom: -4px; left: -10px; width: 10px; }`.
       - **Tách biệt Hover (`Bug #2103`)**: Xóa bỏ hoàn toàn selector `.segment-main:hover > .segment-copy-path-btn, .segment-main:hover > .segment-copy-value-btn`. Thay bằng:
         1. Hover vào nút Key chỉ hiện nút Copy Path: `.segment-main > .segment-key-btn:hover + .segment-copy-path-btn, .segment-main > button[id]:hover + .segment-copy-path-btn { opacity: 1; pointer-events: auto; }` (cùng `:hover, :focus-visible, &.copied` trên chính `.segment-copy-path-btn`).
         2. Hover vào vùng Value chỉ hiện nút Copy Value: `.segment-main > .segment-preview-container:hover + .segment-copy-value-btn, .segment-main > .segment-preview-container:hover ~ .segment-copy-value-btn { opacity: 1; pointer-events: auto; }` (cùng `:hover, :focus-visible, &.copied` trên chính `.segment-copy-value-btn`).
       - **Tự động tắt Badge sau 1.5s–2s (`Bug #2103`)**:
         - Inject `DestroyRef` trong `JsonViewerComponent`, quản lý `private copyFeedbackTimer: ReturnType<typeof setTimeout> | null = null;` với hằng số `static readonly COPY_FEEDBACK_DURATION_MS = 1800;` (`1.8s`, nằm trong khoảng `1.5s–2s`).
         - Trong `copyPath()`, `onChildPathCopy()`, `copyValue()`, và `onChildValuePathCopy()`, gọi `this.scheduleCopyFeedbackReset()` để `clearTimeout` cũ và đặt `setTimeout` mới sau `1800ms` tự động đặt `this.copiedPath.set(null)` và `this.copiedValuePath.set(null)`. Đăng ký `this.destroyRef.onDestroy(() => this.clearCopyFeedbackTimer())` để tránh rò rỉ bộ nhớ.

### 4.2. Task #886 & Task #2102 (Bug #2083): Screen 1 - Event Overview Dashboard & Connected Pages (`AC-MAP-01`, `AC-MAP-02`, `WI-2083`, `WI-2102`)
- **Files**:
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/remote-entry/entry.routes.ts`
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/models/field-mapping.model.ts`
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/services/field-mapping.service.{ts,spec.ts}`
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/event-overview/event-overview.component.{ts,html,scss,spec.ts}`
- **Requirements**:
  1. **KPI Header Cards & Cycle Select (`AC-MAP-01`, `WI-2102`)**:
     - Card 1: `Tổng sự kiện nhận về` (`9.737` - định dạng phân cách hàng nghìn bằng dấu chấm).
     - Card 2: `Trang liên kết đang nhận` (`4 / 4`).
     - Card 3: `Khách đã nhận diện` (`549`).
     - Dropdown chọn khung thời gian (`data-testid="cycle-range-select"`): Bắt buộc dùng `<tds-select [data]="cycleOptions" valueField="value" textField="label" [ngModel]="selectedCycleDays()" (ngModelChange)="onCycleChange($event)" [allowClear]="false" size="md">` từ `TDSSelectModule` (`tds-ui/select`), tuyệt đối không dùng thẻ `<select>` native.
  2. **Connected Pages Sidebar (`AC-MAP-02`, `WI-2102`)**:
     - Ô tìm kiếm tức thì (`data-testid="sidebar-search-input"`): Dùng `<input tds-input tdsSize="md" type="text" ...>` từ `TDSFormInputModule` (`tds-ui/input`).
     - Các nút chọn trang liên kết (`[attr.data-testid]="'sidebar-page-' + page.id"`): Dùng `<button tds-button-flat color="secondary" type="button" ...>` từ `TDSButtonModule` (`tds-ui/button`) kết hợp viền `tds-color-border-brand-primary` khi active.
     - Vùng cuộn danh sách trang áp dụng `tds-panel-scroll`.
  3. **Connected Pages Statistics Table (`AC-MAP-01`, `WI-2102`)**:
     - Bảng 4 cột (`data-testid="connected-pages-stats-table"`): Bắt buộc dùng `<tds-table [listData]="filteredPages()" [showPagination]="false" [frontPagination]="false" [templateMode]="true">` từ `TDSTableModule` (`tds-ui/table`) chứa trực tiếp `<thead>` và `<tbody>` (không truyền `[scroll]` để tránh measure-row ẩn làm lệch số dòng `tbody tr`).

### 4.3. Task #887 & Task #2102 (Bug #2083): Screen 2 - General Configuration & JSON Field Mapping Stepper (`AC-MAP-03`, `AC-MAP-04`, `WI-2083`, `WI-2102`)
- **Files**: `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/general-config/general-config.component.{ts,html,scss,spec.ts}`
- **Requirements**:
  1. **4-Step Progress Stepper (`AC-MAP-03`, `WI-2102`)**:
     - Hiển thị 4 bước: `1. Chưa cấu hình` ➔ `2. Đã cấu hình chung` ➔ `3. Đang mapping (0/2 form đã map xong)` ➔ `4. Hoàn tất`.
     - Loại bỏ mã màu hex cứng (`#10b981`, `#2563eb`, `#e2e8f0`, `#475569`) trong `general-config.component.scss`, thay bằng semantic utility classes TDS UI (`tds-color-background-success-subtle tds-color-text-white`, `tds-color-background-primary-subtle tds-color-text-white`, `tds-color-background-neutral-subtle tds-color-text-secondary`).
  2. **Sub-navigation Tabs (`TDSTabsModule` - `WI-2102`)**:
     - Thay thế 3 `<button>` sub-tab tự code bằng `<tds-tabset tdsType="line" [tdsBorderless]="true" [selectedIndex]="activeSubTabIndex()" (selectedIndexChange)="onSubTabIndexChange($event)">` từ `TDSTabsModule` (`tds-ui/tabs`), sử dụng `<ng-template>` cho `[title]` chứa `<span data-testid="subtab-general" (click)="onSelectSubTab('general')">`, `subtab-behavior`, `subtab-history`.
  3. **Connection Info & JSON Field Mapping Table (`AC-MAP-03`, `WI-2102`)**:
     - `Nguồn dữ liệu *` (`data-testid="source-type-select"`) và `Tên trang liên kết *` (`data-testid="connected-page-select"`): Dùng `<tds-select [data]="sourceTypeOptions" ...>` và `<tds-select [data]="connectedPageOptions" ...>` (`TDSSelectModule`). Dấu `*` bắt buộc dùng `tds-color-text-error` (xóa `text-red-500`).
     - Bảng `json-field-mapping-table`: Dùng `<tds-table [listData]="jsonConfig().mappings" [showPagination]="false" [frontPagination]="false" [templateMode]="true">` (`TDSTableModule`).
     - Các dòng mở (`!item.isLocked`): Cột 1 dùng `<input tds-input tdsSize="sm" [attr.data-testid]="'mapping-cdp-input-' + i">`, Cột 2 dùng `<tds-select [data]="availableJsonPaths()" [attr.data-testid]="'mapping-json-select-' + i">`, Cột 3 dùng `<button tds-button-outline color="error" size="xs" [attr.data-testid]="'remove-mapping-btn-' + i">Xóa</button>`.
     - Các dòng khóa (`item.isLocked`): Cột 2 dùng `tds-color-background-neutral-minimal` (thay `bg-slate-100`), Cột 3 dùng `<tds-tag status="warning" [attr.data-testid]="'locked-badge-' + i">` (hoặc semantic tokens `tds-color-background-warning-minimal tds-color-text-warning tds-color-border-warning`, xóa `bg-amber-50 text-amber-800 border-amber-200`).
     - Khối thêm dòng mới (`add-mapping-controls`): Dùng `<input tds-input tdsSize="sm">` cho `new-cdp-field-input` và `new-json-path-input`, `<button tds-button-outline color="secondary" size="sm" data-testid="add-mapping-btn">+ Thêm trường</button>`.
     - Header Save Action: Thông báo dùng `tds-color-text-success` / `tds-color-text-error` (xóa `text-emerald-600`, `text-red-600`), nút lưu dùng `<button tds-button color="primary" size="md" data-testid="save-config-btn" (click)="onSaveConfig()">Lưu cấu hình</button>` (xóa `bg-blue-600 hover:bg-blue-700 text-white`).
  4. **Sample JSON Payload Preview & Live Event Preview Table (`AC-MAP-04`, `WI-2102`)**:
     - Nút `copy-payload-btn`: Dùng `<button tds-button-outline color="secondary" size="sm" data-testid="copy-payload-btn">`.
     - Banner `copied-json-path-banner`: Dùng `tds-color-background-info-minimal tds-color-border-info tds-color-text-info` (xóa `bg-blue-50 border-blue-200 text-blue-800`).
     - Khối `json-viewer-container`, `general-config-page` và `sample-json-syntax-highlight`: Thêm `tds-panel-scroll`; thay `bg-slate-900 text-slate-100` bằng `tds-color-background-neutral-boldest tds-color-text-white`.
     - Bảng `live-preview-events-table`: Dùng `<tds-table [listData]="displayedLiveEvents()" [showPagination]="false" [frontPagination]="false" [templateMode]="true">`.
     - Các nút phân trang (`page-btn-1`, `page-btn-2`, `page-btn-last`): Dùng `<button tds-button [color]="currentPage() === n ? 'primary' : 'secondary'" size="xs">` (xóa `bg-blue-600 text-white`).

### 4.4. Task #888: Screen 3 - Behavior Events Toggle & Form Field Mapping (`AC-MAP-05`, `AC-MAP-06`)
- **Files**: `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/behavior-form-mapping/behavior-form-mapping.component.{ts,html,scss,spec.ts}`
- **Requirements**:
  1. **Behavior Events Table (`AC-MAP-05`)**:
     - Hiển thị 4 sự kiện: `Gửi form` (`AutoFormSubmit`, 8 lượt), `Xem trang` (`PageView`, 3.281 lượt), `Nhấp chuột` (`AutoClick`, 2.089 lượt), `Tỷ lệ đọc trang` (`ScrollDepth`, 711 lượt).
     - Checkbox `Lưu vào Hồ sơ KH` cập nhật tức thì qua `FieldMappingService.toggleBehaviorEvent(eventType)`.
  2. **Detected Web Forms & Form Field Mapping Detail (`AC-MAP-06`)**:
     - Danh sách 2 form đã ghi nhận: `Form liên hệ` (`/lien-he.html`, `FORM-01`, 4 trường) và `Form đăng ký dùng thử` (`/dang-ky-dung-thu.html`, `FORM-02`, 3 trường) với nút `[Cấu hình mapping]`.
     - Màn hình chi tiết Mapping Form liên hệ:
       - `form.tds-input-1` (`"0969733325"`) ➔ `phone` · `CH-SDT` · `Cao`
       - `form.tds-input-2` (`"Tấn "`) ➔ `name` · `CH-TEN` · `Cao`
       - `form.tds-input-3` (`"tansida@gmail.com"`) ➔ `email` · `CH-EMAIL` · `Cao`
       - `form.tds-input-4` (`"Quận 7"`) ➔ `null` (*Chưa chọn*)
       - Nút `‹ Quay lại` và `[Lưu thay đổi]`.

### 4.5. Task #889: Screen 4 - Version History Diff & 1-Click Rollback (`AC-MAP-07`, `AC-MAP-08`)
- **Files**:
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/version-history/version-history.component.{ts,html,scss,spec.ts}`
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/remote-entry/entry.routes.ts` (đăng ký route `pages/:pageId/forms/:formId/history` và `history`)
- **TDS UI & Architectural Requirements**:
  1. **TDS UI Compliance (Zero Raw Tailwind Colors)**:
     - Import `TDSButtonModule` (`button[tds-button]`, `button[tds-button-outline]`, `button[tds-button-flat]`), `TDSTagModule` (`<tds-tag>`), `TDSBreadCrumbModule` (`<tds-breadcrumb>`, `<tds-breadcrumb-item>`).
     - Sử dụng 100% semantic tokens `tds-color-surface-*`, `tds-color-text-*`, `tds-color-border-*`, `tds-color-background-*-minimal` và `tds-panel-scroll`.
  2. **Header & Breadcrumbs**:
     - Nút `‹ Quay lại mapping form` (`button[tds-button-outline]` hoặc `button[tds-button-flat]`, `data-testid="back-to-form-mapping-btn"`, gọi `onBackToFormMapping()`).
     - Breadcrumb (`<tds-breadcrumb>` / `data-testid="version-history-breadcrumb"`): `Mapping dữ liệu / CRM / Gửi form / Form liên hệ / Lịch sử thay đổi`.
     - Tiêu đề: **Lịch sử thay đổi mapping** kèm phụ đề: `WEB-01 · form /lien-he.html (Form liên hệ). Mỗi lần lưu tạo một phiên bản mới và áp dụng ngay. Chỉ admin được cấu hình mapping.`
  3. **Version Diff Detail (`AC-MAP-07`)**:
     - Tiêu đề khối: `Phiên bản {{ selectedVersion().version }}: {{ getVersionComparisonTitle(selectedVersion()) }}` (VD: `Phiên bản 3: thay đổi so với phiên bản 2`) kèm `<tds-tag [status]="selectedVersion().status === 'active' ? 'success' : 'neutral'">{{ selectedVersion().status === 'active' ? 'Đang chạy' : 'Lưu trữ' }}</tds-tag>`.
     - Metadata: `Lưu bởi {{ selectedVersion().authorName }} · {{ formatSavedAt(selectedVersion().savedAt) }} · áp dụng cho dữ liệu nhận từ lúc lưu`.
     - Hiển thị danh sách `selectedVersion().diffs` với 3 loại badge chuẩn `<tds-tag>`:
       - `type: 'added'` ➔ `<tds-tag status="success">Thêm</tds-tag>` (Badge xanh lá): `form.tds-input-3 → email · CH-EMAIL · tin cậy Cao` (`Hệ thống tự map`)
       - `type: 'modified'` ➔ `<tds-tag status="info">Sửa</tds-tag>` (Badge xanh dương): `form.tds-input-2 · quy tắc chuẩn hóa` (`Không áp dụng ➔ CH-TEN`)
       - `type: 'unmapped'` ➔ `<tds-tag status="warning">Chưa map</tds-tag>` (Badge cam): `form.tds-input-4 → thuộc tính mở rộng` (`Chưa có trường CDP phù hợp, dữ liệu vẫn được giữ`)
  4. **Version List Sidebar & 1-Click Rollback (`AC-MAP-08`)**:
     - Hiển thị danh sách các phiên bản sắp xếp giảm dần theo `version` (`sortedVersions` computed: `Phiên bản 3 - Đang chạy`, `Phiên bản 2 - Lưu trữ`, `Phiên bản 1 - Lưu trữ`).
     - Mỗi phiên bản hiển thị `{{ v.authorName }} · {{ formatVersionDate(v.savedAt) }} · {{ v.version === 1 ? 'tạo mới' : v.changeCount + ' thay đổi' }}`.
     - Các phiên bản `Lưu trữ` (`v.status === 'archived'`) có nút `[Xem]` (`(click)="onSelectVersion(v.version)"`) và `[Khôi phục]` (`(click)="onRollbackVersion(v.version)"`).
     - Khi bấm `[Khôi phục]` trên phiên bản cũ (VD: Phiên bản 2), gọi `FieldMappingService.rollbackToVersion(2)` tạo `Phiên bản 4` mới ở trạng thái `Đang chạy` (`active`), chuyển `Phiên bản 3` sang `Lưu trữ` (`archived`), bảo toàn 100% lịch sử cũ và hiển thị thông báo xác nhận.
     - Chân trang sidebar hiển thị chú thích: *"Khôi phục tạo một phiên bản mới từ bản cũ và áp dụng ngay. Lịch sử không bị xóa."*

---

## 5. VERIFICATION & TEST MATRIX (TASK #890)

| Mã AC | Task | Tiêu chí nghiệm thu | File Unit Test (`Jest`) |
| :--- | :--- | :--- | :--- |
| `AC-MAP-01` | `#886` | Hiển thị chính xác 3 chỉ số KPI (`9.737`, `4 / 4`, `549`), bộ lọc 30/90/180 ngày và bảng thống kê trang liên kết. | `event-overview.component.spec.ts`, `field-mapping.service.spec.ts` |
| `AC-MAP-02` | `#886` | Tìm kiếm tức thì trang liên kết theo tên, `site_id`, `page_id` trên sidebar trái. | `event-overview.component.spec.ts`, `field-mapping.service.spec.ts` |
| `AC-MAP-03` | `#887` | Hiển thị Stepper 4 bước và bảng ánh xạ JSON (`site_id`, `data.system_event_type` bị khóa cố định). | `general-config.component.spec.ts`, `field-mapping.service.spec.ts` |
| `AC-MAP-04` | `#887` | Xem trước JSON mẫu định dạng chuẩn kèm nút `[Copy Payload]` và bảng 10 bản ghi trả về sau cấu hình. | `general-config.component.spec.ts` |
| `AC-MAP-05` | `#888` | Checkbox bật/tắt lưu sự kiện hành vi vào hồ sơ khách hàng lưu trạng thái tức thì. | `behavior-form-mapping.component.spec.ts`, `field-mapping.service.spec.ts` |
| `AC-MAP-06` | `#888` | Bảng ánh xạ trường form cho phép chọn trường CDP (`phone`, `name`, `email`), chuẩn hóa (`CH-SDT`, `CH-TEN`, `CH-EMAIL`), và độ tin cậy (`Cao`). | `behavior-form-mapping.component.spec.ts` |
| `AC-MAP-07` | `#889` | Hiển thị danh sách phiên bản và phân biệt rõ các loại thay đổi (`Thêm` xanh lá, `Sửa` xanh dương, `Chưa map` cam). | `version-history.component.spec.ts`, `field-mapping.service.spec.ts` |
| `AC-MAP-08` | `#889` | Bấm nút `[Khôi phục]` phiên bản cũ tạo một phiên bản mới mang cấu hình bản được chọn mà không xóa lịch sử cũ. | `version-history.component.spec.ts`, `field-mapping.service.spec.ts` |
| `AC-MAP-09` | `#885` | Người dùng bôi đen chuột tự do trên bất kỳ key, value, string literals trong `wicx-json-viewer` (`user-select: text !important`). | `json-viewer.component.spec.ts` |
| `AC-MAP-10` | `#885 / #1173 / #1508 / #2103` | Tách bạch nút 1-click `Copy path` (cạnh Key) và `Copy value` (cạnh Value); dùng `position: absolute` không tạo khoảng trống; hover Key chỉ hiện nút Copy Path, hover Value chỉ hiện nút Copy Value, và badge `'Đã chép ...'` tự động tắt sau `1.5s-2s` (`1800ms`). | `json-viewer.component.spec.ts` |

