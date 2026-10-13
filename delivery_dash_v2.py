"""
DELIVERY DASH v2 — SAVE THE DELIVERY!
Challenging educational game prototype.

Requirements:
    pip install pygame

Run:
    python delivery_dash_v2.py

Design goals:
    - Answers are NEVER displayed before the player commits.
    - Numbers are randomized within controlled difficulty ranges.
    - Players calculate Time / Speed / Distance themselves.
    - Limited lives, countdowns, bonuses, streaks and payment.
    - Drag-and-drop interaction where appropriate.
    - Level 4 requires both vehicle AND delivery order.
    - Level 5 is a multi-step final decision.
"""

import math
import random
import sys
from dataclasses import dataclass

import pygame


# ============================================================
# CONFIG
# ============================================================

WIDTH, HEIGHT = 1280, 760
FPS = 60

pygame.init()
pygame.display.set_caption("DELIVERY DASH v2 - Save the Delivery!")
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

FONT_NAME = "arial"

# Colors
BG = (246, 248, 252)
WHITE = (255, 255, 255)
TEXT = (29, 36, 48)
MUTED = (104, 115, 131)
PRIMARY = (42, 103, 220)
PRIMARY_DARK = (27, 69, 153)
GREEN = (35, 171, 91)
GREEN_DARK = (24, 118, 60)
RED = (220, 69, 69)
RED_DARK = (154, 43, 43)
ORANGE = (238, 145, 38)
YELLOW = (248, 195, 54)
ROAD = (68, 73, 83)
ROAD_DARK = (48, 52, 61)
BORDER = (218, 223, 232)
SHADOW = (224, 228, 236)
LIGHT_BLUE = (232, 241, 255)
LIGHT_GREEN = (231, 247, 237)
LIGHT_RED = (253, 235, 235)
LIGHT_ORANGE = (255, 242, 220)
SKY = (218, 237, 250)


# ============================================================
# DRAWING HELPERS
# ============================================================

def font(size, bold=False):
    return pygame.font.SysFont(FONT_NAME, size, bold=bold)


def draw_text(surface, value, x, y, size=20, color=TEXT,
              bold=False, center=False):
    img = font(size, bold).render(str(value), True, color)
    rect = img.get_rect()
    if center:
        rect.center = (int(x), int(y))
    else:
        rect.topleft = (int(x), int(y))
    surface.blit(img, rect)
    return rect


def wrap_text(value, width, size=18, bold=False):
    words = value.split()
    lines = []
    line = ""

    for word in words:
        candidate = word if not line else line + " " + word
        if font(size, bold).size(candidate)[0] <= width:
            line = candidate
        else:
            if line:
                lines.append(line)
            line = word

    if line:
        lines.append(line)
    return lines


def paragraph(value, x, y, width, size=18, color=TEXT,
              gap=7, bold=False):
    yy = y
    for line in wrap_text(value, width, size, bold):
        draw_text(screen, line, x, yy, size, color, bold)
        yy += size + gap
    return yy


def panel(rect, radius=18, border=BORDER):
    r = pygame.Rect(rect)
    pygame.draw.rect(screen, SHADOW, r.move(0, 5), border_radius=radius)
    pygame.draw.rect(screen, WHITE, r, border_radius=radius)
    if border:
        pygame.draw.rect(screen, border, r, 2, border_radius=radius)


def button(rect, label, color=PRIMARY, size=17):
    r = pygame.Rect(rect)
    pygame.draw.rect(screen, color, r, border_radius=11)
    draw_text(screen, label, r.centerx, r.centery, size,
              WHITE, True, True)
    return r


def badge(x, y, label, color=PRIMARY_DARK, bg=LIGHT_BLUE, width=130):
    r = pygame.Rect(x, y, width, 32)
    pygame.draw.rect(screen, bg, r, border_radius=16)
    draw_text(screen, label, r.centerx, r.centery, 13,
              color, True, True)
    return r


def draw_check(cx, cy, color=GREEN, scale=1.0):
    s = scale
    pygame.draw.circle(screen, color, (int(cx), int(cy)), int(22*s), 3)
    pygame.draw.line(screen, color,
                     (int(cx-10*s), int(cy)),
                     (int(cx-2*s), int(cy+8*s)), max(2, int(4*s)))
    pygame.draw.line(screen, color,
                     (int(cx-2*s), int(cy+8*s)),
                     (int(cx+12*s), int(cy-10*s)), max(2, int(4*s)))


def draw_cross(cx, cy, color=RED, scale=1.0):
    s = scale
    pygame.draw.circle(screen, color, (int(cx), int(cy)), int(22*s), 3)
    pygame.draw.line(screen, color,
                     (int(cx-10*s), int(cy-10*s)),
                     (int(cx+10*s), int(cy+10*s)), max(2, int(4*s)))
    pygame.draw.line(screen, color,
                     (int(cx+10*s), int(cy-10*s)),
                     (int(cx-10*s), int(cy+10*s)), max(2, int(4*s)))


# ============================================================
# VECTOR ART
# ============================================================

def draw_scooter(cx, cy, scale=1.0, sad=False, dance=False):
    s = scale
    body = RED if sad else PRIMARY

    left = (int(cx-28*s), int(cy+15*s))
    right = (int(cx+28*s), int(cy+15*s))
    wr = max(5, int(12*s))

    pygame.draw.circle(screen, ROAD_DARK, left, wr)
    pygame.draw.circle(screen, ROAD_DARK, right, wr)
    pygame.draw.circle(screen, WHITE, left, max(2, wr//3))
    pygame.draw.circle(screen, WHITE, right, max(2, wr//3))

    pygame.draw.line(screen, body,
                     (int(cx-23*s), int(cy+5*s)),
                     (int(cx+18*s), int(cy+5*s)),
                     max(3, int(7*s)))

    pygame.draw.arc(screen, body,
                    (int(cx-13*s), int(cy-22*s),
                     int(43*s), int(42*s)),
                    0.3, 2.4, max(3, int(6*s)))

    pygame.draw.line(screen, body,
                     (int(cx+18*s), int(cy+4*s)),
                     (int(cx+31*s), int(cy-18*s)),
                     max(3, int(5*s)))

    pygame.draw.line(screen, body,
                     (int(cx+31*s), int(cy-18*s)),
                     (int(cx+40*s), int(cy-18*s)),
                     max(2, int(4*s)))

    head = (int(cx), int(cy-39*s))
    pygame.draw.circle(screen, (237, 180, 138), head, max(5, int(8*s)))
    pygame.draw.arc(screen, ROAD_DARK,
                    (int(cx-9*s), int(head[1]-10*s),
                     int(18*s), int(17*s)),
                    math.pi, math.pi*2, max(2, int(4*s)))

    if dance:
        pygame.draw.line(screen, ROAD_DARK,
                         (int(cx-3*s), int(cy-25*s)),
                         (int(cx-25*s), int(cy-44*s)),
                         max(2, int(4*s)))
        pygame.draw.line(screen, ROAD_DARK,
                         (int(cx+3*s), int(cy-25*s)),
                         (int(cx+25*s), int(cy-44*s)),
                         max(2, int(4*s)))
    else:
        pygame.draw.line(screen, ROAD_DARK,
                         (int(cx), int(cy-28*s)),
                         (int(cx-5*s), int(cy-5*s)),
                         max(3, int(5*s)))


def draw_fast_bike(cx, cy, scale=1.0):
    s = scale
    wr = max(5, int(12*s))

    pygame.draw.circle(screen, ROAD_DARK,
                       (int(cx-28*s), int(cy+14*s)), wr)
    pygame.draw.circle(screen, ROAD_DARK,
                       (int(cx+28*s), int(cy+14*s)), wr)

    pygame.draw.polygon(
        screen, RED,
        [
            (int(cx-33*s), int(cy+3*s)),
            (int(cx-4*s), int(cy-15*s)),
            (int(cx+27*s), int(cy-5*s)),
            (int(cx+13*s), int(cy+9*s)),
            (int(cx-20*s), int(cy+9*s)),
        ]
    )

    pygame.draw.line(screen, ROAD_DARK,
                     (int(cx+8*s), int(cy-10*s)),
                     (int(cx+25*s), int(cy-29*s)),
                     max(2, int(4*s)))


def draw_bicycle(cx, cy, scale=1.0):
    s = scale
    wr = max(5, int(14*s))
    a = (int(cx-29*s), int(cy+12*s))
    b = (int(cx+29*s), int(cy+12*s))

    pygame.draw.circle(screen, ROAD_DARK, a, wr, max(2, int(3*s)))
    pygame.draw.circle(screen, ROAD_DARK, b, wr, max(2, int(3*s)))

    points = [
        a,
        (int(cx-4*s), int(cy-12*s)),
        (int(cx+4*s), int(cy+12*s)),
        a,
        b,
        (int(cx-4*s), int(cy-12*s)),
        (int(cx+20*s), int(cy-14*s)),
        b
    ]

    for p1, p2 in zip(points, points[1:]):
        pygame.draw.line(screen, PRIMARY_DARK, p1, p2,
                         max(2, int(3*s)))


def draw_house(cx, cy, scale=1.0):
    s = scale
    w, h = int(76*s), int(60*s)

    pygame.draw.rect(
        screen, (249, 222, 179),
        (int(cx-w/2), int(cy-h/2), w, h),
        border_radius=max(3, int(5*s))
    )

    roof = [
        (int(cx-49*s), int(cy-18*s)),
        (int(cx), int(cy-62*s)),
        (int(cx+49*s), int(cy-18*s))
    ]
    pygame.draw.polygon(screen, (194, 72, 64), roof)

    pygame.draw.rect(
        screen, (105, 69, 48),
        (int(cx-11*s), int(cy+3*s), int(22*s), int(37*s))
    )

    for dx in (-27, 10):
        pygame.draw.rect(
            screen, (143, 204, 229),
            (int(cx+dx*s), int(cy-6*s), int(18*s), int(18*s))
        )


def draw_food(cx, cy, kind="pizza", scale=1.0):
    s = scale

    if kind == "pizza":
        pygame.draw.circle(screen, (225, 157, 70),
                           (int(cx), int(cy)), int(32*s))
        pygame.draw.circle(screen, (195, 85, 52),
                           (int(cx), int(cy)), int(26*s))
        for dx, dy in [(-11, -8), (8, -9), (-3, 9), (14, 7), (-15, 9)]:
            pygame.draw.circle(screen, ROAD_DARK,
                               (int(cx+dx*s), int(cy+dy*s)),
                               max(2, int(4*s)))

    elif kind == "burger":
        pygame.draw.ellipse(
            screen, (211, 147, 68),
            (int(cx-35*s), int(cy-22*s),
             int(70*s), int(25*s))
        )
        pygame.draw.rect(
            screen, (105, 61, 38),
            (int(cx-33*s), int(cy-4*s),
             int(66*s), int(14*s)),
            border_radius=max(2, int(4*s))
        )
        pygame.draw.rect(
            screen, GREEN_DARK,
            (int(cx-37*s), int(cy+8*s),
             int(74*s), int(7*s)),
            border_radius=max(2, int(3*s))
        )
        pygame.draw.ellipse(
            screen, (237, 182, 90),
            (int(cx-35*s), int(cy-28*s),
             int(70*s), int(19*s))
        )

    else:
        pygame.draw.rect(
            screen, (237, 173, 74),
            (int(cx-32*s), int(cy-25*s),
             int(64*s), int(50*s)),
            border_radius=max(3, int(7*s))
        )
        pygame.draw.line(screen, (185, 119, 45),
                         (int(cx), int(cy-25*s)),
                         (int(cx), int(cy+25*s)), 2)


def draw_traffic_light(cx, cy, scale=1.0, state="red"):
    s = scale
    r = pygame.Rect(int(cx-16*s), int(cy-48*s),
                    int(32*s), int(96*s))
    pygame.draw.rect(screen, ROAD_DARK, r, border_radius=int(8*s))

    colors = {
        "red": RED,
        "yellow": YELLOW,
        "green": GREEN
    }

    for i, name in enumerate(["red", "yellow", "green"]):
        col = colors[name] if name == state else (75, 79, 86)
        pygame.draw.circle(screen, col,
                           (int(cx), int(cy + (-28+i*28)*s)),
                           max(3, int(7*s)))


# ============================================================
# EFFECTS
# ============================================================

@dataclass
class Particle:
    x: float
    y: float
    vx: float
    vy: float
    life: int
    size: int
    color: tuple


class Confetti:
    def __init__(self):
        colors = [PRIMARY, GREEN, RED, ORANGE, YELLOW]
        self.particles = [
            Particle(
                random.randint(0, WIDTH),
                random.randint(-HEIGHT, 0),
                random.uniform(-2.5, 2.5),
                random.uniform(2.0, 6.5),
                random.randint(60, 140),
                random.randint(4, 9),
                random.choice(colors)
            )
            for _ in range(140)
        ]

    def update(self):
        for p in self.particles:
            p.x += p.vx
            p.y += p.vy
            p.vy += 0.04
            p.life -= 1

    def draw(self):
        for p in self.particles:
            if p.life <= 0:
                continue
            pygame.draw.rect(
                screen, p.color,
                (int(p.x), int(p.y), p.size, p.size*2),
                border_radius=2
            )


# ============================================================
# GAME
# ============================================================

class DeliveryDash:
    def __init__(self):
        self.state = "menu"
        self.level = 0

        self.score = 0
        self.payment = 0
        self.lives = 3
        self.streak = 0

        self.feedback = ""
        self.feedback_good = False

        self.round_time = 0.0
        self.time_left = 0.0

        self.dragging = None
        self.drag_pos = (0, 0)

        self.confetti = None
        self.anim_frame = 0

        self.scenarios = {}

        self.generate_all_scenarios()

    # --------------------------------------------------------
    # SCENARIO GENERATION
    # --------------------------------------------------------

    def generate_all_scenarios(self):
        # LEVEL 1
        # Valid vehicles vary, so player cannot memorize a fixed answer.
        distance = random.choice([12, 15, 18, 20, 22, 24])
        deadline = random.choice([24, 27, 30, 33, 36, 40])

        vehicles = [
            ("Bicycle", random.choice([18, 20, 22])),
            ("Scooter", random.choice([35, 40, 42])),
            ("Fast Bike", random.choice([55, 60, 65]))
        ]

        self.scenarios[1] = {
            "distance": distance,
            "deadline": deadline,
            "vehicles": vehicles
        }

        # LEVEL 2
        speed = random.choice([30, 36, 40, 45, 48, 50, 60])
        minutes = random.choice([20, 25, 30, 35, 40, 45])
        max_distance = speed * minutes / 60

        self.scenarios[2] = {
            "speed": speed,
            "minutes": minutes,
            "max_distance": max_distance
        }

        # LEVEL 3
        # Generate one route that is safe and one that is unsafe.
        deadline3 = random.choice([55, 60, 65, 70])
        route_a = self.random_route()
        route_b = self.random_route()

        # Ensure one safe / one unsafe.
        ta = route_a["distance"] / route_a["speed"] * 60 + route_a["delay"]
        tb = route_b["distance"] / route_b["speed"] * 60 + route_b["delay"]

        if (ta <= deadline3) == (tb <= deadline3):
            route_a = {
                "distance": random.choice([35, 40, 45]),
                "speed": random.choice([35, 40]),
                "delay": random.choice([10, 15, 20])
            }
            route_b = {
                "distance": random.choice([45, 50, 55]),
                "speed": random.choice([55, 60, 65]),
                "delay": 0
            }

        self.scenarios[3] = {
            "deadline": deadline3,
            "A": route_a,
            "B": route_b
        }

        # LEVEL 4
        pizza_distance = random.choice([12, 15, 18, 20])
        burger_distance = random.choice([24, 27, 30, 33, 36])
        pizza_deadline = random.choice([25, 30, 35])
        burger_deadline = random.choice([38, 40, 45, 48])

        vehicle_a = random.choice([30, 32, 35])
        vehicle_b = random.choice([55, 60, 65])

        self.scenarios[4] = {
            "pizza": {
                "distance": pizza_distance,
                "deadline": pizza_deadline
            },
            "burger": {
                "distance": burger_distance,
                "deadline": burger_deadline
            },
            "vehicles": {
                "Scooter": vehicle_a,
                "Fast Bike": vehicle_b
            }
        }

        # LEVEL 5
        # Generate 3 routes. Exactly one is the best strategy:
        # fastest route that is inside the deadline.
        final_deadline = random.choice([48, 52, 55, 58, 60])

        routes = [
            {
                "distance": random.choice([30, 35, 40]),
                "speed": random.choice([45, 50, 55]),
                "delay": random.choice([5, 10, 15])
            },
            {
                "distance": random.choice([40, 45, 50]),
                "speed": random.choice([55, 60, 65]),
                "delay": random.choice([0, 5])
            },
            {
                "distance": random.choice([22, 25, 28, 32]),
                "speed": random.choice([35, 40, 45]),
                "delay": random.choice([10, 15, 20])
            }
        ]

        # Ensure at least two options have different status, and the
        # intended solution is the fastest safe route.
        for _ in range(100):
            totals = [
                r["distance"] / r["speed"] * 60 + r["delay"]
                for r in routes
            ]
            safe = [t <= final_deadline for t in totals]

            if any(safe) and not all(safe):
                break

            routes = [
                {
                    "distance": random.choice([30, 35, 40]),
                    "speed": random.choice([45, 50, 55]),
                    "delay": random.choice([5, 10, 15])
                },
                {
                    "distance": random.choice([40, 45, 50]),
                    "speed": random.choice([55, 60, 65]),
                    "delay": random.choice([0, 5])
                },
                {
                    "distance": random.choice([22, 25, 28, 32]),
                    "speed": random.choice([35, 40, 45]),
                    "delay": random.choice([10, 15, 20])
                }
            ]

        self.scenarios[5] = {
            "deadline": final_deadline,
            "routes": routes
        }

    @staticmethod
    def random_route():
        return {
            "distance": random.choice([30, 35, 40, 45, 50, 55]),
            "speed": random.choice([35, 40, 45, 50, 55, 60]),
            "delay": random.choice([0, 5, 10, 15, 20])
        }

    # --------------------------------------------------------
    # FLOW
    # --------------------------------------------------------

    def start_game(self):
        self.state = "playing"
        self.level = 1
        self.score = 0
        self.payment = 0
        self.lives = 3
        self.streak = 0
        self.generate_all_scenarios()
        self.reset_level()

    def reset_level(self):
        self.feedback = ""
        self.feedback_good = False
        self.dragging = None
        self.drag_pos = (0, 0)
        self.confetti = None
        self.anim_frame = 0

        self.round_time = self.level_time_limit()
        self.time_left = self.round_time

        self.selected_route = None
        self.selected_vehicle = None

        self.ravi_x = 570
        self.ravi_dragging = False

        # Level 5 has an extra verification step.
        self.final_step = 0
        self.final_choice = None

    def level_time_limit(self):
        return {
            1: 35,
            2: 30,
            3: 35,
            4: 45,
            5: 55
        }.get(self.level, 30)

    def go_next(self):
        if self.level >= 5:
            self.state = "complete"
            return

        self.level += 1
        self.reset_level()

    def success(self, message, base_reward=100, bonus=0):
        # Time bonus
        ratio = max(0.0, self.time_left / max(1.0, self.round_time))
        speed_bonus = int(ratio * 50)

        streak_bonus = self.streak * 10
        total = base_reward + bonus + speed_bonus + streak_bonus

        self.score += total
        self.payment += total
        self.streak += 1

        self.feedback = message
        self.feedback_good = True
        self.confetti = Confetti()
        self.state = "success"

    def failure(self, message):
        self.lives -= 1
        self.streak = 0
        self.feedback = message
        self.feedback_good = False

        if self.lives <= 0:
            self.state = "game_over"
        else:
            self.state = "failure"

    def timeout(self):
        self.failure(
            "TIME'S UP! Ravi could not make the decision fast enough."
        )

    # --------------------------------------------------------
    # HUD
    # --------------------------------------------------------

    def draw_top(self):
        pygame.draw.rect(screen, WHITE, (0, 0, WIDTH, 78))
        pygame.draw.line(screen, BORDER, (0, 77), (WIDTH, 77), 2)

        draw_text(screen, "DELIVERY DASH", 32, 14, 26,
                  PRIMARY_DARK, True)
        draw_text(screen, "SAVE THE DELIVERY", 33, 45, 12,
                  MUTED, True)

        # Level progress
        start = 510
        for i in range(5):
            x = start + i * 82
            col = (
                GREEN if i+1 < self.level
                else PRIMARY if i+1 == self.level
                else (222, 226, 233)
            )
            pygame.draw.circle(screen, col, (x, 37), 14)
            draw_text(screen, i+1, x, 37, 11, WHITE, True, True)
            if i < 4:
                pygame.draw.line(screen, BORDER,
                                 (x+14, 37), (x+68, 37), 4)

        # Timer
        timer_ratio = max(0, self.time_left / max(1, self.round_time))
        timer_col = GREEN if timer_ratio > .5 else ORANGE if timer_ratio > .25 else RED

        pygame.draw.rect(screen, (234, 237, 242),
                         (925, 14, 105, 15), border_radius=8)
        pygame.draw.rect(screen, timer_col,
                         (925, 14, int(105*timer_ratio), 15),
                         border_radius=8)
        draw_text(screen, f"{max(0, math.ceil(self.time_left))}s",
                  1045, 12, 16, timer_col, True)

        draw_text(screen, f"SCORE {self.score}", 1100, 43,
                  15, TEXT, True)

        # Lives
        draw_text(screen, "LIVES", 850, 42, 12, MUTED, True)
        for i in range(3):
            col = RED if i < self.lives else BORDER
            pygame.draw.circle(screen, col,
                               (898+i*18, 48), 6)

    def header(self, title, subtitle):
        self.draw_top()
        draw_text(screen, f"LEVEL {self.level} - {title}",
                  42, 105, 27, TEXT, True)
        draw_text(screen, subtitle, 42, 140, 17, MUTED)

    # --------------------------------------------------------
    # MENU
    # --------------------------------------------------------

    def draw_menu(self):
        screen.fill(BG)

        pygame.draw.circle(screen, LIGHT_BLUE, (1080, 150), 190)
        pygame.draw.circle(screen, LIGHT_GREEN, (160, 650), 150)

        draw_text(screen, "DELIVERY", 75, 105, 57,
                  PRIMARY_DARK, True)
        draw_text(screen, "DASH", 75, 168, 72, TEXT, True)

        draw_text(screen, "SAVE THE DELIVERY!",
                  80, 265, 25, GREEN_DARK, True)

        paragraph(
            "Help Ravi make smart delivery decisions. "
            "Calculate time, distance and speed yourself. "
            "Every second matters — and every mistake costs payment.",
            82, 315, 500, 20, TEXT, 9
        )

        panel((80, 480, 515, 150))
        draw_text(screen, "5 CHALLENGING LEVELS",
                  110, 512, 18, PRIMARY_DARK, True)
        draw_text(screen, "CALCULATE • CHOOSE • DRAG • DELIVER",
                  110, 548, 16, TEXT, True)
        draw_text(screen, "3 LIVES  •  TIME BONUS  •  STREAK BONUS",
                  110, 582, 15, MUTED, True)

        draw_scooter(850, 380, 2.0)
        draw_food(1060, 285, "pizza", 1.0)
        draw_house(1070, 485, 1.0)

        button((790, 575, 350, 65),
               "START DELIVERY", PRIMARY, 23)

        draw_text(screen,
                  "Tip: the game will NOT show you the answers.",
                  80, 710, 13, MUTED)

    # --------------------------------------------------------
    # LEVEL 1
    # --------------------------------------------------------

    def draw_level1(self):
        data = self.scenarios[1]

        self.header(
            "CHOOSE THE RIGHT RIDE",
            "Drag the SLOWEST vehicle that can still reach the customer on time."
        )

        panel((40, 185, 350, 475))
        badge(68, 210, "DELIVERY")

        draw_food(115, 282, "pizza", 0.72)
        draw_text(screen, "PIZZA ORDER", 165, 263,
                  21, TEXT, True)
        draw_text(screen, f"Distance: {data['distance']} km",
                  68, 325, 18, MUTED)
        draw_text(screen, f"Deadline: {data['deadline']} min",
                  68, 358, 18, RED, True)

        pygame.draw.line(screen, BORDER,
                         (68, 395), (365, 395), 2)

        draw_text(screen, "STRATEGY CHALLENGE",
                  68, 420, 15, PRIMARY_DARK, True)
        paragraph(
            "More speed is NOT automatically better. "
            "Find the slowest vehicle whose travel time fits the deadline.",
            68, 450, 280, 17, TEXT, 7
        )

        # Road
        pygame.draw.rect(screen, ROAD_DARK,
                         (425, 210, 800, 150), border_radius=20)
        pygame.draw.rect(screen, ROAD,
                         (425, 218, 800, 134), border_radius=17)

        for x in range(450, 1200, 80):
            pygame.draw.rect(screen, (232, 232, 222),
                             (x, 281, 42, 5), border_radius=2)

        draw_scooter(570, 286, 1.05)
        draw_text(screen, "RAVI", 570, 338, 12,
                  WHITE, True, True)

        draw_house(1090, 284, .72)
        draw_text(screen, "CUSTOMER", 1090, 338, 12,
                  WHITE, True, True)

        vehicles = [
            ("Bicycle", data["vehicles"][0][1], "bicycle"),
            ("Scooter", data["vehicles"][1][1], "scooter"),
            ("Fast Bike", data["vehicles"][2][1], "fast"),
        ]

        for i, (name, speed, kind) in enumerate(vehicles):
            x = 425 + i * 265
            r = pygame.Rect(x, 395, 235, 245)

            selected = self.dragging == kind
            fill = LIGHT_BLUE if selected else WHITE
            border = PRIMARY if selected else BORDER

            pygame.draw.rect(screen, fill, r, border_radius=18)
            pygame.draw.rect(screen, border, r,
                             3 if selected else 2,
                             border_radius=18)

            if kind == "bicycle":
                draw_bicycle(r.centerx, 455, .85)
            elif kind == "scooter":
                draw_scooter(r.centerx, 455, .85)
            else:
                draw_fast_bike(r.centerx, 455, .85)

            draw_text(screen, name, r.centerx, 520,
                      19, TEXT, True, True)

            # IMPORTANT: only speed is shown.
            # Travel time / answer is intentionally hidden.
            draw_text(screen, f"{speed} km/h",
                      r.centerx, 552, 17,
                      PRIMARY_DARK, True, True)

            pygame.draw.rect(screen,
                             PRIMARY if selected else ROAD_DARK,
                             (r.x+35, 585, 165, 32),
                             border_radius=10)
            draw_text(screen, "DRAG TO RAVI",
                      r.centerx, 601, 12,
                      WHITE, True, True)

    def handle_level1(self, event):
        cards = [
            ("bicycle", pygame.Rect(425, 395, 235, 245)),
            ("scooter", pygame.Rect(690, 395, 235, 245)),
            ("fast", pygame.Rect(955, 395, 235, 245)),
        ]

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            for kind, r in cards:
                if r.collidepoint(event.pos):
                    self.dragging = kind
                    self.drag_pos = event.pos
                    break

        elif event.type == pygame.MOUSEMOTION and self.dragging:
            self.drag_pos = event.pos

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            if not self.dragging:
                return

            drop = pygame.Rect(500, 215, 145, 130)
            kind = self.dragging

            if drop.collidepoint(event.pos):
                data = self.scenarios[1]
                speed_map = {
                    "bicycle": data["vehicles"][0][1],
                    "scooter": data["vehicles"][1][1],
                    "fast": data["vehicles"][2][1]
                }

                speed = speed_map[kind]
                minutes = data["distance"] / speed * 60

                valid = minutes <= data["deadline"]

                # Need SLOWEST valid vehicle.
                valid_speeds = [
                    (v[1], v[0])
                    for v in data["vehicles"]
                    if data["distance"] / v[1] * 60 <= data["deadline"]
                ]

                if valid_speeds:
                    target_speed, target_name = min(valid_speeds)
                else:
                    target_speed, target_name = None, None

                if valid and speed == target_speed:
                    self.success(
                        "SMART CHOICE! You picked the slowest ride "
                        "that meets the deadline.",
                        100, 30
                    )
                elif valid:
                    self.failure(
                        "That vehicle arrives on time, but it is faster "
                        "than necessary. The mission asked for the slowest "
                        "valid vehicle."
                    )
                else:
                    self.failure(
                        "Too slow! Ravi would arrive after the deadline."
                    )

            self.dragging = None

    # --------------------------------------------------------
    # LEVEL 2
    # --------------------------------------------------------

    def draw_level2(self):
        data = self.scenarios[2]

        self.header(
            "HOW FAR CAN RAVI GO?",
            "Drag Ravi to the checkpoint he should reach after the given time."
        )

        panel((40, 185, 355, 475))
        badge(68, 210, "MISSION")

        draw_text(screen, f"Speed: {data['speed']} km/h",
                  68, 270, 22, TEXT, True)
        draw_text(screen, f"Time: {data['minutes']} minutes",
                  68, 308, 20, MUTED)

        pygame.draw.line(screen, BORDER,
                         (68, 350), (365, 350), 2)

        draw_text(screen, "Your task",
                  68, 382, 16, PRIMARY_DARK, True)

        paragraph(
            "Move Ravi to the correct distance marker. "
            "Do the calculation in your head or on paper.",
            68, 415, 280, 17, TEXT, 7
        )

        draw_text(screen, "No formula is shown.",
                  68, 530, 15, MUTED, True)
        draw_text(screen, "YOU must work it out.",
                  68, 555, 15, PRIMARY_DARK, True)

        # Dynamic road scale
        max_distance = max(30, math.ceil(data["max_distance"] / 10) * 10)
        x0, x1 = 455, 1150
        y = 390

        pygame.draw.line(screen, ROAD_DARK,
                         (x0, y), (x1, y), 42)
        pygame.draw.line(screen, ROAD,
                         (x0, y), (x1, y), 32)

        # Five checkpoints
        checkpoints = 6
        for i in range(checkpoints):
            distance = max_distance * i / (checkpoints-1)
            x = x0 + (x1-x0) * i/(checkpoints-1)

            pygame.draw.circle(screen, WHITE,
                               (int(x), y), 5)
            draw_text(screen, f"{distance:.0f} km",
                      x, 335, 16, TEXT, True, True)

        # Hide the target: there is no highlighted correct marker.
        # Player sees only ordinary checkpoints.
        pygame.draw.rect(screen, SKY,
                         (450, 470, 720, 165),
                         border_radius=18)

        draw_text(screen,
                  "DRAG RAVI ALONG THE ROAD",
                  810, 505, 19, PRIMARY_DARK, True, True)

        draw_text(screen,
                  "Then press CHECK POSITION",
                  810, 538, 16, MUTED, False, True)

        draw_scooter(self.ravi_x, 590, .8)
        draw_text(screen, "RAVI", self.ravi_x, 632,
                  12, PRIMARY_DARK, True, True)

        button((965, 560, 185, 50),
               "CHECK POSITION", PRIMARY, 16)

    def handle_level2(self, event):
        x0, x1 = 455, 1150
        max_distance = max(
            30,
            math.ceil(self.scenarios[2]["max_distance"] / 10) * 10
        )
        target_x = x0 + (
            self.scenarios[2]["max_distance"] / max_distance
        ) * (x1-x0)

        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if math.dist(event.pos, (self.ravi_x, 590)) < 65:
                self.ravi_dragging = True

            elif pygame.Rect(965, 560, 185, 50).collidepoint(event.pos):
                if abs(self.ravi_x - target_x) <= 24:
                    self.success(
                        "POSITION LOCKED! Ravi is exactly where he should be.",
                        100, 30
                    )
                else:
                    self.failure(
                        "Wrong checkpoint. Recalculate how far Ravi travels "
                        "during the given time."
                    )

        elif event.type == pygame.MOUSEMOTION and self.ravi_dragging:
            self.ravi_x = max(x0, min(x1, event.pos[0]))

        elif event.type == pygame.MOUSEBUTTONUP and event.button == 1:
            self.ravi_dragging = False

    # --------------------------------------------------------
    # LEVEL 3
    # --------------------------------------------------------

    def draw_route(self, rect, route_name, route, selected=False):
        r = pygame.Rect(rect)
        border = PRIMARY if selected else BORDER

        pygame.draw.rect(screen, WHITE, r, border_radius=18)
        pygame.draw.rect(screen, border, r,
                         3 if selected else 2,
                         border_radius=18)

        badge(r.x+20, r.y+18, f"ROUTE {route_name}")

        draw_text(screen,
                  f"{route['distance']} km",
                  r.x+25, r.y+78, 22, TEXT, True)
        draw_text(screen,
                  f"{route['speed']} km/h",
                  r.x+25, r.y+112, 18, MUTED)
        draw_text(screen,
                  "Traffic delay",
                  r.x+25, r.y+147, 16, MUTED)
        draw_text(screen,
                  f"+ {route['delay']} min",
                  r.x+160, r.y+147, 16,
                  RED if route["delay"] else GREEN, True)

        # Do NOT show total time.
        draw_text(screen,
                  "Total travel time: ???",
                  r.x+25, r.y+190, 17,
                  PRIMARY_DARK, True)

        return button(
            (r.x+25, r.y+235, r.width-50, 45),
            f"TAKE ROUTE {route_name}",
            PRIMARY,
            15
        )

    def draw_level3(self):
        data = self.scenarios[3]

        self.header(
            "TRAFFIC TROUBLE",
            "Choose the route that reaches the customer before the deadline."
        )

        panel((40, 190, 300, 445))
        badge(68, 215, "MISSION")

        draw_food(110, 285, "burger", .72)
        draw_text(screen, "BURGER ORDER",
                  165, 268, 20, TEXT, True)

        draw_text(screen,
                  f"Deadline: {data['deadline']} min",
                  68, 330, 19, RED, True)

        pygame.draw.line(screen, BORDER,
                         (68, 365), (310, 365), 2)

        draw_text(screen, "Calculate:",
                  68, 395, 16, PRIMARY_DARK, True)
        draw_text(screen, "travel time + traffic delay",
                  68, 427, 16, TEXT)
        draw_text(screen, "Then compare with deadline.",
                  68, 455, 16, TEXT)

        draw_text(screen, "The answer is hidden.",
                  68, 530, 15, MUTED, True)

        self.draw_route(
            (390, 210, 385, 325),
            "A", data["A"],
            self.selected_route == "A"
        )
        self.draw_route(
            (815, 210, 385, 325),
            "B", data["B"],
            self.selected_route == "B"
        )

        # Visual road
        pygame.draw.rect(screen, ROAD_DARK,
                         (425, 570, 750, 62), border_radius=15)
        draw_scooter(500, 600, .48)
        pygame.draw.line(screen, WHITE,
                         (555, 600), (1030, 600), 4)
        draw_house(1110, 600, .42)

    def handle_level3(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        a = pygame.Rect(415, 445, 335, 45)
        b = pygame.Rect(840, 445, 335, 45)

        if a.collidepoint(event.pos):
            self.selected_route = "A"
            route = self.scenarios[3]["A"]
            total = route["distance"]/route["speed"]*60 + route["delay"]
            deadline = self.scenarios[3]["deadline"]

            if total <= deadline:
                self.success(
                    "Route A works! Ravi reaches before the deadline.",
                    100, 35
                )
            else:
                self.failure(
                    "Route A is too slow once traffic is included."
                )

        elif b.collidepoint(event.pos):
            self.selected_route = "B"
            route = self.scenarios[3]["B"]
            total = route["distance"]/route["speed"]*60 + route["delay"]
            deadline = self.scenarios[3]["deadline"]

            if total <= deadline:
                self.success(
                    "Excellent route planning! Ravi beats the deadline.",
                    100, 35
                )
            else:
                self.failure(
                    "Route B misses the deadline. Traffic and distance matter."
                )

    # --------------------------------------------------------
    # LEVEL 4
    # --------------------------------------------------------

    def draw_level4(self):
        data = self.scenarios[4]

        self.header(
            "TWO ORDERS, ONE RIDER",
            "Choose one vehicle AND an order sequence that saves both deliveries."
        )

        panel((40, 190, 330, 455))
        badge(68, 215, "TWO ORDERS")

        draw_food(100, 285, "pizza", .58)
        draw_text(screen, "PIZZA",
                  150, 270, 18, TEXT, True)
        draw_text(screen,
                  f"{data['pizza']['distance']} km",
                  150, 300, 16, MUTED)
        draw_text(screen,
                  f"Deadline {data['pizza']['deadline']} min",
                  150, 327, 15, RED, True)

        draw_food(100, 390, "burger", .58)
        draw_text(screen, "BURGER",
                  150, 375, 18, TEXT, True)
        draw_text(screen,
                  f"{data['burger']['distance']} km",
                  150, 405, 16, MUTED)
        draw_text(screen,
                  f"Deadline {data['burger']['deadline']} min",
                  150, 432, 15, RED, True)

        pygame.draw.line(screen, BORDER,
                         (68, 465), (340, 465), 2)

        draw_text(screen, "Step 1: vehicle",
                  68, 490, 15, PRIMARY_DARK, True)
        draw_text(screen, "Step 2: delivery order",
                  68, 518, 15, PRIMARY_DARK, True)
        draw_text(screen, "Both must be valid.",
                  68, 550, 15, MUTED)

        # Vehicle choices — only speed shown.
        vehicles = [
            ("Scooter", data["vehicles"]["Scooter"], "scooter"),
            ("Fast Bike", data["vehicles"]["Fast Bike"], "fast"),
        ]

        for i, (name, speed, kind) in enumerate(vehicles):
            x = 405 + i*405
            r = pygame.Rect(x, 205, 365, 220)

            selected = self.selected_vehicle == name

            pygame.draw.rect(
                screen,
                LIGHT_BLUE if selected else WHITE,
                r, border_radius=18
            )
            pygame.draw.rect(
                screen,
                PRIMARY if selected else BORDER,
                r, 3 if selected else 2,
                border_radius=18
            )

            if kind == "scooter":
                draw_scooter(r.centerx, 260, .82)
            else:
                draw_fast_bike(r.centerx, 260, .82)

            draw_text(screen, name, r.centerx, 320,
                      21, TEXT, True, True)
            draw_text(screen, f"{speed} km/h",
                      r.centerx, 351, 17,
                      PRIMARY_DARK, True, True)

            button(
                (x+70, 375, 225, 38),
                "SELECT VEHICLE",
                PRIMARY if not selected else GREEN,
                14
            )

        # Order choice appears only after vehicle selection.
        panel((405, 450, 770, 190))

        if not self.selected_vehicle:
            draw_text(screen,
                      "STEP 1: Select a vehicle above.",
                      790, 515, 20, PRIMARY_DARK, True, True)
        else:
            draw_text(screen,
                      f"Vehicle selected: {self.selected_vehicle}",
                      790, 485, 19, TEXT, True, True)

            draw_text(screen,
                      "STEP 2: Choose which order Ravi should deliver first.",
                      790, 515, 16, MUTED, False, True)

            button((470, 555, 260, 50),
                   "PIZZA FIRST",
                   PRIMARY, 16)
            button((850, 555, 260, 50),
                   "BURGER FIRST",
                   PRIMARY, 16)

    def handle_level4(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        # Vehicle selection
        if pygame.Rect(475, 375, 225, 38).collidepoint(event.pos):
            self.selected_vehicle = "Scooter"
            return

        if pygame.Rect(880, 375, 225, 38).collidepoint(event.pos):
            self.selected_vehicle = "Fast Bike"
            return

        if not self.selected_vehicle:
            return

        # Order selection
        if pygame.Rect(470, 555, 260, 50).collidepoint(event.pos):
            self.evaluate_level4("Pizza")
        elif pygame.Rect(850, 555, 260, 50).collidepoint(event.pos):
            self.evaluate_level4("Burger")

    def evaluate_level4(self, first):
        data = self.scenarios[4]
        speed = data["vehicles"][self.selected_vehicle]

        # This is intentionally a simplified route model:
        # first order is delivered from Ravi's current location,
        # second order is then delivered from the first customer's
        # area. We use cumulative distances for the challenge.
        #
        # For the generated scenarios, the first/second decision is
        # meaningful but not exposed to the player.
        pizza = data["pizza"]
        burger = data["burger"]

        if first == "Pizza":
            first_order = pizza
            second_order = burger
        else:
            first_order = burger
            second_order = pizza

        first_time = first_order["distance"] / speed * 60
        second_time = (
            second_order["distance"] / speed * 60
        )

        first_ok = first_time <= first_order["deadline"]
        second_ok = first_time + second_time <= second_order["deadline"]

        # If the selected vehicle/order is valid, success.
        if first_ok and second_ok:
            self.success(
                "MASTER PLANNER! Both customers receive their orders "
                "before their deadlines.",
                150, 60
            )
        else:
            if not first_ok:
                msg = "The first delivery already misses its deadline."
            else:
                msg = "The second delivery becomes late after the first stop."
            self.failure(msg)

    # --------------------------------------------------------
    # LEVEL 5
    # --------------------------------------------------------

    def draw_final_route(self, rect, route_name, route, selected=False):
        r = pygame.Rect(rect)

        pygame.draw.rect(
            screen,
            LIGHT_BLUE if selected else WHITE,
            r, border_radius=18
        )
        pygame.draw.rect(
            screen,
            PRIMARY if selected else BORDER,
            r, 3 if selected else 2,
            border_radius=18
        )

        badge(r.x+18, r.y+18, f"ROUTE {route_name}")

        draw_text(screen,
                  f"Distance: {route['distance']} km",
                  r.x+20, r.y+72, 17, TEXT, True)
        draw_text(screen,
                  f"Speed: {route['speed']} km/h",
                  r.x+20, r.y+103, 16, MUTED)
        draw_text(screen,
                  f"Traffic: +{route['delay']} min",
                  r.x+20, r.y+134, 16,
                  RED if route["delay"] else GREEN, True)

        # Hide total calculation.
        draw_text(screen,
                  "ARRIVAL TIME: ???",
                  r.x+20, r.y+176, 18,
                  PRIMARY_DARK, True)

        return button(
            (r.x+20, r.y+214, r.width-40, 42),
            "SELECT ROUTE",
            PRIMARY,
            14
        )

    def draw_level5(self):
        data = self.scenarios[5]

        self.header(
            "FINAL DELIVERY",
            "Choose the fastest route that still beats the deadline."
        )

        draw_text(screen,
                  "FINAL FOOD ORDER",
                  50, 188, 20, TEXT, True)
        draw_text(screen,
                  f"Deadline: {data['deadline']} minutes",
                  50, 220, 17, RED, True)

        for i, route in enumerate(data["routes"]):
            self.draw_final_route(
                (45+i*400, 265, 370, 270),
                chr(65+i),
                route,
                self.final_choice == i
            )

        panel((45, 575, 1190, 105))

        if self.final_choice is None:
            draw_text(
                screen,
                "STEP 1: Pick the route you believe is the fastest route "
                "that still meets the deadline.",
                70, 618, 18, TEXT, True
            )
        else:
            draw_text(
                screen,
                f"Route {chr(65+self.final_choice)} selected.",
                70, 603, 19, TEXT, True
            )
            draw_text(
                screen,
                "STEP 2: Send Ravi to reveal whether your calculation was correct.",
                70, 635, 16, MUTED
            )
            button((1000, 600, 190, 52),
                   "SEND RAVI", GREEN, 17)

    def handle_level5(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        buttons = [
            ("A", pygame.Rect(65, 479, 330, 42)),
            ("B", pygame.Rect(465, 479, 330, 42)),
            ("C", pygame.Rect(865, 479, 330, 42)),
        ]

        for idx, (_, rect) in enumerate(buttons):
            if rect.collidepoint(event.pos):
                self.final_choice = idx
                return

        if self.final_choice is not None:
            if pygame.Rect(1000, 600, 190, 52).collidepoint(event.pos):
                data = self.scenarios[5]
                deadline = data["deadline"]

                totals = [
                    r["distance"]/r["speed"]*60 + r["delay"]
                    for r in data["routes"]
                ]

                safe_indices = [
                    i for i, total in enumerate(totals)
                    if total <= deadline
                ]

                if safe_indices:
                    best = min(safe_indices, key=lambda i: totals[i])
                else:
                    best = None

                if self.final_choice == best:
                    self.success(
                        "FINAL DELIVERY SAVED! Perfect route selection.",
                        200, 100
                    )
                else:
                    self.failure(
                        "Wrong strategic choice. Remember: calculate the "
                        "full travel time, include traffic, then choose the "
                        "FASTEST route that is still on time."
                    )

    # --------------------------------------------------------
    # RESULT SCREENS
    # --------------------------------------------------------

    def draw_result(self, success_state):
        screen.fill(BG)

        if success_state:
            if self.confetti:
                self.confetti.update()
                self.confetti.draw()

            panel((245, 110, 790, 535), 30, LIGHT_GREEN)

            draw_text(screen,
                      "DELIVERY SUCCESSFUL!",
                      640, 175, 39,
                      GREEN_DARK, True, True)

            bounce = math.sin(self.anim_frame*.12)*7
            draw_scooter(500, 325+bounce, 1.4, dance=True)
            draw_food(640, 325, "box", .82)
            draw_house(805, 325, .82)

            draw_text(screen,
                      "RAVI MADE IT ON TIME!",
                      640, 420, 24, TEXT, True, True)

            draw_text(screen,
                      f"+ PAYMENT: Rs.{self.payment}",
                      640, 462, 20,
                      GREEN_DARK, True, True)

            draw_text(screen,
                      f"SCORE: {self.score}",
                      640, 495, 18,
                      PRIMARY_DARK, True, True)

            bonus = int(
                max(0, self.time_left / max(1, self.round_time)) * 50
            )
            draw_text(screen,
                      f"TIME BONUS: +{bonus}",
                      640, 523, 14,
                      MUTED, True, True)

            label = "FINISH GAME" if self.level == 5 else "NEXT LEVEL"
            button((480, 565, 320, 55),
                   label, GREEN, 19)

        else:
            panel((245, 110, 790, 535), 30, LIGHT_RED)

            draw_text(screen,
                      "DELIVERY FAILED",
                      640, 175, 39,
                      RED_DARK, True, True)

            draw_scooter(640, 320, 1.4, sad=True)

            draw_text(screen,
                      "Ravi missed the objective.",
                      640, 410, 24, TEXT, True, True)

            lines = wrap_text(self.feedback, 570, 17)
            yy = 455
            for line in lines[:5]:
                draw_text(screen, line, 640, yy, 17,
                          MUTED, False, True)
                yy += 26

            draw_text(screen,
                      f"LIVES REMAINING: {self.lives}",
                      640, 525, 15, RED_DARK, True, True)

            button((480, 565, 320, 55),
                   "TRY AGAIN", RED, 19)

    def handle_result(self, event):
        if event.type != pygame.MOUSEBUTTONDOWN or event.button != 1:
            return

        r = pygame.Rect(480, 565, 320, 55)

        if r.collidepoint(event.pos):
            if self.feedback_good:
                self.go_next()
            else:
                self.state = "playing"
                self.reset_level()

    # --------------------------------------------------------
    # GAME OVER
    # --------------------------------------------------------

    def draw_game_over(self):
        screen.fill(BG)

        panel((280, 150, 720, 460), 30, LIGHT_RED)

        draw_text(screen,
                  "GAME OVER",
                  640, 225, 46, RED_DARK, True, True)

        draw_scooter(640, 355, 1.35, sad=True)

        draw_text(screen,
                  "Ravi's delivery shift is over.",
                  640, 440, 23, TEXT, True, True)

        draw_text(screen,
                  f"FINAL SCORE: {self.score}",
                  640, 485, 20,
                  PRIMARY_DARK, True, True)

        draw_text(screen,
                  "Try again and beat your score.",
                  640, 520, 16, MUTED, False, True)

        button((470, 555, 340, 55),
               "RESTART", PRIMARY, 19)

    def handle_game_over(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(470, 555, 340, 55).collidepoint(event.pos):
                self.start_game()

    # --------------------------------------------------------
    # COMPLETE
    # --------------------------------------------------------

    def draw_complete(self):
        screen.fill(BG)

        pygame.draw.circle(screen, LIGHT_GREEN,
                           (1080, 145), 190)

        draw_text(screen,
                  "DELIVERY DASH COMPLETE!",
                  640, 120, 39, TEXT, True, True)

        draw_scooter(640, 285, 1.55, dance=True)
        draw_food(640, 405, "box", .9)

        draw_text(screen,
                  "RAVI'S PAYMENT IS SAFE!",
                  640, 470, 29,
                  GREEN_DARK, True, True)

        draw_text(screen,
                  f"FINAL SCORE: {self.score}",
                  640, 515, 24,
                  PRIMARY_DARK, True, True)

        draw_text(screen,
                  f"TOTAL PAYMENT: Rs.{self.payment}",
                  640, 550, 21,
                  GREEN_DARK, True, True)

        draw_text(screen,
                  "TIME • SPEED • DISTANCE MASTER",
                  640, 592, 17, MUTED, True, True)

        button((470, 645, 340, 55),
               "PLAY AGAIN", PRIMARY, 19)

    def handle_complete(self, event):
        if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
            if pygame.Rect(470, 645, 340, 55).collidepoint(event.pos):
                self.start_game()

    # --------------------------------------------------------
    # EVENT ROUTER
    # --------------------------------------------------------

    def handle_event(self, event):
        if event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE:
            self.state = "menu"
            return

        if self.state == "menu":
            if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                if pygame.Rect(790, 575, 350, 65).collidepoint(event.pos):
                    self.start_game()
            return

        if self.state == "playing":
            if event.type == pygame.MOUSEBUTTONDOWN:
                # Any action resets nothing; timer keeps running.
                pass

            if self.level == 1:
                self.handle_level1(event)
            elif self.level == 2:
                self.handle_level2(event)
            elif self.level == 3:
                self.handle_level3(event)
            elif self.level == 4:
                self.handle_level4(event)
            elif self.level == 5:
                self.handle_level5(event)

        elif self.state in ("success", "failure"):
            self.handle_result(event)

        elif self.state == "game_over":
            self.handle_game_over(event)

        elif self.state == "complete":
            self.handle_complete(event)

    # --------------------------------------------------------
    # UPDATE / DRAW
    # --------------------------------------------------------

    def update(self, dt):
        if self.state == "playing":
            self.time_left -= dt
            if self.time_left <= 0:
                self.time_left = 0
                self.timeout()

        self.anim_frame += 1

    def draw(self):
        if self.state == "menu":
            self.draw_menu()

        elif self.state == "playing":
            screen.fill(BG)

            if self.level == 1:
                self.draw_level1()
            elif self.level == 2:
                self.draw_level2()
            elif self.level == 3:
                self.draw_level3()
            elif self.level == 4:
                self.draw_level4()
            elif self.level == 5:
                self.draw_level5()

        elif self.state == "success":
            self.draw_result(True)

        elif self.state == "failure":
            self.draw_result(False)

        elif self.state == "game_over":
            self.draw_game_over()

        elif self.state == "complete":
            self.draw_complete()

        # Draw dragged vehicle on top of everything.
        if self.state == "playing" and self.dragging:
            x, y = self.drag_pos
            if self.dragging == "bicycle":
                draw_bicycle(x, y, .75)
            elif self.dragging == "scooter":
                draw_scooter(x, y, .75)
            elif self.dragging == "fast":
                draw_fast_bike(x, y, .75)

    def run(self):
        while True:
            dt = clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                self.handle_event(event)

            self.update(dt)
            self.draw()
            pygame.display.flip()


# ============================================================
# ENTRY POINT
# ============================================================

if __name__ == "__main__":
    DeliveryDash().run()
