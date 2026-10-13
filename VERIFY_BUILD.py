"""Offline/static verifier for Leap2Launch. Run from the v21 project folder."""
import ast, glob, os, re, sys
try:
    from jinja2 import Environment, FileSystemLoader
except ImportError:
    print("FAIL: Jinja2 is missing. Install requirements.txt first."); raise SystemExit(2)
root = os.path.dirname(os.path.abspath(__file__))
app_path = os.path.join(root, "app.py")
source = open(app_path, encoding="utf-8").read()
try:
    tree = ast.parse(source, filename=app_path)
    compile(tree, app_path, "exec")
    print("PASS app.py syntax")
except Exception as exc:
    print("FAIL app.py syntax:", exc); raise SystemExit(1)

env = Environment(loader=FileSystemLoader(os.path.join(root, "templates")))
templates = glob.glob(os.path.join(root, "templates", "**", "*.html"), recursive=True)
for filename in templates:
    rel = os.path.relpath(filename, os.path.join(root, "templates"))
    try:
        env.parse(open(filename, encoding="utf-8").read())
    except Exception as exc:
        print("FAIL Jinja", rel, exc); raise SystemExit(1)
print(f"PASS Jinja syntax ({len(templates)} templates)")

routes = re.findall(r"@app\.(?:route|get|post)\(['\"]([^'\"]+)", source)
if routes.count("/build-status") != 1:
    print("FAIL: /build-status must be registered exactly once"); raise SystemExit(1)
required_routes = ["/signup", "/verify-email", "/resend-verification", "/account/roles", "/account/change-email", "/career-explorer", "/career-discovery", "/open-library", "/career-assessment/<slug>"]
for route in required_routes:
    if route not in routes:
        print("FAIL: missing route", route); raise SystemExit(1)
required_templates = ["verify_email.html", "resend_verification.html", "account_roles.html", "change_email.html", "verify_email_change.html", "career_explorer_global.html", "career_detail_global.html", "career_discovery_global.html", "career_assessment.html", "open_library.html"]
for name in required_templates:
    if not os.path.exists(os.path.join(root, "templates", name)):
        print("FAIL: missing template", name); raise SystemExit(1)
if "email_verified=1" not in source or "email_verified" not in source:
    print("FAIL: email verification gate missing"); raise SystemExit(1)
print("PASS required routes, templates and email-verification gate")
for route_name in ['learning_dashboard', 'course_enroll', 'course_bookmark', 'course_review', 'course_completion_certificate']:
    if not re.search(rf"def\s+{route_name}\s*\(", source):
        print("FAIL: missing Learning Studio route", route_name); raise SystemExit(1)
for template_name in ['learning_dashboard.html', 'courses_catalogue.html', 'course_learn.html']:
    if not os.path.exists(os.path.join(root, 'templates', template_name)):
        print("FAIL: missing Learning Studio template", template_name); raise SystemExit(1)
for table_name in ['course_enrollments', 'course_bookmarks', 'course_reviews']:
    if table_name not in source:
        print("FAIL: missing Learning Studio table", table_name); raise SystemExit(1)
print("PASS Learning Studio enrollment, dashboard, bookmarks, reviews and completion-record source checks")

# Read the catalogue as a literal AST node; never execute app.py during static validation.
catalogue = None
for node in tree.body:
    if isinstance(node, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "CAREER_CATALOG" for t in node.targets):
        try: catalogue = ast.literal_eval(node.value)
        except Exception as exc:
            print("FAIL: career catalogue is not static data:", exc); raise SystemExit(1)
        break
if not isinstance(catalogue, list) or len(catalogue) < 20:
    print("FAIL: expected at least 20 starter career categories"); raise SystemExit(1)
slugs = [item.get("slug") for item in catalogue]
if len(slugs) != len(set(slugs)) or any(not x for x in slugs):
    print("FAIL: missing or duplicate career slug"); raise SystemExit(1)
for item in catalogue:
    for field in ("title", "group", "description", "paths", "skills", "try", "resources"):
        if not item.get(field):
            print("FAIL: catalogue item missing", field, item.get("slug")); raise SystemExit(1)
    for resource in item["resources"]:
        if not resource.get("name") or not re.match(r"^https://", resource.get("url", "")):
            print("FAIL: invalid or non-HTTPS resource", item["slug"], resource); raise SystemExit(1)
print(f"PASS career catalogue ({len(catalogue)} unique categories; required fields and HTTPS resources)")
print("PASS local static build verification")
try:
    import flask
    print("PASS Flask import available")
except Exception:
    print("WARN Flask not installed in this test environment; browser/end-to-end checks require installing requirements.txt locally")
