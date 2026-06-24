import json

from app.models.job import Job
from app.models.profile import CandidateProfile


def build_resume_prompt(profile: CandidateProfile, job: Job) -> str:
    facts = json.dumps(profile.verified_facts_json, ensure_ascii=False)
    return f"""Create a concise ATS-friendly resume draft for the target role.
Use only the supplied fact registry. Each summary or bullet must cite the exact fact_ids it uses.
Reorder and rephrase supported evidence, but do not add scope, seniority, tools, metrics, dates,
companies, outcomes, or responsibilities. Omit a section when no relevant evidence supports it.
The skills section may contain only confirmed skill facts.

TARGET ROLE: {job.title} at {job.company_name}
REQUIRED SKILLS: {json.dumps(job.required_skills)}
JOB DESCRIPTION: {job.description}

VERIFIED FACT REGISTRY:
{facts}
"""

