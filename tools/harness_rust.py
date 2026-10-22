#!/usr/bin/env python3
"""
tools/harness_rust.py - Python Typed Bridge to Harness Native Rust CLI & Kev System One Engine (v0.1.14).

Cung cấp interface chuẩn mực cho các Agent và script Python gọi binary Rust native:
1. supervise_task(text: str) -> SupervisionEvaluationResult: Phân luồng rủi ro Lambda qua Kev System One (<50ms).
2. record_lesson(...): Ghi nhận bài học kinh nghiệm đồng thời vào SQLite và Floci DynamoDB.
3. query_lessons(...): Truy vấn bài học kinh nghiệm theo domain (phục vụ Zero-Search injection).
4. sync_experiences(): Đồng bộ 2 chiều dữ liệu kinh nghiệm giữa SQLite local và Floci DynamoDB cloud.

100% Strict Typing: Zero any, Zero dict[Any, Any], hoàn toàn sử dụng Typed Dataclasses.
"""

from __future__ import annotations

import json
import os
import subprocess
import sys
import time
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List, Optional

PROJECT_ROOT = Path(__file__).resolve().parent.parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
if str(PROJECT_ROOT / "tools") not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT / "tools"))

NATIVE_BIN = PROJECT_ROOT / "scripts" / "bin" / "harness-cli"


@dataclass
class SupervisionEvaluationResult:
    """Kết quả phân luồng rủi ro traffic-light từ Kev System One qua Rust CLI."""
    decision: str  # green | yellow | red
    risk_lane: str  # tiny | normal | high-risk
    confidence: float
    requires_human_review: bool
    suggested_route: str  # automated_pipeline | peer_review_queue | human_supervisor
    explanation: str
    latency_ms: int
    status: str = "success"
    urgency_score: Optional[float] = None
    error: Optional[str] = None


@dataclass
class ExperienceRecordDto:
    """Bản ghi bài học kinh nghiệm với schema chuẩn hóa."""
    id: str
    domain: str
    cue: str
    lesson: str
    evidence: str
    confidence: str = "medium"
    work_item_id: Optional[str] = None
    pattern_hash: Optional[str] = None
    created_at: Optional[str] = None
    harness_patch: Optional[str] = None
    successful_harness: Optional[str] = None
    failure_trajectories: Optional[str] = None


@dataclass
class ExperienceSyncResult:
    """Kết quả đồng bộ 2 chiều SQLite local và Floci DynamoDB."""
    domain: str
    cue: str
    lesson: str
    evidence: str
    confidence: str
    sqlite_synced: bool
    dynamodb_synced: bool
    experience_id: Optional[str] = None
    sqlite_error: Optional[str] = None
    dynamodb_error: Optional[str] = None


@dataclass
class TwoWaySyncSummary:
    """Tổng kết đồng bộ 2 chiều SQLite và DynamoDB."""
    sqlite_to_dynamo_count: int = 0
    dynamo_to_sqlite_count: int = 0
    total_synced: int = 0
    errors: List[str] = field(default_factory=list)


def is_binary_available() -> bool:
    return NATIVE_BIN.is_file() and os.access(str(NATIVE_BIN), os.X_OK)


class HarnessRustBridge:
    """Typed Bridge kết nối hệ thống Python với Native Rust CLI harness-cli."""

    def __init__(self, bin_path: Optional[Path] = None, project_root: Optional[Path] = None) -> None:
        self.project_root = project_root or PROJECT_ROOT
        self.bin_path = bin_path or (self.project_root / "scripts" / "bin" / "harness-cli")

    def is_available(self) -> bool:
        return self.is_binary_available()

    def is_binary_available(self) -> bool:
        return self.bin_path.is_file() and os.access(str(self.bin_path), os.X_OK)

    def supervise_task(self, text: str, timeout: float = 10.0) -> SupervisionEvaluationResult:
        """
        Gọi binary Rust phân luồng rủi ro tác vụ qua Kev System One.
        Đảm bảo phản hồi traffic-light với graceful fallback an toàn.
        """
        t0 = time.time()
        if not self.is_binary_available():
            latency_ms = int((time.time() - t0) * 1000)
            return self._heuristic_fallback(
                text=text,
                reason=f"Native binary {self.bin_path} not found",
                latency_ms=latency_ms
            )

        try:
            res = subprocess.run(
                [str(self.bin_path), "supervise", "evaluate", "--text", text, "--json"],
                cwd=str(self.project_root),
                capture_output=True,
                text=True,
                timeout=timeout
            )
            latency_ms = int((time.time() - t0) * 1000)
            output = res.stdout.strip()

            if res.returncode == 0 and output:
                try:
                    raw = json.loads(output)
                    return SupervisionEvaluationResult(
                        decision=str(raw.get("decision", "yellow")),
                        risk_lane=str(raw.get("risk_lane", "normal")),
                        confidence=float(raw.get("confidence", 0.5)),
                        requires_human_review=bool(raw.get("requires_human_review", False)),
                        suggested_route=str(raw.get("suggested_route", "peer_review_queue")),
                        explanation=str(raw.get("explanation", "")),
                        latency_ms=latency_ms,
                        status="success",
                        urgency_score=float(raw["urgency_score"]) if raw.get("urgency_score") is not None else None,
                        error=None
                    )
                except Exception as json_err:
                    return self._heuristic_fallback(
                        text=text,
                        reason=f"Failed to parse binary output JSON: {json_err}",
                        latency_ms=latency_ms
                    )
            else:
                err_msg = res.stderr.strip() or f"Binary exited with code {res.returncode}"
                return self._heuristic_fallback(
                    text=text,
                    reason=err_msg,
                    latency_ms=latency_ms
                )
        except Exception as e:
            latency_ms = int((time.time() - t0) * 1000)
            return self._heuristic_fallback(
                text=text,
                reason=f"Subprocess execution error: {e}",
                latency_ms=latency_ms
            )

    def _heuristic_fallback(self, text: str, reason: str, latency_ms: int) -> SupervisionEvaluationResult:
        """Graceful Fallback: Phân tích heuristic an toàn khi Kev System One không phản hồi."""
        lower = text.lower()
        if any(w in lower for w in ["drop", "delete", "rm -rf", "secret", "private key", "prod", "production"]):
            decision = "red"
            risk_lane = "high-risk"
            route = "human_supervisor"
            req_human = True
            conf = 0.90
        elif any(w in lower for w in ["doc", "typo", "readme", "comment", "format"]):
            decision = "green"
            risk_lane = "tiny"
            route = "automated_pipeline"
            req_human = False
            conf = 0.85
        else:
            decision = "yellow"
            risk_lane = "normal"
            route = "peer_review_queue"
            req_human = False
            conf = 0.50

        return SupervisionEvaluationResult(
            decision=decision,
            risk_lane=risk_lane,
            confidence=conf,
            requires_human_review=req_human,
            suggested_route=route,
            explanation=f"[Graceful Fallback] {reason}",
            latency_ms=latency_ms,
            status="fallback",
            urgency_score=None,
            error=reason
        )

    def record_lesson(
        self,
        domain: str,
        cue: str,
        lesson: str,
        evidence: str,
        confidence: str = "high",
        work_item_id: Optional[str | int] = None,
        pattern_hash: Optional[str] = None
    ) -> ExperienceSyncResult:
        """
        Ghi nhận bài học kinh nghiệm đồng thời vào SQLite và Floci DynamoDB cloud.
        """
        result = ExperienceSyncResult(
            domain=domain,
            cue=cue,
            lesson=lesson,
            evidence=evidence,
            confidence=confidence,
            sqlite_synced=False,
            dynamodb_synced=False
        )

        # 1. Ghi vào SQLite qua Rust Binary
        if self.is_binary_available():
            try:
                cmd = [
                    str(self.bin_path), "learn", "record",
                    "--domain", domain,
                    "--cue", cue,
                    "--lesson", lesson,
                    "--evidence", evidence,
                    "--confidence", confidence
                ]
                if work_item_id is not None:
                    cmd.extend(["--work-item-id", str(work_item_id)])
                if pattern_hash is not None:
                    cmd.extend(["--pattern-hash", str(pattern_hash)])

                res = subprocess.run(
                    cmd,
                    cwd=str(self.project_root),
                    capture_output=True,
                    text=True,
                    timeout=10
                )
                result.sqlite_synced = (res.returncode == 0)
                if res.returncode != 0:
                    result.sqlite_error = res.stderr.strip()
            except Exception as e:
                result.sqlite_error = str(e)

        # 2. Đồng bộ lên Floci DynamoDB
        try:
            from tools.floci_client import FlociHarnessDB  # type: ignore
            db = FlociHarnessDB()
            ddb_res = db.record_experience(
                domain=domain,
                cue=cue,
                lesson=lesson,
                evidence=evidence,
                confidence=confidence,
                work_item_id=work_item_id
            )
            result.dynamodb_synced = True
            result.experience_id = ddb_res.get("id")
        except Exception as e:
            result.dynamodb_error = str(e)

        return result

    def query_lessons(
        self,
        domain: Optional[str] = None,
        work_item_id: Optional[str | int] = None,
        limit: int = 10
    ) -> List[ExperienceRecordDto]:
        """Truy vấn danh sách bài học kinh nghiệm theo domain hoặc work_item_id (O(1) GSI)."""
        # Ưu tiên truy vấn Floci DynamoDB qua GSI
        try:
            from tools.floci_client import FlociHarnessDB  # type: ignore
            db = FlociHarnessDB()
            items = db.query_experiences(domain=domain, work_item_id=work_item_id, limit=limit)
            if items:
                records: List[ExperienceRecordDto] = []
                for it in items:
                    records.append(
                        ExperienceRecordDto(
                            id=str(it.get("id", "")),
                            domain=str(it.get("domain", "")),
                            cue=str(it.get("cue", "")),
                            lesson=str(it.get("lesson", "")),
                            evidence=str(it.get("evidence", "")),
                            confidence=str(it.get("confidence", "medium")),
                            work_item_id=str(it.get("work_item_id")) if it.get("work_item_id") is not None else None,
                            pattern_hash=str(it.get("pattern_hash")) if it.get("pattern_hash") is not None else None,
                            created_at=str(it.get("created_at")) if it.get("created_at") is not None else None,
                            harness_patch=it.get("harness_patch"),
                            successful_harness=it.get("successful_harness"),
                            failure_trajectories=it.get("failure_trajectories")
                        )
                    )
                return records
        except Exception:
            pass

        # Fallback sang SQLite
        try:
            from tools.harness_learning_search import search_experiences  # type: ignore
            raw_exps = search_experiences(domain=domain, limit=limit)
            return [
                ExperienceRecordDto(
                    id=str(r.get("id", "")),
                    domain=str(r.get("domain", "")),
                    cue=str(r.get("cue", "")),
                    lesson=str(r.get("lesson", "")),
                    evidence=str(r.get("evidence", "")),
                    confidence=str(r.get("confidence", "medium")),
                    work_item_id=str(r.get("work_item_id")) if r.get("work_item_id") is not None else None,
                    pattern_hash=str(r.get("pattern_hash")) if r.get("pattern_hash") is not None else None,
                    created_at=str(r.get("created_at")) if r.get("created_at") is not None else None,
                    harness_patch=r.get("harness_patch"),
                    successful_harness=r.get("successful_harness"),
                    failure_trajectories=r.get("failure_trajectories")
                )
                for r in raw_exps
            ]
        except Exception:
            return []

    def sync_experiences(self) -> TwoWaySyncSummary:
        """Đồng bộ 2 chiều dữ liệu kinh nghiệm giữa SQLite local và Floci DynamoDB cloud."""
        summary = TwoWaySyncSummary()
        try:
            from tools.floci_client import FlociHarnessDB  # type: ignore
            from tools.harness_learning_search import get_sqlite_conn  # type: ignore

            db = FlociHarnessDB()
            conn = get_sqlite_conn()
            if not conn:
                summary.errors.append("SQLite connection not available")
                return summary

            # 1. Đọc từ SQLite
            cur = conn.cursor()
            cur.execute("SELECT * FROM harness_experience;")
            sqlite_rows = [dict(r) for r in cur.fetchall()]

            # 2. Đọc từ DynamoDB
            ddb_items = db.query_experiences(limit=500)
            ddb_cues = {f"{it.get('domain')}:{it.get('cue')}" for it in ddb_items}

            # Đồng bộ SQLite -> DynamoDB
            for row in sqlite_rows:
                key = f"{row.get('domain')}:{row.get('cue')}"
                if key not in ddb_cues:
                    db.put_experience({
                        "id": str(row.get("id")),
                        "domain": str(row.get("domain")),
                        "work_item_id": str(row.get("work_item_id")) if row.get("work_item_id") is not None else None,
                        "cue": str(row.get("cue")),
                        "lesson": str(row.get("lesson")),
                        "evidence": str(row.get("evidence")),
                        "confidence": str(row.get("confidence", "medium")),
                        "pattern_hash": str(row.get("pattern_hash")) if row.get("pattern_hash") else None,
                        "created_at": str(row.get("created_at"))
                    })
                    summary.sqlite_to_dynamo_count += 1

            # Đồng bộ DynamoDB -> SQLite
            sqlite_cues = {f"{r.get('domain')}:{r.get('cue')}" for r in sqlite_rows}
            for it in ddb_items:
                key = f"{it.get('domain')}:{it.get('cue')}"
                if key not in sqlite_cues:
                    try:
                        cur.execute(
                            """
                            INSERT INTO harness_experience (domain, work_item_id, cue, lesson, evidence, confidence, pattern_hash, created_at)
                            VALUES (?, ?, ?, ?, ?, ?, ?, ?);
                            """,
                            (
                                str(it.get("domain", "")),
                                int(it["work_item_id"]) if it.get("work_item_id") and str(it["work_item_id"]).isdigit() else None,
                                str(it.get("cue", "")),
                                str(it.get("lesson", "")),
                                str(it.get("evidence", "")),
                                str(it.get("confidence", "medium")),
                                str(it.get("pattern_hash", "")),
                                str(it.get("created_at", ""))
                            )
                        )
                        conn.commit()
                        summary.dynamo_to_sqlite_count += 1
                    except Exception as ins_err:
                        summary.errors.append(f"Insert Dynamo item to SQLite error: {ins_err}")

            conn.close()
            summary.total_synced = summary.sqlite_to_dynamo_count + summary.dynamo_to_sqlite_count
        except Exception as e:
            summary.errors.append(str(e))

        return summary


# Module level convenience functions matching backwards compatibility
_default_bridge = HarnessRustBridge()

def supervise_task(text: str, timeout: float = 12.0) -> SupervisionEvaluationResult:
    return _default_bridge.supervise_task(text=text, timeout=timeout)

def record_lesson(
    domain: str,
    cue: str,
    lesson: str,
    evidence: str,
    confidence: str = "high",
    work_item_id: Optional[str | int] = None
) -> ExperienceSyncResult:
    return _default_bridge.record_lesson(
        domain=domain,
        cue=cue,
        lesson=lesson,
        evidence=evidence,
        confidence=confidence,
        work_item_id=work_item_id
    )

def query_lessons(domain: Optional[str] = None, limit: int = 10) -> List[ExperienceRecordDto]:
    return _default_bridge.query_lessons(domain=domain, limit=limit)


if __name__ == "__main__":
    print("Testing tools/harness_rust.py...")
    bridge = HarnessRustBridge()
    print(f"Binary available: {bridge.is_binary_available()}")
    if bridge.is_binary_available():
        res = bridge.supervise_task("Check git status and compile release")
        print("Supervise result:", asdict(res))
        rec = bridge.record_lesson(
            domain="system_test",
            cue="rust_bridge_validation",
            lesson="Always test bridge communication with live native binary",
            evidence="supervise_task returned 0 error",
            confidence="high"
        )
        print("Record lesson result:", asdict(rec))
        queried = bridge.query_lessons(domain="system_test")
        print("Queried lessons:", len(queried))
