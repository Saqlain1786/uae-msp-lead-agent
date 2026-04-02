from datetime import datetime, timezone

from fastapi import APIRouter, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

from app.agent.engine import LeadAgentEngine
from app.agent.scheduler import get_next_run_time
from app.config import settings
from app.services.reporting import latest_daily_report
from app.services.storage import count_leads_on_date, list_leads, list_run_logs, latest_run_log

templates = Jinja2Templates(directory="app/templates")
router = APIRouter()
engine = LeadAgentEngine()


@router.get("/")
def dashboard(request: Request, message: str | None = None):
    run = latest_run_log()
    report = latest_daily_report()
    today = datetime.now(timezone.utc).date().isoformat()
    context = {
        "request": request,
        "title": settings.app_name,
        "scheduler_enabled": settings.scheduler_enabled,
        "last_run_time": run["finished_at"] if run else None,
        "next_run_time": get_next_run_time(),
        "leads_found_today": count_leads_on_date(today),
        "leads_saved_today": run["leads_saved"] if run and run["started_at"].startswith(today) else 0,
        "report": report,
        "message": message,
    }
    return templates.TemplateResponse("dashboard.html", context)


@router.post("/run-agent-ui")
def run_agent_ui():
    try:
        result = engine.run_cycle()
        msg = f"Agent run succeeded: saved {result.leads_saved} leads."
    except Exception as exc:  # keep UI route resilient
        msg = f"Agent run failed: {exc}"
    return RedirectResponse(url=f"/?message={msg}", status_code=303)


@router.get("/runs")
def runs_page(request: Request):
    return templates.TemplateResponse(
        "runs.html",
        {
            "request": request,
            "title": settings.app_name,
            "runs": list_run_logs(limit=100),
        },
    )


@router.get("/leads-ui")
def leads_page(request: Request):
    return templates.TemplateResponse(
        "leads.html",
        {
            "request": request,
            "title": settings.app_name,
            "leads": list_leads(),
        },
    )
