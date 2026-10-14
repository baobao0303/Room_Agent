#!/usr/bin/env bash
# Source Code Context Hook for Claude Code (UserPromptSubmit)
# Automatically scans active projects, git branches, status, and query_reader snippets.

set -e

PROJECTS_DIR="/home/baoltb/Desktop/Paseo_Project/projects"
TOOLS_DIR="/home/baoltb/Desktop/Paseo_Project/tools"

# Read stdin JSON from Claude Code
INPUT_JSON=$(cat || echo "{}")

USER_PROMPT=$(python3 -c "
import json, sys
try:
    data = json.loads(sys.argv[1])
    print(data.get('userPrompt', ''))
except Exception:
    print('')
" "$INPUT_JSON" 2>/dev/null || echo "")

CONTEXT_LINES=()
CONTEXT_LINES+=("=== KHÔNG GIAN DỰ ÁN (WORKSPACE SOURCE CONTEXT) ===")

if [ -d "$PROJECTS_DIR" ]; then
  for dir in "$PROJECTS_DIR"/*/; do
    if [ -d "$dir/.git" ]; then
      repo_name=$(basename "$dir")
      branch=$(git -C "$dir" branch --show-current 2>/dev/null || echo "detached")
      last_commit=$(git -C "$dir" log -1 --oneline 2>/dev/null || echo "none")
      status=$(git -C "$dir" status -s 2>/dev/null || echo "")

      CONTEXT_LINES+=("• [$repo_name] Nhánh: $branch | Commit gần nhất: $last_commit")
      if [ -n "$status" ]; then
        CONTEXT_LINES+=("  Files đang sửa đổi (uncommitted):")
        while IFS= read -r line; do
          CONTEXT_LINES+=("    $line")
        done <<< "$status"
      else
        CONTEXT_LINES+=("  Trạng thái: Sạch (clean)")
      fi
    fi
  done
fi

# If user prompt mentions specific files or asks to inspect code, run query_reader snippet
SNIPPET_CONTEXT=""
if [ -n "$USER_PROMPT" ] && [ -f "$TOOLS_DIR/query_reader.py" ]; then
  # Extract potential file or path mentioned in user prompt
  DETECTED_PATH=$(python3 -c "
import sys, re
prompt = sys.argv[1]
# Match paths or filenames like apps/..., libs/..., *.ts, *.json, *.md
matches = re.findall(r'([a-zA-Z0-9_\-\./]+\.(?:ts|js|json|md|html|scss|css|py|sh))', prompt)
if matches:
    print(matches[0])
" "$USER_PROMPT" 2>/dev/null || echo "")

  if [ -n "$DETECTED_PATH" ]; then
    # Search for this path in projects
    FOUND_FILE=$(find "$PROJECTS_DIR" -path "*$DETECTED_PATH" -type f 2>/dev/null | head -n 1 || echo "")
    if [ -n "$FOUND_FILE" ]; then
      SNIPPET_OUTPUT=$(python3 "$TOOLS_DIR/query_reader.py" "$FOUND_FILE" "$USER_PROMPT" -n 2 -m 30 2>/dev/null || echo "")
      if [ -n "$SNIPPET_OUTPUT" ]; then
        CONTEXT_LINES+=("")
        CONTEXT_LINES+=("=== TỰ ĐỘNG TRÍCH XUẤT SOURCE TỪ: $DETECTED_PATH ===")
        while IFS= read -r sline; do
          CONTEXT_LINES+=("$sline")
        done <<< "$SNIPPET_OUTPUT"
      fi
    fi
  fi
fi

# Join lines
JOINED_CONTEXT=$(printf "%s\n" "${CONTEXT_LINES[@]}")

# Output JSON with hookSpecificOutput
python3 -c "
import json, sys
context = sys.stdin.read()
output = {
    'hookSpecificOutput': {
        'additionalContext': context
    }
}
print(json.dumps(output))
" <<< "$JOINED_CONTEXT"

exit 0
