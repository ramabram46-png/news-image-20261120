#!/usr/bin/env python3
"""Draw the news-image-20261120 poster — "The World in One Day".

Newspaper front page for Friday 20 November 2026. 43 stories, every one
verified against real sources (see research-20-nov-2026.md).

Built on the news-19 v2 program (same proven layout: THE DAY IN UTC strip,
dark-navy map, 3 equal leads, 10 mediums 5-across). The live leaderboard
for 20 Nov (424 entries, ~08:10 WIB) sets the consensus: Akvan landfall,
the Shenzhen declaration, Trump deferring Iran to 2027, the Wall Street
AI selloff, COP31's closing day. Freshness rule: a story counts as
Friday's when first reported 20 Nov in any timezone — the overnight
Asian reports (declaration, Dow close, Berlin talks, GTA tally, Rose
pardon) are Friday's news; Thursday's ICJ verdict, Kerch strike, PIF
Tower hit, Han ruling, Fiji declaration and APEC Outlook go in DATE CHECK.

Flat vector only — no photos, no AI images. Deterministic: same input
gives the same bytes. 1024x1024 PNG, well under 1 MiB.
Usage: python3 draw_poster.py [output.png]
"""

import math
import sys

from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024
M = 28                        # outer margin
CW = W - 2 * M                # content width

PAPER = (247, 243, 232)
INK = (26, 26, 26)
RED = (166, 30, 34)
NAVY = (31, 58, 95)
DARKMAP = (16, 42, 80)
LAND = (222, 200, 150)
GOLD = (201, 162, 39)
TEAL = (42, 127, 111)
GREEN = (46, 125, 50)
OCHRE = (180, 120, 30)
GREY = (107, 101, 88)
HAIR = (26, 26, 26)
NIGHT = (10, 30, 60)

NOTO = "/usr/share/fonts/truetype/noto/"
F_DISP_BLACK = NOTO + "NotoSerifDisplay-Black.ttf"
F_DISP_BOLD = NOTO + "NotoSerifDisplay-Bold.ttf"
F_SERIF_IT = NOTO + "NotoSerif-Italic.ttf"
F_SANS = NOTO + "NotoSans-Regular.ttf"
F_SANS_B = NOTO + "NotoSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


def fit_font(path, text, max_w, start):
    """Largest size (<= start) whose text fits max_w."""
    size = start
    f = ImageFont.truetype(path, size)
    while f.getlength(text) > max_w and size > 10:
        size -= 2
        f = ImageFont.truetype(path, size)
    return f


def wrap(d, text, fnt, max_w):
    """Greedy word wrap; returns a list of lines."""
    lines, cur = [], ""
    for word in text.split():
        trial = f"{cur} {word}".strip()
        if d.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = word
    if cur:
        lines.append(cur)
    return lines


def draw_wrapped(d, x, y, text, fnt, fill, max_w, leading, max_lines=None):
    lines = wrap(d, text, fnt, max_w)
    if max_lines is not None:
        lines = lines[:max_lines]
    for line in lines:
        d.text((x, y), line, font=fnt, fill=fill)
        y += leading
    return y


# ---------------------------------------------------------------------------
# content (verified facts — see research-19-nov-2026.md; do not change)
# ---------------------------------------------------------------------------

REGIONS = [
    ("EUROPE", 7, (31, 78, 121)),
    ("THE AMERICAS", 11, (46, 125, 50)),
    ("ASIA-PACIFIC", 15, (166, 30, 34)),
    ("MIDEAST", 6, (180, 120, 30)),
    ("AFRICA", 1, (74, 103, 65)),
    ("OCEANIA", 2, (42, 127, 111)),
    ("WORLD", 1, (90, 90, 110)),
]

NUMBERS = [
    ("300,000", "evacuated ahead of Akvan"),
    ("-1,101", "Dow points lost"),
    ("$1.84bn", "GTA VI day-one sales"),
    ("$97.17", "Anthropic's close"),
    ("2.2%", "Japan's core inflation"),
    ("423", "rescue teams in Odisha"),
]

UTC = [
    ("OVERNIGHT", "Shenzhen declaration out; Trump defers Iran"),
    ("06:30 UTC", "Akvan makes landfall near Gopalpur"),
    ("MORNING", "Japan CPI 2.2%; China holds its rates"),
    ("12:00 ET", "Trump press conference in Washington"),
    ("MIDNIGHT", "COP31 final text due in Antalya"),
]

LEADS = [
    ("SHENZHEN · DIPLOMACY", RED, "summit",
     "Trump, Xi and Putin issue a joint peace declaration",
     "Four points, no Ukraine, no Iran; nuclear war 'cannot be won'."),
    ("ODISHA · STORM", TEAL, "akvan",
     "Cyclone Akvan makes landfall at noon",
     "300,000 evacuated; 423 rescue teams out as the storm hits."),
    ("WASHINGTON · IRAN", RED, "iran2027",
     "Trump puts the Iran decision off to 2027",
     "'See what happens after Jan 1'; Senate backs him, 51-48."),
]

MEDIUMS = [
    ("NEW YORK · MARKETS", RED, "market",
     "Wall Street slides as the AI rally breaks",
     "Dow -1,101; S&P -2.02%, a sixth straight loss."),
    ("ANTALYA · CLIMATE", OCHRE, "cop31",
     "COP31's closing day: fossil fuels cut",
     "Slimmed draft drops 'fossil' and the $120bn figure."),
    ("BERLIN · DIPLOMACY", NAVY, "berlin",
     "Europe ready for Ukraine talks with Russia",
     "Merz: Moscow's demands 'not realistic'."),
    ("BEIJING · ECONOMY", RED, "rates",
     "China holds loan rates for an 18th month",
     "LPR stays at 3.00% and 3.50% at Friday's review."),
    ("TOKYO · ECONOMY", TEAL, "cpi",
     "Japan's core inflation hits 2.2%",
     "Above the BOJ's 2% target; a Dec hike looms."),
    ("TOKYO · SPACE", NAVY, "hayabusa",
     "Hayabusa2 gives up its asteroid landing",
     "Engine trouble forces a new plan for the probe."),
    ("WASHINGTON · POLITICS", NAVY, "presser",
     "Trump faces the press at noon",
     "First news conference since the Shenzhen summit."),
    ("VICE CITY · GAMES", GREEN, "gta",
     "GTA VI passes The Odyssey: $1.84bn",
     "19.05m copies in a day; no official figures yet."),
    ("BASEBALL · SPORT", NAVY, "baseball",
     "Trump pardons Pete Rose",
     "Posthumous pardon for the 4,256-hit legend."),
    ("BHOPAL · SCIENCE", TEAL, "vaccine",
     "India's first home-made H5N1 vaccine",
     "A chicken vaccine, dedicated to the nation today."),
]

# ALSO items are kept short on purpose: one line each at 9px in a
# three-column band. City in caps, then the news in a few words.
ALSO = [
    "WASHINGTON — Senate rejects war-powers curb",
    "GAZA — Two killed in Gaza strikes [L]",
    "BEIRUT — Israel strikes Hezbollah site [L]",
    "CARACAS — US–Venezuela sign military deal [L]",
    "BRUSSELS — EU–UK summit opens [L]",
    "NEW DELHI — Modi meets William and Kate [L]",
    "DHAKA — Fire at Yunus home; arson feared [L]",
    "SEOUL — Samsung falls 4.2% on AI exit [L]",
    "HONG KONG — Hang Seng 1.6% lower [L]",
    "SYDNEY — ASX 200 opens 0.8% lower [L]",
    "WELLINGTON — NZ resume on 243–5 [L]",
    "KYIV — Kyiv says it hit two oil refineries [L]",
    "DAMASCUS — Syria hails 'historic' UN vote [L]",
    "TEHRAN — Iran war cost tops $48bn [L]",
    "LONDON — King's message to Palestinians [L]",
    "MOGADISHU — Somalia expels UAE envoy [L]",
    "BOGOTÁ — Colombia marches again [L]",
    "QUITO — Hegseth visits Ecuador [L]",
    "GEORGETOWN — 'Ceding Guyanese land' floated [L]",
    "SANA'A — 10 died in the capital in 2 days [L]",
    "KUALA LUMPUR — ASEAN summit closes [L]",
    "MANILA — Philippines–Chile trade deal [L]",
    "MANILA — Musk plans Philippines projects [L]",
    "HONG KONG — India beats Malaysia [L]",
    "IPOH — Harimau Shakti exercise opens [L]",
    "NEW YORK — US jobless claims 203,000 [L]",
    "MUNICH — Bayern beat Köln 3–0 [L]",
    "DOHA — Argentina 0–2 Australia, U17 [L]",
    "GENEVA — Race to succeed Guterres stuck [L]",
    "WORLD — World Children's Day marked [L]",
]

DATE_CHECK = ("DATE CHECK — LEFT OFF BECAUSE THEY BROKE BEFORE FRIDAY: "
              "the ICJ's genocide verdict on Myanmar (Thu) · Anthropic's $81.3bn "
              "IPO debut (Thu) · GTA VI's midnight launch (Thu) · the Crimean "
              "Bridge's third strike (Thu) · the Houthi strike on Riyadh's PIF "
              "Tower (Thu) · Han Duck-soo's sentence overturned (Thu) · Fiji's "
              "disaster declaration (Wed) · APEC's Shenzhen Outlook (Thu).")

FOOTER = ("Every story here happened, or was first reported, on Friday "
          "20 November 2026 — overnight reports count where they first landed "
          "on Friday in Asia. Disputed claims are attributed, not stated as "
          "fact. Sources: Reuters, AP, BBC, Al Jazeera, Sensor Tower, IMD, "
          "Nasdaq, Bank of Japan, PBOC. Original drawings. The World in One "
          "Day — 20 November 2026.")

# ---------------------------------------------------------------------------
# flat illustration scenes (each paints one rectangle x,y,w,h)
# ---------------------------------------------------------------------------

def scene_summit(d, x, y, w, h):
    """Shenzhen at dusk: three flags in front of a dark skyline, low sun,
    the three leaders at the table. The panel reads as a scene now — v1's
    beige panel with a small table was half empty."""
    # dusk sky in three bands
    d.rectangle([x, y, x + w, y + h * 0.30], fill=(70, 40, 80))
    d.rectangle([x, y + h * 0.30, x + w, y + h * 0.52], fill=(170, 80, 70))
    d.rectangle([x, y + h * 0.52, x + w, y + h], fill=(232, 222, 196))
    # low sun, right of frame
    sx, sy, sr = x + w * 0.82, y + h * 0.34, 13
    d.ellipse([sx - sr, sy - sr, sx + sr, sy + sr], fill=(255, 190, 90))
    # dark skyline across the full width, windows lit
    for bx, bw, bh in [(0.02, 0.10, 0.20), (0.14, 0.08, 0.14),
                       (0.24, 0.12, 0.24), (0.38, 0.09, 0.16),
                       (0.49, 0.11, 0.22), (0.62, 0.10, 0.15),
                       (0.74, 0.09, 0.20), (0.85, 0.11, 0.26)]:
        d.rectangle([x + w * bx, y + h * 0.52 - h * bh,
                     x + w * (bx + bw), y + h * 0.52], fill=(45, 30, 55))
        for wx in (0.02, 0.05):
            d.rectangle([x + w * (bx + wx), y + h * (0.52 - bh + 0.04),
                         x + w * (bx + wx) + 3,
                         y + h * (0.52 - bh + 0.07)],
                        fill=(255, 200, 110))
    # three flags, US / China / Russia — three stripes each, drawn so
    # they read at 50px tall (v1's two-tone flags read as the wrong
    # countries: the US flag looked Polish, the Russian flag looked
    # Finnish)
    x0, fw = x + w * 0.10, w * 0.16
    x1 = x0 + fw + w * 0.13
    x2 = x1 + fw + w * 0.13
    flags = [
        [RED, (255, 255, 255), RED],                 # US: red-white-red
        [RED, RED, RED],                             # China: red, gold star
        [(255, 255, 255), (0, 57, 166), RED],        # Russia: white-blue-red
    ]
    for fx, stripes in zip((x0, x1, x2), flags):
        d.line([fx + fw / 2, y + h * 0.08, fx + fw / 2, y + h * 0.48],
               fill=(60, 60, 60), width=2)
        for i, col in enumerate(stripes):
            d.rectangle([fx, y + h * (0.08 + i * 0.08),
                         fx + fw, y + h * (0.16 + i * 0.08)], fill=col)
    # gold star on the China flag
    d.ellipse([x1 + 4, y + h * 0.095, x1 + 12, y + h * 0.155],
              fill=(255, 215, 0))
    # the table and the three leaders
    d.rectangle([x + w * 0.07, y + h * 0.66, x + w * 0.93, y + h * 0.84],
                fill=(120, 72, 48))
    for cx, suit, hair in [(0.24, NAVY, (200, 200, 200)),
                           (0.50, (31, 31, 31), (30, 30, 30)),
                           (0.76, NAVY, (200, 200, 200))]:
        px = x + w * cx
        d.ellipse([px - 11, y + h * 0.46, px + 11, y + h * 0.58],
                  fill=(242, 200, 160))
        d.pieslice([px - 11, y + h * 0.46, px + 11, y + h * 0.54], 180, 360,
                   fill=hair)
        d.polygon([(px - 18, y + h * 0.72), (px + 18, y + h * 0.72),
                   (px + 13, y + h * 0.56), (px - 13, y + h * 0.56)],
                  fill=suit)


def scene_gta(d, x, y, w, h):
    """A neon sunset city strip, a palm, the Vice City heroine's car with
    its headlights on. The title text sits on the teal band below."""
    d.rectangle([x, y, x + w, y + h], fill=(245, 220, 220))
    for yy, col in [(0.0, (255, 107, 149)), (0.25, (255, 179, 120)),
                    (0.5, (255, 214, 0)), (0.75, (58, 199, 199))]:
        d.rectangle([x, y + h * yy, x + w, y + h * (yy + 0.25)], fill=col)
    for bx, bw, bh in [(0.04, 0.13, 0.28), (0.20, 0.10, 0.20),
                       (0.34, 0.14, 0.32), (0.66, 0.12, 0.24),
                       (0.82, 0.10, 0.18)]:
        d.rectangle([x + w * bx, y + h * 0.72 - h * bh,
                     x + w * (bx + bw), y + h * 0.72], fill=(30, 30, 55))
    for wx in (0.01, 0.05):
        for bx, bw, bh in [(0.04, 0.13, 0.28), (0.34, 0.14, 0.32)]:
            d.rectangle([x + w * (bx + wx), y + h * (0.72 - bh + 0.05),
                         x + w * (bx + wx) + 3,
                         y + h * (0.72 - bh + 0.08)],
                        fill=(255, 230, 120))
    d.line([x + w * 0.88, y + h * 0.30, x + w * 0.94, y + h * 0.72],
           fill=(20, 60, 20), width=4)
    for ang in (-50, -20, 10, 40):
        rad = math.radians(ang)
        d.line([x + w * 0.88, y + h * 0.30,
                x + w * 0.88 + 26 * math.cos(rad),
                y + h * 0.30 + 26 * math.sin(rad)],
               fill=(20, 60, 20), width=3)
    d.rectangle([x + w * 0.04, y + h * 0.72, x + w * 0.96, y + h * 0.78],
                fill=(30, 30, 40))
    for i in range(5):
        d.line([x + w * (0.04 + i * 0.19), y + h * 0.78,
                x + w * (0.04 + i * 0.19), y + h * 1.0],
               fill=(255, 200, 90), width=2)
    d.rounded_rectangle([x + w * 0.25, y + h * 0.78, x + w * 0.70, y + h * 0.95],
                        radius=8, fill=(166, 30, 34))
    d.polygon([(x + w * 0.31, y + h * 0.78), (x + w * 0.38, y + h * 0.70),
               (x + w * 0.52, y + h * 0.70), (x + w * 0.58, y + h * 0.78)],
              fill=(180, 220, 230))
    for cx in (0.33, 0.62):
        d.ellipse([x + w * cx - 7, y + h * 0.90, x + w * cx + 7, y + h * 0.98],
                  fill=(20, 20, 20))
    d.ellipse([x + w * 0.68, y + h * 0.84, x + w * 0.70, y + h * 0.88],
              fill=(255, 255, 180))
    d.text((x + w * 0.06, y + h * 0.02), "$1.84bn",
           font=font(F_SANS_B, 20), fill=(255, 255, 255),
           stroke_width=2, stroke_fill=(166, 30, 34))


def scene_ipo(d, x, y, w, h):
    """Anthropic's first day: the Nasdaq board, a rising row of green
    candles, the IPO price in big type."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 42, 80))
    d.text((x + 8, y + 6), "ANT  $83", font=font(F_SANS_B, 19),
           fill=(255, 255, 255))
    # rising arrow, drawn as a polygon — the ▲ glyph is missing from
    # Noto Sans Bold and rendered as an empty box in v2's first pass
    tx = x + w * 0.74
    d.polygon([(tx, y + 20), (tx + 12, y + 20), (tx + 6, y + 8)],
              fill=(120, 220, 140))
    for i, top in enumerate([0.66, 0.58, 0.62, 0.50, 0.44, 0.36]):
        bx = x + w * (0.08 + i * 0.15)
        bw = w * 0.09
        d.line([bx + bw / 2, y + h * (top - 0.06),
                bx + bw / 2, y + h * 0.78], fill=(120, 220, 140), width=2)
        d.rectangle([bx, y + h * top, bx + bw, y + h * 0.78],
                    fill=(46, 180, 90))
    d.line([x + w * 0.06, y + h * 0.82, x + w * 0.94, y + h * 0.82],
           fill=(255, 255, 255), width=2)


def scene_bridge(d, x, y, w, h):
    """The Crimean Bridge at night: the road deck broken, a red plume
    rising, the railway span intact below. Kept from v1 — it worked."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 30, 50))
    for i in range(7):
        d.ellipse([x + w * (0.08 + i * 0.13), y + h * 0.05,
                   x + w * (0.08 + i * 0.13) + 2, y + h * 0.05 + 2],
                  fill=(255, 255, 255))
    d.rectangle([x, y + h * 0.80, x + w, y + h], fill=(30, 45, 70))
    for bx in (0.12, 0.40, 0.68):
        d.rectangle([x + w * bx, y + h * 0.40, x + w * (bx + 0.05), y + h * 0.80],
                    fill=(70, 90, 120))
    d.rectangle([x, y + h * 0.62, x + w * 0.45, y + h * 0.66], fill=(180, 190, 200))
    d.rectangle([x + w * 0.62, y + h * 0.62, x + w, y + h * 0.66],
                fill=(180, 190, 200))
    d.polygon([(x + w * 0.45, y + h * 0.62), (x + w * 0.55, y + h * 0.66),
               (x + w * 0.55, y + h * 0.62), (x + w * 0.62, y + h * 0.66)],
              fill=(120, 130, 145))
    d.polygon([(x + w * 0.50, y + h * 0.06), (x + w * 0.58, y + h * 0.24),
               (x + w * 0.66, y + h * 0.30), (x + w * 0.60, y + h * 0.42),
               (x + w * 0.52, y + h * 0.46), (x + w * 0.46, y + h * 0.32),
               (x + w * 0.42, y + h * 0.22)],
              fill=(220, 60, 40))
    d.ellipse([x + w * 0.42, y + h * 0.30, x + w * 0.58, y + h * 0.50],
              fill=(255, 150, 60))
    d.rectangle([x, y + h * 0.72, x + w, y + h * 0.75], fill=(120, 130, 145))


def scene_icj(d, x, y, w, h):
    """The Peace Palace at The Hague: clock tower, gables, flag — and the
    flag is the Rohingya green, the claimants' colour."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    d.ellipse([x + w * 0.76, y + h * 0.08, x + w * 0.76 + 20,
               y + h * 0.08 + 20], fill=(255, 210, 120))
    d.rectangle([x + w * 0.42, y + h * 0.10, x + w * 0.58, y + h * 0.78],
                fill=(150, 100, 60))
    d.polygon([(x + w * 0.40, y + h * 0.10), (x + w * 0.60, y + h * 0.10),
               (x + w * 0.50, y + h * 0.02)], fill=(110, 70, 40))
    d.ellipse([x + w * 0.46, y + h * 0.16, x + w * 0.54, y + h * 0.24],
              fill=(255, 255, 255))
    d.line([x + w * 0.50, y + h * 0.20, x + w * 0.50, y + h * 0.17],
           fill=(26, 26, 26), width=2)
    d.line([x + w * 0.50, y + h * 0.20, x + w * 0.53, y + h * 0.20],
           fill=(26, 26, 26), width=2)
    for bx, bw in [(0.06, 0.30), (0.64, 0.30)]:
        d.rectangle([x + w * bx, y + h * 0.38, x + w * (bx + bw), y + h * 0.78],
                    fill=(170, 120, 75))
        d.polygon([(x + w * bx, y + h * 0.38),
                   (x + w * (bx + bw), y + h * 0.38),
                   (x + w * (bx + bw / 2), y + h * 0.28)], fill=(110, 70, 40))
        d.rectangle([x + w * (bx + 0.12), y + h * 0.55,
                     x + w * (bx + 0.18), y + h * 0.78], fill=(60, 45, 30))
    d.rectangle([x, y + h * 0.78, x + w, y + h], fill=(90, 130, 80))
    d.line([x + w * 0.08, y + h * 0.78, x + w * 0.08, y + h * 0.20],
           fill=(60, 60, 60), width=2)
    d.rectangle([x + w * 0.08, y + h * 0.20, x + w * 0.24, y + h * 0.32],
                fill=(0, 120, 60))


def scene_gaza(d, x, y, w, h):
    """A tank silhouette against a dust-orange sky, a grey city behind,
    a small Red Cross tent. Kept from v1 — it worked."""
    d.rectangle([x, y, x + w, y + h], fill=(245, 215, 150))
    d.rectangle([x, y + h * 0.72, x + w, y + h], fill=(200, 170, 110))
    for bx, bw, bh in [(0.08, 0.12, 0.30), (0.24, 0.10, 0.22),
                       (0.38, 0.14, 0.34), (0.80, 0.10, 0.26)]:
        d.rectangle([x + w * bx, y + h * 0.72 - h * bh,
                     x + w * (bx + bw), y + h * 0.72], fill=(150, 130, 110))
    d.ellipse([x + w * 0.80, y + h * 0.10, x + w * 0.80 + 18,
               y + h * 0.10 + 18], fill=(255, 220, 140))
    tx, ty = x + w * 0.32, y + h * 0.42
    d.rectangle([tx, ty, tx + w * 0.42, ty + h * 0.22], fill=(60, 65, 50))
    d.rectangle([tx + w * 0.06, ty - h * 0.16, tx + w * 0.28, ty],
                fill=(60, 65, 50))
    d.line([tx + w * 0.28, ty - h * 0.08, tx + w * 0.55, ty - h * 0.16],
           fill=(40, 45, 35), width=3)
    for cx in (0.36, 0.50, 0.64):
        d.ellipse([x + w * cx - 8, ty + h * 0.20, x + w * cx + 8, ty + h * 0.30],
                  fill=(30, 30, 30))
    d.polygon([(x + w * 0.80, y + h * 0.72), (x + w * 0.87, y + h * 0.55),
               (x + w * 0.94, y + h * 0.72)], fill=(240, 240, 235))
    d.rectangle([x + w * 0.855, y + h * 0.63, x + w * 0.885, y + h * 0.68],
                fill=(200, 30, 30))
    d.rectangle([x + w * 0.868, y + h * 0.615, x + w * 0.873, y + h * 0.695],
                fill=(200, 30, 30))


def scene_akvan(d, x, y, w, h):
    """A cyclone spiral over the Bay of Bengal, rain slanting across a
    red-alert strip. Kept from v1 — it worked."""
    d.rectangle([x, y, x + w, y + h], fill=(20, 50, 80))
    cx, cy = x + w * 0.5, y + h * 0.45
    for i, r in enumerate(range(6, 46, 6)):
        a0 = i * 1.1
        pts = []
        for k in range(20):
            a = a0 + k * 0.22
            rr = r * (0.5 + k * 0.035)
            pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a) * 0.9))
        d.line(pts, fill=(255, 255, 255), width=3)
    d.ellipse([cx - 5, cy - 4, cx + 5, cy + 4], fill=(255, 220, 100))
    for i in range(6):
        rx = x + w * (0.05 + i * 0.17)
        d.line([rx, y + h * 0.78, rx + 6, y + h * 0.95],
               fill=(180, 200, 230), width=2)
    d.rectangle([x, y + h * 0.80, x + w, y + h * 0.94], fill=(166, 30, 34))
    d.text((x + 6, y + h * 0.815), "RED ALERT",
           font=font(F_SANS_B, 9), fill=(255, 255, 255))


def scene_cop31(d, x, y, w, h):
    """Antalya at dusk: the Taurus peaks, a white negotiation table, two
    flags and a gavel. Kept from v1 — it worked."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 225, 190))
    d.polygon([(x, y + h * 0.55), (x + w * 0.25, y + h * 0.18),
               (x + w * 0.45, y + h * 0.55)], fill=(90, 110, 140))
    d.polygon([(x + w * 0.45, y + h * 0.55), (x + w * 0.70, y + h * 0.22),
               (x + w, y + h * 0.55)], fill=(70, 90, 120))
    d.ellipse([x + w * 0.80, y + h * 0.08, x + w * 0.80 + 16,
               y + h * 0.08 + 16], fill=(255, 200, 90))
    d.rectangle([x, y + h * 0.55, x + w, y + h], fill=(180, 160, 110))
    d.rectangle([x + w * 0.08, y + h * 0.66, x + w * 0.92, y + h * 0.74],
                fill=(255, 255, 255))
    for fx, col in [(0.12, RED), (0.80, TEAL)]:
        d.line([x + w * fx, y + h * 0.66, x + w * fx, y + h * 0.40],
               fill=(60, 60, 60), width=2)
        d.rectangle([x + w * fx, y + h * 0.40, x + w * (fx + 0.08),
                     y + h * 0.50], fill=col)
    d.line([x + w * 0.46, y + h * 0.66, x + w * 0.54, y + h * 0.60],
           fill=(120, 80, 40), width=4)
    d.rectangle([x + w * 0.53, y + h * 0.58, x + w * 0.60, y + h * 0.62],
                fill=(120, 80, 40))


def scene_kyiv(d, x, y, w, h):
    """Kyiv at dusk: a blue sky, a dark skyline with one gold dome, and
    the blue-and-yellow flag. The city watches the Shenzhen summit from
    the sidelines — that is the story, so the flag leads."""
    d.rectangle([x, y, x + w, y + h], fill=(70, 110, 170))
    d.ellipse([x + w * 0.82, y + h * 0.08, x + w * 0.82 + 12,
               y + h * 0.08 + 12], fill=(255, 220, 120))
    for bx, bw, bh in [(0.04, 0.14, 0.30), (0.22, 0.12, 0.22),
                       (0.38, 0.16, 0.34), (0.58, 0.12, 0.24),
                       (0.74, 0.14, 0.28)]:
        d.rectangle([x + w * bx, y + h * 0.86 - h * bh,
                     x + w * (bx + bw), y + h * 0.86], fill=(40, 50, 80))
    cx = x + w * 0.46
    d.pieslice([cx - 8, y + h * 0.86 - h * 0.34 - 8,
                cx + 8, y + h * 0.86 - h * 0.34 + 8],
               180, 360, fill=(255, 200, 60))
    d.rectangle([x, y + h * 0.86, x + w, y + h], fill=(240, 210, 90))
    fx, fy = x + w * 0.08, y + h * 0.10
    d.line([fx, fy, fx, fy + h * 0.30], fill=(60, 60, 60), width=2)
    d.rectangle([fx, fy, fx + w * 0.20, fy + h * 0.09], fill=(0, 90, 180))
    d.rectangle([fx, fy + h * 0.09, fx + w * 0.20, fy + h * 0.18],
                fill=(255, 215, 0))


def scene_apec(d, x, y, w, h):
    """The Shenzhen Declaration itself: a white document with a gold seal
    on a teal conference backdrop, a red '21' badge for the 21 economies."""
    d.rectangle([x, y, x + w, y + h], fill=(30, 80, 95))
    for bx, bw, bh in [(0.04, 0.14, 0.22), (0.22, 0.10, 0.16),
                       (0.78, 0.12, 0.20)]:
        d.rectangle([x + w * bx, y + h * 0.88 - h * bh,
                     x + w * (bx + bw), y + h * 0.88], fill=(20, 50, 65))
    d.rectangle([x + w * 0.28, y + h * 0.08, x + w * 0.72, y + h * 0.92],
                fill=(255, 255, 255))
    d.ellipse([x + w * 0.45, y + h * 0.16, x + w * 0.55, y + h * 0.30],
              fill=GOLD)
    d.ellipse([x + w * 0.47, y + h * 0.19, x + w * 0.53, y + h * 0.27],
              fill=(255, 255, 255))
    for i, ly in enumerate([0.40, 0.52, 0.64, 0.76]):
        d.rectangle([x + w * 0.34, y + h * ly, x + w * (0.66 - i * 0.04),
                     y + h * ly + 3], fill=(120, 120, 120))
    d.ellipse([x + w * 0.66, y + h * 0.06, x + w * 0.80, y + h * 0.20],
              fill=RED)
    d.text((x + w * 0.695, y + h * 0.085), "21",
           font=font(F_SANS_B, 11), fill=(255, 255, 255))


def scene_melenchon(d, x, y, w, h):
    """Paris: the Eiffel Tower at dusk and the tricolore on a pole. The
    tower is drawn with four strokes — legs, two crossbars, spire."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 225, 180))
    d.ellipse([x + w * 0.80, y + h * 0.08, x + w * 0.80 + 14,
               y + h * 0.08 + 14], fill=(255, 200, 90))
    cx, base = x + w * 0.62, y + h * 0.90
    d.line([cx - 16, base, cx, y + h * 0.12], fill=(60, 55, 70), width=3)
    d.line([cx + 16, base, cx, y + h * 0.12], fill=(60, 55, 70), width=3)
    d.line([cx - 10, y + h * 0.62, cx + 10, y + h * 0.62],
           fill=(60, 55, 70), width=3)
    d.line([cx - 6, y + h * 0.38, cx + 6, y + h * 0.38],
           fill=(60, 55, 70), width=3)
    d.line([cx, y + h * 0.12, cx, y + h * 0.04], fill=(60, 55, 70), width=2)
    d.rectangle([x, y + h * 0.90, x + w, y + h], fill=(120, 110, 100))
    fx, fy = x + w * 0.08, y + h * 0.14
    d.line([fx, fy, fx, fy + h * 0.42], fill=(60, 60, 60), width=2)
    for i, col in enumerate([(0, 57, 166), (255, 255, 255), RED]):
        d.rectangle([fx + w * 0.07 * i, fy, fx + w * 0.07 * (i + 1),
                     fy + h * 0.22], fill=col)


def scene_geology(d, x, y, w, h):
    """The Great Unconformity: flat sedimentary strata on top, a red
    zigzag where a billion years of rock is missing, dark basement below.
    Two small labels date the gap — 540m above, 1.7bn below."""
    d.rectangle([x, y, x + w, y + h * 0.18], fill=(235, 210, 170))
    d.rectangle([x, y + h * 0.18, x + w, y + h * 0.34], fill=(190, 150, 110))
    d.rectangle([x, y + h * 0.34, x + w, y + h * 0.50], fill=(160, 145, 125))
    zig = []
    for i in range(9):
        zig.append((x + w * (i / 8), y + h * (0.50 + (0.05 if i % 2 else -0.02))))
    d.line(zig, fill=RED, width=3)
    d.rectangle([x, y + h * 0.50, x + w, y + h], fill=(70, 60, 55))
    for sx, sy in [(0.15, 0.62), (0.45, 0.75), (0.75, 0.66), (0.30, 0.88),
                   (0.60, 0.90)]:
        d.ellipse([x + w * sx, y + h * sy, x + w * sx + 4, y + h * sy + 3],
                  fill=(100, 90, 80))
    d.text((x + 5, y + h * 0.06), "540m", font=font(F_SANS_B, 10),
           fill=(120, 90, 60))
    d.text((x + w * 0.78, y + h * 0.78), "1.7bn",
           font=font(F_SANS_B, 10), fill=(200, 190, 170))


def scene_florida(d, x, y, w, h):
    """Flooded Broward: a rain band over the water, a palm leaning, a
    half-submerged car. Kept from v1 — it worked."""
    d.rectangle([x, y, x + w, y + h], fill=(120, 150, 180))
    d.ellipse([x + w * 0.72, y + h * 0.08, x + w * 0.72 + 18,
               y + h * 0.08 + 18], fill=(255, 230, 150))
    d.rectangle([x, y + h * 0.68, x + w, y + h], fill=(60, 90, 130))
    for i in range(5):
        rx = x + w * (0.05 + i * 0.20)
        d.line([rx, y + h * 0.06, rx - 6, y + h * 0.30],
               fill=(230, 240, 250), width=2)
    d.line([x + w * 0.10, y + h * 0.68, x + w * 0.16, y + h * 0.35],
           fill=(40, 60, 30), width=4)
    for ang in (-60, -30, 0, 30):
        rad = math.radians(ang)
        d.line([x + w * 0.16, y + h * 0.35,
                x + w * 0.16 + 22 * math.cos(rad),
                y + h * 0.35 + 22 * math.sin(rad)],
               fill=(40, 60, 30), width=3)
    d.rounded_rectangle([x + w * 0.40, y + h * 0.60, x + w * 0.85, y + h * 0.72],
                        radius=8, fill=(166, 30, 34))
    d.polygon([(x + w * 0.46, y + h * 0.60), (x + w * 0.51, y + h * 0.54),
               (x + w * 0.60, y + h * 0.54), (x + w * 0.64, y + h * 0.60)],
              fill=(180, 220, 230))
    d.ellipse([x + w * 0.48, y + h * 0.68, x + w * 0.48 + 10, y + h * 0.68 + 5],
              fill=(20, 20, 20))
    for wx in (0.30, 0.60, 0.85):
        d.line([x + w * wx, y + h * 0.80, x + w * (wx + 0.08), y + h * 0.80],
               fill=(200, 220, 240), width=2)




def scene_iran2027(d, x, y, w, h):
    """Washington defers the Iran decision: a desk calendar flipped to
    2027, the 2026 page crossed out, a small US flag beside it."""
    d.rectangle([x, y, x + w, y + h], fill=(232, 222, 196))
    d.rectangle([x + w * 0.06, y + h * 0.10, x + w * 0.62, y + h * 0.90],
                fill=(255, 255, 255), outline=(26, 26, 26), width=2)
    d.rectangle([x + w * 0.06, y + h * 0.10, x + w * 0.62, y + h * 0.28],
                fill=RED)
    d.text((x + w * 0.12, y + h * 0.32), "2027",
           font=font(F_SANS_B, 30), fill=RED)
    d.text((x + w * 0.12, y + h * 0.68), "2026",
           font=font(F_SANS_B, 16), fill=(150, 150, 150))
    d.line([x + w * 0.10, y + h * 0.74, x + w * 0.36, y + h * 0.80],
           fill=RED, width=3)
    for i, col in enumerate([RED, (255, 255, 255), RED, (255, 255, 255),
                             RED, (255, 255, 255), RED]):
        d.rectangle([x + w * (0.70 + i * 0.04), y + h * 0.18,
                     x + w * (0.74 + i * 0.04), y + h * 0.44], fill=col)
    d.rectangle([x + w * 0.70, y + h * 0.18, x + w * 0.98, y + h * 0.44],
                outline=(26, 26, 26), width=1)
    d.ellipse([x + w * 0.72, y + h * 0.20, x + w * 0.76, y + h * 0.24],
              fill=(0, 57, 166))
    d.text((x + w * 0.70, y + h * 0.52), "JAN 1",
           font=font(F_SANS_B, 13), fill=INK)


def scene_market(d, x, y, w, h):
    """Wall Street's red day: a row of falling red candles under a
    plunging yellow line, the Dow's -1,101 in big type."""
    d.rectangle([x, y, x + w, y + h], fill=(16, 42, 80))
    d.text((x + 8, y + 5), "-1,101", font=font(F_SANS_B, 19),
           fill=(255, 120, 110))
    for i, top in enumerate([0.34, 0.42, 0.38, 0.50, 0.56, 0.64]):
        bx = x + w * (0.08 + i * 0.15)
        bw = w * 0.09
        d.line([bx + bw / 2, y + h * (top - 0.06),
                bx + bw / 2, y + h * (top + 0.28)], fill=(255, 120, 110),
               width=2)
        d.rectangle([bx, y + h * top, bx + bw, y + h * (top + 0.22)],
                    fill=(220, 60, 50))
    d.line([(x + w * 0.06, y + h * 0.22), (x + w * 0.30, y + h * 0.40),
            (x + w * 0.55, y + h * 0.52), (x + w * 0.94, y + h * 0.80)],
           fill=(255, 200, 90), width=3)
    d.line([x + w * 0.06, y + h * 0.86, x + w * 0.94, y + h * 0.86],
           fill=(255, 255, 255), width=2)


def scene_berlin(d, x, y, w, h):
    """Berlin: the Brandenburg Gate at dusk, the EU flag's circle of
    stars above it, a small German flag on a pole."""
    d.rectangle([x, y, x + w, y + h], fill=(250, 225, 180))
    d.ellipse([x + w * 0.80, y + h * 0.06, x + w * 0.80 + 14,
               y + h * 0.06 + 14], fill=(255, 200, 90))
    d.rectangle([x + w * 0.10, y + h * 0.30, x + w * 0.90, y + h * 0.42],
                fill=(170, 140, 100))
    for cx in (0.18, 0.34, 0.50, 0.66, 0.82):
        d.rectangle([x + w * cx - 4, y + h * 0.42, x + w * cx + 4,
                     y + h * 0.88], fill=(150, 120, 85))
    d.rectangle([x + w * 0.06, y + h * 0.88, x + w * 0.94, y + h * 0.96],
                fill=(120, 110, 100))
    d.line([x + w * 0.50, y + h * 0.30, x + w * 0.50, y + h * 0.06],
           fill=(60, 60, 60), width=2)
    d.rectangle([x + w * 0.50, y + h * 0.06, x + w * 0.62, y + h * 0.16],
                fill=(0, 57, 166))
    for k in range(6):
        a = math.radians(k * 60)
        d.ellipse([x + w * 0.56 + 7 * math.cos(a) - 1,
                   y + h * 0.11 + 5 * math.sin(a) - 1,
                   x + w * 0.56 + 7 * math.cos(a) + 1,
                   y + h * 0.11 + 5 * math.sin(a) + 1],
                  fill=(255, 215, 0))


def scene_rates(d, x, y, w, h):
    """Beijing: a bank front with columns and a red '3.00%' rate board
    held flat — the 18th month on hold."""
    d.rectangle([x, y, x + w, y + h], fill=(240, 225, 190))
    d.polygon([(x + w * 0.10, y + h * 0.30), (x + w * 0.50, y + h * 0.08),
               (x + w * 0.90, y + h * 0.30)], fill=(150, 60, 50))
    for cx in (0.20, 0.38, 0.56, 0.74):
        d.rectangle([x + w * cx - 5, y + h * 0.32, x + w * cx + 5,
                     y + h * 0.78], fill=(220, 205, 170),
                    outline=(120, 100, 70), width=1)
    d.rectangle([x + w * 0.08, y + h * 0.78, x + w * 0.92, y + h * 0.86],
                fill=(120, 100, 70))
    d.rectangle([x + w * 0.28, y + h * 0.50, x + w * 0.72, y + h * 0.74],
                fill=NAVY)
    d.text((x + w * 0.33, y + h * 0.55), "3.00%",
           font=font(F_SANS_B, 13), fill=(255, 255, 255))


def scene_cpi(d, x, y, w, h):
    """Tokyo: three rising CPI bars — 2.1, then 2.2 — with a red line
    marking the BOJ's 2% target."""
    d.rectangle([x, y, x + w, y + h], fill=(255, 255, 255))
    d.line([x + w * 0.06, y + h * 0.30, x + w * 0.94, y + h * 0.30],
           fill=RED, width=2)
    d.text((x + w * 0.06, y + h * 0.06), "2% target",
           font=font(F_SANS_B, 9), fill=RED)
    for i, (lab, bh, col) in enumerate([("2.0", 0.30, (150, 150, 150)),
                                        ("2.1", 0.44, TEAL),
                                        ("2.2", 0.52, RED)]):
        bx = x + w * (0.12 + i * 0.28)
        d.rectangle([bx, y + h * (0.88 - bh), bx + w * 0.18, y + h * 0.88],
                    fill=col)
        d.text((bx, y + h * (0.88 - bh) - 12), lab,
               font=font(F_SANS_B, 10), fill=INK)
    d.text((x + w * 0.06, y + h * 0.90), "SEP - OCT",
           font=font(F_SANS_B, 8), fill=GREY)


def scene_hayabusa(d, x, y, w, h):
    """Hayabusa2 in deep space: the probe with its solar panels, a grey
    asteroid below, and a dashed course bending away from it."""
    d.rectangle([x, y, x + w, y + h], fill=(10, 20, 40))
    for sx, sy in [(0.12, 0.15), (0.30, 0.08), (0.70, 0.12), (0.88, 0.25),
                   (0.20, 0.35), (0.55, 0.06)]:
        d.ellipse([x + w * sx, y + h * sy, x + w * sx + 2, y + h * sy + 2],
                  fill=(255, 255, 255))
    d.rectangle([x + w * 0.42, y + h * 0.28, x + w * 0.58, y + h * 0.44],
                fill=(200, 200, 210), outline=(255, 255, 255), width=1)
    d.rectangle([x + w * 0.18, y + h * 0.32, x + w * 0.42, y + h * 0.40],
                fill=(40, 90, 160))
    d.rectangle([x + w * 0.58, y + h * 0.32, x + w * 0.82, y + h * 0.40],
                fill=(40, 90, 160))
    d.ellipse([x + w * 0.60, y + h * 0.62, x + w * 0.60 + 34,
               y + h * 0.62 + 26], fill=(140, 130, 120))
    d.ellipse([x + w * 0.66, y + h * 0.68, x + w * 0.66 + 8,
               y + h * 0.68 + 6], fill=(100, 90, 80))
    for i in range(6):
        px = x + w * (0.10 + i * 0.10)
        py = y + h * (0.55 + i * 0.055)
        d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 200, 90))


def scene_presser(d, x, y, w, h):
    """The White House at noon: the portico, a podium with microphones,
    and a clock reading 12."""
    d.rectangle([x, y, x + w, y + h], fill=(200, 220, 240))
    d.rectangle([x + w * 0.14, y + h * 0.34, x + w * 0.86, y + h * 0.86],
                fill=(255, 255, 255))
    d.polygon([(x + w * 0.14, y + h * 0.34), (x + w * 0.86, y + h * 0.34),
               (x + w * 0.50, y + h * 0.16)], fill=(230, 230, 230))
    for cx in (0.26, 0.42, 0.58, 0.74):
        d.rectangle([x + w * cx - 4, y + h * 0.38, x + w * cx + 4,
                     y + h * 0.78], fill=(200, 200, 200))
    d.rectangle([x + w * 0.40, y + h * 0.60, x + w * 0.60, y + h * 0.86],
                fill=(90, 60, 40))
    d.line([x + w * 0.46, y + h * 0.60, x + w * 0.44, y + h * 0.52],
           fill=(26, 26, 26), width=2)
    d.line([x + w * 0.54, y + h * 0.60, x + w * 0.56, y + h * 0.52],
           fill=(26, 26, 26), width=2)
    d.ellipse([x + w * 0.80, y + h * 0.08, x + w * 0.80 + 18,
               y + h * 0.08 + 18], fill=(255, 255, 255),
              outline=(26, 26, 26), width=1)
    d.text((x + w * 0.835, y + h * 0.10), "12",
           font=font(F_SANS_B, 9), fill=INK)


def scene_baseball(d, x, y, w, h):
    """A ballpark at dusk: the green diamond, white bases, a bat and a
    ball, and Rose's 4,256 in big type."""
    d.rectangle([x, y, x + w, y + h], fill=(60, 120, 60))
    d.polygon([(x + w * 0.50, y + h * 0.10), (x + w * 0.92, y + h * 0.52),
               (x + w * 0.50, y + h * 0.94), (x + w * 0.08, y + h * 0.52)],
              fill=(90, 160, 80))
    for bx, by in [(0.50, 0.10), (0.92, 0.52), (0.50, 0.94), (0.08, 0.52)]:
        d.rectangle([x + w * bx - 4, y + h * by - 4,
                     x + w * bx + 4, y + h * by + 4], fill=(255, 255, 255))
    d.line([x + w * 0.20, y + h * 0.78, x + w * 0.38, y + h * 0.60],
           fill=(180, 130, 80), width=5)
    d.ellipse([x + w * 0.62, y + h * 0.18, x + w * 0.62 + 12,
               y + h * 0.18 + 12], fill=(255, 255, 255),
              outline=RED, width=1)
    d.text((x + w * 0.06, y + h * 0.70), "4,256",
           font=font(F_SANS_B, 16), fill=(255, 255, 255),
           stroke_width=1, stroke_fill=(26, 26, 26))


def scene_vaccine(d, x, y, w, h):
    """Bhopal: a vaccine vial and a syringe over a green cross, with a
    white egg — a chicken vaccine, not a human one."""
    d.rectangle([x, y, x + w, y + h], fill=(235, 245, 235))
    d.rectangle([x + w * 0.08, y + h * 0.10, x + w * 0.30, y + h * 0.32],
                fill=(46, 125, 50))
    d.rectangle([x + w * 0.16, y + h * 0.02, x + w * 0.22, y + h * 0.40],
                fill=(46, 125, 50))
    d.rectangle([x + w * 0.42, y + h * 0.34, x + w * 0.58, y + h * 0.86],
                fill=(220, 240, 255), outline=(26, 26, 26), width=1)
    d.rectangle([x + w * 0.47, y + h * 0.22, x + w * 0.53, y + h * 0.34],
                fill=(150, 150, 150))
    d.rectangle([x + w * 0.42, y + h * 0.58, x + w * 0.58, y + h * 0.68],
                fill=(255, 80, 80))
    d.line([x + w * 0.66, y + h * 0.30, x + w * 0.86, y + h * 0.10],
           fill=(26, 26, 26), width=3)
    d.polygon([(x + w * 0.86, y + h * 0.10), (x + w * 0.94, y + h * 0.04),
               (x + w * 0.90, y + h * 0.16)], fill=(26, 26, 26))
    d.ellipse([x + w * 0.68, y + h * 0.62, x + w * 0.68 + 22,
               y + h * 0.62 + 28], fill=(255, 255, 255),
              outline=(200, 190, 160), width=1)

SCENES = {
    "summit": scene_summit,
    "gta": scene_gta,
    "ipo": scene_ipo,
    "bridge": scene_bridge,
    "icj": scene_icj,
    "gaza": scene_gaza,
    "akvan": scene_akvan,
    "cop31": scene_cop31,
    "kyiv": scene_kyiv,
    "apec": scene_apec,
    "melenchon": scene_melenchon,
    "geology": scene_geology,
    "florida": scene_florida,
    "iran2027": scene_iran2027,
    "market": scene_market,
    "berlin": scene_berlin,
    "rates": scene_rates,
    "cpi": scene_cpi,
    "hayabusa": scene_hayabusa,
    "presser": scene_presser,
    "baseball": scene_baseball,
    "vaccine": scene_vaccine,
}

# ---------------------------------------------------------------------------
# map — dark navy panel, filled tan continents, big red numbered pins.
# v1's light dotted-grey map was the weakest element on the board;
# the top-20 leaders all use a dark map with filled land.
# ---------------------------------------------------------------------------

CONTINENTS = [
    [(-168, 66), (-140, 70), (-125, 72), (-110, 68), (-95, 69), (-85, 66),
     (-80, 73), (-65, 60), (-55, 52), (-65, 45), (-75, 35), (-80, 26),
     (-84, 30), (-90, 21), (-97, 26), (-105, 20), (-110, 24), (-117, 33),
     (-125, 40), (-124, 48), (-135, 58), (-150, 60), (-165, 60)],
    [(-78, 7), (-77, 4), (-80, -3), (-81, -6), (-75, -15), (-70, -18),
     (-70, -23), (-65, -25), (-57, -30), (-48, -28), (-40, -20),
     (-35, -9), (-35, -6), (-44, -3), (-50, 0), (-60, 8), (-70, 11)],
    [(-10, 37), (-9, 43), (-2, 48), (-4, 50), (2, 51), (5, 53), (8, 57),
     (10, 59), (18, 56), (21, 55), (24, 58), (28, 59), (30, 60),
     (28, 62), (24, 65), (21, 70), (30, 70), (40, 68), (45, 68),
     (55, 69), (68, 73), (75, 73), (80, 73), (100, 77), (110, 74),
     (130, 72), (150, 70), (170, 67), (178, 65), (170, 60), (162, 60),
     (158, 53), (142, 50), (140, 45), (135, 43), (130, 38), (127, 35),
     (122, 30), (120, 22), (110, 20), (105, 10), (100, 8), (98, 12),
     (95, 16), (90, 22), (85, 20), (80, 15), (77, 8), (73, 20),
     (70, 25), (66, 25), (60, 25), (57, 26), (52, 26), (50, 30),
     (48, 30), (44, 29), (42, 15), (43, 12), (40, 15), (39, 21),
     (35, 29), (34, 31), (30, 36), (27, 37), (23, 36), (19, 42),
     (14, 45), (8, 44), (3, 42), (-1, 37)],
    [(12, 35), (10, 37), (20, 32), (30, 31), (32, 31), (35, 28),
     (37, 18), (43, 11), (48, 11), (51, 12), (44, 1), (40, -5),
     (39, -10), (36, -18), (33, -26), (28, -33), (20, -35), (17, -32),
     (14, -22), (12, -18), (12, -6), (9, 4), (6, 4), (-8, 4),
     (-13, 8), (-17, 15), (-16, 20), (-15, 27), (-10, 31), (-6, 33)],
    [(113, -22), (114, -30), (115, -35), (118, -35), (124, -33),
     (129, -32), (132, -32), (136, -35), (140, -38), (145, -38),
     (150, -37), (153, -32), (153, -27), (150, -22), (146, -19),
     (142, -11), (136, -12), (132, -11), (130, -13), (126, -14),
     (122, -17), (118, -20), (114, -22)],
]


def lonlat_to_xy(lon, lat, mx, my, mw, mh):
    return (mx + (lon + 180) / 360 * mw,
            my + (85 - lat) / 145 * mh)


def draw_map(d, mx, my, mw, mh, pins, grey):
    """Dark-navy panel, tan filled continents, red numbered pins for the
    13 featured stories, small grey dots for the ALSO briefs."""
    d.rectangle([mx, my, mx + mw, my + mh], fill=DARKMAP)
    for poly in CONTINENTS:
        pts = [lonlat_to_xy(lon, lat, mx, my, mw, mh) for lon, lat in poly]
        d.polygon(pts, fill=LAND)
    f_num = font(F_SANS_B, 10)
    for lon, lat in grey:
        gx, gy = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        d.ellipse([gx - 2, gy - 2, gx + 2, gy + 2], fill=(170, 170, 160))
    for num, pin in pins.items():
        # a pin may carry an (dx, dy) pixel offset: five pins crowd into
        # Europe and the Gulf, so they are nudged apart with a thin white
        # leader line back to the true spot (v2 first pass: pins 5/11,
        # 4/9 and 6/8 sat on top of each other, and pin 10 hid pin 1)
        lon, lat = pin[0], pin[1]
        dx, dy = (pin[2], pin[3]) if len(pin) > 3 else (0, 0)
        px, py = lonlat_to_xy(lon, lat, mx, my, mw, mh)
        if dx or dy:
            d.line([px, py, px + dx, py + dy], fill=(255, 255, 255), width=1)
            d.ellipse([px - 2, py - 2, px + 2, py + 2], fill=(255, 255, 255))
            px, py = px + dx, py + dy
        r = 9
        d.ellipse([px - r, py - r, px + r, py + r],
                  fill=RED, outline=(255, 255, 255), width=1)
        w_num = d.textlength(num, font=f_num)
        d.text((px - w_num / 2, py - 7), num, font=f_num,
               fill=(255, 255, 255))


def _num_disc(d, cx, cy, r, label, col):
    d.ellipse([cx - r, cy - r, cx + r, cy + r], fill=col,
              outline=(255, 255, 255), width=1)
    f = font(F_SANS_B, 11)
    w = d.textlength(label, font=f)
    d.text((cx - w / 2, cy - 7), label, font=f, fill=(255, 255, 255))


# ---------------------------------------------------------------------------
# layout
# ---------------------------------------------------------------------------

def build():
    img = Image.new("RGB", (W, H), PAPER)
    d = ImageDraw.Draw(img)
    y = 10

    # --- top band
    fs = font(F_SANS_B, 13)
    left = "THE WORLD IN ONE DAY"
    right = "FRIDAY'S NEWS · ONE PAGE · 43 STORIES"
    d.text((M, y), left, font=fs, fill=RED)
    d.text((W - M - d.textlength(right, font=fs), y), right,
           font=fs, fill=RED)
    y += 18
    d.line([M, y + 3, W - M, y + 3], fill=INK, width=2)
    y += 8

    # --- masthead
    f_head = fit_font(F_DISP_BLACK, "THE WORLD IN ONE DAY", CW, 62)
    d.text((M, y), "THE WORLD IN ONE DAY", font=f_head, fill=INK)
    y += 58

    # --- strapline
    fs = font(F_SERIF_IT, 17)
    d.text((M, y), "A peace declaration in Shenzhen · Akvan comes ashore · "
                   "Trump puts Iran off to 2027", font=fs, fill=RED)
    y += 22
    d.line([M, y, W - M, y], fill=HAIR, width=1)
    y += 6

    # --- THE DAY IN UTC: the hook device (the leaders' timeline strip)
    uw = (CW - 4 * 6) // 5
    for i, (lab, txt) in enumerate(UTC):
        ux = M + i * (uw + 6)
        d.rectangle([ux, y, ux + uw, y + 40], fill=(255, 255, 255),
                    outline=NAVY, width=1)
        d.text((ux + 7, y + 3), lab, font=font(F_SANS_B, 10), fill=RED)
        draw_wrapped(d, ux + 7, y + 17, txt, font(F_SANS, 10), INK,
                     uw - 14, leading=11, max_lines=2)
    y += 40 + 6

    # --- region bar
    total = sum(c for _, c, _ in REGIONS)
    widths = [max(int(CW * c / total), 60) for _, c, _ in REGIONS]
    excess = sum(widths) - CW
    widths[widths.index(max(widths))] -= excess
    x = M
    fr = font(F_SANS_B, 11)
    for (name, count, col), wdt in zip(REGIONS, widths):
        d.rectangle([x, y, x + wdt, y + 19], fill=col)
        label = f"{name} {count}"
        d.text((x + wdt / 2 - d.textlength(label, font=fr) / 2, y + 3),
               label, font=fr, fill=(255, 255, 255))
        x += wdt
    y += 19 + 6

    # --- BY THE NUMBERS
    sw = (CW - 5 * 8) // 6
    d.line([M, y, W - M, y], fill=HAIR, width=1)
    y += 6
    for i, (num, lab) in enumerate(NUMBERS):
        x = M + i * (sw + 8)
        d.text((x, y), num, font=font(F_SANS_B, 17), fill=RED)
        draw_wrapped(d, x, y + 22, lab, font(F_SANS, 10), INK, sw - 16,
                     leading=11, max_lines=2)
    y += 44 + 6

    # --- three equal leads
    panel_h = 100
    lead_w = (CW - 2 * 16) // 3
    lead_bottom = y
    for i, (kick, col, scene, head, summ) in enumerate(LEADS):
        x = M + i * (lead_w + 16)
        SCENES[scene](d, x, y, lead_w, panel_h)
        _num_disc(d, x + lead_w - 18, y + panel_h - 16, 13, str(i + 1), col)
        d.text((x, y + panel_h + 9), kick, font=font(F_SANS_B, 11), fill=col)
        hy = draw_wrapped(d, x, y + panel_h + 31, head,
                          font(F_DISP_BOLD, 19), INK, lead_w,
                          leading=21, max_lines=2)
        sy = draw_wrapped(d, x, hy + 3, summ, font(F_SANS, 12), INK,
                          lead_w, leading=13, max_lines=2)
        lead_bottom = max(lead_bottom, sy)
    y = lead_bottom + 6
    d.line([M, y, W - M, y], fill=HAIR, width=1)
    y += 6

    # --- the day in brief: 10 mediums, 5-across x 2 rows, taller scenes
    fh_b = font(F_SANS_B, 14)
    d.text((M, y), "THE DAY IN BRIEF", font=fh_b, fill=RED)
    d.text((W - M - d.textlength("STORIES 04–13", font=fr), y + 2),
           "STORIES 04–13", font=fr, fill=GREY)
    y += 18
    card_w = (CW - 4 * 12) // 5
    card_h = 124
    for idx, (kick, col, scene, head, summ) in enumerate(MEDIUMS):
        r, c = divmod(idx, 5)
        x = M + c * (card_w + 12)
        cy = y + r * (card_h + 8)
        d.rectangle([x, cy, x + card_w, cy + card_h],
                    fill=(255, 255, 255), outline=(200, 192, 170), width=1)
        SCENES[scene](d, x + 1, cy + 1, card_w - 2, 50)
        _num_disc(d, x + card_w - 15, cy + 62, 9, str(idx + 4), col)
        tx = x + 10
        tw = card_w - 20 - 24
        d.text((tx, cy + 54), kick, font=font(F_SANS_B, 10), fill=col)
        hy = draw_wrapped(d, tx, cy + 67, head, font(F_SANS_B, 13), INK,
                          tw, leading=14, max_lines=2)
        draw_wrapped(d, tx, hy + 2, summ, font(F_SANS, 11), INK, tw,
                     leading=11, max_lines=2)
    y += 2 * card_h + 8 + 6
    d.line([M, y, W - M, y], fill=HAIR, width=1)
    y += 6

    # --- footer band: dark map + ALSO list
    d.text((M, y), "WHERE IT HAPPENED", font=fh_b, fill=RED)
    map_w = 380
    ax = M + map_w + 20
    d.text((ax, y), "ALSO ON FRIDAY 20 NOVEMBER — 30 MORE STORIES",
           font=fh_b, fill=RED)
    y += 16
    pins = {
        "1": (114.1, 22.5),      # Shenzhen — declaration
        "2": (85.8, 19.8),       # Gopalpur, Odisha — Akvan landfall
        "3": (-77.0, 38.9),      # Washington — Iran deferred
        "4": (-74.0, 40.7),      # New York — Wall Street slide
        "5": (30.7, 36.9),       # Antalya — COP31
        "6": (13.4, 52.5),       # Berlin — Ukraine talks
        "7": (116.4, 39.9),      # Beijing — loan rates held
        "8": (139.7, 35.7),      # Tokyo — core CPI 2.2%
        "9": (139.7, 35.7, 16, 12),   # Tokyo — Hayabusa2 (JAXA), nudged
        "10": (-77.0, 38.9, -18, 14), # Washington — noon presser, nudged
        "11": (-80.2, 25.8),     # Miami — GTA VI launch
        "12": (-84.5, 39.1, -20, -12), # Cincinnati — Pete Rose, nudged
        "13": (77.4, 23.3),      # Bhopal — H5N1 vaccine
    }
    grey = [
        (4.4, 50.9), (77.2, 28.6), (90.4, 23.8), (127.0, 37.5),
        (114.2, 22.3), (151.2, -33.9), (174.8, -41.3), (30.5, 50.4),
        (36.3, 33.5), (51.4, 35.7), (-0.1, 51.5), (45.3, 2.0),
        (-74.1, 4.7), (-78.5, -0.2), (-58.2, 6.8), (44.2, 15.4),
        (101.7, 3.1), (121.0, 14.6), (101.1, 4.6), (11.6, 48.1),
        (51.5, 25.3), (6.1, 46.2), (-66.9, 10.5), (35.5, 33.9),
        (34.5, 31.5),
    ]
    draw_map(d, M, y, map_w, 150, pins, grey)
    d.text((M, y + 154),
           "Red pins mark stories 1–13; grey dots mark the briefs.",
           font=font(F_SANS, 10), fill=GREY)

    acol_w = (W - M - ax - 4) // 3
    fa = font(F_SANS, 9)
    fa_b = font(F_SANS_B, 9)
    for i, item in enumerate(ALSO):
        c, r = divmod(i, 10)
        x = ax + c * (acol_w + 4)
        yy = y + r * 14
        num = str(i + 14)
        d.text((x, yy), num, font=fa_b, fill=RED)
        text = item
        while (d.textlength(text, font=fa) > acol_w - 20
               and len(text) > 8):
            text = text[:-2]
        if text != item:
            text = text[:-1] + "…"
        d.text((x + 18, yy), text, font=fa, fill=INK)
    y += 150 + 18

    # --- DATE CHECK
    d.rectangle([M, y, W - M, y + 30], fill=(238, 232, 214),
                outline=(200, 192, 170), width=1)
    draw_wrapped(d, M + 8, y + 3, DATE_CHECK, font(F_SANS, 10), INK,
                 CW - 16, leading=12, max_lines=2)
    y += 30 + 4

    # --- footer
    draw_wrapped(d, M, y, FOOTER, font(F_SANS, 10), GREY, CW,
                 leading=13, max_lines=2)
    y += 26

    assert y <= H, f"layout overflow: final y={y} > H={H}"
    return img


def main():
    out = sys.argv[1] if len(sys.argv) > 1 else "entry.png"
    build().save(out, optimize=True)
    print(f"wrote {out}")


if __name__ == "__main__":
    main()
