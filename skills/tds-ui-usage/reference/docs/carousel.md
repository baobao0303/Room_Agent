# Carousel

Carousel component với hỗ trợ multiple effects, auto-play, swipe gestures và customizable dot positions.

**Selector:** `tds-carousel`, `[tds-carousel-content]`
**Import:** `import { TDSCarouselModule } from 'tds-ui/carousel';`
**Export as:** `tdsCarousel`, `tdsCarouselContent`

## Key Inputs

### TDSCarouselComponent (tds-carousel)

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsEffect` | `'scrollx' \| 'fade' \| string` | `'scrollx'` | Effect chuyển slide: `scrollx` (horizontal scroll), `fade` (opacity fade) |
| `tdsEnableSwipe` | `boolean` | `true` | Bật/tắt swipe gesture để chuyển slide |
| `tdsDots` | `boolean` | `true` | Hiển thị navigation dots |
| `tdsAutoPlay` | `boolean` | `false` | Tự động chuyển slide |
| `tdsAutoPlaySpeed` | `number` | `3000` | Thời gian giữa các auto-play transitions (ms) |
| `tdsTransitionSpeed` | `number` | `500` | Thời gian transition animation (ms) |
| `tdsDotPosition` | `'top' \| 'bottom' \| 'left' \| 'right'` | `'bottom'` | Vị trí hiển thị dots |
| `tdsDotRender` | `TemplateRef<{ $implicit: number }>` | - | Custom template cho dot |
| `tdsStrategyOptions` | `any` | `undefined` | Options truyền vào strategy (custom strategies) |

### TDSCarouselContentDirective ([tds-carousel-content])

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| N/A | N/A | N/A | Directive marker cho carousel content slides |

## Key Outputs

### TDSCarouselComponent

| Output | Type | Description |
|--------|------|-------------|
| `tdsBeforeChange` | `EventEmitter<FromToInterface>` | Emit trước khi chuyển slide với `{ from, to }` |
| `tdsAfterChange` | `EventEmitter<number>` | Emit sau khi chuyển slide với index mới |

## Key Methods

### TDSCarouselComponent

| Method | Parameters | Description |
|--------|-----------|-------------|
| `next` | - | Chuyển đến slide tiếp theo |
| `pre` | - | Chuyển đến slide trước đó |
| `goTo` | `index: number` | Chuyển đến slide cụ thể theo index |

## Interfaces

### FromToInterface

```typescript
interface FromToInterface {
  from: number;  // Index hiện tại
  to: number;    // Index sẽ chuyển đến
}
```

## Usage

```html
<!-- Basic carousel with scrollx effect -->
<tds-carousel [tdsAutoPlay]="true" [tdsAutoPlaySpeed]="3000">
  <div tds-carousel-content>
    <img src="slide1.jpg" alt="Slide 1">
  </div>
  <div tds-carousel-content>
    <img src="slide2.jpg" alt="Slide 2">
  </div>
  <div tds-carousel-content>
    <img src="slide3.jpg" alt="Slide 3">
  </div>
</tds-carousel>

<!-- Fade effect -->
<tds-carousel tdsEffect="fade" [tdsEnableSwipe]="false">
  <div tds-carousel-content *ngFor="let item of items">
    <h3>{{ item.title }}</h3>
    <p>{{ item.description }}</p>
  </div>
</tds-carousel>

<!-- Custom dot position and render -->
<tds-carousel 
  tdsDotPosition="left" 
  [tdsDotRender]="customDot"
  (tdsAfterChange)="onSlideChange($event)">
  
  <div tds-carousel-content *ngFor="let slide of slides; let i = index">
    <div class="slide-content">{{ slide.content }}</div>
  </div>
</tds-carousel>

<ng-template #customDot let-index>
  <button class="custom-dot">
    <span>{{ index + 1 }}</span>
  </button>
</ng-template>

<!-- Manual control -->
<tds-carousel #myCarousel>
  <div tds-carousel-content *ngFor="let item of items">
    {{ item }}
  </div>
</tds-carousel>

<button (click)="myCarousel.next()">Next</button>
<button (click)="myCarousel.pre()">Previous</button>
<button (click)="myCarousel.goTo(0)">First</button>

<!-- With before/after change events -->
<tds-carousel 
  (tdsBeforeChange)="onBeforeChange($event)"
  (tdsAfterChange)="onAfterChange($event)">
  
  <div tds-carousel-content *ngFor="let item of items">
    {{ item }}
  </div>
</tds-carousel>

<!-- Vertical carousel -->
<tds-carousel tdsDotPosition="left">
  <div tds-carousel-content>
    <img src="vertical1.jpg">
  </div>
  <div tds-carousel-content>
    <img src="vertical2.jpg">
  </div>
</tds-carousel>
```

```typescript
import { TDSCarouselModule, TDSCarouselContentDirective } from 'tds-ui/carousel';
import { CommonModule } from '@angular/common';

@Component({
  standalone: true,
  imports: [TDSCarouselModule, TDSCarouselContentDirective, CommonModule],
})
export class MyComponent {
  slides = [
    { content: 'Slide 1' },
    { content: 'Slide 2' },
    { content: 'Slide 3' }
  ];

  items = ['Item 1', 'Item 2', 'Item 3'];

  onSlideChange(index: number) {
    console.log('Changed to slide:', index);
  }

  onBeforeChange(event: FromToInterface) {
    console.log('Before change:', event.from, '->', event.to);
  }

  onAfterChange(index: number) {
    console.log('After change:', index);
  }
}
```

## Custom Strategies

Carousel có thể be extended với custom strategies:

```typescript
import { TDSCarouselBaseStrategy } from 'tds-ui/carousel';
import { TDSCarouselComponentAsSource } from 'tds-ui/carousel';
import { TDS_CAROUSEL_CUSTOM_STRATEGIES } from 'tds-ui/carousel';

class CustomStrategy extends TDSCarouselBaseStrategy {
  // Implement custom strategy
}

// Provide in component or module
@Component({
  providers: [
    {
      provide: TDS_CAROUSEL_CUSTOM_STRATEGIES,
      useValue: [
        { name: 'custom', strategy: CustomStrategy }
      ]
    }
  ]
})
```

## Notes

- Keyboard navigation: Arrow keys để chuyển slide
- Swipe gesture hoạt động trên touch devices và mouse drag
- Auto-play sẽ pause khi user tương tác với carousel
- `tdsTransitionSpeed` kiểm soát tốc độ animation
- `tdsDotPosition` có thể là `top`, `bottom` (default), `left`, hoặc `right`
- Khi `tdsDotPosition` là `left` hoặc `right`, carousel sẽ chuyển sang vertical mode
- `tdsBeforeChange` emit trước khi transition bắt đầu
- `tdsAfterChange` emit sau khi transition hoàn thành
- Component tự động responsive với window resize
- RTL support tự động hoạt động khi `dir="rtl"`
- Custom dot render có thể be used với `TemplateRef`
- `tdsStrategyOptions` cho phép pass options vào custom strategies
- Swipe có thể be disabled với `tdsEnableSwipe="false"`
- Auto-play speed phải lớn hơn 0 để hoạt động
- Component tự động loop (về đầu khi hết slides)
