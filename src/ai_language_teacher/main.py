import uvicorn

from ai_language_teacher.web.app import create_app


def main() -> None:
    # Localhost only: the app has no authentication.
    uvicorn.run(create_app(), host="127.0.0.1", port=8000)


if __name__ == "__main__":
    main()
