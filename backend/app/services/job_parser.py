import re

from app.ai.client import AIUnavailableError, ai_client
from app.ai.prompts.job_parser import build_job_parser_prompt
from app.ai.schemas import JobExtraction
from app.models.job import Job
from app.services.profile_analysis import KNOWN_TECH_SKILLS, normalize_evidence


def _skills_in_text(text: str) -> list[str]:
    normalized = text.casefold()
    return [
        skill
        for skill in KNOWN_TECH_SKILLS
        if re.search(rf"(?<![\w+#-]){re.escape(skill.casefold())}(?![\w+#-])", normalized)
    ]


def deterministic_job_extraction(description: str) -> JobExtraction:
    normalized = description.casefold()
    nice_marker = min(
        (
            normalized.find(marker)
            for marker in ("nice to have", "preferred", "bonus")
            if marker in normalized
        ),
        default=-1,
    )
    required_text = description if nice_marker < 0 else description[:nice_marker]
    nice_text = "" if nice_marker < 0 else description[nice_marker:]
    years = re.search(r"(\d+(?:\.\d+)?)\s*\+?\s*(?:years|yrs)", normalized)
    work_mode = None
    for mode in ("remote", "hybrid", "onsite", "on-site"):
        if mode in normalized:
            work_mode = "onsite" if mode == "on-site" else mode
            break
    missing = []
    if not work_mode:
        missing.append("work_mode")
    if not years:
        missing.append("minimum_years_experience")
    return JobExtraction(
        required_skills=_skills_in_text(required_text),
        nice_to_have_skills=_skills_in_text(nice_text),
        work_mode=work_mode,
        minimum_years_experience=float(years.group(1)) if years else None,
        missing_information=missing,
    )


def _ground_list(items: list[str], description: str) -> list[str]:
    source = normalize_evidence(description)
    return [item for item in items if normalize_evidence(item) in source]


def parse_job(job: Job) -> JobExtraction:
    fallback = deterministic_job_extraction(job.description)
    try:
        extraction = ai_client.generate_structured(
            build_job_parser_prompt(job.description), JobExtraction
        )
    except (AIUnavailableError, ValueError):
        extraction = fallback

    mentioned_skills = {skill.casefold(): skill for skill in _skills_in_text(job.description)}
    required = [
        mentioned_skills[skill.casefold()]
        for skill in extraction.required_skills
        if skill.casefold() in mentioned_skills
    ]
    nice = [
        mentioned_skills[skill.casefold()]
        for skill in extraction.nice_to_have_skills
        if skill.casefold() in mentioned_skills
        and skill.casefold() not in {s.casefold() for s in required}
    ]
    extraction.required_skills = required or fallback.required_skills
    extraction.nice_to_have_skills = nice or fallback.nice_to_have_skills
    extraction.responsibilities = _ground_list(extraction.responsibilities, job.description)
    extraction.qualifications = _ground_list(extraction.qualifications, job.description)
    extraction.benefits = _ground_list(extraction.benefits, job.description)
    extraction.red_flags = _ground_list(extraction.red_flags, job.description)
    return extraction


def apply_job_extraction(job: Job, extraction: JobExtraction) -> None:
    for field in (
        "required_skills", "nice_to_have_skills", "responsibilities", "qualifications",
        "benefits", "red_flags", "missing_information", "experience_level",
        "minimum_years_experience", "employment_type",
    ):
        value = getattr(extraction, field)
        if value not in (None, [], ""):
            setattr(job, field, value)
    if not job.work_mode and extraction.work_mode:
        job.work_mode = extraction.work_mode
    job.parsed_json = extraction.model_dump(mode="json")
