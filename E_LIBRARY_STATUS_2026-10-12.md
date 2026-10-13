# Leap2Launch E-Library status — 12 October 2026 (expanded + audit tooling)

## Standard-reference bookshelf

- **277 curated standard books** across **59 subject areas**.
- Every subject area has at least two book entries in this catalogue.
- Each record includes title, authors, subject, recommended level, learning purpose, a usefulness note, and a legitimate-access lookup.
- Learning-purpose tags: Advanced / specialist reference (35), Core textbook (145), Practical & professional reference (60), Applied / research methods (13), Practice & problem-solving (18), Foundation & introductory reading (6).
- Users can search by title/author/subject and filter by field and learning purpose.
- Copyrighted books link to legitimate catalogue lookups; they are not represented as free PDFs.

## Direct PDF library

- **70 direct-PDF records** across **40 subject labels**.
- Expanded with official MIT OpenCourseWare psychology textbook material and additional foundational biology problem sets; the NASA systems-engineering entry now points to NASA NTRS's *Systems Engineering Handbook Rev 2* PDF rather than the older 2018 URL.
- PDF catalogue cards filter to `.pdf` URLs and include a search box, subject filter, type filter, access notes and short descriptions.
- Direct PDF records are intentionally separate from the standard-reference bibliography; commercial textbook scans are not added without authorization.

## Link-audit findings and limits

- A web-retrieval spot-check confirmed PDF content for MIT OCW *Bioprocess Design and Simulation*, NIST *Cybersecurity Framework 2.0*, NASA *Systems Engineering Handbook Rev 2*, and four MIT introductory-biology problem/practice PDFs.
- OpenStax asset URLs returned 403 or were inaccessible to the web retrieval service. OpenStax official pages confirm the corresponding textbooks are downloadable as free PDFs, so those results are classified as **manual browser checks required**, not broken links.
- MIT OCW's 25 MB psychology course textbook is listed on its official resource page, but the web retrieval service rejected the file due to its fetch-size limit. WHO IRIS also failed to fetch in this environment; neither result proves the URL is broken.
- `PDF_LINK_AUDIT_EVIDENCE_2026-10-12.csv` lists evidence for all 70 resources and explicitly marks resources not live-checked. It does not claim full live validation.
- `AUDIT_DIRECT_PDF_LINKS.py` is included to run a real HTTP audit from an internet-connected computer. It tries HEAD then a small ranged GET, follows redirects, checks the `%PDF-` signature where possible and writes `PDF_LINK_AUDIT_LIVE.csv`. It does not download complete PDFs. Review 403/429/network failures manually.
- The build container has no external DNS access, so it cannot run a full live HTTP audit itself. Flask is also not installed in this isolated environment, so browser end-to-end testing remains outstanding.

## Verification run

- `python -m py_compile app.py VERIFY_E_LIBRARY.py AUDIT_DIRECT_PDF_LINKS.py VERIFY_PDF_LINK_AUDIT.py` — PASS.
- `python VERIFY_E_LIBRARY.py` — PASS: 70 unique PDF records, 40 subjects, 277 books across 59 fields, search/filter and metadata checks.
- `python VERIFY_BUILD.py` — PASS static source/template checks (119 templates, route and Learning Studio checks).
- `python VERIFY_PDF_LINK_AUDIT.py` — PASS audit helper unit tests without external network calls.
