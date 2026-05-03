# Edutrack

### 1. Project Title  
**EduTrack - Online Education Management Platform**

### 2. Topic Area  
**Education Technology (EdTech)**

### 3. Problem Statement  
1 Students and instructors struggle to manage courses, assignments, and progress in a unified system.  
2 Existing platforms are often overloaded and not adapted to local needs.  
3 Lack of transparent analytics prevents administrators from making informed decisions.  
4 A simple, user‑friendly platform for managing education is needed.  

### 4. Proposed Solution  
EduTrack provides a web application where students can register, take courses, and track progress, while instructors manage content and administrators access analytics.  

### 5. Target Users  
 Students  
 Instructors  
 Academic administrators  

### 6. Technology Stack  
 **Frontend:** HTML, CSS, JavaScript  
 **Backend:** FastAPI (Python)  
 **Database:** PostgreSQL (Render PostgreSQL Service)  
 **Cloud / Hosting:** Render  
 **APIs / Integrations:** SQLAlchemy ORM, Alembic migrations  
 **Other Tools:** GitHub, Docker (optional)  

### 7. Key Features  
 User registration and authentication  
 Course management (CRUD operations)  
 Student progress tracking  
 Admin dashboard with analytics  

### 8. Team Members   
 Alibek - Developer - 230103020@sdu.edu.kz  
 Yerasyl Aman - Backend developer - 230103052@sdu.edu.kz
 Toletay Amir - Project manger - 230103142@sdu.edu.kz

### 9. Expected Outcome  
A working web application with a connected database, deployed on Render, supporting basic course and user management features.  

### 10. Structure

edutrack/
├── app/              # FastAPI бэкенд
│   ├── routers/      # auth, users, lessons, matches, challenges, leaderboard
│   ├── models/       # SQLAlchemy модели
│   ├── schemas/      # Pydantic схемы
│   └── core/         # database, security, config
├── static/           # Фронтенд (index.html)
├── migrations/       # Alembic
├── Dockerfile
└── docker-compose.yml

### 11. Git Repo Link (GitHub/GitLab)  
`https://github.com/username/edutrack-full`
