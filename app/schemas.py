from datetime import datetime
from typing import Optional

from pydantic import BaseModel


class HealthResponse(BaseModel):
    status: str


class LeadOut(BaseModel):
    id: int
    company_name: Optional[str]
    website: Optional[str]
    country: Optional[str]
    city: Optional[str]
    address: Optional[str]
    phone: Optional[str]
    public_email: Optional[str]
    contact_page: Optional[str]
    careers_page: Optional[str]
    lead_type: Optional[str]
    confidence_score: Optional[float]
    source_url: Optional[str]
    notes: Optional[str]
    reasoning: Optional[str]
    detected_signals: Optional[str]
    created_at: Optional[str]


class RunAgentResponse(BaseModel):
    status: str
    candidates_seen: int
    leads_saved: int
    high_confidence_count: int
    summary: str


class DailyReportOut(BaseModel):
    id: int
    report_date: str
    total_candidates: int
    total_saved: int
    high_confidence_count: int
    summary_text: str
    created_at: Optional[str]


class AgentStatus(BaseModel):
    last_run_time: Optional[datetime]
    next_scheduled_run_time: Optional[datetime]
    leads_found_today: int
    leads_saved_today: int
    last_run_result: Optional[str]
