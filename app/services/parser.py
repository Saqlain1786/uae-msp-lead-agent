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


def extract_signals(html: str, base_url: str, fallback_text: str = "") -> dict:
    soup = BeautifulSoup(html or "", "html.parser")
    text = " ".join(soup.stripped_strings)
    text = f"{fallback_text} {text}".strip().lower()

    emails = sorted(set(re.findall(r"[A-Z0-9._%+-]+@[A-Z0-9.-]+\.[A-Z]{2,}", text, re.IGNORECASE)))
    phones = sorted(set(re.findall(r"(?:\+971|0)?\s?\d(?:[\s\-]?\d){7,10}", text)))

    links = []
    careers_page = None
    contact_page = None
    for a in soup.find_all("a", href=True):
        href = urljoin(base_url, a["href"])
        label = (a.get_text() or "").lower()
        links.append(href)
        if any(k in href.lower() or k in label for k in ["career", "job", "vacanc"]):
            careers_page = careers_page or href
        if "contact" in href.lower() or "contact" in label:
            contact_page = contact_page or href

    cities = [city for city in UAE_CITIES if city.lower() in text]
    keywords = [kw for kw in SERVICE_KEYWORDS if kw in text]

    return {
        "emails": emails,
        "phones": phones,
        "links": sorted(set(links)),
        "careers_page": careers_page,
        "contact_page": contact_page,
        "uae_cities": cities,
        "service_keywords": keywords,
        "text": text,
    }
