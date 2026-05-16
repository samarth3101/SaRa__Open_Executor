from enum import Enum

class GoalStatus(str, Enum):
    active = "active"
    paused = "paused"
    completed = "completed"

class TaskStatus(str, Enum):
    pending = "pending"
    in_progress = "in_progress"
    completed = "completed"
    blocked = "blocked"

class PriorityLevel(int, Enum):
    low = 1
    medium = 2
    high = 3
