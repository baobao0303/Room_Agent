#!/usr/bin/env python3
"""
scripts/harness_seed.py - Seed initial sample data for test matrix and tools into Floci DynamoDB.
"""
import os
import sys
from datetime import datetime

BASE_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
sys.path.insert(0, BASE_DIR)

from tools.floci_client import FlociHarnessDB

def seed():
    db = FlociHarnessDB()
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    # 1. Seed Story with verify_command
    stories = [
        {
            "id": 1,
            "title": "[Auth] – User có thể đăng nhập bằng Google OAuth",
            "state": "Active",
            "priority": "P1",
            "verify_command": "cargo test auth::oauth",
            "last_verified_at": now_str,
            "last_verified_result": "PASSED (0.24s)",
            "created_at": now_str,
            "updated_at": now_str
        },
        {
            "id": 2,
            "title": "[Payment] – Khách hàng có thể quét mã QR",
            "state": "New",
            "priority": "P0",
            "verify_command": "cargo test payment::qr",
            "last_verified_at": None,
            "last_verified_result": "UNVERIFIED",
            "created_at": now_str,
            "updated_at": now_str
        },
        {
            "id": 3,
            "title": "[Dashboard] – Quản trị viên có thể xem biểu đồ doanh thu",
            "state": "Accepted",
            "priority": "P2",
            "verify_command": "npm run test:dashboard",
            "last_verified_at": now_str,
            "last_verified_result": "PASSED",
            "created_at": now_str,
            "updated_at": now_str
        }
    ]

    for s in stories:
        db.put_story(s)

    # 2. Seed Tools
    tools = [
        {
            "name": "cargo-test-runner",
            "command": "cargo test -- --nocapture",
            "description": "Executes Rust unit and integration tests",
            "responsibility": "test_execution",
            "created_at": now_str
        },
        {
            "name": "query-reader",
            "command": "python3 tools/query_reader.py",
            "description": "Semantic BM25 text & directory search",
            "responsibility": "code_exploration",
            "created_at": now_str
        },
        {
            "name": "research-agent",
            "command": "python3 tools/research/research_agent.py",
            "description": "Tiered architecture and technical research assistant",
            "responsibility": "deep_research",
            "created_at": now_str
        }
    ]

    for t in tools:
        db.put_tool(t)

    print("✓ Seeded sample stories, test verification commands, and tools into Floci DynamoDB")

if __name__ == "__main__":
    seed()
