from dataclasses import dataclass
from urllib.parse import urlsplit, urlunsplit

import httpx

from app.models.profile import CandidateProfile, RoleCriteria

REMOTIVE_JOBS_URL = "https://remotive.com/api/remote-jobs"


@dataclass(frozen=True)
class DiscoveredJob:
    company_name: str
    title: str
    description: str
    url: str
    location: str | None
    employment_type: str | None


def build_discovery_query(
    profile: CandidateProfile, criteria: RoleCriteria | None, fallback_role: str
) -> str:
    """Build a short, useful search phrase from user-confirmed search data."""
    titles = (
        (criteria.job_titles if criteria else []) or profile.best_fit_roles_json or [fallback_role]
    )
    skills = (criteria.required_skills if criteria else []) or profile.skills_json or []
    parts = [str(titles[0]).strip()] + [str(skill).strip() for skill in skills[:2]]
    return " ".join(part for part in parts if part)[:180]


def normalize_listing_url(url: str) -> str:
    """Remove fragments and query parameters so the same listing is imported once."""
    parsed = urlsplit(url.strip())
    return urlunsplit((parsed.scheme, parsed.netloc, parsed.path.rstrip("/"), "", ""))


def discover_remote_jobs(query: str, limit: int) -> list[DiscoveredJob]:
    """Retrieve current listings from Remotive's public remote-job API."""
    response = httpx.get(
        REMOTIVE_JOBS_URL,
        params={"search": query},
        timeout=10.0,
        headers={"Accept": "application/json", "User-Agent": "Rolewise/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    listings = payload.get("jobs", []) if isinstance(payload, dict) else []
    results: list[DiscoveredJob] = []
    seen_urls: set[str] = set()
    for listing in listings:
        if not isinstance(listing, dict):
            continue
        title = str(listing.get("title") or "").strip()
        company = str(listing.get("company_name") or "").strip()
        description = str(listing.get("description") or "").strip()
        raw_url = str(listing.get("url") or "").strip()
        if not (title and company and description and raw_url.startswith(("https://", "http://"))):
            continue
        url = normalize_listing_url(raw_url)
        if not url or url in seen_urls:
            continue
        seen_urls.add(url)
        results.append(
            DiscoveredJob(
                company_name=company[:240],
                title=title[:240],
                description=description[:200_000],
                url=url,
                location=(str(listing.get("candidate_required_location") or "").strip() or None),
                employment_type=(str(listing.get("job_type") or "").strip() or None),
            )
        )
        if len(results) >= limit:
            break
    return results
