# Avatar

Hiển thị avatar với hình ảnh, icon, hoặc text. Hỗ trợ nhiều kích thước và hình dáng khác nhau.

**Selector:** `tds-avatar`
**Import:** `import { TDSAvatarModule } from 'tds-ui/avatar';`
**Export as:** `tdsAvatar`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSrc` | `string` | — | URL hình ảnh avatar |
| `tdsSrcSet` | `string` | — | Srcset attribute cho responsive images |
| `tdsSrcPlaceholder` | `string` | — | URL hình ảnh placeholder khi lỗi |
| `alt` | `string` | — | Alt text cho hình ảnh |
| `text` | `string` | — | Text hiển thị (khi không có hình) |
| `icon` | `string` | — | Icon class (khi không có hình) |
| `shape` | `'square' \| 'circle'` | `'circle'` | Hình dáng avatar |
| `size` | `'sm' \| 'md' \| 'lg' \| 'xl' \| number` | `'md'` | Kích thước (có thể truyền số px) |
| `gap` | `number` | `4` | Khoảng cách giữa text và viền (px) |
| `isAvatar` | `boolean` | `true` | Loại placeholder (true = user, false = image) |
| `tdsBordered` | `boolean` | `false` | Hiển thị viền |
| `tdsTheme` | `'default' \| 'light' \| 'dark'` | `'default'` | Theme |
| `attrLoading` | `'eager' \| 'lazy'` | `'eager'` | Loading attribute cho hình ảnh |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| `error` | `EventEmitter<Event>` | Emit khi hình ảnh load lỗi |

## Usage

```html
<!-- Hình ảnh -->
<tds-avatar tdsSrc="https://example.com/avatar.jpg" alt="User Avatar"></tds-avatar>

<!-- Text -->
<tds-avatar text="John Doe"></tds-avatar>

<!-- Icon -->
<tds-avatar icon="tdsi-user-fill"></tds-avatar>

<!-- Custom size -->
<tds-avatar [size]="64" text="AB"></tds-avatar>

<!-- Square shape -->
<tds-avatar shape="square" tdsSrc="https://example.com/avatar.jpg"></tds-avatar>

<!-- With border -->
<tds-avatar [tdsBordered]="true" text="User"></tds-avatar>

<!-- Placeholder khi lỗi -->
<tds-avatar 
  tdsSrc="invalid-url.jpg" 
  tdsSrcPlaceholder="placeholder.jpg"
  alt="User">
</tds-avatar>
```

```typescript
import { TDSAvatarModule } from 'tds-ui/avatar';

@Component({
  standalone: true,
  imports: [TDSAvatarModule],
})
export class MyComponent {
  avatarUrl = 'https://example.com/avatar.jpg';
  
  onAvatarError(event: Event) {
    console.log('Avatar load error', event);
  }
}
```

## Avatar Group

**Selector:** `tds-avatar-group`
**Import:** `import { TDSAvatarModule } from 'tds-ui/avatar';`

```html
<tds-avatar-group>
  <tds-avatar tdsSrc="user1.jpg"></tds-avatar>
  <tds-avatar tdsSrc="user2.jpg"></tds-avatar>
  <tds-avatar text="+5"></tds-avatar>
</tds-avatar-group>
```

## Notes

- Avatar tự động hiển thị placeholder khi hình ảnh load lỗi
- `isAvatar = true`: hiển thị placeholder user (mặc định)
- `isAvatar = false`: hiển thị placeholder image
- Text được tự động rút gọn còn 2 ký tự và scale để vừa với avatar
- Kích thước có thể là preset (`sm`, `md`, `lg`, `xl`) hoặc số cụ thể (pixels)
