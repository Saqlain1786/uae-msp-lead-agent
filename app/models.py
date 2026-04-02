from dataclasses import dataclass
from datetime import datetime


@dataclass
class Candidate:
    company_name: str
    website: str
    source_url: str
    page_text: str
    html: str = ""


@dataclass
class ReasoningResult:
    classification: str
    confidence_score: float
    save_decision: bool
    explanation: str
    detected_signals: list[str]


@dataclass
class AgentRunResult:
    started_at: datetime
    finished_at: datetime
    candidates_seen: int
    leads_saved: int
    high_confidence_count: int
    status: str
    summary: str
