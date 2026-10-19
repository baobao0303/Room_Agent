#!/usr/bin/env bash
set -euo pipefail

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BOLD='\033[1m'
NC='\033[0m'

SERVER_NAME="figma"
CONFIG_DIR="${HOME}/.codex"
CONFIG_FILE="${CONFIG_DIR}/config.toml"
NVM_SCRIPT="${HOME}/.nvm/nvm.sh"

msg_ok() { echo -e "  ${GREEN}[OK]${NC} $1"; }
msg_warn() { echo -e "  ${YELLOW}[WARN]${NC} $1"; }
msg_err() { echo -e "  ${RED}[ERROR]${NC} $1"; }

remove_existing_server_block() {
  local input_file="$1"
  local output_file="$2"
  awk '
    BEGIN { skip = 0 }
    /^\[mcp_servers\.(figma|figma-framelink)\]/ { skip = 1; next }
    /^\[/ && skip == 1 { skip = 0 }
    skip == 0 { print }
  ' "$input_file" > "$output_file"
}

toml_escape() {
  local value="$1"
  value="${value//\\/\\\\}"
  value="${value//\"/\\\"}"
  printf '%s' "$value"
}

echo ""
echo "============================================================"
echo "  Setup Figma Framelink MCP for Codex"
echo "============================================================"
echo ""

echo -e "${BOLD}[1/5] Checking Node.js and npm${NC}"
if ! command -v node >/dev/null 2>&1; then
  msg_err "Node.js is not installed. Install Node.js 20+ first."
  echo "  Ubuntu: curl -fsSL https://deb.nodesource.com/setup_20.x | sudo -E bash - && sudo apt-get install -y nodejs"
  echo "  macOS:  brew install node"
  exit 1
fi
if ! command -v npm >/dev/null 2>&1; then
  msg_err "npm is not installed."
  exit 1
fi
NODE_VERSION="$(node -v)"
NODE_MAJOR="$(echo "$NODE_VERSION" | tr -d 'v' | cut -d. -f1)"
echo "  Node.js: ${NODE_VERSION}"
echo "  npm:     $(npm -v)"
if [[ "$NODE_MAJOR" -lt 18 ]]; then
  msg_err "Node.js 18+ is required."
  exit 1
fi
if [[ "$NODE_MAJOR" -lt 20 ]]; then
  msg_warn "Node.js 20+ is recommended for figma-developer-mcp."
fi
msg_ok "Node.js and npm are available."
echo ""

echo -e "${BOLD}[2/5] Checking npx${NC}"
NPX_PATH="$(command -v npx || true)"
if [[ -z "$NPX_PATH" ]]; then
  msg_err "npx was not found. Reinstall Node.js/npm."
  exit 1
fi
msg_ok "npx found at ${NPX_PATH}"
if [[ ! -f "$NVM_SCRIPT" ]]; then
  msg_err "NVM script was not found at ${NVM_SCRIPT}."
  echo "  Install NVM first or create ${NVM_SCRIPT} before running this setup."
  exit 1
fi
msg_ok "NVM script found at ${NVM_SCRIPT}"
echo ""

echo -e "${BOLD}[3/5] Reading Figma Personal Access Token${NC}"
echo "  Create a token in Figma:"
echo "    1. Account menu -> Settings -> Security."
echo "    2. Personal access tokens -> Generate new token."
echo "    3. Name: tds-ui-figma-framelink"
echo "    4. Expiration: choose a suitable period (maximum is currently 90 days)."
echo "    5. Scope: select only File content: Read (file_content:read)."
echo "    6. Generate and copy it immediately; Figma displays it only once."
echo ""
echo "  No write, comments, variables, projects, or library scopes are required."
echo "  The token is visible while typing so Ubuntu/team setup is easier to understand."
echo "  Do not run this while screen sharing."
echo "  The token is written directly to ${CONFIG_FILE} for reliable Ubuntu/GUI startup."
echo "  Do not commit or share ${CONFIG_FILE}."
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

echo -e "${BOLD}[4/5] Choosing the Figma image directory${NC}"
DEFAULT_IMAGE_DIR="${PWD}/.figma-assets"
echo "  Downloaded Figma assets should be kept separately for each project."
echo "  Press Enter to use the project default, or enter a custom directory."
read -r -p "  Image directory [${DEFAULT_IMAGE_DIR}]: " IMAGE_DIR_INPUT
IMAGE_DIR_INPUT="${IMAGE_DIR_INPUT:-$DEFAULT_IMAGE_DIR}"

if [[ "$IMAGE_DIR_INPUT" == /* ]]; then
  IMAGE_DIR_CANDIDATE="$IMAGE_DIR_INPUT"
else
  IMAGE_DIR_CANDIDATE="${PWD}/${IMAGE_DIR_INPUT}"
fi

mkdir -p "$IMAGE_DIR_CANDIDATE"
IMAGE_DIR="$(cd "$IMAGE_DIR_CANDIDATE" && pwd -P)"
if [[ -z "$IMAGE_DIR" ]]; then
  msg_err "Could not resolve the image directory."
  exit 1
fi
msg_ok "Figma images will be stored in ${IMAGE_DIR}"
echo ""

echo -e "${BOLD}[5/5] Writing Codex MCP config${NC}"
mkdir -p "$CONFIG_DIR"
touch "$CONFIG_FILE"

BACKUP_FILE="${CONFIG_FILE}.bak.$(date +%Y%m%d%H%M%S)"
cp "$CONFIG_FILE" "$BACKUP_FILE"

TMP_FILE="$(mktemp)"
remove_existing_server_block "$CONFIG_FILE" "$TMP_FILE"
mv "$TMP_FILE" "$CONFIG_FILE"

printf -v NVM_SCRIPT_SHELL '%q' "$NVM_SCRIPT"
printf -v FIGMA_TOKEN_SHELL '%q' "$FIGMA_TOKEN"
printf -v IMAGE_DIR_SHELL '%q' "$IMAGE_DIR"
MCP_COMMAND="export DO_NOT_TRACK=1; source ${NVM_SCRIPT_SHELL} && exec npx -y figma-developer-mcp --figma-api-key=${FIGMA_TOKEN_SHELL} --image-dir=${IMAGE_DIR_SHELL} --stdio"
MCP_COMMAND_TOML="$(toml_escape "$MCP_COMMAND")"

cat >> "$CONFIG_FILE" <<EOF

[mcp_servers.${SERVER_NAME}]
command = "/bin/bash"
args = ["-lc", "${MCP_COMMAND_TOML}"]
env_vars = ["FIGMA_API_KEY"]
enabled = true
startup_timeout_sec = 30
tool_timeout_sec = 120
EOF

unset FIGMA_TOKEN FIGMA_TOKEN_SHELL
msg_ok "Wrote MCP server '${SERVER_NAME}' to ${CONFIG_FILE}"
echo "  Backup: ${BACKUP_FILE}"
echo ""

echo -e "${BOLD}Next steps${NC}"
echo "  1. Restart VS Code / Codex."
echo ""
echo "  2. In Codex, run:"
echo "     /mcp"
echo ""
echo "  3. Check that '${SERVER_NAME}' is active and provides:"
echo "     get_figma_data"
echo "     download_figma_images"
echo ""
echo "  Terminal check:"
echo "     codex mcp list"
echo ""
echo "============================================================"
echo -e "${GREEN}Done.${NC}"
