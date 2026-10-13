# Leap2Launch V26 — Security Patch Status

**Date:** 12 October 2026  
**Status:** Static patch applied; runtime validation pending.

## Changes applied

- Added session-bound CSRF tokens for browser form POST requests.
- Added hidden CSRF fields to all 72 static POST forms across templates.
- Added a narrow JSON-request exemption for the existing JSON-based companion endpoints; keep cross-origin CORS disabled for untrusted origins.
- Changed `/logout` to POST-only and changed the shared navigation logout control to a POST form.
- Changed `/like-post/<post_id>` to POST-only.
- Changed `/set-language/<code>` to POST-only and updated the navigation selector and language page to submit CSRF-protected forms.

## Static checks

- `python -m py_compile app.py`: PASS.
- `python VERIFY_BUILD.py`: PASS for syntax, Jinja templates, required route/template/email-gate checks, and the 22-category career catalogue.
- Template scan: 72 POST forms found; 0 missing hidden CSRF tokens.

## Not yet verified

Flask is unavailable in the isolated build environment, so no live Flask test-client or browser tests were possible. Install the project's requirements in a clean virtual environment and test valid and invalid CSRF submissions, login/signup/password-reset, language changes, logout, likes, and all JSON endpoints before calling this release runtime-tested. The JSON exemption is intended only for same-origin JSON endpoints and must be revisited if permissive CORS is enabled.
