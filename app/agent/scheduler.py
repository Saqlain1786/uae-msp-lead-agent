from datetime import datetime, timezone

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.cron import CronTrigger

from app.agent.engine import LeadAgentEngine
from app.config import settings

scheduler = BackgroundScheduler(timezone="UTC")
engine = LeadAgentEngine()
_last_result: str | None = None


def _run_job() -> None:
    global _last_result
    result = engine.run_cycle()
    _last_result = result.summary


def start_scheduler() -> None:
    if not settings.scheduler_enabled:
        return
    if scheduler.running:
        return
    scheduler.add_job(
        _run_job,
        trigger=CronTrigger(hour=settings.scheduler_hour_utc, minute=settings.scheduler_minute_utc),
        id="daily_lead_discovery",
        replace_existing=True,
        max_instances=1,
        coalesce=True,
    )
    scheduler.start()


def stop_scheduler() -> None:
    if scheduler.running:
        scheduler.shutdown(wait=False)


def get_next_run_time() -> datetime | None:
    job = scheduler.get_job("daily_lead_discovery")
    if not job:
        return None
    next_time = job.next_run_time
    if next_time is None:
        return None
    return next_time.astimezone(timezone.utc)


def get_last_result() -> str | None:
    return _last_result
