from typing import List, Literal, Optional
from pydantic import BaseModel

CommandIntent = Literal[
    "today_remaining",
    "latest_emails",
    "news_summary",
    "goal_status",
    "add_task",
    "unknown",
]


class CommandCard(BaseModel):
    title: str
    subtitle: Optional[str] = None
    description: Optional[str] = None
    url: Optional[str] = None
    label: Optional[str] = None


class CommandRequest(BaseModel):
    text: str
    user_id: int = 1


class CommandResponse(BaseModel):
    intent: CommandIntent
    summary: str
    priority_items: List[str]
    suggested_next_action: str
    source: str
    estimated_minutes: Optional[int] = None
    command_text: Optional[str] = None
    cards: List[CommandCard] = []
