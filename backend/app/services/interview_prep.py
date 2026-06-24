from app.models.job import Job
from app.models.profile import CandidateProfile
from app.services.claim_validation import fact_registry


def build_interview_prep(
    profile: CandidateProfile, job: Job, stage: str
) -> dict[str, object]:
    confirmed_skills = {skill.casefold() for skill in profile.skills_json or []}
    technical = [
        {
            "id": f"technical-{index}",
            "question": f"How would you approach a practical {skill} problem in this role?",
            "skill": skill,
            "candidate_has_verified_evidence": skill.casefold() in confirmed_skills,
        }
        for index, skill in enumerate(job.required_skills[:10], start=1)
    ]
    registry = fact_registry(profile)
    story_facts = [
        (fact_id, fact)
        for fact_id, fact in registry.items()
        if fact.get("category") in {"experience", "project", "achievement"}
    ][:6]
    behavioral = [
        {
            "id": f"behavioral-{index}",
            "question": "What was your role, action, and verified outcome in this example?",
            "source_fact_id": fact_id,
            "verified_source": fact["value"],
            "note": "Build the STAR answer yourself; Rolewise does not invent missing details.",
        }
        for index, (fact_id, fact) in enumerate(story_facts, start=1)
    ]
    if not behavioral:
        behavioral.append(
            {
                "id": "behavioral-source-needed",
                "question": "Which real project best demonstrates ownership or problem solving?",
                "source_fact_id": None,
                "verified_source": None,
                "note": (
                    "Add a verified example to your profile first; Rolewise does not invent "
                    "a STAR story."
                ),
            }
        )
    missing = [skill for skill in job.required_skills if skill.casefold() not in confirmed_skills]
    return {
        "technical_questions": technical,
        "behavioral_questions": behavioral,
        "company_research": [
            f"Review {job.company_name}'s official product and engineering pages.",
            "Confirm the role's current priorities with the recruiter.",
            "Note recent company information from primary sources before the interview.",
        ],
        "mock_interview_plan": [
            f"10 minutes: concise introduction for the {stage} stage",
            "25 minutes: role-relevant technical questions",
            "15 minutes: verified behavioral examples",
            "10 minutes: candidate questions and reflection",
        ],
        "questions_to_ask": [
            "What would strong performance look like in the first 90 days?",
            "Which technical trade-offs is the team working through now?",
            "How does the team review and ship changes?",
        ],
        "focus_areas": [*job.required_skills[:6], *[f"Gap: {skill}" for skill in missing[:4]]],
    }
