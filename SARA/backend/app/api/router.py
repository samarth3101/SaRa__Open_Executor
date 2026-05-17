from fastapi import APIRouter
from app.api.routes import (
    health,
    users,
    goals,
    milestones,
    tasks,
    graph,
    commands,
)
from app.api.routes import gmail

api_router = APIRouter()

api_router.include_router(health.router)
api_router.include_router(users.router)
api_router.include_router(goals.router)
api_router.include_router(milestones.router)
api_router.include_router(tasks.router)
api_router.include_router(graph.router)
api_router.include_router(commands.router)
api_router.include_router(gmail.router)