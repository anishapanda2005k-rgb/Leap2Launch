"""Check external learning-resource URLs without modifying the project database.

Usage:
  python CHECK_LEARNING_LINKS.py                 # check all catalog URLs
  python CHECK_LEARNING_LINKS.py --timeout 12    # adjust per-request timeout
  python CHECK_LEARNING_LINKS.py --output link_audit.csv

This is an on-demand maintenance tool. It follows redirects, tries GET when a
provider rejects HEAD, rate-limits concurrent requests, and writes a CSV report.
It does not sign in, submit forms, download course content, or change resource
status automatically. HTTP errors may be caused by anti-bot rules, so review
reported failures manually before removing a link.
"""
from __future__ import annotations
import argparse
import csv
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

from learning_resource_catalog import RESOURCES

USER_AGENT = "Leap2LaunchLearningLinkAudit/1.0 (+manual educational resource maintenance)"


def _request(url: str, method: str, timeout: float):
    request = Request(url, method=method, headers={"User-Agent": USER_AGENT, "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.status, response.geturl(), ""
    except HTTPError as exc:
        # HTTPError is also a response; preserve the status for reporting.
        return exc.code, exc.geturl() or url, str(exc.reason or "HTTP error")
    except (URLError, TimeoutError, OSError) as exc:
        return None, url, str(getattr(exc, "reason", exc))[:240]


def check_url(url: str, timeout: float = 10.0) -> dict:
    parsed = urlparse(url)
    base = {"url": url, "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
            "final_url": url, "status_code": "", "result": "", "note": ""}
    if parsed.scheme != "https" or not parsed.netloc:
        base.update(result="INVALID_URL", note="Only absolute HTTPS URLs are accepted")
        return base
    status, final_url, note = _request(url, "HEAD", timeout)
    if status in (403, 405, 501) or status is None:
        get_status, get_final, get_note = _request(url, "GET", timeout)
        # For GET, read at most a tiny amount then close; urlopen has already
        # opened the response, and the request does not save page content.
        status, final_url = get_status, get_final
        if get_note:
            note = get_note
        elif status is not None:
            note = "GET fallback used after HEAD was blocked/unsupported"
    base.update(final_url=final_url, status_code=status if status is not None else "")
    if status is None:
        base.update(result="NETWORK_ERROR", note=note or "No HTTP response")
    elif 200 <= status < 400:
        base.update(result="OK", note=note or ("Redirect followed" if final_url != url else "HTTP response received"))
    elif status in (401, 403, 429):
        base.update(result="REVIEW_MANUALLY", note=note or "Provider may block automated checks")
    else:
        base.update(result="CHECK_LINK", note=note or "Review the URL in a normal browser")
    return base


def main():
    parser = argparse.ArgumentParser(description="Audit external learning-resource links")
    parser.add_argument("--timeout", type=float, default=10.0, help="timeout per HTTP request in seconds (default: 10)")
    parser.add_argument("--workers", type=int, default=4, help="parallel requests (1-8; default: 4)")
    parser.add_argument("--output", default="learning_link_audit.csv", help="CSV report path")
    args = parser.parse_args()
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if not 1 <= args.workers <= 8:
        parser.error("--workers must be between 1 and 8")
    unique = {}
    for row in RESOURCES:
        domain, title, provider, resource_type, description, access_note, certificate_note, url, keywords = row
        unique.setdefault(url, {"domain": domain, "title": title, "provider": provider, "resource_type": resource_type, "url": url})
    records = list(unique.values())
    print(f"Checking {len(records)} unique official/provider URLs. This may take a few minutes.")
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(check_url, item["url"], args.timeout): item for item in records}
        for future in as_completed(futures):
            item = futures[future]
            try:
                result = future.result()
            except Exception as exc:  # keep one unexpected failure from stopping the audit
                result = {"url": item["url"], "checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"),
                          "final_url": item["url"], "status_code": "", "result": "AUDIT_ERROR", "note": str(exc)[:240]}
            results.append({**item, **result})
            print(f"[{result['result']}] {result.get('status_code') or '—'} {item['title']}")
    results.sort(key=lambda x: (x["result"] != "CHECK_LINK", x["domain"].casefold(), x["title"].casefold()))
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    fields = ["domain", "title", "provider", "resource_type", "url", "final_url", "status_code", "result", "note", "checked_at_utc"]
    with output.open("w", newline="", encoding="utf-8-sig") as handle:
        writer = csv.DictWriter(handle, fieldnames=fields, extrasaction="ignore")
        writer.writeheader()
        writer.writerows(results)
    counts = {}
    for result in results:
        counts[result["result"]] = counts.get(result["result"], 0) + 1
    print(f"\nSaved report: {output.resolve()}")
    print("Summary: " + ", ".join(f"{key}={value}" for key, value in sorted(counts.items())))
    print("Review CHECK_LINK / NETWORK_ERROR / REVIEW_MANUALLY entries in a browser before changing catalog records.")

if __name__ == "__main__":
    main()
