---
name: fewer-permission-prompts
description: "Configure settings.json and auto-allowlists to eliminate permission dialogs and safety classifier prompts for trusted tools."
---

# Fewer Permission Prompts Skill (`fewer-permission-prompts`)

Configure execution permissions for Agent to eliminate manual permission prompts and prevent blocking errors from safety auto-classifiers.

## 1. Objectives
- Grant direct execution permissions for core tools (`Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebSearch`, `WebFetch`).
- Enable `bypassPermissions` and bypass dangerous confirmation prompts in trusted local environments.

## 2. Canonical Configuration File: `~/.paseo/claude-config/settings.json`

```json
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep",
      "WebSearch",
      "WebFetch"
    ],
    "defaultMode": "bypassPermissions",
    "disableAutoMode": "disable"
  },
  "skipDangerousModePermissionPrompt": true,
  "skipAutoPermissionPrompt": true,
  "allowDangerouslySkipPermissions": true
}
```

## 3. Lệnh kiểm tra và áp dụng
```bash
# Đồng bộ cài đặt quyền
mkdir -p ~/.paseo/claude-config
cat << 'EOF' > ~/.paseo/claude-config/settings.json
{
  "permissions": {
    "allow": [
      "Bash",
      "Read",
      "Write",
      "Edit",
      "Glob",
      "Grep",
      "WebSearch",
      "WebFetch"
    ],
    "defaultMode": "bypassPermissions"
  },
  "skipDangerousModePermissionPrompt": true,
  "skipAutoPermissionPrompt": true,
  "allowDangerouslySkipPermissions": true
}
EOF
```
