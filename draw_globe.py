#!/usr/bin/env python3
"""news-image-20261126: a one-image world atlas of Thursday 26 November 2026.

Draws a stylised world map on a deep-navy atlas background, pins the day's
stories by region, and lists them as numbered headlines below the map.
Deterministic: fixed geometry, no randomness, no wall-clock, no network.
Writes /output/entry.png (or $MAKEFUN_OUTPUT_DIR/entry.png) and, when the
repository directory is writable, a copy as entry.png next to this file.
"""

import os
from PIL import Image, ImageDraw, ImageFont

W, H = 1024, 1024

NAVY = (11, 30, 58)          # deep atlas navy
NAVY_LIGHT = (16, 42, 76)    # panel navy
PARCHMENT = (216, 196, 154)  # land fill
PARCHMENT_LINE = (168, 144, 102)
GOLD = (232, 184, 75)
GOLD_DIM = (180, 140, 55)
INK = (240, 238, 230)        # near-white text
MUTED = (168, 186, 205)      # muted blue-grey text
PIN_RED = (206, 74, 56)

FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"
FONTB = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"


def font(path, size):
    return ImageFont.truetype(path, size)


# Map frame (equirectangular): lon -180..180 -> x, lat 78..-58 -> y.
MX0, MX1, MY0, MY1 = 28, 996, 148, 636
LON0, LON1, LAT0, LAT1 = -180.0, 180.0, 78.0, -58.0


def xy(lon, lat):
    x = MX0 + (lon - LON0) / (LON1 - LON0) * (MX1 - MX0)
    y = MY0 + (LAT0 - lat) / (LAT0 - LAT1) * (MY1 - MY0)
    return (x, y)


# Simplified continent outlines (lon, lat) -- recognisable, not precise.
NORTH_AMERICA = [
    (-168, 66), (-150, 70), (-135, 69), (-125, 71), (-115, 68), (-105, 68),
    (-95, 69), (-85, 66), (-82, 62), (-78, 62), (-70, 62), (-65, 60),
    (-60, 55), (-55, 52), (-60, 47), (-65, 44), (-70, 42), (-75, 38),
    (-76, 35), (-80, 32), (-81, 28), (-84, 30), (-88, 29), (-91, 19),
    (-95, 19), (-97, 16), (-92, 15), (-87, 13), (-83, 9), (-80, 8),
    (-83, 9), (-90, 14), (-95, 16), (-100, 18), (-105, 20), (-108, 23),
    (-112, 28), (-115, 31), (-118, 33), (-122, 37), (-124, 42), (-124, 48),
    (-128, 52), (-135, 58), (-145, 60), (-155, 58), (-162, 58), (-168, 62),
]
GREENLAND = [
    (-46, 60), (-38, 64), (-30, 68), (-22, 70), (-25, 76), (-35, 80),
    (-48, 80), (-58, 76), (-58, 70), (-53, 64),
]
SOUTH_AMERICA = [
    (-80, 10), (-77, 8), (-72, 12), (-64, 10), (-58, 8), (-52, 5),
    (-50, 0), (-44, -3), (-38, -5), (-35, -8), (-38, -15), (-40, -22),
    (-48, -28), (-54, -34), (-58, -38), (-63, -41), (-66, -47), (-69, -52),
    (-71, -54), (-73, -50), (-73, -42), (-72, -32), (-71, -22), (-70, -18),
    (-75, -15), (-78, -8), (-80, -3), (-81, 1), (-80, 5),
]
AFRICA = [
    (-17, 15), (-16, 20), (-12, 27), (-8, 31), (-5, 35), (0, 36),
    (10, 37), (15, 34), (20, 32), (25, 32), (30, 31), (33, 28),
    (36, 22), (39, 18), (42, 15), (44, 11), (48, 11), (51, 10),
    (46, 4), (41, -2), (40, -8), (38, -14), (35, -20), (33, -26),
    (30, -30), (27, -33), (22, -35), (18, -33), (16, -28), (14, -22),
    (12, -17), (12, -10), (10, -4), (9, 0), (8, 4), (4, 6),
    (-2, 5), (-8, 5), (-12, 8), (-15, 11),
]
EURASIA = [
    (-10, 36), (-9, 40), (-9, 43), (-4, 44), (-2, 48), (-4, 50),
    (0, 51), (2, 53), (6, 53), (8, 57), (10, 59), (6, 60),
    (10, 62), (14, 66), (18, 69), (24, 71), (30, 70), (36, 68),
    (44, 68), (52, 68), (60, 69), (68, 72), (76, 72), (84, 74),
    (95, 76), (105, 77), (115, 74), (125, 73), (135, 72), (145, 72),
    (155, 70), (165, 69), (172, 66), (178, 65), (178, 62), (170, 60),
    (162, 58), (158, 52), (156, 50), (150, 46), (143, 42), (140, 38),
    (135, 35), (132, 33), (129, 33), (126, 35), (124, 38), (121, 34),
    (120, 30), (117, 24), (112, 22), (109, 19), (108, 13), (105, 9),
    (103, 7), (100, 6), (98, 10), (97, 14), (94, 16), (92, 21),
    (89, 22), (87, 21), (84, 19), (81, 15), (80, 10), (77, 8),
    (75, 12), (73, 19), (71, 21), (68, 23), (65, 25), (61, 25),
    (58, 25), (56, 26), (54, 27), (52, 28), (50, 29), (48, 30),
    (46, 29), (44, 29), (42, 27), (40, 24), (39, 21), (38, 24),
    (36, 28), (35, 31), (34, 35), (32, 36), (29, 36), (27, 37),
    (25, 37), (23, 36), (21, 38), (19, 40), (16, 42), (13, 44),
    (10, 44), (7, 44), (4, 43), (1, 43), (-1, 44), (-2, 47),
    (-4, 48), (-8, 44), (-9, 38),
]
AUSTRALIA = [
    (113, -22), (114, -28), (115, -33), (118, -35), (122, -34), (126, -32),
    (129, -32), (132, -32), (135, -35), (138, -35), (141, -38), (145, -38),
    (149, -37), (151, -34), (153, -31), (153, -27), (151, -24), (148, -20),
    (146, -19), (143, -15), (142, -11), (139, -14), (136, -12), (135, -15),
    (132, -12), (130, -13), (127, -14), (124, -15), (122, -17), (119, -19),
    (116, -20), (114, -22),
]
UK = [(-5, 50), (-3, 53), (-5, 56), (-3, 58), (-1, 57), (0, 53), (1, 51)]
JAPAN = [(130, 31), (132, 33), (135, 34), (137, 35), (139, 37), (140, 39),
         (141, 41), (142, 43), (141, 45), (140, 42), (138, 38), (134, 35),
         (131, 33)]
NEW_ZEALAND = [(167, -45), (169, -43), (172, -41), (175, -38), (178, -38),
               (175, -40), (173, -42), (170, -44), (167, -46)]

CONTINENTS = [NORTH_AMERICA, GREENLAND, SOUTH_AMERICA, AFRICA, EURASIA,
              AUSTRALIA, UK, JAPAN, NEW_ZEALAND]

# (number, lon, lat, headline)
STORIES = [
    (1, 127, 40,
     "North Korea: Kim orders wider rollout of tactical nuclear weapons"),
    (2, 32, 49,
     "Ukraine says it hit a major Russian air base, damaging five planes"),
    (3, -95, 38,
     "US prepares new tariffs aimed at global factory overcapacity"),
    (4, -77, 39,
     "Second US judge blocks Trump's birthright citizenship order"),
    (5, 73, 34,
     "Pakistan's first astronaut to fly on China's Shenzhou-24"),
    (6, 31, 30,
     "Cairo tanker crash sparks huge highway fire; at least 30 killed"),
    (7, 11, 51,
     "BepiColombo enters Mercury orbit after an eight-year journey"),
]


def wrap(draw, text, fnt, max_w):
    """Greedy word wrap into lines no wider than max_w."""
    words = text.split()
    lines, cur = [], ""
    for w in words:
        trial = (cur + " " + w).strip()
        if draw.textlength(trial, font=fnt) <= max_w:
            cur = trial
        else:
            if cur:
                lines.append(cur)
            cur = w
    if cur:
        lines.append(cur)
    return lines


def draw_map(d):
    # Ocean panel.
    d.rectangle([MX0, MY0, MX1, MY1], fill=NAVY_LIGHT,
                outline=GOLD_DIM, width=2)
    # Graticule: every 30 degrees.
    for lon in range(-180, 181, 30):
        x = MX0 + (lon + 180) / 360 * (MX1 - MX0)
        d.line([(x, MY0), (x, MY1)], fill=(60, 90, 130), width=1)
    for lat in range(-60, 79, 30):
        y = MY0 + (78 - lat) / 136 * (MY1 - MY0)
        d.line([(MX0, y), (MX1, y)], fill=(60, 90, 130), width=1)
    # Land.
    for poly in CONTINENTS:
        pts = [xy(lon, lat) for lon, lat in poly]
        d.polygon(pts, fill=PARCHMENT, outline=PARCHMENT_LINE)
    # Equator, dashed look via short segments.
    y_eq = xy(0, 0)[1]
    for x in range(MX0, MX1, 14):
        d.line([(x, y_eq), (x + 8, y_eq)], fill=(120, 150, 185), width=1)
    # Compass rose, over the empty North Pacific (top left of the map).
    cx, cy, r = 132, 262, 34
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=GOLD, width=2)
    d.polygon([(cx, cy - r + 6), (cx - 7, cy + 8), (cx + 7, cy + 8)],
              fill=GOLD)
    d.polygon([(cx, cy + r - 6), (cx - 7, cy - 8), (cx + 7, cy - 8)],
              fill=MUTED)
    d.text((cx, cy - r + 16), "N", font=font(FONTB, 18), fill=INK,
           anchor="mm")
    d.text((cx, cy + r + 14), "WORLD MAP", font=font(FONTB, 14),
           fill=MUTED, anchor="mm")


def draw_pin(d, num, lon, lat):
    x, y = xy(lon, lat)
    r = 17
    d.ellipse([x - r - 3, y - r - 3, x + r + 3, y + r + 3],
              outline=(255, 255, 255), width=2)
    d.ellipse([x - r, y - r, x + r, y + r], fill=PIN_RED,
              outline=(255, 255, 255), width=2)
    d.text((x, y + 1), str(num), font=font(FONTB, 22), fill=(255, 255, 255),
           anchor="mm")


def main():
    img = Image.new("RGB", (W, H), NAVY)
    d = ImageDraw.Draw(img)

    # Outer gold frame.
    d.rectangle([10, 10, W - 11, H - 11], outline=GOLD_DIM, width=2)

    # Masthead.
    title_f = font(FONTB, 52)
    d.text((W // 2, 52), "THE WORLD IN ONE IMAGE", font=title_f,
           fill=INK, anchor="mm")
    date_f = font(FONTB, 28)
    d.text((W // 2, 102), "Thursday 26 November 2026", font=date_f,
           fill=GOLD, anchor="mm")
    d.line([(W // 2 - 320, 130), (W // 2 + 320, 130)], fill=GOLD_DIM, width=2)

    # Map + pins.
    draw_map(d)
    for num, lon, lat, _ in STORIES:
        draw_pin(d, num, lon, lat)

    # Headline list.
    label_f = font(FONTB, 21)
    d.text((40, 664), "THE DAY IN SEVEN STORIES  —  NUMBERS MATCH THE MAP",
           font=label_f, fill=GOLD, anchor="lm")
    d.line([(40, 686), (W - 40, 686)], fill=GOLD_DIM, width=1)

    head_f = font(FONTB, 23)
    y = 706
    row_h = 41
    for num, _lon, _lat, text in STORIES:
        bx, by = 52, y + 8
        d.ellipse([bx - 15, by - 15, bx + 15, by + 15], fill=PIN_RED,
                  outline=(255, 255, 255), width=2)
        d.text((bx, by + 1), str(num), font=font(FONTB, 20),
               fill=(255, 255, 255), anchor="mm")
        lines = wrap(d, text, head_f, W - 120)
        d.text((84, y), lines[0], font=head_f, fill=INK, anchor="lm")
        y += row_h

    # Footer.
    foot_f = font(FONT, 17)
    d.text((W // 2, 1000),
           "All stories first reported on Thursday 26 November 2026  ·  One image, one day",
           font=foot_f, fill=MUTED, anchor="mm")

    out_dir = os.environ.get("MAKEFUN_OUTPUT_DIR", "/output")
    os.makedirs(out_dir, exist_ok=True)
    out_path = os.path.join(out_dir, "entry.png")
    img.save(out_path, format="PNG", optimize=True)
    # Local copy for inspection when the repo directory is writable.
    try:
        here = os.path.dirname(os.path.abspath(__file__))
        img.save(os.path.join(here, "entry.png"), format="PNG",
                 optimize=True)
    except OSError:
        pass


if __name__ == "__main__":
    main()
