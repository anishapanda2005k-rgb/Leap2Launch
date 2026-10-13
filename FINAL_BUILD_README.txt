Leap2Launch — V26 Expanded Career Pathways
==========================================

Core journey:
Discover → Assess → Map Gaps → Learn → Demonstrate → Verify → Match → Connect → Outcome

Live user-generated workflows:
- Registered accounts and account-owned profiles
- Community feed with database-backed posts and image attachments
- Connection requests, acceptance/rejection notifications, and accepted-connection chat
- Mentorship requests, status updates, notifications, and mentorship chat
- Company-created industry challenges with student solution submissions
- Challenge owner notifications and submission review view
- Skill assessment, aptitude, soft skills, department assessment
- Skill map, dynamic skill gaps, learning plan, mastery/review
- External learning resources/courses and roadmaps
- Games and game-to-proof workflows
- Human skill verification, appeals, skill freshness/trust
- Industry jobs/internships/challenges and explainable matching
- Portfolio, resume, ATS, rewards, outcomes, notifications, analytics
- Accessibility and 12 interface languages

Demo-data policy:
- The application no longer seeds demo accounts, synthetic demo evidence, sample demo jobs/internships, or synthetic challenges on startup.
- The old SIH Demo Lab page and unused legacy app backups have been removed from this release.
- A pre-existing database created by an older version may still contain old demo records. Back it up and review/purge those records before production use; this release does not blindly delete rows that might be linked to real user data.

Live-update behavior:
- Community feed polls for new posts every 4 seconds.
- Connection and mentorship chat poll for new messages every 2.5 seconds.
- Unread notification badges poll every 5 seconds.
- These are near-real-time database polling workflows, not WebSocket push notifications.

Setup/testing:
- Install requirements.txt in a virtual environment.
- Configure email/SMTP and production secret settings before using account verification or deploying publicly.
- Run the app in a local environment with Flask and dependencies installed, then test signup/login, post creation, connection requests, chats, notifications, challenge creation/submission/review and role permissions.
- Static Python syntax check passes for app.py. Browser/runtime E2E tests have not been completed in this environment.

LATEST UPDATE — 2026-10-13
See AI_ENGINE_QUICKSTART.txt and AI_ENGINE_SETUP_2026-10-13.md for the configurable AI adapter and limitations. No model API key is included. To enable model-powered reasoning, the project owner must configure a permitted provider on the server. Run VERIFY_ALL_STATIC.bat before use; static tests do not replace browser/E2E tests.
