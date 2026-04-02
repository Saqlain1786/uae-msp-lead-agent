import sqlite3
from contextlib import contextmanager
from pathlib import Path

from app.config import settings


Path(settings.database_path).parent.mkdir(parents=True, exist_ok=True)


@contextmanager
def get_connection():
    conn = sqlite3.connect(settings.database_path)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()


def init_db() -> None:
    with get_connection() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS leads (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                company_name TEXT,
                website TEXT,
                country TEXT,
                city TEXT,
                address TEXT,
                phone TEXT,
                public_email TEXT,
                contact_page TEXT,
                careers_page TEXT,
                lead_type TEXT,
                confidence_score REAL,
                source_url TEXT,
                notes TEXT,
                reasoning TEXT,
                detected_signals TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
        cur.execute("CREATE UNIQUE INDEX IF NOT EXISTS idx_leads_website ON leads(website)")
        cur.execute("CREATE INDEX IF NOT EXISTS idx_leads_company ON leads(company_name)")
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS run_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                started_at TEXT,
                finished_at TEXT,
                status TEXT,
                candidates_seen INTEGER,
                leads_saved INTEGER,
                summary TEXT
            )
            """
        )
        cur.execute(
            """
            CREATE TABLE IF NOT EXISTS daily_reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                report_date TEXT,
                total_candidates INTEGER,
                total_saved INTEGER,
                high_confidence_count INTEGER,
                summary_text TEXT,
                created_at TEXT DEFAULT CURRENT_TIMESTAMP
            )
            """
        )
