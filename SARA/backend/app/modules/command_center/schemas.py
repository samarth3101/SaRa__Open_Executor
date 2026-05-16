from typing import List, Literal
from pydantic import BaseModel


CommandIntent = Literal["today_remaining", "latest_emails", "news_summary", "unknown"]


class CommandRequest(BaseModel):
    text: str
    user_id: int = 1


class CommandResponse(BaseModel):
    intent: CommandIntent
    summary: str
    priority_items: List[str]
    suggested_next_action: str
    source: str
