from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import Goal, User
from app.schemas.goal import GoalCreate, GoalRead

router = APIRouter(prefix="/goals", tags=["Goals"])


@router.post("/", response_model=GoalRead)
def create_goal(payload: GoalCreate, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    goal = Goal(
        user_id=payload.user_id,
        title=payload.title,
        description=payload.description,
        timeline=payload.timeline,
        intent_payload=payload.intent_payload,
    )
    db.add(goal)
    db.commit()
    db.refresh(goal)
    return goal


@router.get("/", response_model=list[GoalRead])
def list_goals(db: Session = Depends(get_db)):
    return db.query(Goal).order_by(Goal.id.desc()).all()
