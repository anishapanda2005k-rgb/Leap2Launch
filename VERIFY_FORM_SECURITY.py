"""Static regression checks for browser form CSRF and method safety."""
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parent
APP = (ROOT / "app.py").read_text(encoding="utf-8")
TEMPLATES = ROOT / "templates"

assert "@app.before_request" in APP and "def _protect_browser_post_requests()" in APP, "Global browser POST CSRF guard missing"
assert "hmac.compare_digest" in APP, "CSRF comparison must use constant-time comparison"
assert 'request.form.get("csrf_token")' in APP, "CSRF guard does not read form tokens"
assert 'app.jinja_env.globals["csrf_token"] = _csrf_token' in APP, "CSRF helper is not available to templates"

post_forms = []
for path in TEMPLATES.rglob("*.html"):
    content = path.read_text(encoding="utf-8", errors="replace")
    for match in re.finditer(r"<form\b[^>]*>", content, re.IGNORECASE):
        opening = match.group(0)
        method_match = re.search(r"\bmethod\s*=\s*[\"']?([^\s\"'>]+)", opening, re.IGNORECASE)
        method = method_match.group(1).lower() if method_match else "get"
        if method != "post":
            continue
        tail = content[match.end():]
        close = re.search(r"</form\s*>", tail, re.IGNORECASE)
        body = tail[:close.start()] if close else tail
        line = content.count("\n", 0, match.start()) + 1
        if "csrf_token" not in body:
            post_forms.append(f"{path.relative_to(ROOT)}:{line}")
assert not post_forms, "POST form(s) missing CSRF token: " + ", ".join(post_forms)

# These two known state-changing actions must not regress to GET links/routes.
assert '@app.route("/logout", methods=["POST"])' in APP, "Logout must remain POST-only"
assert '@app.route("/like-post/<int:post_id>", methods=["POST"])' in APP, "Like action must remain POST-only"
base = (TEMPLATES / "base.html").read_text(encoding="utf-8")
assert 'action="{{ url_for(\'logout\') }}"' in base and 'method="POST"' in base, "Navigation logout form must use POST"
assert "csrf_token()" in base, "Navigation logout form must include CSRF token"

print(f"PASS: global session-bound CSRF guard and constant-time token comparison present.")
print(f"PASS: all scanned POST forms across {len(list(TEMPLATES.rglob('*.html')))} templates include CSRF tokens.")
print("PASS: logout and post-like state changes remain POST-only.")
print("LIMIT: static checks do not replace runtime testing of every route, role, and record-ownership rule.")
