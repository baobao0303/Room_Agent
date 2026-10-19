# Timeline

Component hiển thị danh sách sự kiện theo trình tự thời gian với các mode khác nhau.

**Selector:** `tds-timeline`
**Import:** `import { TDSTimelineModule } from 'tds-ui/timeline';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsMode` | `TDSTimelineMode` | `'left'` | Mode hiển thị: `left`, `right`, `alternate`, `custom` |
| `tdsPending` | `string \| boolean \| TemplateRef` | — | Hiển thị item pending ở cuối timeline |
| `tdsPendingDot` | `string \| TemplateRef` | — | Custom dot cho pending item (mặc định là spinner) |
| `tdsReverse` | `boolean` | `false` | Đảo ngược thứ tự hiển thị |

## Timeline Item

**Selector:** `tds-timeline-item` hoặc `[tds-timeline-item]`

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsColor` | `TDSTimelineItemColor` | `'primary'` | Màu dot: `primary`, `secondary`, `info`, `warning`, `error`, `success`, hoặc custom color |
| `tdsLabel` | `string \| TemplateRef` | — | Label hiển thị bên cạnh dot |
| `tdsDot` | `string \| TemplateRef` | — | Custom dot content |
| `tdsPosition` | `TDSTimelinePosition` | — | Vị trí item: `left`, `right` (chỉ dùng với `tdsMode='custom'`) |

## Usage

```html
<!-- Basic timeline (left mode) -->
<tds-timeline>
  <tds-timeline-item>
    <p>Create project structure</p>
    <p>2024-01-01 09:00</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Implement core features</p>
    <p>2024-01-02 14:30</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Testing and deployment</p>
    <p>2024-01-03 10:00</p>
  </tds-timeline-item>
</tds-timeline>

<!-- With colors -->
<tds-timeline>
  <tds-timeline-item tdsColor="success">
    <p>Completed task</p>
  </tds-timeline-item>
  <tds-timeline-item tdsColor="warning">
    <p>In progress</p>
  </tds-timeline-item>
  <tds-timeline-item tdsColor="error">
    <p>Failed task</p>
  </tds-timeline-item>
  <tds-timeline-item tdsColor="info">
    <p>Pending review</p>
  </tds-timeline-item>
</tds-timeline>

<!-- With labels (alternate mode) -->
<tds-timeline>
  <tds-timeline-item [tdsLabel]="'2024-01-01'">
    <p>Project kickoff</p>
  </tds-timeline-item>
  <tds-timeline-item [tdsLabel]="'2024-01-15'">
    <p>First milestone</p>
  </tds-timeline-item>
  <tds-timeline-item [tdsLabel]="'2024-02-01'">
    <p>Second milestone</p>
  </tds-timeline-item>
</tds-timeline>

<!-- Alternate mode -->
<tds-timeline tdsMode="alternate">
  <tds-timeline-item>
    <p>Event 1</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Event 2</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Event 3</p>
  </tds-timeline-item>
</tds-timeline>

<!-- Right mode -->
<tds-timeline tdsMode="right">
  <tds-timeline-item>
    <p>Right aligned item 1</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Right aligned item 2</p>
  </tds-timeline-item>
</tds-timeline>

<!-- Custom mode with manual position -->
<tds-timeline tdsMode="custom">
  <tds-timeline-item tdsPosition="left">
    <p>Left item</p>
  </tds-timeline-item>
  <tds-timeline-item tdsPosition="right">
    <p>Right item</p>
  </tds-timeline-item>
</tds-timeline>

<!-- With pending state -->
<tds-timeline [tdsPending]="true">
  <tds-timeline-item>
    <p>Step 1</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Step 2</p>
  </tds-timeline-item>
</tds-timeline>

<!-- With custom pending text -->
<tds-timeline tdsPending="Loading more events...">
  <tds-timeline-item>
    <p>Event 1</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Event 2</p>
  </tds-timeline-item>
</tds-timeline>

<!-- With custom pending dot -->
<tds-timeline [tdsPending]="true" [tdsPendingDot]="customPendingDot">
  <ng-template #customPendingDot>
    <span>Loading...</span>
  </ng-template>
  <tds-timeline-item>
    <p>Event 1</p>
  </tds-timeline-item>
</tds-timeline>

<!-- Reverse order -->
<tds-timeline [tdsReverse]="true">
  <tds-timeline-item>
    <p>Latest event</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Middle event</p>
  </tds-timeline-item>
  <tds-timeline-item>
    <p>Oldest event</p>
  </tds-timeline-item>
</tds-timeline>

<!-- Custom color -->
<tds-timeline>
  <tds-timeline-item [tdsColor]="'#ff0000'">
    <p>Custom red color</p>
  </tds-timeline-item>
  <tds-timeline-item [tdsColor]="'#00ff00'">
    <p>Custom green color</p>
  </tds-timeline-item>
</tds-timeline>

<!-- With custom dot -->
<tds-timeline>
  <tds-timeline-item [tdsDot]="customIcon">
    <ng-template #customIcon>
      <span class="custom-icon">★</span>
    </ng-template>
    <p>Custom dot icon</p>
  </tds-timeline-item>
</tds-timeline>
```

```typescript
import { TDSTimelineModule, TDSTimelineItemModule } from 'tds-ui/timeline';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  imports: [CommonModule, TDSTimelineModule, TDSTimelineItemModule]
})
export class MyComponent {
  events = [
    { id: 1, title: 'Project kickoff', date: '2024-01-01', color: 'success' },
    { id: 2, title: 'Development started', date: '2024-01-15', color: 'primary' },
    { id: 3, title: 'Testing phase', date: '2024-02-01', color: 'warning' },
    { id: 4, title: 'Deployment', date: '2024-02-15', color: 'error' }
  ];
}
```

```html
<!-- Dynamic timeline -->
<tds-timeline>
  @for (event of events; track event.id) {
    <tds-timeline-item [tdsColor]="event.color">
      <p>{{ event.title }}</p>
      <small>{{ event.date }}</small>
    </tds-timeline-item>
  }
</tds-timeline>
```

## Notes

- `tdsMode='left'`: Tất cả items nằm bên trái
- `tdsMode='right'`: Tất cả items nằm bên phải
- `tdsMode='alternate'`: Items xen kẽ trái-phải
- `tdsMode='custom'`: Tự control position bằng `tdsPosition` trên từng item
- Khi có `tdsLabel` trên bất kỳ item nào, timeline tự động chuyển sang `alternate` mode
- `tdsReverse` đảo ngược thứ tự hiển thị (item cuối cùng hiển thị đầu tiên)
- `tdsPending` hiển thị item loading ở cuối timeline
- `tdsPendingDot` có thể là string hoặc TemplateRef để custom icon
- Màu dot hỗ trợ các preset colors: `primary`, `secondary`, `info`, `warning`, `error`, `success`
- Có thể dùng custom color bằng cách truyền mã màu (VD: `#ff0000`, `rgb(255, 0, 0)`)
- Component tự động thêm class `.tds-timeline-item-last` cho item cuối cùng
- Hỗ trợ RTL (right-to-left)
- Pending item mặc định hiển thị spinner, có thể custom bằng `tdsPendingDot`
