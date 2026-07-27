import json
from typing import TypeVar

import httpx
from pydantic import BaseModel

from app.core.config import settings

ResponseModel = TypeVar("ResponseModel", bound=BaseModel)

TRUTHFUL_SYSTEM_RULES = """You are a careful career strategy assistant.
Use only facts explicitly present in the supplied candidate sources.
Never invent or infer experience,
companies, dates, degrees, metrics, achievements, tools, certifications, or employment history.
Every factual candidate claim must include an exact evidence quote and its source asset id.
If support is missing, put the item in suggestions or missing information instead of claims.
Return only valid JSON matching the supplied schema."""


class AIUnavailableError(RuntimeError):
    pass


class AIClient:
    def __init__(self) -> None:
        self.api_key = settings.llm_api_key
        self.base_url = settings.llm_base_url.rstrip("/")
        self.model = settings.llm_model

    @property
    def available(self) -> bool:
        return bool(self.api_key)

    def generate_structured(
        self,
        prompt: str,
        response_model: type[ResponseModel],
        system: str = TRUTHFUL_SYSTEM_RULES,
    ) -> ResponseModel:
        if not self.api_key:
            raise AIUnavailableError("No AI provider is configured")
        schema = json.dumps(response_model.model_json_schema(), ensure_ascii=False)
        response = httpx.post(
            f"{self.base_url}/chat/completions",
            headers={
                "Authorization": f"Bearer {self.api_key}",
                "HTTP-Referer": settings.openrouter_http_referer or settings.frontend_url,
                "X-OpenRouter-Title": settings.openrouter_x_openrouter_title
                or settings.app_name,
                "X-OpenRouter-Metadata": "enabled",
            },
            json={
                "model": self.model,
                "temperature": 0,
                "response_format": {"type": "json_object"},
                "messages": [
                    {"role": "system", "content": f"{system}\nJSON schema:\n{schema}"},
                    {"role": "user", "content": prompt},
                ],
            },
            timeout=60,
        )
        response.raise_for_status()
        content = response.json()["choices"][0]["message"]["content"]
        return response_model.model_validate_json(content)


ai_client = AIClient()
