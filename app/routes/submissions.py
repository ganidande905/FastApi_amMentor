from fastapi import APIRouter, Depends, Query, HTTPException
from sqlalchemy.orm import Session
from typing import List, Optional
from app.db.db import get_db
from app.db import crud
from app.schemas import submission
from app.schemas.submission import SubmissionOut
from app.db.crud import get_submissions_for_user
router = APIRouter()


@router.get("/", response_model=List[SubmissionOut])
def get_submissions(
    email: str = Query(...),
    track_id: Optional[int] = Query(None),
    db: Session = Depends(get_db)
):
    submissions = get_submissions_for_user(db, email, track_id)

    if not submissions:
        raise HTTPException(status_code=404, detail="No submissions found")
    print("DEBUG: Type of returned object:", type(submissions[0]))
    return submissions