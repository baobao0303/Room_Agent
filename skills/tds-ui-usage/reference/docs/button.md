# Button

Nút bấm với nhiều kiểu dáng. Mỗi variant là một component riêng với selector riêng — tất cả import chung qua `TDSButtonModule`.

**Import:** `import { TDSButtonModule } from 'tds-ui/button';`

## Selector Overview

| Selector | Component | exportAs | Mô tả |
|----------|-----------|----------|-------|
| `button[tds-button]`, `a[tds-button]` | `TDSButtonComponent` | `tdsButton` | Button mặc định (filled) |
| `button[tds-button-outline]`, `a[tds-button-outline]` | `TDSButtonOutlineComponent` | `tdsButtonOutline` | Button viền |
| `button[tds-button-flat]`, `a[tds-button-flat]` | `TDSButtonFlatComponent` | `tdsButtonFlat` | Button phẳng |
| `button[tds-button-icon]`, `a[tds-button-icon]` | `TDSButtonIconComponent` | `tdsButtonIcon` | Chỉ icon (filled) |
| `button[tds-button-outline-icon]`, `a[tds-button-outline-icon]` | `TDSButtonOutlineIconComponent` | `tdsButtonOutlineIcon` | Chỉ icon (outline) |
| `button[tds-button-flat-icon]`, `a[tds-button-flat-icon]` | `TDSButtonFlatIconComponent` | `tdsButtonFlatIcon` | Chỉ icon (flat) |
| `button[tds-button-text]`, `a[tds-button-text]` | `TDSButtonTextComponent` | `tdsButtontext` | Chỉ text |
| `button[tds-button-close]`, `a[tds-button-close]`, `span[tds-button-close]` | `TDSButtonCloseComponent` | `tdsButtonClose` | Nút đóng (X) |
| `button[tds-button-overlay]` | `TDSButtonOverlayComponent` | `tdsButtonOverlay` | Nút overlay (play) |
| `button[tds-button-toggle]` | `TDSButtonToggleComponent` | `tdsButtonToggle` | Nút toggle |
| `button[tds-button-icon-no-spacing]` | `TDSButtonIconNoSpacingComponent` | `tdsButtonIconNoSpacing` | Icon không spacing |
| `button[tds-button-base]`, `a[tds-button-base]` | `TDSButtonBaseComponent` | `tdsButton` | Base raw — cần set `tdsType` thủ công |
| `a[tds-text-link]` | `TDSTextLinkDirective` | — | Text link (disabled/underline) |
| `tds-button-group` | `TDSButtonGroupComponent` | — | Nhóm button |

## Group 1 — Kế thừa TDSButtonBase

Các variant dưới đây dùng chung inputs/outputs từ `TDSButtonBase` (xem bảng Shared Inputs/Outputs cuối trang).

### tds-button (Mặc định)

```html
<button tds-button color="primary" (tdsBtnClick)="onSave()">Lưu</button>
<button tds-button color="secondary" size="lg">Large</button>

<!-- Loading -->
<button tds-button color="primary" [loading]="isSaving">Đang lưu...</button>

<!-- Disabled -->
<button tds-button [disabled]="!form.valid" color="primary">Gửi</button>

<!-- Với icon -->
<button tds-button color="primary" tdsPrefixIcon="tdsi-search-fill">Tìm kiếm</button>
<button tds-button color="primary" tdsSuffixIcon="tdsi-arrow-right-fill">Tiếp tục</button>

<!-- Rounded -->
<button tds-button color="primary" rounded="rounded-full">Rounded</button>

<!-- Loading template -->
<ng-template #loadingTpl><span>Đang xử lý...</span></ng-template>
<button tds-button [loading]="isLoading" [loadingTemplate]="loadingTpl">Submit</button>
```

### tds-button-outline

Inputs bổ sung: `tdsBorderStyle: 'solid' | 'dashed'` (mặc định `'solid'`)

```html
<button tds-button-outline color="secondary" (tdsBtnClick)="onAction()">Outline</button>
<button tds-button-outline color="error" tdsBorderStyle="dashed">Dashed</button>

<!-- Loading -->
<button tds-button-outline color="primary" [loading]="isLoading">Loading...</button>
```

### tds-button-flat

```html
<button tds-button-flat color="primary" (tdsBtnClick)="onAction()">Flat</button>

<!-- Loading -->
<button tds-button-flat color="secondary" [loading]="isLoading">Loading...</button>
```

### tds-button-icon

Button chỉ icon, không có text. Dùng `tdsIcon` để set icon.

```html
<button tds-button-icon color="primary" tdsIcon="tdsi-close-fill"></button>
<button tds-button-icon color="secondary" tdsIcon="tdsi-edit-fill" size="sm"></button>
```

### tds-button-outline-icon

Outline version của icon button.

```html
<button tds-button-outline-icon color="secondary" tdsIcon="tdsi-search-fill"></button>
```

### tds-button-flat-icon

Flat version của icon button.

```html
<button tds-button-flat-icon color="primary" tdsIcon="tdsi-close-fill"></button>
```

### tds-button-base

Component raw — không set `tdsType` sẵn. Bạn cần truyền `tdsType` thủ công.

```html
<button tds-button-base tdsType="default" color="primary">Base button</button>
<button tds-button-base tdsType="outline" color="secondary">Base outline</button>
```

> **Note:** Chỉ dùng `tds-button-base` khi bạn cần kiểm soát `tdsType` động. Với các variant cố định, ưu tiên dùng selector riêng (`tds-button`, `tds-button-outline`, v.v.).

## Group 2 — API riêng

Các variant dưới đây không kế thừa `TDSButtonBase`, có inputs riêng đơn giản hơn.

### tds-button-text

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `'sm' \| 'md'` | `'md'` | Kích thước |
| `tdsColor` | `TDSButtonColor` | `'primary'` | Màu sắc |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `tdsPrefixIcon` | `string \| TemplateRef` | `null` | Icon trước text |
| `tdsSuffixIcon` | `string \| TemplateRef` | `null` | Icon sau text |

```html
<button tds-button-text tdsColor="primary">Text button</button>
<button tds-button-text tdsColor="secondary" tdsSize="sm">Small text</button>
<button tds-button-text tdsColor="info" tdsPrefixIcon="tdsi-info-fill">Info</button>
<button tds-button-text [disabled]="true">Disabled</button>
```

### tds-button-close

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `ButtonSize` | `'xl'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `tdsType` | `'flat' \| 'base'` | `'flat'` | Kiểu close button |
| `tdsIconTemplate` | `string \| TemplateRef` | `'tdsi-close-fill'` | Icon tùy chỉnh |
| `tdsTabIndex` | `number \| null` | `null` | Tab index |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |

```html
<button tds-button-close></button>
<button tds-button-close tdsSize="sm"></button>
<button tds-button-close tdsType="base"></button>
<button tds-button-close tdsIconTemplate="tdsi-minus-fill"></button>
```

### tds-button-overlay

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `ButtonSize` | `'md'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `tdsLoading` | `boolean` | `false` | Hiển thị spinner |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |
| `tdsIcon` | `string \| TemplateRef` | `'tdsi-play-fill'` | Icon |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |

```html
<button tds-button-overlay></button>
<button tds-button-overlay tdsSize="lg"></button>
<button tds-button-overlay [tdsLoading]="isLoading"></button>
```

### tds-button-toggle

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `'sm' \| 'md'` | `'md'` | Kích thước |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |
| `tdsActive` | `boolean` | `false` | Trạng thái active |
| `tdsIcon` | `string \| TemplateRef` | `'tdsi-filter-fill'` | Icon |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |

| Output | Type | Description |
|--------|------|-------------|
| `tdsActiveChange` | `EventEmitter<boolean>` | Emit khi toggle state thay đổi |

```html
<button tds-button-toggle [(tdsActive)]="isActive" tdsIcon="tdsi-filter-fill"></button>
```

### tds-button-icon-no-spacing

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `'sm' \| 'md'` | `'md'` | Kích thước |
| `tdsColor` | `TDSButtonColor` | `'primary'` | Màu sắc |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme |
| `tdsIcon` | `string \| TemplateRef` | `'tdsi-filter-fill'` | Icon |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |

```html
<button tds-button-icon-no-spacing tdsIcon="tdsi-filter-fill"></button>
<button tds-button-icon-no-spacing tdsIcon="tdsi-edit-fill" tdsColor="secondary"></button>
```

## Group 3 — Utility

### tds-text-link

Text link. Hỗ trợ underline và disabled state.

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa — set `tabindex=-1`, `preventDefault` + `stopImmediatePropagation` khi click |
| `tdsUnderline` | `boolean` | `false` | Gạch chân link |

```html
<a tds-text-link href="/docs">Tài liệu</a>
<a tds-text-link [tdsUnderline]="true" href="/docs">Underlined</a>
<a tds-text-link [tdsDisabled]="true" href="/docs">Disabled</a>
<a tds-text-link [tdsUnderline]="true" [tdsDisabled]="true" href="/docs">Disabled underline</a>
```

### tds-button-group

```html
<tds-button-group>
  <button tds-button color="primary">Lưu</button>
  <button tds-button-outline color="secondary">Hủy</button>
</tds-button-group>
```

## Shared Inputs/Outputs (Group 1)

Áp dụng cho: `tds-button`, `tds-button-outline`, `tds-button-flat`, `tds-button-icon`, `tds-button-outline-icon`, `tds-button-flat-icon`, `tds-button-base`.

### Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `color` | `TDSButtonColor` | `'primary'` | Màu sắc: `primary`, `secondary`, `success`, `error`, `warning`, `info`, `custom` |
| `size` | `ButtonSize` | `'md'` | Kích thước: `xs`, `sm`, `md`, `lg`, `xl` |
| `loading` | `boolean` | `false` | Hiển thị spinner loading |
| `disabled` | `boolean` | `false` | Vô hiệu hóa button |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |
| `tdsBgStyle` | `TDSButtonBackgroundColorStyle` | `'default'` | Nền: `default`, `minimal`, `ghost` |
| `tdsBorderStyle` | `TDSButtonBorderStyle` | `'solid'` | Viền: `solid`, `dashed` (chỉ `tds-button-outline` và `tds-button-base`) |
| `tdsIcon` | `string \| TemplateRef` | `null` | Icon class hoặc template |
| `tdsPrefixIcon` | `string \| TemplateRef` | `null` | Icon trước text |
| `tdsSuffixIcon` | `string \| TemplateRef` | `null` | Icon sau text |
| `tdsThrottleTime` | `number` | `300` | Thời gian chặn click liên tiếp (ms) |
| `rounded` | `string` | `''` | CSS class border radius tùy chỉnh |
| `loadingTemplate` | `string \| TemplateRef` | `undefined` | Template tùy chỉnh cho loading state |
| `tdsType` | `TDSButtonType` | auto | **Chỉ dùng với `tds-button-base`** — các variant khác tự set internal |

### Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsBtnClick` | `EventEmitter<MouseEvent>` | Click event (throttled, không emit khi disabled/loading) |

## Notes

- Dùng `(tdsBtnClick)` thay vì `(click)` để có throttle chống click nhanh
- `tdsThrottleTime` được cấu hình global qua `TDSConfigService`
- `rounded` nhận CSS class (ví dụ: `rounded-full`, `rounded-lg`)
- Import `TDSButtonModule` vào `imports: []` của standalone component
- Hỗ trợ cả `<button>` và `<a>` tags (trừ một số variant đặc thù)
- `tdsType` là internal — mỗi selector tự set `tdsType`. Chỉ `tds-button-base` cần set thủ công
