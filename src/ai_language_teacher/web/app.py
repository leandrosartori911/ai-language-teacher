from contextlib import closing
from pathlib import Path
from typing import Annotated
from urllib.parse import quote

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.progression import open_skills, unlocked_lessons
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import COURSES, PREREQUISITES
from ai_language_teacher.storage import (
    DEFAULT_DB_PATH,
    connect,
    list_students,
    load_student,
    save_student,
)

HERE = Path(__file__).parent


def course_mastery(student: Student, skill: str, lessons: list[Lesson]) -> float:
    # Unanswered items count as 0, unlike Student.skills (answered items only).
    knowledge = student.knowledge[skill]
    scores = [knowledge.get_score(item) for lesson in lessons for item in lesson.items]
    return sum(scores) / len(scores)


def create_app(db_path: str | Path = DEFAULT_DB_PATH) -> FastAPI:
    app = FastAPI(title="AI Language Teacher")
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")

    def home_page(request: Request, error: str | None = None, status_code: int = 200) -> Response:
        with closing(connect(db_path)) as conn:
            names = list_students(conn)
        return templates.TemplateResponse(
            request, "home.html", {"names": names, "error": error}, status_code=status_code
        )

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> Response:
        return home_page(request)

    @app.post("/students")
    def create_student(request: Request, name: Annotated[str, Form()] = "") -> Response:
        name = name.strip()
        if not name:
            return home_page(request, "Please enter a name.", 400)

        with closing(connect(db_path)) as conn:
            if load_student(conn, name) is None:
                save_student(conn, Student(name))
        return RedirectResponse(f"/students/{quote(name)}", status_code=303)

    # ":path" so a name containing "/" still matches this route.
    @app.get("/students/{name:path}", response_class=HTMLResponse)
    def dashboard(request: Request, name: str) -> Response:
        with closing(connect(db_path)) as conn:
            student = load_student(conn, name)
        if student is None:
            raise HTTPException(status_code=404, detail="No profile with that name")

        # Read-only page: open_skills/unlocked_lessons update the student in
        # memory, but nothing is saved here.
        opened = open_skills(student, COURSES, PREREQUISITES)
        skills = [
            {
                "name": skill,
                "open": skill in opened,
                "mastery": round(course_mastery(student, skill, lessons) * 100),
                "unlocked": len(unlocked_lessons(student, skill, lessons)),
                "total": len(lessons),
                "prerequisite": PREREQUISITES[skill],
            }
            for skill, lessons in COURSES.items()
        ]
        return templates.TemplateResponse(
            request, "dashboard.html", {"name": student.name, "skills": skills}
        )

    return app
