# Leap2Launch — Functional Architecture Audit

**Audit date:** 10 October 2026  
**Audited source:** Adaptive Career Discovery v1 ZIP (v21 project folder)  
**Audit type:** Static source/template audit. This is not a claim of end-to-end completion.

## Executive finding

Leap2Launch has substantial breadth, but the existence of routes and templates alone does not prove that every user-facing flow works end-to-end. The next engineering objective is to establish a reliable, testable path from each visible action through validation, persistence, permissions, feedback and downstream module updates.

## Static inventory

- Flask route registrations found: **158** (some routes are aliases or share endpoints).
- HTML templates found under `templates/`: **108**.
- HTML `<form>` elements found in those templates: **70**.
- `url_for(...)` references checked: **371**.
- Missing `url_for` endpoint names in the static comparison: **0**.
- Python compilation: **PASS**.
- Jinja template parsing: **PASS**.
- Local `VERIFY_BUILD.py`: **PASS** for compile/template/static checks; it warns that Flask is unavailable in this environment.
- Browser/server end-to-end tests: **NOT RUN**. Flask is not installed in this execution environment, so authentication, database operations, role boundaries, form submissions and redirects have not been runtime-verified here.

## What these checks do and do not establish

The zero missing endpoint result means the templates' statically discoverable `url_for` names correspond to declared endpoints. It does **not** establish that all form actions work, database rows are correctly written, permissions are secure, external resources are current, or the rendered browser experience behaves correctly.

## High-priority engineering work

### P0 — Runtime reliability and data safety

1. Create a reproducible test setup using a temporary test database, never the user's live database.
2. Smoke-test startup, signup/login/logout, password reset, profile save, and role-based navigation.
3. For each POST route, test valid input, invalid input, duplicate submission, unauthorized user, wrong record owner, and missing record.
4. Audit database migrations for idempotency and preserve existing database contents during upgrade.
5. Check all upload/download paths for ownership, allowed file types, file size, path traversal, and safe error handling.
6. Add CSRF protection or an explicit, documented alternative for state-changing browser forms.

### P1 — Prove each feature works end-to-end

For each feature, record its UI entry point, route/API, validation, database table(s), permission rule, success feedback, failure feedback, and tests. Prioritise:

- Profile and onboarding
- Skill selection, assessment, history and skill gaps
- Learning recommendations, learning plans, lesson progress and mastery reviews
- Games, results, proof/evidence and human verification
- Skill Passport and evidence freshness
- Opportunities, eligibility/matching, application submission and status tracking
- Faculty/industry challenge creation and student submissions
- Connection requests, accept/reject, protected chat and notifications
- Mentorship request, acceptance, sessions, feedback and chat
- Resume/portfolio/ATS flows
- Rewards and redemption
- Analytics, exports, admin/audit views and role restrictions
- Career discovery conversation and restart/continue behavior

### P2 — Make the platform useful beyond placement

The existing signup role set is limited to `student`, `company`, and `faculty`. Career stage and purpose should not be encoded as one account role. Introduce separate, editable profile concepts for:

- **Workspace / role:** student/learner, professional, faculty/academic, mentor, employer/recruiter, institution, researcher, entrepreneur and restricted admin (only where justified).
- **Career stage:** studying, fresher, employed, seeking a new role, changing field, returning to work, founder, etc.
- **Goals (multi-select):** explore careers, learn from curiosity, connect/network, follow industry news, build skills, grow in current role, seek internships/jobs, change career, mentor, research/collaborate, build a venture.
- **Privacy preferences:** in particular, job-seeking activity must not be exposed to a current employer by default.

Do not create a separate login or unrelated database per persona. Use a common identity, explicit role assignments/permissions, and shared career/profile data.

### P3 — Real intelligence rather than labels

Any AI/recommendation feature must declare whether it uses deterministic local logic, user history, a curated dataset, or live external sources. A UI label saying “AI” is not enough. Research-backed recommendations must preserve source URL/title, retrieval date, eligibility, price/certificate conditions where relevant, and uncertainty. Never fabricate live opportunities or course details. If live search/API integration is not configured, show that limitation clearly.

## Definition of done for a feature

A feature is complete only when:

1. A real user can reach it from navigation.
2. Inputs are validated server-side.
3. The expected action changes or retrieves persistent data correctly.
4. The user sees truthful success/error feedback.
5. A different user cannot access data/actions they do not own or have permission to use.
6. Empty, duplicate, expired and failure states are handled.
7. The main flow and at least one failure/permission flow have automated or repeatable tests.
8. Any external dependency is configured and tested, or clearly marked as unavailable—not simulated as successful.

## Recommended delivery sequence

1. Build a temporary-database runtime test harness and record baseline test failures.
2. Fix P0 defects without replacing the production database or deleting current features.
3. Complete and test the critical student/professional journeys across skills → learning/practice → evidence → verification → passport → opportunities/connections.
4. Add flexible goals and career-stage onboarding with an idempotent database migration.
5. Integrate recommendations and AI against verified platform data, then add live external research only with explicit source and failure handling.
6. Run regression tests and package a clean release with a truthful test report.

## Current status

**Static checks pass; full functionality is not yet proven.** This report deliberately does not label the application “100% working” until runtime tests have been run.
