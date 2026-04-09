from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas, database

router = APIRouter(prefix="/enrollments", tags=["enrollments"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.post("/", response_model=schemas.Enrollment)
def enroll(enrollment: schemas.EnrollmentBase, db: Session = Depends(get_db)):
    new_enroll = models.Enrollment(student_id=enrollment.student_id, course_id=enrollment.course_id)
    db.add(new_enroll)
    db.commit()
    db.refresh(new_enroll)
    return new_enroll

@router.get("/", response_model=list[schemas.Enrollment])
def get_enrollments(db: Session = Depends(get_db)):
    return db.query(models.Enrollment).all()
