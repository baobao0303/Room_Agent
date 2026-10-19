# Task #2102 (Bug #2083): Refactor GeneralConfigComponent & EventOverviewComponent to TDS UI Components

- **Target Files**:
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/general-config/general-config.component.{ts,html,scss,spec.ts}`
  - `projects/wicx-crm-fe/apps/mfe-cdp/src/app/pages/field-mapping/components/event-overview/event-overview.component.{ts,html,scss,spec.ts}`

## Requirements & Acceptance Criteria
1. **REQ-TDS-01 (TDSSelectModule)**: Replace all native `<select>` elements (`cycle-range-select` in `EventOverviewComponent`; `source-type-select`, `connected-page-select`, `mapping-json-select-*` in `GeneralConfigComponent`) with `<tds-select [data]="..." [ngModel]="..." (ngModelChange)="...">`.
2. **REQ-TDS-02 (TDSButtonModule)**: Replace all native `<button>` elements (`save-config-btn`, `remove-mapping-btn-*`, `add-mapping-btn`, `copy-payload-btn`, `page-btn-*`, `sidebar-page-*`) with `tds-button`, `tds-button-outline`, or `tds-button-flat` directives.
3. **REQ-TDS-03 (TDSTabsModule)**: Replace custom sub-navigation buttons (`subtab-general`, `subtab-behavior`, `subtab-history`) in `GeneralConfigComponent` with `<tds-tabset tdsType="line">` and `<tds-tab>`.
4. **REQ-TDS-04 (TDSTableModule)**: Replace all native `<table>` elements (`connected-pages-stats-table`, `json-field-mapping-table`, `live-preview-events-table`) with `<tds-table [listData]="..." [showPagination]="false" [frontPagination]="false" [templateMode]="true">`.
5. **REQ-TDS-05 (TDSFormInputModule / Semantic Tokens / Scrollbar)**: Add `tds-input` to text inputs, replace 100% hardcoded Tailwind color classes and hex codes with `tds-color-*` semantic tokens, add `tds-panel-scroll` to scrollable containers, and ensure 100% Jest unit test pass rate in `mfe-cdp`.
