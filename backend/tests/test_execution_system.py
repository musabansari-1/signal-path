from datetime import date
from pathlib import Path

from fastapi.testclient import TestClient

from tests.test_jobs_scoring import setup_candidate


def create_job(client: TestClient, project_id: str) -> str:
    job_id = client.post(
        "/api/jobs",
        json={
            "project_id": project_id,
            "company_name": "Acme",
            "title": "Backend Engineer",
            "description": (
                "Build Python and FastAPI services with PostgreSQL for customer workflows."
            ),
            "location": "Remote",
            "work_mode": "remote",
        },
    ).json()["id"]
    client.post(f"/api/jobs/{job_id}/parse")
    client.post(f"/api/jobs/{job_id}/score")
    return job_id


def test_application_analytics_and_interview_prep_are_grounded(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    job_id = create_job(client, project_id)
    application = client.post(
        "/api/applications",
        json={
            "job_id": job_id,
            "status": "applied",
            "follow_up_date": date.today().isoformat(),
        },
    )
    assert application.status_code == 201
    application_id = application.json()["id"]
    assert application.json()["date_applied"] == date.today().isoformat()
    assert client.post(
        "/api/applications", json={"job_id": job_id, "status": "saved"}
    ).status_code == 409

    analytics = client.get(f"/api/applications/analytics?project_id={project_id}")
    assert analytics.status_code == 200
    assert analytics.json()["total_applications"] == 1
    assert analytics.json()["follow_ups_due"] == 1
    assert analytics.json()["average_match_score"] is not None

    prep = client.post(
        "/api/interview-prep/generate",
        json={
            "job_id": job_id,
            "application_id": application_id,
            "interview_stage": "technical",
        },
    )
    assert prep.status_code == 201
    body = prep.json()
    assert body["technical_questions"]
    assert body["behavioral_questions"][0]["verified_source"] is None
    assert "does not invent" in body["behavioral_questions"][0]["note"]


def test_portfolio_audit_and_codex_prompt_use_supplied_project_data(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    created = client.post(
        "/api/portfolio-projects",
        json={
            "project_id": project_id,
            "name": "Task API",
            "description": (
                "A small API that stores and updates personal tasks for signed-in users."
            ),
            "tech_stack": ["Python", "FastAPI"],
        },
    )
    assert created.status_code == 201
    portfolio_id = created.json()["id"]
    audited = client.post(f"/api/portfolio-projects/{portfolio_id}/audit")
    assert audited.status_code == 200
    assert audited.json()["improvement_tasks"]
    prompted = client.post(f"/api/portfolio-projects/{portfolio_id}/codex-prompt")
    prompt = prompted.json()["codex_prompt"]
    assert "Task API" in prompt and "Python, FastAPI" in prompt
    assert "Do not claim features" in prompt


def test_weekly_plan_is_idempotent_and_tracks_progress(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    first = client.post("/api/weekly-plan/generate", json={"project_id": project_id})
    second = client.post("/api/weekly-plan/generate", json={"project_id": project_id})
    assert first.status_code == 200
    assert len(first.json()) == 7
    assert [task["id"] for task in first.json()] == [task["id"] for task in second.json()]

    task_id = first.json()[0]["id"]
    updated = client.patch(f"/api/weekly-tasks/{task_id}", json={"status": "complete"})
    assert updated.json()["status"] == "complete"
    summary = client.get(f"/api/weekly-plan/summary?project_id={project_id}").json()
    assert summary == {"total": 7, "complete": 1, "skipped": 0, "completion_rate": 14.3}
