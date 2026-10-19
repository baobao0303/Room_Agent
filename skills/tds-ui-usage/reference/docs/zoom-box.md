# Zoom Box

Component hiển thị hình ảnh phóng to khi hover hoặc click. Hỗ trợ nhiều chế độ zoom và có thể hiển thị lens hoặc overlay.

**Selector:** `tds-zoombox`
**Import:** `import { TDSZoomBoxModule } from 'tds-ui/zoom-box';`
**Export as:** `TDSZoomBoxComponent`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `thumbImage` | `string` | - | URL hình ảnh thumbnail (bắt buộc) |
| `fullImage` | `string` | - | URL hình ảnh full size (bắt buộc) |
| `zoomMode` | `'hover' \| 'toggle' \| 'click' \| 'toggle-click' \| 'hover-freeze'` | `'hover'` | Chế độ kích hoạt zoom |
| `magnification` | `number` | `1` | Tỷ lệ phóng to |
| `minZoomRatio` | `number` | `0` | Tỷ lệ zoom tối thiểu |
| `maxZoomRatio` | `number` | `2` | Tỷ lệ zoom tối đa |
| `enableLens` | `boolean` | `false` | Hiển thị lens trên thumbnail |
| `lensWidth` | `number` | `100` | Chiều rộng lens (px) |
| `lensHeight` | `number` | `100` | Chiều cao lens (px) |
| `circularLens` | `boolean` | `false` | Lens hình tròn |
| `enableOverlay` | `boolean` | `false` | Hiển thị zoom trong overlay bên ngoài |
| `enableScrollZoom` | `boolean` | `false` | Cho phép zoom bằng scroll chuột |
| `scrollStepSize` | `number` | `0.1` | Bước zoom mỗi lần scroll |
| `extendX` | `number` | `0` | Khoảng cách ngang của overlay (px) |
| `extendY` | `number` | `0` | Khoảng cách dọc của overlay (px) |
| `postion` | `POSITION_TYPE \| POSITION_TYPE[]` | `'right'` | Vị trí overlay |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `zoomScroll` | `EventEmitter<number>` | Phát ra khi magnification thay đổi |
| `zoomPosition` | `EventEmitter<zoomboxCoord>` | Phát ra khi vị trí zoom thay đổi |

## Usage

```html
<!-- Hover mode với lens -->
<tds-zoombox
  [thumbImage]="thumbnailUrl"
  [fullImage]="fullSizeUrl"
  [enableLens]="true"
  [lensWidth]="150"
  [lensHeight]="150"
  [magnification]="2">
</tds-zoombox>

<!-- Toggle mode với overlay -->
<tds-zoombox
  [thumbImage]="thumbnailUrl"
  [fullImage]="fullSizeUrl"
  zoomMode="toggle"
  [enableOverlay]="true"
  [extendX]="10"
  [extendY]="10"
  (zoomScroll)="onZoomChange($event)">
</tds-zoombox>

<!-- Click mode với scroll zoom -->
<tds-zoombox
  [thumbImage]="thumbnailUrl"
  [fullImage]="fullSizeUrl"
  zoomMode="click"
  [enableScrollZoom]="true"
  [scrollStepSize]="0.2"
  [minZoomRatio]="0.5"
  [maxZoomRatio]="3"
  [circularLens]="true">
</tds-zoombox>
```

```typescript
import { TDSZoomBoxModule } from 'tds-ui/zoom-box';

@Component({
  standalone: true,
  imports: [TDSZoomBoxModule],
})
export class MyComponent {
  thumbnailUrl = 'https://example.com/thumb.jpg';
  fullSizeUrl = 'https://example.com/full.jpg';

  onZoomChange(magnification: number) {
    console.log('Zoom level:', magnification);
  }
}
```

## Zoom Modes

- **`hover`**: Zoom khi mouse enter, tắt khi mouse leave
- **`toggle`**: Click để bật/tắt zoom
- **`click`**: Click để bật zoom, mouse leave để tắt
- **`toggle-click`**: Click để bật/tắt zoom, mouse leave để tắt, di chuyển chuột để zoom
- **`hover-freeze`**: Hover để zoom, click để đóng băng/thaw zoom

## Notes

- Cần cung cấp cả `thumbImage` và `fullImage` để component hoạt động
- Khi `enableOverlay = true`, zoom sẽ hiển thị trong popup bên ngoài thay vì lens
- `enableScrollZoom` cho phép điều chỉnh mức zoom bằng chuột
- Có thể đặt vị trí overlay bằng `postion` (lưu ý: typo `postion` thay vì `position` trong cả code và property name)
- Component tự động tính toán tỷ lệ và vị trí zoom dựa trên kích thước ảnh
