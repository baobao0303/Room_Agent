# Radio

Radio button đơn. Dùng `tds-radio-group` để nhóm các radio.

**Selector:** `[tds-radio]`, `[tds-radio-button]`
**Import:** `import { TDSRadioModule } from 'tds-ui/radio';`
**Export as:** `tdsRadio`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `value` | `any` | — | Giá trị của radio |
| `disabled` | `boolean` | `false` | Vô hiệu hóa |
| `autoFocus` | `boolean` | `false` | Tự động focus |
| `size` | `ButtonSize` (`'xs' \| 'sm' \| 'md' \| 'lg' \| 'xl'`) | `'md'` | Kích thước |
| `tdsTheme` | `TDSTheme` (`'default' \| 'light' \| 'dark'`) | `'default'` | Theme |
| `tdsIcon` | `string \| TemplateRef` | — | Icon hiển thị (chỉ cho radio button) |
| `[tds-radio-button]` | `boolean` | `false` | Dùng dạng button thay vì circle |

## Methods

| Method | Description |
|--------|-------------|
| `focus()` | Focus vào radio |
| `blur()` | Blur radio |

## Usage

```html
<!-- Basic radio with radio-group -->
<tds-radio-group [(ngModel)]="selectedOption">
  <label tds-radio [value]="'a'">Option A</label>
  <label tds-radio [value]="'b'">Option B</label>
  <label tds-radio [value]="'c'">Option C</label>
</tds-radio-group>

<!-- ReactiveForm -->
<tds-radio-group [formControl]="colorCtrl">
  <label tds-radio [value]="'red'">Red</label>
  <label tds-radio [value]="'green'">Green</label>
  <label tds-radio [value]="'blue'">Blue</label>
</tds-radio-group>

<!-- Radio button style -->
<tds-radio-group [(ngModel)]="size">
  <label tds-radio-button [value]="'small'" tdsIcon="tds-icon-sm">Small</label>
  <label tds-radio-button [value]="'medium'" tdsIcon="tds-icon-md">Medium</label>
  <label tds-radio-button [value]="'large'" tdsIcon="tds-icon-lg">Large</label>
</tds-radio-group>

<!-- Disabled -->
<tds-radio-group [(ngModel)]="status" [disabled]="true">
  <label tds-radio [value]="'active'">Active</label>
  <label tds-radio [value]="'inactive'">Inactive</label>
</tds-radio-group>

<!-- Different sizes -->
<tds-radio-group [(ngModel)]="selected" size="lg">
  <label tds-radio [value]="1">Large</label>
  <label tds-radio [value]="2">Radio</label>
</tds-radio-group>
```

```typescript
import { TDSRadioModule } from 'tds-ui/radio';

selectedOption = 'a';
colorCtrl = new FormControl('red');
size = 'medium';
status = 'active';

// Radio button với icon
// tdsIcon có thể là string class hoặc TemplateRef
iconTemplate: TemplateRef<any> = ...;
```

## Notes

- Dùng `<label>` bọc `tds-radio` để click vào text cũng chọn được
- Radio buttons trong cùng `tds-radio-group` tự động chia sẻ `name`
- Dùng `[tds-radio-button]` để đổi style từ circle sang button
- `tdsIcon` chỉ hoạt động với radio button style
- Tự động hỗ trợ RTL (right-to-left)
- Size có thể set riêng cho từng radio hoặc từ `tds-radio-group`

## tds-radio-group Inputs

`tds-radio-group` có các inputs riêng để điều khiển nhóm radio:

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `disabled` | `boolean` | `false` | Vô hiệu hóa tất cả radios trong group |
| `tdsButtonStyle` | `'primary' \| 'secondary'` | `'primary'` | Style của radio button (chỉ khi dùng button style) |
| `tdsButtonType` | `'outline' \| 'base'` | `'outline'` | Type của radio button (chỉ khi dùng button style) |
| `tdsButtonIcon` | `boolean` | `false` | Hiển thị icon trong radio button |
| `tdsName` | `string \| null` | `null` | Name attribute cho tất cả radios trong group |
| `tdsSize` | `ButtonSize` | `'md'` | Kích thước cho tất cả radios (ưu tiên hơn `size`) |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme cho group |
| `size` | `ButtonSize` | `'md'` | **DEPRECATED** — dùng `tdsSize` thay thế |

**Export as:** `tdsRadioGroup`
