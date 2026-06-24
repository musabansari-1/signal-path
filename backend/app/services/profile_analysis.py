import hashlib
import re
from datetime import UTC, datetime

from app.ai.client import AIUnavailableError, ai_client
from app.ai.prompts.profile_analysis import build_profile_analysis_prompt
from app.ai.schemas import CandidateProfileExtraction, EvidenceClaim
from app.models.profile import CandidateProfile, CareerAsset

KNOWN_TECH_SKILLS = (
    "Python", "Java", "JavaScript", "TypeScript", "React", "Next.js", "Node.js",
    "FastAPI", "Django", "Flask", "SQL", "PostgreSQL", "MySQL", "MongoDB", "Redis",
    "AWS", "Azure", "GCP", "Docker", "Kubernetes", "Git", "GraphQL", "REST",
    "Tailwind CSS", "C++", "C#", "Go", "Rust", "Spring Boot",
)


def normalize_evidence(value: str) -> str:
    return re.sub(r"\s+", " ", value).strip().casefold()


def fact_id(category: str, value: str, source: str | None) -> str:
    payload = f"{category}|{normalize_evidence(value)}|{source or 'user'}"
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()[:20]


def deterministic_extraction(assets: list[CareerAsset]) -> CandidateProfileExtraction:
    claims: list[EvidenceClaim] = []
    for asset in assets:
        text = asset.extracted_text or ""
        normalized = text.casefold()
        for skill in KNOWN_TECH_SKILLS:
            if re.search(rf"(?<![\w+#-]){re.escape(skill.casefold())}(?![\w+#-])", normalized):
                claims.append(
                    EvidenceClaim(
                        category="skill",
                        value=skill,
                        source_asset_id=asset.id,
                        evidence_quote=skill,
                    )
                )
    unique = {claim.value.casefold(): claim for claim in claims}
    return CandidateProfileExtraction(
        claims=list(unique.values()),
        suggestions=["Add a concise headline and confirm your strongest recent achievements."],
        missing_information_questions=[
            "Which outcomes or metrics from your work can you verify?",
            "Which roles are you targeting next?",
        ],
    )


def analyze_assets(
    assets: list[CareerAsset],
) -> tuple[CandidateProfileExtraction, list[dict[str, object]]]:
    try:
        extraction = ai_client.generate_structured(
            build_profile_analysis_prompt(assets), CandidateProfileExtraction
        )
    except (AIUnavailableError, ValueError):
        extraction = deterministic_extraction(assets)

    by_id = {asset.id: asset for asset in assets}
    verified: list[dict[str, str]] = []
    rejected: list[dict[str, str]] = []
    for claim in extraction.claims:
        source = by_id.get(claim.source_asset_id)
        evidence = normalize_evidence(claim.evidence_quote)
        source_text = normalize_evidence(source.extracted_text or "") if source else ""
        record = {
            "fact_id": fact_id(claim.category, claim.value, str(claim.source_asset_id)),
            "category": claim.category,
            "value": claim.value,
            "source_asset_id": str(claim.source_asset_id),
            "evidence_quote": claim.evidence_quote,
            "verification": "source_quote",
        }
        if source and len(evidence) >= 2 and evidence in source_text:
            verified.append(record)
        else:
            rejected.append({**record, "reason": "Evidence quote was not found in the source"})
    return extraction, verified + [{"rejected_claim": item} for item in rejected]


def apply_analysis(
    profile: CandidateProfile,
    extraction: CandidateProfileExtraction,
    verification_records: list[dict[str, object]],
) -> None:
    verified = [record for record in verification_records if "rejected_claim" not in record]
    rejected = [
        record["rejected_claim"]
        for record in verification_records
        if "rejected_claim" in record
    ]
    profile.headline = extraction.headline
    profile.summary = extraction.summary
    profile.skills_json = sorted(
        {str(fact["value"]) for fact in verified if fact["category"] == "skill"},
        key=str.casefold,
    )
    profile.verified_facts_json = verified
    profile.strengths_json = extraction.strengths
    profile.gaps_json = extraction.gaps
    profile.best_fit_roles_json = extraction.best_fit_roles
    profile.suggestions_json = [
        *({"type": "suggestion", "text": item} for item in extraction.suggestions),
        *({"type": "question", "text": item} for item in extraction.missing_information_questions),
        *({"type": "rejected_claim", **item} for item in rejected),
    ]
    profile.reviewed_at = None


def mark_profile_reviewed(profile: CandidateProfile) -> None:
    profile.reviewed_at = datetime.now(UTC).isoformat()
