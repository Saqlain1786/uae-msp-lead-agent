import json
from datetime import datetime, timezone

from app.database import get_connection


def create_lead(payload: dict) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO leads (
                company_name, website, country, city, address, phone, public_email,
                contact_page, careers_page, lead_type, confidence_score, source_url,
                notes, reasoning, detected_signals, created_at
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                payload.get("company_name"),
                payload.get("website"),
                payload.get("country", "UAE"),
                payload.get("city"),
                payload.get("address"),
                payload.get("phone"),
                payload.get("public_email"),
                payload.get("contact_page"),
                payload.get("careers_page"),
                payload.get("lead_type"),
                payload.get("confidence_score"),
                payload.get("source_url"),
                payload.get("notes"),
                payload.get("reasoning"),
                json.dumps(payload.get("detected_signals", [])),
                datetime.now(timezone.utc).isoformat(),
            ),
        )
        return cur.lastrowid


def list_leads() -> list[dict]:
    with get_connection() as conn:
        rows = conn.execute("SELECT * FROM leads ORDER BY id DESC").fetchall()
    return [dict(r) for r in rows]


def get_lead(lead_id: int) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM leads WHERE id = ?", (lead_id,)).fetchone()
    return dict(row) if row else None


def get_lead_by_website(website: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM leads WHERE website = ?", (website,)).fetchone()
    return dict(row) if row else None


def get_lead_by_company_name(company_name: str) -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM leads WHERE lower(company_name) = lower(?)", (company_name,)).fetchone()
    return dict(row) if row else None


def delete_lead(lead_id: int) -> bool:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM leads WHERE id = ?", (lead_id,))
        return cur.rowcount > 0


def create_run_log(payload: dict) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO run_logs (started_at, finished_at, status, candidates_seen, leads_saved, summary)
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                payload["started_at"],
                payload["finished_at"],
                payload["status"],
                payload["candidates_seen"],
                payload["leads_saved"],
                payload["summary"],
            ),
        )
        return cur.lastrowid


def latest_run_log() -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM run_logs ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else None


def count_leads_on_date(date_str: str) -> int:
    with get_connection() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c FROM leads WHERE substr(created_at,1,10)=?", (date_str,)
        ).fetchone()
    return int(row["c"])
