from app.database import get_connection


def create_daily_report(payload: dict) -> int:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT INTO daily_reports (report_date, total_candidates, total_saved, high_confidence_count, summary_text)
            VALUES (?, ?, ?, ?, ?)
            """,
            (
                payload["report_date"],
                payload["total_candidates"],
                payload["total_saved"],
                payload["high_confidence_count"],
                payload["summary_text"],
            ),
        )
        return cur.lastrowid


def latest_daily_report() -> dict | None:
    with get_connection() as conn:
        row = conn.execute("SELECT * FROM daily_reports ORDER BY id DESC LIMIT 1").fetchone()
    return dict(row) if row else None
