#!/usr/bin/env python3
"""
tools/dual_ide_hook.py - Universal Dual-IDE Hook Router for Orca & Paseo.

Provides a unified lifecycle bridge between:
1. Orca IDE: Visual Workspace, PTY Terminals, Ephemeral Tabs, Live Kanban Board.
2. Paseo IDE / Claude Code: Headless Daemon, Background Sub-Agents, Handoff Memos, CLI Hooks.

Features:
- Detects running runtime (Orca vs Paseo).
- Bóc tách tiền tố tư duy: [THUẬN], [NGHỊCH], [THẢO-LUẬN], [TÍNH-NĂNG], [FIX-BUG], [BẪY-LỖI], [REFACTOR], [REVIEW], [QUÉT], [TEST], [LƯỠNG-DIỆN].
- Tự động nạp chỉ thị tư duy vào context LLM.
- Đồng bộ hóa trạng thái terminal & board sang Orca nếu Orca đang chạy.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional, Tuple

PROJECT_ROOT = Path(__file__).resolve().parent.parent
REG_FILE = PROJECT_ROOT / "bmad" / "rooms" / "agent_terminals.json"
PROGRESS_FILE = PROJECT_ROOT / ".harness_progress.json"

# ==============================================================================
# PREFIX TAXONOMY & ROUTING DIRECTIVES
# ==============================================================================
PREFIX_MAP = {
    "thảo-luận": {
        "pattern": r"\[(thảo luận|thảo-luận|thao luan|thao-luan|discuss|advisory)\]",
        "category": "DISCUSS",
        "mode": "THẢO LUẬN (Architectural ADR / Discussion)",
        "subagent": "strategic-reasoning-architect + gemini-codebase-analyzer",
        "route": "PM ➔ Lead Dev (KHÔNG CODE, chốt giải pháp đồng thuận và xuất biên bản ADR)",
        "directive": "BẮT BUỘC KHÔNG VIẾT CODE. PM thẩm định Feasibility qua Kev System One (<50ms). Lead Dev & Sub-Agents phân tích đánh đổi (trade-offs), thu thập bằng chứng codebase và xuất biên bản ADR tại bmad/adrs/."
    },
    "thuận": {
        "pattern": r"\[(thuận|thuan|forward|happy-path|happy|tính-năng|tinh-nang|feature)\]",
        "category": "FORWARD",
        "mode": "THUẬN (Forward / Happy Path / Feature)",
        "subagent": "Peer Dev (Maker) + slpc-qc-verifier (Checker)",
        "route": "PM ➔ Lead (Zero-Search) ➔ Peer (Code) ➔ QC (5-Stage ISTQB) ➔ Closed",
        "directive": "Tập trung hoàn thiện nhanh luồng chạy chuẩn (Golden Flow): input hợp lệ, kết quả mong đợi, DTO chuẩn, tối ưu diff theo triết lý Lazy Senior Dev / YAGNI, không over-engineering."
    },
    "nghịch": {
        "pattern": r"\[(nghịch|nghich|reverse|edge-case|adversarial|edge|bẫy-lỗi|bay-loi)\]",
        "category": "REVERSE",
        "mode": "NGHỊCH (Reverse / Edge / Adversarial)",
        "subagent": "strategic-reasoning-architect + slpc-qc-verifier",
        "route": "Lead (Mock cực hạn) ➔ Peer (Fail-safe) ➔ QC (BVA Stress Test)",
        "directive": "Tập trung truy quét kịch bản biên và bẫy lỗi: dữ liệu rỗng/null/undefined, boundary values (BVA), timeout mạng, race condition, fail-safe degradation, rollback và cơ chế chống crash."
    },
    "fix-bug": {
        "pattern": r"\[(fix-bug|fixbug|sửa-lỗi|sua-loi|bug)\]",
        "category": "FIX_BUG",
        "mode": "SỬA LỖI (Root Cause Analysis & Minimal Fix)",
        "subagent": "gemini-codebase-analyzer + Peer Dev",
        "route": "Lead (Tìm RCA) ➔ Peer (Viết regression test trước, sửa sau) ➔ QC verify",
        "directive": "Tìm nguyên nhân gốc (RCA) trước khi sửa. Viết regression test tái hiện lỗi, sau đó thực hiện diff tối thiểu sửa triệt để bug, không làm ảnh hưởng các luồng xung quanh."
    },
    "refactor": {
        "pattern": r"\[(refactor|tối-ưu|toi-uu|clean|cleanup)\]",
        "category": "REFACTOR",
        "mode": "TỐI ƯU HÓA (YAGNI & Code Cleanliness)",
        "subagent": "simplify + Peer Dev",
        "route": "Lead (Khoanh vùng scope) ➔ Peer (Rút gọn mã nguồn) ➔ QC (So khớp regression)",
        "directive": "Rút gọn mã nguồn, xóa dead code, loại bỏ boilerplate thừa theo nguyên tắc YAGNI. 0 thay đổi logic nghiệp vụ, 100% test cũ phải pass."
    },
    "review": {
        "pattern": r"\[(review|rà-soát|ra-soat|audit)\]",
        "category": "REVIEW",
        "mode": "RÀ SOÁT CHÉO (Multi-Perspective Code Review)",
        "subagent": "gemini-codebase-analyzer + strategic-reasoning-architect + slpc-qc-verifier",
        "route": "Bộ 3 Sub-Agents review độc lập (Spec, Code, Security) ➔ Tổng hợp report",
        "directive": "KHÔNG SỬA CODE. Đánh giá 3 chiều: (1) Chuẩn spec & AC; (2) Chất lượng code Angular 18/Strict Typing; (3) An toàn bảo mật & anti-leak."
    },
    "quét": {
        "pattern": r"\[(quét|quet|khảo-sát|khao-sat|scan)\]",
        "category": "SCAN",
        "mode": "KHẢO SÁT HỆ THỐNG (Repository Exploration)",
        "subagent": "gemini-codebase-analyzer (1M+ token context)",
        "route": "Quét toàn cục monorepo ➔ Lập bản đồ phụ thuộc & điểm chạm",
        "directive": "KHÔNG TẠO TASK CODE. Dùng gemini context lớn quét sâu cấu trúc codebase, lập bản đồ phụ thuộc component/service và dự báo vùng ảnh hưởng (blast radius)."
    },
    "test": {
        "pattern": r"\[(test|kiểm-thử|kiem-thu|qc-test)\]",
        "category": "TEST",
        "mode": "KIỂM ĐỊNH ĐỘC LẬP (5-Stage ISTQB Generation)",
        "subagent": "slpc-qc-verifier",
        "route": "QC Gate ➔ Sinh test matrix 5 giai đoạn ➔ Chạy runner Exit 0",
        "directive": "Sinh unit test theo chuẩn ISTQB 5-Stage (REQ, TP, EP/BVA, Decision Table, State Transition). Đảm bảo 100% test pass exit code 0."
    },
    "lưỡng-diện": {
        "pattern": r"\[(lưỡng-diện|luong-dien|dual|both)\]",
        "category": "DUAL",
        "mode": "LƯỠNG DIỆN (Dual-Anchor: Forward + Reverse)",
        "subagent": "Đầy đủ SLPPC Sub-Agents",
        "route": "PM ➔ Lead ➔ Peer ➔ QC (Phân tích song song 2 mặt)",
        "directive": "BẮT BUỘC tư duy 2 mặt song song trong khối Thinking: (1) [THUẬN]: Happy path chuẩn spec; (2) [NGHỊCH]: Dữ liệu biên, trường hợp ngoại lệ, testcase fail, fail-safe."
    }
}


def parse_prompt_intent(prompt: str) -> Tuple[str, Dict[str, str]]:
    """Phân tích tiền tố và trả về (prompt_đã_lọc_tiền_tố, thông_tin_cấu_hình)."""
    p_lower = prompt.lower()
    for key, info in PREFIX_MAP.items():
        if re.search(info["pattern"], p_lower):
            cleaned = re.sub(info["pattern"], "", prompt, flags=re.IGNORECASE).strip()
            return cleaned, info

    # Mặc định: Lưỡng diện
    return prompt, PREFIX_MAP["lưỡng-diện"]


# ==============================================================================
# DUAL-ENVIRONMENT SENSING (ORCA VS PASEO)
# ==============================================================================
def detect_environments() -> Dict[str, Any]:
    """Kiểm tra sự hiện diện và trạng thái của Orca và Paseo."""
    orca_available = False
    orca_running = False
    orca_terms: list[Dict[str, Any]] = []

    if shutil.which("orca"):
        orca_available = True
        try:
            res = subprocess.run(["orca", "status", "--json"], capture_output=True, text=True, timeout=2)
            if res.returncode == 0:
                data = json.loads(res.stdout)
                orca_running = data.get("result", {}).get("runtime", {}).get("reachable", False)
        except Exception:
            pass

        if orca_running:
            try:
                t_res = subprocess.run(["orca", "terminal", "list", "--json"], capture_output=True, text=True, timeout=2)
                if t_res.returncode == 0:
                    t_data = json.loads(t_res.stdout)
                    orca_terms = t_data.get("result", {}).get("terminals", [])
            except Exception:
                pass

    paseo_available = bool(shutil.which("paseo"))
    paseo_config = (Path.home() / ".paseo" / "config.json").is_file()

    return {
        "orca": {
            "available": orca_available,
            "running": orca_running,
            "terminals_count": len(orca_terms),
            "terminals": orca_terms
        },
        "paseo": {
            "available": paseo_available,
            "configured": paseo_config,
        },
        "active_primary": "orca" if orca_running else "paseo"
    }


def sync_orca_terminals_if_needed(intent: Dict[str, str], orca_info: Dict[str, Any]):
    """Đồng bộ tiêu đề terminal trên Orca theo intent."""
    if not orca_info.get("running"):
        return

    # Ghi nhận trạng thái intent vào latest handoff
    sup_memo = PROJECT_ROOT / "bmad" / "rooms" / "supervisor" / "latest_handoff.md"
    try:
        sup_memo.parent.mkdir(parents=True, exist_ok=True)
        content = (
            f"# DUAL-IDE HOOK DISPATCH INTENT\n"
            f"- **Thời gian**: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"- **Chế độ tư duy**: {intent['mode']}\n"
            f"- **Tiến trình định tuyến**: {intent['route']}\n"
            f"- **Chỉ thị cốt lõi**: {intent['directive']}\n"
        )
        sup_memo.write_text(content, encoding="utf-8")
    except Exception:
        pass


def build_hook_output(cleaned_prompt: str, intent: Dict[str, str], env: Dict[str, Any]) -> str:
    """Tạo nội dung additionalContext bổ sung cho LLM."""
    orca_status_str = "🟢 Đang chạy (Active PTY Workspace)" if env["orca"]["running"] else "⚪ Ngoại tuyến (Offline/Headless)"
    paseo_status_str = "🟢 Sẵn sàng (Daemon/Profiles Configured)" if env["paseo"]["configured"] else "⚪ Chưa cấu hình"

    lines = [
        "═══════════════════════════════════════════════════════════════════════",
        "🎯 [DUAL-IDE UNIVERSAL HOOK - ORCA & PASEO RUNTIME ROUTER]",
        "═══════════════════════════════════════════════════════════════════════",
        f"• Môi trường thực thi  : [Orca: {orca_status_str}] | [Paseo: {paseo_status_str}]",
        f"• Chế độ tư duy (Mode) : {intent['mode']}",
        f"• Sub-Agent phụ trách  : {intent['subagent']}",
        f"• Luồng chuyển giao    : {intent['route']}",
        "───────────────────────────────────────────────────────────────────────",
        f"🧠 CHỈ THỊ BẮT BUỘC TRONG KHỐI THINKING:",
        f"{intent['directive']}",
        "───────────────────────────────────────────────────────────────────────",
    ]

    if intent["category"] == "DISCUSS":
        lines.append("⚠️ LƯU Ý VAI TRÒ: Đây là luồng [THẢO LUẬN]. KHÔNG tạo Task thi công mã nguồn cho Peer.")
        lines.append("  Chỉ tổng hợp bằng chứng thực nghiệm và xuất biên bản ADR (bmad/adrs/).")
    elif intent["category"] in ("FORWARD", "FIX_BUG", "REFACTOR"):
        lines.append("🚀 LƯU Ý VAI TRÒ: Yêu cầu can thiệp mã nguồn. Đi đầy đủ 5 cổng SLPPC:")
        lines.append("  Supervisor ➔ PM (Kev <50ms) ➔ Lead (Zero-Search) ➔ Peer (Code) ➔ QC (ISTQB Closed).")
    elif intent["category"] == "TEST":
        lines.append("🧪 LƯU Ý VAI TRÒ: Nhảy thẳng vào QC Gate. Chạy tools/qc_test_generator.py sinh 5-Stage ISTQB.")

    lines.append("═══════════════════════════════════════════════════════════════════════")
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(description="Universal Dual-IDE Hook Router for Orca & Paseo")
    parser.add_argument("--prompt", help="User prompt string")
    parser.add_argument("--json", action="store_true", help="Output pure JSON for Claude Code hook")
    args = parser.parse_args()

    raw_prompt = args.prompt or ""

    # Đọc từ stdin nếu stdin có dữ liệu và không truyền --prompt
    if not raw_prompt and not sys.stdin.isatty():
        try:
            stdin_data = sys.stdin.read()
            if stdin_data.strip():
                try:
                    payload = json.loads(stdin_data)
                    raw_prompt = payload.get("userPrompt") or payload.get("prompt") or stdin_data
                except Exception:
                    raw_prompt = stdin_data
        except Exception:
            raw_prompt = ""

    cleaned_prompt, intent = parse_prompt_intent(raw_prompt)
    env = detect_environments()
    sync_orca_terminals_if_needed(intent, env["orca"])
    context_str = build_hook_output(cleaned_prompt, intent, env)

    if args.json or not sys.stdout.isatty():
        # Định dạng chuẩn Claude Code Hook Specific Output
        output = {
            "hookSpecificOutput": {
                "additionalContext": context_str
            }
        }
        print(json.dumps(output, ensure_ascii=False))
    else:
        print(context_str)


if __name__ == "__main__":
    main()
