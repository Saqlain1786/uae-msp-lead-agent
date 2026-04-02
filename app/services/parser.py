import re
from urllib.parse import urljoin

from bs4 import BeautifulSoup

UAE_CITIES = ["Dubai", "Abu Dhabi", "Sharjah", "Ajman", "Ras Al Khaimah", "Fujairah", "Umm Al Quwain"]
SERVICE_KEYWORDS = [
    "managed it",
    "msp",
    "it support",
    "helpdesk",
    "outsourcing",
    "microsoft 365",
    "vacancy",
    "hiring",
]


def extract_signals(html: str | None, base_url: str | None, fallback_text: str = "") -> dict:
    safe_html = html or ""
    safe_base = base_url or ""
    safe_text = fallback_text or ""

    try:
        soup = BeautifulSoup(safe_html, "html.parser")
    except Exception:
        soup = BeautifulSoup("", "html.parser")

    merged_text = " ".join(soup.stripped_strings)
    text = f"{safe_text} {merged_text}".strip().lower()

    emails = sorted(set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE))) if text else []
    phones = sorted(set(re.findall(r"(?:\+971|0)?\s?\d(?:[\s\-]?\d){7,10}", text))) if text else []

    links: list[str] = []
    careers_page = None
    contact_page = None

    for a in soup.find_all("a", href=True):
        href_raw = a.get("href")
        if not href_raw:
            continue
        href = urljoin(safe_base, href_raw)
        label = (a.get_text() or "").lower()
        links.append(href)
        if any(k in href.lower() or k in label for k in ["career", "job", "vacanc"]):
            careers_page = careers_page or href
        if "contact" in href.lower() or "contact" in label:
            contact_page = contact_page or href

    cities = [city for city in UAE_CITIES if city.lower() in text] if text else []
    keywords = [kw for kw in SERVICE_KEYWORDS if kw in text] if text else []

    return {
        "emails": emails or [],
        "phones": phones or [],
        "links": sorted(set(links)) if links else [],
        "careers_page": careers_page,
        "contact_page": contact_page,
        "uae_cities": cities or [],
        "service_keywords": keywords or [],
        "text": text,
    }
