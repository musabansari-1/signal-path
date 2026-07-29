from dataclasses import dataclass
from urllib.parse import quote_plus, urlsplit, urlunsplit

import httpx

from app.core.config import settings
from app.models.profile import CandidateProfile, RoleCriteria

REMOTIVE_JOBS_URL = "https://remotive.com/api/remote-jobs"
THE_MUSE_JOBS_URL = "https://www.themuse.com/api/public/jobs"
ADZUNA_JOBS_URL = "https://api.adzuna.com/v1/api/jobs"


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


def _append_remote(results: list[DiscoveredJob], listing: dict, seen_urls: set[str], limit: int) -> None:
    title = str(listing.get("title") or "").strip()
    company = str(listing.get("company_name") or "").strip()
    description = str(listing.get("description") or "").strip()
    raw_url = str(listing.get("url") or "").strip()
    if not (title and company and description and raw_url.startswith(("https://", "http://"))):
        return
    url = normalize_listing_url(raw_url)
    if not url or url in seen_urls:
        return
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
    if len(results) > limit:
        results.pop()


def discover_remotive_jobs(query: str, limit: int) -> list[DiscoveredJob]:
    response = httpx.get(
        REMOTIVE_JOBS_URL,
        params={"search": query, "limit": max(limit * 2, 20)},
        timeout=10.0,
        headers={"Accept": "application/json", "User-Agent": "Rolewise/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    listings = payload.get("jobs", []) if isinstance(payload, dict) else []
    results: list[DiscoveredJob] = []
    seen_urls: set[str] = set()
    for listing in listings:
        if isinstance(listing, dict):
            _append_remote(results, listing, seen_urls, limit)
        if len(results) >= limit:
            break
    return results


def discover_the_muse_jobs(query: str, limit: int) -> list[DiscoveredJob]:
    params = {"page": 1, "descending": "true"}
    if query.strip():
        params["category"] = "Software Engineering"
    response = httpx.get(
        THE_MUSE_JOBS_URL,
        params=params,
        timeout=10.0,
        headers={"Accept": "application/json", "User-Agent": "Rolewise/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    listings = payload.get("results", []) if isinstance(payload, dict) else []
    results: list[DiscoveredJob] = []
    seen_urls: set[str] = set()
    for listing in listings:
        if not isinstance(listing, dict):
            continue
        title = str(listing.get("name") or "").strip()
        company = str((listing.get("company") or {}).get("name") or "").strip()
        locations = listing.get("locations") or []
        location = None
        if isinstance(locations, list) and locations:
            location = str((locations[0] or {}).get("name") or "").strip() or None
        levels = listing.get("levels") or []
        employment_type = None
        if isinstance(levels, list) and levels:
            employment_type = str((levels[0] or {}).get("name") or "").strip() or None
        descriptions = listing.get("refs") or {}
        raw_url = str((descriptions or {}).get("landing_page") or listing.get("refs", {}).get("landing_page") or "").strip()
        description = str(listing.get("contents") or "").strip()
        if not raw_url and isinstance(listing.get("refs"), dict):
            raw_url = str(listing["refs"].get("landing_page") or "").strip()
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
                location=location,
                employment_type=employment_type,
            )
        )
        if len(results) >= limit:
            break
    return results


def discover_adzuna_jobs(query: str, limit: int) -> list[DiscoveredJob]:
    if not (settings.adzuna_app_id and settings.adzuna_app_key):
        return []
    response = httpx.get(
        f"{ADZUNA_JOBS_URL}/us/search/1",
        params={
            "app_id": settings.adzuna_app_id,
            "app_key": settings.adzuna_app_key,
            "what": query,
            "results_per_page": limit,
            "content-type": "application/json",
        },
        timeout=10.0,
        headers={"Accept": "application/json", "User-Agent": "Rolewise/1.0"},
    )
    response.raise_for_status()
    payload = response.json()
    listings = payload.get("results", []) if isinstance(payload, dict) else []
    results: list[DiscoveredJob] = []
    seen_urls: set[str] = set()
    for listing in listings:
        if not isinstance(listing, dict):
            continue
        title = str(listing.get("title") or "").strip()
        company = str((listing.get("company") or {}).get("display_name") or "").strip()
        description = str(listing.get("description") or "").strip()
        raw_url = str(listing.get("redirect_url") or listing.get("adref") or "").strip()
        location = str((listing.get("location") or {}).get("display_name") or "").strip() or None
        employment_type = str(listing.get("contract_time") or "").strip() or None
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
                location=location,
                employment_type=employment_type,
            )
        )
        if len(results) >= limit:
            break
    return results


def discover_remote_jobs(query: str, limit: int) -> list[DiscoveredJob]:
    """Retrieve current listings from multiple legal job sources."""
    providers = (
        discover_remotive_jobs,
        discover_the_muse_jobs,
        discover_adzuna_jobs,
    )
    results: list[DiscoveredJob] = []
    seen_urls: set[str] = set()
    for provider in providers:
        try:
            provider_results = provider(query, limit)
        except httpx.HTTPError:
            continue
        for listing in provider_results:
            url = normalize_listing_url(listing.url)
            if not url or url in seen_urls:
                continue
            seen_urls.add(url)
            results.append(listing)
            if len(results) >= limit:
                return results
    return results
