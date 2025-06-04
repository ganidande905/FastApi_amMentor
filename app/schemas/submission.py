from pydantic import BaseModel
from typing import Optional
from datetime import date,datetime

class SubmissionBase(BaseModel):
    track_id: int
    task_no: int
    reference_link: str
    start_date: date
class SubmissionCreate(SubmissionBase):
    mentee_email: str


class SubmissionOut(BaseModel):
    id: int 
    mentee_id: int
    task_id: int
    reference_link: str
    status: str
    submitted_at: date
    approved_at: Optional[date] = None
    mentor_feedback: Optional[str] = None   
    start_date: date
    class Config:
        orm_mode = True

class SubmissionApproval(BaseModel):
    submission_id: int
    mentor_email: str
    status: str
    mentor_feedback: Optional[str] = None
    accepted: bool
    points_awarded: int

class PauseTask(BaseModel):
    task_no: int
    track_id: int
    mentee_email: str
    mentor_email: str

class TasksList(BaseModel):
    track_id: int
    mentee_id: str

class StartTask(BaseModel):
    mentee_email: str
    task_no: int
    track_id: int