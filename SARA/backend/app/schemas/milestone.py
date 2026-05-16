from datetime import datetime
from pydantic import BaseModel, ConfigDict

class MilestoneCreate(BaseModel):
    goal_id: int
    title: str
    description: str | None = None
    order_index: int = 1

class MilestoneRead(BaseModel):
    id: int
    goal_id: int
    title: str
    description: str | None
    order_index: int
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
