from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.schemas.command import CommandHistoryRead
from app.modules.command_center.schemas import CommandRequest, CommandResponse
from app.modules.command_center.service import execute_command, get_command_history_for_user

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/execute", response_model=CommandResponse)
def run_command(payload: CommandRequest, db: Session = Depends(get_db)):
    return execute_command(db=db, text=payload.text, user_id=payload.user_id)


@router.get("/history/{user_id}", response_model=list[CommandHistoryRead])
def get_command_history(
    user_id: int,
    limit: int = Query(default=100, ge=1, le=500),
    db: Session = Depends(get_db),
):
    return get_command_history_for_user(db=db, user_id=user_id, limit=limit)
