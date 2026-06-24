from app.ai.client import AIUnavailableError, ai_client
from app.ai.prompts.resume_tailor import build_resume_prompt
from app.ai.schemas import GroundedText, ResumeGeneration
from app.models.job import Job
from app.models.profile import CandidateProfile
from app.services.claim_validation import fact_registry, validate_grounded_text


def local_resume_draft(profile: CandidateProfile, job: Job) -> ResumeGeneration:
    registry = fact_registry(profile)
    skills = {skill.casefold(): skill for skill in profile.skills_json or []}
    relevant = [
        skills[skill.casefold()]
        for skill in [*job.required_skills, *job.nice_to_have_skills]
        if skill.casefold() in skills
    ]
    selected = list(dict.fromkeys(relevant or list(skills.values())))[:8]
    skill_fact_ids = [
        fact_id
        for fact_id, fact in registry.items()
        if fact.get("category") == "skill"
        and str(fact.get("value", "")).casefold() in {skill.casefold() for skill in selected}
    ]
    summary = GroundedText(
        text=(
            f"Engineer with a verified profile covering {', '.join(selected[:5])}."
            if selected
            else ""
        ),
        fact_ids=skill_fact_ids[:5],
    )
    experience = [
        GroundedText(text=str(fact["value"]), fact_ids=[fact_id])
        for fact_id, fact in registry.items()
        if fact.get("category") in {"experience", "achievement"}
    ][:8]
    projects = [
        GroundedText(text=str(fact["value"]), fact_ids=[fact_id])
        for fact_id, fact in registry.items()
        if fact.get("category") == "project"
    ][:5]
    return ResumeGeneration(
        professional_summary=summary,
        skills_section=selected,
        experience_bullets=experience,
        project_bullets=projects,
        warnings=["Review every line before export."],
    )


def generate_grounded_resume(
    profile: CandidateProfile, job: Job
) -> tuple[dict[str, object], str, dict[str, object]]:
    ai_suggestions: list[str] = []
    try:
        suggested = ai_client.generate_structured(
            build_resume_prompt(profile, job), ResumeGeneration
        )
        ai_suggestions = [
            suggested.professional_summary.text,
            *[item.text for item in suggested.experience_bullets],
            *[item.text for item in suggested.project_bullets],
        ]
    except (AIUnavailableError, ValueError):
        pass
    # The final draft is composed from exact registry values. AI prose stays review-only because
    # citing a fact id alone cannot prove that a rephrased metric, scope, or outcome is truthful.
    draft = local_resume_draft(profile, job)

    accepted: list[str] = []
    removed: list[str] = [item for item in ai_suggestions if item.strip()]
    warnings = list(draft.warnings)
    summary_result = validate_grounded_text(draft.professional_summary, profile)
    summary = summary_result.accepted
    if summary_result.warning:
        removed.append(draft.professional_summary.text)
        warnings.append(summary_result.warning)

    def validate_items(items: list[GroundedText]) -> list[dict[str, object]]:
        valid: list[dict[str, object]] = []
        for item in items:
            result = validate_grounded_text(item, profile)
            if result.accepted:
                accepted.append(result.accepted)
                valid.append(
                    {
                        "text": result.accepted,
                        "fact_ids": item.fact_ids,
                        "verification": "server_validated",
                    }
                )
            else:
                removed.append(item.text)
                if result.warning:
                    warnings.append(result.warning)
        return valid

    experience = validate_items(draft.experience_bullets)
    projects = validate_items(draft.project_bullets)
    confirmed_skills = {skill.casefold(): skill for skill in profile.skills_json or []}
    skills = list(
        dict.fromkeys(
            confirmed_skills[skill.casefold()]
            for skill in draft.skills_section
            if skill.casefold() in confirmed_skills
        )
    )
    if summary:
        accepted.insert(0, summary)
    content = {
        "professional_summary": summary,
        "skills": skills,
        "experience_bullets": experience,
        "project_bullets": projects,
    }
    lines = [f"# {profile.headline or job.title}", ""]
    if summary:
        lines.extend(["## Professional summary", summary, ""])
    if skills:
        lines.extend(["## Skills", ", ".join(skills), ""])
    if experience:
        lines.extend(["## Experience", *[f"- {item['text']}" for item in experience], ""])
    if projects:
        lines.extend(["## Projects", *[f"- {item['text']}" for item in projects], ""])
    checklist = {
        "verified_claims": accepted,
        "needs_user_confirmation": removed,
        "removed_or_avoided_claims": removed,
        "warnings": list(dict.fromkeys(warnings)),
        "ready_for_export": False,
        "user_confirmed_at": None,
    }
    return content, "\n".join(lines).strip(), checklist
