# QR Code

Thành phần hiển thị mã QR với các tính năng mở rộng như download, expand preview, và quản lý trạng thái active/expired/loading.

**Selector:** `tds-qrcode`
**Import:** `import { TDSQRCodeModule } from 'tds-ui/qr-code';`
**Export as:** `tdsQRCode`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsValue` | `string` | `''` | Giá trị để mã hóa thành QR code |
| `tdsSize` | `number \| 'xs'` | `160` | Kích thước QR code (px) hoặc `'xs'` cho size nhỏ (50px) |
| `tdsColor` | `string` | `'#000000'` | Màu sắc của QR code |
| `tdsIcon` | `string` | `''` | Icon class hiển thị ở giữa QR code |
| `tdsIconSize` | `number` | `40` | Kích thước icon ở giữa (px) |
| `tdsBordered` | `boolean` | `true` | Hiển thị viền bao quanh QR code |
| `tdsStatus` | `'active' \| 'expired' \| 'loading'` | `'active'` | Trạng thái hiển thị |
| `tdsLevel` | `'L' \| 'M' \| 'Q' \| 'H'` | `'M'` | Mức độ sửa lỗi QR (Low, Medium, Quartile, High) |
| `tdsIconDownload` | `string` | `'tdsi-download-fill'` | Icon class cho nút download |
| `tdsIconExpand` | `string` | `'tdsi-image-expand-line'` | Icon class cho nút expand |
| `tdsFilename` | `string` | `'qr-code'` | Tên file khi download QR code |
| `tdsHiddenDownload` | `boolean` | `false` | Ẩn nút download |
| `tdsHiddenExpand` | `boolean` | `false` | Ẩn nút expand preview |
| `tdsBootECC` | `boolean` | `true` | Sử dụng Boost Error Correction |
| `tdsPadding` | `number` | `8` | Padding khi expand preview (px) |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `tdsRefresh` | `EventEmitter<string>` | Phát sinh khi click nút refresh (khi status là expired) |

## Usage

```html
<!-- QR code cơ bản -->
<tds-qrcode [tdsValue]="qrData"></tds-qrcode>

<!-- QR code với màu sắc tùy chỉnh -->
<tds-qrcode
  [tdsValue]="'https://example.com'"
  [tdsColor]="'#ff0000'"
  [tdsSize]="200">
</tds-qrcode>

<!-- QR code với logo ở giữa -->
<tds-qrcode
  [tdsValue]="'https://example.com'"
  [tdsIcon]="'my-logo'"
  [tdsIconSize]="50"
  [tdsSize]="250">
</tds-qrcode>

<!-- QR code nhỏ (xs size) -->
<tds-qrcode
  [tdsValue]="'https://example.com'"
  [tdsSize]="'xs'">
</tds-qrcode>

<!-- QR code với trạng thái loading -->
<tds-qrcode
  [tdsValue]="qrData"
  [tdsStatus]="'loading'">
</tds-qrcode>

<!-- QR code expired -->
<tds-qrcode
  [tdsValue]="expiredQrData"
  [tdsStatus]="'expired'"
  (tdsRefresh)="refreshQR()">
</tds-qrcode>

<!-- QR code ẩn các nút chức năng -->
<tds-qrcode
  [tdsValue]="'https://example.com'"
  [tdsHiddenDownload]="true"
  [tdsHiddenExpand]="true"
  [tdsBordered]="false">
</tds-qrcode>

<!-- QR code với mức độ sửa lỗi cao -->
<tds-qrcode
  [tdsValue]="'https://example.com'"
  [tdsLevel]="'H'"
  [tdsFilename]="'my-qrcode'">
</tds-qrcode>
```

```typescript
import { TDSQRCodeModule } from 'tds-ui/qr-code';

@Component({
  standalone: true,
  imports: [TDSQRCodeModule],
})
export class MyComponent {
  qrData = 'https://example.com';
  expiredQrData = 'expired-data';

  refreshQR(): void {
    console.log('Refreshing QR code...');
    // Logic để tạo mới QR code
    this.expiredQrData = 'new-qr-data';
  }
}
```

## Notes

- **Responsive**: QR code tự động vẽ lại khi `tdsValue`, `tdsIcon`, `tdsLevel`, `tdsSize`, `tdsIconSize`, hoặc `tdsColor` thay đổi
- **SSR Support**: Component tự động detect môi trường browser/server để tránh lỗi canvas trong SSR
- **Download**: Click nút download sẽ tải QR code về dưới dạng file PNG với tên file theo `tdsFilename`
- **Expand Preview**: Click nút expand sẽ mở preview hình ảnh QR code với padding trắng xung quanh
- **Trạng thái**:
  - `active`: Hiển thị QR code bình thường với các nút chức năng
  - `loading`: Hiển thị spinner loading
  - `expired`: Hiển thị thông báo expired và nút refresh
- **Size xs**: Khi `tdsSize="xs"`, QR code sẽ có kích thước 50px và ẩn nút download
- **Error Correction Levels**:
  - `L`: Low (~7% correction)
  - `M`: Medium (~15% correction) - default
  - `Q`: Quartile (~25% correction)
  - `H`: High (~30% correction)
