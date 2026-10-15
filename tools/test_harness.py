#!/usr/bin/env python3
"""
tools/test_harness.py - End-to-end self-test script for Harness Manager and Floci DynamoDB.
"""
import os
import sys
import json

BASE_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
sys.path.insert(0, BASE_DIR)

from tools.harness_manager import HarnessManager

def run_tests():
    print("=== STARTING HARNESS FLOCI DYNAMODB SELF-TEST ===")
    mgr = HarnessManager()

    # 1. Test Syntax Validation
    print("1. Testing Validation Rules...")
    try:
        mgr.validate_work_item("User Story", "Invalid Title Without Dash", "Invalid desc")
        assert False, "Should fail on invalid title"
    except ValueError:
        print("  ✓ Caught invalid User Story title correctly.")

    try:
        mgr.validate_work_item("User Story", "[Auth] - User có thể login", "Not BDD")
        assert False, "Should fail on non-BDD description"
    except ValueError:
        print("  ✓ Caught non-BDD description correctly.")

    # 2. Test Add Work Item
    print("2. Testing Work Item Creation on Floci DynamoDB...")
    story = mgr.add_work_item(
        wi_type="User Story",
        title="[Authentication] – Khách hàng có thể đăng nhập bằng Google OAuth",
        description="As a Khách hàng, I want đăng nhập bằng Google, So that truy cập nhanh không cần nhớ mật khẩu.",
        priority="P1",
        story_points=5,
        area_path="Auth",
        iteration_path="Sprint 1",
        acceptance_criteria="1. Nút Google OAuth hoạt động. 2. Nhận JWT token hợp lệ."
    )
    story_id = story.get("id")
    print(f"  ✓ Created User Story #{story_id} in Floci (Storage: {story.get('storage')})")

    task = mgr.add_work_item(
        wi_type="Task",
        title="Auth Module - Tích hợp Google OAuth SDK",
        priority="P2",
        assigned_to="lead_dev",
        parent_id=story_id
    )
    task_id = task.get("id")
    print(f"  ✓ Created child Task #{task_id} in Floci (Storage: {task.get('storage')})")

    # 3. Test State Machine Lifecycle
    print("3. Testing State Machine Lifecycle...")
    # New -> Accepted (by BA)
    up1 = mgr.update_state(story_id, "Accepted")
    print(f"  ✓ Transitioned Story #{story_id} to Accepted")

    # Accepted -> Active (by Dev)
    up2 = mgr.update_state(story_id, "Active", assigned_to="peer_dev_1")
    print(f"  ✓ Transitioned Story #{story_id} to Active (Assigned: {up2.get('assigned_to')})")

    # 4. Test Query and Stats
    print("4. Testing Queries and Statistics...")
    items = mgr.list_work_items()
    print(f"  ✓ Listed {len(items)} total work items from Floci DynamoDB.")

    stats = mgr.get_stats()
    print("  ✓ Floci Database Statistics:")
    print(f"    - Total Work Items: {stats.get('total_work_items')}")
    print(f"    - Total Stories   : {stats.get('total_stories')}")
    print(f"    - Total Tools     : {stats.get('total_tools')}")
    for k, v in stats.get("by_type", {}).items():
        print(f"    - {k}: {v}")

    # 5. Clean up test artifacts
    print("5. Cleaning up Test Artifacts...")
    mgr.delete_work_item(task_id)
    mgr.delete_work_item(story_id)
    print(f"  ✓ Cleaned up test Task #{task_id} and Story #{story_id}")

    print("\n=== ALL HARNESS FLOCI TESTS PASSED SUCCESSFULLY! ===")

if __name__ == "__main__":
    run_tests()
