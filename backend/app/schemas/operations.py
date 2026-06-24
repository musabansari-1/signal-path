import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict


class BackgroundJobResponse(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    project_id: uuid.UUID | None
    job_type: str
    status: str
    payload_json: dict[str, Any]
    result_json: dict[str, Any]
    error_message: str | None
    created_at: datetime
    updated_at: datetime

