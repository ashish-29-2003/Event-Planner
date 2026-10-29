"""
Timeline and task management data models with strict input validation boundaries.
"""

from enum import Enum

from pydantic import BaseModel, ConfigDict, Field


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskItem(BaseModel):
    model_config = ConfigDict(extra="forbid")

    id: str = Field(..., min_length=1, max_length=64, description="Unique task ID")
    event_id: str | None = Field(None, max_length=64, description="Associated celebration ID")
    phase: str = Field(
        ..., min_length=2, max_length=64, description="Timeline phase (e.g. Phase 1: Foundation, Phase 5: Day-Of)"
    )
    title: str = Field(..., min_length=2, max_length=150, description="Actionable task headline")
    description: str = Field(..., min_length=2, max_length=1000, description="Logistical or ritual details")
    due_date: str | None = Field(None, min_length=8, max_length=12, description="Due date (YYYY-MM-DD)")
    owner_role: str = Field("Host", min_length=2, max_length=64, description="Assigned owner: Host, Family, Caterer, Decorator")
    priority: TaskPriority = Field(TaskPriority.MEDIUM)
    status: TaskStatus = Field(TaskStatus.TODO)
