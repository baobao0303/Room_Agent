# Install TDS UI Figma Workflow

## 1. Install The Skill

Open a terminal at the skill root—the directory containing `SKILL.md` and
`scripts`—then copy the complete skill into the client you use:

```bash
# Codex
mkdir -p ~/.codex/skills
cp -R . ~/.codex/skills/tds-ui-figma
```

```bash
# Claude Code
mkdir -p ~/.claude/skills
cp -R . ~/.claude/skills/tds-ui-figma
```

Restart the client, then invoke the skill:

```text
Codex: $tds-ui-figma
Claude Code: /tds-ui-figma
```

The skill checks Framelink MCP before reading Figma. If MCP is missing, it
stops and gives the setup command for the current client.

## 2. Setup Figma Framelink MCP For Codex

Team members can run one bash script, enter their Figma token, then restart Codex:

Before running the script, create a Figma Personal Access Token:

1. Open Figma and go to **Account menu → Settings → Security**.
2. Scroll to **Personal access tokens** and select **Generate new token**.
3. Use the name `tds-ui-figma-framelink`.
4. Choose an expiration period. Figma currently allows up to 90 days.
5. Select only **File content: Read** (`file_content:read`). Framelink needs
   this scope to read nodes and download rendered images; no write,
   comments, variables, projects, or library scopes are required.
6. Generate and copy the token immediately. Figma shows it only once.

The token can read only Figma files that the account already has permission
to access. Do not paste it into AI chat, source code, commits, or screenshots.

```bash
bash ~/.codex/skills/tds-ui-figma/scripts/setup-figma-framelink-codex.sh
```

The script:

- checks Node.js and `npx`
- asks for a Figma Personal Access Token with visible input
- loads NVM through `/bin/bash -lc` when Codex starts the MCP server
- defaults downloads to the current project's `.figma-assets`
- accepts a custom directory for projects that need a different asset location
- checks and replaces existing `figma` and `figma-framelink` blocks
- passes the token directly through `--figma-api-key`

Do not run the script while screen sharing because the token is visible while typing.
`~/.codex/config.toml contains the Figma token`, so do not commit or share that
file.

After setup:

```bash
source ~/.bashrc
codex mcp list
```

Then restart VS Code/Codex and check `/mcp`.

## 3. Manual Codex MCP Config

If you prefer manual setup on Ubuntu, add this to `~/.codex/config.toml`:

```toml
[mcp_servers.figma]
command = "/bin/bash"
args = ["-lc", "export DO_NOT_TRACK=1; source /home/<username>/.nvm/nvm.sh && exec npx -y figma-developer-mcp --figma-api-key=figd_your_token_here --image-dir=/path/to/project/.figma-assets --stdio"]
env_vars = ["FIGMA_API_KEY"]
enabled = true
startup_timeout_sec = 30
tool_timeout_sec = 120
```

Replace `<username>`, the token, and the image path. Use a project-specific
`.figma-assets` directory by default, or provide a custom directory when the
project requires another download location.

## 4. Setup Figma Framelink MCP For Claude Code On Ubuntu

For Claude Code on Ubuntu, create the token with the same
`file_content:read` scope described in Step 2, then run:

```bash
bash ~/.claude/skills/tds-ui-figma/scripts/setup-figma-framelink-claude-ubuntu.sh
```

The script:

- checks Node.js and `npx`
- asks for a Figma Personal Access Token with visible input
- checks `~/.claude.json`
- migrates legacy `framelink` to `figma-framelink`
- writes the token directly to `~/.claude.json`
- detects Node PATH dynamically from the current machine's Node.js binary,
  equivalent to `dirname "$(which node)"`

Do not run the script while screen sharing. Do not commit or share `~/.claude.json` because it contains the token.

## 5. Manual Claude Code MCP Config

Framelink MCP provides `get_figma_data` and `download_figma_images` to read Figma designs.

Add this to `~/.claude.json`:

```json
{
  "mcpServers": {
    "figma-framelink": {
      "command": "npx",
      "args": [
        "-y",
        "figma-developer-mcp",
        "--stdio"
      ],
      "env": {
        "FIGMA_API_KEY": "figd_your_token_here",
        "PATH": "/home/<username>/.nvm/versions/node/v24.18.0/bin:/usr/local/sbin:/usr/local/bin"
      }
    }
  }
}
```

Replace:

- `figd_your_token_here` with your Figma Personal Access Token.
- `/home/<username>/.nvm/versions/node/v24.18.0/bin` with the output of:

```bash
dirname "$(which node)"
```

For security, prefer environment variables when possible. Do not commit `~/.claude.json` or any file containing a token.

The Claude Ubuntu setup script above fills this automatically from the actual Node.js version/path on the machine.

## 6. Setup TDS Token Cache

The skill reads token source URLs from:

```text
references/config/tds-token-sources.json
```

Sync the latest token JSON files:

```bash
node ~/.codex/skills/tds-ui-figma/scripts/sync-tds-tokens.js
```

When the TDS token JSON links are updated, tell Codex:

```text
Cap nhat TDS token map
```

Codex should run the sync script again.

## 7. Configure Project Theme Preset

Before Figma analysis, configure the map bundled with the installed skill:

```text
references/config/tds-project-token-map.json
```

Example:

```json
{
  "version": 1,
  "projects": {
    "my_project": {
      "themePreset": "green",
      "themes": {
        "default": {
          "modes": {
            "light": {},
            "dark": {}
          }
        }
      }
    }
  }
}
```

The distributed file starts with `projects.default.themePreset` set to `null`.
This means the first Figma workflow still stops and asks the developer to
choose a supported preset.

Supported presets are loaded from the latest remote `theme.json`, not from a hardcoded list:

```bash
node ~/.codex/skills/tds-ui-figma/scripts/set-tds-theme-preset.js --list
```

If the preset is missing, the skill must stop before Figma analysis because primary/secondary colors cannot be mapped accurately.

When a developer chooses a preset, save it to the installed skill:

```bash
node ~/.codex/skills/tds-ui-figma/scripts/set-tds-theme-preset.js green
```

This writes:

```text
~/.codex/skills/tds-ui-figma/references/config/tds-project-token-map.json
```

For a Claude installation, run the equivalent script under
`~/.claude/skills/tds-ui-figma`; it updates that skill's project map. Deleting
the remote token cache does not delete either project map.

## 8. Quick Test

Token lookup:

```bash
node ~/.codex/skills/tds-ui-figma/scripts/tds-token-lookup.js "#0C1014" text
```

Expected:

```json
{
  "status": "exact",
  "matches": ["tds-color-text-primary"]
}
```

Theme color without preset should stop:

```bash
node ~/.codex/skills/tds-ui-figma/scripts/tds-token-lookup.js "#27A745" background
```

Expected:

```json
{
  "status": "missing",
  "reason": "themePresetRequired"
}
```
