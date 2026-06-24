from datetime import date, timedelta


def week_bounds(today: date | None = None) -> tuple[date, date]:
    current = today or date.today()
    monday = current - timedelta(days=current.weekday())
    return monday, monday + timedelta(days=6)


def weekly_task_specs(
    job_count: int, application_count: int, follow_ups_due: int
) -> list[dict[str, object]]:
    monday, _ = week_bounds()
    specs = [
        (
            0,
            "collect_jobs",
            "Collect focused opportunities",
            f"Add {max(3, 5 - job_count)} roles that match your criteria.",
        ),
        (
            1,
            "score_shortlist",
            "Score and shortlist",
            "Review explainable scores and choose the strongest opportunities.",
        ),
        (
            2,
            "tailor_resume",
            "Tailor a resume",
            "Build one truthful, job-specific resume from verified evidence.",
        ),
        (
            3,
            "apply_outreach",
            "Apply with intention",
            "Submit a reviewed application and prepare one relevant outreach draft.",
        ),
        (
            4,
            "follow_up",
            "Close follow-up loops",
            f"Review {follow_ups_due} due follow-ups and record every response.",
        ),
        (
            5,
            "portfolio",
            "Strengthen one proof point",
            "Complete one high-priority portfolio improvement.",
        ),
        (
            6,
            "interview_prep",
            "Practice and reflect",
            f"Review {application_count} applications and practice one interview area.",
        ),
    ]
    return [
        {
            "task_date": monday + timedelta(days=offset),
            "day_label": (monday + timedelta(days=offset)).strftime("%A"),
            "task_type": task_type,
            "title": title,
            "description": description,
        }
        for offset, task_type, title, description in specs
    ]
