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


class JobExtraction(BaseModel):
    required_skills: list[str] = []
    nice_to_have_skills: list[str] = []
    responsibilities: list[str] = []
    qualifications: list[str] = []
    benefits: list[str] = []
    red_flags: list[str] = []
    missing_information: list[str] = []
    work_mode: str | None = None
    employment_type: str | None = None
    experience_level: str | None = None
    minimum_years_experience: float | None = None


class GroundedText(BaseModel):
    text: str
    fact_ids: list[str] = []


class ResumeGeneration(BaseModel):
    professional_summary: GroundedText
    skills_section: list[str] = []
    experience_bullets: list[GroundedText] = []
    project_bullets: list[GroundedText] = []
    warnings: list[str] = []


class MessageGeneration(BaseModel):
    subject_line: str | None = None
    message_body: str
    fact_ids: list[str] = []
    personalization_points: list[str] = []
    review_warnings: list[str] = []
