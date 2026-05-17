from sqlalchemy.orm import Session

from app.modules.command_center.schemas import CommandResponse, CommandCard
from app.db.models import Task, Goal, GmailToken
from app.services.gmail_service import get_latest_emails
from app.modules.news.service import get_news_summary
from app.core.enums import GoalStatus, TaskStatus


def detect_intent(text: str) -> str:
    value = text.lower().strip()

    today_keywords = [
        "remaining",
        "today",
        "what is left",
        "what's left",
        "pending tasks",
    ]
    email_keywords = [
        "latest emails",
        "latest email",
        "check email",
        "check my email",
        "inbox",
        "mail updates",
        "email",
        "mail",
        "messages",
        "unread",
    ]
    news_keywords = [
        "news",
        "news summary",
        "latest news",
        "headlines",
        "geopolitics",
        "world news",
        "tech news",
        "latest updates",
        "what's happening",
        "whats happening",
        "world",
        "current events",
    ]
    goal_keywords = [
        "goal", "goals", "progress", "milestone",
        "how am i doing", "overview", "status"
    ]
    add_keywords = ["add task", "create task", "new task", "add a task"]

    if any(w in value for w in add_keywords):
        return "add_task"
    if any(w in value for w in email_keywords):
        return "latest_emails"
    if any(w in value for w in news_keywords):
        return "news_summary"
    if any(w in value for w in goal_keywords):
        return "goal_status"
    if any(w in value for w in today_keywords):
        return "today_remaining"

    return "unknown"


def handle_today_remaining(db: Session, user_id: int) -> CommandResponse:
    tasks = (
        db.query(Task)
        .filter(Task.status != TaskStatus.completed)
        .order_by(Task.created_at.desc())
        .all()
    )

    if not tasks:
        return CommandResponse(
            intent="today_remaining",
            summary="You have no pending tasks right now.",
            priority_items=[],
            suggested_next_action="plan_next_goal",
            source="database",
            estimated_minutes=1,
            cards=[],
        )

    task_titles = [task.title for task in tasks[:5]]
    priority_items = task_titles

    cards = [
        CommandCard(
            title=task.title,
            subtitle=f"Status: {task.status}",
            description=getattr(task, "description", None),
            label="Task",
        )
        for task in tasks[:5]
    ]

    return CommandResponse(
        intent="today_remaining",
        summary=f"You have {len(tasks)} pending task(s).",
        priority_items=priority_items,
        suggested_next_action="start_highest_priority_task",
        source="database",
        estimated_minutes=2,
        cards=cards,
    )


def handle_goal_status(db: Session, user_id: int) -> CommandResponse:
    goals = db.query(Goal).filter(Goal.status == GoalStatus.active).all()

    if not goals:
        return CommandResponse(
            intent="goal_status",
            summary="No active goals found.",
            priority_items=[],
            suggested_next_action="Add a goal to start tracking your progress.",
            source="local_db",
            cards=[],
        )

    goal_list = [f"{g.title} — {g.timeline}" for g in goals]

    cards = [
        CommandCard(
            title=g.title,
            subtitle=f"Timeline: {g.timeline}",
            description=getattr(g, "description", None),
            label="Goal",
        )
        for g in goals[:5]
    ]

    return CommandResponse(
        intent="goal_status",
        summary=f"You have {len(goals)} active goal(s).",
        priority_items=goal_list,
        suggested_next_action="Review progress on the top goal",
        source="local_db",
        cards=cards,
    )


def handle_add_task(text: str) -> CommandResponse:
    return CommandResponse(
        intent="add_task",
        summary="Task creation via command is coming soon.",
        priority_items=["Use the task dashboard to add tasks for now."],
        suggested_next_action="Go to task dashboard and add your task manually.",
        source="system",
        cards=[],
    )


def handle_latest_emails(db: Session, user_id: int) -> CommandResponse:
    token_row = db.query(GmailToken).filter(GmailToken.user_id == user_id).first()

    if not token_row:
        return CommandResponse(
            intent="latest_emails",
            summary="Gmail is not connected yet.",
            priority_items=[],
            suggested_next_action="connect_gmail",
            source="gmail",
            estimated_minutes=1,
            cards=[],
        )

    emails = get_latest_emails(token_row, limit=5)

    if not emails:
        return CommandResponse(
            intent="latest_emails",
            summary="No recent important emails found.",
            priority_items=[],
            suggested_next_action="review",
            source="gmail",
            estimated_minutes=1,
            cards=[],
        )

    priority_items = [
        f"{email['sender']} — {email['subject']}"
        for email in emails[:5]
    ]

    cards = [
        CommandCard(
            title=email["subject"],
            subtitle=email["sender"],
            description=email.get("preview"),
            label="Email",
        )
        for email in emails[:5]
    ]

    joined = " ".join(f"{e['subject']} {e['preview']}".lower() for e in emails)
    suggested_action = "review"

    if any(word in joined for word in ["urgent", "asap", "reply", "approval", "action required", "meeting", "invoice"]):
        suggested_action = "reply"

    senders = ", ".join(
        email["sender"].split("<")[0].strip().replace('"', "")
        for email in emails[:3]
    )

    return CommandResponse(
        intent="latest_emails",
        summary=f"You have {len(emails)} recent inbox emails. Top senders: {senders}.",
        priority_items=priority_items,
        suggested_next_action=suggested_action,
        source="gmail",
        estimated_minutes=5,
        cards=cards,
    )


def handle_news_summary(text: str) -> CommandResponse:
    result = get_news_summary(text)

    article_lines = [
        f"{article.source} — {article.title}"
        for article in result.articles[:5]
    ]

    cards = [
        CommandCard(
            title=article.title,
            subtitle=article.source,
            description=article.description,
            url=article.url,
            label="News",
        )
        for article in result.articles[:5]
    ]

    return CommandResponse(
        intent="news_summary",
        summary=result.summary,
        priority_items=article_lines,
        suggested_next_action=result.suggested_action,
        source=result.source,
        estimated_minutes=1,
        cards=cards,
    )


def handle_unknown() -> CommandResponse:
    return CommandResponse(
        intent="unknown",
        summary="SaRa did not understand that command yet.",
        priority_items=[
            "Try: what's remaining today",
            "Try: check my goals",
            "Try: check latest emails",
            "Try: latest geopolitics news",
        ],
        suggested_next_action="Use one of the supported command formats above.",
        source="system",
        cards=[],
    )


def execute_command(db: Session, text: str, user_id: int) -> CommandResponse:
    intent = detect_intent(text)

    if intent == "today_remaining":
        response = handle_today_remaining(db, user_id)
    elif intent == "goal_status":
        response = handle_goal_status(db, user_id)
    elif intent == "add_task":
        response = handle_add_task(text)
    elif intent == "latest_emails":
        response = handle_latest_emails(db, user_id)
    elif intent == "news_summary":
        response = handle_news_summary(text)
    else:
        response = handle_unknown()

    response.command_text = text
    return response
