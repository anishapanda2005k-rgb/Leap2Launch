# Reference Library UX & Regression Checks — 13 October 2026

## Fixed

- Wired the Standard Reference Bookshelf's **Learning purpose** selector to the same filtering function used by search and field selection.
- The selected purpose now updates visible cards, result count, and the empty-results state immediately.
- Added a regression assertion to `VERIFY_E_LIBRARY.py` so the selector cannot silently become inert again.
- Added `VERIFY_FORM_SECURITY.py`, which checks that every scanned POST form includes a CSRF token and that logout/post-like routes remain POST-only.

## Verification performed on the extracted release ZIP

- `python -m py_compile app.py VERIFY_E_LIBRARY.py VERIFY_FORM_SECURITY.py`
- `python VERIFY_E_LIBRARY.py`
- `python VERIFY_FORM_SECURITY.py`
- `python VERIFY_BUILD.py`
- `python VERIFY_LEARNING_CATALOG.py`
- `python VERIFY_LEARNING_LINK_AUDIT.py`
- `python VERIFY_PDF_LINK_AUDIT.py`
- `python VERIFY_WEB_AUDIT_REPORT.py`

All above static/source checks pass. The project contains 70 direct-PDF records, 277 reference books across 59 fields, 122 course/resource directory entries across 64 subject labels, and 119 HTML templates.

## Limitations

- Browser end-to-end testing was not possible in this environment because Flask is not installed and outbound package/DNS access is unavailable.
- Static CSRF checks do not replace runtime testing of authentication, roles, or per-record ownership.
- The 70 PDF catalogue entries are not all live-verified; see `PDF_LINK_AUDIT_WEB_CHECK_REPORT_2026-10-12.md` for the exact evidence status.
