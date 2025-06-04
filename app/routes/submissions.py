from typing import Optional
from fastapi import APIRouter, Depends, HTTPException , Query
from sqlalchemy.orm import Session
from app.db import crud
from app.db.db import get_db
from app.schemas.submission import SubmissionOut

router = APIRouter()

@router.get("/", response_model=list[SubmissionOut])
def get_submissions(
    email: str = Query(...), 
    track_id: Optional[int] = Query(None), 
    db: Session = Depends(get_db)
):
    submissions = crud.get_submissions(db, email, track_id,)
    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found")
    return submissions