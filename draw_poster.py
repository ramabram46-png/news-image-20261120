#!/usr/bin/env python3
"""The World in One Day — Friday 20 November 2026.

Draws a one-page newspaper front page that sums up a single day's world
news in one image: masthead, three equal leads, ten briefs, a world map,
an ALSO list and a DATE CHECK box.

Everything on the page is drawn with PIL primitives (rectangles, ellipses,
polygons, lines) and the DejaVu / Liberation fonts shipped with the system.
No photos, no downloaded art, no network. The output is deterministic:
the same run twice produces a byte-identical PNG.

Usage:
    python3 draw_poster.py [--out PATH] [--size N]
"""

import argparse
import math
import os
import sys

from PIL import Image, ImageDraw, ImageFont

# ---------------------------------------------------------------- palette
CREAM = (247, 240, 220)      # paper
CREAM_DK = (238, 228, 200)   # slightly deeper paper for panels
INK = (26, 26, 26)           # near-black text
INK_SOFT = (64, 60, 52)      # secondary text
RED = (176, 30, 36)          # strapline, kickers, numbers, pins
RED_DK = (140, 22, 28)
NAVY = (13, 38, 68)          # map sea, cyclone sky
NAVY_DK = (9, 28, 52)
TEAL = (31, 122, 109)        # badge 2, CPI bars
GREEN = (46, 125, 50)        # region bar: Americas
BLUE = (31, 78, 121)         # region bar: Europe
GOLD = (201, 162, 39)        # region bar: Mideast
SLATE = (61, 72, 82)         # region bar: merged tail
SAND = (216, 201, 163)       # map land
SKY_DUSK = (59, 45, 92)      # Shenzhen dusk sky
WHITE = (255, 255, 255)
GREY = (120, 116, 106)

FONT_DIR = "/usr/share/fonts/truetype"
SERIF_B = os.path.join(FONT_DIR, "dejavu/DejaVuSerif-Bold.ttf")
SERIF = os.path.join(FONT_DIR, "dejavu/DejaVuSerif.ttf")
SERIF_I = os.path.join(FONT_DIR, "liberation/LiberationSerif-Italic.ttf")
SANS = os.path.join(FONT_DIR, "dejavu/DejaVuSans.ttf")
SANS_B = os.path.join(FONT_DIR, "dejavu/DejaVuSans-Bold.ttf")
SANS_L = os.path.join(FONT_DIR, "liberation/LiberationSans-Regular.ttf")
SANS_LB = os.path.join(FONT_DIR, "liberation/LiberationSans-Bold.ttf")

W, H = 1024, 1024
MARGIN = 28
CW = W - 2 * MARGIN  # 968


def font(path, size):
    return ImageFont.truetype(path, size)


def wrap(d, text, f, max_w):
    """Greedy word wrap; returns a list of lines that fit max_w."""
    lines, cur = [], ""
    for word in text.split():
        trial = word if not cur else cur + " " + word
        if d.textlength(trial, font=f) <= max_w or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_lines(d, x, y, lines, f, fill, leading):
    for i, line in enumerate(lines):
        d.text((x, y + i * leading), line, font=f, fill=fill)
    return y + len(lines) * leading


def truncate(d, text, f, max_w, ellipsis="\u2026"):
    if d.textlength(text, font=f) <= max_w:
        return text
    while text and d.textlength(text + ellipsis, font=f) > max_w:
        text = text[:-1]
    return text + ellipsis


def badge(d, cx, cy, r, n, bg, fg=WHITE, size=13):
    """Numbered circle badge centred at (cx, cy)."""
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=bg)
    f = font(SANS_B, size)
    tw = d.textlength(str(n), font=f)
    bb = f.getbbox(str(n))
    th = bb[3] - bb[1]
    d.text((cx - tw / 2, cy - th / 2 - 1), str(n), font=f, fill=fg)


def fit_size(d, text, path, start, max_w):
    """Largest font size <= start whose text fits max_w."""
    size = start
    while size > 8:
        f = font(path, size)
        if d.textlength(text, font=f) <= max_w:
            return f, size
        size -= 1
    return font(path, 8), 8


# ------------------------------------------------------------ masthead
def draw_masthead(d):
    """Top header, giant title, strapline. Returns y below the strapline."""
    f_top = font(SANS_B, 11)
    d.text((MARGIN, 8), "THE WORLD IN ONE DAY", font=f_top, fill=RED)
    right = "FRIDAY'S NEWS \u00b7 ONE PAGE \u00b7 43 STORIES"
    d.text((W - MARGIN - d.textlength(right, font=f_top), 8), right,
           font=f_top, fill=RED)
    d.line([(MARGIN, 30), (W - MARGIN, 30)], fill=INK, width=2)

    title = "THE WORLD IN ONE DAY"
    f_title, _ = fit_size(d, title, SERIF_B, 60, CW)
    title_y = 40
    d.text((MARGIN, title_y), title, font=f_title, fill=INK)
    # measured ink bottom of the title row
    title_bottom = title_y + f_title.getbbox(title)[3]

    strap = ("A peace declaration in Shenzhen \u00b7 Akvan comes ashore "
             "\u00b7 Trump puts Iran off to 2027")
    f_strap = font(SERIF_I, 20)
    strap_y = title_bottom + 8  # ~16px ink-to-ink clearance
    d.text((MARGIN, strap_y), strap, font=f_strap, fill=RED)
    strap_bottom = strap_y + f_strap.getbbox(strap)[3]
    d.line([(MARGIN, strap_bottom + 4), (W - MARGIN, strap_bottom + 4)],
           fill=RED, width=1)
    return strap_bottom + 6


# ------------------------------------------------------- UTC time strip
UTC_BOXES = [
    ("OVERNIGHT", "Shenzhen declaration out; Trump defers Iran"),
    ("06:30 UTC", "Akvan makes landfall near Gopalpur"),
    ("MORNING", "Japan CPI 2.2%; China holds its rates"),
    ("12:00 ET", "Trump press conference in Washington"),
    ("MIDNIGHT", "COP31 final text due in Antalya"),
]


def draw_utc_strip(d, y):
    """Five equal boxes, two lines of text each, shared baselines."""
    h = 48
    bw = CW / 5.0
    f_lab = font(SANS_B, 11)
    f_txt = font(SANS_L, 12)
    for i, (label, text) in enumerate(UTC_BOXES):
        x0 = MARGIN + i * bw
        x1 = x0 + bw
        d.rectangle([x0, y, x1 - 1, y + h], outline=INK, width=1)
        d.text((x0 + 8, y + 5), label, font=f_lab, fill=RED)
        lines = wrap(d, text, f_txt, bw - 16)
        draw_lines(d, x0 + 8, y + 20, lines[:2], f_txt, INK, 13)
    return y + h


# ---------------------------------------------------------- region bar
REGIONS = [
    ("EUROPE 7", 7, BLUE),
    ("THE AMERICAS 11", 11, GREEN),
    ("ASIA-PACIFIC 15", 15, RED),
    ("MIDEAST 6", 6, GOLD),
]
TAIL_LABEL = "AFRICA 1 \u00b7 OCEANIA 2 \u00b7 WORLD 1"
TAIL_W = 190  # fixed merged tail segment, per the approved layout


def draw_region_bar(d, y):
    h = 20
    f = font(SANS_B, 10)
    big_total = sum(n for _, n, _ in REGIONS)
    big_w = CW - TAIL_W
    x = MARGIN
    for label, n, color in REGIONS:
        w = big_w * n / big_total
        d.rectangle([x, y, x + w, y + h], fill=color)
        tw = d.textlength(label, font=f)
        d.text((x + (w - tw) / 2, y + 4), label, font=f, fill=WHITE)
        x += w
    d.rectangle([x, y, x + TAIL_W, y + h], fill=SLATE)
    tw = d.textlength(TAIL_LABEL, font=f)
    d.text((x + (TAIL_W - tw) / 2, y + 4), TAIL_LABEL, font=f, fill=WHITE)
    return y + h


# ------------------------------------------------------- by the numbers
NUMBERS = [
    ("300,000", "evacuated ahead of Akvan"),
    ("-1,101", "Dow points lost"),
    ("$1.84bn", "GTA VI day-one sales"),
    ("$97.17", "Anthropic's close"),
    ("2.2%", "Japan's core inflation"),
    ("423", "rescue teams in Odisha"),
]


def draw_numbers(d, y):
    """Six equal columns, number and label centred in each."""
    col = CW / 6.0
    f_num = font(SANS_LB, 22)
    f_lab = font(SANS_L, 11)
    for i, (num, label) in enumerate(NUMBERS):
        cx = MARGIN + col * (i + 0.5)
        tw = d.textlength(num, font=f_num)
        d.text((cx - tw / 2, y), num, font=f_num, fill=RED)
        lines = wrap(d, label, f_lab, col - 10)
        ly = y + 26
        for j, line in enumerate(lines[:2]):
            lw = d.textlength(line, font=f_lab)
            d.text((cx - lw / 2, ly + j * 12), line, font=f_lab, fill=INK)
    return y + 48


# ------------------------------------------------- lead illustrations
def illo_shenzhen(d, x, y, w, h):
    """Dusk skyline in Shenzhen: three flags over a dark city, three
    leaders seated at a table in the foreground."""
    d.rectangle([x, y, x + w, y + h], fill=SKY_DUSK)
    # stars
    for sx, sy in [(12, 10), (48, 22), (96, 8), (150, 18), (210, 9),
                   (262, 20), (296, 12), (180, 28)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=(250, 240, 200))
    # skyline blocks
    base = y + h - 30
    blocks = [(0, 46, 34, 62), (36, 30, 30, 78), (68, 52, 40, 56),
              (110, 26, 34, 82), (146, 44, 36, 64), (184, 32, 30, 76),
              (216, 48, 38, 60), (256, 28, 34, 80), (292, 40, 26, 68)]
    for bx, bt, bw, _ in blocks:
        d.rectangle([x + bx, base - bt, x + bx + bw, base], fill=(24, 18, 44))
        for wy in range(base - bt + 6, base - 4, 10):
            for wx in range(bx + 5, bx + bw - 4, 9):
                if (wx * 7 + wy * 3) % 5 < 2:
                    d.rectangle([x + wx, wy, x + wx + 3, wy + 4],
                                fill=(250, 214, 120))
    # three flags on poles above the skyline
    def flag(fx, kind):
        d.line([(x + fx, y + 8), (x + fx, y + 30)], fill=INK, width=2)
        if kind == "latvia":
            d.rectangle([x + fx, y + 8, x + fx + 34, y + 14], fill=(176, 30, 36))
            d.rectangle([x + fx, y + 14, x + fx + 34, y + 18], fill=WHITE)
            d.rectangle([x + fx, y + 18, x + fx + 34, y + 24], fill=(176, 30, 36))
        elif kind == "china":
            d.rectangle([x + fx, y + 8, x + fx + 34, y + 24], fill=(222, 41, 16))
            d.ellipse([x + fx + 4, y + 11, x + fx + 10, y + 17], fill=(255, 222, 0))
        else:  # russia
            d.rectangle([x + fx, y + 8, x + fx + 34, y + 13], fill=WHITE)
            d.rectangle([x + fx, y + 13, x + fx + 34, y + 18], fill=(0, 57, 166))
            d.rectangle([x + fx, y + 18, x + fx + 34, y + 24], fill=(213, 0, 0))
    flag(18, "latvia")
    flag(128, "china")
    flag(238, "russia")
    # ground + table with three seated figures
    d.rectangle([x, base, x + w, y + h], fill=(206, 178, 128))
    d.rectangle([x + 40, y + h - 22, x + w - 40, y + h - 14], fill=(60, 40, 28))
    for fx, suit in [(70, (20, 40, 80)), (155, (40, 40, 40)), (240, (90, 30, 30))]:
        d.ellipse([x + fx - 9, y + h - 34, x + fx + 9, y + h - 16], fill=(232, 190, 150))
        d.pieslice([x + fx - 16, y + h - 20, x + fx + 16, y + h + 4],
                   180, 360, fill=suit)


def illo_cyclone(d, x, y, w, h):
    """White spiral over the Bay of Bengal on a dark navy night."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    cx, cy = x + w // 2, y + h // 2 - 4
    for k in range(5):
        r = 10 + k * 8
        a0 = 20 + k * 38
        d.arc([cx - r, cy - r, cx + r, cy + r], a0, a0 + 235,
              fill=WHITE, width=5)
    d.ellipse([cx - 6, cy - 6, cx + 6, cy + 6], fill=(255, 214, 0))
    # red alert banner across the bottom
    d.rectangle([x, y + h - 18, x + w, y + h], fill=RED)
    f = font(SANS_B, 11)
    d.text((x + 8, y + h - 16), "RED ALERT", font=f, fill=WHITE)


def illo_calendar(d, x, y, w, h):
    """A desk calendar flipped to 2027, 2026 struck through; a JAN 1 card."""
    d.rectangle([x, y, x + w, y + h], fill=CREAM_DK)
    # big calendar card
    cx0, cy0, cw, ch = x + 14, y + 8, 168, h - 16
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + ch], fill=WHITE, outline=INK, width=2)
    d.rectangle([cx0, cy0, cx0 + cw, cy0 + 16], fill=RED)
    for px in (cx0 + 30, cx0 + cw - 30):
        d.rectangle([px - 3, cy0 - 5, px + 3, cy0 + 8], fill=INK)
    f_big = font(SANS_B, 40)
    d.text((cx0 + 18, cy0 + 26), "2027", font=f_big, fill=RED)
    f_old = font(SANS_B, 20)
    d.text((cx0 + 24, cy0 + ch - 26), "2026", font=f_old, fill=GREY)
    d.line([(cx0 + 20, cy0 + ch - 14), (cx0 + 92, cy0 + ch - 14)],
           fill=RED, width=3)
    # small JAN 1 card with red/white stripes
    kx0, ky0, kw, kh = x + w - 104, y + 22, 88, 52
    for i in range(6):
        col = RED if i % 2 == 0 else WHITE
        d.rectangle([kx0 + i * (kw // 6), ky0, kx0 + (i + 1) * (kw // 6), ky0 + kh],
                    fill=col, outline=INK, width=1)
    f_jan = font(SANS_B, 15)
    d.text((kx0 + 14, ky0 + kh + 4), "JAN 1", font=f_jan, fill=INK)


LEADS = [
    ("SHENZHEN \u00b7 DIPLOMACY",
     "Trump, Xi and Putin issue a joint peace declaration",
     "Four points, no Ukraine, no Iran; nuclear war \u2018cannot be won\u2019.",
     illo_shenzhen, RED),
    ("ODISHA \u00b7 STORM",
     "Cyclone Akvan makes landfall at noon",
     "300,000 evacuated; 423 rescue teams out as the storm hits.",
     illo_cyclone, TEAL),
    ("WASHINGTON \u00b7 IRAN",
     "Trump puts the Iran decision off to 2027",
     "\u2018See what happens after Jan 1\u2019; Senate backs him, 51\u201348.",
     illo_calendar, RED),
]


def draw_leads(d, y):
    """Three equal lead columns: illustration, kicker, headline, summary."""
    col_w = (CW - 2 * 16) / 3.0
    illo_h = 96
    f_kick = font(SANS_LB, 12)
    f_head = font(SERIF_B, 21)
    f_sum = font(SANS_L, 12)
    for i, (kicker, head, summ, illo, badge_col) in enumerate(LEADS):
        x = MARGIN + i * (col_w + 16)
        illo(d, x, y, col_w, illo_h)
        badge(d, x + col_w - 14, y + illo_h - 14, 12, i + 1, badge_col)
        ky = y + illo_h + 6
        d.text((x, ky), kicker, font=f_kick, fill=RED)
        lines = wrap(d, head, f_head, col_w)
        draw_lines(d, x, ky + 17, lines[:3], f_head, INK, 23)
        slines = wrap(d, summ, f_sum, col_w)
        draw_lines(d, x, ky + 17 + 2 * 23, slines[:2], f_sum, INK_SOFT, 14)
    return y + illo_h + 6 + 17 + 2 * 23 + 2 * 14


# ---------------------------------------------- medium illustrations
def m_candles(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    f = font(SANS_B, 15)
    d.text((x + 4, y + 2), "\u22121,101", font=f, fill=RED)
    tops = [22, 26, 30, 34, 38]
    for i, top in enumerate(tops):
        cx = x + 30 + i * 30
        d.line([(cx, y + top - 6), (cx, y + top + 16)], fill=RED, width=2)
        d.rectangle([cx - 7, y + top, cx + 7, y + top + 12], fill=RED)
    d.line([(x + 8, y + 16), (x + w - 8, y + 46)], fill=RED_DK, width=2)


def m_mountains(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 238))
    d.ellipse([x + w - 52, y + 6, x + w - 28, y + 30], fill=(255, 214, 0))
    d.polygon([(x, y + h), (x + 60, y + 8), (x + 120, y + h)], fill=(96, 130, 160))
    d.polygon([(x + 70, y + h), (x + 140, y + 2), (x + w, y + h)], fill=(70, 100, 130))
    d.rectangle([x, y + h - 8, x + w, y + h], fill=(120, 150, 110))


def m_gate(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(238, 228, 200))
    d.ellipse([x + w // 2 - 14, y + 2, x + w // 2 + 14, y + 26], fill=(255, 200, 60))
    gx, gy = int(x + w // 2), y + 10
    d.polygon([(gx - 62, gy + 10), (gx + 62, gy + 10), (gx, gy - 2)], fill=(150, 110, 70))
    d.rectangle([gx - 62, gy + 10, gx + 62, gy + 14], fill=(150, 110, 70))
    for cx in range(gx - 56, gx + 57, 18):
        d.rectangle([cx, gy + 14, cx + 8, gy + 38], fill=(150, 110, 70))
    d.rectangle([x, gy + 38, x + w, y + h], fill=(120, 100, 70))


def m_bank(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 232, 238))
    gx = int(x + w // 2)
    d.polygon([(gx - 58, y + 12), (gx + 58, y + 12), (gx, y + 2)], fill=(90, 100, 115))
    d.rectangle([gx - 58, y + 12, gx + 58, y + 18], fill=(90, 100, 115))
    for cx in range(gx - 52, gx + 53, 20):
        d.rectangle([cx, y + 18, cx + 9, y + 42], fill=(120, 130, 145))
    d.rectangle([x + 18, y + 8, x + 92, y + 26], fill=NAVY)
    f = font(SANS_B, 12)
    d.text((x + 24, y + 11), "3.00%", font=f, fill=WHITE)


def m_cpi(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=WHITE)
    f = font(SANS_B, 10)
    d.text((x + 4, y + 2), "2% target", font=f, fill=RED)
    d.line([(x + 4, y + 14), (x + w - 4, y + 14)], fill=RED, width=2)
    vals = [("2.0", 20, TEAL), ("2.1", 26, GREEN), ("2.2", 32, RED)]
    for i, (lab, bh, col) in enumerate(vals):
        bx = x + 24 + i * 52
        d.rectangle([bx, y + h - 6 - bh, bx + 34, y + h - 6], fill=col)
        d.text((bx + 6, y + h - 6 - bh - 12), lab, font=f, fill=INK)


def m_space(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=NAVY_DK)
    for sx, sy in [(10, 8), (40, 20), (80, 6), (120, 16), (160, 10), (60, 34), (140, 30)]:
        d.ellipse([x + sx, y + sy, x + sx + 2, y + sy + 2], fill=WHITE)
    d.ellipse([x + w - 58, y + 12, x + w - 18, y + 52], fill=(150, 148, 140))
    d.ellipse([x + w - 48, y + 20, x + w - 36, y + 32], fill=(120, 118, 112))
    d.rectangle([x + 20, y + 26, x + 52, y + 32], fill=(200, 200, 200))
    d.polygon([(x + 52, y + 24), (x + 66, y + 29), (x + 52, y + 34)], fill=(255, 214, 0))


def m_whitehouse(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(214, 228, 240))
    gx = int(x + w // 2)
    d.rectangle([gx - 52, y + 26, gx + 52, y + h - 6], fill=WHITE)
    d.polygon([(gx - 58, y + 26), (gx + 58, y + 26), (gx, y + 12)], fill=WHITE)
    for cx in range(gx - 44, gx + 45, 16):
        d.rectangle([cx, y + 28, cx + 7, y + h - 6], fill=(200, 205, 210))
    d.line([(gx, y + 2), (gx, y + 12)], fill=INK, width=2)
    d.rectangle([gx + 1, y + 2, gx + 14, y + 9], fill=RED)


def m_gta(d, x, y, w, h):
    for i, col in enumerate([(255, 120, 140), (255, 170, 90), (255, 220, 120)]):
        d.rectangle([x, y + i * h // 3, x + w, y + (i + 1) * h // 3], fill=col)
    d.ellipse([x + 8, y + 4, x + 44, y + 40], fill=(255, 240, 160))
    # palm silhouettes on the right, clear of the sales figure
    d.line([(x + w - 22, y + h - 6), (x + w - 34, y + 16)], fill=(40, 30, 40), width=3)
    d.line([(x + w - 34, y + 16), (x + w - 20, y + 8)], fill=(40, 30, 40), width=2)
    d.line([(x + w - 34, y + 16), (x + w - 46, y + 24)], fill=(40, 30, 40), width=2)
    f = font(SANS_B, 20)
    d.text((x + 8, y + h - 26), "$1.84bn", font=f, fill=INK)


def m_baseball(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(90, 160, 90))
    d.polygon([(x + w // 2, y + h - 8), (x + 14, y + 22), (x + w // 2, y + 6),
               (x + w - 14, y + 22)], fill=(210, 190, 150))
    d.line([(x + w // 2, y + h - 8), (x + 14, y + 22)], fill=WHITE, width=2)
    d.line([(x + w // 2, y + h - 8), (x + w - 14, y + 22)], fill=WHITE, width=2)
    f = font(SANS_B, 15)
    d.text((x + w // 2 - 24, y + 16), "4,256", font=f, fill=INK)
    d.ellipse([x + w - 30, y + 6, x + w - 18, y + 18], fill=WHITE)


def m_vaccine(d, x, y, w, h):
    d.rectangle([x, y, x + w, y + h], fill=(226, 240, 226))
    d.rectangle([x + 12, y + 14, x + 52, y + 26], fill=GREEN)
    d.rectangle([x + 26, y + 2, x + 38, y + 38], fill=GREEN)
    d.rectangle([x + w - 52, y + 10, x + w - 30, y + 44], fill=WHITE, outline=INK, width=1)
    d.rectangle([x + w - 50, y + 4, x + w - 32, y + 10], fill=TEAL)
    d.rectangle([x + w - 50, y + 26, x + w - 32, y + 36], fill=(120, 200, 220))


MEDIUMS = [
    ("NEW YORK \u00b7 MARKETS", "Wall Street slides as the AI rally breaks",
     "Dow \u22121,101; S&P \u22122.02%, a sixth straight loss.", m_candles, RED),
    ("ANTALYA \u00b7 CLIMATE", "COP31\u2019s closing day: fossil fuels cut",
     "Slimmed draft drops \u2018fossil\u2019 and the $120bn figure.", m_mountains, GREEN),
    ("BERLIN \u00b7 DIPLOMACY", "Europe ready for Ukraine talks with Russia",
     "Merz: Moscow\u2019s demands \u2018not realistic\u2019.", m_gate, TEAL),
    ("BEIJING \u00b7 ECONOMY", "China holds loan rates for an 18th month",
     "LPR stays at 3.00% and 3.50% at Friday\u2019s review.", m_bank, RED),
    ("TOKYO \u00b7 ECONOMY", "Japan\u2019s core inflation hits 2.2%",
     "Above the BOJ\u2019s 2% target; a Dec hike looms.", m_cpi, RED),
    ("TOKYO \u00b7 SPACE", "Hayabusa2 gives up its asteroid landing",
     "Engine trouble forces a new plan for the probe.", m_space, TEAL),
    ("WASHINGTON \u00b7 POLITICS", "Trump faces the press at noon",
     "First news conference since the Shenzhen summit.", m_whitehouse, RED),
    ("VICE CITY \u00b7 GAMES", "GTA VI passes The Odyssey: $1.84bn",
     "19.05m copies in a day; no official figures yet.", m_gta, GREEN),
    ("BASEBALL \u00b7 SPORT", "Trump pardons Pete Rose",
     "Posthumous pardon for the 4,256-hit legend.", m_baseball, RED),
    ("BHOPAL \u00b7 SCIENCE", "India\u2019s first home-made H5N1 vaccine",
     "A chicken vaccine, dedicated to the nation.", m_vaccine, GREEN),
]


def draw_brief_header(d, y):
    f_h = font(SANS_B, 13)
    d.text((MARGIN, y), "THE DAY IN BRIEF", font=f_h, fill=RED)
    f_r = font(SANS_B, 11)
    right = "STORIES 04\u201313"
    d.text((W - MARGIN - d.textlength(right, font=f_r), y + 2), right,
           font=f_r, fill=INK_SOFT)
    d.line([(MARGIN, y + 19), (W - MARGIN, y + 19)], fill=INK, width=1)
    return y + 25


def draw_mediums(d, y):
    """5 x 2 grid of brief cards."""
    card_w = 189
    gap = (CW - 5 * card_w) / 4.0
    illo_h = 50
    card_h = 120
    row_gap = 4
    f_kick = font(SANS_LB, 10)
    f_head = font(SANS_LB, 13)
    f_sum = font(SANS_L, 11)
    for idx, (kicker, head, summ, illo, badge_col) in enumerate(MEDIUMS):
        row, col = divmod(idx, 5)
        x = MARGIN + col * (card_w + gap)
        cy = y + row * (card_h + row_gap)
        d.rectangle([x, cy, x + card_w, cy + card_h], fill=CREAM,
                    outline=(200, 190, 165), width=1)
        illo(d, x + 1, cy + 1, card_w - 2, illo_h)
        d.text((x + 5, cy + illo_h + 4), kicker, font=f_kick, fill=RED)
        hlines = wrap(d, head, f_head, card_w - 34)
        draw_lines(d, x + 5, cy + illo_h + 17, hlines[:2], f_head, INK, 14)
        slines = wrap(d, summ, f_sum, card_w - 34)
        draw_lines(d, x + 5, cy + illo_h + 17 + 2 * 14, slines[:2],
                   f_sum, INK_SOFT, 12)
        badge(d, x + card_w - 13, cy + card_h - 13, 11, idx + 4, badge_col,
              size=11)
    return y + 2 * card_h + row_gap


# ------------------------------------------------------- map + ALSO
ALSO = [
    (14, "WASHINGTON", "Senate rejects Iran war-powers curb 51\u201348"),
    (15, "GAZA", "Two killed in Gaza strikes"),
    (16, "BEIRUT", "Israel strikes a Hezbollah site in the east"),
    (17, "CARACAS", "US and Venezuela sign a military-cooperation deal"),
    (18, "BRUSSELS", "EU\u2013UK summit opens"),
    (19, "NEW DELHI", "Modi meets William and Kate"),
    (20, "DHAKA", "Fire at Yunus home; arson feared"),
    (21, "SEOUL", "Samsung falls 4.2% as AI money leaves chips"),
    (22, "HONG KONG", "Hang Seng 1.6% lower"),
    (23, "SYDNEY", "ASX 200 opens 0.8% lower"),
    (24, "WELLINGTON", "NZ resume on 243\u20135; Nicholls 113*"),
    (25, "KYIV", "Kyiv says it hit two Russian oil refineries"),
    (26, "DAMASCUS", "Syria hails a \u2018historic\u2019 UN vote"),
    (27, "TEHRAN", "Iran war cost tops $48bn, AP tally"),
    (28, "LONDON", "King\u2019s message to Palestinians"),
    (29, "MOGADISHU", "Somalia expels the UAE envoy"),
    (30, "BOGOT\u00c1", "Colombia marches again"),
    (31, "QUITO", "Hegseth visits Ecuador on the anti-narco fight"),
    (32, "GEORGETOWN", "Trump aide \u2018floated ceding Guyanese land\u2019"),
    (33, "SANA\u2019A", "Houthi ministry: 10 died in the capital in two days"),
    (34, "KUALA LUMPUR", "ASEAN summit closes with new pacts"),
    (35, "MANILA", "Philippines\u2013Chile trade deal"),
    (36, "MANILA", "Musk plans Philippines projects"),
    (37, "HONG KONG", "India beats Malaysia in badminton"),
    (38, "IPOH", "Harimau Shakti exercise opens"),
    (39, "NEW YORK", "US jobless claims 203,000"),
    (40, "MUNICH", "Bayern beat K\u00f6ln 3\u20130"),
    (41, "DOHA", "Argentina 0\u20132 Australia, U17 Cup"),
    (42, "GENEVA", "Race to succeed Guterres deadlocked"),
    (43, "WORLD", "World Children\u2019s Day marked"),
]

# (lon, lat) of the 13 featured stories, for the map pins
PINS = [
    (1, 114.0, 22.5), (2, 85.0, 19.3), (3, -77.0, 38.9), (4, -74.0, 40.7),
    (5, 30.7, 36.9), (6, 13.4, 52.5), (7, 116.4, 39.9), (8, 139.7, 35.7),
    (9, 139.7, 35.7), (10, -77.0, 38.9), (11, -80.2, 25.8),
    (12, -84.5, 39.1), (13, 77.4, 23.3),
]
PIN_DX = {1: 22, 2: 16, 4: -28, 5: -16, 6: -20, 7: -22, 8: 18, 9: 32,
          10: 26, 11: -6, 12: -30, 13: -18}
PIN_DY = {1: 16, 2: 16, 4: 14, 5: -10, 6: -8, 7: -12, 8: -16, 9: 10,
          10: -18, 11: 22, 12: -14, 13: 14}


def draw_map(d, x, y, w, h):
    """Stylised world map: beige land blobs on navy, red numbered pins."""
    d.rectangle([x, y, x + w, y + h], fill=NAVY)
    # land as clusters of overlapping ellipses (rough continents)
    blobs = [
        # North America
        (0.02, 0.10, 0.30, 0.28), (0.10, 0.05, 0.22, 0.20),
        (0.16, 0.30, 0.10, 0.22),
        # South America
        (0.20, 0.52, 0.12, 0.30), (0.23, 0.44, 0.09, 0.16),
        # Europe
        (0.44, 0.08, 0.10, 0.14), (0.47, 0.16, 0.07, 0.10),
        # Africa
        (0.45, 0.30, 0.13, 0.32), (0.47, 0.24, 0.09, 0.14),
        # Asia
        (0.55, 0.06, 0.34, 0.26), (0.62, 0.28, 0.16, 0.20),
        (0.78, 0.30, 0.10, 0.14),
        # Australia
        (0.80, 0.66, 0.12, 0.14),
    ]
    for fx, fy, fw, fh in blobs:
        d.ellipse([x + fx * w, y + fy * h, x + (fx + fw) * w,
                   y + (fy + fh) * h], fill=SAND)
    for n, lon, lat in PINS:
        px = x + (lon + 180.0) / 360.0 * w + PIN_DX.get(n, 0)
        py = y + (90.0 - lat) / 180.0 * h + PIN_DY.get(n, 0)
        badge(d, px, py, 8, n, RED, size=9)


def draw_bottom(d, y):
    """Map header, map + ALSO list, caption, DATE CHECK, footer."""
    f_h = font(SANS_B, 13)
    d.text((MARGIN, y), "WHERE IT HAPPENED", font=f_h, fill=RED)
    map_x, map_y = MARGIN, y + 20
    map_w, map_h = 330, 140
    draw_map(d, map_x, map_y, map_w, map_h)

    ax = MARGIN + map_w + 16
    aw = W - MARGIN - ax
    f_ah = font(SANS_B, 12)
    d.text((ax, y), "ALSO ON FRIDAY 20 NOVEMBER \u2014 30 MORE STORIES",
           font=f_ah, fill=RED)
    f_n = font(SANS_LB, 11)
    f_t = font(SANS_L, 11)
    col_w = aw / 3.0
    for i, (n, city, text) in enumerate(ALSO):
        col, row = divmod(i, 10)
        ix = ax + col * col_w
        iy = map_y + row * 14
        d.text((ix, iy), str(n), font=f_n, fill=RED)
        rest = truncate(d, city + " \u2014 " + text, f_t, col_w - 24)
        d.text((ix + 22, iy), rest, font=f_t, fill=INK)

    cap_y = map_y + map_h + 5
    d.text((MARGIN, cap_y),
           "Red pins mark stories 1\u201313; grey dots mark the briefs.",
           font=font(SANS_L, 10), fill=INK_SOFT)

    box_y = cap_y + 18
    box_h = 50
    d.rectangle([MARGIN, box_y, W - MARGIN, box_y + box_h],
                outline=INK, width=1)
    check = ("DATE CHECK \u2014 LEFT OFF BECAUSE THEY BROKE BEFORE FRIDAY: "
             "The ICJ\u2019s genocide verdict on Myanmar (Thu) \u00b7 "
             "Anthropic\u2019s $81.3bn IPO debut (Thu) \u00b7 GTA VI\u2019s midnight "
             "launch (Thu) \u00b7 the Crimean Bridge\u2019s third strike (Thu) \u00b7 "
             "the Houthi strike on Riyadh\u2019s PIF Tower (Thu) \u00b7 "
             "Han Duck-soo\u2019s sentence overturned (Thu) \u00b7 Fiji\u2019s disaster "
             "declaration (Wed) \u00b7 APEC\u2019s Shenzhen Outlook (Thu).")
    f_c = font(SANS_L, 11)
    lines = wrap(d, check, f_c, CW - 16)
    draw_lines(d, MARGIN + 8, box_y + 6, lines[:3], f_c, INK, 12)

    foot = ("Every story here happened, or was first reported, on Friday "
            "20 November 2026 \u2014 overnight reports count where they first "
            "landed on Friday in Asia. Disputed claims are attributed, not "
            "stated as fact. Sources: Reuters, AP, BBC, Al Jazeera, Sensor "
            "Tower, IMD, Nasdaq, Bank of Japan, PBOC. Original drawings. "
            "The World in One Day \u2014 20 November 2026.")
    f_f = font(SANS_L, 9)
    flines = wrap(d, foot, f_f, CW)
    draw_lines(d, MARGIN, box_y + box_h + 7, flines[:3], f_f, INK_SOFT, 11)
    return box_y + box_h + 7 + len(flines[:3]) * 11


# ------------------------------------------------------------------ main
def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="/output/entry.png")
    ap.add_argument("--size", type=int, default=1024)
    args = ap.parse_args()

    img = Image.new("RGB", (args.size, args.size), CREAM)
    d = ImageDraw.Draw(img)

    y = draw_masthead(d)
    y = draw_utc_strip(d, y + 2)
    y = draw_region_bar(d, y + 2)
    y = draw_numbers(d, y + 4)
    y = draw_leads(d, y + 4)
    y = draw_brief_header(d, y + 2)
    y = draw_mediums(d, y)
    draw_bottom(d, y + 6)

    out_dir = os.path.dirname(os.path.abspath(args.out))
    os.makedirs(out_dir, exist_ok=True)
    img.save(args.out, format="PNG")
    print("wrote", args.out)


if __name__ == "__main__":
    main()
