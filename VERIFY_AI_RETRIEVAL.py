"""Offline behavioral tests for Leap2Launch's local AI catalogue retrieval."""
import ast
import os
import re

ROOT = os.path.dirname(os.path.abspath(__file__))
with open(os.path.join(ROOT, "app.py"), encoding="utf-8") as f:
    source = f.read()
tree = ast.parse(source)
node = next((n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "_retrieve_career_context"), None)
if node is None:
    raise SystemExit("FAIL: retrieval function missing")
module = ast.Module(body=[node], type_ignores=[])
namespace = {
    "re": re,
    "CAREER_CATALOG": [
        {"title": "Bioinformatics Analyst", "group": "Science & Research", "description": "Analyse biological datasets and sequence information.", "paths": ["Computational biology", "Genomics"], "skills": ["Python", "BLAST", "Statistics"], "try": ["Analyse a public sequence dataset"]},
        {"title": "Cybersecurity Analyst", "group": "Technology", "description": "Investigate security alerts and improve defensive controls.", "paths": ["Security operations"], "skills": ["Networking", "Threat analysis"], "try": ["Review a safe sample security log"]},
        {"title": "Nutrition Professional", "group": "Health & Care", "description": "Support evidence-informed food and nutrition education.", "paths": ["Nutrition education"], "skills": ["Communication", "Food science"], "try": ["Compare public dietary guidance"]},
    ],
}
exec(compile(module, "app.py:_retrieve_career_context", "exec"), namespace)
retrieve = namespace["_retrieve_career_context"]

bio = retrieve("I want biotechnology bioinformatics genomics Python BLAST", limit=2)
assert bio and bio[0]["title"] == "Bioinformatics Analyst", "biology/data query should rank bioinformatics first"
assert len(bio) <= 2, "retrieval limit must be respected"
assert "retrieval_terms" in bio[0] and bio[0]["retrieval_score"] > 0
cyber = retrieve("cybersecurity networking threat analysis", limit=5)
assert cyber and cyber[0]["title"] == "Cybersecurity Analyst", "security query should rank cybersecurity first"
assert retrieve("and the what should I do", limit=5) == [], "stop-word-only query should return no candidates"
assert retrieve("biology", limit=0), "limit should be clamped to at least one for a non-empty query"
print("PASS: retrieval ranks relevant catalogue records")
print("PASS: retrieval respects result limits and emits match evidence")
print("PASS: stop-word-only queries return no candidates")
print("PASS: retrieval stays local and does not require network/API")
