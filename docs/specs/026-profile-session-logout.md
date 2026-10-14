# 026: Profiles work like accounts, with logout and delete

## Problem
Today the student's name is part of every URL (`/study/hiragana/Ana`),
and the only way back to the profile list is the "AI Language Teacher"
link in the header. There is no sense of being "inside" a profile, and
nothing says how to switch to another one. The user wants a profile to
feel like an account: you enter it, use the app, and leave it with a
Logout button. There is also no way to delete a profile that is not
wanted any more.

## Behavior
- Choosing or creating a profile on "Who is studying?" opens it: the app
  remembers the current profile in a cookie and goes to its dashboard.
  Choosing an existing profile is a POST of its name to `/students`, the
  same form that creates one (an existing name is never overwritten).
- While a profile is open, every page shows the profile name and a
  **Logout** button at the right of the header.
- Logout forgets the current profile and goes back to "Who is studying?",
  which lists the profiles and has the form to create a new one.
- URLs no longer contain the name: `/dashboard`, `/study/<skill>`,
  `/practice/<skill>`, `/ask/<skill>`. Opening any of them without a
  current profile redirects to "Who is studying?". The old URLs with the
  name are removed (404), with no compatibility redirect.
- No passwords: the app is local, binds to `127.0.0.1` and profiles share
  one computer (MVP decision). Logout is about switching people, not
  security.
- Logout is a POST (a link that changes state could be triggered by
  another site); the existing Origin check covers it.
- The cookie holds the URL-encoded profile name (`profile`), `HttpOnly`,
  `SameSite=Lax`, not signed: signing needs a new dependency and protects
  nothing here, since anyone at the keyboard can pick any profile.
- **Delete a profile** (added by the user on approval): each profile on
  "Who is studying?" has a trash button. It opens a confirmation page:
  "You are about to delete the profile <name> and all its progress. This
  cannot be undone. Are you sure?" with **Yes, delete** and **No**
  buttons. Yes deletes the profile with all its progress and goes back
  to "Who is studying?"; No goes back without changing anything. Deleting
  the open profile also logs out. The confirmation is a page, not a
  JavaScript dialog: it works without JavaScript and the Yes button is a
  POST, so another site cannot delete a profile.

## Acceptance Criteria
- [ ] Choosing a profile sets the cookie and redirects to `/dashboard`.
- [ ] Creating a profile does the same.
- [ ] Every profile page shows the name and a Logout button.
- [ ] Logout clears the cookie and redirects to "Who is studying?".
- [ ] Profile pages without a current profile redirect to the home page.
- [ ] A cookie naming a profile that no longer exists is treated as no
      profile.
- [ ] Study, practice and ask keep working as before, without the name
      in the URL; the old URLs with the name return 404.
- [ ] Each profile on the home page has a trash button linking to its
      confirmation page.
- [ ] The confirmation page names the profile and has Yes and No; it
      deletes nothing by itself. Unknown profile: 404.
- [ ] Yes deletes the profile and all its rows and redirects home; other
      profiles are untouched. Unknown profile: 404.
- [ ] Deleting the open profile clears the cookie; deleting another one
      keeps it.
- [ ] A delete POST from another site's Origin is blocked (403).

## Decisions
- No PIN per profile until someone asks for one.
- Plain URL-encoded name in the cookie, no new dependency (see above).

## Out of Scope
- Real accounts, passwords, online sync.
- Renaming profiles (could be a later spec).
- The visual design of the header and the trash button (spec 030).
