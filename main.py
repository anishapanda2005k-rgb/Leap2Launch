import pygame
import sys
import random
import math

pygame.init()

# ============================================================
# BIOLAB SKILL QUEST
# A learning + skill assessment game for biotechnology students
# Python 3.12 + pygame 2.6.1
# ============================================================

WIDTH, HEIGHT = 1200, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("BIOLAB SKILL QUEST - Student Assessment")
clock = pygame.time.Clock()

# ============================================================
# COLORS
# ============================================================

BG = (5, 11, 22)
GRID = (12, 25, 42)
PANEL = (17, 31, 52)
PANEL2 = (25, 46, 72)
DARK = (10, 20, 34)

WHITE = (240, 248, 255)
GREY = (145, 165, 190)

CYAN = (55, 225, 255)
BLUE = (70, 125, 255)
GREEN = (70, 230, 150)
YELLOW = (255, 210, 65)
RED = (255, 80, 100)
PURPLE = (180, 105, 255)
ORANGE = (255, 150, 70)

# ============================================================
# FONTS
# ============================================================

FONT = pygame.font.SysFont("arial", 18)
SMALL = pygame.font.SysFont("arial", 15)
MED = pygame.font.SysFont("arial", 26, bold=True)
BIG = pygame.font.SysFont("arial", 45, bold=True)
TITLE = pygame.font.SysFont("arial", 58, bold=True)

# ============================================================
# GAME STATE
# ============================================================

scene = "MENU"

score = 0
mistakes = 0
correct = 0
questions_answered = 0

skill_scores = {
    "Lab Safety": 0,
    "Pipetting": 0,
    "Equipment": 0,
    "Microscopy": 0,
    "Data Analysis": 0,
}

# ============================================================
# GENERAL VARIABLES
# ============================================================

popup_text = ""
popup_color = WHITE
popup_timer = 0

knowledge_index = 0
knowledge_timer = 0

# ============================================================
# KNOWLEDGE CARDS
# ============================================================

knowledge = [
    (
        "LAB SAFETY",
        "Always identify the material before handling it.",
        "Correct labeling and PPE reduce avoidable laboratory errors."
    ),
    (
        "PIPETTING",
        "The first stop controls how much liquid is aspirated.",
        "The second stop helps dispense the remaining liquid."
    ),
    (
        "PIPETTE TIPS",
        "Use an appropriate tip for the pipette and volume.",
        "Good technique improves accuracy and reproducibility."
    ),
    (
        "CENTRIFUGE",
        "Centrifuge tubes should be balanced.",
        "Balanced loading reduces vibration and protects equipment."
    ),
    (
        "MICROSCOPE",
        "Start focusing with the lowest objective.",
        "This makes locating the specimen easier and safer."
    ),
    (
        "MAGNIFICATION",
        "Total magnification = ocular magnification × objective.",
        "For example: 10x ocular × 40x objective = 400x."
    ),
    (
        "DATA ANALYSIS",
        "Replicates help assess consistency.",
        "A single unusual value should be investigated, not ignored."
    ),
    (
        "CONTROLS",
        "Controls provide a reference for interpreting results.",
        "They help distinguish experimental effects from background."
    ),
    (
        "REPRODUCIBILITY",
        "Good science depends on repeatable procedures.",
        "Record conditions, observations and measurements carefully."
    ),
]

# ============================================================
# HELPER FUNCTIONS
# ============================================================

def draw_text(text, x, y, font=FONT, color=WHITE, center=False):

    surface = font.render(str(text), True, color)

    if center:
        rect = surface.get_rect(center=(x, y))
    else:
        rect = surface.get_rect(topleft=(x, y))

    screen.blit(surface, rect)


def draw_panel(rect, fill=PANEL, border=BLUE, radius=18):

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=radius
    )

    pygame.draw.rect(
        screen,
        border,
        rect,
        2,
        border_radius=radius
    )


def draw_button(rect, label, enabled=True):

    fill = PANEL2 if enabled else (40, 44, 52)
    border = CYAN if enabled else (80, 80, 90)

    pygame.draw.rect(
        screen,
        fill,
        rect,
        border_radius=12
    )

    pygame.draw.rect(
        screen,
        border,
        rect,
        2,
        border_radius=12
    )

    draw_text(
        label,
        rect.centerx,
        rect.centery,
        FONT,
        WHITE if enabled else GREY,
        True
    )

    return rect


def draw_background():

    screen.fill(BG)

    for x in range(0, WIDTH, 40):
        pygame.draw.line(
            screen,
            GRID,
            (x, 0),
            (x, HEIGHT)
        )

    for y in range(0, HEIGHT, 40):
        pygame.draw.line(
            screen,
            GRID,
            (0, y),
            (WIDTH, y)
        )


def popup(title, message, color=CYAN):

    global popup_text
    global popup_color
    global popup_timer

    popup_text = title + "  |  " + message
    popup_color = color
    popup_timer = pygame.time.get_ticks() + 3000


def reset_game():

    global score
    global mistakes
    global correct
    global questions_answered
    global skill_scores

    score = 0
    mistakes = 0
    correct = 0
    questions_answered = 0

    skill_scores = {
        "Lab Safety": 0,
        "Pipetting": 0,
        "Equipment": 0,
        "Microscopy": 0,
        "Data Analysis": 0,
    }


# ============================================================
# SCIENTIST CHARACTER
# ============================================================

def draw_scientist(x, y, talking=False):

    bounce = math.sin(pygame.time.get_ticks() / 250) * 3

    x = int(x)
    y = int(y + bounce)

    # Shadow
    pygame.draw.ellipse(
        screen,
        (3, 7, 14),
        (x - 48, y + 125, 96, 18)
    )

    # Legs
    pygame.draw.line(
        screen,
        (70, 80, 100),
        (x - 15, y + 80),
        (x - 22, y + 125),
        8
    )

    pygame.draw.line(
        screen,
        (70, 80, 100),
        (x + 15, y + 80),
        (x + 22, y + 125),
        8
    )

    # Lab coat
    pygame.draw.rect(
        screen,
        WHITE,
        (x - 42, y + 25, 84, 75),
        border_radius=18
    )

    # Arms
    arm = -10 if talking else 0

    pygame.draw.line(
        screen,
        WHITE,
        (x - 38, y + 40),
        (x - 75, y + 65 + arm),
        10
    )

    pygame.draw.line(
        screen,
        WHITE,
        (x + 38, y + 40),
        (x + 75, y + 65 - arm),
        10
    )

    # Hands
    pygame.draw.circle(
        screen,
        (230, 185, 150),
        (x - 78, y + 65 + arm),
        9
    )

    pygame.draw.circle(
        screen,
        (230, 185, 150),
        (x + 78, y + 65 - arm),
        9
    )

    # Neck
    pygame.draw.rect(
        screen,
        (230, 185, 150),
        (x - 10, y + 15, 20, 20)
    )

    # Head
    pygame.draw.circle(
        screen,
        (230, 185, 150),
        (x, y),
        38
    )

    # Hair
    pygame.draw.arc(
        screen,
        (35, 25, 30),
        (x - 36, y - 34, 72, 55),
        math.pi,
        2 * math.pi,
        12
    )

    # Glasses
    pygame.draw.rect(
        screen,
        (30, 40, 50),
        (x - 28, y - 10, 23, 15),
        2
    )

    pygame.draw.rect(
        screen,
        (30, 40, 50),
        (x + 5, y - 10, 23, 15),
        2
    )

    pygame.draw.line(
        screen,
        (30, 40, 50),
        (x - 5, y - 3),
        (x + 5, y - 3),
        2
    )

    # Eyes
    pygame.draw.circle(
        screen,
        (20, 25, 35),
        (x - 17, y - 2),
        3
    )

    pygame.draw.circle(
        screen,
        (20, 25, 35),
        (x + 17, y - 2),
        3
    )

    # Smile
    pygame.draw.arc(
        screen,
        (80, 35, 40),
        (x - 15, y + 3, 30, 20),
        0,
        math.pi,
        3
    )


# ============================================================
# MENU
# ============================================================

def draw_menu():

    draw_background()

    draw_text(
        "BIOLAB",
        65,
        75,
        TITLE,
        CYAN
    )

    draw_text(
        "SKILL QUEST",
        65,
        140,
        TITLE,
        WHITE
    )

    draw_text(
        "INTERACTIVE BIOTECHNOLOGY SKILL ASSESSMENT",
        70,
        215,
        MED,
        GREEN
    )

    draw_panel(
        pygame.Rect(65, 270, 550, 300),
        PANEL,
        BLUE
    )

    draw_text(
        "YOUR MISSION",
        100,
        305,
        MED,
        YELLOW
    )

    draw_text(
        "Test your scientific decision-making.",
        100,
        355,
        FONT
    )

    draw_text(
        "Choose wisely instead of memorising answers.",
        100,
        390,
        FONT
    )

    draw_text(
        "Learn from mistakes and improve your score.",
        100,
        425,
        FONT
    )

    draw_text(
        "Skills assessed:",
        100,
        470,
        FONT,
        CYAN
    )

    draw_text(
        "Safety | Pipetting | Equipment | Microscopy | Data",
        100,
        505,
        SMALL,
        GREY
    )

    draw_button(
        pygame.Rect(65, 610, 300, 60),
        "START SKILL QUEST"
    )

    draw_scientist(
        900,
        300,
        True
    )

    # Floating molecules
    t = pygame.time.get_ticks() / 800

    for i in range(12):

        x = 760 + math.sin(t + i) * 160
        y = 120 + i * 40

        pygame.draw.circle(
            screen,
            CYAN if i % 2 == 0 else PURPLE,
            (int(x), int(y)),
            4
        )


# ============================================================
# ROUND 1 - LAB SAFETY
# ============================================================

safety_questions = [
    {
        "question": "You notice an unlabeled tube on the bench. What is the best action?",
        "options": [
            "Use it if the liquid looks familiar",
            "Ask someone else to guess",
            "Do not use it until it is correctly identified",
            "Smell it to identify the contents"
        ],
        "answer": 2,
        "explanation": "Unknown or unlabeled materials should not be used until their identity is established.",
    },
    {
        "question": "Why is appropriate PPE important in a laboratory?",
        "options": [
            "Only to look professional",
            "To reduce exposure to laboratory hazards",
            "It makes experiments faster",
            "It replaces all other safety procedures"
        ],
        "answer": 1,
        "explanation": "PPE is one layer of protection against laboratory hazards.",
    },
    {
        "question": "A spill occurs during an experiment. What should you do first?",
        "options": [
            "Ignore it",
            "Spread it out so it dries",
            "Follow the appropriate laboratory spill procedure",
            "Hide the spill"
        ],
        "answer": 2,
        "explanation": "Spills should be handled according to the laboratory's established safety procedure.",
    }
]

safety_index = 0


def draw_safety():

    global safety_index

    draw_background()

    draw_text(
        "01  LAB SAFETY",
        40,
        28,
        MED
    )

    draw_text(
        f"QUESTION {safety_index + 1} / {len(safety_questions)}",
        40,
        65,
        SMALL,
        GREY
    )

    q = safety_questions[safety_index]

    draw_panel(
        pygame.Rect(55, 120, 1090, 490),
        PANEL,
        BLUE
    )

    draw_text(
        "SCENARIO",
        90,
        155,
        MED,
        CYAN
    )

    # Question wrapping
    words = q["question"].split()
    lines = []
    line = ""

    for word in words:

        if len(line + " " + word) <= 65:
            line += (" " if line else "") + word
        else:
            lines.append(line)
            line = word

    if line:
        lines.append(line)

    y = 205

    for line in lines:

        draw_text(
            line,
            90,
            y,
            FONT
        )

        y += 30

    option_rects = []

    for i, option in enumerate(q["options"]):

        row = i // 2
        col = i % 2

        rect = pygame.Rect(
            90 + col * 510,
            300 + row * 110,
            480,
            80
        )

        draw_panel(
            rect,
            PANEL2,
            CYAN,
            12
        )

        draw_text(
            f"{chr(65 + i)}",
            rect.x + 25,
            rect.centery,
            MED,
            YELLOW,
            True
        )

        draw_text(
            option,
            rect.x + 55,
            rect.centery,
            SMALL,
            WHITE,
            True
        )

        option_rects.append(rect)

    draw_text(
        "Choose the safest scientific decision.",
        90,
        565,
        SMALL,
        GREY
    )

    return option_rects


# ============================================================
# ROUND 2 - PIPETTING
# ============================================================

pipette_target = random.choice([50, 100, 200, 250, 500])

pipette_options = [
    10,
    50,
    100,
    200,
    500,
    1000
]

pipette_selected = None
pipette_done = False


def draw_pipetting():

    draw_background()

    draw_text(
        "02  PIPETTING CHALLENGE",
        40,
        28,
        MED
    )

    draw_text(
        "Select the most suitable pipette setting for the requested volume.",
        40,
        65,
        SMALL,
        GREY
    )

    draw_panel(
        pygame.Rect(50, 120, 1100, 500),
        PANEL,
        PURPLE
    )

    draw_text(
        "TARGET VOLUME",
        90,
        155,
        MED,
        CYAN
    )

    draw_text(
        f"{pipette_target} uL",
        90,
        200,
        BIG,
        YELLOW
    )

    draw_text(
        "Which setting is most appropriate?",
        90,
        265,
        FONT
    )

    option_rects = []

    for i, value in enumerate(pipette_options):

        rect = pygame.Rect(
            90 + (i % 3) * 320,
            330 + (i // 3) * 105,
            280,
            75
        )

        draw_panel(
            rect,
            PANEL2,
            CYAN,
            12
        )

        draw_text(
            f"{value} uL",
            rect.centerx,
            rect.centery,
            MED,
            WHITE,
            True
        )

        option_rects.append((rect, value))

    draw_text(
        "SKILL TIP: Choose equipment that can accurately cover the requested range.",
        90,
        555,
        SMALL,
        GREY
    )

    return option_rects


# ============================================================
# ROUND 3 - EQUIPMENT
# ============================================================

equipment_questions = [
    {
        "question": "Why should centrifuge tubes be balanced?",
        "options": [
            "To make them look organised",
            "To reduce vibration and mechanical stress",
            "To increase temperature",
            "To change the sample colour"
        ],
        "answer": 1,
        "explanation": "Balanced loading helps the centrifuge operate smoothly and reduces vibration."
    },
    {
        "question": "Which instrument is designed to measure small liquid volumes accurately?",
        "options": [
            "Microscope",
            "Pipette",
            "Centrifuge",
            "Water bath"
        ],
        "answer": 1,
        "explanation": "A micropipette is designed for accurate transfer of small liquid volumes."
    },
    {
        "question": "What is a microscope's objective used for?",
        "options": [
            "Primary magnification of the specimen",
            "Heating the specimen",
            "Centrifuging the specimen",
            "Measuring liquid volume"
        ],
        "answer": 0,
        "explanation": "The objective lens provides the primary magnification and resolution of the specimen."
    }
]

equipment_index = 0


def draw_equipment():

    q = equipment_questions[equipment_index]

    draw_background()

    draw_text(
        "03  EQUIPMENT EXPERT",
        40,
        28,
        MED
    )

    draw_text(
        f"QUESTION {equipment_index + 1} / {len(equipment_questions)}",
        40,
        65,
        SMALL,
        GREY
    )

    draw_panel(
        pygame.Rect(55, 120, 1090, 490),
        PANEL,
        BLUE
    )

    draw_text(
        "LAB EQUIPMENT DECISION",
        90,
        155,
        MED,
        CYAN
    )

    draw_text(
        q["question"],
        90,
        210,
        FONT
    )

    option_rects = []

    for i, option in enumerate(q["options"]):

        rect = pygame.Rect(
            90,
            280 + i * 75,
            970,
            58
        )

        draw_panel(
            rect,
            PANEL2,
            BLUE,
            10
        )

        draw_text(
            chr(65 + i),
            rect.x + 25,
            rect.centery,
            MED,
            YELLOW,
            True
        )

        draw_text(
            option,
            rect.x + 65,
            rect.centery,
            FONT,
            WHITE,
            True
        )

        option_rects.append(rect)

    draw_text(
        "Think about the scientific purpose of the equipment.",
        90,
        555,
        SMALL,
        GREY
    )

    return option_rects


# ============================================================
# ROUND 4 - MICROSCOPY
# ============================================================

microscopy_stage = 0

microscopy_questions = [
    {
        "question": "What should you generally use first when locating a specimen?",
        "options": [
            "Highest-power objective",
            "Lowest-power objective",
            "No objective",
            "Oil immersion immediately"
        ],
        "answer": 1,
        "explanation": "Starting with low power gives a wider field of view and makes specimen location easier."
    },
    {
        "question": "If the ocular lens is 10x and the objective is 40x, total magnification is:",
        "options": [
            "40x",
            "50x",
            "400x",
            "4000x"
        ],
        "answer": 2,
        "explanation": "Total magnification = ocular × objective = 10 × 40 = 400x."
    },
    {
        "question": "What is the main purpose of focusing?",
        "options": [
            "To make the specimen chemically react",
            "To obtain a sharp image",
            "To increase sample volume",
            "To change the objective colour"
        ],
        "answer": 1,
        "explanation": "Focusing adjusts the optics so the specimen appears sharp."
    }
]


def draw_microscopy():

    q = microscopy_questions[microscopy_stage]

    draw_background()

    draw_text(
        "04  MICROSCOPY MASTER",
        40,
        28,
        MED
    )

    draw_text(
        f"QUESTION {microscopy_stage + 1} / {len(microscopy_questions)}",
        40,
        65,
        SMALL,
        GREY
    )

    draw_panel(
        pygame.Rect(55, 120, 1090, 500),
        PANEL,
        PURPLE
    )

    # Microscope illustration
    pygame.draw.ellipse(
        screen,
        (45, 55, 70),
        (90, 250, 230, 100)
    )

    pygame.draw.line(
        screen,
        WHITE,
        (205, 290),
        (205, 430),
        18
    )

    pygame.draw.arc(
        screen,
        WHITE,
        (130, 220, 180, 260),
        math.pi / 2,
        math.pi * 1.7,
        14
    )

    pygame.draw.rect(
        screen,
        CYAN,
        (160, 410, 170, 25),
        border_radius=8
    )

    pygame.draw.circle(
        screen,
        PURPLE,
        (245, 410),
        16
    )

    draw_text(
        "MICROSCOPE",
        205,
        475,
        SMALL,
        GREY,
        True
    )

    draw_text(
        q["question"],
        430,
        175,
        FONT
    )

    option_rects = []

    for i, option in enumerate(q["options"]):

        rect = pygame.Rect(
            430,
            240 + i * 75,
            620,
            58
        )

        draw_panel(
            rect,
            PANEL2,
            CYAN,
            10
        )

        draw_text(
            chr(65 + i),
            rect.x + 25,
            rect.centery,
            MED,
            YELLOW,
            True
        )

        draw_text(
            option,
            rect.x + 65,
            rect.centery,
            SMALL,
            WHITE,
            True
        )

        option_rects.append(rect)

    return option_rects


# ============================================================
# ROUND 5 - DATA DETECTIVE
# ============================================================

data_case = random.randint(0, 2)

data_cases = [
    {
        "title": "CELL COUNT DATA",
        "data": [102, 98, 101, 99],
        "question": "What is the best interpretation?",
        "options": [
            "The measurements are reasonably consistent",
            "Every measurement is completely unrelated",
            "The experiment must be discarded",
            "The numbers prove the method is perfect"
        ],
        "answer": 0,
        "explanation": "The values are close to one another, suggesting good consistency among these measurements."
    },
    {
        "title": "MICROSCOPY OBSERVATION",
        "data": [12, 13, 12, 30],
        "question": "What should you do with the value 30?",
        "options": [
            "Automatically delete it",
            "Investigate whether it has a valid explanation",
            "Change it to 12",
            "Ignore all measurements"
        ],
        "answer": 1,
        "explanation": "An unusual value should be investigated before deciding whether it represents an error or real variation."
    },
    {
        "title": "EXPERIMENTAL COMPARISON",
        "data": [5, 6, 5, 6],
        "question": "What does the repeated pattern mainly tell you?",
        "options": [
            "The measurements show consistency",
            "The experiment has no value",
            "The samples are necessarily identical",
            "The result is automatically statistically significant"
        ],
        "answer": 0,
        "explanation": "Close replicate measurements suggest consistency, but consistency alone does not prove statistical significance."
    }
]


def draw_data():

    case = data_cases[data_case]

    draw_background()

    draw_text(
        "05  DATA DETECTIVE",
        40,
        28,
        MED
    )

    draw_text(
        "Interpret evidence instead of guessing.",
        40,
        65,
        SMALL,
        GREY
    )

    draw_panel(
        pygame.Rect(55, 120, 1090, 500),
        PANEL,
        GREEN
    )

    draw_text(
        case["title"],
        90,
        155,
        MED,
        CYAN
    )

    # Data bars
    max_value = max(case["data"])

    for i, value in enumerate(case["data"]):

        x = 120 + i * 125

        height = int(
            180 * value / max_value
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                x,
                400 - height,
                70,
                height
            ),
            border_radius=8
        )

        draw_text(
            str(value),
            x + 35,
            420,
            FONT,
            WHITE,
            True
        )

        draw_text(
            f"R{i + 1}",
            x + 35,
            445,
            SMALL,
            GREY,
            True
        )

    draw_text(
        case["question"],
        650,
        180,
        FONT
    )

    option_rects = []

    for i, option in enumerate(case["options"]):

        rect = pygame.Rect(
            650,
            235 + i * 72,
            430,
            55
        )

        draw_panel(
            rect,
            PANEL2,
            GREEN,
            10
        )

        draw_text(
            chr(65 + i),
            rect.x + 22,
            rect.centery,
            MED,
            YELLOW,
            True
        )

        draw_text(
            option,
            rect.x + 55,
            rect.centery,
            SMALL,
            WHITE,
            True
        )

        option_rects.append(rect)

    draw_text(
        "SKILL: observation + scientific reasoning",
        650,
        535,
        SMALL,
        GREY
    )

    return option_rects


# ============================================================
# KNOWLEDGE SCREEN
# ============================================================

def draw_knowledge():

    draw_background()

    draw_text(
        "SCIENCE BREAK",
        600,
        70,
        TITLE,
        CYAN,
        True
    )

    draw_text(
        "Read this before continuing.",
        600,
        135,
        MED,
        GREY,
        True
    )

    title, line1, line2 = knowledge[knowledge_index]

    draw_panel(
        pygame.Rect(190, 190, 820, 350),
        PANEL,
        PURPLE
    )

    draw_text(
        title,
        600,
        250,
        BIG,
        YELLOW,
        True
    )

    draw_text(
        line1,
        600,
        330,
        FONT,
        WHITE,
        True
    )

    draw_text(
        line2,
        600,
        365,
        FONT,
        WHITE,
        True
    )

    draw_text(
        "Knowledge cards are intentionally slow.",
        600,
        430,
        SMALL,
        GREY,
        True
    )

    draw_button(
        pygame.Rect(450, 490, 300, 55),
        "CONTINUE"
    )


# ============================================================
# FINAL SCORE
# ============================================================

def draw_score():

    draw_background()

    # Calculate percentage
    total_questions = 3 + 1 + 3 + 3 + 1
    percentage = int(
        correct / max(1, total_questions) * 100
    )

    # Score capped at 100
    final_score = max(
        0,
        min(
            100,
            score
        )
    )

    draw_text(
        "MISSION COMPLETE",
        600,
        55,
        TITLE,
        GREEN,
        True
    )

    draw_text(
        "BIOLAB SKILL REPORT",
        600,
        120,
        MED,
        CYAN,
        True
    )

    draw_panel(
        pygame.Rect(120, 165, 960, 455),
        PANEL,
        BLUE
    )

    draw_text(
        f"{final_score} / 100",
        600,
        225,
        BIG,
        YELLOW,
        True
    )

    draw_text(
        "OVERALL PERFORMANCE",
        600,
        275,
        SMALL,
        GREY,
        True
    )

    y = 325

    for skill, value in skill_scores.items():

        draw_text(
            skill,
            210,
            y,
            FONT
        )

        pygame.draw.rect(
            screen,
            (40, 50, 65),
            (450, y + 4, 400, 15),
            border_radius=7
        )

        pygame.draw.rect(
            screen,
            GREEN,
            (
                450,
                y + 4,
                int(400 * min(100, value) / 100),
                15
            ),
            border_radius=7
        )

        draw_text(
            f"{value}%",
            880,
            y,
            SMALL,
            GREEN
        )

        y += 48

    if final_score >= 90:

        rank = "ELITE LAB SCIENTIST"

    elif final_score >= 75:

        rank = "STRONG LAB TRAINEE"

    elif final_score >= 60:

        rank = "DEVELOPING SCIENTIST"

    else:

        rank = "KEEP TRAINING"

    draw_text(
        rank,
        600,
        570,
        MED,
        CYAN,
        True
    )

    draw_button(
        pygame.Rect(450, 640, 300, 50),
        "PLAY AGAIN"
    )


# ============================================================
# QUESTION FEEDBACK
# ============================================================

def answer_question(
    selected,
    answer,
    explanation,
    skill,
    points=10
):

    global score
    global mistakes
    global correct
    global questions_answered

    questions_answered += 1

    if selected == answer:

        correct += 1
        score += points
        skill_scores[skill] += 100 // 3

        popup(
            "CORRECT!",
            explanation,
            GREEN
        )

        return True

    else:

        mistakes += 1
        score = max(
            0,
            score - 3
        )

        popup(
            "NOT QUITE",
            explanation,
            RED
        )

        return False


# ============================================================
# MAIN
# ============================================================

def main():

    global scene

    global safety_index
    global equipment_index
    global microscopy_stage

    global pipette_target
    global pipette_done

    global data_case

    global knowledge_index
    global knowledge_timer

    while True:

        dt = clock.tick(60) / 1000

        # ====================================================
        # EVENTS
        # ====================================================

        for event in pygame.event.get():

            if event.type == pygame.QUIT:

                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:

                if event.key == pygame.K_ESCAPE:

                    scene = "MENU"

                if event.key == pygame.K_SPACE:

                    if scene == "KNOWLEDGE":

                        knowledge_index = (
                            knowledge_index + 1
                        ) % len(knowledge)

            if event.type == pygame.MOUSEBUTTONDOWN:

                if event.button != 1:
                    continue

                mouse = event.pos

                # ============================================
                # MENU
                # ============================================

                if scene == "MENU":

                    if pygame.Rect(
                        65, 610, 300, 60
                    ).collidepoint(mouse):

                        reset_game()

                        safety_index = 0
                        equipment_index = 0
                        microscopy_stage = 0

                        pipette_target = random.choice(
                            [50, 100, 200, 250, 500]
                        )

                        pipette_done = False

                        data_case = random.randint(
                            0,
                            len(data_cases) - 1
                        )

                        scene = "SAFETY"

                # ============================================
                # SAFETY
                # ============================================

                elif scene == "SAFETY":

                    rects = draw_safety()

                    for i, rect in enumerate(rects):

                        if rect.collidepoint(mouse):

                            q = safety_questions[safety_index]

                            answer_question(
                                i,
                                q["answer"],
                                q["explanation"],
                                "Lab Safety",
                                10
                            )

                            safety_index += 1

                            if safety_index >= len(
                                safety_questions
                            ):

                                scene = "KNOWLEDGE"

                                knowledge_index = 0
                                knowledge_timer = 0

                # ============================================
                # KNOWLEDGE
                # ============================================

                elif scene == "KNOWLEDGE":

                    if pygame.Rect(
                        450, 490, 300, 55
                    ).collidepoint(mouse):

                        scene = "PIPETTING"

                # ============================================
                # PIPETTING
                # ============================================

                elif scene == "PIPETTING":

                    options = draw_pipetting()

                    for rect, value in options:

                        if rect.collidepoint(mouse):

                            if pipette_done:
                                continue

                            pipette_done = True

                            # Best practical choice:
                            # smallest suitable pipette that can cover
                            # target without exceeding its range.
                            if pipette_target <= 100:
                                expected = 100
                            elif pipette_target <= 200:
                                expected = 200
                            elif pipette_target <= 500:
                                expected = 500
                            else:
                                expected = 1000

                            if value == expected:

                                score += 15
                                correct += 1
                                skill_scores["Pipetting"] = 100

                                popup(
                                    "EXCELLENT PIPETTING CHOICE",
                                    "You selected a suitable volume range.",
                                    GREEN
                                )

                            else:

                                mistakes += 1
                                score = max(0, score - 3)

                                popup(
                                    "TRY AGAIN IN YOUR HEAD",
                                    f"For {pipette_target} uL, think about the appropriate pipette range.",
                                    RED
                                )

                            scene = "EQUIPMENT"

                # ============================================
                # EQUIPMENT
                # ============================================

                elif scene == "EQUIPMENT":

                    rects = draw_equipment()

                    for i, rect in enumerate(rects):

                        if rect.collidepoint(mouse):

                            q = equipment_questions[
                                equipment_index
                            ]

                            answer_question(
                                i,
                                q["answer"],
                                q["explanation"],
                                "Equipment",
                                10
                            )

                            equipment_index += 1

                            if equipment_index >= len(
                                equipment_questions
                            ):

                                scene = "KNOWLEDGE"

                                knowledge_index = 3
                                knowledge_timer = 0

                # ============================================
                # MICROSCOPY
                # ============================================

                elif scene == "MICROSCOPY":

                    rects = draw_microscopy()

                    for i, rect in enumerate(rects):

                        if rect.collidepoint(mouse):

                            q = microscopy_questions[
                                microscopy_stage
                            ]

                            answer_question(
                                i,
                                q["answer"],
                                q["explanation"],
                                "Microscopy",
                                10
                            )

                            microscopy_stage += 1

                            if microscopy_stage >= len(
                                microscopy_questions
                            ):

                                scene = "KNOWLEDGE"

                                knowledge_index = 6
                                knowledge_timer = 0

                # ============================================
                # DATA
                # ============================================

                elif scene == "DATA":

                    rects = draw_data()

                    case = data_cases[data_case]

                    for i, rect in enumerate(rects):

                        if rect.collidepoint(mouse):

                            answer_question(
                                i,
                                case["answer"],
                                case["explanation"],
                                "Data Analysis",
                                10
                            )

                            scene = "SCORE"

                # ============================================
                # SCORE
                # ============================================

                elif scene == "SCORE":

                    if pygame.Rect(
                        450, 640, 300, 50
                    ).collidepoint(mouse):

                        reset_game()

                        safety_index = 0
                        equipment_index = 0
                        microscopy_stage = 0

                        pipette_target = random.choice(
                            [50, 100, 200, 250, 500]
                        )

                        pipette_done = False

                        data_case = random.randint(
                            0,
                            len(data_cases) - 1
                        )

                        scene = "SAFETY"

        # ====================================================
        # KNOWLEDGE TIMER
        # ====================================================

        if scene == "KNOWLEDGE":

            knowledge_timer += dt

            # Slow automatic rotation:
            # 15 seconds, enough reading time
            if knowledge_timer >= 15:

                knowledge_timer = 0

                knowledge_index = (
                    knowledge_index + 1
                ) % len(knowledge)

        # ====================================================
        # DRAW
        # ====================================================

        if scene == "MENU":

            draw_menu()

        elif scene == "SAFETY":

            draw_safety()

        elif scene == "PIPETTING":

            draw_pipetting()

        elif scene == "EQUIPMENT":

            draw_equipment()

        elif scene == "MICROSCOPY":

            draw_microscopy()

        elif scene == "DATA":

            draw_data()

        elif scene == "KNOWLEDGE":

            draw_knowledge()

        elif scene == "SCORE":

            draw_score()

        # ====================================================
        # POPUP
        # ====================================================

        if (
            popup_text
            and pygame.time.get_ticks() < popup_timer
        ):

            box = pygame.Rect(
                160,
                15,
                880,
                50
            )

            draw_panel(
                box,
                PANEL,
                popup_color,
                10
            )

            message = popup_text

            if len(message) > 115:

                message = message[:112] + "..."

            draw_text(
                message,
                box.centerx,
                box.centery,
                SMALL,
                WHITE,
                True
            )

        pygame.display.flip()


# ============================================================
# RUN
# ============================================================

if __name__ == "__main__":
    main()