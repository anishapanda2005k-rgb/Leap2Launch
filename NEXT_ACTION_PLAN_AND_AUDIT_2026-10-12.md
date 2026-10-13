# Leap2Launch V26 — Consolidated Audit & Next Actions

**Date:** 12 October 2026  
**Source:** `app.py`, templates, `requirements.txt`, `VERIFY_BUILD.py` in the supplied V26 ZIP.  
**Scope:** Static source audit only. No production database was opened or changed.

## Confirmed static checks

- `app.py` parses and compiles successfully.
- Jinja parsing succeeds for all 118 templates.
- The existing `VERIFY_BUILD.py` passes its required route/template/email-gate checks.
- The starter career catalogue has 22 unique slugs, required fields, and HTTPS resource URLs.
- Flask and pygame are unavailable in this isolated environment; browser/server runtime and end-to-end tests were not run.

## Confirmed observations requiring engineering attention

1. **CSRF protection is not evident in the inspected application configuration or browser-form flow.** Add a real CSRF token strategy to state-changing browser forms and test rejection of missing/invalid tokens. Preserve JSON/API use cases with explicit, narrow exemptions only where necessary.
2. **Logout is currently a GET route and is linked as an anchor in `templates/base.html`.** Convert logout to POST and update the shared navigation form, alongside CSRF protection.
3. **Post likes are currently state-changing through GET** (`/like-post/<int:post_id>`). Convert to POST and update the UI accordingly.
4. **Authorization must be reviewed route-by-route.** The presence of a login decorator alone does not establish ownership checks; verify user IDs and record ownership for reads, updates, exports, uploads and downloads.
5. **Email verification depends on environment configuration.** Test SMTP success/failure, expired and reused tokens, retry limits, and account state transitions. Never report email as sent when delivery failed.
6. **Upload/download and generated PDF paths need adversarial tests** for ownership, path traversal, invalid file types, large files, and malformed user text.
7. **Reproducible dependencies need version constraints.** `requirements.txt` currently lists unpinned top-level packages. Establish tested versions on the target Windows/Python version before release.

These are static observations and review priorities, not claims that a live exploit was demonstrated.

## Recommended implementation and test order

### P0 — Safe runtime baseline

- Create a clean virtual environment on the target machine and install the project's dependencies.
- Use a temporary test database; never use or overwrite the user's real database during tests.
- Verify app startup and `/health` plus `/build-status`.
- Run signup, verification, login, logout, password reset and profile persistence flows.
- Record each failure before making changes.

### P1 — Request security and permissions

- Add CSRF protection to state-changing browser forms.
- Make logout and post-like actions POST-only.
- Review all sensitive routes for authentication, role checks and per-record ownership checks.
- Exercise unauthorized-user and wrong-owner test cases.
- Test upload/download handling and PDF generation with malformed inputs.

### P2 — End-to-end product journeys

- Skills → assessment → learning plan → course progress → evidence → human verification → Skill Passport.
- Career discovery → career detail → relevant learning resources → opportunity match → application tracking.
- Employer challenge → student submission → review → outcome/feedback.
- Connections and mentorship → accept/reject → protected messaging → notifications.
- Resume/portfolio → export → permission and input validation.

### P3 — Product depth after reliability

- Expand the career catalogue with curated, sourced information instead of bulk-generated unsupported claims.
- Add editable career stage and multi-select goals independently from account role.
- Preserve resource provenance: provider, source URL, last-checked date, free/paid status, certificate conditions and eligibility where available.
- Mark unavailable live integrations honestly; do not simulate current opportunities or successful email delivery.

## Release acceptance criteria

A release should only be called tested when the app starts in a clean environment, core journeys pass, invalid and unauthorized cases are rejected, persisted data is correct, the prior feature set has passed regression checks, and the test report lists any remaining limitations.


## Learning-directory expansion update — 2026-10-12

The course/resource directory was independently researched and expanded after the original static audit. `learning_resource_catalog.py` now seeds 121 entries across 64 subject labels. Of these, 55 entries have an official provider page check recorded in `source_checked_at`; entries include individual free courses, free-audit courses with optional paid certificates, and open course materials/resources. Course pages are prioritized above broad provider catalogues in the external-resource results.

New direct course/resource pages include OpenLearn material on Jamovi, carbon footprints, forensic science, business communication, mammals/ecology, metagenomics, sustainable chemistry, political/social change and social sciences; HarvardX/edX offerings on statistics, remote work, electrochemistry, education, contract law, food science, ethics/finance, entrepreneurship, linear models and machine learning; Harvard's Pyramids of Giza archaeology course; MIT OpenCourseWare aerospace engineering and CAD; NASA's Beginner's Guide to Aeronautics; and OpenLearn's exoplanet course.

The Courses UI now shows availability, duration, fee/access notes, certificate conditions and a clear distinction between provider pages checked on the review date and general discovery links not individually checked. This is still a curated and expandable directory, not a complete index of every course worldwide. Static verification passes; live Flask/browser end-to-end testing remains outstanding because Flask is unavailable in this isolated environment.


## Independent maintenance improvement — 2026-10-12

- Added SWAYAM Plus as a separate official discovery source; it includes a mixture of free and paid programmes and some credit-eligible learning, so the directory explicitly tells learners to inspect course-level price and delivery mode. Official source: https://swayamplus.education.gov.in/about and https://swayamplus.education.gov.in/catalog.
- Added `CHECK_LEARNING_LINKS.py`, a repeatable URL audit that emits a CSV with status, final redirect URL, timestamp and review recommendation. It does not auto-disable links or download course content.
- Added `VERIFY_LEARNING_LINK_AUDIT.py` offline tests for HTTP status classification, blocked HEAD fallback and invalid URL handling.
- This maintenance tool makes future upkeep repeatable; it is not a claim that all external URLs were live-checked in this build environment.
