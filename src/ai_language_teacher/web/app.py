import sqlite3
from collections.abc import Awaitable, Callable
from contextlib import closing
from datetime import date
from pathlib import Path
from typing import Annotated, Any
from urllib.parse import quote

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import HTMLResponse, PlainTextResponse, RedirectResponse, Response
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.middleware.trustedhost import TrustedHostMiddleware

from ai_language_teacher.core.assessment import Assessment, AssessmentResult
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.progression import open_skills, unlocked_lessons
from ai_language_teacher.core.question import Question
from ai_language_teacher.core.review import (
    learned_items,
    record_answer,
    record_practice,
    study_queue,
)
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
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]


def course_mastery(student: Student, skill: str, lessons: list[Lesson]) -> float:
    # Unanswered items count as 0, unlike Student.skills (answered items only).
    knowledge = student.knowledge[skill]
    scores = [knowledge.get_score(item) for lesson in lessons for item in lesson.items]
    return sum(scores) / len(scores)


def lesson_of(lessons: list[Lesson], item: str) -> Lesson:
    return next(lesson for lesson in lessons if item in lesson.items)


def question_of(lesson: Lesson, item: str) -> Question:
    return next(question for question in lesson.questions if question.item == item)


def evaluate(skill: str, item: str, answer: str) -> AssessmentResult:
    question = question_of(lesson_of(COURSES[skill], item), item)
    return Assessment.from_question(skill, question).evaluate(answer)


def create_app(
    db_path: str | Path = DEFAULT_DB_PATH, today: Callable[[], date] = date.today
) -> FastAPI:
    app = FastAPI(title="AI Language Teacher")
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")

    # Blocks DNS rebinding: another site's domain pointed at 127.0.0.1.
    app.add_middleware(TrustedHostMiddleware, allowed_hosts=ALLOWED_HOSTS)

    @app.middleware("http")
    async def reject_foreign_posts(
        request: Request, call_next: Callable[[Request], Awaitable[Response]]
    ) -> Response:
        # Blocks other websites from posting forms here (CSRF). Clients that
        # send no Origin header (not a browser) are allowed.
        origin = request.headers.get("origin")
        own = f"{request.url.scheme}://{request.headers.get('host')}"
        if request.method == "POST" and origin is not None and origin != own:
            return PlainTextResponse("Cross-site request blocked", status_code=403)
        return await call_next(request)

    def home_page(request: Request, error: str | None = None, status_code: int = 200) -> Response:
        with closing(connect(db_path)) as conn:
            names = list_students(conn)
        return templates.TemplateResponse(
            request, "home.html", {"names": names, "error": error}, status_code=status_code
        )

    def load_or_404(conn: sqlite3.Connection, name: str) -> Student:
        student = load_student(conn, name)
        if student is None:
            raise HTTPException(status_code=404, detail="No profile with that name")
        return student

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
            student = load_or_404(conn, name)

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

    def study_target(conn: sqlite3.Connection, skill: str, name: str) -> Student:
        if skill not in COURSES:
            raise HTTPException(status_code=404, detail="No course for that skill")
        student = load_or_404(conn, name)
        if skill not in open_skills(student, COURSES, PREREQUISITES):
            raise HTTPException(status_code=403, detail=f"{skill} is locked")
        return student

    def skill_page(
        request: Request,
        template: str,
        student: Student,
        skill: str,
        status_code: int = 200,
        **context: Any,
    ) -> Response:
        context |= {
            "name": student.name,
            "skill": skill,
            "study_url": f"/study/{skill}/{quote(student.name)}",
            "practice_url": f"/practice/{skill}/{quote(student.name)}",
        }
        return templates.TemplateResponse(request, template, context, status_code=status_code)

    def item_context(lessons: list[Lesson], item: str) -> dict[str, Any]:
        lesson = lesson_of(lessons, item)
        return {
            "item": item,
            "teaching": lesson.teaching[item],
            "prompt": question_of(lesson, item).prompt,
            "expected": lesson.items[item],
        }

    @app.get("/study/{skill}/{name:path}", response_class=HTMLResponse)
    def study(request: Request, skill: str, name: str, step: str | None = None) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, name)

        lessons = COURSES[skill]
        queue = study_queue(student, skill, lessons, today())
        if not queue:
            dues = [card.due for card in student.cards[skill].values()]
            return skill_page(
                request,
                "study.html",
                student,
                skill,
                mode="done",
                next_review=min(dues, default=None),
            )

        item = queue[0]
        is_new = item not in student.cards[skill]
        mode = "teach" if is_new and step != "quiz" else "quiz"
        return skill_page(
            request, "study.html", student, skill, mode=mode, **item_context(lessons, item)
        )

    @app.post("/study/{skill}/{name:path}", response_class=HTMLResponse)
    def submit_answer(
        request: Request,
        skill: str,
        name: str,
        item: Annotated[str, Form()] = "",
        answer: Annotated[str, Form()] = "",
    ) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, name)
            lessons = COURSES[skill]
            day = today()

            # Only the current queue can be answered: a resent form or an item
            # that is not due yet records nothing.
            if item not in study_queue(student, skill, lessons, day):
                return RedirectResponse(f"/study/{skill}/{quote(student.name)}", status_code=303)

            context = item_context(lessons, item)
            if not answer.strip():
                return skill_page(
                    request,
                    "study.html",
                    student,
                    skill,
                    400,
                    mode="quiz",
                    error="Please type an answer.",
                    **context,
                )

            result = evaluate(skill, item, answer)
            record_answer(student, result, day)
            save_student(conn, student)

        return skill_page(
            request,
            "study.html",
            student,
            skill,
            mode="feedback",
            correct=result.correct,
            answer=answer,
            **context,
        )

    def practice_lesson(student: Student, skill: str, number: str) -> tuple[int, Lesson]:
        lessons = COURSES[skill]
        if not (number.isdigit() and 1 <= int(number) <= len(lessons)):
            raise HTTPException(status_code=404, detail="No such lesson")
        if int(number) > len(unlocked_lessons(student, skill, lessons)):
            raise HTTPException(status_code=403, detail="That lesson is locked")
        return int(number), lessons[int(number) - 1]

    @app.get("/practice/{skill}/{name:path}", response_class=HTMLResponse)
    def practice(
        request: Request, skill: str, name: str, lesson: str | None = None, n: int = 0
    ) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, name)

        if lesson is None:
            unlocked = unlocked_lessons(student, skill, COURSES[skill])
            lessons = [
                {
                    "number": number,
                    "title": each.title,
                    "learned": len(learned_items(student, skill, each)),
                    "total": len(each.items),
                }
                for number, each in enumerate(unlocked, start=1)
            ]
            return skill_page(
                request, "practice.html", student, skill, mode="list", lessons=lessons
            )

        number, chosen = practice_lesson(student, skill, lesson)
        if n < 0:
            raise HTTPException(status_code=404, detail="No such position")
        learned = learned_items(student, skill, chosen)
        context: dict[str, Any] = {
            "number": number,
            "title": chosen.title,
            "count": len(learned),
            "n": n,
        }
        if not learned:
            mode = "empty"
        elif n >= len(learned):
            mode = "complete"
        else:
            mode = "quiz"
            context |= item_context(COURSES[skill], learned[n])
        return skill_page(request, "practice.html", student, skill, mode=mode, **context)

    @app.post("/practice/{skill}/{name:path}", response_class=HTMLResponse)
    def submit_practice(
        request: Request,
        skill: str,
        name: str,
        lesson: Annotated[str, Form()] = "",
        n: Annotated[int, Form()] = 0,
        item: Annotated[str, Form()] = "",
        answer: Annotated[str, Form()] = "",
    ) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, name)
            number, chosen = practice_lesson(student, skill, lesson)
            learned = learned_items(student, skill, chosen)
            # Only learned items of this lesson can be practised.
            if item not in learned:
                url = f"/practice/{skill}/{quote(student.name)}?lesson={number}"
                return RedirectResponse(url, status_code=303)

            context: dict[str, Any] = {
                "number": number,
                "title": chosen.title,
                "count": len(learned),
                "n": n,
            }
            context |= item_context(COURSES[skill], item)
            if not answer.strip():
                return skill_page(
                    request,
                    "practice.html",
                    student,
                    skill,
                    400,
                    mode="quiz",
                    error="Please type an answer.",
                    **context,
                )

            result = evaluate(skill, item, answer)
            record_practice(student, result, today())
            save_student(conn, student)

        return skill_page(
            request,
            "practice.html",
            student,
            skill,
            mode="feedback",
            correct=result.correct,
            answer=answer,
            **context,
        )

    return app
