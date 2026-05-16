from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.session import get_db
from app.db.models import Goal, Milestone
from app.schemas.milestone import MilestoneCreate, MilestoneRead

router = APIRouter(prefix="/milestones", tags=["Milestones"])

@router.post("/", response_model=MilestoneRead)
def create_milestone(payload: MilestoneCreate, db: Session = Depends(get_db)):
    goal = db.query(Goal).filter(Goal.id == payload.goal_id).first()
    if not goal:
        raise HTTPException(status_code=404, detail="Goal not found")

    milestone = Milestone(
        goal_id=payload.goal_id,
        title=payload.title,
        description=payload.description,
        order_index=payload.order_index,
    )
    db.add(milestone)
    db.commit()
    db.refresh(milestone)
    return milestone

@router.get("/", response_model=list[MilestoneRead])
def list_milestones(db: Session = Depends(get_db)):
    return db.query(Milestone).order_by(Milestone.order_index.asc(), Milestone.id.asc()).all()
