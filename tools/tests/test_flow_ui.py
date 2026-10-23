#!/usr/bin/env python3
"""
tools/tests/test_flow_ui.py - Unit test suite for SLPPC Visual Flow UI State Bridge (flow_server.py).
"""

import io
import json
import sys
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

BASE_DIR = Path(__file__).resolve().parent.parent.parent
sys.path.insert(0, str(BASE_DIR))

from tools.web import flow_server


class DummyClient:
    def __init__(self, data: bytes):
        self.rfile = io.BytesIO(data)
        self.wfile = io.BytesIO()

    def makefile(self, *args, **kwargs):
        if "r" in args[0]:
            return self.rfile
        return self.wfile

    def sendall(self, data):
        self.wfile.write(data)


class TestFlowServer(unittest.TestCase):
    def test_01_build_pipeline_status_schema(self):
        """PipelineStatusDto must strictly contain 5 nodes and valid metrics."""
        dto = flow_server.build_pipeline_status()
        self.assertIn("timestamp", dto)
        self.assertIn("active_work_item", dto)
        self.assertIn("concurrency", dto)
        self.assertIn("nodes", dto)

        # Nodes validation
        nodes = dto["nodes"]
        self.assertEqual(len(nodes), 5)
        for expected_role in ("supervisor", "pm", "lead", "peer", "qc"):
            self.assertIn(expected_role, nodes)
            self.assertIn("role", nodes[expected_role])
            self.assertIn("status", nodes[expected_role])

        # Concurrency
        self.assertEqual(dto["concurrency"]["ceiling"], 5)
        self.assertGreaterEqual(dto["concurrency"]["active_workers"], 1)

        # tdsTestId contract
        self.assertEqual(dto.get("tds_test_id"), "flow-dashboard-server-status-active")

    def test_02_handler_status_endpoint(self):
        """GET /api/pipeline/status returns 200 OK with application/json."""
        req_data = b"GET /api/pipeline/status HTTP/1.1\r\nHost: localhost\r\n\r\n"
        client = DummyClient(req_data)

        handler = flow_server.FlowStatusHandler(client, ("127.0.0.1", 9999), None)
        response_bytes = client.wfile.getvalue()

        self.assertIn(b"200 OK", response_bytes)
        self.assertIn(b"Content-Type: application/json", response_bytes)
        self.assertIn(b"Access-Control-Allow-Origin: *", response_bytes)

        # Extract JSON body
        header_end = response_bytes.find(b"\r\n\r\n")
        body_json = json.loads(response_bytes[header_end + 4:].decode("utf-8"))
        self.assertIn("nodes", body_json)
        self.assertIn("supervisor", body_json["nodes"])

    def test_03_handler_flow_spa_endpoint(self):
        """GET /flow returns 200 OK with text/html and tdsTestId."""
        req_data = b"GET /flow HTTP/1.1\r\nHost: localhost\r\n\r\n"
        client = DummyClient(req_data)

        handler = flow_server.FlowStatusHandler(client, ("127.0.0.1", 9999), None)
        response_bytes = client.wfile.getvalue()

        self.assertIn(b"200 OK", response_bytes)
        self.assertIn(b"Content-Type: text/html", response_bytes)
        self.assertIn(b"flow-dashboard-server-status-active", response_bytes)


if __name__ == "__main__":
    unittest.main()
