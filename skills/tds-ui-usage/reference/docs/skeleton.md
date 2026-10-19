# Skeleton

Placeholder loading animation thay thế nội dung khi đang tải.

**Selector:** `tds-skeleton`
**Import:** `import { TDSSkeletonModule } from 'tds-ui/skeleton';`
**Export as:** `tdsSkeleton`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsActive` | `boolean` | `false` | Hiệu ứng pulse animation |
| `tdsLoading` | `boolean` | `true` | Hiển thị skeleton (false = hiển thị content) |
| `tdsAvatar` | `boolean \| TDSSkeletonAvatar` | `false` | Hiển thị avatar placeholder |
| `tdsParagraph` | `boolean \| TDSSkeletonParagraph` | `true` | Hiển thị paragraph lines |
| `tdsTitle` | `boolean \| TDSSkeletonTitle` | `true` | Hiển thị title line |
| `tdsRound` | `boolean` | `false` | Bo tròn các dòng |

## TDSSkeletonAvatar Config

```typescript
interface TDSSkeletonAvatar {
  size?: 'sm' | 'md' | 'lg' | number;
  shape?: 'circle' | 'square';
}
```

## TDSSkeletonParagraph Config

```typescript
interface TDSSkeletonParagraph {
  rows?: number;
  width?: number | string | (number | string)[];
}
```

## TDSSkeletonTitle Config

```typescript
interface TDSSkeletonTitle {
  width?: number | string;
}
```

## Usage

```html
<!-- Basic skeleton with default config -->
<tds-skeleton [tdsLoading]="isLoading">
  <div>Nội dung thực tế khi đã tải xong</div>
</tds-skeleton>

<!-- With animation -->
<tds-skeleton [tdsLoading]="isLoading" [tdsActive]="true">
  <div class="content">Content here</div>
</tds-skeleton>

<!-- With avatar -->
<tds-skeleton
  [tdsLoading]="isLoading"
  [tdsAvatar]="true"
  [tdsActive]="true">
  <div>User profile content</div>
</tds-skeleton>

<!-- Custom paragraph rows -->
<tds-skeleton
  [tdsLoading]="isLoading"
  [tdsParagraph]="{ rows: 4, width: '80%' }">
  <div>Content</div>
</tds-skeleton>

<!-- Rounded skeleton -->
<tds-skeleton
  [tdsLoading]="isLoading"
  [tdsRound]="true"
  [tdsActive]="true">
  <div>Content</div>
</tds-skeleton>
```

```typescript
import { TDSSkeletonModule } from 'tds-ui/skeleton';

@Component({
  standalone: true,
  imports: [TDSSkeletonModule],
  template: `...`
})
export class MyComponent {
  isLoading = true;
}
```

## Skeleton Element

**Selector:** `tds-skeleton-element`
**Import:** `import { TDSSkeletonElementDirective } from 'tds-ui/skeleton';`

### Element Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsType` | `'button' \| 'input' \| 'avatar' \| 'image'` | — | Loại skeleton element |
| `tdsActive` | `boolean` | `false` | Hiệu ứng pulse animation |
| `tdsBlock` | `boolean` | `false` | Block display |

### Button Type Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsShape` | `'round' \| 'circle' \| 'default'` | `'round'` | Hình dáng button |
| `tdsSize` | `'sm' \| 'md' \| 'lg'` | `'md'` | Kích thước |

### Avatar Type Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsShape` | `'circle' \| 'square'` | `'circle'` | Hình dáng avatar |
| `tdsSize` | `'sm' \| 'md' \| 'lg' \| number` | `'md'` | Kích thước |

### Input Type Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `'sm' \| 'md' \| 'lg'` | `'md'` | Kích thước |

### Image Type

Không có additional inputs, chỉ hiển thị placeholder image mặc định.

```html
<!-- Button skeleton -->
<tds-skeleton-element tdsType="button" [tdsSize]="'lg'"></tds-skeleton-element>

<!-- Avatar skeleton -->
<tds-skeleton-element tdsType="avatar" [tdsShape]="'square'" [tdsSize]="64"></tds-skeleton-element>

<!-- Input skeleton -->
<tds-skeleton-element tdsType="input" [tdsSize]="'sm'"></tds-skeleton-element>

<!-- Image skeleton -->
<tds-skeleton-element tdsType="image"></tds-skeleton-element>

<!-- With animation -->
<tds-skeleton-element tdsType="button" [tdsActive]="true"></tds-skeleton-element>
```

## Notes

- `tdsLoading="true"` (default) = hiển thị skeleton, `false` = render content slot
- `tdsActive="true"` để có animation shimmer (pulse effect)
- Config objects cho avatar, paragraph, title cho phép custom dimensions
- Default: 1 title, 3 paragraph rows, không avatar
- Skeleton element components được sử dụng riêng biệt hoặc thông qua main skeleton component
- Avatar size có thể là preset (`sm`, `md`, `lg`) hoặc số cụ thể (pixels)

## Skeleton Element Sub-Components

Các sub-components cho từng loại skeleton element, dùng chung selector `tds-skeleton-element` với `tdsType`:

### Skeleton Element Button (`tds-skeleton-element[tdsType="button"]`)
- Component: `TDSSkeletonElementButtonComponent`
- Inputs: `tdsShape` (`'round' | 'circle' | 'default'`, default: `'round'`), `tdsSize` (`'sm' | 'md' | 'lg'`, default: `'md'`)

### Skeleton Element Avatar (`tds-skeleton-element[tdsType="avatar"]`)
- Component: `TDSSkeletonElementAvatarComponent`
- Inputs: `tdsShape` (`'circle' | 'square'`, default: `'circle'`), `tdsSize` (`'sm' | 'md' | 'lg' | number`, default: `'md'`)

### Skeleton Element Input (`tds-skeleton-element[tdsType="input"]`)
- Component: `TDSSkeletonElementInputComponent`
- Inputs: `tdsSize` (`'sm' | 'md' | 'lg'`, default: `'md'`)

### Skeleton Element Image (`tds-skeleton-element[tdsType="image"]`)
- Component: `TDSSkeletonElementImageComponent`
- No additional inputs

## Implementation Notes

- `tdsActive` and `tdsLoading` on `tds-skeleton` do **not** use `@InputBoolean()` decorator — they accept plain boolean values only. Ensure template binding uses `[tdsActive]="true"` (bracket syntax) rather than `tdsActive="true"`.
- `tdsBlock` on `tds-skeleton-element` does use `@InputBoolean()`.
- All skeleton element sub-components are standalone and matched via attribute selector on `tdsType`.
