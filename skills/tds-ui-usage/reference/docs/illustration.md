# Illustration

Thành phần minh họa (illustration) động theo theme, tự động load SVG từ CDN và cache. Hỗ trợ light/dark theme với fallback mechanism.

**Selector:** `tds-illustration`
**Import:** `import { TDSIllustrationModule } from 'tds-ui/illustration';`
**Export as:** `tdsIllustration`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsName` | `string` | - | Tên illustration (không bao gồm extension) |
| `tdsFallbackTemplate` | `TemplateRef \| string` | `'Không tìm thấy ảnh minh họa'` | Template hoặc text hiển thị khi load lỗi |

## Key Outputs

Không có outputs.

## Usage

```html
<!-- Illustration cơ bản -->
<tds-illustration [tdsName]="'empty-state'"></tds-illustration>

<!-- Illustration với custom fallback -->
<tds-illustration 
  [tdsName]="'no-data'" 
  [tdsFallbackTemplate]="customFallback">
</tds-illustration>

<ng-template #customFallback>
  <div class="custom-fallback">
    <i class="tdsi-warning-fill"></i>
    <span>Không thể tải minh họa</span>
  </div>
</ng-template>
```

```typescript
import { TDSIllustrationModule } from 'tds-ui/illustration';

@Component({
  standalone: true,
  imports: [TDSIllustrationModule],
})
export class MyComponent {
  illustrationName = 'empty-cart';
}
```

## Configuration

Cấu hình base URL và fallback bằng `TDS_ILLUSTRATION_CONFIG`.

**Import:** `import { TDS_ILLUSTRATION_CONFIG, TDSIllustrationConfig } from 'tds-ui/illustration';`

```typescript
import { TDS_ILLUSTRATION_CONFIG, TDSIllustrationConfig } from 'tds-ui/illustration';

const customConfig: TDSIllustrationConfig = {
  baseUrl: 'https://cdn.example.com/illustrations',
  fallback: 'default'
};

@Component({
  standalone: true,
  imports: [TDSIllustrationModule],
  providers: [
    { provide: TDS_ILLUSTRATION_CONFIG, useValue: customConfig }
  ]
})
export class MyComponent {}
```

**Mặc định:**
- `baseUrl`: `https://static-tds-public-projects.tds.local/assets/empty-state`
- `fallback`: `default`

## Service

Dùng `TDSIllustrationService` để load illustrations programmatically.

**Import:** `import { TDSIllustrationService } from 'tds-ui/illustration';`

```typescript
constructor(private illustrationService: TDSIllustrationService) {}

loadIllustration() {
  this.illustrationService.get('empty-state').subscribe({
    next: (svg: SafeHtml) => {
      // SVG loaded successfully
      console.log('SVG loaded:', svg);
    },
    error: () => {
      // Failed to load (tried both dark and light theme)
      console.error('Failed to load illustration');
    }
  });
}
```

## Theme Support

Component tự động load illustration theo theme hiện tại:
- **Light theme**: `{baseUrl}/light/{name}.svg`
- **Dark theme**: `{baseUrl}/dark/{name}.svg`

**Fallback mechanism:**
1. Thử load illustration theo theme hiện tại
2. Nếu lỗi và theme là `dark`, thử fallback sang `light`
3. Nếu vẫn lỗi, hiển thị `tdsFallbackTemplate`

## File Structure

Illustrations phải được tổ chức theo cấu trúc sau:

```
{baseUrl}/
├── light/
│   ├── empty-state.svg
│   ├── no-data.svg
│   └── ...
└── dark/
    ├── empty-state.svg
    ├── no-data.svg
    └── ...
```

## SVG Normalization

Service tự động:
- Loại bỏ thuộc tính `width` và `height` từ SVG
- Cache loaded SVGs để tránh redundant requests
- Sanitize HTML để bypass Angular security

## Notes

- Component sử dụng `effect()` để tự động react khi `tdsName` thay đổi
- SVGs được cache trong service, cùng một illustration chỉ load 1 lần
- Hỗ trợ Angular signals (`tdsName` là signal input)
- Hiển thị spinner khi đang load illustration
- Illustrations responsive theo theme changes
