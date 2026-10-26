# CSS Utility Classes

tds-ui cung cấp các utility CSS classes dạng Tailwind qua `gen/alias.scss`. Các class này được include tự động khi dùng tds-ui, không cần import thêm.

Tất cả classes đều nằm trong Tailwind `@layer utilities` và hỗ trợ dark mode tự động.

## Naming Pattern

Pattern chung: `tds-color-{type}-{semantic}[-variant]`

Ví dụ: `tds-color-text-primary`, `tds-color-background-error-subtle-hover`

## Color Utilities

### Text Color — `tds-color-text-*`

Áp dụng màu chữ.

| Semantic Value | Ý nghĩa |
|----------------|---------|
| `brand-primary` | Màu brand chính |
| `primary` | Text chính (neutral-900) |
| `secondary` | Text phụ (neutral-500) |
| `tertiary` | Text cấp 3 (neutral-600) |
| `quaternary` | Text cấp 4 (neutral-700) |
| `placeholder` | Placeholder (neutral-400) |
| `inactive` | Không hoạt động (neutral-400) |
| `success` | Thành công (green-500) |
| `info` | Thông tin (sky-500) |
| `warning` | Cảnh báo (amber-500) |
| `error` | Lỗi (red-500) |
| `accent-1` | Nhấn mạnh (orange-500) |
| `disable` | Bị vô hiệu (neutral-300) |
| `white` | Trắng |
| `interactive` | Có thể tương tác (sky-500) |
| `interactive-hover` | Hover link (sky-600) |
| `interactive-pressed` | Pressed link (sky-600) |
| `interactive-visited` | Đã truy cập (indigo-500) |

```html
<span class="tds-color-text-primary">Text chính</span>
<span class="tds-color-text-error">Text lỗi</span>
<a class="tds-color-text-interactive hover:tds-color-text-interactive-hover">Link</a>
```

### Icon Color — `tds-color-icon-*`

Áp dụng màu icon. Cùng giá trị semantic với `text` (trừ `placeholder`).

```html
<i class="tds-color-icon-success tds-icon-check"></i>
```

### Background Color — `tds-color-background-*`

#### Semantic Backgrounds

Màu nền theo ngữ cảnh, có 2 mức độ: `-subtle` (đậm) và `-minimal` (nhạt).

Semantic colors: `primary`, `secondary`, `success`, `info`, `warning`, `error`, `accent-1`

| Variant | Mô tả |
|---------|-------|
| `{color}-subtle` | Nền đậm |
| `{color}-minimal` | Nền nhạt |
| `{color}-subtle-hover` | Hover nền đậm |
| `{color}-minimal-hover` | Hover nền nhạt |
| `{color}-subtle-pressed` | Pressed nền đậm |
| `{color}-minimal-pressed` | Pressed nền nhạt |

```html
<div class="tds-color-background-success-subtle">Nền success đậm</div>
<div class="tds-color-background-info-minimal">Nền info nhạt</div>
```

#### Neutral Backgrounds

| Class | Mô tả |
|-------|-------|
| `tds-color-background-neutral-boldest` | Neutral đậm nhất |
| `tds-color-background-neutral-bold` | Neutral đậm |
| `tds-color-background-neutral-subtle` | Neutral vừa |
| `tds-color-background-neutral-minimal` | Neutral nhạt |
| `tds-color-background-neutral-minimalist` | Neutral nhạt nhất |

#### Utility Backgrounds

| Class | Mô tả |
|-------|-------|
| `tds-color-background-disable` | Nền disabled |
| `tds-color-background-white` | Nền trắng |
| `tds-color-background-black` | Nền đen |
| `tds-color-background-neutral-lighten` | Nền sáng |

### Border Color — `tds-color-border-*`

| Semantic Value | Ý nghĩa |
|----------------|---------|
| `brand-primary` | Viền brand chính |
| `primary` | Viền chính (neutral-200) |
| `secondary` | Viền phụ (neutral-100) |
| `tertiary` | Viền mờ (neutral-50) |
| `neutral-subtle` | Viền neutral rõ |
| `neutral-minimal` | Viền neutral vừa |
| `neutral-minimalist` | Viền neutral mờ |
| `success`, `info`, `warning`, `error`, `accent-1` | Viền theo ngữ cảnh |
| `disable` | Viền disabled |
| `white`, `black` | Viền trắng/đen |

```html
<div class="border tds-color-border-error">Viền lỗi</div>
```

### Surface Color — `tds-color-surface-*`

Màu nền theo elevation level. Tự động thay đổi giữa light/dark mode.

| Level | Mô tả | Có hover variant |
|-------|-------|-------------------|
| `lighten` | Nền sáng nhất | Không |
| `lowest` | Elevation thấp nhất | Có (`-hover`) |
| `low` | Elevation thấp | Có (`-hover`) |
| `medium` | Elevation trung bình | Có (`-hover`) |
| `high` | Elevation cao | Có (`-hover`) |
| `highest` | Elevation cao nhất | Có (`-hover`) |
| `sunken` | Nền lõm (inset) | Không |

```html
<div class="tds-color-surface-low">Card nền thấp</div>
<div class="tds-color-surface-medium-hover">Hover nền trung bình</div>
```

### Overlay & Ring

```html
<!-- Overlay đen 40% opacity -->
<div class="tds-color-overlay-default fixed inset-0"></div>

<!-- Ring focus 20% opacity -->
<div class="ring-2 tds-color-ring-error">Focus ring lỗi</div>
```

| Class | Mô tả |
|-------|-------|
| `tds-color-overlay-default` | Overlay đen 40% opacity |
| `tds-color-ring-primary` | Ring primary 20% opacity |
| `tds-color-ring-error` | Ring error 20% opacity |
| `tds-color-ring-info` | Ring info 20% opacity |
| `tds-color-ring-warning` | Ring warning 20% opacity |
| `tds-color-ring-success` | Ring success 20% opacity |
| `tds-color-ring-accent-1` | Ring accent 20% opacity |

## Theme System

tds-ui hỗ trợ 5 theme màu. Theme chỉ thay đổi primary/secondary color scales, các semantic colors (success, error, warning, info) giữ nguyên.

### Áp dụng theme

Thêm class `tds-theme-color-{name}` vào `<body>` hoặc container bất kỳ:

```html
<body class="tds-theme-color-blue">
  <!-- Nội dung app -->
</body>
```

### Themes available

| Theme | Class | Mô tả |
|-------|-------|-------|
| Blue (default) | `tds-theme-color-blue` | Màu xanh dương |
| Green | `tds-theme-color-green` | Màu xanh lá |
| Orange | `tds-theme-color-orange` | Màu cam |
| Red | `tds-theme-color-red` | Màu đỏ |
| Yellow | `tds-theme-color-yellow` | Màu vàng |

### Dark Mode

Dark mode tự động hoạt động qua Tailwind `dark:` variant. Các utility classes đều có giá trị cho cả light và dark mode — không cần thêm class riêng.

```html
<!-- Tự động đổi màu khi dark mode -->
<span class="tds-color-text-primary">Text</span>
<div class="tds-color-surface-low">Surface</div>
```

## Scrollbar Utilities

| Class | Mô tả | Kích thước |
|-------|-------|------------|
| `tds-custom-scroll` | Scrollbar chuẩn (áp dụng cho body mặc định) | 10px |
| `tds-panel-scroll` | Scrollbar mỏng cho panel nội bộ | 4px |
| `tds-table-hide-scrollbar` | Ẩn scrollbar background trong table | — |

```html
<div class="tds-custom-scroll overflow-auto">Nội dung dài...</div>
<div class="tds-panel-scroll overflow-auto">Panel nội bộ...</div>
```

Lưu ý: `tds-custom-scroll` đã được áp dụng cho `body` mặc định (trừ iOS hoặc khi có class `tds-disabled-custom-scroll`).

## Ví dụ Tổng hợp

### Card với semantic colors

```html
<div class="rounded-lg border p-4 tds-color-surface-low tds-color-border-primary">
  <h3 class="tds-color-text-primary font-semibold">Tiêu đề</h3>
  <p class="tds-color-text-secondary mt-1">Mô tả phụ</p>
  <span class="inline-block mt-2 px-2 py-1 rounded tds-color-background-success-minimal tds-color-text-success text-sm">
    Thành công
  </span>
</div>
```

### Status badge

```html
<span class="px-2 py-0.5 rounded text-xs tds-color-background-error-subtle tds-color-text-white">
  Lỗi
</span>

<span class="px-2 py-0.5 rounded text-xs tds-color-background-warning-minimal tds-color-text-warning">
  Cảnh báo
</span>
```

### Interactive container

```html
<div class="p-3 rounded tds-color-surface-lowest hover:tds-color-surface-lowest-hover
            border tds-color-border-secondary cursor-pointer transition-colors">
  Hover để thấy đổi nền
</div>
```
