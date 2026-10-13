"""Offline verification for the curated external learning directory."""
import os
import sqlite3
import tempfile
from urllib.parse import urlparse
from learning_resource_catalog import RESOURCES, ensure_learning_resource_catalog

fd, path = tempfile.mkstemp(suffix=".sqlite3")
os.close(fd)
try:
    conn = sqlite3.connect(path)
    ensure_learning_resource_catalog(conn)
    conn.commit()
    first_count = conn.execute("SELECT COUNT(*) FROM external_learning_resources").fetchone()[0]
    ensure_learning_resource_catalog(conn)
    conn.commit()
    second_count = conn.execute("SELECT COUNT(*) FROM external_learning_resources").fetchone()[0]
    assert first_count == len(RESOURCES), (first_count, len(RESOURCES))
    assert second_count == first_count, "Seeding must be idempotent"
    domains = {r[0] for r in conn.execute("SELECT DISTINCT domain FROM external_learning_resources")}
    assert len(domains) >= 40, len(domains)
    assert first_count >= 122, first_count
    individually_checked = conn.execute("SELECT COUNT(*) FROM external_learning_resources WHERE source_checked_at='2026-10-12'").fetchone()[0]
    assert individually_checked >= 55, individually_checked
    for column in ("availability_note", "duration_note", "fee_note", "source_checked_at"):
        assert column in {row[1] for row in conn.execute("PRAGMA table_info(external_learning_resources)")}, column
    for term in ("yoga", "nutritionist", "cybersecurity", "aerospace", "archaeology", "space research"):
        count = conn.execute(
            "SELECT COUNT(*) FROM external_learning_resources WHERE lower(domain) LIKE ? OR lower(title) LIKE ? OR lower(keywords) LIKE ?",
            (f"%{term}%", f"%{term}%", f"%{term}%"),
        ).fetchone()[0]
        assert count > 0, f"No directory entry found for required topic: {term}"
    urls = [r[0] for r in conn.execute("SELECT url FROM external_learning_resources")]
    assert all(urlparse(u).scheme == "https" and urlparse(u).netloc for u in urls)
    print(f"PASS: {first_count} entries; {len(domains)} subject labels; {individually_checked} individual course/resource pages have source-check metadata; repeat seeding is idempotent; required topic searches and HTTPS URLs checked.")
    conn.close()
finally:
    os.remove(path)

# Upgrade test: an existing project database with the previous schema must be preserved.
fd, legacy_path = tempfile.mkstemp(suffix=".sqlite3")
os.close(fd)
try:
    legacy = sqlite3.connect(legacy_path)
    legacy.execute("""CREATE TABLE external_learning_resources (
        id INTEGER PRIMARY KEY AUTOINCREMENT, domain TEXT NOT NULL, title TEXT NOT NULL,
        provider TEXT NOT NULL, resource_type TEXT NOT NULL, description TEXT NOT NULL,
        access_note TEXT NOT NULL, certificate_note TEXT NOT NULL, url TEXT NOT NULL,
        keywords TEXT DEFAULT '', last_reviewed TEXT NOT NULL,
        status TEXT NOT NULL DEFAULT 'Active', UNIQUE(domain,title))""")
    legacy.execute("""INSERT INTO external_learning_resources
        (domain,title,provider,resource_type,description,access_note,certificate_note,url,keywords,last_reviewed,status)
        VALUES('Test','Preserved legacy row','Provider','Course','Description','Free','Check','https://example.org','test','2026-10-01','Active')""")
    ensure_learning_resource_catalog(legacy)
    legacy.commit()
    migrated_columns = {row[1] for row in legacy.execute("PRAGMA table_info(external_learning_resources)")}
    assert {"availability_note", "duration_note", "fee_note", "source_checked_at"} <= migrated_columns
    assert legacy.execute("SELECT COUNT(*) FROM external_learning_resources WHERE title='Preserved legacy row'").fetchone()[0] == 1
    assert legacy.execute("SELECT COUNT(*) FROM external_learning_resources").fetchone()[0] == len(RESOURCES) + 1
    legacy.close()
    print("PASS: legacy database schema upgrades without losing existing rows.")
finally:
    os.remove(legacy_path)
