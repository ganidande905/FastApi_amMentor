from sqlalchemy.orm import Session
from app.db import models
from datetime import datetime, date, timedelta

def get_user_by_email(db: Session, email: str):
    return db.query(models.User).filter(models.User.email == email).first()

def get_task(db: Session, track_id: int, task_no: int):
    return db.query(models.Task).filter_by(track_id=track_id, task_no=task_no).first()

def submit_task(db: Session, mentee_id: int, task_id: int, reference_link: str):
    submission = db.query(models.Submission).filter_by(mentee_id=mentee_id, task_id=task_id).first()
    submission.status = "Submitted"
    submission.submitted_at = datetime.now()
    submission.reference_link = reference_link
    db.commit()
    db.refresh(submission)
    return submission

def approve_submission(db: Session, submission_id: int, mentor_feedback: str, status: str):
    sub = db.query(models.Submission).filter_by(id=submission_id).first()
    if not sub:
        return None

    sub.status = status
    sub.mentor_feedback = mentor_feedback
    if status == "approved":
        sub.approved_at = datetime.now()

    db.commit()
    db.refresh(sub)
    return sub

def is_mentor_of(db: Session, mentor_id: int, mentee_id: int):
    return db.query(models.MentorMenteeMap).filter_by(mentor_id=mentor_id, mentee_id=mentee_id).first() is not None

def get_leaderboard_data(db: Session, track_id: int):
    from sqlalchemy import func
    return (
        db.query(
            models.User.name,
            func.sum(models.Task.points).label("total_points"),
            func.count(models.Submission.id).label("tasks_completed")
        )
        .join(models.Submission, models.Submission.mentee_id == models.User.id)
        .join(models.Task, models.Submission.task_id == models.Task.id)
        .filter(models.Submission.status == "approved")
        .filter(models.Task.track_id == track_id)
        .group_by(models.User.id)
        .order_by(func.sum(models.Task.points).desc())
        .all()
    )
def get_otp_by_email(db, email):
    return db.query(models.OTP).filter(models.OTP.email == email).first()

def create_or_update_otp(db, email, otp, expires_at):
    entry = get_otp_by_email(db, email)
    if entry:
        entry.otp = otp
        entry.expires_at = expires_at
    else:
        entry = models.OTP(email=email, otp=otp, expires_at=expires_at)
        db.add(entry)
    db.commit()

def pause_task(db: Session, submission: int):
    pause_row=db.query(models.Submission).filter_by(id=submission).first()
    pause_row.pause=datetime.now()
    pause_row.status = "paused"
    db.commit()
    db.refresh()
    return pause_row

def end_pause(db: Session, submission: int):
    pause_row=db.query(models.Submission).filter_by(id=submission).first()
    pause_row.total_paused_time+= datetime.combine(date.today(), datetime.now()) - datetime.combine(date.today(), pause_row.pause_start)
    pause_row.status = "ongoing"
    db.commit()
    db.refresh()
    return pause_row

def get_otp_by_email(db, email):
    return db.query(models.OTP).filter(models.OTP.email == email).first()

def create_or_update_otp(db, email, otp, expires_at):
    entry = get_otp_by_email(db, email)
    if entry:
        entry.otp = otp
        entry.expires_at = expires_at
    else:
        entry = models.OTP(email=email, otp=otp, expires_at=expires_at)
        db.add(entry)
    db.commit()

def start_task(db: Session, task_id: int, mentee_id: int):
    task_start = models.Submission(
        mentee_id = mentee_id,
        task_id = task_id,
        start_date = datetime.now(),
        status = "ongoing"
    )
    db.add(task_start)
    db.commit()
    db.refresh(task_start)
    return task_start

def find_time_spent_on_task(db: Session, submission: int):
    submission = db.query(models.Submission).filter_by(id=submission).first()
    if submission.submitted_at:
        time_spent = (submission.submitted_at - submission.start_date - timedelta(submission.total_paused_time)).days
    else:
        time_spent = (datetime.now() - submission.start_date - timedelta(submission.total_paused_time)).days
    return time_spent

def get_submission(db: Session, mentee_email: str, track_id: int, task_no: int):
    mentee = get_user_by_email(mentee_email)
    return db.query(models.Submission).filter_by(mentee_email=mentee.id, track_id=track_id, task_no=task_no)
