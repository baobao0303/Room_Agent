#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

SERVER_NAME="figma-framelink"
CLAUDE_FILE="${HOME}/.claude.json"

msg_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
msg_warn() { echo -e "  ${YELLOW}[WARN]${NC} $1"; }
msg_err() { echo -e "  ${RED}[ERROR]${NC} $1"; }

echo ""
echo "============================================================"
echo "  Setup Figma Framelink MCP for Claude Code on Ubuntu"
echo "============================================================"
echo ""

echo -e "${BOLD}[1/4] Checking Node.js and npx${NC}"
if ! command -v node >/dev/null 2>&1; then
  msg_err "Node.js is not installed. Install Node.js 20+ first."
  echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
  exit 1
fi
if ! command -v npx >/dev/null 2>&1; then
  msg_err "npx was not found. Reinstall Node.js/npm."
  exit 1
fi

NODE_PATH="$(command -v node)"
NPX_PATH="$(command -v npx)"
NODE_BIN_DIR="$(dirname "$NODE_PATH")"
NODE_VERSION="$(node -v)"
NODE_MAJOR="$(echo "$NODE_VERSION" | tr -d 'v' | cut -d. -f1)"
CLAUDE_PATH="${NODE_BIN_DIR}:/usr/local/sbin:/usr/local/bin:/usr/sbin:/usr/bin:/sbin:/bin"

echo "  Node.js: ${NODE_VERSION}"
echo "  node:    ${NODE_PATH}"
echo "  npx:     ${NPX_PATH}"
echo "  PATH:    ${CLAUDE_PATH}"
if [[ "$NODE_MAJOR" -lt 18 ]]; then
  msg_err "Node.js 18+ is required."
  exit 1
fi
if [[ "$NODE_MAJOR" -lt 20 ]]; then
  msg_warn "Node.js 20+ is recommended for figma-developer-mcp."
fi
msg_ok "Node.js and npx are available."
echo ""

echo -e "${BOLD}[2/4] Reading Figma Personal Access Token${NC}"
echo "  Create a token in Figma:"
echo "    1. Account menu -> Settings -> Security."
echo "    2. Personal access tokens -> Generate new token."
echo "    3. Name: tds-ui-figma-framelink"
echo "    4. Expiration: choose a suitable period (maximum is currently 90 days)."
echo "    5. Scope: select only File content: Read (file_content:read)."
echo "    6. Generate and copy it immediately; Figma displays it only once."
echo ""
echo "  No write, comments, variables, projects, or library scopes are required."
echo "  The token is visible while typing so team setup is easier to understand."
echo "  Do not run this while screen sharing."
echo "  This Claude setup writes the token directly into ${CLAUDE_FILE}."
echo "  Do not commit or share ${CLAUDE_FILE}."
echo ""

read -r -p "  Enter Figma token (visible input): " FIGMA_TOKEN
echo ""
if [[ -z "${FIGMA_TOKEN}" ]]; then
  msg_err "Token is empty."
  exit 1
fi
if [[ ! "$FIGMA_TOKEN" =~ ^figd_ ]]; then
  msg_warn "Token does not start with figd_. Figma tokens usually start with figd_."
  read -r -p "  Continue anyway? (y/N): " CONTINUE_ANYWAY
  if [[ "${CONTINUE_ANYWAY,,}" != "y" ]]; then
    msg_err "Aborted."
    exit 1
  fi
fi
echo ""

echo -e "${BOLD}[3/4] Updating Claude MCP config${NC}"
mkdir -p "$(dirname "$CLAUDE_FILE")"
if [[ -f "$CLAUDE_FILE" ]]; then
  BACKUP_FILE="${CLAUDE_FILE}.bak.$(date +%Y%m%d%H%M%S)"
  cp "$CLAUDE_FILE" "$BACKUP_FILE"
  echo "  Existing config found."
  echo "  Backup: ${BACKUP_FILE}"
else
  echo "  No existing ${CLAUDE_FILE}; creating a new one."
fi

node - "$CLAUDE_FILE" "$FIGMA_TOKEN" "$CLAUDE_PATH" <<'NODE'
const fs = require('fs');

const [file, token, pathValue] = process.argv.slice(2);
let config = {};

if (fs.existsSync(file)) {
  const raw = fs.readFileSync(file, 'utf8').trim();
  if (raw) {
    try {
      config = JSON.parse(raw);
    } catch (error) {
      console.error(`  [ERROR] ${file} is not valid JSON: ${error.message}`);
      process.exit(1);
    }
  }
}

if (!config || typeof config !== 'object' || Array.isArray(config)) {
  config = {};
}

if (!config.mcpServers || typeof config.mcpServers !== 'object' || Array.isArray(config.mcpServers)) {
  config.mcpServers = {};
}

const legacyExisted = Boolean(config.mcpServers.framelink);
const canonicalExisted = Boolean(config.mcpServers['figma-framelink']);
delete config.mcpServers.framelink;
config.mcpServers['figma-framelink'] = {
  command: 'npx',
  args: ['-y', 'figma-developer-mcp', '--stdio'],
  env: {
    FIGMA_API_KEY: token,
    PATH: pathValue,
  },
};

fs.writeFileSync(file, `${JSON.stringify(config, null, 2)}\n`);
const action = legacyExisted
  ? 'Migrated mcpServers.framelink to'
  : canonicalExisted
    ? 'Updated'
    : 'Added';
console.log(`  ${action} mcpServers.figma-framelink`);
NODE

unset FIGMA_TOKEN
msg_ok "Wrote MCP server '${SERVER_NAME}' to ${CLAUDE_FILE}"
echo ""

echo -e "${BOLD}[4/4] Next steps${NC}"
echo "  1. Restart Claude Code."
echo ""
echo "  2. Check that '${SERVER_NAME}' is active and provides:"
echo "     get_figma_data"
echo "     download_figma_images"
echo ""
echo "============================================================"
echo -e "${GREEN}Done.${NC}"
