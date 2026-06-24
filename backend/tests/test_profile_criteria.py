import uuid
from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.client import ai_client
from app.ai.schemas import CandidateProfileExtraction, EvidenceClaim
from app.core.config import settings
from app.models.profile import CareerAsset
from app.services.profile_analysis import analyze_assets
from tests.test_auth_projects import register


def create_project(client: TestClient) -> str:
    return client.post(
        "/api/projects", json={"name": "Platform search", "target_role": "Platform engineer"}
    ).json()["id"]


def test_upload_analyze_and_edit_profile(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    monkeypatch.setattr(settings, "local_upload_dir", str(tmp_path))
    register(client)
    project_id = create_project(client)
    resume = (
        b"Dev Candidate\nBackend Engineer\n"
        b"Built APIs with Python, FastAPI, PostgreSQL and Docker."
    )

    uploaded = client.post(
        "/api/career-assets/upload",
        data={"project_id": project_id, "asset_type": "resume", "is_primary": "true"},
        files={"file": ("resume.txt", resume, "text/plain")},
    )
    assert uploaded.status_code == 201
    assert uploaded.json()["file_name"] == "resume.txt"
    assert len(list(tmp_path.rglob("*.txt"))) == 1

    analyzed = client.post(
        "/api/candidate-profile/analyze", json={"project_id": project_id}
    )
    assert analyzed.status_code == 200
    assert {"Python", "FastAPI", "PostgreSQL", "Docker"}.issubset(
        set(analyzed.json()["skills_json"])
    )
    assert all(
        fact["verification"] == "source_quote"
        for fact in analyzed.json()["verified_facts_json"]
    )

    edited = client.patch(
        f"/api/candidate-profile?project_id={project_id}",
        json={"headline": "Backend engineer", "skills_json": ["Python", "FastAPI"]},
    )
    assert edited.status_code == 200
    assert edited.json()["reviewed_at"] is not None
    assert any(
        fact["verification"] == "user_confirmed"
        for fact in edited.json()["verified_facts_json"]
    )


def test_upload_rejects_unsupported_files(client: TestClient, tmp_path: Path, monkeypatch) -> None:
    monkeypatch.setattr(settings, "local_upload_dir", str(tmp_path))
    register(client)
    project_id = create_project(client)
    response = client.post(
        "/api/career-assets/upload",
        data={"project_id": project_id},
        files={"file": ("payload.exe", b"not really an executable", "application/octet-stream")},
    )
    assert response.status_code == 415
    assert not list(tmp_path.rglob("*.*"))


def test_role_criteria_require_review_and_validate_salary(client: TestClient) -> None:
    register(client)
    project_id = create_project(client)
    invalid = client.post(
        "/api/role-criteria",
        json={"project_id": project_id, "salary_min": 120000, "salary_max": 80000},
    )
    assert invalid.status_code == 422

    created = client.post(
        "/api/role-criteria",
        json={
            "project_id": project_id,
            "job_titles": ["Platform engineer"],
            "work_modes": ["remote"],
            "required_skills": ["Python"],
        },
    )
    assert created.status_code == 201
    assert created.json()["work_modes"] == ["remote"]
    assert client.get(f"/api/role-criteria/{project_id}").json()["job_titles"] == [
        "Platform engineer"
    ]


def test_ai_claim_without_source_quote_is_rejected(monkeypatch) -> None:
    asset = CareerAsset(
        id=uuid.uuid4(),
        user_id=uuid.uuid4(),
        project_id=uuid.uuid4(),
        title="resume.txt",
        extracted_text="Built production APIs with Python.",
    )
    extraction = CandidateProfileExtraction(
        claims=[
            EvidenceClaim(
                category="skill",
                value="Kubernetes",
                source_asset_id=asset.id,
                evidence_quote="Operated Kubernetes in production",
            )
        ]
    )
    monkeypatch.setattr(ai_client, "generate_structured", lambda *_args, **_kwargs: extraction)

    _, records = analyze_assets([asset])

    assert not [record for record in records if "rejected_claim" not in record]
    assert records[0]["rejected_claim"]["value"] == "Kubernetes"
