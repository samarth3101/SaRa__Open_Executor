from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import GoalStatus, PriorityLevel, TaskStatus

class GraphTaskRead(BaseModel):
    id: int
    milestone_id: int | None
    title: str
    description: str | None
    priority: PriorityLevel
    status: TaskStatus
    estimated_minutes: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)

class GraphMilestoneRead(BaseModel):
    id: int
    title: str
    description: str | None
    order_index: int
    created_at: datetime
    tasks: list[GraphTaskRead] = []

    model_config = ConfigDict(from_attributes=True)

class GoalGraphRead(BaseModel):
    id: int
    user_id: int
    title: str
    description: str | None
    timeline: str | None
    status: GoalStatus
    intent_payload: dict | None
    created_at: datetime
    milestones: list[GraphMilestoneRead] = []
    tasks: list[GraphTaskRead] = []

    model_config = ConfigDict(from_attributes=True)
