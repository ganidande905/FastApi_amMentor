from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class TaskBase(BaseModel):
    track_id: int
    task_no: int
    title: str
    description: Optional[str] = None
    points: int = 10
    deadline_days: Optional[datetime] = None 

class TaskCreate(TaskBase):
    pass

class TaskOut(BaseModel):
    id: int
    track_id: int
    task_no: int
    title: str
    description: Optional[str]
    points: int
    deadline: Optional[int]

    class Config:
        orm_mode = True

    @classmethod
    def from_orm(cls, obj):
        return cls(
            id=obj.id,
            track_id=obj.track_id,
            task_no=obj.task_no,
            title=obj.title,
            description=obj.description,
            points=obj.points,
            deadline=obj.deadline_days
        )