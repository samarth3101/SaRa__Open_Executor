from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.db.models import CommandHistory
from app.modules.command_center.schemas import CommandRequest, CommandResponse
from app.modules.command_center.service import execute_command

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/execute", response_model=CommandResponse)
def run_command(payload: CommandRequest, db: Session = Depends(get_db)):
    result = execute_command(db=db, text=payload.text, user_id=payload.user_id)

    history = CommandHistory(
        user_id=payload.user_id,
        command_text=payload.text,
        intent=result.intent,
        summary=result.summary,
        source=result.source,
    )
    db.add(history)
    db.commit()

    return result


@router.get("/history/{user_id}")
def get_command_history(user_id: int, db: Session = Depends(get_db)):
    records = (
        db.query(CommandHistory)
        .filter(CommandHistory.user_id == user_id)
        .order_by(CommandHistory.created_at.desc())
        .limit(20)
        .all()
    )
    return records
