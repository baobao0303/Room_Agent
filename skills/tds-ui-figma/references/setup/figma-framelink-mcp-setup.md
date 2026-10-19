# Framelink Figma MCP Setup

Use this reference only when Framelink/Figma MCP access is missing, broken, or the user asks Codex to help set up Figma MCP with a Personal Access Token for Codex or Claude Code.

Framelink uses the `figma-developer-mcp` package (`GLips/Figma-Context-MCP`) and reads Figma through the REST API. It is read-only, returns compact component/layout metadata, and does not bypass Figma rate limits.

## Security Rules

- Do not ask the user to paste a Figma token into chat.
- Do not commit tokens to the repository.
- For Codex on Ubuntu, pass the token directly through `--figma-api-key` because
  GUI-launched Codex may not inherit shell profile variables.
- For Claude Code on Ubuntu, the team setup script writes the token directly into `~/.claude.json` because GUI-launched tools may not inherit shell profile variables.
- If a token is exposed, tell the user to revoke it and create a new one in Figma.

## User-Owned Step

Create the Figma Personal Access Token before running a setup script:

1. In the Figma file browser, open the account menu.
2. Select **Settings**, then **Security**.
3. Scroll to **Personal access tokens** and select **Generate new token**.
4. Enter `tds-ui-figma-framelink` as the token name.
5. Choose an expiration period. Figma currently permits up to 90 days.
6. Select only **File content: Read** (`file_content:read`).
7. Generate the token and copy it immediately; Figma displays it only once.

`file_content:read` is sufficient for Framelink to read file/node content and
download rendered images. Do not select write, comments, variables, projects,
or library scopes for this workflow.

Preferred Codex setup:

```bash
bash ~/.codex/skills/tds-ui-figma/scripts/setup-figma-framelink-codex.sh
```

The script asks for the token locally and configures
`[mcp_servers.figma]` in `~/.codex/config.toml`. It loads NVM through
`/bin/bash -lc`, defaults downloads to the current project's `.figma-assets`,
and accepts a custom directory when prompted.

`~/.codex/config.toml contains the Figma token`, so do not commit or share it.

Preferred Claude Code setup on Ubuntu:

```bash
bash ~/.claude/skills/tds-ui-figma/scripts/setup-figma-framelink-claude-ubuntu.sh
```

The script asks for the token locally with visible input, checks
`~/.claude.json`, migrates legacy `framelink` to `figma-framelink`, and
detects Node PATH dynamically from the actual Node.js binary on that machine.

## Codex Ubuntu Config

The setup script generates this shape. For manual setup, replace the username,
token, and image path:

```toml
[mcp_servers.figma]
command = "/bin/bash"
args = ["-lc", "export DO_NOT_TRACK=1; source /home/<username>/.nvm/nvm.sh && exec npx -y figma-developer-mcp --figma-api-key=figd_your_token_here --image-dir=/path/to/project/.figma-assets --stdio"]
env_vars = ["FIGMA_API_KEY"]
enabled = true
startup_timeout_sec = 30
tool_timeout_sec = 120
```

Use a project-specific `.figma-assets` directory by default. A custom directory
is valid when a project needs assets elsewhere. The setup script creates the
selected directory automatically.

## Verification

- Restart VS Code/Codex.
- Check `/mcp` in Codex or `codex mcp list` in CLI.
- Confirm `figma` is active before trying to read a Figma URL.
- Test with a specific Figma selection link that includes `node-id`.
- For color variables, do NOT call the REST Variables API. Use Framelink's resolved hex as evidence and map colors through `node scripts/tds-token-lookup.js`.

## Common Failures

| Symptom | Check |
|---|---|
| `figma` not listed | Restart Codex and verify the generated config block. |
| Token does not work | Verify token is valid and has view access to the file. |
| Ubuntu/VS Code cannot see token | Rerun the setup so the token is passed through `--figma-api-key`. |
| `403` on `/files/{key}` | Token is wrong, expired, or lacks access to the Figma file. |
| `403` on `/variables/local` | REST Variables API is not part of this workflow. Use Framelink node data plus `node scripts/tds-token-lookup.js` for color mapping. |
| `429` or sparse data | Figma REST API rate limit; use a smaller selected frame/node or a better seat/plan. |
| Node data too broad/noisy | Ask for Copy link to selection, not the full file URL. |
| VS Code Restricted Mode | Trust the workspace. |


---
## 📚 Điều Hướng: TDS Figma Rules & Setup
- **Mục lục chính:** [[SKILL]]
◀️ **Trước:** [[tds-ui-component-map]] | ⏭️ **Cuối mục**
