import sqlite3
from collections.abc import Awaitable, Callable, Iterator, Sequence
from contextlib import closing
from datetime import date, timedelta
from pathlib import Path
from typing import Annotated, Any, Literal
from urllib.parse import quote, unquote

from fastapi import FastAPI, Form, HTTPException, Request
from fastapi.responses import (
    HTMLResponse,
    PlainTextResponse,
    RedirectResponse,
    Response,
    StreamingResponse,
)
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from starlette.middleware.trustedhost import TrustedHostMiddleware

from ai_language_teacher.core.assessment import Assessment, AssessmentResult
from ai_language_teacher.core.lesson import Lesson
from ai_language_teacher.core.progression import open_skills, unlocked_lessons
from ai_language_teacher.core.question import Question
from ai_language_teacher.core.review import (
    due_items,
    learned_items,
    record_answer,
    record_practice,
    study_queue,
)
from ai_language_teacher.core.student import Student
from ai_language_teacher.language.japanese.course import (
    COURSE_LABELS,
    COURSES,
    PREREQUISITES,
    course_overview,
)
from ai_language_teacher.language.japanese.lookup import find_course_words
from ai_language_teacher.storage import (
    DEFAULT_DB_PATH,
    connect,
    delete_student,
    list_students,
    load_student,
    save_student,
)
from ai_language_teacher.teacher import (
    MAX_HISTORY_MESSAGES,
    TeacherUnavailable,
    ask_ollama,
    chat_messages,
    chat_ollama,
    current_model,
    free_conversation_lesson,
    grounded_prompt,
    safe_answer,
    safe_stream,
    teacher_prompt,
)

HERE = Path(__file__).parent
ALLOWED_HOSTS = ["127.0.0.1", "localhost"]
MAX_QUESTION_LENGTH = 500
TOO_LONG = f"Please type a question of up to {MAX_QUESTION_LENGTH} characters."
MAX_EXPLAINED_ANSWER = 100
# Holds the open profile's URL-encoded name (spec 026). Not signed: the app is
# local and has no passwords, so anyone at the keyboard can open any profile.
PROFILE_COOKIE = "profile"


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


def queue_left(student: Student, skill: str, day: date) -> dict[str, int]:
    # The study queue is the due reviews followed by the new items.
    reviews = len(due_items(student, skill, day))
    queue = study_queue(student, skill, COURSES[skill], day)
    return {"reviews": reviews, "new": len(queue) - reviews}


def unlock_progress(student: Student, skill: str) -> tuple[int, list[str]]:
    unlocked = unlocked_lessons(student, skill, COURSES[skill])
    return len(unlocked), open_skills(student, COURSES, PREREQUISITES)


def unlock_messages(student: Student, skill: str, before: tuple[int, list[str]]) -> list[str]:
    # Compares unlock_progress before and after an answer; nothing new is stored.
    lessons_before, opened_before = before
    lessons_after, opened_after = unlock_progress(student, skill)
    lessons = COURSES[skill]
    messages = [
        f"Lesson {number} unlocked: {lessons[number - 1].title}"
        for number in range(lessons_before + 1, lessons_after + 1)
    ]
    opened = [each for each in opened_after if each not in opened_before]
    return messages + [f"{each.capitalize()} is now open!" for each in opened]


def explain_question(answer: str, expected: str) -> str:
    # The answer is cut so the question always fits MAX_QUESTION_LENGTH.
    answer = answer.strip()[:MAX_EXPLAINED_ANSWER]
    return (
        f'I answered "{answer}", but the right answer is "{expected}". '
        "Why is my answer wrong, and how can I remember the right one?"
    )


class ChatTurn(BaseModel):
    role: Literal["user", "assistant"]
    content: str


class TeacherRequest(BaseModel):
    # The history comes from the browser tab (spec 028); the server keeps nothing.
    message: str
    history: list[ChatTurn] = []


class ChatRequest(TeacherRequest):
    item: str


def current_student(conn: sqlite3.Connection, request: Request) -> Student | None:
    # A cookie naming a deleted profile counts as no profile.
    cookie = request.cookies.get(PROFILE_COOKIE)
    return None if cookie is None else load_student(conn, unquote(cookie))


def create_app(
    db_path: str | Path = DEFAULT_DB_PATH,
    today: Callable[[], date] = date.today,
    ask: Callable[[str], str] = ask_ollama,
    chat: Callable[[list[dict[str, str]]], Iterator[str]] = chat_ollama,
) -> FastAPI:
    app = FastAPI(title="AI Language Teacher")
    app.mount("/static", StaticFiles(directory=HERE / "static"), name="static")
    templates = Jinja2Templates(directory=HERE / "templates")
    # chat.js keeps no more history than the server sends (spec 035).
    templates.env.globals["max_history"] = MAX_HISTORY_MESSAGES

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
            current = current_student(conn, request)
        context = {"names": names, "error": error, "name": current and current.name}
        return templates.TemplateResponse(request, "home.html", context, status_code=status_code)

    def open_student(conn: sqlite3.Connection, request: Request) -> Student:
        student = current_student(conn, request)
        if student is None:
            # No open profile: back to "Who is studying?".
            raise HTTPException(status_code=303, headers={"Location": "/"})
        return student

    @app.get("/", response_class=HTMLResponse)
    def home(request: Request) -> Response:
        return home_page(request)

    # Creates the profile if needed, then opens it. Choosing an existing
    # profile on the home page posts its name here too.
    @app.post("/students")
    def open_profile(request: Request, name: Annotated[str, Form()] = "") -> Response:
        name = name.strip()
        if not name:
            return home_page(request, "Please enter a name.", 400)

        with closing(connect(db_path)) as conn:
            if load_student(conn, name) is None:
                save_student(conn, Student(name))
        response = RedirectResponse("/dashboard", status_code=303)
        response.set_cookie(PROFILE_COOKIE, quote(name, safe=""), httponly=True, samesite="lax")
        return response

    @app.post("/logout")
    def logout() -> Response:
        response = RedirectResponse("/", status_code=303)
        response.delete_cookie(PROFILE_COOKIE)
        return response

    @app.get("/delete", response_class=HTMLResponse)
    def confirm_delete(request: Request, name: str = "") -> Response:
        # Only asks; the Yes button posts to /delete below.
        with closing(connect(db_path)) as conn:
            if load_student(conn, name) is None:
                raise HTTPException(status_code=404, detail="No profile with that name")
            current = current_student(conn, request)
        context = {"target": name, "name": current and current.name}
        return templates.TemplateResponse(request, "delete.html", context)

    @app.post("/delete")
    def delete_profile(request: Request, name: Annotated[str, Form()] = "") -> Response:
        with closing(connect(db_path)) as conn:
            if not delete_student(conn, name):
                raise HTTPException(status_code=404, detail="No profile with that name")
        response = RedirectResponse("/", status_code=303)
        if unquote(request.cookies.get(PROFILE_COOKIE, "")) == name:
            response.delete_cookie(PROFILE_COOKIE)
        return response

    @app.get("/dashboard", response_class=HTMLResponse)
    def dashboard(request: Request) -> Response:
        with closing(connect(db_path)) as conn:
            student = open_student(conn, request)

        # Read-only page: open_skills/unlocked_lessons update the student in
        # memory, but nothing is saved here.
        opened = open_skills(student, COURSES, PREREQUISITES)
        day = today()

        def percent(skill: str | None) -> int:
            if skill is None:
                return 0
            return round(course_mastery(student, skill, COURSES[skill]) * 100)

        cards = [
            {
                "name": skill,
                "japanese": COURSE_LABELS[skill][0],
                "sample": COURSE_LABELS[skill][1],
                "open": skill in opened,
                "mastery": percent(skill),
                "unlocked": len(unlocked_lessons(student, skill, lessons)),
                "total": len(lessons),
                "due": len(due_items(student, skill, day)),
                "prerequisite": PREREQUISITES[skill],
                "prerequisite_mastery": percent(PREREQUISITES[skill]),
            }
            for skill, lessons in COURSES.items()
        ]
        # Continue: due reviews first, in course order, then new items.
        continue_skill = next((each for each in opened if due_items(student, each, day)), None)
        if continue_skill is None:
            continue_skill = next(
                (each for each in opened if study_queue(student, each, COURSES[each], day)), None
            )
        dues = [card.due for each in opened for card in student.cards[each].values()]
        context = {
            "name": student.name,
            "courses": opened,
            "current": "/dashboard",
            "cards": cards,
            "continue_skill": continue_skill,
            "next_review": min(dues, default=None),
        }
        return templates.TemplateResponse(request, "dashboard.html", context)

    def study_target(conn: sqlite3.Connection, skill: str, request: Request) -> Student:
        student = open_student(conn, request)
        if skill not in COURSES:
            raise HTTPException(status_code=404, detail="No course for that skill")
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
            "courses": open_skills(student, COURSES, PREREQUISITES),
            "current": f"/study/{skill}",
            "skill": skill,
            "study_url": f"/study/{skill}",
            "practice_url": f"/practice/{skill}",
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

    @app.get("/study/{skill}", response_class=HTMLResponse)
    def study(request: Request, skill: str, step: str | None = None) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, request)

        lessons = COURSES[skill]
        day = today()
        queue = study_queue(student, skill, lessons, day)
        if not queue:
            dues = [card.due for card in student.cards[skill].values()]
            return skill_page(
                request,
                "study.html",
                student,
                skill,
                mode="done",
                next_review=min(dues, default=None),
                due_tomorrow=len(due_items(student, skill, day + timedelta(days=1))),
            )

        item = queue[0]
        is_new = item not in student.cards[skill]
        mode = "teach" if is_new and step != "quiz" else "quiz"
        return skill_page(
            request,
            "study.html",
            student,
            skill,
            mode=mode,
            left=queue_left(student, skill, day),
            **item_context(lessons, item),
        )

    @app.post("/study/{skill}", response_class=HTMLResponse)
    def submit_answer(
        request: Request,
        skill: str,
        item: Annotated[str, Form()] = "",
        answer: Annotated[str, Form()] = "",
    ) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, request)
            lessons = COURSES[skill]
            day = today()

            # Only the current queue can be answered: a resent form or an item
            # that is not due yet records nothing.
            if item not in study_queue(student, skill, lessons, day):
                return RedirectResponse(f"/study/{skill}", status_code=303)

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
                    left=queue_left(student, skill, day),
                    **context,
                )

            result = evaluate(skill, item, answer)
            before = unlock_progress(student, skill)
            record_answer(student, result, day)
            unlocks = unlock_messages(student, skill, before)
            save_student(conn, student)

        return skill_page(
            request,
            "study.html",
            student,
            skill,
            mode="feedback",
            unlocks=unlocks,
            left=queue_left(student, skill, day),
            correct=result.correct,
            answer=answer,
            explain=explain_question(answer, context["expected"]),
            **context,
        )

    def practice_lesson(student: Student, skill: str, number: str) -> tuple[int, Lesson]:
        lessons = COURSES[skill]
        if not (number.isdigit() and 1 <= int(number) <= len(lessons)):
            raise HTTPException(status_code=404, detail="No such lesson")
        if int(number) > len(unlocked_lessons(student, skill, lessons)):
            raise HTTPException(status_code=403, detail="That lesson is locked")
        return int(number), lessons[int(number) - 1]

    @app.get("/practice/{skill}", response_class=HTMLResponse)
    def practice(
        request: Request, skill: str, lesson: str | None = None, n: int = 0
    ) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, request)

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

    @app.post("/practice/{skill}", response_class=HTMLResponse)
    def submit_practice(
        request: Request,
        skill: str,
        lesson: Annotated[str, Form()] = "",
        n: Annotated[int, Form()] = 0,
        item: Annotated[str, Form()] = "",
        answer: Annotated[str, Form()] = "",
    ) -> Response:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, request)
            number, chosen = practice_lesson(student, skill, lesson)
            learned = learned_items(student, skill, chosen)
            # Only learned items of this lesson can be practised.
            if item not in learned:
                url = f"/practice/{skill}?lesson={number}"
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
            before = unlock_progress(student, skill)
            record_practice(student, result, today())
            unlocks = unlock_messages(student, skill, before)
            save_student(conn, student)

        return skill_page(
            request,
            "practice.html",
            student,
            skill,
            mode="feedback",
            unlocks=unlocks,
            correct=result.correct,
            answer=answer,
            explain=explain_question(answer, context["expected"]),
            **context,
        )

    def teacher_target(request: Request, skill: str, item: str) -> Student:
        with closing(connect(db_path)) as conn:
            student = study_target(conn, skill, request)
        # Read-only: only items the student can already see can be asked about.
        unlocked = unlocked_lessons(student, skill, COURSES[skill])
        if not any(item in lesson.items for lesson in unlocked):
            raise HTTPException(status_code=404, detail="No such item in unlocked lessons")
        return student

    def item_prompt(skill: str, item: str, question: str, earlier: Sequence[str] = ()) -> str:
        # Words from the student's earlier questions ground follow-ups ("and its
        # polite form?") that do not repeat the word.
        context = item_context(COURSES[skill], item)
        words = find_course_words("\n".join([*earlier, question]))
        return teacher_prompt(item, context["expected"], context["teaching"], question, words)

    @app.post("/ask/{skill}", response_class=HTMLResponse)
    def ask_teacher(
        request: Request,
        skill: str,
        item: Annotated[str, Form()] = "",
        question: Annotated[str, Form()] = "",
    ) -> Response:
        # The no-JavaScript fallback of the chat (spec 028).
        student = teacher_target(request, skill, item)
        context = item_context(COURSES[skill], item)
        question = question.strip()
        if not question or len(question) > MAX_QUESTION_LENGTH:
            context |= {"question": question, "error": TOO_LONG}
            return skill_page(request, "ask.html", student, skill, 400, **context)

        prompt = item_prompt(skill, item, question)
        try:
            reply, model = safe_answer(ask(prompt), prompt), None
        except TeacherUnavailable:
            reply, model = None, current_model()
        return skill_page(
            request,
            "ask.html",
            student,
            skill,
            question=question,
            reply=reply,
            model=model,
            **context,
        )

    def chat_reply(body: TeacherRequest, prompt: Callable[[str, list[str]], str]) -> Response:
        # prompt(message, earlier student messages) builds the grounded prompt.
        message = body.message.strip()
        if not message or len(message) > MAX_QUESTION_LENGTH:
            return PlainTextResponse(TOO_LONG, status_code=400)

        history = [(turn.role, turn.content) for turn in body.history][-MAX_HISTORY_MESSAGES:]
        earlier = [content for role, content in history if role == "user"]
        messages = chat_messages(history, prompt(message, earlier))
        try:
            chunks = chat(messages)
        except TeacherUnavailable:
            text = "The AI teacher is not available. Start Ollama and run: ollama pull "
            return PlainTextResponse(text + current_model(), status_code=503)
        # Japanese from earlier turns may be repeated, so it counts as allowed too.
        allowed = "\n".join(each["content"] for each in messages)
        return StreamingResponse(safe_stream(chunks, allowed), media_type="text/plain")

    @app.post("/chat/{skill}")
    def chat_with_teacher(request: Request, skill: str, body: ChatRequest) -> Response:
        teacher_target(request, skill, body.item)
        return chat_reply(
            body, lambda message, earlier: item_prompt(skill, body.item, message, earlier)
        )

    @app.get("/teacher", response_class=HTMLResponse)
    def teacher_page(request: Request) -> Response:
        with closing(connect(db_path)) as conn:
            student = open_student(conn, request)
        context = {
            "name": student.name,
            "courses": open_skills(student, COURSES, PREREQUISITES),
            "current": "/teacher",
        }
        return templates.TemplateResponse(request, "teacher.html", context)

    @app.post("/teacher")
    def free_chat(request: Request, body: TeacherRequest) -> Response:
        # Free conversation (spec 034): no item, grounded on the course words only.
        with closing(connect(db_path)) as conn:
            open_student(conn, request)

        def prompt(message: str, earlier: list[str]) -> str:
            words = find_course_words("\n".join([*earlier, message]))
            return grounded_prompt(free_conversation_lesson(course_overview()), message, words)

        return chat_reply(body, prompt)

    return app
