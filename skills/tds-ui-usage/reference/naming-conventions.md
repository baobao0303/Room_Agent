# tds-ui Naming Conventions

Guide for reading and understanding tds-ui APIs correctly.

## Selectors

| Type | Convention | Example |
|------|-----------|---------|
| Component selector | `tds-xxx` | `<tds-modal>`, `<tds-select>` |
| Attribute selector (element) | `button[tds-xxx]`, `a[tds-xxx]` | `<button tds-button>`, `<a tds-button>` |
| Attribute selector (any) | `[tds-xxx]` | `<span tds-tooltip>`, `<div tds-popover>` |

## TypeScript Classes

| Type | Convention | Example |
|------|-----------|---------|
| Component class | `TDS` prefix + PascalCase + `Component` | `TDSButtonComponent`, `TDSModalComponent` |
| Directive class | `TDS` prefix + PascalCase + `Directive` | `TDSTooltipDirective` |
| Service class | `TDS` prefix + PascalCase + `Service` | `TDSModalService`, `TDSMessageService` |
| Module class | `TDS` prefix + PascalCase + `Module` | `TDSButtonModule`, `TDSModalModule` |

## Inputs & Outputs

### Naming patterns

Tds-ui components use a mix of naming patterns for inputs/outputs:

| Pattern | Examples | Notes |
|---------|----------|-------|
| `tds` prefix | `tdsColor`, `tdsSize`, `tdsTheme`, `tdsType` | Common styling/theme inputs |
| No prefix | `disabled`, `visible`, `size`, `mode`, `open` | Core functional inputs |
| Mixed | Some components use both patterns | Always check per-component docs |

**Luôn kiểm tra `docs/{component-name}.md`** để biết chính xác inputs/outputs của từng component.

### How to read the API tables in docs

Each component doc has tables like:

```
| Input | Type | Default | Description |
|-------|------|---------|-------------|
| tdsColor | TDSButtonColor | 'primary' | Màu button |
| disabled | boolean | false | Vô hiệu hóa |
```

Usage in template:
```html
<button tds-button color="primary" [disabled]="isDisabled">Click</button>
```

Note: `tdsColor` uses attribute binding without brackets for string values, `disabled` uses bracket binding for boolean/expression values.

## Import Pattern

Import **Module** vào standalone component:

```typescript
import { TDSButtonModule } from 'tds-ui/button';

@Component({
  standalone: true,
  imports: [TDSButtonModule],
  template: `<button tds-button>Click</button>`
})
```

See `import-guide.md` for detailed import patterns and special cases.

## CSS Classes

Component CSS classes follow the pattern: `tds-{component}-{property}-{value}`

Example: `tds-button-color-primary`, `tds-button-size-lg`

Note: These classes are managed internally. Prefer using component inputs over manual CSS classes.
