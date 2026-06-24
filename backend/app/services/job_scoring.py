from dataclasses import dataclass
from datetime import UTC, datetime

from app.models.job import Job, JobScore
from app.models.profile import CandidateProfile, RoleCriteria


def _norm(values: list[str]) -> set[str]:
    return {value.strip().casefold() for value in values if value.strip()}


def _ratio(matches: int, total: int, empty_score: int = 70) -> int:
    return round(matches / total * 100) if total else empty_score


@dataclass(frozen=True)
class ScoreBreakdown:
    skill: int
    experience: int
    criteria: int
    keyword: int
    location: int
    growth: int
    difficulty: int

    @property
    def total(self) -> int:
        return round(
            self.skill * 0.25
            + self.experience * 0.20
            + self.criteria * 0.20
            + self.keyword * 0.15
            + self.location * 0.10
            + self.growth * 0.05
            + self.difficulty * 0.05
        )


def compute_job_score(
    job: Job,
    profile: CandidateProfile,
    criteria: RoleCriteria | None,
    existing: JobScore | None = None,
) -> JobScore:
    candidate_skills = _norm(profile.skills_json or [])
    required = _norm(job.required_skills or [])
    nice = _norm(job.nice_to_have_skills or [])
    matched_required = required & candidate_skills
    missing_required = required - candidate_skills
    skill_score = _ratio(len(matched_required), len(required))

    if job.minimum_years_experience is None:
        experience_score = 75
    elif profile.years_experience is None:
        experience_score = 45
    elif profile.years_experience >= job.minimum_years_experience:
        experience_score = 100
    else:
        experience_score = max(
            20, round(profile.years_experience / job.minimum_years_experience * 100)
        )

    criteria_checks: list[bool] = []
    avoided = False
    if criteria:
        titles = _norm(criteria.job_titles)
        if titles:
            criteria_checks.append(any(title in job.title.casefold() for title in titles))
        modes = _norm(criteria.work_modes)
        if modes and job.work_mode:
            criteria_checks.append(job.work_mode.casefold() in modes)
        avoided = any(role in job.title.casefold() for role in _norm(criteria.roles_to_avoid))
        criteria_score = _ratio(sum(criteria_checks), len(criteria_checks), empty_score=70)
        if avoided:
            criteria_score = 0
    else:
        criteria_score = 60

    job_keywords = required | nice
    matched_keywords = job_keywords & candidate_skills
    keyword_score = _ratio(len(matched_keywords), len(job_keywords))

    if not criteria or not criteria.locations:
        location_score = 75
    elif job.work_mode == "remote" and "remote" in _norm(criteria.work_modes):
        location_score = 100
    elif job.location and any(
        location in job.location.casefold() for location in _norm(criteria.locations)
    ):
        location_score = 100
    else:
        location_score = 35

    target_titles = _norm(criteria.job_titles) if criteria else set()
    growth_score = 85 if any(title in job.title.casefold() for title in target_titles) else 65
    difficulty_score = max(15, 100 - len(job.red_flags or []) * 25)
    breakdown = ScoreBreakdown(
        skill_score, experience_score, criteria_score, keyword_score,
        location_score, growth_score, difficulty_score,
    )
    total = breakdown.total
    if total >= 80:
        recommendation = "strong_apply"
    elif total >= 65:
        recommendation = "apply"
    elif total >= 45:
        recommendation = "maybe"
    else:
        recommendation = "skip"
    strengths = [f"Your profile confirms {skill}" for skill in sorted(matched_required)]
    if location_score == 100:
        strengths.append("The location and work-mode preference aligns")
    gaps = [
        f"The role asks for {skill}, which is not confirmed in your profile"
        for skill in sorted(missing_required)
    ]
    if profile.years_experience is None and job.minimum_years_experience:
        gaps.append("Your profile does not yet confirm total years of experience")
    explanation = (
        f"The {total}/100 score combines verified skill overlap, experience, your saved criteria, "
        "keyword evidence, location fit, growth alignment, and stated role risks."
    )
    next_step = (
        "Address the listed gaps directly; do not add them as experience."
        if gaps
        else "The verified evidence supports a focused application."
    )
    strategy = (
        "Emphasize only the matched skills and evidence already present in your profile. "
        f"{next_step}"
    )
    score = existing or JobScore(job_id=job.id, user_id=job.user_id, project_id=job.project_id)
    score.total_score = total
    score.skill_match_score = breakdown.skill
    score.experience_match_score = breakdown.experience
    score.criteria_match_score = breakdown.criteria
    score.keyword_match_score = breakdown.keyword
    score.location_fit_score = breakdown.location
    score.growth_potential_score = breakdown.growth
    score.difficulty_score = breakdown.difficulty
    score.recommendation = recommendation
    score.strengths = strengths
    score.gaps = gaps
    score.keywords_to_add = sorted(matched_keywords)
    score.explanation = explanation
    score.application_strategy = strategy
    score.scored_at = datetime.now(UTC)
    job.latest_score = total
    return score
