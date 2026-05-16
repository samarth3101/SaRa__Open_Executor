from datetime import datetime
from pydantic import BaseModel, ConfigDict
from app.core.enums import PriorityLevel, TaskStatus

class TaskCreate(BaseModel):
    goal_id: int
    milestone_id: int | None = None
    title: str
    description: str | None = None
    priority: PriorityLevel = PriorityLevel.medium
    estimated_minutes: int | None = None

class TaskUpdate(BaseModel):
    title: str | None = None
    description: str | None = None
    priority: PriorityLevel | None = None
    status: TaskStatus | None = None
    estimated_minutes: int | None = None

class TaskRead(BaseModel):
    id: int
    goal_id: int
    milestone_id: int | None
    title: str
    description: str | None
    priority: PriorityLevel
    status: TaskStatus
    estimated_minutes: int | None
    created_at: datetime

    model_config = ConfigDict(from_attributes=True)
