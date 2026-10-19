---
name: tds-ui-figma
description: Use when implementing, reviewing, or planning Angular UI from a Figma link/frame using tds-ui components and tds-color tokens, updating/syncing TDS token JSON maps, or setting up Framelink Figma MCP for this workflow. Generic for any Angular project using tds-ui. Do not use for generic Angular bugfixes.
---

# TDS UI Figma Workflow (Team)

## 📚 Liên kết nhanh & Mục lục TDS
- **Mục lục components:** [[components-index]]
- **Quy tắc mapping Figma sang TDS:** [[figma-to-tds-ui-rules]]
- **Quy tắc màu sắc:** [[figma-color-to-tds-token-rules]]
- **Cấu hình Figma MCP:** [[figma-framelink-mcp-setup]]
- **Quy định Review:** [[Quy-Dinh-Code-Review-Va-Chuan-TDS]]

## Overview

Use this as the required workflow for turning a selected Figma design into Angular code using **tds-ui** components and **tds-color** tokens. Generic for any Angular project — does not depend on a specific project's conventions.

Keep loaded context limited to the selected node, required visual assets, and TDS components actually used.

## MCP Preflight (REQUIRED)

Before reading or analyzing a Figma link, check whether Framelink MCP provides
`get_figma_data` and `download_figma_images`.

If both tools are available, continue to Step 0.

If either tool is unavailable, stop the Figma workflow and give the user the
setup command for the current client:

```bash
# Codex
bash ~/.codex/skills/tds-ui-figma/scripts/setup-figma-framelink-codex.sh

# Claude Code on Ubuntu
bash ~/.claude/skills/tds-ui-figma/scripts/setup-figma-framelink-claude-ubuntu.sh
```

Tell the user to run only the command matching their client. The script shows
how to create a Figma Personal Access Token and asks for it locally. The token
must have only **File content: Read** (`file_content:read`); no write,
comments, variables, projects, or library scopes are required. Never ask the
user to paste the token into chat.

After the script finishes, tell the user to restart Codex or Claude Code and
invoke the skill again (`$tds-ui-figma` in Codex or `/tds-ui-figma` in Claude
Code). Do not continue Figma analysis until the MCP tools are available.

## Required Sub-Skills

- **tds-ui-usage**: Load only after the Figma frame reveals concrete TDS components or when an API detail is needed. Prefer specific component docs over the full catalog.
- **figma:figma-use**: Optional. Load only for Figma write actions or JavaScript execution in the Figma file. For normal reads, use Framelink `get_figma_data` / `download_figma_images` (structure, layout, assets) directly — neither needs this skill.

## Core Rules

- Prioritize readability, maintainability, scalability, and reusable solutions.
- Avoid quick fixes, duplicated code, hardcoded logic, and deeply nested logic.
- Keep functions small and single-responsibility.
- Follow existing project patterns before adding new abstractions.
- Reply to the developer in the language of their latest message.

## Updating Token Maps

When the developer asks to update, refresh, sync, or pull the latest TDS token JSON maps, run:

```bash
node <skill-dir>/scripts/sync-tds-tokens.js
```

This fetches the latest remote files configured in `references/config/tds-token-sources.json`:

- `themeTokens` from `theme.json`
- `globalTokens` from `global.json`
- `aliasTokens` from `alias.json`

The lookup helper uses cached files for speed and offline reliability. Do not edit cached token JSON by hand. If a lookup result seems stale, sync first, then rerun `node <skill-dir>/scripts/tds-token-lookup.js <hex> <role> [project] [themePreset] [mode]`.

## Setting Up Framelink MCP

When the developer asks to setup/install/configure Figma MCP or Framelink MCP for Codex, direct them to run:

```bash
bash ~/.codex/skills/tds-ui-figma/scripts/setup-figma-framelink-codex.sh
```

The Codex script asks for the Figma token locally with visible input and writes
an NVM-aware `[mcp_servers.figma]` block to `~/.codex/config.toml`. It removes
both old `figma-framelink` and `figma` blocks first. The default image directory
is the current project's `.figma-assets`; the developer can enter a custom directory
when prompted. `~/.codex/config.toml contains the Figma token`, so
tell the developer not to commit or share it. Never ask the user to paste a
Figma token into chat.

When the developer asks to setup Claude Code on Ubuntu, direct them to run:

```bash
bash ~/.claude/skills/tds-ui-figma/scripts/setup-figma-framelink-claude-ubuntu.sh
```

The Claude Ubuntu script asks for the token locally with visible input, checks
`~/.claude.json`, migrates legacy `framelink` to `figma-framelink`, writes the
token directly into Claude config, and detects Node PATH dynamically from the
actual Node.js binary on that machine.

## Step 0: Ask for Theme Preset (REQUIRED)

**Before any analysis**, determine the project's theme preset:

1. Read `<skill-dir>/references/config/tds-project-token-map.json` and resolve the requested project, falling back to `projects.default`.
2. Treat a missing or `null` `themePreset` as unconfigured.
3. If a saved `themePreset` is not present in the current remote `theme.json` and is not "other" or "none", stop and report that the current theme is not supported. Run `node <skill-dir>/scripts/set-tds-theme-preset.js --list` to show the supported presets.
4. If the preset is unconfigured, **stop immediately before calling Figma MCP or analyzing layout**. Sync/read remote `theme.json`, list the supported preset names, and ask the user to choose one or "other".
5. If the user asks for a preset/color that is not supported and is not "other" or "none", ask them to choose a supported preset. Do not invent a preset or manually map primary/secondary.
6. Persist the selected preset by running `node <skill-dir>/scripts/set-tds-theme-preset.js <themePreset> [project]`. This updates the single skill-local project map.
7. Reuse the saved preset later. Ask again only when it is missing, null, unsupported, or explicitly changed.
8. Store the answer for color mapping (Step 3). Remote token JSON remains in the disposable cache configured by `references/config/tds-token-sources.json`; the project map does not.

Never assume a default theme preset. If no supported project `themePreset` (or "other" / "none") is configured and the user has not answered yet, stop before Figma analysis, component mapping, color mapping, or implementation. Do not continue with "I will gather Figma structure first."

This step is mandatory because the same hex value maps to different TDS classes depending on the active theme preset. The supported preset list is not hardcoded in this skill; it comes from the synced remote `theme.json` array.
## Figma Sources

When the user provides a Figma URL, frame, or node, gather the full design context before coding, planning final implementation details, or reviewing visual parity.

Collect only the sources needed for the request:

1. **Figma node data - required**: Use `get_figma_data` with the file key and selected `node-id` whenever available. Read layout, spacing, typography, hierarchy, fills, strokes, effects, constraints, variants, component names, and text content from node data.
2. **Image/SVG/GIF assets - conditional**: Use `download_figma_images` only when the MCP data identifies a real asset needed by the implementation. Do not download TDS icons such as `tdsi-*`; use TDS icon classes instead.
3. **Screenshot or visual export - optional**: Capture/export only when the user asks for visual comparison, pixel/visual parity, or when node data is insufficient to understand composition.

Do not rely only on screenshots when MCP node data can provide spacing, hierarchy, typography, or constraints. If a conditional source is needed but cannot be retrieved, report exactly what is missing and treat it as a Figma verification gap.

If Figma MCP access is missing or token setup is requested, read `references/setup/figma-framelink-mcp-setup.md`. Never ask the user to paste a Figma token into chat.

## Figma MCP Layer

Use Framelink MCP as the Figma source for this workflow. Do NOT call the Figma REST Variables API.

**Framelink MCP** (`get_figma_data`, `download_figma_images`) is REST-based, fast, and headless (no Figma desktop app needed). Use it for the node tree, layout, spacing, typography, component/variant metadata, icon flags, and image references. It returns resolved hex values, not variable/alias names.

For colors, use Framelink's resolved hex as evidence and map it through the maintained token maps with `node scripts/tds-token-lookup.js <hex> <role> [project] [themePreset] [mode]`. The helper syncs and caches `theme.json`, `global.json`, and `alias.json` from `references/config/tds-token-sources.json`. Accept exact one-class matches only; ask on ambiguous/missing matches. If lookup returns `reason=themePresetRequired`, ask the user for the project theme preset and rerun lookup. Never invent hex-to-class mappings outside the maintained maps.

## Output Modes

Use **Analysis Mode** when the user asks to analyze, review, compare, map, inspect, or read the Figma design, or when the user sends only a Figma link without explicitly asking to implement immediately.

Use **Implementation Mode** when the user clearly asks to implement, code, build, or proceed directly while skipping the analysis report, regardless of the language used. In Implementation Mode, skip the full analysis report, but still determine theme preset before gathering Figma data. If theme preset is missing, stop and ask before writing code.

### Analysis Report Template

When using Analysis Mode, return the sections in this exact order. Keep the report concise, but do not omit a section.

#### 1. JS/Token Lookup Output

Start with the result generated from `node scripts/tds-token-lookup.js` or the `COLOR_MAP` emitted by `scripts/figma-digest.js`. Summarize exact, ambiguous, missing, and `themePresetRequired` results before any layout diagram.

````md
## JS/Token Lookup Output

Theme preset: green
Token cache: ~/.cache/tds-ui-figma/tokens

| Hex | Role | Source | Result | Status |
|---|---|---|---|---|
| `#0C1014` | text | aliasTokens | `tds-color-text-primary` | exact |
| `#27A745` | background | themeTokens | `bg-tds-color-primary-500-light dark:bg-tds-color-primary-500-dark` | exact |
| `#ABCDEF` | border | none | ask user | missing |
| `#1A6DE3` | background | themeTokens | ask theme preset | themePresetRequired |

Questions:
- `#ABCDEF` is not found in TDS tokens. Which TDS class should be used, or is a custom local color allowed?
- Project theme preset is required before mapping `#1A6DE3`.
````

#### 2. Layout

Describe the layout hierarchy and include a lightweight Markdown/ASCII or Mermaid diagram when useful.

````md
## Layout

Screen structure:
- Header with title and actions
- Filter bar with search and status select
- Data table with row actions
- Pagination footer

```text
Page
|-- Header
|-- Filter bar
|-- Table
`-- Pagination
```
````

#### 3. Figma Component to TDS UI Mapping

Map visible Figma components to `tds-ui` components. Include gaps instead of inventing custom UI.

````md
## Component Mapping

| Figma evidence | Proposed TDS UI | Notes |
|---|---|---|
| Primary button | `tds-ui/button` | Use existing primary variant |
| Search input | `tds-ui/input` | Preserve placeholder, disabled, error states |
| Data table | `tds-ui/table` | Confirm columns and row actions |
| Unknown chart block | ask user | No clear mapped component yet |
````

#### 4. Color Mapping

Show the Figma color evidence and lookup result. Missing or ambiguous values must become questions.

````md
## Color Mapping

| Figma source | Hex | Role | TDS result | Status |
|---|---|---|---|---|
| Title text | `#0C1014` | text | `tds-color-text-primary` | exact |
| CTA fill | `#27A745` | background | `bg-tds-color-primary-500-light dark:bg-tds-color-primary-500-dark` | exact |
| Border line | `#ABCDEF` | border | ask user | missing |
````

## Workflow

1. **Parse Figma input**
   - Extract `fileKey` and `node-id` from the Figma URL.
   - Prefer the selected frame or node over the full file.
   - If the node id is absent and the task needs exact UI, ask for the target frame or clearly state the ambiguity.

2. **Gather Figma context**
   - Call Framelink `get_figma_data` for the target node (structure, components/variants, layout, typography, icon flags).
   - When color classes are needed and Framelink returned resolved hex values, use the maintained token maps via `node scripts/tds-token-lookup.js <hex> <role> [project] [themePreset] [mode]`. The helper checks project overrides, then cached remote `theme.json`, `alias.json`, and `global.json`. Accept exact one-class matches only; ask on ambiguous/missing matches. If lookup returns `reason=themePresetRequired`, ask the user for the project theme preset and rerun lookup. Never invent hex-to-class mappings outside the maintained maps.
   - Pass the theme preset from Step 0 as the `themePreset` parameter.
   - For a new project, if `references/config/tds-project-token-map.json` has no configured `themePreset`, run `node <skill-dir>/scripts/set-tds-theme-preset.js --list`, ask the user to choose one supported preset from remote `theme.json`, save it with the setter, then continue.
   - Download only referenced images/SVG/GIF assets that cannot be represented by existing TDS icons or CSS.
   - Capture/export a screenshot only for visual parity requests or when the node data is not enough to understand the layout.
   - Record missing required/conditional sources as verification gaps before continuing.

3. **Map design to `tds-ui`**
   - Start from `references/mapping/tds-ui-component-map.md`.
   - For Framelink MCP component evidence, typography class rules, color role rules, icon size, font weight, spacing, radius, and "ask instead of guess" rules, read `references/mapping/figma-to-tds-ui-rules.md`.
   - Read `references/mapping/figma-color-to-tds-token-rules.md` for the token-map source order and reporting rules. Never manually guess a class from hex.
   - Then load only specific `tds-ui-usage/reference/docs/*.md` files for components used by the design. Use the full component index only when no likely TDS component can be identified.
   - Use `tds-ui` modules and public APIs instead of custom primitives when an equivalent exists.
   - If no `tds-ui` component fits, record the gap first. For behavioral UI, ask the user before implementing custom markup. For purely structural wrappers, use project-local Angular markup and Tailwind utilities while preserving repo tokens, spacing, and behavior.

4. **Plan implementation**
   - Identify target component, module, route, service, DTO, state model, and asset paths.
   - Include loading, empty, error, disabled, and responsive states expected by the screen.
   - Keep scope limited to the requested screen or component.
   - Explain any Figma-to-code tradeoff before or while implementing when the design conflicts with project rules.

5. **Implement**
   - Use Angular 18+ and strict TypeScript.
   - Never use the `any` type unless there is no reasonable alternative and the reason is stated.
   - Prefer explicit typing over implicit typing for public API boundaries.
   - Use `interface` for DTOs and API responses.
   - Use `type` for unions, mapped types, and utility types.
   - Define return types for public methods.
   - Name DTO interfaces with a `Dto` suffix.
   - Import `tds-ui` from sub-paths only, for example `tds-ui/button`, not root `tds-ui`.
   - Prefer Tailwind utility classes for new feature UI. Add component SCSS only when selectors, media queries, complex reusable styles, or existing local structure require it.
   - Avoid hardcoded design tokens when `tds-ui` variables, Tailwind tokens, or component inputs can express the design.
   - Render TDS color aliases directly as utility classes, for example `tds-color-text-secondary`, `tds-color-surface-low`, or `tds-color-border-success`; do not prefix them with `text-`, `bg-`, or `border-`.
   - Render TDS typography classes with the `tds-` prefix, for example `tds-body-2 font-semibold`; do not use `text-body-2` or combine weight into names like `tds-body-2-semibold`.
   - For data-heavy Figma screens, set the common default typography/color once on the nearest stable container, usually `tds-body-2 tds-color-text-primary`. Do not repeat those classes on every `span`. Only add typography/color classes to child text when MCP shows a different size, weight, semantic role, or color.
   - For Single-Row Page Headers / Toolbars with horizontal auto-layout: preserve the single-row structure (`h-14` / `56px`, `px-6`). Wrap `tds-tabset` with a constrained width and hide `.tds-tabs-content-holder { display: none !important; }` so native `...` overflow triggers cleanly without tab clipping. Set uniform button & input height (`h-9` / `36px`), outline button padding `px-3.5`, primary CTA `px-4 font-semibold`, and search input `min-w-[300px]` to prevent text truncation.
   - For TDS icon classes, always verify exact class names from `node_modules/tds-ui/icon/list-icon.js` (e.g. `tdsi-user-list-fill`, `tdsi-sort-arrow-up-down-line`, `tdsi-filter-1-fill`, `tdsi-plus-fill`).

6. **Verify**
   - Run the narrowest useful check first.
   - Then run `npx tsc -p tsconfig.json --noEmit` or `npx ng build` when appropriate for the change.
   - For Figma-driven UI, verify structural/component parity from node data. Verify visual parity against a screenshot/export only when one was requested or captured.
   - Report unrelated existing failures separately.

## Decision Rules

| Situation | Action |
|---|---|
| Figma component has a clear `tds-ui` equivalent | Use `tds-ui` and load the relevant component doc if API details are needed. |
| Figma component is not in the map | Search `tds-ui-usage` docs before building custom UI. |
| No `tds-ui` component fits | Record the gap first. For behavioral UI, ask the user before custom markup. For structural wrappers, use project-local markup/CSS with project tokens and behavior. |
| Figma MCP cannot read the file | Explain the access/setup issue, use `references/setup/figma-framelink-mcp-setup.md`, and only use screenshot/export as fallback after reporting the node data gap. |
| Node data is available but optional assets or screenshot/export are missing | Continue when they are not required for the requested implementation. If they are required, state the gap and ask before proceeding. |
| Design conflicts with project rules | Follow project rules, then note the tradeoff. |
| Implementation touches shared behavior | Broaden tests and verification beyond the narrow component. |

## Output Style

- Reply in the user's language (match the language of their latest message).
- Keep implementation notes concise.
- List the `tds-ui` modules used.
- Call out missing Figma sources, MCP access issues, visual verification gaps, and unrelated existing failures plainly.
- Include file references and verification commands/results when work is complete.


