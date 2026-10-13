"""Offline tests for CHECK_LEARNING_LINKS.py; never contacts external sites."""
from unittest.mock import patch
import CHECK_LEARNING_LINKS as audit


def run():
    with patch.object(audit, "_request", return_value=(200, "https://provider.example/course", "")):
        result = audit.check_url("https://provider.example/course")
        assert result["result"] == "OK" and result["status_code"] == 200
    with patch.object(audit, "_request", side_effect=[(405, "https://provider.example/course", "Method Not Allowed"), (200, "https://provider.example/course", "")]):
        result = audit.check_url("https://provider.example/course")
        assert result["result"] == "OK" and "GET fallback" in result["note"]
    with patch.object(audit, "_request", return_value=(404, "https://provider.example/missing", "Not Found")):
        result = audit.check_url("https://provider.example/missing")
        assert result["result"] == "CHECK_LINK"
    with patch.object(audit, "_request", return_value=(403, "https://provider.example/course", "Forbidden")):
        result = audit.check_url("https://provider.example/course")
        assert result["result"] == "REVIEW_MANUALLY"
    result = audit.check_url("http://not-https.example/course")
    assert result["result"] == "INVALID_URL"
    print("PASS: link-audit result classification, HEAD-to-GET fallback, blocked-provider handling, and HTTPS validation.")

if __name__ == "__main__":
    run()
