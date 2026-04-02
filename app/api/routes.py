from datetime import datetime, timezone

from fastapi import APIRouter, HTTPException

from app.agent.engine import LeadAgentEngine
from app.agent.scheduler import get_last_result, get_next_run_time
from app.schemas import AgentStatus, DailyReportOut, HealthResponse, LeadOut, RunAgentResponse
from app.services.reporting import latest_daily_report
from app.services.storage import count_leads_on_date, delete_lead, get_lead, latest_run_log, list_leads

router = APIRouter()
engine = LeadAgentEngine()


@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    return HealthResponse(status="ok")


@router.get("/leads", response_model=list[LeadOut])
def leads() -> list[LeadOut]:
    return [LeadOut(**row) for row in list_leads()]


@router.get("/leads/{lead_id}", response_model=LeadOut)
def lead(lead_id: int) -> LeadOut:
    row = get_lead(lead_id)
    if not row:
        raise HTTPException(status_code=404, detail="Lead not found")
    return LeadOut(**row)


@router.delete("/leads/{lead_id}")
def remove_lead(lead_id: int) -> dict:
    if not delete_lead(lead_id):
        raise HTTPException(status_code=404, detail="Lead not found")
    return {"deleted": True}


@router.post("/run-agent", response_model=RunAgentResponse)
def run_agent() -> RunAgentResponse:
    result = engine.run_cycle()
    return RunAgentResponse(
        status=result.status,
        candidates_seen=result.candidates_seen,
        leads_saved=result.leads_saved,
        high_confidence_count=result.high_confidence_count,
        summary=result.summary,
    )


@router.get("/reports/daily", response_model=DailyReportOut)
def get_daily_report() -> DailyReportOut:
    report = latest_daily_report()
    if not report:
        raise HTTPException(status_code=404, detail="No daily report available")
    return DailyReportOut(**report)


@router.get("/agent/status", response_model=AgentStatus)
def agent_status() -> AgentStatus:
    run = latest_run_log()
    now_date = datetime.now(timezone.utc).date().isoformat()
    return AgentStatus(
        last_run_time=datetime.fromisoformat(run["finished_at"]) if run else None,
        next_scheduled_run_time=get_next_run_time(),
        leads_found_today=count_leads_on_date(now_date),
        leads_saved_today=run["leads_saved"] if run and run["started_at"].startswith(now_date) else 0,
        last_run_result=get_last_result() or (run["summary"] if run else None),
    )
