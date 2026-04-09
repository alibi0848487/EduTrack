from fastapi import FastAPI
import models, database
from routers import students, courses, enrollments
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

models.Base.metadata.create_all(bind=database.engine)

app.include_router(students.router)
app.include_router(courses.router)
app.include_router(enrollments.router)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)
