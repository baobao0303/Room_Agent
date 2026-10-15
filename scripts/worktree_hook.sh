#!/usr/bin/env bash
# =============================================================================
# Paseo Worktree Lifecycle Hook Runner (pre-create | post-create | pre-destroy)
# Invoked automatically by Paseo worktree setup/teardown (configured in paseo.json)
# =============================================================================
set -euo pipefail

PHASE="${1:-post-create}"
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_ROOT="$(cd "${SCRIPT_DIR}/.." && pwd)"

export PASEO_SOURCE_CHECKOUT_PATH="${PASEO_SOURCE_CHECKOUT_PATH:-${PROJECT_ROOT}}"
export PASEO_ROOT_PATH="${PASEO_ROOT_PATH:-${PROJECT_ROOT}}"
export PASEO_WORKTREE_PATH="${PASEO_WORKTREE_PATH:-$(pwd)}"
export PASEO_BRANCH_NAME="${PASEO_BRANCH_NAME:-$(git rev-parse --abbrev-ref HEAD 2>/dev/null || echo main)}"
export PASEO_WORKTREE_PORT="${PASEO_WORKTREE_PORT:-8765}"

python3 "${PROJECT_ROOT}/tools/paseo_hooks.py" worktree "${PHASE}"
