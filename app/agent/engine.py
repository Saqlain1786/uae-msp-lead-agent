from datetime import datetime, timezone

from app.agent.reasoner import RuleBasedReasoner
from app.config import settings
from app.models import AgentRunResult
from app.services.dedup import is_duplicate
from app.services.discovery import get_discovery_provider
from app.services.parser import extract_signals
from app.services.reporting import create_daily_report
from app.services.storage import create_lead, create_run_log


class LeadAgentEngine:
    def __init__(self) -> None:
        self.reasoner = RuleBasedReasoner()

    def run_cycle(self) -> AgentRunResult:
        started_at = datetime.now(timezone.utc)
        provider = get_discovery_provider(settings.discovery_mode)
        candidates = provider.discover()

        leads_saved = 0
        high_conf = 0

        for candidate in candidates:
            evidence = extract_signals(candidate.html, candidate.website, candidate.page_text)
            reasoning = self.reasoner.evaluate(evidence)

            if reasoning.confidence_score >= 0.8:
                high_conf += 1

            if not reasoning.save_decision:
                continue
            if is_duplicate(candidate.website, candidate.company_name):
                continue

            lead_payload = {
                "company_name": candidate.company_name,
                "website": candidate.website,
                "country": "UAE" if evidence.get("uae_cities") else None,
                "city": evidence.get("uae_cities", [None])[0],
                "phone": evidence.get("phones", [None])[0],
                "public_email": evidence.get("emails", [None])[0],
                "contact_page": evidence.get("contact_page"),
                "careers_page": evidence.get("careers_page"),
                "lead_type": reasoning.classification,
                "confidence_score": reasoning.confidence_score,
                "source_url": candidate.source_url,
                "reasoning": reasoning.explanation,
                "detected_signals": reasoning.detected_signals,
                "notes": "Autonomously discovered from public web content.",
            }
            create_lead(lead_payload)
            leads_saved += 1

        finished_at = datetime.now(timezone.utc)
        summary = f"Processed {len(candidates)} candidates and saved {leads_saved} leads."

        create_run_log(
            {
                "started_at": started_at.isoformat(),
                "finished_at": finished_at.isoformat(),
                "status": "success",
                "candidates_seen": len(candidates),
                "leads_saved": leads_saved,
                "summary": summary,
            }
        )

        create_daily_report(
            {
                "report_date": started_at.date().isoformat(),
                "total_candidates": len(candidates),
                "total_saved": leads_saved,
                "high_confidence_count": high_conf,
                "summary_text": summary,
            }
        )

        return AgentRunResult(
            started_at=started_at,
            finished_at=finished_at,
            candidates_seen=len(candidates),
            leads_saved=leads_saved,
            high_confidence_count=high_conf,
            status="success",
            summary=summary,
        )
