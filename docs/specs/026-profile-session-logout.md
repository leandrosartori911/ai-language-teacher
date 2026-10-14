# 026: Profiles work like accounts, with logout

> Status: **draft, not approved yet** (recorded 2026-10-14 from the
> user's review of the web UI). Review and approve before tests.

## Problem
Today the student's name is part of every URL (`/study/hiragana/Ana`),
and the only way back to the profile list is the "AI Language Teacher"
link in the header. There is no sense of being "inside" a profile, and
nothing says how to switch to another one. The user wants a profile to
feel like an account: you enter it, use the app, and leave it with a
Logout button.

## Behavior
- Choosing or creating a profile on "Who is studying?" opens it: the app
  remembers the current profile in a cookie and goes to its dashboard.
- While a profile is open, every page shows the profile name and a
  **Logout** button at the right of the header.
- Logout forgets the current profile and goes back to "Who is studying?",
  which lists the profiles and has the form to create a new one.
- URLs no longer contain the name: `/dashboard`, `/study/<skill>`,
  `/practice/<skill>`, `/ask/<skill>`. Opening any of them without a
  current profile redirects to "Who is studying?".
- No passwords: the app is local, binds to `127.0.0.1` and profiles share
  one computer (MVP decision). Logout is about switching people, not
  security.
- Logout is a POST (a link that changes state could be triggered by
  another site); the existing Origin check covers it.

## Acceptance Criteria
- [ ] Choosing a profile sets the cookie and redirects to `/dashboard`.
- [ ] Creating a profile does the same.
- [ ] Every profile page shows the name and a Logout button.
- [ ] Logout clears the cookie and redirects to "Who is studying?".
- [ ] Profile pages without a current profile redirect to the home page.
- [ ] A cookie naming a profile that no longer exists is treated as no
      profile.
- [ ] Study, practice and ask keep working as before, without the name
      in the URL.

## Open questions
- Should a profile optionally have a PIN, for siblings sharing one PC?
  (Proposal: no, until someone asks.)
- Signed cookie or the plain name? Starlette's `SessionMiddleware`
  signs cookies but needs `itsdangerous` (not installed: a new
  dependency). The plain profile name is enough for a local app without
  passwords (anyone at the keyboard can pick any profile anyway).
  Proposal: plain `HttpOnly`, `SameSite=Lax` cookie, no new dependency.

## Out of Scope
- Real accounts, passwords, online sync.
- Deleting or renaming profiles (could be a later spec).
- The visual design of the header (spec 030).
