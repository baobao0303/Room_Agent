#!/usr/bin/env bash
# ==============================================================================
# scripts/rtk_profile_env.sh - RTK (Rust Token Killer) Profile Environment & Proxy
# Thực hiện chuẩn hóa Issue #5 trong Master Spec:
# docs/spec/ephemeral-sub-agent-orchestration-spec.md (Mục 16.3 & 17.2)
# ==============================================================================

ROLE="${1:-shared}"

# 1. Base RTK Environment
if [ -d "$HOME/.local/bin" ] && [[ ":$PATH:" != *":$HOME/.local/bin:"* ]]; then
    export PATH="$HOME/.local/bin:$PATH"
fi

export RTK_TELEMETRY_DISABLED=1
export RTK_COMPACT_MODE=1
export RTK_TEST_FAILURES_ONLY=1

# 2. Kiểm tra binary RTK
if ! command -v rtk &> /dev/null; then
    return 0 2>/dev/null || exit 0
fi

# 3. Role-specific CLI Aliases
case "$ROLE" in
    supervisor)
        alias git="rtk git"
        alias log="rtk git log -n 5"
        alias stat="rtk git status"
        alias gain="rtk gain"
        ;;
    pm)
        alias diff="rtk diff"
        alias find="rtk find"
        alias stat="rtk git status"
        ;;
    lead)
        alias git="rtk git"
        alias diff="rtk git diff"
        alias tsc="rtk tsc"
        alias log="rtk git log -n 10"
        ;;
    peer|peer2|peer3|peer4)
        alias git="rtk git"
        alias jest="rtk jest"
        alias tsc="rtk tsc"
        alias cat="rtk read -l aggressive"
        ;;
    design)
        alias diff="rtk diff"
        alias cat="rtk read"
        alias find="rtk find"
        ;;
    qc)
        alias jest="rtk jest"
        alias playwright="rtk test"
        alias err="rtk err"
        ;;
    security|security_sentinel)
        alias grep="rtk grep"
        alias diff="rtk diff"
        alias stat="rtk git status"
        ;;
    *)
        alias git="rtk git"
        alias jest="rtk jest"
        alias tsc="rtk tsc"
        alias cat="rtk read"
        alias find="rtk find"
        alias grep="rtk grep"
        ;;
esac
