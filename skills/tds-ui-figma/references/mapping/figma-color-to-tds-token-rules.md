# TDS Figma Color Mapping

Use this reference when Framelink returns Figma colors or typography and the implementation needs TDS classes.

## Remote Token Sources

The canonical token files are configured in `references/config/tds-token-sources.json`:

| Source | URL | Purpose |
|---|---|---|
| `themeTokens` | `https://tds.tmtco.org/assets/tds-design-token/theme.json` | Theme preset array used to resolve primary/secondary swapping. Supported preset names must be read from this file after sync. |
| `globalTokens` | `https://tds.tmtco.org/assets/tds-design-token/global.json` | Primitive/global tokens such as neutral, red, spacing, radius, font size. |
| `aliasTokens` | `https://tds.tmtco.org/assets/tds-design-token/alias.json` | Semantic aliases such as `tds-color-text-primary`, `tds-color-surface-low`, typography, icon size. |

Run `node scripts/sync-tds-tokens.js` to prefetch them. `node scripts/tds-token-lookup.js` also syncs automatically when the cache is missing.

Cache directory:

1. `$TDS_TOKEN_CACHE_DIR`
2. `$XDG_CACHE_HOME/tds-ui-figma/tokens`
3. `%LOCALAPPDATA%/tds-ui-figma/tokens`
4. `~/.cache/tds-ui-figma/tokens`

Set `TDS_TOKEN_LOOKUP_OFFLINE=1` to force cached files only.

## Source Order

1. If Figma returns a semantic alias, generate the semantic class directly, for example `Alias/color/text/secondary` -> `tds-color-text-secondary`.
2. If Figma returns a global/primitive path, generate the property utility, for example `Global/color/primary/50` -> `bg-tds-color-primary-50-light dark:bg-tds-color-primary-50-dark`.
3. If Framelink returns only a resolved hex, use:

```bash
node <skill-dir>/scripts/tds-token-lookup.js <hex> <role> [project] [themePreset] [mode]
```

Lookup order inside the helper:

1. Explicit `TDS_PROJECT_MAP`, then the skill-local `references/config/tds-project-token-map.json`. Legacy project-local `.claude` and `.codex` maps are read-only fallbacks.
2. Remote `theme.json` cache for selected theme preset, so primary/secondary colors follow the active project theme.
3. Remote `alias.json` cache for semantic classes.
4. Remote `global.json` cache for primitive/global classes.

## Rules

- `status=exact`: use the returned class.
- `status=ambiguous`: ask the user to choose a class.
- `status=missing`: ask the user to confirm a class or allow a custom local color.
- `reason=themePresetRequired`: run `node <skill-dir>/scripts/set-tds-theme-preset.js --list`, ask the user to choose a supported preset from remote `theme.json`, save it, and rerun lookup with that value.
- `reason=unsupportedThemePreset`: the chosen preset is not present in remote `theme.json`; report that the current theme/color is unsupported and ask the user to choose one of `supportedThemePresets`.
- Do not add a new project override unless the user requests it.
- Do not manually map `#HEX -> tds-color-*` outside the helper or explicit Figma alias/global evidence.

## Project Override Schema

```json
{
  "version": 1,
  "projects": {
    "your_project_name": {
      "themePreset": "green",
      "themes": {
        "default": {
          "modes": {
            "light": {
              "#535A67": {
                "text": ["tds-color-text-quaternary"]
              }
            },
            "dark": {}
          }
        }
      }
    }
  }
}
```

## Generated Class Rules

Use semantic aliases directly:

| Figma alias | Generated class |
|---|---|
| `Alias/color/background/info/subtle` | `tds-color-background-info-subtle` |
| `Alias/color/text/secondary` | `tds-color-text-secondary` |
| `Alias/color/border/primary` | `tds-color-border-primary` |
| `Alias/color/icon/success` | `tds-color-icon-success` |

Use property prefixes only for global/primitive tokens:

| Role | Prefix |
|---|---|
| `text`, `icon` | `text-` |
| `background`, `surface` | `bg-` |
| `border` | `border-` |
| `ring` | `ring-` |

## Typography Reminder

- Typography classes must use the `tds-` prefix, for example `tds-body-2`, `tds-caption-1`, `tds-heading-6`.
- Do not use `text-body-2`, `text-heading-6`.
- Do not merge font weight into the size class. Use `tds-body-2 font-semibold`, not `tds-body-2-semibold`.


---
## 📚 Điều Hướng: TDS Figma Rules & Setup
- **Mục lục chính:** [[SKILL]]
⏮️ **Đầu mục** | ▶️ **Tiếp:** [[figma-to-tds-ui-rules]]
