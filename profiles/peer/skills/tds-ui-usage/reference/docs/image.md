# Image

Thành phần hình ảnh với khả năng xem trước (preview), hỗ trợ placeholder và fallback. Dùng directive selector trên thẻ `<img>`.

**Selector:** `img[tds-image]`
**Import:** `import { TDSImageModule } from 'tds-ui/image';`
**Export as:** `tdsImage`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSrc` | `string` | `''` | Đường dẫn hình ảnh (sẽ được prepend với `TDS_BASE_URL_IMAGE` nếu có) |
| `srcset` | `string \| null` | `null` | Thuộc tính srcset cho responsive images |
| `disablePreview` | `boolean` | `false` | Vô hiệu hóa tính năng preview khi click vào ảnh |
| `fallback` | `string \| null` | `null` | Ảnh hiển thị khi load ảnh gốc lỗi |
| `placeholder` | `string \| null` | `null` | Ảnh hiển thị trong khi đang load |

## Key Outputs

Không có outputs - directive kích hoạt preview service khi click.

## Usage

```html
<!-- Image thường với preview -->
<img tds-image [tdsSrc]="imageUrl" alt="Product image" />

<!-- Image với placeholder và fallback -->
<img tds-image 
     [tdsSrc]="imageUrl" 
     [placeholder]="'/assets/placeholder.png'"
     [fallback]="'/assets/error.png'" />

<!-- Image với srcset -->
<img tds-image 
     [tdsSrc]="imageSrc" 
     [srcset]="imageSrcSet" />

<!-- Vô hiệu hóa preview -->
<img tds-image [tdsSrc]="imageUrl" [disablePreview]="true" />
```

```typescript
import { TDSImageDirective } from 'tds-ui/image';
import { TDS_BASE_URL_IMAGE } from 'tds-ui/image';

@Component({
  standalone: true,
  imports: [TDSImageDirective],
  providers: [
    { provide: TDS_BASE_URL_IMAGE, useValue: 'https://cdn.example.com/images' }
  ]
})
export class MyComponent {
  imageUrl = 'product-123.jpg';
  imageSrcSet = 'product-123-small.jpg 480w, product-123.jpg 1080w';
}
```

## Image Group

Sử dụng `tds-image-group` để nhóm nhiều ảnh lại và preview chúng như một gallery.

**Selector:** `tds-image-group`
**Import:** `import { TDSImageGroupComponent } from 'tds-ui/image';`
**Export as:** `tdsImageGroup`

```html
<tds-image-group>
  <img tds-image [tdsSrc]="image1" />
  <img tds-image [tdsSrc]="image2" />
  <img tds-image [tdsSrc]="image3" />
</tds-image-group>
```

## Preview Service

Dùng `TDSImageService` để programmatically mở image preview.

**Import:** `import { TDSImageService } from 'tds-ui/image';`

```typescript
constructor(private imageService: TDSImageService) {}

openPreview() {
  const images: TDSImage[] = [
    { src: 'image1.jpg' },
    { src: 'image2.jpg', alt: 'Description' }
  ];
  
  const options: TDSImagePreviewOptions = {
    zoom: 1,
    rotate: 0,
    activeIndex: 0,
    maskClosable: true,
    keyboard: true
  };
  
  const previewRef = this.imageService.preview(images, options);
  
  // Control preview
  previewRef.switchTo(1); // Switch to image at index 1
  previewRef.next(); // Next image
  previewRef.prev(); // Previous image
  previewRef.close(); // Close preview
}
```

## Preview Options

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| `zoom` | `number` | `1` | Mức zoom ban đầu |
| `rotate` | `number` | `0` | Góc xoay ban đầu (độ) |
| `activeIndex` | `number` | `0` | Index của ảnh hiển thị đầu tiên |
| `maskClosable` | `boolean` | `true` | Đóng preview khi click vào mask |
| `keyboard` | `boolean` | `true` | Cho phép điều khiển bằng bàn phím |
| `noAnimation` | `boolean` | `false` | Vô hiệu hóa animation |
| `closeOnNavigation` | `boolean` | `true` | Đóng preview khi navigate |
| `zIndex` | `number` | `1000` | Z-index của preview overlay |
| `direction` | `Direction` | - | Direction (ltr/rtl) |
| `operations` | `TDSImageContainerOperation[]` | `[]` | Custom operations |

## Notes

- Directive tự động quản lý trạng thái loading/error với placeholder và fallback
- Click vào ảnh để mở preview (gallery mode nếu trong image group)
- Preview hỗ trợ: zoom in/out, rotate left/right, drag to move, next/prev
- Hỗ trợ RTL direction
- Tự động prepend `TDS_BASE_URL_IMAGE` vào `tdsSrc` nếu không phải URL đầy đủ hoặc base64
