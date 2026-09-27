# 0001: Web stack is FastAPI + Jinja2 templates

- Status: accepted
- Date: 2026-09-27

## Context
The MVP needs a web interface (chosen over a CLI). The project is also a
way to learn Python and a portfolio piece, and it must cost nothing to
build and run. Later, the interface should re-theme itself per language
(for example, Japanese in the flag's red and white).

## Decision
Use FastAPI with server-rendered Jinja2 templates and a small amount of
vanilla JavaScript. No frontend framework and no frontend build step.
Colors are defined as CSS variables from the start so per-language theming
is a stylesheet change later. The app binds to `127.0.0.1` only.

## Consequences
- One language (Python) and one toolchain for the whole app.
- FastAPI is widely used, which helps the portfolio.
- Rich client-side interactivity is harder than with a SPA framework; if
  the UI outgrows templates, a framework like React can be added behind
  the same FastAPI endpoints.

## Alternatives considered
- React SPA + FastAPI API: stronger frontend portfolio signal, but two
  stacks and roughly double the work for the MVP.
- CLI only: fastest, but not the product the user wants.
