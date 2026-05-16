from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.modules.command_center.schemas import CommandRequest, CommandResponse
from app.modules.command_center.service import execute_command

router = APIRouter(prefix="/commands", tags=["commands"])


@router.post("/execute", response_model=CommandResponse)
def run_command(payload: CommandRequest, db: Session = Depends(get_db)):
    return execute_command(db=db, text=payload.text, user_id=payload.user_id)
