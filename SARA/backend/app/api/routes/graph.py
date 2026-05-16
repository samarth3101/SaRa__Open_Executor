from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, selectinload
from app.db.session import get_db
from app.db.models import Goal, Milestone
from app.schemas.graph import GoalGraphRead

router = APIRouter(prefix="/graph", tags=["Execution Graph"])

@router.get("/goals/{goal_id}", response_model=GoalGraphRead)
def get_goal_graph(goal_id: int, db: Session = Depends(get_db)):
    goal = (
        db.query(Goal)
        .options(
            selectinload(Goal.milestones).selectinload(Milestone.tasks),
            selectinload(Goal.tasks),
        )
        .filter(Goal.id == goal_id)
        .first()
    )

    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    return goal
