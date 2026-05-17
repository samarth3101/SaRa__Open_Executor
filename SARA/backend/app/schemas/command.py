from datetime import datetime, timezone

from pydantic import BaseModel, ConfigDict, field_serializer


class CommandHistoryRead(BaseModel):
    id: int
    user_id: int
    command_text: str
    intent: str
    summary: str | None
    source: str | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

    @field_serializer("created_at")
    def serialize_created_at(self, value: datetime) -> datetime:
        if value.tzinfo is None:
            value = value.replace(tzinfo=timezone.utc)
        return value.astimezone(timezone.utc)
