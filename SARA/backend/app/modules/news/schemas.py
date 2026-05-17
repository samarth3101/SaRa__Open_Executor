from typing import List, Optional
from pydantic import BaseModel


class NewsArticle(BaseModel):
    title: str
    source: str
    url: str
    published_at: Optional[str] = None
    description: Optional[str] = None


class NewsSummaryResult(BaseModel):
    ok: bool
    source: str
    summary: str
    articles: List[NewsArticle]
    suggested_action: str
    estimated_time: str
    topic: Optional[str] = None
