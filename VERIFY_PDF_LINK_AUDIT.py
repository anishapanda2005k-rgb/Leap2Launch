"""Offline unit tests for the live PDF-link audit helper."""
from unittest.mock import patch
import AUDIT_DIRECT_PDF_LINKS as audit


def run():
    with patch.object(audit, "request", return_value=(200, "https://example.org/book.pdf", "application/pdf", b"%PDF-1.7", "")):
        row = audit.audit({"name":"Sample PDF", "subject":"Test", "provider":"Example", "url":"https://example.org/book.pdf"}, 1)
        assert row["result"] == "PDF_RESPONSE" and row["pdf_signature"] == "yes"
    with patch.object(audit, "request", side_effect=[(405, "https://example.org/book.pdf", "", b"", "Method Not Allowed"), (200, "https://example.org/book.pdf", "application/pdf", b"%PDF-1.4", "Ranged GET used")]):
        row = audit.audit({"name":"Sample PDF", "subject":"Test", "provider":"Example", "url":"https://example.org/book.pdf"}, 1)
        assert row["result"] == "PDF_RESPONSE" and row["pdf_signature"] == "yes"
    with patch.object(audit, "request", return_value=(403, "https://example.org/book.pdf", "text/html", b"", "Forbidden")):
        row = audit.audit({"name":"Sample PDF", "subject":"Test", "provider":"Example", "url":"https://example.org/book.pdf"}, 1)
        assert row["result"] == "REVIEW_MANUALLY"
    with patch.object(audit, "request", return_value=(404, "https://example.org/book.pdf", "text/html", b"", "Not Found")):
        row = audit.audit({"name":"Sample PDF", "subject":"Test", "provider":"Example", "url":"https://example.org/book.pdf"}, 1)
        assert row["result"] == "CHECK_LINK"
    row = audit.audit({"name":"Bad URL", "subject":"Test", "provider":"Example", "url":"http://example.org/book.pdf"}, 1)
    assert row["result"] == "INVALID_URL"
    print("PASS: PDF signature detection, ranged-GET fallback, blocked-host handling, 404 classification and HTTPS validation.")

if __name__ == "__main__": run()
