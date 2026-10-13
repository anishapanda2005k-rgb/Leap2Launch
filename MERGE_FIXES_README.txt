Leap2Launch V26 combined build
================================
Base: the newer V26 Student/AI/learning build, which retains the earlier Faculty and Industry route/template set.
Fixes applied:
- Added the missing top-level `import re` used by Open Library PDF filtering.
- Fixed the faculty post-login redirect to use the registered `faculty_hub` endpoint instead of the nonexistent `faculty_dashboard`.
- Kept the temporary email-verification bypass from the supplied V26 build.
Validation:
- app.py compiles successfully.
- ZIP archive integrity checked.
- Browser/end-to-end testing could not be performed in this build environment; please run locally and report any new traceback.
