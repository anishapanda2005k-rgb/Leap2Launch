"""Live audit for the direct-PDF E-Library catalogue.

Run from this folder:
    python AUDIT_DIRECT_PDF_LINKS.py
    python AUDIT_DIRECT_PDF_LINKS.py --timeout 15 --workers 3

Uses only Python's standard library. Tests the exact PDF URLs in app.py with
HEAD, falls back to a tiny ranged GET, checks the PDF signature where possible,
and writes PDF_LINK_AUDIT_LIVE.csv. HTTP 403/429 is marked for manual review,
not automatically labelled broken. This script does not download full PDFs.
"""
from __future__ import annotations
import argparse, ast, csv, re, time
from concurrent.futures import ThreadPoolExecutor, as_completed
from datetime import datetime, timezone
from pathlib import Path
from urllib.error import HTTPError, URLError
from urllib.parse import urlparse
from urllib.request import Request, urlopen

ROOT = Path(__file__).resolve().parent
USER_AGENT = "Leap2Launch-PDFLinkAudit/1.0 (educational-resource link validation)"


def catalogue():
    source = (ROOT / "app.py").read_text(encoding="utf-8")
    tree = ast.parse(source)
    route = next(n for n in ast.walk(tree) if isinstance(n, ast.FunctionDef) and n.name == "open_library")
    assignment = next(n for n in ast.walk(route) if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "resources" for t in n.targets))
    resources = ast.literal_eval(assignment.value)
    return [r for r in resources if re.search(r"\.pdf(?:$|[?#])", r["url"], re.I)]


def request(url, method, timeout, ranged=False):
    headers = {"User-Agent": USER_AGENT, "Accept": "application/pdf,*/*;q=0.8"}
    if ranged:
        headers["Range"] = "bytes=0-7"
    req = Request(url, method=method, headers=headers)
    try:
        with urlopen(req, timeout=timeout) as response:
            sample = response.read(8) if method == "GET" else b""
            return response.status, response.geturl(), response.headers.get("Content-Type", ""), sample, ""
    except HTTPError as exc:
        sample = b""
        try:
            if method == "GET": sample = exc.read(8)
        except Exception: pass
        return exc.code, exc.geturl() or url, exc.headers.get("Content-Type", "") if exc.headers else "", sample, str(exc.reason or "HTTP error")
    except (URLError, TimeoutError, OSError) as exc:
        return None, url, "", b"", str(getattr(exc, "reason", exc))[:240]


def audit(item, timeout):
    url = item["url"]
    stamp = datetime.now(timezone.utc).isoformat(timespec="seconds")
    base = {"checked_at_utc": stamp, "name": item["name"], "subject": item["subject"], "provider": item["provider"], "url": url, "final_url": url, "http_status": "", "content_type": "", "pdf_signature": "", "result": "", "note": ""}
    parsed = urlparse(url)
    if parsed.scheme != "https" or not parsed.netloc:
        base.update(result="INVALID_URL", note="Only absolute HTTPS URLs are accepted")
        return base
    status, final, ctype, sample, note = request(url, "HEAD", timeout)
    if status in (403, 405, 429, 501) or status is None:
        status, final, ctype, sample, note2 = request(url, "GET", timeout, ranged=True)
        note = note2 or ("Ranged GET used after HEAD was blocked/unsupported" if status is not None else note)
    base.update(final_url=final, http_status=status if status is not None else "", content_type=ctype, pdf_signature="yes" if sample.startswith(b"%PDF-") else ("no" if sample else "not tested"))
    if status is None:
        base.update(result="NETWORK_ERROR", note=note or "No HTTP response; check connection/DNS")
    elif status in (401, 403, 429):
        base.update(result="REVIEW_MANUALLY", note=note or "Provider may block automated requests; open in a normal browser")
    elif status >= 400:
        base.update(result="CHECK_LINK", note=note or "HTTP error; inspect redirect and try browser")
    elif sample.startswith(b"%PDF-") or "application/pdf" in ctype.lower():
        base.update(result="PDF_RESPONSE", note=note or ("Redirect followed" if final != url else "Server responded with PDF signature/content type"))
    elif status < 400 and not sample:
        base.update(result="REVIEW_MANUALLY", note="HEAD succeeded but PDF bytes were not inspected; rerun or open in browser")
    else:
        base.update(result="NOT_CONFIRMED_PDF", note=note or "Successful HTTP response but no PDF signature/content type; inspect in browser")
    return base


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--timeout", type=float, default=12.0)
    ap.add_argument("--workers", type=int, default=3)
    ap.add_argument("--output", default="PDF_LINK_AUDIT_LIVE.csv")
    args = ap.parse_args()
    if args.timeout <= 0 or not 1 <= args.workers <= 6:
        ap.error("timeout must be positive and workers must be 1–6")
    rows = catalogue()
    print(f"Auditing {len(rows)} direct-PDF records; no full files are downloaded.")
    results = []
    with ThreadPoolExecutor(max_workers=args.workers) as pool:
        futures = {pool.submit(audit, item, args.timeout): item for item in rows}
        for f in as_completed(futures):
            item = futures[f]
            try: result = f.result()
            except Exception as exc:
                result = {"checked_at_utc": datetime.now(timezone.utc).isoformat(timespec="seconds"), "name": item["name"], "subject": item["subject"], "provider": item["provider"], "url": item["url"], "final_url": item["url"], "http_status": "", "content_type": "", "pdf_signature": "not tested", "result": "AUDIT_ERROR", "note": str(exc)[:240]}
            results.append(result)
            print(f"[{result['result']}] {result['http_status'] or '—'} | {item['name']}")
            time.sleep(0.1)
    results.sort(key=lambda r: (r["result"], r["subject"].casefold(), r["name"].casefold()))
    output = (ROOT / args.output).resolve()
    fields = ["checked_at_utc", "name", "subject", "provider", "url", "final_url", "http_status", "content_type", "pdf_signature", "result", "note"]
    with output.open("w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=fields); writer.writeheader(); writer.writerows(results)
    counts = {}
    for r in results: counts[r["result"]] = counts.get(r["result"], 0) + 1
    print("Summary: " + ", ".join(f"{k}={v}" for k, v in sorted(counts.items())))
    print(f"Report saved: {output}")
    print("Important: 403/429/network errors require manual review; do not remove links solely from an automated result.")

if __name__ == "__main__": main()
