from app.models.execution import PortfolioProject


def audit_portfolio_project(
    project: PortfolioProject, target_role: str | None
) -> dict[str, object]:
    strengths = []
    if project.github_url:
        strengths.append("Source repository is linked")
    if project.live_url:
        strengths.append("A live demonstration is available")
    if project.tech_stack:
        strengths.append("Technology choices are visible")
    tasks = []
    if len(project.description.split()) < 40:
        tasks.append(
            {"title": "Explain the problem and user", "priority": "high", "status": "pending"}
        )
    if not project.github_url:
        tasks.append(
            {
                "title": "Add a source repository or explain access",
                "priority": "high",
                "status": "pending",
            }
        )
    if not project.live_url:
        tasks.append(
            {
                "title": "Add a demo, screenshots, or walkthrough",
                "priority": "medium",
                "status": "pending",
            }
        )
    tasks.extend(
        [
            {
                "title": "Document setup and architecture decisions",
                "priority": "medium",
                "status": "pending",
            },
            {
                "title": "Add tests for the most important behavior",
                "priority": "medium",
                "status": "pending",
            },
        ]
    )
    alignment = [target_role] if target_role else []
    return {
        "strengths": strengths,
        "weaknesses": [task["title"] for task in tasks if task["priority"] == "high"],
        "role_alignment": alignment,
        "tasks": tasks,
        "interview_talking_points": [
            "The user problem and why it mattered",
            "The hardest technical trade-off you actually made",
            "What you would improve with more time",
        ],
    }


def build_codex_prompt(project: PortfolioProject) -> str:
    return f"""Improve the presentation and engineering quality of this existing project.

Project: {project.name}
Description: {project.description}
Technology stack supplied by the owner: {', '.join(project.tech_stack) or 'not specified'}

Work from the repository's actual code and behavior.
Do not claim features, metrics, tests, deployment,
or architecture that are not present. Start by inspecting the repository and README, then propose a
small implementation plan. Prioritize: clear setup documentation, architecture explanation, focused
tests, accessible demo presentation, and honest limitations. Preserve existing behavior unless a
verified improvement requires a change.
"""
