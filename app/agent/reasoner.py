from app.config import settings
from app.models import ReasoningResult


class RuleBasedReasoner:
    def evaluate(self, evidence: dict | None) -> ReasoningResult:
        if not isinstance(evidence, dict):
            return ReasoningResult(
                classification="Unknown",
                confidence_score=0.0,
                save_decision=False,
                explanation="insufficient data",
                detected_signals=[],
            )

        text = (evidence.get("text") or "").strip().lower()
        emails = evidence.get("emails") if isinstance(evidence.get("emails"), list) else []
        phones = evidence.get("phones") if isinstance(evidence.get("phones"), list) else []
        cities = evidence.get("uae_cities") if isinstance(evidence.get("uae_cities"), list) else []

        if not text and not emails and not phones:
            return ReasoningResult(
                classification="Unknown",
                confidence_score=0.0,
                save_decision=False,
                explanation="insufficient data",
                detected_signals=[],
            )

        signals: list[str] = []
        score = 0.0

        if any(k in text for k in ["managed it", "msp", "managed services"]):
            signals.append("company offers managed IT services")
            score += 0.25
        if any(k in text for k in ["it support", "helpdesk"]):
            signals.append("company offers IT support/helpdesk")
            score += 0.2
        if evidence.get("careers_page") or any(k in text for k in ["hiring", "vacanc", "jobs"]):
            signals.append("careers page exists")
            score += 0.1
        if cities:
            signals.append("UAE city detected")
            score += 0.15
        if emails:
            signals.append("public contact email detected")
            score += 0.15
        if phones:
            signals.append("public phone detected")
            score += 0.1
        if any(k in text for k in ["outsourcing", "managed services"]):
            signals.append("outsourcing/managed services wording detected")
            score += 0.1
        if any(k in text for k in ["hiring", "vacanc", "job opening"]):
            signals.append("hiring/vacancy wording detected")
            score += 0.05

        classification = "Unknown"
        if any(k in text for k in ["managed it", "msp"]):
            classification = "MSP"
        elif any(k in text for k in ["it support", "helpdesk"]):
            classification = "IT Support Provider"
        elif "outsourcing" in text:
            classification = "Outsourcing Opportunity"
        elif any(k in text for k in ["hiring", "vacanc"]):
            classification = "Hiring Lead"

        score = min(score, 1.0)
        save_decision = score >= settings.reasoner_save_threshold and (
            bool(emails) or bool(phones) or bool(evidence.get("contact_page"))
        )

        explanation = (
            "Saved because public evidence suggests a UAE-relevant IT business lead with verifiable contact signals."
            if save_decision
            else "Rejected due to weak/insufficient public business evidence or low confidence score."
        )

        return ReasoningResult(
            classification=classification,
            confidence_score=round(score, 2),
            save_decision=save_decision,
            explanation=explanation,
            detected_signals=signals,
        )
