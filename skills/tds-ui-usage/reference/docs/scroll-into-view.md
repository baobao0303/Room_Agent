# Scroll Into View

Component container hỗ trợ scroll đến phần tử con được chỉ định với animation mượt mà.

**Selector:** `tds-scroll-into-view`
**Directive:** `[tds-scroll-into-view]`
**Import:** `import { TDSScrollIntoViewModule } from 'tds-ui/scroll-into-view';`

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `disabled` | `boolean` | `false` | Vô hiệu hóa chức năng scroll |
| `scrollID` | `any` | `undefined` | ID định danh cho phần tử để scroll đến |

## Key Outputs

| Output | Type | Description |
|--------|------|-------------|
| N/A | N/A | Không có outputs được định nghĩa |

## Methods

| Method | Parameters | Description |
|--------|-----------|-------------|
| `scrollIntoView(dataID)` | `dataID: any` | Scroll đến phần tử có `scrollID` tương ứng |
| `getScrollID()` | - | Lấy `scrollID` của directive |
| `getElement()` | - | Lấy `ElementRef` của phần tử |

## Usage

```html
<!-- Container với các item con -->
<tds-scroll-into-view #scrollContainer>
  <div [tds-scroll-into-view] [scrollID]="'section1'">Section 1</div>
  <div [tds-scroll-into-view] [scrollID]="'section2'">Section 2</div>
  <div [tds-scroll-into-view] [scrollID]="'section3'">Section 3</div>
</tds-scroll-into-view>

<!-- Buttons để trigger scroll -->
<button (click)="scrollContainer.scrollIntoView('section1')">Go to Section 1</button>
<button (click)="scrollContainer.scrollIntoView('section2')">Go to Section 2</button>
<button (click)="scrollContainer.scrollIntoView('section3')">Go to Section 3</button>

<!-- Với disabled state -->
<div [tds-scroll-into-view] [scrollID]="'section4'" [disabled]="true">Disabled Section</div>
```

```typescript
import { TDSScrollIntoViewModule } from 'tds-ui/scroll-into-view';
import { Component, ViewChild } from '@angular/core';

@Component({
  selector: 'app-scroll-into-view-demo',
  standalone: true,
  imports: [TDSScrollIntoViewModule],
  template: `
    <div class="demo-container">
      <!-- Navigation buttons -->
      <div class="nav-buttons">
        <button tds-button (click)="scrollTo('intro')">Introduction</button>
        <button tds-button (click)="scrollTo('features')">Features</button>
        <button tds-button (click)="scrollTo('pricing')">Pricing</button>
        <button tds-button (click)="scrollTo('contact')">Contact</button>
      </div>

      <!-- Scroll container -->
      <tds-scroll-into-view #scrollView class="content-area">
        <section [tds-scroll-into-view] [scrollID]="'intro'" class="section">
          <h2>Introduction</h2>
          <p>Content goes here...</p>
        </section>

        <section [tds-scroll-into-view] [scrollID]="'features'" class="section">
          <h2>Features</h2>
          <p>Content goes here...</p>
        </section>

        <section [tds-scroll-into-view] [scrollID]="'pricing'" class="section">
          <h2>Pricing</h2>
          <p>Content goes here...</p>
        </section>

        <section [tds-scroll-into-view] [scrollID]="'contact'" [disabled]="isContactDisabled" class="section">
          <h2>Contact</h2>
          <p>Content goes here...</p>
        </section>
      </tds-scroll-into-view>
    </div>
  `
})
export class ScrollIntoViewDemoComponent {
  @ViewChild('scrollView') scrollView!: any;

  isContactDisabled = false;

  scrollTo(sectionId: string): void {
    this.scrollView.scrollIntoView(sectionId);
  }
}
```

## Notes

- Component sử dụng `ContentChildren` để lấy danh sách các phần tử con có directive `[tds-scroll-into-view]`
- Scroll animation sử dụng `behavior: "smooth"` và `block: "end"` mặc định
- Container có class mặc định: `block relative w-full overflow-auto`
- Hỗ trợ vô hiệu hóa từng item con riêng lẻ với input `disabled`
- Mỗi phần tử con cần có `scrollID` duy nhất để có thể scroll đến

## Directive vs Component

- **Directive `[tds-scroll-into-view]`**: Áp dụng cho các phần tử con cần scroll đến
- **Component `tds-scroll-into-view`**: Container bao bọc các phần tử con

## Host Classes

Container component áp dụng các classes:
- `block` - display: block
- `relative` - position: relative
- `w-full` - width: 100%
- `overflow-auto` - overflow: auto
