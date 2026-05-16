from sqlalchemy.orm import Session

from app.modules.command_center.schemas import CommandResponse
from app.db.models import Task


def detect_intent(text: str) -> str:
    value = text.lower()

    if any(word in value for word in ["today", "remaining", "left", "pending"]):
        return "today_remaining"
    if any(word in value for word in ["email", "mail", "inbox"]):
        return "latest_emails"
    if any(word in value for word in ["news", "geopolitics", "latest updates"]):
        return "news_summary"
    return "unknown"


def handle_today_remaining(db: Session, user_id: int) -> CommandResponse:
    tasks = (
        db.query(Task)
        .filter(Task.status != "completed")
        .order_by(Task.created_at.asc())
        .all()
    )

    if not tasks:
        return CommandResponse(
            intent="today_remaining",
            summary="You have no pending tasks right now.",
            priority_items=[],
            suggested_next_action="Add a new task or plan your next milestone.",
            source="local_db",
        )

    titles = [task.title for task in tasks[:5]]

    return CommandResponse(
        intent="today_remaining",
        summary=f"You have {len(tasks)} pending task(s) right now.",
        priority_items=titles,
        suggested_next_action=f"Start with: {titles[0]}",
        source="local_db",
    )


def handle_latest_emails() -> CommandResponse:
    return CommandResponse(
        intent="latest_emails",
        summary="Email integration is not connected yet.",
        priority_items=["Mail connector will be added in the next step."],
        suggested_next_action="For now, finish Command Center integration first.",
        source="mock",
    )


def handle_news_summary() -> CommandResponse:
    return CommandResponse(
        intent="news_summary",
        summary="News integration is not connected yet.",
        priority_items=["Multi-source news summarization will be added after command routing works."],
        suggested_next_action="First complete the typed command flow.",
        source="mock",
    )


def handle_unknown() -> CommandResponse:
    return CommandResponse(
        intent="unknown",
        summary="I could not understand that command yet.",
        priority_items=[
            "Try: what's remaining today",
            "Try: check latest emails",
            "Try: latest geopolitics news"
        ],
        suggested_next_action="Use one of the supported command formats.",
        source="system",
    )


def execute_command(db: Session, text: str, user_id: int) -> CommandResponse:
    intent = detect_intent(text)

    if intent == "today_remaining":
        return handle_today_remaining(db, user_id)
    if intent == "latest_emails":
        return handle_latest_emails()
    if intent == "news_summary":
        return handle_news_summary()
    return handle_unknown()
