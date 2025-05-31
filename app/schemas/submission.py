from pydantic import BaseModel
from typing import Optional
from datetime import datetime

class SubmissionBase(BaseModel):
    track_id: int
    task_no: int
    reference_link: str

class SubmissionCreate(SubmissionBase):
    mentee_email: str

class SubmissionOut(BaseModel):
    id: int 
    mentee_id: int
    task_id: int
    reference_link: str
    status: str
    submitted_at: datetime
    approved_at: Optional[datetime] = None
    mentor_feedback: Optional[str] = None

    class Config:
        orm_mode = True

class SubmissionApproval(BaseModel):
    submission_id: int
    mentor_email: str
    status: str
    mentor_feedback: Optional[str] = None

class PauseTask(BaseModel):
    submission_id: int
    pause_start: datetime
    task_no: int
    track_id: int
    mentee_email: str
    mentor_email: str

class TasksList(BaseModel):
    track_id: int
    mentee_id: str

class StartTask(BaseModel):
    mentee_email: int
    task_no: int
    track_id: int