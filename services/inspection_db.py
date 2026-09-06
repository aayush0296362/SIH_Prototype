"""Persistent SQLite storage for LMSCAN inspector reviews."""
from __future__ import annotations

import json
import sqlite3
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
DB_PATH = DATA_DIR / "lmscan.db"


def _connect() -> sqlite3.Connection:
    DATA_DIR.mkdir(parents=True, exist_ok=True)
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    with _connect() as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS inspections (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                inspection_id TEXT UNIQUE NOT NULL,
                created_at TEXT NOT NULL,
                decision TEXT NOT NULL,
                notes TEXT,
                product_name TEXT,
                manufacturer TEXT,
                manufacturer_address TEXT,
                batch_number TEXT,
                mrp TEXT,
                net_quantity TEXT,
                fssai_license_number TEXT,
                manufacturing_date TEXT,
                expiry_date TEXT,
                compliance_percent REAL,
                applicable_rules INTEGER DEFAULT 0,
                detected_rules INTEGER DEFAULT 0,
                missing_rules INTEGER DEFAULT 0,
                unclear_rules INTEGER DEFAULT 0,
                evidence_images INTEGER DEFAULT 0,
                review_status_json TEXT,
                record_json TEXT NOT NULL
            )
        """)
        conn.commit()


def _next_inspection_id(conn: sqlite3.Connection) -> str:
    """Return a monotonic inspection ID that is not reused after deletion."""
    row = conn.execute(
        "SELECT COALESCE((SELECT seq FROM sqlite_sequence WHERE name = 'inspections'), 0) + 1 AS next_id"
    ).fetchone()
    return f"INS-{int(row['next_id']):05d}"


def save_inspection(record: Dict[str, Any]) -> str:
    init_db()
    created_at = datetime.now(timezone.utc).astimezone().isoformat(timespec="seconds")
    summary = record.get("summary", {}) or {}
    review_status = record.get("review_status", {}) or {}
    inspection = record.get("inspection", {}) or {}
    with _connect() as conn:
        inspection_id = _next_inspection_id(conn)
        conn.execute(
            """INSERT INTO inspections (
                inspection_id, created_at, decision, notes, product_name, manufacturer,
                manufacturer_address, batch_number, mrp, net_quantity, fssai_license_number,
                manufacturing_date, expiry_date, compliance_percent, applicable_rules,
                detected_rules, missing_rules, unclear_rules, evidence_images,
                review_status_json, record_json
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                inspection_id, created_at, record.get("decision", "Requires Review"),
                record.get("notes", ""), summary.get("product_name"), summary.get("manufacturer"),
                summary.get("manufacturer_address"), summary.get("batch_number"), summary.get("mrp"),
                summary.get("net_quantity"), summary.get("fssai_license_number"),
                summary.get("manufacturing_date"), summary.get("expiry_date"),
                summary.get("compliance_percent"), summary.get("applicable_rules", 0),
                summary.get("detected_rules", 0), summary.get("missing_rules", 0),
                summary.get("unclear_rules", 0), summary.get("evidence_images", inspection.get("images_processed", 0)),
                json.dumps(review_status, ensure_ascii=False),
                json.dumps(record, ensure_ascii=False, default=str),
            ),
        )
        conn.commit()
    return inspection_id


def _row_to_record(row: sqlite3.Row) -> Dict[str, Any]:
    raw = json.loads(row["record_json"])
    raw["inspection_id"] = row["inspection_id"]
    raw["created_at"] = row["created_at"]
    raw["decision"] = row["decision"]
    raw["notes"] = row["notes"] or ""
    raw["summary"] = raw.get("summary", {}) or {}
    raw["summary"].setdefault("product_name", row["product_name"])
    raw["summary"].setdefault("manufacturer", row["manufacturer"])
    raw["summary"].setdefault("compliance_percent", row["compliance_percent"])
    raw["review_status"] = json.loads(row["review_status_json"] or "{}")
    return raw


def get_inspections(limit: Optional[int] = 200) -> List[Dict[str, Any]]:
    init_db()
    query = "SELECT * FROM inspections ORDER BY id DESC"
    params = ()
    if limit is not None:
        query += " LIMIT ?"
        params = (max(1, int(limit)),)
    with _connect() as conn:
        rows = conn.execute(query, params).fetchall()
    return [_row_to_record(row) for row in rows]


def get_inspection(inspection_id: str) -> Optional[Dict[str, Any]]:
    if not inspection_id:
        return None
    init_db()
    with _connect() as conn:
        row = conn.execute("SELECT * FROM inspections WHERE inspection_id = ?", (inspection_id,)).fetchone()
    return _row_to_record(row) if row else None


def delete_inspection(inspection_id: str) -> bool:
    """Permanently delete one saved inspection record by its public inspection ID."""
    if not inspection_id:
        return False
    init_db()
    with _connect() as conn:
        cursor = conn.execute(
            "DELETE FROM inspections WHERE inspection_id = ?",
            (inspection_id,),
        )
        conn.commit()
        return cursor.rowcount > 0
