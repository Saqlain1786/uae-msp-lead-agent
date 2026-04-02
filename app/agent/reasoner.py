from app.config import settings
from app.models import ReasoningResult


class RuleBasedReasoner:
    def evaluate(self, evidence: dict) -> ReasoningResult:
        signals: list[str] = []
        score = 0.0
        text = evidence.get("text", "")

        if any(k in text for k in ["managed it", "msp", "managed services"]):
            signals.append("company offers managed IT services")
            score += 0.25
        if any(k in text for k in ["it support", "helpdesk"]):
            signals.append("company offers IT support/helpdesk")
            score += 0.2
        if evidence.get("careers_page") or any(k in text for k in ["hiring", "vacanc", "jobs"]):
            signals.append("careers page exists")
            score += 0.1
        if evidence.get("uae_cities"):
            signals.append("UAE city detected")
            score += 0.15
        if evidence.get("emails"):
            signals.append("public contact email detected")
            score += 0.15
        if evidence.get("phones"):
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
        elif any(k in text for k in ["outsourcing"]):
            classification = "Outsourcing Opportunity"
        elif any(k in text for k in ["hiring", "vacanc"]):
            classification = "Hiring Lead"

        score = min(score, 1.0)
        save_decision = score >= settings.reasoner_save_threshold and (
            evidence.get("emails") or evidence.get("phones") or evidence.get("contact_page")
        )

        if save_decision:
            explanation = (
                "Saved because public evidence suggests a UAE-relevant IT business lead with verifiable contact signals."
            )
        else:
            explanation = "Rejected due to weak/insufficient public business evidence or low confidence score."

        return ReasoningResult(
            classification=classification,
            confidence_score=round(score, 2),
            save_decision=save_decision,
            explanation=explanation,
            detected_signals=signals,
        )
