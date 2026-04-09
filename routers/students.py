from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
import models, schemas, database

router = APIRouter(prefix="/students", tags=["students"])

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()

@router.get("/", response_model=list[schemas.Student])
def get_students(db: Session = Depends(get_db)):
    return db.query(models.Student).all()

@router.post("/", response_model=schemas.Student)
def add_student(student: schemas.StudentCreate, db: Session = Depends(get_db)):
    new_student = models.Student(name=student.name, email=student.email)
    db.add(new_student)
    db.commit()
    db.refresh(new_student)
    return new_student
