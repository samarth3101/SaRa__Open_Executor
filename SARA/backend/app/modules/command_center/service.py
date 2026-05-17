import re
from sqlalchemy.orm import Session

from app.modules.command_center.schemas import CommandResponse, CommandCard
from app.db.models import Task, Goal, GmailToken, CommandHistory, User
from app.services.gmail_service import get_latest_emails
from app.modules.news.service import get_news_summary
from app.core.enums import GoalStatus, TaskStatus, PriorityLevel


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
        "goal",
        "goals",
        "progress",
        "milestone",
        "how am i doing",
        "overview",
        "status",
    ]
    add_goal_keywords = [
        "add goal",
        "create goal",
        "new goal",
        "set goal",
    ]
    add_task_keywords = [
        "add task",
        "create task",
        "new task",
        "add a task",
    ]

    if any(w in value for w in add_goal_keywords):
        return "add_goal"
    if any(w in value for w in add_task_keywords):
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


def create_command_history(
    db: Session,
    user_id: int,
    command_text: str,
    response: CommandResponse,
) -> None:
    history = CommandHistory(
        user_id=user_id,
        command_text=command_text,
        intent=response.intent,
        summary=response.summary,
        source=response.source,
    )
    db.add(history)
    db.commit()


def get_command_history_for_user(db: Session, user_id: int, limit: int = 100):
    return (
        db.query(CommandHistory)
        .filter(CommandHistory.user_id == user_id)
        .order_by(CommandHistory.created_at.desc())
        .limit(limit)
        .all()
    )


def extract_task_title(text: str) -> str:
    cleaned = text.strip()

    patterns = [
        r"^(add task)\s+",
        r"^(create task)\s+",
        r"^(new task)\s+",
        r"^(add a task)\s+",
    ]

    lowered = cleaned.lower()
    for pattern in patterns:
        match = re.match(pattern, lowered)
        if match:
            cleaned = cleaned[len(match.group(0)):].strip()
            break

    cleaned = cleaned.strip(" .:-")
    return cleaned


def extract_goal_title(text: str) -> str:
    cleaned = text.strip()

    patterns = [
        r"^(add goal)\s+",
        r"^(create goal)\s+",
        r"^(new goal)\s+",
        r"^(set goal)\s+",
    ]

    lowered = cleaned.lower()
    for pattern in patterns:
        match = re.match(pattern, lowered)
        if match:
            cleaned = cleaned[len(match.group(0)):].strip()
            break

    cleaned = cleaned.strip(" .:-")
    return cleaned


def infer_priority(text: str) -> PriorityLevel:
    lowered = text.lower()

    if any(word in lowered for word in ["urgent", "high priority", "important", "asap"]):
        return PriorityLevel.high
    if any(word in lowered for word in ["low priority", "later", "whenever"]):
        return PriorityLevel.low
    return PriorityLevel.medium


def infer_estimated_minutes(text: str) -> int | None:
    lowered = text.lower()

    minute_match = re.search(r"(\d+)\s*(min|mins|minute|minutes)\b", lowered)
    if minute_match:
        return int(minute_match.group(1))

    hour_match = re.search(r"(\d+)\s*(hr|hrs|hour|hours)\b", lowered)
    if hour_match:
        return int(hour_match.group(1)) * 60

    return None


def infer_goal_timeline(text: str) -> str | None:
    lowered = text.lower()

    if any(word in lowered for word in ["today", "tonight"]):
        return "Today"
    if "this week" in lowered:
        return "This week"
    if "this month" in lowered:
        return "This month"
    if any(word in lowered for word in ["quarter", "q1", "q2", "q3", "q4"]):
        return "This quarter"

    return None


def get_default_goal_for_user(db: Session, user_id: int) -> Goal | None:
    return (
        db.query(Goal)
        .filter(Goal.user_id == user_id, Goal.status == GoalStatus.active)
        .order_by(Goal.created_at.desc())
        .first()
    )


def get_any_goal_for_user(db: Session, user_id: int) -> Goal | None:
    return (
        db.query(Goal)
        .filter(Goal.user_id == user_id)
        .order_by(Goal.created_at.desc())
        .first()
    )


def handle_today_remaining(db: Session, user_id: int) -> CommandResponse:
    tasks = (
        db.query(Task)
        .join(Goal, Goal.id == Task.goal_id)
        .filter(Goal.user_id == user_id, Task.status != TaskStatus.completed)
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

    cards = [
        CommandCard(
            title=task.title,
            subtitle=f"Status: {task.status.value}",
            description=task.description,
            label="Task",
        )
        for task in tasks[:5]
    ]

    return CommandResponse(
        intent="today_remaining",
        summary=f"You have {len(tasks)} pending task(s).",
        priority_items=[task.title for task in tasks[:5]],
        suggested_next_action="start_highest_priority_task",
        source="database",
        estimated_minutes=2,
        cards=cards,
    )


def handle_goal_status(db: Session, user_id: int) -> CommandResponse:
    goals = (
        db.query(Goal)
        .filter(Goal.user_id == user_id, Goal.status == GoalStatus.active)
        .order_by(Goal.created_at.desc())
        .all()
    )

    if not goals:
        fallback_goal = get_any_goal_for_user(db, user_id)

        if fallback_goal:
            return CommandResponse(
                intent="goal_status",
                summary="No active goals found, but SaRa found an older goal in your workspace.",
                priority_items=[
                    fallback_goal.title,
                    fallback_goal.timeline or "No timeline set",
                ],
                suggested_next_action="Reactivate or review your latest goal.",
                source="local_db",
                estimated_minutes=1,
                cards=[
                    CommandCard(
                        title=fallback_goal.title,
                        subtitle=f"Timeline: {fallback_goal.timeline or 'Not set'}",
                        description=fallback_goal.description,
                        label="Existing goal",
                    )
                ],
            )

        return CommandResponse(
            intent="goal_status",
            summary="No goals found yet.",
            priority_items=[
                "Create your first goal",
                "Then add tasks under it",
            ],
            suggested_next_action="Create a goal to start tracking your progress.",
            source="local_db",
            estimated_minutes=1,
            cards=[],
        )

    cards = [
        CommandCard(
            title=g.title,
            subtitle=f"Timeline: {g.timeline or 'Not set'}",
            description=g.description,
            label="Goal",
        )
        for g in goals[:5]
    ]

    return CommandResponse(
        intent="goal_status",
        summary=f"You have {len(goals)} active goal(s).",
        priority_items=[f"{g.title} — {g.timeline or 'No timeline'}" for g in goals[:5]],
        suggested_next_action="Review progress on the top goal.",
        source="local_db",
        estimated_minutes=2,
        cards=cards,
    )


def handle_add_goal(db: Session, user_id: int, text: str) -> CommandResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        return CommandResponse(
            intent="add_goal",
            summary="SaRa could not create a goal because the user was not found.",
            priority_items=[],
            suggested_next_action="Create or load a valid user first.",
            source="system",
            estimated_minutes=1,
            cards=[],
        )

    title = extract_goal_title(text)
    if not title:
        return CommandResponse(
            intent="add_goal",
            summary="SaRa needs a goal title before creating a goal.",
            priority_items=[
                "Try: create goal ship SaRa MVP",
                "Try: add goal finish frontend polish this week",
            ],
            suggested_next_action="Rewrite the command with a clear goal title.",
            source="system",
            estimated_minutes=1,
            cards=[],
        )

    goal = Goal(
        user_id=user_id,
        title=title,
        description=f"Created from command: {text}",
        timeline=infer_goal_timeline(text),
        status=GoalStatus.active,
        intent_payload={"source_command": text},
    )

    db.add(goal)
    db.commit()
    db.refresh(goal)

    subtitle_parts = [
        f"Status: {goal.status.value}",
        f"Timeline: {goal.timeline or 'Not set'}",
    ]

    return CommandResponse(
        intent="add_goal",
        summary=f'Goal "{goal.title}" was created successfully.',
        priority_items=[
            goal.title,
            f"Timeline: {goal.timeline or 'Not set'}",
        ],
        suggested_next_action="Now add a task under this goal.",
        source="database",
        estimated_minutes=1,
        cards=[
            CommandCard(
                title=goal.title,
                subtitle=" · ".join(subtitle_parts),
                description=goal.description,
                label="Goal created",
            )
        ],
    )


def handle_add_task(db: Session, user_id: int, text: str) -> CommandResponse:
    title = extract_task_title(text)
    if not title:
        return CommandResponse(
            intent="add_task",
            summary="SaRa needs a task title before creating a task.",
            priority_items=[
                "Try: add task review landing page copy",
                "Try: create task fix gmail sync bug",
            ],
            suggested_next_action="Rewrite the command with a clear task title.",
            source="system",
            estimated_minutes=1,
            cards=[],
        )

    goal = get_default_goal_for_user(db, user_id)
    used_fallback_goal = False

    if not goal:
        goal = get_any_goal_for_user(db, user_id)
        used_fallback_goal = goal is not None

    if not goal:
        return CommandResponse(
            intent="add_task",
            summary=f'SaRa understood the task "{title}", but there is no goal available to attach it to yet.',
            priority_items=[
                f"Pending task request: {title}",
                "Create one goal first so SaRa can organize tasks properly.",
            ],
            suggested_next_action="Create a goal, then run the same add task command again.",
            source="system",
            estimated_minutes=1,
            cards=[
                CommandCard(
                    title=title,
                    subtitle="Task draft",
                    description="No goal exists yet, so SaRa could not save this task.",
                    label="Needs goal",
                )
            ],
        )

    task = Task(
        goal_id=goal.id,
        milestone_id=None,
        title=title,
        description=f"Created from command: {text}",
        priority=infer_priority(text),
        status=TaskStatus.pending,
        estimated_minutes=infer_estimated_minutes(text),
    )

    db.add(task)
    db.commit()
    db.refresh(task)

    subtitle_parts = [
        f"Goal: {goal.title}",
        f"Priority: {task.priority.value}",
    ]
    if task.estimated_minutes:
        subtitle_parts.append(f"Estimate: {task.estimated_minutes} min")
    if used_fallback_goal:
        subtitle_parts.append("Attached using fallback goal")

    priority_items = [
        f"{task.title} — {task.priority.value} priority",
        f"Attached to goal: {goal.title}",
    ]
    if used_fallback_goal:
        priority_items.append("No active goal was found, so SaRa used your most recent goal.")

    return CommandResponse(
        intent="add_task",
        summary=f'Task "{task.title}" was added successfully.',
        priority_items=priority_items,
        suggested_next_action="Review today_remaining to see the updated task queue.",
        source="database",
        estimated_minutes=1,
        cards=[
            CommandCard(
                title=task.title,
                subtitle=" · ".join(subtitle_parts),
                description=task.description,
                label="Task created",
            )
        ],
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

    cards = [
        CommandCard(
            title=email["subject"],
            subtitle=email["sender"],
            description=email.get("preview"),
            label="Email",
        )
        for email in emails[:5]
    ]

    joined = " ".join(f"{e['subject']} {e.get('preview', '')}".lower() for e in emails)
    suggested_action = "review"

    if any(
        word in joined
        for word in ["urgent", "asap", "reply", "approval", "action required", "meeting", "invoice"]
    ):
        suggested_action = "reply"

    senders = ", ".join(
        email["sender"].split("<")[0].strip().replace('"', "")
        for email in emails[:3]
    )

    return CommandResponse(
        intent="latest_emails",
        summary=f"You have {len(emails)} recent inbox emails. Top senders: {senders}.",
        priority_items=[f"{email['sender']} — {email['subject']}" for email in emails[:5]],
        suggested_next_action=suggested_action,
        source="gmail",
        estimated_minutes=5,
        cards=cards,
    )


def handle_news_summary(text: str) -> CommandResponse:
    result = get_news_summary(text)

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
        priority_items=[f"{article.source} — {article.title}" for article in result.articles[:5]],
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
            "Try: create goal ship SaRa MVP",
            "Try: add task review landing page copy",
            "Try: check latest emails",
            "Try: latest geopolitics news",
        ],
        suggested_next_action="Use one of the supported command formats above.",
        source="system",
        estimated_minutes=1,
        cards=[],
    )


def execute_command(db: Session, text: str, user_id: int) -> CommandResponse:
    intent = detect_intent(text)

    if intent == "today_remaining":
        response = handle_today_remaining(db, user_id)
    elif intent == "goal_status":
        response = handle_goal_status(db, user_id)
    elif intent == "add_goal":
        response = handle_add_goal(db, user_id, text)
    elif intent == "add_task":
        response = handle_add_task(db, user_id, text)
    elif intent == "latest_emails":
        response = handle_latest_emails(db, user_id)
    elif intent == "news_summary":
        response = handle_news_summary(text)
    else:
        response = handle_unknown()

    response.command_text = text
    create_command_history(
        db=db,
        user_id=user_id,
        command_text=text,
        response=response,
    )
    return response
