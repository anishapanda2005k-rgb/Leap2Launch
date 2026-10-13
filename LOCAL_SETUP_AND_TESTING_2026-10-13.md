# Local setup and testing — 13 October 2026

## Start the app on Windows

1. Extract the ZIP to a normal writable folder (not inside the ZIP preview).
2. Install Python 3.11 or newer and enable **Add Python to PATH**.
3. Double-click `SETUP_AND_RUN_WINDOWS.bat`.
4. The script creates a project-local `.venv`, installs `requirements.txt`, runs the static checks, then starts Flask if those checks pass.
5. Open `http://127.0.0.1:5000` and keep the terminal open while testing.

The first run requires internet access to install packages. If pip cannot resolve package hosts, setup cannot complete until connectivity/DNS is available.

## Run static checks only

Double-click `VERIFY_ALL_STATIC.bat`, or run it from Command Prompt. It checks Python syntax, templates, library metadata, course catalogue metadata, link-audit logic and CSRF form coverage.

## Browser test checklist

- Sign up and confirm email verification is enforced.
- Log in/out; check logout is POST-only.
- Create a post and test likes, connections and chat.
- Try a student account and an industry account; verify role permissions.
- Create a challenge, submit a solution and review it as the owner.
- Enroll in a course, bookmark it, review it and check progress/completion records.
- Search/filter the Reference Bookshelf by field and learning purpose.
- Check PDF links on a live internet connection and report any redirects, blocked links or 404s.

## Honest status

Static checks are not the same as browser end-to-end tests. Email verification needs SMTP configuration to send real messages. All PDF URLs have not yet been confirmed live. Before public deployment, set `LEAP2LAUNCH_SECRET_KEY`, configure SMTP, back up/review any older database, and use a production WSGI server with HTTPS; do not expose Flask's debug server publicly.
