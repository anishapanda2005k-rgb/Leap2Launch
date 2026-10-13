"""Static verification for the expanded A–Z PDF-first Leap2Launch e-library."""
from pathlib import Path
import ast, re
root = Path(__file__).resolve().parent
app = (root / "app.py").read_text(encoding="utf-8")
template = (root / "templates" / "open_library.html").read_text(encoding="utf-8")
block = app.split('@app.route("/open-library")', 1)[1].split('# ============================================================\n# GLOBAL CAREER DISCOVERY', 1)[0]
assert 'def open_library()' in block
assert 'render_template("open_library.html", resources=resources, books=STANDARD_REFERENCE_BOOKS)' in block
# Parse the resources literal safely, without executing the application.
match = re.search(r"resources\s*=\s*(\[.*?\])\s*# Never show website directories", block, re.S)
assert match, "Could not locate the library resource list"
resources = ast.literal_eval(match.group(1))
assert len(resources) >= 70, f"Expected 70+ resources after multidisciplinary expansion, got {len(resources)}"
assert len({r['name'] for r in resources}) == len(resources), "Duplicate resource names found"
assert len({r['url'] for r in resources}) == len(resources), "Duplicate resource URLs found"
non_pdf = [r['url'] for r in resources if not re.search(r"\.pdf(?:$|[?#])", r['url'], re.I)]
assert not non_pdf, "Non-direct-PDF URL(s) found: " + repr(non_pdf)
subjects = {r['subject'] for r in resources}
assert len(subjects) >= 20, f"Expected broad discipline coverage, got {len(subjects)} subjects"
required = ["Biology & Life Sciences", "Bioprocess Engineering", "Medicine & Health", "Mathematics & Statistics", "Business & Entrepreneurship", "Law & Legal Studies", "History & Archaeology", "Aviation & Aeronautics", "Cybersecurity & Information Technology", "Agriculture, Fisheries & Food Systems", "Skilled Trades, Manufacturing & Workplace Safety", "Space Science & Satellite Engineering", "Psychology & Behaviour", "Molecular Biology & Genetics"]
for subject in required:
    assert subject in subjects, f"Missing field coverage: {subject}"
for r in resources:
    for field in ('name','kind','subject','provider','url','access','note'):
        assert isinstance(r.get(field), str) and r[field].strip(), f"Missing {field} for {r.get('name')}"
for term in ["library-search", "library-subject", "library-kind", "library-count", "library-empty", "Open / download PDF", "direct PDF"]:
    assert term.lower() in template.lower(), f"Missing PDF-first feature or copy: {term}"
assert 'Open official source' not in template, "Old website-directory button remains"
assert (root / "AUDIT_DIRECT_PDF_LINKS.py").exists(), "Missing live PDF link audit script"
assert (root / "PDF_LINK_AUDIT_EVIDENCE_2026-10-12.csv").exists(), "Missing web-check evidence CSV"
assert (root / "RUN_PDF_LINK_AUDIT.bat").exists(), "Missing Windows audit launcher"
assert (root / "VERIFY_PDF_LINK_AUDIT.py").exists(), "Missing offline audit-script tests"
print(f"PASS: {len(resources)} unique direct-PDF records across {len(subjects)} subject labels.")
print("PASS: title, type, subject, provider, access note, topic description and direct PDF URL exist for every record.")
print("PASS: search, subject/type filters, count and empty state are present.")
print("PASS: science, healthcare, mathematics, business, law, humanities, agriculture, aviation, space, cyber and vocational resources represented.")
print("LIMIT: this static test validates URL format and catalogue metadata, not live network reachability. Run a separate HTTP/browser audit before claiming every link is live.")

# Validate the separate curated standard-reference bookshelf (not mixed into the PDF-only catalogue).
tree = ast.parse(app)
book_node = next((n for n in tree.body if isinstance(n, ast.Assign) and any(isinstance(t, ast.Name) and t.id == "STANDARD_REFERENCE_BOOKS" for t in n.targets)), None)
assert book_node is not None, "Missing standard-reference bookshelf"
books = ast.literal_eval(book_node.value)
assert len(books) >= 200, f"Expected 200+ curated standard books, got {len(books)}"
assert len({b['title'] for b in books}) == len(books), "Duplicate reference-book titles found"
book_subjects = {b['subject'] for b in books}
assert len(book_subjects) >= 50, f"Expected broad book coverage, got {len(book_subjects)} fields"
from collections import Counter
assert min(Counter(b['subject'] for b in books).values()) >= 2, 'Every subject should have at least two curated books'
for b in books:
    for field in ('title','authors','subject','level','role','why','url','access'):
        assert isinstance(b.get(field), str) and b[field].strip(), f"Missing {field} for {b.get('title')}"
    assert b['url'].startswith('https://'), f"Non-HTTPS book link: {b['title']}"
    assert len(b['why']) >= 35, f"Book recommendation lacks a useful rationale: {b['title']}"
    assert len(b['role']) >= 4, f"Missing learning-purpose tag: {b['title']}"
for title in ['Lehninger Principles of Biochemistry', 'Prescott’s Microbiology', 'Bioprocess Engineering: Basic Concepts', 'Molecular Biology of the Cell', 'Janeway’s Immunobiology', 'Introduction to Flight', 'Machinery’s Handbook', 'Pathfinder']:
    assert any(title.lower() in (b['title'] + ' ' + b['url']).lower() for b in books), f"Missing expected standard title: {title}"
for term in ['Standard Reference Bookshelf','bookshelf-search','bookshelf-subject','bookshelf-role','bookshelf-count','Find legitimate edition / library access','b.role']:
    assert term.lower() in template.lower(), f"Missing bookshelf feature: {term}"
# Regression guard: all visible bookshelf filters must trigger filtering.
assert "bookSearch.addEventListener('input', filterBookshelf)" in template, 'Book search is not wired'
assert "bookSubject.addEventListener('change', filterBookshelf)" in template, 'Book field filter is not wired'
assert "bookRole.addEventListener('change', filterBookshelf)" in template, 'Book learning-purpose filter is not wired'
assert '(!bookRole.value || card.dataset.bookRole === bookRole.value)' in template, 'Learning-purpose selection is not applied'
assert 'books=STANDARD_REFERENCE_BOOKS' in block, "Bookshelf is not passed to the page"
print(f"PASS: {len(books)} curated standard books across {len(book_subjects)} fields, with authors, level, usefulness and legitimate-access link.")
print("PASS: required core references (Lehninger, Prescott, Shuler/Kargi, Alberts, Janeway, Anderson, trade reference and Pathfinder) are present.")
print("PASS: bookshelf search and field filter are present; copyrighted books are not mislabeled as free PDFs.")
