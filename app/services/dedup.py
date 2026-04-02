from app.services.storage import get_lead_by_company_name, get_lead_by_website


def is_duplicate(website: str | None, company_name: str | None) -> bool:
    if website and get_lead_by_website(website):
        return True
    if company_name and get_lead_by_company_name(company_name):
        return True
    return False
