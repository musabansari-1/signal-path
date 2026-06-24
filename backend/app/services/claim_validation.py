import re
from dataclasses import dataclass
from typing import Any

from app.ai.schemas import GroundedText
from app.models.profile import CandidateProfile
from app.services.profile_analysis import KNOWN_TECH_SKILLS, normalize_evidence


@dataclass(frozen=True)
class ValidatedText:
    accepted: str | None
    facts: list[dict[str, Any]]
    warning: str | None


def fact_registry(profile: CandidateProfile) -> dict[str, dict[str, Any]]:
    return {
        str(fact.get("fact_id")): fact
        for fact in (profile.verified_facts_json or [])
        if fact.get("fact_id") and fact.get("verification") in {"source_quote", "user_confirmed"}
    }


def validate_grounded_text(
    item: GroundedText,
    profile: CandidateProfile,
    allowed_context: list[str] | None = None,
) -> ValidatedText:
    registry = fact_registry(profile)
    referenced = [registry[fact_id] for fact_id in item.fact_ids if fact_id in registry]
    text = item.text.strip()
    if not text:
        return ValidatedText(None, [], "An empty generated item was removed")
    if item.fact_ids and len(referenced) != len(set(item.fact_ids)):
        return ValidatedText(None, referenced, "A claim cited missing or unverified evidence")

    evidence = " ".join(str(fact.get("value", "")) for fact in referenced)
    evidence_normalized = normalize_evidence(evidence)
    _ = allowed_context
    numbers = re.findall(r"\b\d+(?:[.,]\d+)?%?\b", text)
    unsupported_numbers = [
        number for number in numbers if number.casefold() not in evidence_normalized
    ]
    if unsupported_numbers:
        return ValidatedText(None, referenced, "A generated claim introduced an unsupported number")

    confirmed_skills = {skill.casefold() for skill in (profile.skills_json or [])}
    mentioned_skills = {
        skill.casefold()
        for skill in KNOWN_TECH_SKILLS
        if re.search(rf"(?<![\w+#-]){re.escape(skill.casefold())}(?![\w+#-])", text.casefold())
    }
    if mentioned_skills - confirmed_skills:
        return ValidatedText(None, referenced, "A generated claim introduced an unconfirmed skill")

    if referenced:
        significant = {
            token
            for token in re.findall(r"[a-z0-9+#.]+", evidence_normalized)
            if len(token) >= 3
        }
        text_tokens = set(re.findall(r"[a-z0-9+#.]+", normalize_evidence(text)))
        if significant and not significant.intersection(text_tokens):
            return ValidatedText(
                None, referenced, "A claim did not visibly connect to its cited fact"
            )
    else:
        return ValidatedText(None, [], "A candidate claim had no verified evidence")

    return ValidatedText(text, referenced, None)
