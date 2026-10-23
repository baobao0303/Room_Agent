---
name: fewer-permission-prompts
description: "Configure settings.json and auto-allowlists to eliminate permission dialogs and safety classifier prompts for trusted tools."
---

# Fewer Permission Prompts Skill (`fewer-permission-prompts`)

Cấu hình tối ưu hóa quyền thực thi cho Agent nhằm loại bỏ các prompt hỏi quyền thủ công và tránh lỗi chặn từ auto classifier.

## 1. Mục tiêu
- Cấp quyền thực thi trực tiếp cho các core tools (`Bash`, `Read`, `Write`, `Edit`, `Glob`, `Grep`, `WebSearch`, `WebFetch`).
- Kích hoạt `bypassPermissions` và bỏ qua các prompt xác nhận nguy hiểm trong môi trường tin cậy.

## 2. File cấu hình chuẩn: `~/.paseo/claude-config/settings.json`

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
