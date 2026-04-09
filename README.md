 EduTrack Backend (Alpha)

EduTrack is a learning project designed to manage students and courses.  
The backend is built with **FastAPI + PostgreSQL + SQLAlchemy**.

 Features
- CRUD operations for students (`/students`)
- CRUD operations for courses (`/courses`)
- Student enrollment in courses (`/enrollments`)
- Interactive API documentation via Swagger UI



 Project Structure
edutrack/
│─ main.py
│─ database.py
│─ models.py
│─ schemas.py
│─ routers/
│    ├─ students.py
│    ├─ courses.py
│    └─ enrollments.py
│─ README.md



 Installation & Setup (Local)

1. Clone the repository:
   ```bash
   git clone https://github.com/alibi0848487/EduTrack.git
   cd EduTrack
2. Create and activate a virtual environment:
   python -m venv .venv
    source .venv/bin/activate   # macOS
    .venv\Scripts\activate      # Windows
3. Install dependencies:
   pip install fastapi uvicorn sqlalchemy psycopg2-binary pydantic email-validator
4. Create a PostgreSQL database:
   CREATE DATABASE edutrack_db;
5. Update the connection string in database.py:
   DATABASE_URL = "postgresql://<username>:<password>@localhost:5432/edutrack_db"
6. Run the server:
   uvicorn main:app --reload
7. Open API docs:
   http://127.0.0.1:8000/docs
