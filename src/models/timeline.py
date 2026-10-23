"""
Timeline and task management data models.
"""

from enum import Enum

from pydantic import BaseModel, Field


class TaskPriority(str, Enum):
    HIGH = "high"
    MEDIUM = "medium"
    LOW = "low"


class TaskStatus(str, Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    DONE = "done"


class TaskItem(BaseModel):
    id: str = Field(..., description="Unique task ID")
    event_id: str | None = Field(None, description="Associated celebration ID")
    phase: str = Field(
        ..., description="Timeline phase (e.g. Phase 1: Foundation, Phase 5: Day-Of)"
    )
    title: str = Field(..., description="Actionable task headline")
    description: str = Field(..., description="Logistical or ritual details")
    due_date: str | None = Field(None, description="Due date (YYYY-MM-DD)")
    owner_role: str = Field("Host", description="Assigned owner: Host, Family, Caterer, Decorator")
    priority: TaskPriority = Field(TaskPriority.MEDIUM)
    status: TaskStatus = Field(TaskStatus.TODO)
