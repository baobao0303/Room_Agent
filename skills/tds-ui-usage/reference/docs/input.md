# Input (tdsInput Directive)

Directive boc `<input>` hoac `<textarea>` de tich hop voi `tds-form-field`. Implements `TDSFormFieldControl`.

**Selector:** `input[tdsInput], textarea[tdsInput], select[tdsNativeControl], input[tdsNativeControl], textarea[tdsNativeControl]`
**Import:** `import { TDSInputModule } from 'tds-ui/tds-input';`
**Export as:** `tdsInput`

**CRITICAL:** Import path is `tds-ui/tds-input` (NOT `tds-ui/input`). See `import-guide.md` special import paths.

## Key Inputs

| Input | Type | Default | Description |
|-------|------|---------|-------------|
| `tdsSize` | `ButtonSize` | `'md'` | Kich thuoc: `sm`, `md`, `lg`, `xl` |
| `disabled` | `boolean` | `false` | Vo hieu hoa (tu dong sync voi NgControl) |
| `tdsBorderless` | `boolean` | `false` | An vien |
| `tdsTheme` | `TDSTheme` | `'default'` | Theme: `default`, `light`, `dark` |

## Outputs

| Output | Type | Description |
|--------|------|-------------|
| `disabled$` | `Subject<boolean>` | Stream thong bao trang thai disabled thay doi |

## Usage

Luon dung ben trong `tds-form-field`:

```html
<tds-form-field>
  <tds-label>Ho ten</tds-label>
  <input tdsInput placeholder="Nhap ho ten" [(ngModel)]="name" />
  <tds-error>Bat buoc nhap</tds-error>
</tds-form-field>

<!-- Voi ReactiveForm -->
<tds-form-field>
  <tds-label>Email</tds-label>
  <input tdsInput [formControl]="emailCtrl" type="email" />
  @if (emailCtrl.hasError('required')) {
    <tds-error>Email la bat buoc</tds-error>
  }
</tds-form-field>

<!-- Voi kich thuoc -->
<tds-form-field>
  <tds-label>Nho</tds-label>
  <input tdsInput tdsSize="sm" />
</tds-form-field>

<!-- Borderless -->
<tds-form-field>
  <tds-label>Khong vien</tds-label>
  <input tdsInput tdsBorderless />
</tds-form-field>

<!-- Textarea -->
<tds-form-field>
  <tds-label>Mo ta</tds-label>
  <textarea tdsInput rows="4"></textarea>
</tds-form-field>
```

```typescript
import { TDSFormFieldModule } from 'tds-ui/form-field';
import { TDSInputModule } from 'tds-ui/tds-input';
import { FormControl, Validators } from '@angular/forms';

@Component({
  standalone: true,
  imports: [TDSFormFieldModule, TDSInputModule],
})
export class MyComponent {
  name = '';
  emailCtrl = new FormControl('', [Validators.required, Validators.email]);
}
```

## Additional Imports from tds-ui/input (Optional)

For advanced features beyond basic input, import `TDSFormInputModule` from `tds-ui/input` IN ADDITION to `TDSInputModule`:

| Export | Type | Selector | Description |
|--------|------|----------|-------------|
| `TDSInputGroupComponent` | Component | `tds-input-group` | Input group voi addon/prefix/suffix |
| `TDSInputGroupSlotComponent` | Component | `[tds-input-group-slot]` | Slot cho addon/prefix/suffix trong input group |
| `TDSAutosizeDirective` | Directive | `textarea[tdsAutosize]` | Tu dong chieu cao textarea |
| `TDSTextareaCountComponent` | Component | `tds-textarea-count` | Hien thi so ky tu trong textarea |

```typescript
import { TDSInputModule } from 'tds-ui/tds-input';
import { TDSFormInputModule } from 'tds-ui/input';

@Component({
  standalone: true,
  imports: [TDSFormFieldModule, TDSInputModule, TDSFormInputModule],
})
```

## Notes

- Luon boc trong `tds-form-field` de co label, error, prefix/suffix
- Dung attribute `tdsInput` (camelCase) tren native `<input>` hoac `<textarea>`
- Dung attribute `tdsNativeControl` tren native `<select>` de tich hop voi form-field
- `disabled` tu dong dong bo voi `NgControl` neu co (ReactiveForms/TemplateDrivenForms)
- Ho tro RTL (right-to-left)
- Ho tro tat ca HTML input types: `text`, `email`, `password`, `number`, `tel`, `url`, etc.
- Ho tro `<textarea>` qua `textarea[tdsInput]` selector
- `tdsSize` ho tro: `sm`, `md`, `lg`, `xl`
- `tdsTheme` ho tro: `default`, `light`, `dark`
- Standalone directive, co the import truc tiep hoac qua `TDSInputModule`
- `TDSAutosizeDirective` cho phep textarea tu dong thay doi chieu cao, co the truyen `{ minRows, maxRows }`
- `tds-textarea-count` hien thi so ky tu, dung ben ngoai `<textarea tdsInput>`
