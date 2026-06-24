def build_job_parser_prompt(description: str) -> str:
    return f"""Extract structured requirements from this job description.
Every list item must be copied or minimally normalized from the description.
Do not add technologies, requirements, benefits, responsibilities, or concerns that are not present.
If data is absent, leave it empty and record the field name under missing_information.

JOB DESCRIPTION:
{description}
"""
