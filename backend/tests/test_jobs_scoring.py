from pathlib import Path

from fastapi.testclient import TestClient

from app.core.config import settings
from app.services.job_discovery import DiscoveredJob
from tests.test_auth_projects import register


def setup_candidate(client: TestClient, tmp_path: Path, monkeypatch) -> str:
    monkeypatch.setattr(settings, "local_upload_dir", str(tmp_path))
    register(client)
    project_id = client.post(
        "/api/projects", json={"name": "Backend search", "target_role": "Backend engineer"}
    ).json()["id"]
    client.post(
        "/api/career-assets/upload",
        data={"project_id": project_id, "is_primary": "true"},
        files={
            "file": (
                "resume.txt",
                b"Backend engineer using Python, FastAPI, PostgreSQL and Docker.",
                "text/plain",
            )
        },
    )
    client.post("/api/candidate-profile/analyze", json={"project_id": project_id})
    client.patch(
        f"/api/candidate-profile?project_id={project_id}", json={"years_experience": 3}
    )
    client.post(
        "/api/role-criteria",
        json={
            "project_id": project_id,
            "job_titles": ["Backend engineer"],
            "work_modes": ["remote"],
            "locations": ["India"],
        },
    )
    return project_id


def test_job_parse_and_explainable_score(client: TestClient, tmp_path: Path, monkeypatch) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    description = """We need a Backend Engineer with 2+ years of experience.
Required: Python, FastAPI, PostgreSQL, and Kubernetes. This is a remote role in India.
Nice to have: React."""
    created = client.post(
        "/api/jobs",
        json={
            "project_id": project_id,
            "company_name": "Acme",
            "title": "Backend Engineer",
            "description": description,
            "location": "India",
        },
    )
    assert created.status_code == 201
    job_id = created.json()["id"]

    parsed = client.post(f"/api/jobs/{job_id}/parse")
    assert parsed.status_code == 200
    assert "Kubernetes" in parsed.json()["required_skills"]
    assert parsed.json()["minimum_years_experience"] == 2
    assert parsed.json()["work_mode"] == "remote"

    scored = client.post(f"/api/jobs/{job_id}/score")
    assert scored.status_code == 200
    result = scored.json()
    assert 0 <= result["total_score"] <= 100
    assert result["recommendation"] in {"strong_apply", "apply", "maybe", "skip"}
    assert any("kubernetes" in gap.lower() for gap in result["gaps"])
    assert "kubernetes" not in {keyword.lower() for keyword in result["keywords_to_add"]}
    assert client.get(f"/api/jobs/{job_id}").json()["latest_score"] == result["total_score"]


def test_csv_import_has_bounded_contract(client: TestClient, tmp_path: Path, monkeypatch) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    csv_body = (
        "company_name,title,description,location,work_mode\n"
        'Acme,API Engineer,"Build Python APIs for our product",Remote,remote\n'
        "Missing,Incomplete,,Remote,remote\n"
    )
    response = client.post(
        "/api/jobs/import-csv",
        data={"project_id": project_id},
        files={"file": ("jobs.csv", csv_body.encode(), "text/csv")},
    )
    assert response.status_code == 200
    assert response.json()["imported"] == 1
    assert response.json()["skipped"] == 1
    assert len(client.get(f"/api/jobs?project_id={project_id}").json()) == 1


def test_discovery_uses_profile_and_deduplicates_listings(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    listings = [
        DiscoveredJob(
            company_name="Remote Co",
            title="Backend Engineer",
            description="Build Python FastAPI services with PostgreSQL for a remote team.",
            url="https://jobs.example.com/backend-engineer?source=feed",
            location="Worldwide",
            employment_type="full_time",
        )
    ]
    monkeypatch.setattr("app.api.routes.jobs.discover_remote_jobs", lambda query, limit: listings)

    first = client.post("/api/jobs/discover", json={"project_id": project_id})
    assert first.status_code == 200
    result = first.json()
    assert result["searched_for"].startswith("Backend engineer")
    assert "FastAPI" in result["searched_for"]
    assert result["imported"] == 1
    assert result["skipped"] == 0
    assert result["jobs"][0]["source_type"] == "internet"
    assert result["jobs"][0]["latest_score"] is not None

    second = client.post("/api/jobs/discover", json={"project_id": project_id})
    assert second.status_code == 200
    assert second.json()["imported"] == 0
    assert second.json()["skipped"] == 1


def test_discovery_aggregates_across_sources(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    remotive_listing = DiscoveredJob(
        company_name="Remote Co",
        title="Backend Engineer",
        description="Build Python FastAPI services with PostgreSQL for a remote team.",
        url="https://jobs.example.com/backend-engineer?source=feed",
        location="Worldwide",
        employment_type="full_time",
    )
    muse_listing = DiscoveredJob(
        company_name="Muse Co",
        title="Senior Backend Engineer",
        description="Work on Python services and APIs.",
        url="https://jobs.example.com/senior-backend-engineer",
        location="United States",
        employment_type="full_time",
    )
    monkeypatch.setattr(
        "app.api.routes.jobs.discover_remote_jobs", lambda query, limit: [remotive_listing, muse_listing]
    )

    response = client.post("/api/jobs/discover", json={"project_id": project_id, "limit": 15})
    assert response.status_code == 200
    data = response.json()
    assert data["imported"] == 2
    assert {job["company_name"] for job in data["jobs"]} == {"Remote Co", "Muse Co"}


def test_jobs_are_private_to_owner(client: TestClient, tmp_path: Path, monkeypatch) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    job_id = client.post(
        "/api/jobs",
        json={
            "project_id": project_id,
            "company_name": "Private Co",
            "title": "Software Engineer",
            "description": (
                "Build and maintain software products with a thoughtful engineering team."
            ),
        },
    ).json()["id"]
    client.post("/api/auth/logout")
    register(client, "another@example.com")

    assert client.get(f"/api/jobs/{job_id}").status_code == 404
    assert client.post(f"/api/jobs/{job_id}/score").status_code == 404
