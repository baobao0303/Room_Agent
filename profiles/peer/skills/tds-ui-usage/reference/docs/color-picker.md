# Color Picker

Component chọn màu với đầy đủ tính năng: color picker, swatch presets, và palette colors. Hỗ trợ nhiều định dạng màu và theme.

**Selector:** `tds-color-picker`, `[tds-color-picker]`
**Import:** `import { TDSColorPickerModule } from 'tds-ui/color-picker';`
**Export as:** `tdsColorPicker`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `'sm' \| 'md' \| 'lg' \| 'xl'` | `'md'` | Kích thước component |
| `tdsDisabled` | `boolean` | `false` | Vô hiệu hóa color picker |
| `tdsOpen` | `boolean` | `false` | Trạng thái mở/đóng dropdown |
| `tdsPlacement` | `TDSColorPickerPlacementType \| Array<TDSColorPickerPlacementType>` | `[]` | Vị trí dropdown: `bottomLeft`, `bottomRight`, `topLeft`, `topRight`, `left`, `right`, etc. |
| `tdsDropdownMatchSelectWidth` | `boolean` | `false` | Dropdown width match với input width |
| `tdsBackdrop` | `boolean` | `false` | Hiển thị backdrop |
| `tdsDropdownClassName` | `string` | `undefined` | Custom class cho dropdown |
| `tdsDropdownStyle` | `NgStyleInterface` | `null` | Custom style cho dropdown |
| `tdsDropdownWidth` | `number` | `240` | Width của dropdown (px) |
| `tdsPlaceHolder` | `string` | `''` | Placeholder text |
| `tdsFormat` | `ColorFormats` | `'hex'` | Định dạng màu: `hex`, `rgb`, `hsl`, `prgb` |
| `tdsDefaultColor` | `string` | `'#000000'` | Màu mặc định |
| `tdsId` | `string` | `''` | ID của component |
| `tdsShowInput` | `boolean` | `true` | Hiển thị input nhập màu |
| `tdsAllowClear` | `boolean` | `true` | Cho phép xóa màu |
| `tdsInline` | `boolean` | `false` | Hiển thị inline (không dropdown) |
| `tdsSwatchColors` | `Array<string \| TDSColorDTO>` | `default swatch` | Danh sách màu swatch |
| `tdsPalleteColors` | `Array<{ name: string, colors: Array<string \| TDSColorDTO> }>` | `default palette` | Danh sách màu palette theo nhóm |
| `tdsMode` | `TDSModeColorPicker` | `['picker', 'swatch', 'pallete']` | Chế độ hiển thị: `picker`, `swatch`, `pallete`, hoặc kết hợp |
| `tdsType` | `'default' \| 'compact'` | `'default'` | Kiểu hiển thị |
| `tdsSwatchText` | `string` | `'Swatch'` | Text cho tab swatch |
| `tdsPalleteText` | `string` | `'Pallete'` | Text cho tab pallete |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |
| `tdsBordered` | `boolean` | `true` | Hiển thị border |
| `tdsHeightSaturation` | `number` | `240` | Chiều cao saturation picker (px) |
| `tdsAllowOpenDropdown` | `boolean` | `true` | Cho phép mở dropdown |
| `tdsAutoEmitValue` | `boolean` | `true` | Auto emit giá trị khi chọn (false: chỉ emit khi đóng dropdown) |
| `tdsPalleteOptionTemplate` | `TemplateRef<any>` | `null` | Custom template cho palette option |
| `tdsSwatchOptionTemplate` | `TemplateRef<any>` | `null` | Custom template cho swatch option |
| `tdsRequired` | `boolean` | `false` | Bắt buộc chọn màu (dùng cho form validation) |

## Key Outputs

Color Picker sử dụng `ControlValueAccessor`, dùng với `[(ngModel)]` hoặc `[formControl]`.

| Output | Type | Description |
|--------|------|-------------|
| `tdsOpenChange` | `EventEmitter<boolean>` | Phát sinh khi dropdown mở/đóng |
| `tdsCleared` | `EventEmitter<void>` | Phát sinh khi xóa màu |
| `tdsColorChange` | `EventEmitter<TDSTinyColor>` | Phát sinh khi màu thay đổi |
| `tdsPalleteChange` | `EventEmitter<string \| TDSColorDTO>` | Phát sinh khi chọn màu từ palette |
| `tdsSwatchChange` | `EventEmitter<string \| TDSColorDTO>` | Phát sinh khi chọn màu từ swatch |
| `tdsPreviewClick` | `EventEmitter<MouseEvent>` | Phát sinh khi click vào preview |

## Usage

```html
<!-- Cơ bản -->
<tds-color-picker [(ngModel)]="color"></tds-color-picker>

<!-- Với placeholder và size -->
<tds-color-picker 
  [(ngModel)]="color"
  [tdsSize]="'lg'"
  [tdsPlaceHolder]="'Chọn màu'">
</tds-color-picker>

<!-- Chỉ hiển thị swatch -->
<tds-color-picker 
  [(ngModel)]="color"
  [tdsMode]="['swatch']"
  [tdsSwatchColors]="customSwatches">
</tds-color-picker>

<!-- Inline mode -->
<tds-color-picker 
  [(ngModel)]="color"
  [tdsInline]="true"
  [tdsType]="'compact'">
</tds-color-picker>

<!-- Với custom palette -->
<tds-color-picker 
  [(ngModel)]="color"
  [tdsPalleteColors]="customPalettes">
</tds-color-picker>

<!-- Định dạng RGB -->
<tds-color-picker 
  [(ngModel)]="color"
  [tdsFormat]="'rgb'">
</tds-color-picker>

<!-- Với placement -->
<tds-color-picker 
  [(ngModel)]="color"
  [tdsPlacement]="['topRight', 'topLeft']">
</tds-color-picker>
```

```typescript
import { TDSColorPickerModule } from 'tds-ui/color-picker';
import { FormControl } from '@angular/forms';
import { TDSColorDTO } from 'tds-ui/tinycolor';

@Component({
  standalone: true,
  imports: [TDSColorPickerModule],
})
export class MyComponent {
  color = '#1890ff';
  
  // Custom swatches
  customSwatches = [
    '#f5222d',
    '#fa8c16',
    '#fadb14',
    '#52c41a',
    '#1890ff',
    '#722ed1'
  ];
  
  // Custom palettes
  customPalettes = [
    {
      name: 'Red Colors',
      colors: ['#f5222d', '#ff4d4f', '#ff7a45', '#ffa940']
    },
    {
      name: 'Blue Colors',
      colors: ['#1890ff', '#40a9ff', '#69c0ff', '#91d5ff']
    }
  ];
}
```

## Notes

- Dùng `[(ngModel)]` hoặc `[formControl]` để bind giá trị màu
- `tdsMode` chấp nhận array hoặc string:
  - `['picker']`: Chỉ hiển thị color picker
  - `['swatch']`: Chỉ hiển thị swatch
  - `['pallete']`: Chỉ hiển thị palette
  - `['picker', 'swatch']`: Kết hợp picker và swatch
  - `['picker', 'swatch', 'pallete']`: Full mode (default)
- `tdsInline="true"` để hiển thị inline không dropdown
- `tdsAutoEmitValue="false"` để chỉ emit giá trị khi đóng dropdown (tốt cho performance)
- `tdsFormat` hỗ trợ: `hex`, `rgb`, `hsl`, `prgb` (percentage rgb)
- Hỗ trợ custom template cho swatch và palette options
- Hỗ trợ 3 theme: `default`, `light`, `dark`
- TDSColorDTO có thể là string (hex color) hoặc object `{ color: string }`
- Component bao gồm nhiều sub-components: `TDSPanelColorPickerModule`, `TDSSwatchColorPickerModule`, `TDSPalleteColorPickerModule`, `TDSInputColorPickerModule`
