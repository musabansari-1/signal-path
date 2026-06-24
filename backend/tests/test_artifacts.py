from pathlib import Path

from fastapi.testclient import TestClient

from app.ai.client import ai_client
from app.ai.schemas import GroundedText, MessageGeneration, ResumeGeneration
from tests.test_jobs_scoring import setup_candidate


def create_parsed_job(client: TestClient, project_id: str) -> str:
    job_id = client.post(
        "/api/jobs",
        json={
            "project_id": project_id,
            "company_name": "Acme",
            "title": "Backend Engineer",
            "description": (
                "Build Python and FastAPI services with PostgreSQL. "
                "Kubernetes experience is nice to have."
            ),
        },
    ).json()["id"]
    client.post(f"/api/jobs/{job_id}/parse")
    return job_id


def test_resume_generation_withholds_unsupported_ai_prose_and_exports(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    job_id = create_parsed_job(client, project_id)
    profile = client.get(f"/api/candidate-profile?project_id={project_id}").json()
    python_fact = next(
        fact for fact in profile["verified_facts_json"] if fact["value"] == "Python"
    )
    malicious = ResumeGeneration(
        professional_summary=GroundedText(
            text="Drove 90% revenue growth while leading Kubernetes programs with Python.",
            fact_ids=[python_fact["fact_id"]],
        ),
        skills_section=["Python", "Kubernetes"],
        experience_bullets=[
            GroundedText(
                text="Led Kubernetes in production for 10 years.",
                fact_ids=[python_fact["fact_id"]],
            )
        ],
    )
    monkeypatch.setattr(
        ai_client, "generate_structured", lambda *_args, **_kwargs: malicious
    )

    response = client.post("/api/resumes/generate", json={"job_id": job_id})

    assert response.status_code == 201
    resume = response.json()
    assert "Python" in resume["markdown_content"]
    assert "Kubernetes" not in resume["markdown_content"]
    assert "90%" not in resume["markdown_content"]
    assert malicious.professional_summary.text in resume["truthfulness_check_json"][
        "needs_user_confirmation"
    ]
    assert resume["truthfulness_check_json"]["ready_for_export"] is False
    resume_id = resume["id"]
    assert client.post(f"/api/resumes/{resume_id}/export-pdf").status_code == 409

    confirmed = client.patch(
        f"/api/resumes/{resume_id}", json={"confirm_truthfulness": True}
    )
    assert confirmed.json()["truthfulness_check_json"]["ready_for_export"] is True
    pdf = client.post(f"/api/resumes/{resume_id}/export-pdf")
    docx = client.post(f"/api/resumes/{resume_id}/export-docx")
    assert pdf.status_code == 200 and pdf.content.startswith(b"%PDF")
    assert docx.status_code == 200 and docx.content.startswith(b"PK")


def test_messages_use_controlled_verified_claims(
    client: TestClient, tmp_path: Path, monkeypatch
) -> None:
    project_id = setup_candidate(client, tmp_path, monkeypatch)
    job_id = create_parsed_job(client, project_id)
    malicious = MessageGeneration(
        subject_line="I am your next CTO",
        message_body="I led 100 engineers and made $10 million with Kubernetes.",
        fact_ids=[],
    )
    monkeypatch.setattr(
        ai_client, "generate_structured", lambda *_args, **_kwargs: malicious
    )

    response = client.post(
        "/api/messages/generate",
        json={
            "job_id": job_id,
            "message_type": "recruiter_dm",
            "tone": "warm",
            "length": "concise",
        },
    )

    assert response.status_code == 201
    message = response.json()
    assert "100 engineers" not in message["content"]
    assert "$10 million" not in message["content"]
    assert "Python" in message["content"]
    assert message["claims_used_json"]
    assert any("withheld" in warning for warning in message["review_warnings_json"])

    edited = client.patch(
        f"/api/messages/{message['id']}", json={"content": "User-authored replacement"}
    )
    assert any("Edited content" in warning for warning in edited.json()["review_warnings_json"])

