"""Static regression checks for the configurable AI and adaptive career engine."""
import ast
import os
import re
import sys

ROOT = os.path.dirname(os.path.abspath(__file__))
source = open(os.path.join(ROOT, "app.py"), encoding="utf-8").read()
try:
    tree = ast.parse(source)
    compile(tree, "app.py", "exec")
except Exception as exc:
    print("FAIL: app.py syntax", exc)
    raise SystemExit(1)

required_symbols = [
    "_ai_engine_configured", "_ai_model_label", "_call_configured_ai",
    "_ai_messages", "LEAP2LAUNCH_AI_SYSTEM_PROMPT", "ai_companion",
    "career_discovery", "_retrieve_career_context"
]
for symbol in required_symbols:
    if not re.search(rf"\b(?:def|class)\s+{re.escape(symbol)}\b|\b{re.escape(symbol)}\s*=", source):
        print("FAIL: missing AI symbol", symbol)
        raise SystemExit(1)

checks = {
    "server-side API key": "LEAP2LAUNCH_AI_API_KEY" in source,
    "configurable base URL": "LEAP2LAUNCH_AI_BASE_URL" in source,
    "configurable model": "LEAP2LAUNCH_AI_MODEL" in source,
    "bounded provider timeout": "timeout=35" in source,
    "bounded response tokens": "min(int(max_tokens), 1800)" in source,
    "graceful API failure fallback": "if provider_answer:" in source,
    "career discovery goal step": 'flow = {"step": "goal", "answers": answers}' in source,
    "career discovery AI final report": "Career Discovery final report" in source,
    "retrieval-grounded career context": "catalogue_candidates_retrieved_by_keyword" in source and "relevant_local_career_catalogue_records" in source,
    "retrieval behavioral tests included": os.path.exists(os.path.join(ROOT, "VERIFY_AI_RETRIEVAL.py")),
    "four-week roadmap": '"Week 4 — Show evidence"' in source,
    "heuristic match score disclosure": "heuristic, not a probability of success" in open(os.path.join(ROOT, "templates", "career_discovery_global.html"), encoding="utf-8").read(),
    "external provider data notice": "may be sent to that provider" in open(os.path.join(ROOT, "templates", "ai_companion.html"), encoding="utf-8").read(),
    "no API key hard-coded": not re.search(r"(?:sk-[A-Za-z0-9]{20,}|sk-or-v1-[A-Za-z0-9]{20,})", source),
}
for name, passed in checks.items():
    print(("PASS" if passed else "FAIL") + ": " + name)
    if not passed:
        raise SystemExit(1)

readme = os.path.join(ROOT, "AI_ENGINE_SETUP_2026-10-13.md")
if not os.path.exists(readme):
    print("FAIL: missing AI engine setup documentation")
    raise SystemExit(1)
print("PASS: AI engine static verification")
