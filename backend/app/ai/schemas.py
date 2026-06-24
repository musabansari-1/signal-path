import uuid

from pydantic import BaseModel, Field


class EvidenceClaim(BaseModel):
    category: str = Field(
        description="skill, experience, project, education, certification, or achievement"
    )
    value: str = Field(min_length=1, max_length=1000)
    source_asset_id: uuid.UUID
    evidence_quote: str = Field(min_length=1, max_length=2000)


class CandidateProfileExtraction(BaseModel):
    headline: str | None = None
    summary: str | None = None
    strengths: list[str] = []
    gaps: list[str] = []
    best_fit_roles: list[str] = []
    claims: list[EvidenceClaim] = []
    suggestions: list[str] = []
    missing_information_questions: list[str] = []
