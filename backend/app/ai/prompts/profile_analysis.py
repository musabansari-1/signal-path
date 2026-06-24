from app.models.profile import CareerAsset


def build_profile_analysis_prompt(assets: list[CareerAsset]) -> str:
    sources = []
    for asset in assets:
        sources.append(
            f"SOURCE ASSET ID: {asset.id}\nTITLE: {asset.title}\n"
            f"CONTENT:\n{asset.extracted_text or ''}"
        )
    return """Create a structured candidate profile from the sources below.
Keep the summary conservative. A strength or best-fit role may be a suggestion,
but factual claims must each use an exact quote copied from one source.
Do not turn job aspirations into candidate experience.

""" + "\n\n---\n\n".join(sources)
