from pydantic import BaseModel
from typing import Optional

class TrackBase(BaseModel):
    title: str
    description: Optional[str] = None

class TrackCreate(TrackBase):
    pass

class TrackOut(TrackBase):
    id: int

    class Config:
        orm_mode = True

class TaskOut(BaseModel):
    task_no: int
    title: str
    points: int
    deadline: int
    status: str
    time_spent: int
    description: str
    track: str

class MenteeTasks(BaseModel):
    mentee_email: str
    task_no: int
    track_id: int