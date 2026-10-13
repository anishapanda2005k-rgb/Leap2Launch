# Leap2Launch V26 — incremental build notes

## Added in this build
- Expanded the starter catalogue to 21+ broad pathways, including psychology/social sciences, quantitative science, architecture/built environment, Earth/climate/space science, transport/logistics, communications/media, public safety/disaster management, personal services/beauty and research/lab/quality careers.
- Career details now include broad education-route guidance and likely work settings, with reminders to verify country-specific admissions, protected titles and licensing through official sources.
- Added `/career-assessment/<slug>`: a short reflection tailored by career family (practical, people-facing, analytical, creative or planning-oriented), returning a small next-step plan. It is explicitly not presented as a validated psychological test or hiring/admissions predictor.
- Expanded discovery interest options to cover the new pathway families.
- Upgraded `VERIFY_BUILD.py` to check syntax, all Jinja templates, required routes/templates, duplicate route slug issues in the catalogue, required catalogue fields and HTTPS resource links without importing/executing the Flask app.

## Validation performed here
- Python AST/syntax: PASS
- Jinja template parsing: PASS
- Required route/template checks: PASS
- Career catalogue structure: PASS (unique slugs, required fields, HTTPS resource links)
- Full Flask browser/end-to-end tests: NOT RUN because Flask is not installed in this isolated build environment and package installation is blocked by unavailable network/DNS. Run `python -m pip install -r requirements.txt` on the target computer, then run `python VERIFY_BUILD.py` and manually test the routes.

## Not claimed complete
This remains an expandable starter catalogue, not a complete global dataset of every degree, occupation, current salary, admission rule, course or license. Live email OTP delivery requires real SMTP settings. Production launch still needs live security review, CSRF protection, deployment hardening, monitoring, data protection/retention rules and full end-to-end tests.

## 2026-10-12 — Request-method and CSRF hardening (static patch)
- Added session-bound CSRF validation for browser POST requests and tokens to all 72 static POST forms.
- Converted logout, post likes, and language preference changes to POST-only operations.
- Updated shared navigation and language selection forms.
- Static checks pass; Flask/browser runtime tests remain pending because Flask is not installed in the isolated environment.


## 2026-10-12 — Learning Studio expansion
- Added per-user course enrollment and a My Learning dashboard.
- Added save/unsave course bookmarks and enrolled-learner ratings/reviews.
- Expanded course learning pages with persisted assessment progress, progress summaries, and links to resume learning.
- Added gated Leap2Launch completion PDF records after all mapped topic tests pass at 70% or above.
- Clarified that external provider courses/certificates are not republished or impersonated.
- Runtime testing still needs to be performed in a Windows environment with requirements installed.

## 2026-10-13 — Adaptive Career Discovery & Configurable AI Copilot

- Added an optional OpenAI-compatible chat-completions adapter using Python's standard library; no provider key is shipped with the project.
- Added a platform-specific AI system prompt, bounded API request/response handling, recent-turn context, and clear external-provider privacy notice.
- Expanded guided career discovery to collect degree, direction, interests, experience and the learner's goal before generating a pathway report.
- Added a four-week career exploration roadmap to the A–Z career matching page; relative match values are labelled as heuristics, not success probabilities.
- Added `VERIFY_AI_ENGINE.py` to the static verification suite and documented provider setup and limitations in `AI_ENGINE_SETUP_2026-10-13.md`.
- Important: no model API key is included; a capable external model is only active after the project owner configures a permitted provider. No live web retrieval is implemented by this adapter.

- Added `VERIFY_CORE_JOURNEYS.py` to check static route coverage for career discovery, skill-gap/evidence, simulations, Learning Studio and academia-industry workflows.


## 13 October 2026 — AI grounding and offline retrieval tests

- Added `_retrieve_career_context`, a local keyword-ranked retriever over the platform career catalogue. It returns a bounded set of matching records with explicit matched terms and scores; it is not represented as semantic search or live labour-market research.
- Career Discovery now supplies relevant catalogue candidates based on the learner's degree, direction, interests, experience and goal instead of sending the first 100 catalogue entries indiscriminately. A small local fallback candidate set remains available if no keyword matches are found.
- AI Companion context now includes a bounded set of relevant local career records for both general signed-in roles and student coaching.
- Strengthened the AI prompt to distinguish catalogue records from suitability judgements and to avoid treating retrieval matches as proof of aptitude.
- Added `VERIFY_AI_RETRIEVAL.py` with offline behavioral checks for ranking, result limits, matched-term evidence and empty queries. Updated `VERIFY_AI_ENGINE.py` to require retrieval coverage.
- Validation: Python compilation, AI engine checks, retrieval behavior checks, core journey static checks, and build/template verification pass. Flask runtime/browser tests remain unrun because Flask is not installed and package-network access is unavailable in this environment.
