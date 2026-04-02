from abc import ABC, abstractmethod

import httpx

from app.models import Candidate

DISCOVERY_QUERIES = [
    "UAE managed IT services MSP",
    "Dubai IT support helpdesk company",
    "Abu Dhabi IT outsourcing provider",
    "UAE Microsoft 365 support company",
    "UAE IT vacancies managed services",
]


class DiscoveryProvider(ABC):
    @abstractmethod
    def discover(self) -> list[Candidate]:
        raise NotImplementedError


class MockDiscoveryProvider(DiscoveryProvider):
    def discover(self) -> list[Candidate]:
        return [
            Candidate(
                company_name="DesertCloud IT",
                website="https://desertcloud.example",
                source_url="https://directory.example/uae-msp/desertcloud",
                page_text="Managed IT services, helpdesk, Microsoft 365 support in Dubai. Contact sales@desertcloud.example +971 4 123 4567.",
                html="<html><body><a href='/contact'>Contact</a><a href='/careers'>Careers</a><p>Managed IT support in Dubai</p></body></html>",
            ),
            Candidate(
                company_name="Gulf Talent Systems",
                website="https://gulftalent.example",
                source_url="https://jobs.example/company/gulf-talent-systems",
                page_text="We are hiring IT support engineers in Abu Dhabi. Send CV to jobs@gulftalent.example",
                html="<html><body><a href='/jobs'>Vacancies</a><p>IT support hiring Abu Dhabi</p></body></html>",
            ),
            Candidate(
                company_name="Generic Blog",
                website="https://genericblog.example",
                source_url="https://blog.example/post/it-trends",
                page_text="An opinion article about technology trends.",
                html="<html><body><p>No business contact info</p></body></html>",
            ),
        ]


class HttpDiscoveryProvider(DiscoveryProvider):
    """Scaffold for future real discovery integrations (search APIs or curated directories)."""

    def discover(self) -> list[Candidate]:
        # Intentionally conservative: no bypassing controls, only fetch known public pages.
        seeds = []
        candidates: list[Candidate] = []
        with httpx.Client(timeout=8.0, follow_redirects=True) as client:
            for url in seeds:
                try:
                    resp = client.get(url)
                except httpx.HTTPError:
                    continue
                if resp.status_code != 200:
                    continue
                candidates.append(
                    Candidate(
                        company_name=url.split("//")[-1].split("/")[0],
                        website=url,
                        source_url=url,
                        page_text=resp.text[:3000],
                        html=resp.text,
                    )
                )
        return candidates


def get_discovery_provider(mode: str) -> DiscoveryProvider:
    if mode == "live":
        return HttpDiscoveryProvider()
    return MockDiscoveryProvider()
