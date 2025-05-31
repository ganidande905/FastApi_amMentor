from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import crud, models
from app.db.db import get_db
from app.schemas.submission import SubmissionCreate, SubmissionOut, SubmissionApproval, PauseTask, StartTask

router = APIRouter()

@router.post("/submit-task", response_model=SubmissionOut)
def submit_task(data: SubmissionCreate, db: Session = Depends(get_db)):
    # 1. Validate mentee
    mentee = crud.get_user_by_email(db, email=data.mentee_email)
    if not mentee or mentee.role != "mentee":
        raise HTTPException(status_code=403, detail="Invalid or missing mentee")

    # 2. Get task
    task = crud.get_task(db, track_id=data.track_id, task_no=data.task_no)
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")

    # 3. Submit
    submission = crud.submit_task(db, mentee_id=mentee.id, task_id=task.id, reference_link=data.reference_link, status = "submitted")
    if not submission:
        raise HTTPException(status_code=400, detail="Task already submitted")

    return submission

@router.patch("/approve-task", response_model=SubmissionOut)
def approve_task(data: SubmissionApproval, db: Session = Depends(get_db)):
    # 1. Validate mentor
    mentor = crud.get_user_by_email(db, data.mentor_email)
    if not mentor or mentor.role != "mentor":
        raise HTTPException(status_code=403, detail="Invalid or missing mentor")

    # 2. Validate submission
    sub = db.query(models.Submission).filter_by(id=data.submission_id).first()
    if not sub:
        raise HTTPException(status_code=404, detail="Submission not found")
    task = db.query(models.Tasks).filter_by(id=sub.task_id).first()
    points_storage = db.query(models.LeaderboardEntry).filter_by(track_id=sub.track_id, mentee_id=sub.mentee_id).first()

    # 3. Check if late and add points
    if sub.total_paused_time > task.deadline_days:
        points_storage.total_points += task.points/2
    else:
        points_storage.total_points += task.points
    db.commit()

    # 3. Confirm mentor is assigned to this mentee
    if not crud.is_mentor_of(db, mentor.id, sub.mentee_id):
        raise HTTPException(status_code=403, detail="Mentor not authorized for this mentee")

    # 4. Approve or pause
    updated = crud.approve_submission(
        db,
        submission_id=sub.id,
        mentor_feedback=data.mentor_feedback,
        status=data.status # approved, ongoing
    )
    return updated

@router.post("/pause-task", response_model=PauseTask)
def pause_task(data: PauseTask, db: Session = Depends(get_db)):
    mentor = crud.get_user_by_email(db, data.mentor_email)
    mentee = crud.get_user_by_email(db, email=data.mentee_email)
    if not crud.is_mentor_of(db, mentor.id, mentee.id):
        raise HTTPException(status_code=403, detail="Mentor not authorized for this mentee")
    task = crud.get_task(db, task_no=data.task_no, track_id=data.track_id)
    mentee_task_submission = db.query(models.Submission).filter_by(mentee_id=mentee, task=task).first()
    if mentee_task_submission.pause_start:
        return HTTPException(status_code=400, detail="This task is already paused")
    paused = crud.pause_task(mentee_task_submission.id)
    return paused

@router.post("/pause-end", response_model=PauseTask)
def end_pause(data: PauseTask, db: Session = Depends(get_db)):
    mentor = crud.get_user_by_email(db, data.mentor_email)
    mentee = crud.get_user_by_email(db, data.mentee_email)
    if not crud.is_mentor_of(db, mentor.id, mentee.id):
        return HTTPException(status_code=403, detail="Mentor not authorized for this mentee")
    task = crud.get_task(db, task_id=data.task_id)
    mentee_task_submission = db.query(models.Submission).filter_by(mentee_id=mentee, task_id=task).first()
    if mentee_task_submission.pause_start:
        return HTTPException(status_code=400, detail="This task is already paused")
    paused = crud.end_pause(mentee_task_submission.id)
    return paused

@router.post("/start-task", response_model=StartTask)
def start_task(data: StartTask, db: Session = Depends(get_db)):
    mentee = crud.get_user_by_email(email=data.mentee_email)
    task = crud.get_task(db, track_id=data.track_id, task_no=data.task_no)
    existing = crud.get_submission(db, mentee.email, task.track_id, task.task_no)
    if existing:
        return HTTPException(status_code=403, detail="Already Started")
    start = crud.start_task(task_id=task.id, mentee_id=mentee.id)
    return start