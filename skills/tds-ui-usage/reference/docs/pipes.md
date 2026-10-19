# Pipes

Bộ pipes tiện ích của tds-ui. Tất cả standalone — import trực tiếp hoặc qua module.

**Import paths:**
- Core pipes: `import { TDSPipesModule } from 'tds-ui/core/pipes';`
- CDK pipes (filter/keys/mapper): import riêng per pipe

## Pipe Overview

| Pipe | Module | Import Path | Mô tả |
|------|--------|-------------|-------|
| `tdsFilter` | `TDSFilterPipeModule` | `tds-ui/cdk/pipes/filter` | Lọc array qua matcher fn |
| `tdsKeys` | `TDSKeysPipeModule` | `tds-ui/cdk/pipes/keys` | `Object.keys()` cho object |
| `tdsMapper` | `TDSMapperPipeModule` | `tds-ui/cdk/pipes/mapper` | Map value qua mapper fn |
| `tdsToCssUnit` | `TDSPipesModule` | `tds-ui/core/pipes` | Append CSS unit (px mặc định) |
| `tdsSafeNull` | `TDSPipesModule` | `tds-ui/core/pipes` | Thay null/undefined bằng fallback |
| `tdsSanitizer` | `TDSPipesModule` | `tds-ui/core/pipes` | `bypassSecurityTrust*` Angular DomSanitizer |
| `tdsTrim` | `TDSPipesModule` | `tds-ui/core/pipes` | Trim whitespace |
| `tdsBytes` | `TDSPipesModule` | `tds-ui/core/pipes` | Format bytes với unit (B/MB/GB/...) |
| `tdsAggregate` | `TDSPipesModule` | `tds-ui/core/pipes` | Sum/max/min/avg của number[] |
| `tdsEllipsis` | `TDSPipesModule` | `tds-ui/core/pipes` | Cắt chuỗi + suffix |
| `tdsTimeRange` | `TDSPipesModule` | `tds-ui/core/pipes` | Format duration (seconds → HH:mm:ss) |
| `tdsFormatNumber` | `TDSPipesModule` | `tds-ui/core/pipes` | Thousand separators + decimal padding |

## CDK Pipes

### tdsFilter

Lọc array qua matcher function. Truyền thêm args tùy ý cho matcher.

```typescript
import { Component } from '@angular/core';
import { TDSFilterPipe } from 'tds-ui/cdk/pipes/filter';

@Component({
  standalone: true,
  imports: [TDSFilterPipe],
  template: `
    @for (item of items | tdsFilter:filterFn:term; track item.id) {
      <div>{{ item.name }}</div>
    }
  `
})
export class Demo {
  items = [
    { id: 1, name: 'Apple' },
    { id: 2, name: 'Banana' },
    { id: 3, name: 'Cherry' },
  ];
  term = 'a';
  filterFn = (item: { name: string }, term: string) =>
    item.name.toLowerCase().includes(term);
}
```

### tdsKeys

Trả `Object.keys()` của object.

```typescript
import { TDSKeysPipe } from 'tds-ui/cdk/pipes/keys';

// template
// @for (key of obj | tdsKeys; track key) { {{ key }}={{ obj[key] }} }
```

### tdsMapper

Áp dụng mapper fn lên value. Khuyến nghị dùng arrow function.

```typescript
import { TDSMapperPipe } from 'tds-ui/cdk/pipes/mapper';

// template
// {{ value | tdsMapper:(v) => v * 2 }}
// {{ name | tdsMapper:(v, prefix) => prefix + ' ' + v:'Mr' }}
```

## Core Pipes

### tdsToCssUnit

Append CSS unit vào số. Mặc định `px`.

```typescript
import { TDSToCssUnitPipe } from 'tds-ui/core/pipes';

// template
// {{ 100 | tdsToCssUnit }}           → '100px'
// {{ 100 | tdsToCssUnit:'%' }}       → '100%'
// {{ 100 | tdsToCssUnit:'rem' }}     → '100rem'
// {{ 'auto' | tdsToCssUnit }}        → 'auto' (string giữ nguyên)
```

Units hỗ trợ: `cm`, `mm`, `Q`, `in`, `pc`, `pt`, `px`, `em`, `ex`, `ch`, `rem`, `1h`, `vw`, `vh`, `vmin`, `vmax`, `%`. Unit không hợp lệ → fallback `px`.

### tdsSafeNull

Thay `null`/`undefined` bằng fallback string. Mặc định `''`.

```typescript
import { TDSSafeNullPipe } from 'tds-ui/core/pipes';

// template
// {{ user.name | tdsSafeNull:'N/A' }}     → 'N/A' nếu null/undefined
// {{ user.bio | tdsSafeNull }}            → '' nếu null/undefined
```

### tdsSanitizer

Wrap Angular `DomSanitizer.bypassSecurityTrust*`. Cẩn thận — bypass bảo mật, chỉ dùng với content tin cậy.

```typescript
import { TDSSanitizerPipe } from 'tds-ui/core/pipes';

// template
// <div [innerHTML]="html | tdsSanitizer:'html'"></div>
// <iframe [src]="url | tdsSanitizer:'resourceUrl'"></iframe>
// <div [style]="css | tdsSanitizer:'style'"></div>
// <a [href]="url | tdsSanitizer:'url'">Link</a>
```

| Type | Method | Return |
|------|--------|--------|
| `'html'` | `bypassSecurityTrustHtml` | `SafeHtml` |
| `'style'` | `bypassSecurityTrustStyle` | `SafeStyle` |
| `'url'` | `bypassSecurityTrustUrl` | `SafeUrl` |
| `'resourceUrl'` | `bypassSecurityTrustResourceUrl` | `SafeResourceUrl` |

### tdsTrim

`String.prototype.trim()` — bỏ whitespace đầu/cuối.

```typescript
import { TDSTrimPipe } from 'tds-ui/core/pipes';

// {{ '  hello  ' | tdsTrim }}   → 'hello'
```

### tdsBytes

Format số byte thành chuỗi readable. Tự chọn unit hoặc ép unit cụ thể.

```typescript
import { TDSBytesPipe } from 'tds-ui/core/pipes';

// {{ 1500 | tdsBytes }}               → '1.46 kB'
// {{ 1500 | tdsBytes:2 }}             → '1.46 kB' (2 decimal)
// {{ 1048576 | tdsBytes:0 }}          → '1 MB'
// {{ 1024 | tdsBytes:0:'kB':'MB' }}   → '0 MB' (from kB, to MB)
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `input` | `number` | — | Giá trị |
| `decimal` | `number` | `0` | Số chữ số thập phân |
| `from` | `ByteUnit` | `'B'` | Unit của input |
| `to` | `ByteUnit` | auto | Unit output (optional — auto nếu bỏ qua) |

ByteUnit: `'B' \| 'kB' \| 'KB' \| 'MB' \| 'GB' \| 'TB'`

### tdsAggregate

Aggregate number[] — sum/avg/max/min.

```typescript
import { TDSAggregatePipe } from 'tds-ui/core/pipes';

// {{ [1, 2, 3, 4] | tdsAggregate:'sum' }}   → 10
// {{ [1, 2, 3, 4] | tdsAggregate:'avg' }}   → 2.5
// {{ [1, 2, 3, 4] | tdsAggregate:'max' }}   → 4
// {{ [1, 2, 3, 4] | tdsAggregate:'min' }}   → 1
// {{ [] | tdsAggregate:'sum' }}             → undefined
```

Method: `'sum' | 'max' | 'min' | 'avg'`

### tdsEllipsis

Cắt chuỗi xuống tối đa `length` ký tự, append `suffix`.

```typescript
import { TDSEllipsisPipe } from 'tds-ui/core/pipes';

// {{ 'Hello World' | tdsEllipsis:5:'...' }}   → 'Hello...'
// {{ 'Hello' | tdsEllipsis:10:'...' }}        → 'Hello' (không cắt nếu < length)
// {{ 'Hello' | tdsEllipsis }}                 → 'Hello' (length = full)
```

| Param | Type | Default | Description |
|-------|------|---------|-------------|
| `value` | `string` | — | Chuỗi |
| `length` | `number` | `value.length` | Độ dài tối đa |
| `suffix` | `string` | `''` | Hậu tố khi cắt |

Non-string → trả về nguyên giá trị.

### tdsTimeRange

Format số (seconds) thành duration string.

```typescript
import { TDSTimeRangePipe } from 'tds-ui/core/pipes';

// {{ 3661 | tdsTimeRange }}                  → '01:01:01' (HH:mm:ss)
// {{ 3661 | tdsTimeRange:'mm:ss' }}          → '61:01'
// {{ 90 | tdsTimeRange:'HH:mm:ss' }}         → '00:01:30'
```

Format mặc định: `'HH:mm:ss'`. Hỗ trợ tokens `HH`, `mm`, `ss` (và các time units khác theo `timeUnits`).

### tdsFormatNumber

Format số với thousand separators + decimal padding. Lấy default settings từ `TDS_NUMBER_FORMAT` token.

```typescript
import { TDSFormatNumberPipe } from 'tds-ui/core/pipes';

// {{ 1234567 | tdsFormatNumber }}                    → '1,234,567' (default)
// {{ 1234.5 | tdsFormatNumber:{decimalPlaces: 2} }}  → '1,234.50'
// {{ 1234.5 | tdsFormatNumber:{grouping: false} }}   → '1234.5'
```

Settings partial — override global `TDS_NUMBER_FORMAT` token per call.

## Notes

- Tất cả pipes `standalone: true` — import trực tiếp hoặc qua module
- `TDSPipesModule` export cả 9 core pipes; import riêng từng pipe để tree-shake
- CDK pipes (filter/keys/mapper) nằm trong module riêng — không có chung `TDSPipesModule`
- `tdsSanitizer` bypass bảo mật Angular — CHỈ dùng với content tin cậy, không dùng với user input chưa sanitize
- `tdsFilter`, `tdsMapper` truyền function làm arg — nhớ bind `this` hoặc dùng arrow function
- `tdsFormatNumber` inject `TDS_NUMBER_FORMAT` từ DI — cấu hình global qua provider
