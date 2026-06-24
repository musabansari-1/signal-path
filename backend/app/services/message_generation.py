from app.ai.client import AIUnavailableError, ai_client
from app.ai.prompts.message_generator import build_message_prompt
from app.ai.schemas import GroundedText, MessageGeneration
from app.models.job import Job
from app.models.profile import CandidateProfile
from app.services.claim_validation import fact_registry, validate_grounded_text


def local_message(
    profile: CandidateProfile, job: Job, message_type: str, tone: str, length: str
) -> MessageGeneration:
    registry = fact_registry(profile)
    job_skills = {skill.casefold() for skill in [*job.required_skills, *job.nice_to_have_skills]}
    matching_facts = [
        (fact_id, fact)
        for fact_id, fact in registry.items()
        if fact.get("category") == "skill"
        and str(fact.get("value", "")).casefold() in job_skills
    ][:3]
    skills = [str(fact["value"]) for _, fact in matching_facts]
    fact_ids = [fact_id for fact_id, _ in matching_facts]
    evidence = f" My verified background includes {', '.join(skills)}." if skills else ""
    if message_type == "cover_letter":
        body = (
            f"I'm writing to express interest in the {job.title} role at {job.company_name}."
            f"{evidence} I would welcome the chance to discuss how that background could support "
            "the needs described for this role."
        )
        subject = f"Application for {job.title}"
    elif message_type == "follow_up":
        body = (
            f"I'm following up on the {job.title} opportunity at {job.company_name}."
            f"{evidence} I'm still interested and would be glad to provide any helpful context."
        )
        subject = f"Following up: {job.title}"
    else:
        body = (
            f"Hi — I’m interested in the {job.title} role at {job.company_name}."
            f"{evidence} If the role is still open, I’d value a brief conversation "
            "about the team’s needs."
        )
        subject = None
    return MessageGeneration(
        subject_line=subject,
        message_body=body,
        fact_ids=fact_ids,
        personalization_points=[job.title, job.company_name],
        review_warnings=["Review before copying or sending."],
    )


def generate_grounded_message(
    profile: CandidateProfile,
    job: Job,
    message_type: str,
    tone: str,
    length: str,
) -> tuple[str | None, str, list[dict[str, object]], list[str]]:
    ai_review_warning: str | None = None
    try:
        ai_client.generate_structured(
            build_message_prompt(profile, job, message_type, tone, length),
            MessageGeneration,
        )
        ai_review_warning = (
            "AI prose was withheld from the final draft; only server-composed verified "
            "claims were used."
        )
    except (AIUnavailableError, ValueError):
        pass
    # Assemble the final message from controlled language and exact verified skill values. An AI
    # citation is not enough to establish that arbitrary generated prose is factually supported.
    draft = local_message(profile, job, message_type, tone, length)
    if draft.fact_ids:
        result = validate_grounded_text(
            GroundedText(text=draft.message_body, fact_ids=draft.fact_ids), profile
        )
        if not result.accepted:
            fallback = local_message(profile, job, message_type, tone, length)
            result = validate_grounded_text(
                GroundedText(text=fallback.message_body, fact_ids=fallback.fact_ids), profile
            )
            draft = fallback
        if result.accepted:
            claims = [
                {"fact_id": fact_id, "value": fact_registry(profile)[fact_id]["value"]}
                for fact_id in draft.fact_ids
                if fact_id in fact_registry(profile)
            ]
            warnings = list(draft.review_warnings)
            if ai_review_warning:
                warnings.append(ai_review_warning)
            return draft.subject_line, result.accepted, claims, warnings
    fallback = local_message(profile, job, message_type, tone, length)
    return (
        fallback.subject_line,
        fallback.message_body,
        [],
        [
            *fallback.review_warnings,
            "No candidate claims were added because no matching verified facts exist.",
        ],
    )
