#!/usr/bin/env python3
"""
scripts/harness_init_db.py - Initialize Floci DynamoDB tables & S3 bucket for Harness.
"""
import os
import sys

BASE_DIR = os.path.abspath(os.path.dirname(__file__) + "/..")
sys.path.insert(0, BASE_DIR)

from tools.floci_client import FlociHarnessDB

def init_db():
    print("--> Initializing Floci DynamoDB & S3 infrastructure...")
    db = FlociHarnessDB()
    res = db.init_schema()
    print(f"--> Endpoint: {res['endpoint']}")
    print(f"--> Tables: {res.get('existing_tables', []) + res.get('created_tables', [])}")
    print(f"--> S3 Bucket: {res.get('s3_bucket')}")
    print("--> Floci storage ready for Harness!")

if __name__ == "__main__":
    init_db()
