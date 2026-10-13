Leap2Launch — SIH audit/update — 2026-09-10

Latest fixes
- Corrected game-to-course/domain mapping: PCR Master → Biotechnology (specific learning resource: PCR & Gel Electrophoresis).
- My World now surfaces the complete Games Hub catalogue (9 games) and groups games by parent course/domain.
- Games Hub uses the same shared catalogue and distinguishes parent course/domain from specific learning course.
- Added a lightweight 12-language UI translation layer for key navigation labels; language selection remains persisted server-side.
- Added accessible Skip-to-content link and visible keyboard focus states.
- Added a real “Read this page aloud” action using browser speech synthesis on the accessibility page.
- Removed misleading “Coming Soon” labels from the existing CSE/domain UI where the underlying section is available.

Validation
- app.py Python compile: PASS
- Jinja template parse: PASS (0 errors)
- template url_for endpoint audit: PASS (0 missing endpoints)
- Final archive excludes runtime DB, secrets, .encryption_key, __pycache__.

Known limitation
- Full browser click-through/E2E testing was not possible in this Linux container because the project's Windows Flask environment is the intended runtime. Run `python app.py` in the existing Windows venv and test the major flows before presenting.
