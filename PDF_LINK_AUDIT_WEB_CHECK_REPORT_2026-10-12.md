# PDF Link Audit — Web Retrieval Results (12 October 2026)

## Scope and integrity

This report records a direct web-fetch check of a subset of the E-Library's 70 direct-PDF URLs. It is **not** a complete HTTP audit of all links. The runtime's direct network/DNS access was unavailable, so the local Python auditor could not finish a full 70-link run. The web retrieval tool could open some PDFs but returned crawler blocks or internal errors for others.

## Results

- **12 `VERIFIED_PDF`**: direct PDF content opened and was identifiable as a PDF.
- **2 `FETCH_BLOCKED_MANUAL_BROWSER_CHECK`**: OpenStax asset requests returned 403 to the crawler. This is not proof the PDF is broken; verify in a normal browser. OpenStax states that its textbooks are downloadable as PDFs.
- **8 `FETCH_NOT_RESOLVED`**: the web retrieval tool returned an internal error. These are unresolved, not automatically broken.
- **48 `NOT_CHECKED`**: no live result is claimed for these URLs.

See `PDF_LINK_AUDIT_WEB_CHECK_2026-10-12.csv` for every resource and its exact status. The `evidence_ref` column records the corresponding web retrieval evidence identifier where one exists.

## Important interpretation

A verified PDF means the web retrieval tool opened the direct URL and identified PDF content. A 403 or internal retrieval error is **not** enough to call a link broken. This audit did not validate every redirect, every normal-browser download, licensing conditions, or the accuracy/currentness of each textbook.

## Sources used for audit methodology

- Open Textbook Library says its collection contains complete textbooks in portable formats such as PDF and requires open licensing: https://open.umn.edu/opentextbooks/books
- OpenStax says its higher-education textbooks are available as free PDF downloads: https://openstax.org/higher-education

## Next step for a complete live audit

Run `RUN_PDF_LINK_AUDIT.bat` on an internet-connected Windows machine. It generates `PDF_LINK_AUDIT_LIVE.csv`. Treat `REVIEW_MANUALLY`, `NETWORK_ERROR`, and `NOT_CONFIRMED_PDF` as unresolved until opened in a browser; do not remove resources solely due to crawler blocking.
