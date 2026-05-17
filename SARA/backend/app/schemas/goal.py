from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import GoalStatus


class GoalCreate(BaseModel):
    user_id: int
    title: str
    description: str | None = None
    timeline: str | None = None
    intent_payload: dict | None = None


class GoalRead(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    timeline: str | None
    status: GoalStatus
    intent_payload: dict | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
