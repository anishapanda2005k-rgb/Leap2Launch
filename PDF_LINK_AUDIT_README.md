# Direct PDF link audit — 12 October 2026

The PDF catalogue contains **70 direct-PDF records**. The link-audit script is included because a reliable live HTTP audit must run from a machine with working DNS/internet access. The current isolated build environment cannot resolve external hosts (`curl` returns a DNS-resolution error), so it cannot truthfully claim a complete live audit of all links.

## What was checked from official source pages

- **Confirmed as PDF by the web retrieval tool:** MIT OCW *Bioprocess Design and Simulation*; NIST *Cybersecurity Framework 2.0*; NASA *Systems Engineering Handbook Rev 2* (2017 NTRS download); and MIT OCW introductory biology Problem Set 1, Problem Set 1 alternate practice, Problem Set 3 and Problem Set 3 alternate practice.
- **Official PDF listing found, but automated retrieval blocked/limited:** OpenStax direct asset URLs returned 403 or were inaccessible to the web retrieval service. OpenStax's official textbook pages state that the books are available as free PDF downloads. This is **not evidence that the links are broken**; check them in a normal browser and run the local audit.
- **Manual browser check required:** MIT OCW Introduction to Psychology course textbook is a direct official resource, but the retrieval service declined the 25 MB file because it exceeded its fetch limit.
- **Fetch failed / status unknown:** WHO IRIS PDF endpoint could not be retrieved by the web tool. This is not classified as broken.
- **Not checked live in this environment:** Remaining URLs. They are listed in `PDF_LINK_AUDIT_EVIDENCE_2026-10-12.csv` with an explicit status, not assumed to work.

## Run a full live audit on Windows

1. Extract the project ZIP.
2. Double-click `RUN_PDF_LINK_AUDIT.bat`, or run `python AUDIT_DIRECT_PDF_LINKS.py` from the project folder.
3. Open `PDF_LINK_AUDIT_LIVE.csv`.
4. Review `REVIEW_MANUALLY`, `NETWORK_ERROR`, `CHECK_LINK` and `NOT_CONFIRMED_PDF` rows in a normal browser before changing any catalogue record.

The script tries `HEAD`, falls back to a small ranged `GET`, checks the `%PDF-` signature where possible, follows redirects, and does not save full PDFs. Some legitimate hosts block automated requests, so HTTP 403/429 must not be treated as proof of a broken file.
## Web retrieval spot-check results (12 Oct 2026)

See `PDF_LINK_AUDIT_WEB_CHECK_REPORT_2026-10-12.md` and `PDF_LINK_AUDIT_WEB_CHECK_2026-10-12.csv` for the checked subset. This is a partial spot-check, not a claim that all links work. Crawler 403s and retrieval errors are unresolved rather than automatically broken.
