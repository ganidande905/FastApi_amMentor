from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import models
from app.db.db import get_db
from app.schemas.track import TrackOut, MenteeTasks
from app.schemas.task import TaskOut
from app.db import crud

router = APIRouter()

@router.get("/", response_model=list[TrackOut])
def list_tracks(db: Session = Depends(get_db)):
    return db.query(models.Track).all()

@router.get("/{track_id}/tasks", response_model=list[TaskOut])
def mentee_specific_status(track_id: int, mentee_email: str, db: Session = Depends(get_db)):
    tasks = db.query(models.Task).filter_by(track_id=track_id).order_by(models.Task.task_no).all()
    mentee = crud.get_user_by_email(db, mentee_email)
    tasks_with_status=[]
    for task in tasks:
        submission_of_task = db.query(models.Submission).filter_by(task_id=task.id, mentee_id=mentee.id).first()
        if submission_of_task:
            status = submission_of_task.status
            time_spent = crud.find_time_spent_on_task(submission_of_task.id)
        else:
            status = "Not started"
            time_spent = 0
        tasks_with_status.append(
            {
            "task_no": task.task_no,
            "title": task.title,
            "points": task.points,
            "deadline": task.deadline_days,
            "status": status,
            "time_spent": time_spent,
            "description": task.description,
            "track": task.track.title
            }
        )
    return tasks_with_status