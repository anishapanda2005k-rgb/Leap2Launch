# ============================================================
# Leap2Launch - GAME + CERTIFICATE INTEGRATION INSTALLER
# ============================================================
#
# SAVE THIS FILE AS:
# C:\Users\syama\PycharmProjects\PythonProject5\install_games.py
#
# THEN RUN:
# python install_games.py
#
# It will:
# 1. Patch app_backup_old.py automatically
# 2. Add PCR Master game routes
# 3. Add Delivery Dash game routes
# 4. Add game-result/evidence saving
# 5. Add certificate upload support
# 6. Create the required game templates
# 7. Create certificate upload folders
#
# ============================================================

from pathlib import Path
import re
import shutil

BASE_DIR = Path(__file__).resolve().parent
APP_FILE = BASE_DIR / "app_backup_old.py"
TEMPLATES = BASE_DIR / "templates"
STATIC = BASE_DIR / "static"

GAME_BIO = TEMPLATES / "games" / "biotech"
GAME_BBA = TEMPLATES / "games" / "bba"

CERT_DIR = STATIC / "uploads" / "certificates"
GAME_BIO.mkdir(parents=True, exist_ok=True)
GAME_BBA.mkdir(parents=True, exist_ok=True)
CERT_DIR.mkdir(parents=True, exist_ok=True)

if not APP_FILE.exists():
    raise SystemExit(
        f"\napp_backup_old.py not found.\nExpected:\n{APP_FILE}\n"
    )

# ------------------------------------------------------------
# BACKUP
# ------------------------------------------------------------

backup = BASE_DIR / "app_before_game_integration.py"

if not backup.exists():
    shutil.copy2(APP_FILE, backup)
    print(f"[OK] Backup created: {backup.name}")
else:
    print("[OK] Existing backup found.")

# ------------------------------------------------------------
# APP.PY INTEGRATION
# ------------------------------------------------------------

app_code = APP_FILE.read_text(encoding="utf-8")

MARKER = "# ================= Leap2Launch GAME + CERTIFICATE INTEGRATION ================="

if MARKER in app_code:
    print("[OK] Game integration already exists in app_backup_old.py")
else:

    integration = r'''

# ================= Leap2Launch GAME + CERTIFICATE INTEGRATION =================

from flask import send_file
from werkzeug.utils import secure_filename
import json
import uuid
from datetime import datetime


GAME_CERT_ALLOWED = {
    "pdf",
    "png",
    "jpg",
    "jpeg",
    "webp"
}


def ensure_game_schema():
    """
    Adds the tables/columns needed by the games and certificate uploads.
    Safe to run repeatedly.
    """

    db = get_db()

    # Certificate upload columns
    try:
        db.execute(
            "ALTER TABLE certificates ADD COLUMN file_path TEXT"
        )
    except Exception:
        pass

    try:
        db.execute(
            "ALTER TABLE certificates ADD COLUMN file_type TEXT"
        )
    except Exception:
        pass

    # Game results
    db.execute("""
        CREATE TABLE IF NOT EXISTS game_results (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            game_key TEXT NOT NULL,
            game_name TEXT NOT NULL,
            department TEXT,
            score INTEGER DEFAULT 0,
            xp_earned INTEGER DEFAULT 0,
            mistakes INTEGER DEFAULT 0,
            time_taken INTEGER DEFAULT 0,
            result_data TEXT,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # Skill evidence
    db.execute("""
        CREATE TABLE IF NOT EXISTS skill_evidence (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            student_id INTEGER NOT NULL,
            skill TEXT NOT NULL,
            evidence_type TEXT,
            evidence TEXT,
            status TEXT DEFAULT 'Pending',
            score INTEGER DEFAULT 0,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP
        )
    """)

    db.commit()


def game_student():
    """
    Returns the currently logged-in student.
    Uses the existing Leap2Launch student_required/session system.
    """

    try:
        student = get_current_student()
        if student:
            return student
    except Exception:
        pass

    try:
        student = get_logged_in_student()
        if student:
            return student
    except Exception:
        pass

    try:
        student = ensure_student_for_user()
        if student:
            return student
    except Exception:
        pass

    return None


def add_game_evidence(
    student_id,
    skill,
    game_name,
    score,
    result_data,
    xp
):
    db = get_db()

    evidence_text = json.dumps(
        {
            "game": game_name,
            "score": score,
            "xp": xp,
            "result": result_data
        },
        default=str
    )

    # Do NOT automatically verify the skill.
    #
    # Game evidence becomes Pending.
    # Faculty can later verify it.

    existing = db.execute(
        """
        SELECT id, status
        FROM skill_evidence
        WHERE student_id = ?
        AND skill = ?
        AND evidence_type = 'Game'
        ORDER BY id DESC
        LIMIT 1
        """,
        (student_id, skill)
    ).fetchone()

    if existing:
        db.execute(
            """
            UPDATE skill_evidence
            SET evidence = ?,
                score = ?,
                status = CASE
                    WHEN status = 'Verified' THEN 'Verified'
                    ELSE 'Pending'
                END
            WHERE id = ?
            """,
            (
                evidence_text,
                score,
                existing["id"]
            )
        )
    else:
        db.execute(
            """
            INSERT INTO skill_evidence
            (
                student_id,
                skill,
                evidence_type,
                evidence,
                status,
                score
            )
            VALUES (?, ?, ?, ?, ?, ?)
            """,
            (
                student_id,
                skill,
                "Game",
                evidence_text,
                "Pending",
                score
            )
        )

    # Also create/update faculty verification request.
    try:
        verification = db.execute(
            """
            SELECT id, status
            FROM skill_verification
            WHERE student_id = ?
            AND skill = ?
            LIMIT 1
            """,
            (student_id, skill)
        ).fetchone()

        if verification:
            if verification["status"] != "Verified":
                db.execute(
                    """
                    UPDATE skill_verification
                    SET status = 'Pending',
                        evidence_type = 'Game',
                        evidence = ?
                    WHERE id = ?
                    """,
                    (
                        evidence_text,
                        verification["id"]
                    )
                )
        else:
            db.execute(
                """
                INSERT INTO skill_verification
                (
                    student_id,
                    skill,
                    status,
                    evidence_type,
                    evidence
                )
                VALUES (?, ?, 'Pending', 'Game', ?)
                """,
                (
                    student_id,
                    skill,
                    evidence_text
                )
            )

    except Exception:
        pass

    db.commit()


def award_game_xp(student_id, xp):
    db = get_db()

    try:
        db.execute(
            """
            UPDATE students
            SET xp = COALESCE(xp, 0) + ?
            WHERE id = ?
            """,
            (xp, student_id)
        )
        db.commit()
    except Exception:
        pass


# ------------------------------------------------------------
# PCR MASTER
# Biotechnology → Molecular Lab → Games
# ------------------------------------------------------------

@app.route("/games/biotech/pcr-master")
@student_required
def pcr_master_game():

    ensure_game_schema()

    return render_template(
        "games/biotech/pcr_master.html"
    )


@app.route(
    "/games/biotech/pcr-master/complete",
    methods=["POST"]
)
@student_required
def complete_pcr_master():

    ensure_game_schema()

    student = game_student()

    if not student:
        return redirect(url_for("login"))

    try:
        score = int(request.form.get("score", 0))
    except Exception:
        score = 0

    try:
        mistakes = int(request.form.get("mistakes", 0))
    except Exception:
        mistakes = 0

    try:
        time_taken = int(request.form.get("time_taken", 0))
    except Exception:
        time_taken = 0

    result_data_raw = request.form.get(
        "result_data",
        "{}"
    )

    try:
        result_data = json.loads(result_data_raw)
    except Exception:
        result_data = {
            "details": result_data_raw
        }

    # PCR score is out of 100.
    score = max(0, min(100, score))

    # XP is based on demonstrated performance.
    if score >= 90:
        xp = 150
    elif score >= 75:
        xp = 120
    elif score >= 60:
        xp = 90
    elif score >= 40:
        xp = 60
    else:
        xp = 30

    db = get_db()

    db.execute(
        """
        INSERT INTO game_results
        (
            student_id,
            game_key,
            game_name,
            department,
            score,
            xp_earned,
            mistakes,
            time_taken,
            result_data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student["id"],
            "pcr_master",
            "PCR Master",
            "Biotechnology",
            score,
            xp,
            mistakes,
            time_taken,
            json.dumps(result_data, default=str)
        )
    )

    db.commit()

    award_game_xp(
        student["id"],
        xp
    )

    add_game_evidence(
        student_id=student["id"],
        skill="PCR and Molecular Biology",
        game_name="PCR Master",
        score=score,
        result_data={
            "mistakes": mistakes,
            "time_taken": time_taken,
            **result_data
        },
        xp=xp
    )

    return render_template(
        "game_result.html",
        game_name="PCR Master",
        department="Biotechnology",
        score=score,
        xp=xp,
        mistakes=mistakes,
        time_taken=time_taken,
        skill="PCR and Molecular Biology"
    )


# ------------------------------------------------------------
# DELIVERY DASH
# BBA / Management → Business Center → Games
# ------------------------------------------------------------

@app.route("/games/bba/delivery-dash")
@student_required
def delivery_dash_game():

    ensure_game_schema()

    return render_template(
        "games/bba/delivery_dash.html"
    )


@app.route(
    "/games/bba/delivery-dash/complete",
    methods=["POST"]
)
@student_required
def complete_delivery_dash():

    ensure_game_schema()

    student = game_student()

    if not student:
        return redirect(url_for("login"))

    try:
        score = int(request.form.get("score", 0))
    except Exception:
        score = 0

    try:
        mistakes = int(request.form.get("mistakes", 0))
    except Exception:
        mistakes = 0

    try:
        time_taken = int(request.form.get("time_taken", 0))
    except Exception:
        time_taken = 0

    result_data_raw = request.form.get(
        "result_data",
        "{}"
    )

    try:
        result_data = json.loads(result_data_raw)
    except Exception:
        result_data = {
            "details": result_data_raw
        }

    score = max(0, min(100, score))

    if score >= 90:
        xp = 150
    elif score >= 75:
        xp = 120
    elif score >= 60:
        xp = 90
    elif score >= 40:
        xp = 60
    else:
        xp = 30

    db = get_db()

    db.execute(
        """
        INSERT INTO game_results
        (
            student_id,
            game_key,
            game_name,
            department,
            score,
            xp_earned,
            mistakes,
            time_taken,
            result_data
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
        (
            student["id"],
            "delivery_dash",
            "Delivery Dash",
            "BBA / Management",
            score,
            xp,
            mistakes,
            time_taken,
            json.dumps(result_data, default=str)
        )
    )

    db.commit()

    award_game_xp(
        student["id"],
        xp
    )

    add_game_evidence(
        student_id=student["id"],
        skill="Operations and Decision Making",
        game_name="Delivery Dash",
        score=score,
        result_data={
            "mistakes": mistakes,
            "time_taken": time_taken,
            **result_data
        },
        xp=xp
    )

    return render_template(
        "game_result.html",
        game_name="Delivery Dash",
        department="BBA / Management",
        score=score,
        xp=xp,
        mistakes=mistakes,
        time_taken=time_taken,
        skill="Operations and Decision Making"
    )


# ------------------------------------------------------------
# CERTIFICATE UPLOAD
# ------------------------------------------------------------

@app.route(
    "/certificate/upload",
    methods=["POST"]
)
@student_required
def upload_certificate_file():

    ensure_game_schema()

    student = game_student()

    if not student:
        return redirect(url_for("login"))

    name = request.form.get(
        "name",
        ""
    ).strip()

    issuer = request.form.get(
        "issuer",
        ""
    ).strip()

    year = request.form.get(
        "year",
        ""
    ).strip()

    certificate_file = request.files.get(
        "certificate_file"
    )

    if not name:
        return redirect(
            url_for(
                "profile_details"
            )
        )

    file_path = None
    file_type = None

    if certificate_file and certificate_file.filename:

        original_name = secure_filename(
            certificate_file.filename
        )

        if "." in original_name:
            extension = (
                original_name
               .rsplit(".", 1)[1]
               .lower()
            )
        else:
            extension = ""

        if extension not in GAME_CERT_ALLOWED:
            return redirect(
                url_for(
                    "profile_details"
                )
            )

        unique_name = (
            f"{student['id']}_"
            f"{uuid.uuid4().hex}."
            f"{extension}"
        )

        save_path = CERT_DIR / unique_name

        certificate_file.save(
            str(save_path)
        )

        file_path = (
            f"uploads/certificates/"
            f"{unique_name}"
        )

        file_type = extension

    db = get_db()

    db.execute(
        """
        INSERT INTO certificates
        (
            student_id,
            name,
            issuer,
            year,
            file_path,
            file_type
        )
        VALUES (?, ?, ?, ?, ?, ?)
        """,
        (
            student["id"],
            name,
            issuer,
            year,
            file_path,
            file_type
        )
    )

    db.commit()

    return redirect(
        url_for(
            "profile_details"
        )
    )


@app.route(
    "/certificate/<int:certificate_id>/view"
)
@student_required
def view_certificate(certificate_id):

    ensure_game_schema()

    student = game_student()

    if not student:
        return redirect(url_for("login"))

    db = get_db()

    certificate = db.execute(
        """
        SELECT *
        FROM certificates
        WHERE id = ?
        AND student_id = ?
        LIMIT 1
        """,
        (
            certificate_id,
            student["id"]
        )
    ).fetchone()

    if not certificate:
        return "Certificate not found", 404

    if not certificate["file_path"]:
        return "No uploaded certificate file.", 404

    full_path = (
        STATIC /
        certificate["file_path"]
    )

    if not full_path.exists():
        return "Certificate file missing.", 404

    return send_file(
        str(full_path)
    )


@app.route(
    "/certificate/<int:certificate_id>/delete",
    methods=["POST"]
)
@student_required
def delete_certificate(certificate_id):

    ensure_game_schema()

    student = game_student()

    if not student:
        return redirect(url_for("login"))

    db = get_db()

    certificate = db.execute(
        """
        SELECT *
        FROM certificates
        WHERE id = ?
        AND student_id = ?
        LIMIT 1
        """,
        (
            certificate_id,
            student["id"]
        )
    ).fetchone()

    if certificate:

        if certificate["file_path"]:

            file_path = (
                STATIC /
                certificate["file_path"]
            )

            try:
                if file_path.exists():
                    file_path.unlink()
            except Exception:
                pass

        db.execute(
            """
            DELETE FROM certificates
            WHERE id = ?
            AND student_id = ?
            """,
            (
                certificate_id,
                student["id"]
            )
        )

        db.commit()

    return redirect(
        url_for(
            "profile_details"
        )
    )


# ------------------------------------------------------------
# GAME HISTORY
# ------------------------------------------------------------

@app.route("/games/history")
@student_required
def game_history():

    ensure_game_schema()

    student = game_student()

    if not student:
        return redirect(url_for("login"))

    db = get_db()

    results = db.execute(
        """
        SELECT *
        FROM game_results
        WHERE student_id = ?
        ORDER BY id DESC
        """,
        (student["id"],)
    ).fetchall()

    return render_template(
        "game_history.html",
        results=results
    )


# ================= END Leap2Launch GAME + CERTIFICATE INTEGRATION =================
'''

    # Insert BEFORE Flask's main block.
    main_match = re.search(
        r'\nif __name__\s*==\s*[\'"]__main__[\'"]\s*:',
        app_code
    )

    if main_match:
        position = main_match.start()
        app_code = (
            app_code[:position]
            + "\n"
            + integration
            + "\n"
            + app_code[position:]
        )
    else:
        app_code += "\n" + integration + "\n"

    APP_FILE.write_text(
        app_code,
        encoding="utf-8"
    )

    print("[OK] app_backup_old.py patched.")

# ------------------------------------------------------------
# PCR MASTER HTML
# ------------------------------------------------------------

pcr_html = r'''<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>PCR Master | Leap2Launch</title>

<style>
* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background:
        radial-gradient(circle at top left, #172554, #07111f 55%, #020617);
    color: white;
    min-height: 100vh;
}

.container {
    width: min(1100px, 94%);
    margin: auto;
    padding: 35px 0 60px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    gap: 20px;
    margin-bottom: 25px;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 20px;
    background: rgba(59,130,246,.18);
    border: 1px solid rgba(96,165,250,.35);
    color: #93c5fd;
    font-size: 13px;
}

h1 {
    margin: 10px 0;
    font-size: 38px;
}

.subtitle {
    color: #cbd5e1;
}

.panel {
    background: rgba(15,23,42,.82);
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 22px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 20px 50px rgba(0,0,0,.22);
}

.progress {
    height: 10px;
    background: #1e293b;
    border-radius: 20px;
    overflow: hidden;
    margin: 18px 0;
}

.progress-bar {
    height: 100%;
    width: 20%;
    background: linear-gradient(90deg,#38bdf8,#818cf8);
    transition: .3s;
}

.stage {
    display: none;
}

.stage.active {
    display: block;
}

.reagents {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(160px,1fr));
    gap: 14px;
    margin-top: 20px;
}

.reagent {
    padding: 20px;
    border-radius: 16px;
    background: #111827;
    border: 1px solid #334155;
    cursor: pointer;
    transition: .2s;
}

.reagent:hover {
    transform: translateY(-3px);
    border-color: #60a5fa;
}

.reagent.selected {
    border-color: #22c55e;
    background: rgba(34,197,94,.12);
}

.machine {
    border: 2px solid #334155;
    border-radius: 20px;
    padding: 25px;
    background: #020617;
}

.cycles {
    display: grid;
    grid-template-columns: repeat(3,1fr);
    gap: 12px;
}

.cycle {
    padding: 18px;
    border-radius: 15px;
    background: #111827;
    border: 1px solid #334155;
}

input,
select,
textarea {
    width: 100%;
    padding: 13px;
    margin-top: 8px;
    border-radius: 10px;
    border: 1px solid #475569;
    background: #0f172a;
    color: white;
}

button {
    border: 0;
    border-radius: 12px;
    padding: 13px 20px;
    cursor: pointer;
    font-weight: bold;
    background: #3b82f6;
    color: white;
}

button:hover {
    opacity: .9;
}

.next {
    margin-top: 25px;
}

.gel {
    display: flex;
    justify-content: center;
    align-items: end;
    gap: 25px;
    min-height: 250px;
    padding: 30px;
    border-radius: 18px;
    background:
        linear-gradient(90deg,
            rgba(15,23,42,.8),
            rgba(30,64,175,.2),
            rgba(15,23,42,.8));
    border: 1px solid #334155;
}

.lane {
    width: 70px;
    height: 180px;
    background: rgba(30,41,59,.7);
    border-radius: 8px;
    position: relative;
}

.band {
    position: absolute;
    left: 8px;
    right: 8px;
    height: 13px;
    border-radius: 20px;
    background: #67e8f9;
    box-shadow: 0 0 18px #67e8f9;
}

.stat-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit,minmax(150px,1fr));
    gap: 12px;
}

.stat {
    background: #111827;
    border-radius: 15px;
    padding: 18px;
    text-align: center;
}

.stat strong {
    display: block;
    font-size: 26px;
    margin-top: 5px;
}

.hint {
    margin-top: 15px;
    padding: 15px;
    background: rgba(245,158,11,.1);
    border: 1px solid rgba(245,158,11,.3);
    border-radius: 12px;
    color: #fde68a;
}

@media(max-width:700px) {
    h1 {
        font-size: 28px;
    }

    .cycles {
        grid-template-columns: 1fr;
    }
}
</style>
</head>

<body>

<div class="container">

    <div class="header">
        <div>
            <span class="badge">🧬 Biotechnology → Molecular Lab → Game</span>
            <h1>PCR Master</h1>
            <div class="subtitle">
                Demonstrate your understanding of PCR through a virtual molecular lab.
            </div>
        </div>

        <div style="font-size:42px;">🤖</div>
    </div>

    <div class="panel">

        <div>
            <strong id="stageName">Stage 1 — Entry</strong>
        </div>

        <div class="progress">
            <div class="progress-bar" id="progressBar"></div>
        </div>

        <div class="stat-grid">
            <div class="stat">
                Score
                <strong id="score">0</strong>
            </div>

            <div class="stat">
                Mistakes
                <strong id="mistakes">0</strong>
            </div>

            <div class="stat">
                Time
                <strong id="timer">0</strong>
            </div>
        </div>

    </div>

    <!-- ENTRY -->

    <div class="panel stage active" id="stage1">

        <h2>🧬 Welcome to the Molecular Lab</h2>

        <p>
            Your task is to successfully complete a PCR workflow:
        </p>

        <ol>
            <li>Prepare the PCR reaction.</li>
            <li>Program the thermocycler.</li>
            <li>Run DNA amplification.</li>
            <li>Interpret the agarose gel.</li>
        </ol>

        <div class="hint">
            🤖 Hint: Think about what components are required for a PCR reaction before proceeding.
        </div>

        <button class="next" onclick="nextStage(2)">
            Enter Molecular Lab →
        </button>

    </div>


    <!-- PCR SETUP -->

    <div class="panel stage" id="stage2">

        <h2>🧪 PCR Setup</h2>

        <p>
            Select all essential PCR components.
        </p>

        <div class="reagents">

            <div class="reagent" data-correct="true"
                 onclick="selectReagent(this)">
                DNA Template
            </div>

            <div class="reagent" data-correct="true"
                 onclick="selectReagent(this)">
                Forward Primer
            </div>

            <div class="reagent" data-correct="true"
                 onclick="selectReagent(this)">
                Reverse Primer
            </div>

            <div class="reagent" data-correct="true"
                 onclick="selectReagent(this)">
                dNTPs
            </div>

            <div class="reagent" data-correct="true"
                 onclick="selectReagent(this)">
                DNA Polymerase
            </div>

            <div class="reagent" data-correct="true"
                 onclick="selectReagent(this)">
                Buffer + Mg²⁺
            </div>

            <div class="reagent" data-correct="false"
                 onclick="selectReagent(this)">
                Lipase
            </div>

            <div class="reagent" data-correct="false"
                 onclick="selectReagent(this)">
                Starch
            </div>

        </div>

        <button class="next" onclick="checkPCRSetup()">
            Check Reaction →
        </button>

        <div id="setupMessage"></div>

    </div>


    <!-- THERMOCYCLER -->

    <div class="panel stage" id="stage3">

        <h2>🌡️ Thermocycler</h2>

        <p>
            Set the three major PCR stages.
        </p>

        <div class="cycles">

            <div class="cycle">
                <strong>Denaturation</strong>

                <select id="denaturation">
                    <option value="">Select</option>
                    <option value="94">94°C</option>
                    <option value="95">95°C</option>
                    <option value="60">60°C</option>
                    <option value="72">72°C</option>
                </select>
            </div>

            <div class="cycle">
                <strong>Annealing</strong>

                <select id="annealing">
                    <option value="">Select</option>
                    <option value="95">95°C</option>
                    <option value="60">60°C</option>
                    <option value="72">72°C</option>
                </select>
            </div>

            <div class="cycle">
                <strong>Extension</strong>

                <select id="extension">
                    <option value="">Select</option>
                    <option value="95">95°C</option>
                    <option value="60">60°C</option>
                    <option value="72">72°C</option>
                </select>
            </div>

        </div>

        <button class="next" onclick="checkThermocycler()">
            Start Thermocycler →
        </button>

        <div id="thermoMessage"></div>

    </div>


    <!-- AMPLIFICATION -->

    <div class="panel stage" id="stage4">

        <h2>🔬 DNA Amplification</h2>

        <p>
            PCR amplification occurs through repeated cycles of denaturation,
            annealing and extension.
        </p>

        <div style="
            font-size:70px;
            text-align:center;
            margin:35px;
        ">
            🧬
        </div>

        <div id="amplificationText"
             style="text-align:center;font-size:20px;">
            Ready...
        </div>

        <button class="next" onclick="runAmplification()">
            Run 30 Cycles →
        </button>

    </div>


    <!-- GEL -->

    <div class="panel stage" id="stage5">

        <h2>🧫 Gel Electrophoresis</h2>

        <p>
            Examine the amplified DNA and interpret the gel.
        </p>

        <div class="gel">

            <div>
                <div style="text-align:center;margin-bottom:8px;">
                    Ladder
                </div>

                <div class="lane">
                    <div class="band" style="bottom:140px;"></div>
                    <div class="band" style="bottom:110px;"></div>
                    <div class="band" style="bottom:80px;"></div>
                    <div class="band" style="bottom:55px;"></div>
                </div>
            </div>

            <div>
                <div style="text-align:center;margin-bottom:8px;">
                    Sample
                </div>

                <div class="lane" id="sampleLane">
                </div>
            </div>

        </div>

        <p style="margin-top:20px;">
            What does the sample indicate?
        </p>

        <select id="gelAnswer">
            <option value="">Select interpretation</option>
            <option value="correct">
                A clear amplified DNA product is present
            </option>

            <option value="wrong">
                No DNA was produced
            </option>

            <option value="wrong">
                The gel itself is the PCR reaction
            </option>
        </select>

        <button class="next" onclick="finishGel()">
            Analyze Result →
        </button>

        <div id="gelMessage"></div>

    </div>

</div>


<script>

let stage = 1;
let score = 0;
let mistakes = 0;
let startTime = Date.now();
let selectedReagents = new Set();

const stageNames = {
    1: "Stage 1 — Entry",
    2: "Stage 2 — PCR Setup",
    3: "Stage 3 — Thermocycler",
    4: "Stage 4 — DNA Amplification",
    5: "Stage 5 — Gel Electrophoresis"
};

function updateUI() {

    document
        .querySelectorAll(".stage")
        .forEach(x => x.classList.remove("active"));

    const current = document.getElementById(
        "stage" + stage
    );

    if (current) {
        current.classList.add("active");
    }

    document.getElementById(
        "stageName"
    ).textContent = stageNames[stage];

    document.getElementById(
        "progressBar"
    ).style.width = ((stage / 5) * 100) + "%";

    document.getElementById(
        "score"
    ).textContent = score;

    document.getElementById(
        "mistakes"
    ).textContent = mistakes;
}

function nextStage(number) {
    stage = number;
    updateUI();
}

function addScore(points) {
    score += points;
    score = Math.max(0, Math.min(100, score));
    updateUI();
}

function mistake() {
    mistakes++;
    score -= 5;
    score = Math.max(0, score);
    updateUI();
}

function selectReagent(element) {

    const name = element.textContent.trim();

    if (selectedReagents.has(name)) {
        selectedReagents.delete(name);
        element.classList.remove("selected");
    } else {
        selectedReagents.add(name);
        element.classList.add("selected");
    }
}

function checkPCRSetup() {

    const correct = [
        "DNA Template",
        "Forward Primer",
        "Reverse Primer",
        "dNTPs",
        "DNA Polymerase",
        "Buffer + Mg²⁺"
    ];

    let valid = true;

    correct.forEach(item => {

        if (!selectedReagents.has(item)) {
            valid = false;
        }
    });

    if (
        selectedReagents.has("Lipase") ||
        selectedReagents.has("Starch")
    ) {
        valid = false;
    }

    const message =
        document.getElementById("setupMessage");

    if (valid) {

        addScore(20);

        message.innerHTML =
            '<div class="hint">✓ Correct PCR reaction setup.</div>';

        setTimeout(() => {
            stage = 3;
            updateUI();
        }, 700);

    } else {

        mistake();

        message.innerHTML =
            '<div class="hint">🤖 Hint: Review the essential PCR reaction components.</div>';
    }
}

function checkThermocycler() {

    const d =
        document.getElementById("denaturation").value;

    const a =
        document.getElementById("annealing").value;

    const e =
        document.getElementById("extension").value;

    if (
        d === "95" &&
        a === "60" &&
        e === "72"
    ) {

        addScore(20);

        document.getElementById(
            "thermoMessage"
        ).innerHTML =
            '<div class="hint">✓ Thermocycler programmed correctly.</div>';

        setTimeout(() => {
            stage = 4;
            updateUI();
        }, 700);

    } else {

        mistake();

        document.getElementById(
            "thermoMessage"
        ).innerHTML =
            '<div class="hint">🤖 Hint: PCR uses denaturation, annealing and extension at different temperatures.</div>';
    }
}

function runAmplification() {

    const text =
        document.getElementById(
            "amplificationText"
        );

    let cycle = 0;

    const interval = setInterval(() => {

        cycle++;

        text.textContent =
            "PCR cycle " +
            cycle +
            " / 30 — DNA amplification in progress...";

        if (cycle >= 30) {

            clearInterval(interval);

            addScore(20);

            text.textContent =
                "✓ Amplification complete.";

            setTimeout(() => {

                stage = 5;
                updateUI();

                const lane =
                    document.getElementById(
                        "sampleLane"
                    );

                lane.innerHTML =
                    '<div class="band" style="bottom:105px;"></div>';

            }, 700);
        }

    }, 50);
}

function finishGel() {

    const answer =
        document.getElementById(
            "gelAnswer"
        ).value;

    const message =
        document.getElementById(
            "gelMessage"
        );

    if (answer === "correct") {

        addScore(20);

        message.innerHTML =
            '<div class="hint">✓ Correct interpretation.</div>';

        setTimeout(() => {
            submitResult();
        }, 700);

    } else {

        mistake();

        message.innerHTML =
            '<div class="hint">🤖 Hint: Compare the sample band with the DNA ladder.</div>';
    }
}

function submitResult() {

    const timeTaken =
        Math.floor(
            (Date.now() - startTime) / 1000
        );

    const form =
        document.createElement("form");

    form.method = "POST";

    form.action =
        "{{ url_for('complete_pcr_master') }}";

    const values = {
        score: score,
        mistakes: mistakes,
        time_taken: timeTaken,
        result_data: JSON.stringify({
            stage: "Gel Electrophoresis",
            selected_reagents:
                Array.from(selectedReagents),
            thermocycler: {
                denaturation:
                    document.getElementById("denaturation").value,
                annealing:
                    document.getElementById("annealing").value,
                extension:
                    document.getElementById("extension").value
            },
            completed: true
        })
    };

    Object.entries(values).forEach(
        ([key, value]) => {

            const input =
                document.createElement("input");

            input.type = "hidden";
            input.name = key;
            input.value = value;

            form.appendChild(input);
        }
    );

    document.body.appendChild(form);
    form.submit();
}

setInterval(() => {

    const seconds =
        Math.floor(
            (Date.now() - startTime) / 1000
        );

    document.getElementById(
        "timer"
    ).textContent = seconds;

}, 1000);

updateUI();

</script>

</body>
</html>
'''

(GAME_BIO / "pcr_master.html").write_text(
    pcr_html,
    encoding="utf-8"
)

print("[OK] PCR Master template created.")

# ------------------------------------------------------------
# DELIVERY DASH HTML
# ------------------------------------------------------------

delivery_html = r'''<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">

<title>Delivery Dash | Leap2Launch</title>

<style>

* {
    box-sizing: border-box;
}

body {
    margin: 0;
    font-family: Arial, sans-serif;
    background:
        radial-gradient(circle at top left,#312e81,#111827 55%,#020617);
    color: white;
    min-height: 100vh;
}

.container {
    width: min(1100px,94%);
    margin: auto;
    padding: 35px 0 60px;
}

.header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 25px;
}

.badge {
    display: inline-block;
    padding: 8px 14px;
    border-radius: 20px;
    background: rgba(129,140,248,.15);
    border: 1px solid rgba(129,140,248,.35);
    color: #c7d2fe;
    font-size: 13px;
}

h1 {
    font-size: 38px;
    margin: 10px 0;
}

.subtitle {
    color: #cbd5e1;
}

.panel {
    background: rgba(15,23,42,.86);
    border: 1px solid rgba(148,163,184,.18);
    border-radius: 22px;
    padding: 28px;
    margin-bottom: 20px;
    box-shadow: 0 20px 50px rgba(0,0,0,.25);
}

.stats {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(140px,1fr));
    gap: 12px;
    margin-bottom: 20px;
}

.stat {
    padding: 18px;
    border-radius: 15px;
    background: #111827;
    text-align: center;
}

.stat strong {
    display: block;
    font-size: 26px;
    margin-top: 5px;
}

.progress {
    height: 10px;
    background: #1e293b;
    border-radius: 20px;
    overflow: hidden;
}

.progress-bar {
    height: 100%;
    width: 20%;
    background: linear-gradient(90deg,#818cf8,#38bdf8);
    transition: .3s;
}

.scenario {
    display: none;
}

.scenario.active {
    display: block;
}

.options {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(220px,1fr));
    gap: 15px;
    margin-top: 25px;
}

.option {
    padding: 22px;
    background: #111827;
    border: 1px solid #334155;
    border-radius: 16px;
    cursor: pointer;
    transition: .2s;
}

.option:hover {
    transform: translateY(-3px);
    border-color: #818cf8;
}

button {
    border: 0;
    border-radius: 12px;
    padding: 13px 20px;
    background: #6366f1;
    color: white;
    font-weight: bold;
    cursor: pointer;
}

button:hover {
    opacity: .9;
}

.feedback {
    margin-top: 20px;
    padding: 15px;
    border-radius: 12px;
    display: none;
}

.good {
    display: block;
    background: rgba(34,197,94,.12);
    border: 1px solid rgba(34,197,94,.35);
    color: #bbf7d0;
}

.bad {
    display: block;
    background: rgba(239,68,68,.12);
    border: 1px solid rgba(239,68,68,.35);
    color: #fecaca;
}

.hint {
    padding: 15px;
    margin-top: 20px;
    border-radius: 12px;
    background: rgba(245,158,11,.1);
    border: 1px solid rgba(245,158,11,.3);
    color: #fde68a;
}

.vehicle {
    font-size: 70px;
    text-align: center;
    margin: 25px;
}

</style>

</head>

<body>

<div class="container">

    <div class="header">

        <div>

            <span class="badge">
                💼 BBA / Management → Business Center → Game
            </span>

            <h1>Delivery Dash</h1>

            <div class="subtitle">
                Make operational decisions under time,
                cost and customer-pressure constraints.
            </div>

        </div>

        <div style="font-size:45px;">
            🤖
        </div>

    </div>


    <div class="panel">

        <div class="stats">

            <div class="stat">
                Score
                <strong id="score">0</strong>
            </div>

            <div class="stat">
                Lives
                <strong id="lives">3</strong>
            </div>

            <div class="stat">
                Level
                <strong id="level">1</strong>
            </div>

            <div class="stat">
                Time
                <strong id="timer">0</strong>
            </div>

        </div>

        <div class="progress">
            <div
                class="progress-bar"
                id="progressBar">
            </div>
        </div>

    </div>


    <div
        class="panel scenario active"
        id="scenario1">

        <h2>Level 1 — Traffic Problem 🚦</h2>

        <p>
            A delivery vehicle is approaching heavy traffic.
            The customer deadline is close.
        </p>

        <div class="vehicle">
            🚚
        </div>

        <div class="options">

            <div
                class="option"
                onclick="choose(1,1)">
                Take the shorter route despite heavy traffic.
            </div>

            <div
                class="option"
                onclick="choose(1,2)">
                Take a slightly longer route with lower traffic.
            </div>

            <div
                class="option"
                onclick="choose(1,3)">
                Wait for traffic to disappear.
            </div>

        </div>

        <div id="feedback1" class="feedback"></div>

    </div>


    <div
        class="panel scenario"
        id="scenario2">

        <h2>Level 2 — Vehicle Selection 🚛</h2>

        <p>
            You have two deliveries: one urgent and one standard.
            Choose the most appropriate vehicle allocation.
        </p>

        <div class="options">

            <div
                class="option"
                onclick="choose(2,1)">
                Send the fastest vehicle to the urgent delivery.
            </div>

            <div
                class="option"
                onclick="choose(2,2)">
                Send both vehicles to the standard delivery.
            </div>

            <div
                class="option"
                onclick="choose(2,3)">
                Delay both deliveries.
            </div>

        </div>

        <div id="feedback2" class="feedback"></div>

    </div>


    <div
        class="panel scenario"
        id="scenario3">

        <h2>Level 3 — Cost vs Speed 💰</h2>

        <p>
            An express option costs more but significantly
            reduces delivery time.
        </p>

        <div class="options">

            <div
                class="option"
                onclick="choose(3,1)">
                Always select the cheapest option.
            </div>

            <div
                class="option"
                onclick="choose(3,2)">
                Compare the extra cost with the deadline risk.
            </div>

            <div
                class="option"
                onclick="choose(3,3)">
                Ignore the deadline.
            </div>

        </div>

        <div id="feedback3" class="feedback"></div>

    </div>


    <div
        class="panel scenario"
        id="scenario4">

        <h2>Level 4 — Customer Priority 📦</h2>

        <p>
            One customer has a strict deadline while another
            customer is flexible.
        </p>

        <div class="options">

            <div
                class="option"
                onclick="choose(4,1)">
                Prioritize the strict deadline.
            </div>

            <div
                class="option"
                onclick="choose(4,2)">
                Serve randomly.
            </div>

            <div
                class="option"
                onclick="choose(4,3)">
                Ignore customer deadlines.
            </div>

        </div>

        <div id="feedback4" class="feedback"></div>

    </div>


    <div
        class="panel scenario"
        id="scenario5">

        <h2>Level 5 — Final Operations Decision 🧠</h2>

        <p>
            A last-minute disruption has occurred.
            You must balance time, cost and service quality.
        </p>

        <div class="options">

            <div
                class="option"
                onclick="choose(5,1)">
                Re-plan the route using current information.
            </div>

            <div
                class="option"
                onclick="choose(5,2)">
                Continue without considering the disruption.
            </div>

            <div
                class="option"
                onclick="choose(5,3)">
                Cancel every delivery.
            </div>

        </div>

        <div id="feedback5" class="feedback"></div>

    </div>


    <div class="panel">

        <div class="hint">
            🤖 AI Companion Hint:
            Good operations decisions balance multiple constraints.
            Don't simply optimize one variable.
        </div>

    </div>

</div>


<script>

let level = 1;
let score = 0;
let lives = 3;
let mistakes = 0;
let startTime = Date.now();

const correctAnswers = {
    1: 2,
    2: 1,
    3: 2,
    4: 1,
    5: 1
};

const explanations = {
    1:
        "A slightly longer route can be better when congestion creates greater delay risk.",

    2:
        "The fastest vehicle should be allocated to the urgent delivery.",

    3:
        "Good operations management considers both cost and deadline risk.",

    4:
        "Strict customer deadlines should influence delivery priority.",

    5:
        "Operational planning should respond to current information and re-plan when conditions change."
};

function choose(currentLevel, option) {

    if (currentLevel !== level) {
        return;
    }

    const feedback =
        document.getElementById(
            "feedback" + currentLevel
        );

    if (
        option === correctAnswers[currentLevel]
    ) {

        score += 20;

        feedback.className =
            "feedback good";

        feedback.innerHTML =
            "✓ Good decision.<br><br>" +
            explanations[currentLevel];

        document
            .querySelectorAll(
                "#scenario" +
                currentLevel +
                " .option"
            )
            .forEach(
                x => x.style.pointerEvents = "none"
            );

        updateStats();

        setTimeout(() => {

            if (level < 5) {

                level++;

                document
                    .querySelectorAll(".scenario")
                    .forEach(
                        x => x.classList.remove("active")
                    );

                document
                    .getElementById(
                        "scenario" + level
                    )
                    .classList.add("active");

                updateStats();

            } else {

                finishGame();

            }

        }, 1000);

    } else {

        mistakes++;

        lives--;

        score -= 5;

        score =
            Math.max(
                0,
                score
            );

        feedback.className =
            "feedback bad";

        feedback.innerHTML =
            "✗ That decision increases operational risk.<br><br>" +
            explanations[currentLevel];

        updateStats();

        if (lives <= 0) {

            setTimeout(
                finishGame,
                900
            );
        }
    }
}

function updateStats() {

    document.getElementById(
        "score"
    ).textContent = score;

    document.getElementById(
        "lives"
    ).textContent = lives;

    document.getElementById(
        "level"
    ).textContent = level;

    document.getElementById(
        "progressBar"
    ).style.width =
        ((level / 5) * 100) + "%";
}

function finishGame() {

    const timeTaken =
        Math.floor(
            (Date.now() - startTime) / 1000
        );

    const form =
        document.createElement("form");

    form.method = "POST";

    form.action =
        "{{ url_for('complete_delivery_dash') }}";

    const values = {

        score: score,

        mistakes: mistakes,

        time_taken: timeTaken,

        result_data: JSON.stringify({

            levels_completed:
                Math.min(level, 5),

            lives_remaining:
                lives,

            decision_skill:
                "Operations and Decision Making",

            completed:
                true
        })
    };

    Object.entries(values).forEach(
        ([key,value]) => {

            const input =
                document.createElement("input");

            input.type = "hidden";

            input.name = key;

            input.value = value;

            form.appendChild(input);
        }
    );

    document.body.appendChild(form);

    form.submit();
}

setInterval(() => {

    const seconds =
        Math.floor(
            (Date.now() - startTime) / 1000
        );

    document.getElementById(
        "timer"
    ).textContent = seconds;

},1000);

updateStats();

</script>

</body>
</html>
'''

(GAME_BBA / "delivery_dash.html").write_text(
    delivery_html,
    encoding="utf-8"
)

print("[OK] Delivery Dash template created.")

# ------------------------------------------------------------
# GAME RESULT TEMPLATE
# ------------------------------------------------------------

game_result_html = r'''<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width, initial-scale=1.0">

<title>Game Result | Leap2Launch</title>

<style>

body {
    margin: 0;
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    font-family: Arial,sans-serif;

    background:
        radial-gradient(
            circle at top left,
            #172554,
            #020617 65%
        );

    color: white;
}

.card {
    width: min(700px,92%);
    padding: 45px;
    text-align: center;

    background:
        rgba(15,23,42,.9);

    border:
        1px solid rgba(148,163,184,.2);

    border-radius: 25px;

    box-shadow:
        0 25px 70px rgba(0,0,0,.35);
}

.robot {
    font-size: 70px;
}

.score {
    font-size: 70px;
    font-weight: 800;
    margin: 20px;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(130px,1fr));
    gap: 12px;
    margin: 25px 0;
}

.item {
    padding: 18px;
    background: #111827;
    border-radius: 15px;
}

.item strong {
    display: block;
    font-size: 25px;
    margin-top: 5px;
}

.buttons {
    display: flex;
    gap: 12px;
    justify-content: center;
    flex-wrap: wrap;
}

a {
    text-decoration: none;
    color: white;
    background: #3b82f6;
    padding: 13px 20px;
    border-radius: 12px;
    font-weight: bold;
}

.secondary {
    background: #334155;
}

.notice {
    margin-top: 25px;
    padding: 16px;
    border-radius: 13px;
    background: rgba(245,158,11,.1);
    border: 1px solid rgba(245,158,11,.3);
    color: #fde68a;
}

</style>

</head>

<body>

<div class="card">

    <div class="robot">
        🤖
    </div>

    <h1>{{ game_name }} Complete!</h1>

    <p>
        {{ department }}
    </p>

    <div class="score">
        {{ score }}/100
    </div>

    <div class="grid">

        <div class="item">
            XP Earned
            <strong>+{{ xp }}</strong>
        </div>

        <div class="item">
            Mistakes
            <strong>{{ mistakes }}</strong>
        </div>

        <div class="item">
            Time
            <strong>{{ time_taken }}s</strong>
        </div>

    </div>

    <div class="notice">

        <strong>Evidence recorded</strong>

        <br><br>

        Your game performance has been added to your
        skill evidence as <strong>Pending</strong>.

        <br>

        Faculty verification is required before this
        competency becomes officially verified.

    </div>

    <br>

    <p>
        Demonstrated skill:
        <strong>{{ skill }}</strong>
    </p>

    <div class="buttons">

        <a href="{{ url_for('home') }}">
            🏠 Home
        </a>

        <a
            href="{{ url_for('skills') }}"
            class="secondary">
            🧠 My Skills
        </a>

        <a
            href="{{ url_for('game_history') }}"
            class="secondary">
            🎮 Game History
        </a>

    </div>

</div>

</body>
</html>
'''

(TEMPLATES / "game_result.html").write_text(
    game_result_html,
    encoding="utf-8"
)

print("[OK] Game result template created.")

# ------------------------------------------------------------
# GAME HISTORY TEMPLATE
# ------------------------------------------------------------

game_history_html = r'''<!DOCTYPE html>
<html lang="en">
<head>

<meta charset="UTF-8">

<meta
    name="viewport"
    content="width=device-width,initial-scale=1.0">

<title>Game History | Leap2Launch</title>

<style>

body {
    margin: 0;
    font-family: Arial,sans-serif;
    background: #020617;
    color: white;
}

.container {
    width: min(1050px,94%);
    margin: auto;
    padding: 40px 0;
}

.card {
    background: #0f172a;
    border: 1px solid #334155;
    border-radius: 20px;
    padding: 22px;
    margin-bottom: 15px;
}

.grid {
    display: grid;
    grid-template-columns:
        repeat(auto-fit,minmax(130px,1fr));
    gap: 12px;
}

.stat {
    padding: 15px;
    background: #111827;
    border-radius: 12px;
}

a {
    color: #93c5fd;
}

</style>

</head>

<body>

<div class="container">

    <h1>🎮 Game History</h1>

    <p>
        Your demonstrated performance across Leap2Launch simulations.
    </p>

    {% if results %}

        {% for result in results %}

        <div class="card">

            <h2>
                {{ result["game_name"] }}
            </h2>

            <p>
                {{ result["department"] }}
            </p>

            <div class="grid">

                <div class="stat">
                    Score<br>
                    <strong>
                        {{ result["score"] }}/100
                    </strong>
                </div>

                <div class="stat">
                    XP<br>
                    <strong>
                        +{{ result["xp_earned"] }}
                    </strong>
                </div>

                <div class="stat">
                    Mistakes<br>
                    <strong>
                        {{ result["mistakes"] }}
                    </strong>
                </div>

                <div class="stat">
                    Time<br>
                    <strong>
                        {{ result["time_taken"] }}s
                    </strong>
                </div>

            </div>

            <p>
                Evidence status:
                <strong>Pending faculty verification</strong>
            </p>

        </div>

        {% endfor %}

    {% else %}

        <div class="card">
            No games completed yet.
        </div>

    {% endif %}

</div>

</body>
</html>
'''

(TEMPLATES / "game_history.html").write_text(
    game_history_html,
    encoding="utf-8"
)

print("[OK] Game history template created.")

# ------------------------------------------------------------
# CERTIFICATE SECTION TEMPLATE
# ------------------------------------------------------------

certificate_template = r'''
<!-- ======================================================
     CERTIFICATE UPLOAD SECTION
     Put this inside profile_details.html
     ====================================================== -->

<div class="certificate-upload-card">

    <h2>🏆 Add Certificate</h2>

    <form
        method="POST"
        action="{{ url_for('upload_certificate_file') }}"
        enctype="multipart/form-data">

        <label>Certificate Name</label>

        <input
            type="text"
            name="name"
            placeholder="e.g. Python Certification"
            required>

        <label>Issuer</label>

        <input
            type="text"
            name="issuer"
            placeholder="e.g. NPTEL / Coursera / University">

        <label>Year</label>

        <input
            type="text"
            name="year"
            placeholder="2026">

        <label>Certificate File</label>

        <input
            type="file"
            name="certificate_file"
            accept=".pdf,.png,.jpg,.jpeg,.webp">

        <p>
            Supported:
            PDF, PNG, JPG, JPEG, WEBP
        </p>

        <button type="submit">
            Upload Certificate
        </button>

    </form>

</div>
'''

(TEMPLATES / "certificate_upload_section.html").write_text(
    certificate_template,
    encoding="utf-8"
)

print("[OK] Certificate upload template created.")

# ------------------------------------------------------------
# DIRECTORIES FOR ORIGINAL FRIEND GAME SOURCES
# ------------------------------------------------------------

source_bio = BASE_DIR / "game_sources" / "biotech"
source_bba = BASE_DIR / "game_sources" / "bba"

source_bio.mkdir(parents=True, exist_ok=True)
source_bba.mkdir(parents=True, exist_ok=True)

print("[OK] Game source directories created.")

# ------------------------------------------------------------
# SYNTAX CHECK
# ------------------------------------------------------------

import py_compile

try:

    py_compile.compile(
        str(APP_FILE),
        doraise=True
    )

    print("[OK] app_backup_old.py syntax check passed.")

except Exception as error:

    print("\n[WARNING] app_backup_old.py syntax error detected.")
    print(error)

    print(
        "\nYour original app_backup_old.py backup is still available as:"
    )

    print(
        backup
    )

# ------------------------------------------------------------
# FINAL
# ------------------------------------------------------------

print()
print("=" * 65)
print("Leap2Launch INTEGRATION COMPLETE")
print("=" * 65)

print()
print("Created:")
print("  templates/games/biotech/pcr_master.html")
print("  templates/games/bba/delivery_dash.html")
print("  templates/game_result.html")
print("  templates/game_history.html")
print("  templates/certificate_upload_section.html")

print()
print("Created folders:")
print("  game_sources/biotech/")
print("  game_sources/bba/")
print("  static/uploads/certificates/")

print()
print("Game URLs:")
print("  http://127.0.0.1:5000/games/biotech/pcr-master")
print("  http://127.0.0.1:5000/games/bba/delivery-dash")
print("  http://127.0.0.1:5000/games/history")

print()
print("IMPORTANT:")
print("PCR Master       = Biotechnology → Molecular Lab → Games")
print("Delivery Dash    = BBA / Management → Business Center → Games")
print()
print("Game performance = Evidence")
print("Evidence status  = Pending")
print("Faculty           = Verifies skill")
print()
print("Do NOT put the original Pygame/Tkinter source inside app_backup_old.py.")
print("Those original files belong in game_sources/.")
print("=" * 65)