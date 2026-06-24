import json

from app.models.job import Job
from app.models.profile import CandidateProfile


def build_message_prompt(
    profile: CandidateProfile, job: Job, message_type: str, tone: str, length: str
) -> str:
    facts = json.dumps(profile.verified_facts_json, ensure_ascii=False)
    return f"""Draft a {length}, {tone} {message_type} for this opportunity.
Use only candidate claims in the verified fact registry and return every fact_id used.
It is safe to mention the target company and role as the recipient context, but never portray that
company as the candidate's employer. Do not invent referrals, familiarity, metrics, or enthusiasm
about details that are not present. Keep the message editable and do not imply it has been sent.

TARGET: {job.title} at {job.company_name}
JOB DESCRIPTION: {job.description}

VERIFIED FACT REGISTRY:
{facts}
"""

