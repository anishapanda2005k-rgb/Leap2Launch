"""Static validation for the partial web-retrieval PDF audit report."""
import csv
from collections import Counter
from pathlib import Path

root = Path(__file__).resolve().parent
with (root / 'PDF_LINK_AUDIT_WEB_CHECK_2026-10-12.csv').open(encoding='utf-8-sig', newline='') as f:
    rows = list(csv.DictReader(f))
assert len(rows) == 70, f'Expected 70 resource rows, got {len(rows)}'
assert len({r['url'] for r in rows}) == 70, 'Duplicate URLs in audit report'
counts = Counter(r['audit_status'] for r in rows)
assert counts['VERIFIED_PDF'] == 12, counts
assert counts['FETCH_BLOCKED_MANUAL_BROWSER_CHECK'] == 2, counts
assert counts['FETCH_NOT_RESOLVED'] == 8, counts
assert counts['NOT_CHECKED'] == 48, counts
for row in rows:
    if row['audit_status'] == 'VERIFIED_PDF':
        assert row['evidence_ref'] and row['content_type'] == 'application/pdf', row
    if row['audit_status'] == 'NOT_CHECKED':
        assert not row['evidence_ref'], row
report = (root / 'PDF_LINK_AUDIT_WEB_CHECK_REPORT_2026-10-12.md').read_text(encoding='utf-8')
assert 'complete HTTP audit' in report
assert 'not automatically broken' in report
print('PASS: 70 resources accounted for; 12 verified PDFs, 2 crawler-blocked, 8 unresolved fetches, 48 not checked.')
