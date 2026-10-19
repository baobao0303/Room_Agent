# Figma MCP -> TDS-UI Mapping Rules

This reference defines how to map when reading Figma via Framelink MCP. Prioritize real component data from the node tree: `COMPONENTS`, `COMPONENT_SETS`, `componentId`, `componentSetId`, `componentProperties`, instance name, text, layout, fills, strokes.

Goal: map each Figma component to the correct Angular/TDS-UI component. Do not guess. If the MCP output is insufficient to conclude, ask the user or record a clear gap before implementing.

## Source Of Truth

Priority order when analyzing:

1. `COMPONENT_SETS` and `COMPONENTS` from `get_figma_data`.
2. Instance name in `NODES`, e.g. `Button primary`, `Text input`, `Multi select`.
3. `componentProperties`, variant name, state, size, type, icon flags.
4. Layout/text/fill/stroke of the node to cross-check visually.
5. Figma variable/alias name used to map styling once the component mapping is clear. Resolved hex is only supporting evidence, not a source for inferring a semantic class.

Never use token/hex to infer a component when Figma MCP already gives a clear component name/set.

## Hard Rules

- If a Figma node is an `INSTANCE` and has a `componentId`, resolve the component name/set before choosing a TDS-UI component.
- If a Figma component has a clear TDS-UI equivalent, use the TDS-UI public API. Do not use raw HTML/CSS in place of button/select/input/switch/modal/card.
- If a TDS-UI equivalent exists but Figma size/radius/color/padding does not match the default, read the component docs to find props/custom API first. For `tds-form-field`, check `tdsClass` and use local classes through this input to customize the container while preserving TDS behavior.
- If docs/API do not allow matching Figma, record the mismatch explicitly and ask the user to confirm custom local markup/styles before implementing. Do not apply approximate color/size by feel.
- If a Figma component is not in the map, read `tds-ui-usage/reference/components-index.md` or the related component doc before choosing custom markup.
- If there is still no TDS-UI equivalent, record `No confirmed TDS component` and propose local markup. If it affects behavior, ask the user before implementing.
- If Figma access is missing, node data is missing, or Framelink returns only layout without component metadata, do not treat the component mapping as certain.
- Do not map by feel from color names or from resolved hex. Color must be mapped from the Figma variable/alias name when available, e.g. `Alias/color/background/info/subtle` -> `tds-color-background-info-subtle`.
- If Framelink (`get_figma_data`) returns only hex without a variable/alias name, use the maintained token maps with `node scripts/tds-token-lookup.js` directly; the helper checks project overrides, then cached remote `theme.json`, `alias.json`, and `global.json`. If ambiguous/missing, ask the user before choosing a class or hardcoding a color. Do not call the REST Variables API directly.
- For primary/secondary colors driven by the project theme, never guess the theme from hex. The skill-local `references/config/tds-project-token-map.json` must have a configured `themePreset`; if it is missing or null, stop and ask before calling Figma MCP or implementing.
- Do not write wrong class prefixes: use `tds-body-2`, `tds-heading-6`, `tds-color-text-secondary`; do not use `text-body-2`, `tds-body-2-semibold`, `text-tds-color-*`, `bg-tds-color-*`.

## Required Mapping Output

For each Figma analysis, build a table with at least:

| Figma evidence | Figma component/variant | TDS-UI target | Token/class mapping | Confidence | Gap/Question |
|---|---|---|---|---|---|

`Figma evidence` must include node id or component id when present, e.g. `#6788:42574`, `componentId=173:27803`, `componentSet=Button primary`.

`Token/class mapping` must prioritize a Figma variable/alias when Framelink exposes one. When Framelink exposes only a resolved hex, use the maintained token maps and report both the returned class and the resolved hex evidence. Never conclude an implementation by mapping hex to a token outside the maintained maps.

Confidence:

- `high`: componentSet/name + TDS equivalent + clear props/variant.
- `medium`: component name clear but TDS props need verification via docs/nearby code.
- `low`: only layout/text/hex, no component metadata.

If `Confidence=low` for a component with behavior, stop and ask the user or request a more precise node/link.

## Component Mapping From MCP

Start from the real component set/name in the MCP output, then map:

| Figma component set/name | TDS-UI target | Notes |
|---|---|---|
| `Button primary` | `button tds-button` or `button tds-button-outline` | Variant `Type=Base` -> filled, `Type=Outline` -> outline. Use `color`, `size`, `tdsPrefixIcon`, `tdsSuffixIcon` from properties/icon nodes. |
| `Button secondary` | `button tds-button` or `button tds-button-outline` with `color="secondary"` | Verify visually: if Figma has border + white fill, prefer `tds-button-outline`. |
| `Text input` | `tds-form-field` + `input tds-input` | Use `tds-label` when Figma has `Field label`. Preserve required state from Figma label/component property. If Figma height/radius/padding differs from default, use documented `tdsClass` on `tds-form-field` with local CSS before choosing raw input. |
| `Field label` | `tds-label` | Do not treat as a typography token. It is form-field label behavior. |
| `Multi select` | `tds-form-field` + `tds-select mode="multiple"` | Use `textField`, `valueField`, search/loading props from the data contract, not from Figma. |
| `Select`, `Dropdown` | `tds-select` or dropdown directive | Choose `tds-select` for value selection, dropdown for action menus. |
| `Switch` | `tds-switch` | Map `Size` to `tdsSize`; bind a boolean model. Label text is usually a sibling text node, not a switch child. |
| Avatar/profile image | `tds-avatar`; in TPage, use `chatomni-picture-channel` when the Figma avatar also has a small channel icon/badge under or overlaid on the avatar | TPage-specific rule: if the avatar node contains or visually shows a secondary channel icon/badge, search nearby code for `chatomni-picture-channel` and map the badge/icon size to `sizeIcon`. Outside TPage, or when no secondary icon exists, keep `tds-avatar`. |
| `Card panel`, card container | Prefer repo patterns with TDS surface aliases; use `tds-card` only if nearby code already uses it or the design needs card sections | Use structural wrappers such as `div tds-color-surface-low rounded-md`, not raw `bg-white`, so dark-mode/theme aliases still work. |
| `Modal`, footer, dialog layout | Existing page/modal wrapper or `TDSModalService`/`tds-modal` | Use the project flow first. Do not create a modal if the target route already owns the layout. |
| `tdsi-*` icons | TDS icon class | Use component icon inputs when available, otherwise `<i class="tdsi-...">`. |

If a component set does not match the table above, do not add a new mapping in code on your own. Record the candidate and verify via `tds-ui-usage`.

## Page Header & Top Toolbar Rules (Single-Row Layout)

When mapping page headers, table headers, or filter toolbars:

1. **Single-Row Horizontal Alignment**:
   - If Figma frame has horizontal auto-layout (`layoutMode=HORIZONTAL`), do NOT split status tabs and action toolbar into two stacked rows. Keep them on a single horizontal row (`h-14` / `56px`, `px-6`).
2. **Status Tabs Integration (`tds-tabset`)**:
   - Constrain the tabs wrapper width (`max-w-[560px]` / `max-w-[580px]`) so `tds-tabset`'s native ellipsis/dropdown `...` triggers automatically when tabs overflow.
   - Hide the tab content container with `.tds-tabs-content-holder { display: none !important; }` in component SCSS to prevent tab clipping or baseline shift.
3. **Button Sizing, Padding & Uniform Baseline**:
   - All action buttons and search input on the toolbar must share a uniform height (`36px` / `h-9` or `32px` / `h-8`).
   - Button padding: Outline buttons (`button[tds-button-outline]`) should use `px-3.5 py-1.5` or `size="sm"` with icon gap `gap-1.5`. Primary CTA (`button[tds-button] color="primary"`) should use `px-4 font-semibold rounded-md`.
   - Search input width: Give enough width (`w-72 sm:w-80 md:w-96 min-w-[280px]`) to ensure placeholder text is not truncated.
4. **Icon Verification Rule**:
   - Always cross-reference `node_modules/tds-ui/icon/list-icon.js` for exact TDS icon names.
   - Examples: `tdsi-user-list-fill` (not generic shared icon), `tdsi-sort-arrow-up-down-line` (not generic sort), `tdsi-filter-1-fill` (filter phễu), `tdsi-plus-fill` (add).

Icon rule:

- If the Figma node/icon name is `tdsi-*`, you must use that TDS icon class; do not download an SVG.
- If Figma only shows an icon but has no `tdsi-*` name, search for an equivalent icon in the codebase/TDS docs first, e.g. search `tdsi-call`, `tdsi-phone`, `tdsi-headset`.
- If a clearly equivalent icon is found, report it in the mapping and use that TDS icon class.
- If no equivalent TDS icon is found, use the SVG/image asset from Figma if the MCP has an asset ref; if there is no asset or it would change the icon's meaning, ask the user before substituting a different icon.

## Variant And Props Mapping

Read props from the MCP output:

- `Style=Primary`, `Button primary` -> likely `color="primary"` unless visual/stroke says success/secondary.
- `Type=Base` -> `tds-button`.
- `Type=Outline` -> `tds-button-outline`.
- `Size=M` -> `size="md"` or `tdsSize="md"` depending on the component API.
- `State=Default` -> no disabled/loading state.
- `Status=Unactive` for a switch pill -> unchecked model.
- `Prefix icon=true` -> `tdsPrefixIcon="..."` if the icon class is known.
- `Suffix icon=true` -> `tdsSuffixIcon="..."` if the icon class is known.

If a Figma property name exists but the TDS API name is unknown, read the specific TDS docs before writing the template.

If Figma gives only frame geometry for an input/button and no component metadata, do not assume the nearest TDS size or color. Produce a gap:

```text
MCP returned only layout for <input/button> (#node), with no component/variant/size metadata. We can use TDS + a documented custom API if it matches, or custom local markup to match Figma. Which direction do you want?
```

## Typography Mapping

Use MCP `textStyle` only after component mapping. Map the style name; do not set font family manually.

Default inheritance rule for Angular templates:

- For data-heavy screens where most text is `Body/body-2-regular` in the primary text color, put `tds-body-2 tds-color-text-primary` on the nearest stable wrapper.
- Do not repeat `tds-body-2` or `tds-color-text-primary` on plain child `span`/`div` elements that inherit the same size and color.
- Add child classes only when the Figma node differs by role, size, weight, or color, for example `font-semibold`, `tds-body-3`, `tds-caption-1`, `tds-color-text-secondary`, `tds-color-text-placeholder`, or `tds-color-text-error`.
- Component APIs still win over inherited classes. Do not force typography/color classes into TDS components if their public inputs already render the correct variant.

| Figma textStyle | Class |
|---|---|
| `Heading/heading-6` or `Heading/heading-6-*` | `tds-heading-6` + weight class |
| `Body/body-2-regular` | `tds-body-2` |
| `Body/body-2-semibold` | `tds-body-2 font-semibold` |
| `Body/body-3-regular` | `tds-body-3` |
| `Caption/caption-1-regular` | `tds-caption-1` |

Weight rules:

| Figma weight | Class |
|---|---|
| regular | omit weight class |
| medium | `font-medium` |
| semibold / semi bold | `font-semibold` |
| bold | `font-bold` |

If the MCP returns only `fontSize/lineHeight` without a textStyle, cross-check against TDS typography. If there is no clear match, record a gap instead of forcing one.

## Color Mapping

> **Priority (important):** (1) If the element already has a TDS-UI component
> (button, input, form-field, switch, tag, badge...), color/style MUST be applied
> through the component API (`color`, `tdsVariant`, `rounded`...) — do not force
> alias classes onto the component. (2) The alias table below applies ONLY to
> **raw** elements (text, divider, surface, icon, wrapper) not wrapped by a
> TDS-UI component.
>
> When analyzing or reporting, ALWAYS state the TDS alias/class first. Hex is
> data resolved by the MCP for traceability; it is not the primary implementation
> language.

| Element (already a component) | Get color/style via API |
|---|---|
| Button fill | `tds-button` + `color="primary\|secondary\|success\|error\|warning\|info"` |
| Button outline | `tds-button-outline` + `color="..."` (+ `tdsBorderStyle`) |
| Button pill | `tds-button` + `rounded="rounded-full"` |
| Input text/password | `tds-form-field` + `input tdsInput`; use `tdsClass` on `tds-form-field` for local container height/radius/padding overrides when documented props are insufficient |
| Input password toggle eye | `tds-input-password` + `tdsShowPassword` (eye icon is built in) |
| Label form | `tds-label` |
| Tag/badge | `tds-tag` / `tds-badge` |

Color class generation is name-based:

- If Figma exposes a semantic alias name, convert that alias to the class.
- If Figma exposes a global/primitive name, generate the raw global utility from that name and the CSS property role.
- If `get_figma_data` (Framelink) exposes only a resolved hex, look up the maintained token maps with `node scripts/tds-token-lookup.js <hex> <role> [project] [themePreset] [mode]`. The helper checks project overrides, then cached remote `theme.json`, `alias.json`, and `global.json`. Use the class only when lookup returns exactly one match. Ask on ambiguous/missing matches. Do not call the REST Variables API.

Do not manually infer implementation classes from a resolved hex. If the token map is ambiguous or missing, report the gap and ask.

Required reporting format when an alias is present:

```text
Figma source: #node fill/stroke/text
Figma alias: Alias/color/...
Role: background | text | icon | border | surface
Alias/class: tds-color-...
Resolved value: #HEX (evidence only)
```

Required reporting format when no alias is present:

```text
Figma source: #node fill/stroke/text resolved #HEX
Missing: Figma alias/class name
Question: Which class should be used, or is a custom hardcoded color allowed?
```

Never write "use #HEX" in an implementation proposal unless the user has confirmed a custom hardcoded color.

### Figma Variable Names

If Figma exposes a semantic alias path like `Alias/color/{role}/{name}/{state}`, convert it directly to a TDS class by removing `Alias/color/` and joining the rest with hyphens:

| Figma alias | Class |
|---|---|
| `Alias/color/background/info/subtle` | `tds-color-background-info-subtle` |
| `Alias/color/text/secondary` | `tds-color-text-secondary` |
| `Alias/color/border/primary` | `tds-color-border-primary` |
| `Alias/color/icon/success` | `tds-color-icon-success` |

If Figma exposes a global/primitive path like `Global/color/{palette}/{scale}`, generate the raw global utility class from that name and the CSS property role. The output may include the resolved hex for traceability, but the class must be generated from the `Global/color/...` name, not from the hex value.

| Figma global path | Role/property | Generated class |
|---|---|---|
| `Global/color/primary/50` | fill/background | `bg-tds-color-primary-50-light dark:bg-tds-color-primary-50-dark` |
| `Global/color/primary/50` | text/icon | `text-tds-color-primary-50-light dark:text-tds-color-primary-50-dark` |
| `Global/color/primary/50` | stroke/border | `border-tds-color-primary-50-light dark:border-tds-color-primary-50-dark` |
| `Global/color/primary/50` | focus ring | `ring-tds-color-primary-50-light dark:ring-tds-color-primary-50-dark` |

Do not convert resolved hex values to semantic classes by intuition. Example: `#27A745` alone is not enough to choose `tds-color-background-info-subtle` unless that exact mapping exists in the maintained token maps for the requested role.

## Spacing, Radius, Layout

MCP layout values are useful for Tailwind/TDS utility choices, but do not override TDS component internals.

- `padding: 6px 12px` -> prefer component size props for buttons; use a utility only for custom wrappers.
- `padding: 14px 18px` on a form input -> first verify `tds-form-field` `size` and `tdsClass`; if neither can match, ask before a custom raw input.
- `gap: 8px` -> `gap-2` or `gap-tds-spacing-*` if the repo uses token utilities nearby.
- `borderRadius: 4px/6px` -> prefer the component default; use the `rounded` input or a wrapper class only if needed.
- `borderRadius: 999px` on inputs/buttons -> verify documented rounded/custom-class support. If support exists, use it explicitly; if not, ask before a local custom.
- Card/container radius from Figma can map to the repo's existing `rounded-md` when nearby code uses Tailwind. Pair it with TDS aliases such as `tds-color-surface-low`, `tds-color-surface-lowest`, and `tds-color-border-secondary`; avoid raw `bg-white`, `text-neutral-*`, or `border-neutral-*` when a TDS role alias exists.

## When To Ask Instead Of Guess

Ask or stop with a gap when:

- The Figma URL points to a parent frame but the desired component is ambiguous.
- The `get_figma_data` output lacks `COMPONENTS`/`COMPONENT_SETS` for an interactive element.
- Figma shows a custom component but no known TDS equivalent exists.
- TDS has an equivalent but docs do not expose the size/radius/color required by Figma, including cases where `tdsClass` is unavailable or insufficient.
- Component behavior is not visible in the static design, e.g. select data source, server search, validation rules, disabled/loading states.
- A variant is named differently from the TDS docs and nearby code does not show the API.
- A visual asset/image/video is required but not downloaded or identified. If the MCP exposes `IMAGE` only, do not call it a video unless a video URL/ref is present or the user confirms an existing video asset.

Suggested wording:

```text
The MCP output has layout/text but not enough component metadata for <area>. I cannot map confidently to a TDS component. Can you send a selection link to a more precise component/frame, or confirm custom markup for this part?
```

## Example Analysis Pattern

```text
Figma evidence: #6788:42574, componentSet=Button primary, name=Style=Primary, Type=Base, Size=M, State=Default, Suffix icon=true
TDS target: <button tds-button color="primary" size="md" tdsSuffixIcon="tdsi-chevron-right-fill">
Confidence: high
Gap/Question: none
```

```text
Figma evidence: frame with white fill and radius, no componentSet
TDS target: repo wrapper div with `tds-color-surface-low rounded-md` or tds-card
Confidence: medium
Gap/Question: choose the repo wrapper if nearby code uses structural divs; use tds-card only if the user wants a strict TDS card.
```


---
## 📚 Điều Hướng: TDS Figma Rules & Setup
- **Mục lục chính:** [[SKILL]]
◀️ **Trước:** [[figma-color-to-tds-token-rules]] | ▶️ **Tiếp:** [[tds-ui-component-map]]
