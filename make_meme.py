#!/usr/bin/env python3
"""Draw the GTA 6 launch-week meme variants with Pillow.

Scene idea: on launch day the office is empty because everyone
called in sick to play in Leonida. The white ghost mascot sits
in a beach chair in the scene, controller in hand, holding its
magenta star coin, next to a wooden sign that names the site.
"""
from PIL import Image, ImageDraw, ImageFont
import math
import os

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "meme")
os.makedirs(OUT, exist_ok=True)

BOLD = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"


def font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, size)


def centered(draw, cx, y, text, fnt, fill, stroke=0, stroke_fill=(0, 0, 0)):
    box = draw.textbbox((0, 0), text, font=fnt, stroke_width=stroke)
    w = box[2] - box[0]
    draw.text((cx - w / 2, y), text, font=fnt, fill=fill,
              stroke_width=stroke, stroke_fill=stroke_fill)
    return box[3] - box[1]


def sparkle(draw, cx, cy, r, fill=(0, 0, 0)):
    pts = []
    for i in range(8):
        ang = math.radians(i * 45 - 90)
        rad = r if i % 2 == 0 else r * 0.30
        pts.append((cx + rad * math.cos(ang), cy + rad * math.sin(ang)))
    draw.polygon(pts, fill=fill)


def ghost(draw, cx, top, w, h, coin=True):
    """White ghost: rounded dome, wavy hem, sparkle eyes, magenta coin."""
    x0, x1 = cx - w / 2, cx + w / 2
    # body outline then fill (thick black outline)
    draw.pieslice([x0 - 7, top - 7, x1 + 7, top + w + 14], 180, 360, fill=(0, 0, 0))
    draw.rectangle([x0 - 7, top + w / 2, x1 + 7, top + h], fill=(0, 0, 0))
    draw.pieslice([x0, top, x1, top + w], 180, 360, fill=(255, 255, 255))
    draw.rectangle([x0, top + w / 2, x1, top + h - 26], fill=(255, 255, 255))
    # wavy hem: white scallops over the black base
    waves = 4
    for i in range(waves):
        wx = x0 + (w / waves) * i
        draw.ellipse([wx + 3, top + h - 48, wx + w / waves - 3, top + h + 2],
                     fill=(255, 255, 255))
    # eyes: two black four-pointed sparkles
    sparkle(draw, cx - w * 0.19, top + w * 0.42, 30)
    sparkle(draw, cx + w * 0.19, top + w * 0.42, 30)
    # little round hand + magenta coin with white star
    if coin:
        ccx, ccy, cr = cx + w * 0.52, top + h * 0.52, 62
        draw.ellipse([ccx - cr - 6, ccy - cr - 6, ccx + cr + 6, ccy + cr + 6], fill=(0, 0, 0))
        draw.ellipse([ccx - cr, ccy - cr, ccx + cr, ccy + cr], fill=(230, 0, 140))
        sparkle(draw, ccx, ccy, 34, fill=(255, 255, 255))
        draw.ellipse([cx + w * 0.30, top + h * 0.46, cx + w * 0.44, top + h * 0.60],
                     fill=(255, 255, 255), outline=(0, 0, 0), width=6)


def palm(draw, x, base, h, lean=1):
    draw.line([x, base, x + 26 * lean, base - h], fill=(60, 35, 20), width=16)
    tx, ty = x + 26 * lean, base - h
    for ang in (-160, -115, -70, -25, 15):
        a = math.radians(ang)
        draw.arc([tx - 120, ty - 60, tx + 120, ty + 90],
                 start=ang, end=ang + 55, fill=(20, 110, 45), width=13)


def sunset_bg(img):
    px = img.load()
    W, H = img.size
    top = (70, 20, 110)
    mid = (230, 60, 140)
    low = (255, 150, 60)
    for y in range(H):
        t = y / H
        if t < 0.55:
            k = t / 0.55
            c = tuple(int(top[i] + (mid[i] - top[i]) * k) for i in range(3))
        else:
            k = (t - 0.55) / 0.45
            c = tuple(int(mid[i] + (low[i] - mid[i]) * k) for i in range(3))
        for x in range(0, W, 4):
            for dx in range(4):
                px[x + dx, y] = c


def variant_sick_day():
    W = H = 1024
    img = Image.new("RGB", (W, H), (0, 0, 0))
    sunset_bg(img)
    d = ImageDraw.Draw(img)
    # sun
    d.ellipse([392, 300, 632, 540], fill=(255, 220, 90))
    # sea + sand
    d.rectangle([0, 560, W, 700], fill=(30, 140, 190))
    d.rectangle([0, 700, W, 1024], fill=(245, 205, 130))
    # skyline silhouettes
    for bx, bw, bh in [(20, 90, 210), (130, 70, 150), (830, 80, 190), (925, 70, 140)]:
        d.rectangle([bx, 560 - bh, bx + bw, 560], fill=(35, 15, 60))
    palm(d, 90, 720, 200, 1)
    palm(d, 950, 730, 210, -1)
    # top banner
    d.rectangle([0, 0, W, 150], fill=(0, 0, 0))
    centered(d, W / 2, 18, "GTA 6 LAUNCH DAY:", font(58), (255, 255, 255))
    centered(d, W / 2, 84, "EVERYONE CALLED IN SICK", font(52), (255, 220, 60))
    # speech bubble from the ghost
    d.rounded_rectangle([450, 180, 995, 305], radius=28, fill=(255, 255, 255),
                        outline=(0, 0, 0), width=6)
    d.polygon([(520, 298), (470, 350), (580, 298)], fill=(255, 255, 255))
    centered(d, 722, 200, "*cough* sorry boss,", font(38), (0, 0, 0))
    centered(d, 722, 248, "Leonida fever is real.", font(38), (0, 0, 0))
    # ghost in a beach chair, centre-left of the scene
    d.polygon([(120, 800), (430, 800), (470, 880), (90, 880)], fill=(210, 30, 60))
    d.rectangle([100, 860, 470, 890], fill=(120, 20, 40))
    ghost(d, 275, 400, 250, 330)
    # controller in front of the ghost
    d.rounded_rectangle([185, 700, 365, 770], radius=30, fill=(25, 25, 35),
                        outline=(255, 255, 255), width=4)
    d.ellipse([215, 722, 245, 752], fill=(230, 0, 140))
    d.ellipse([305, 722, 335, 752], fill=(60, 200, 120))
    # wooden sign planted in the sand, naming the site in the scene
    d.rectangle([640, 730, 668, 950], fill=(100, 65, 30))
    d.rounded_rectangle([520, 640, 990, 745], radius=14, fill=(140, 95, 45),
                        outline=(60, 35, 15), width=6)
    centered(d, 755, 662, "make.fun", font(64), (255, 255, 255), stroke=2)
    d.rounded_rectangle([520, 758, 990, 860], radius=14, fill=(255, 255, 255),
                        outline=(60, 35, 15), width=5)
    centered(d, 755, 772, "agents win real money", font(34), (0, 0, 0))
    centered(d, 755, 814, "in bounties here", font(34), (0, 0, 0))
    # bottom banner
    d.rectangle([0, 924, W, 1024], fill=(0, 0, 0))
    centered(d, W / 2, 950, "WAITED 13 YEARS. OFFICE CAN WAIT 1 DAY.",
             font(36), (255, 255, 255))
    img.save(os.path.join(OUT, "variant1-sick-day.png"))
    print("variant1 done")


def variant_waited():
    W = H = 1024
    img = Image.new("RGB", (W, H), (245, 240, 230))
    d = ImageDraw.Draw(img)
    d.rectangle([0, 0, W, 130], fill=(20, 20, 30))
    centered(d, W / 2, 30, "THE 13-YEAR WAIT, IN ONE PHOTO", font(46), (255, 255, 255))
    # left panel: 2013
    d.rectangle([30, 160, 497, 700], fill=(180, 210, 240), outline=(0, 0, 0), width=6)
    centered(d, 263, 180, "2013: AGE 15", font(44), (0, 0, 0))
    centered(d, 263, 250, "\"GTA 6 soon,", font(40), (0, 0, 0))
    centered(d, 263, 300, "trust me bro\"", font(40), (0, 0, 0))
    ghost(d, 263, 380, 170, 230, coin=False)
    # right panel: 2026
    d.rectangle([527, 160, 994, 700], fill=(255, 170, 90), outline=(0, 0, 0), width=6)
    centered(d, 760, 180, "2026: AGE 28", font(44), (0, 0, 0))
    centered(d, 760, 250, "IT'S OUT. I'M CRYING", font(36), (0, 0, 0))
    centered(d, 760, 300, "AT MY KID'S BEDTIME", font(34), (0, 0, 0))
    ghost(d, 760, 380, 170, 230, coin=True)
    d.rectangle([0, 730, W, 1024], fill=(230, 0, 140))
    centered(d, W / 2, 760, "make.fun", font(72), (255, 255, 255))
    centered(d, W / 2, 850, "my agent entered this meme in a bounty", font(38), (255, 255, 255))
    centered(d, W / 2, 900, "and agents win real money there", font(38), (255, 255, 255))
    img.save(os.path.join(OUT, "variant2-waited.png"))
    print("variant2 done")


def variant_memo():
    W = H = 1024
    img = Image.new("RGB", (W, H), (210, 190, 160))
    d = ImageDraw.Draw(img)
    d.rectangle([90, 70, 934, 954], fill=(255, 255, 250), outline=(0, 0, 0), width=5)
    centered(d, 512, 110, "INTERNAL MEMO — HR", font(52), (0, 0, 0))
    d.line([140, 195, 884, 195], fill=(0, 0, 0), width=4)
    lines = [
        "Effective GTA 6 launch week:",
        "",
        "each employee's grandmother",
        "may pass away no more than",
        "ONCE per GTA release.",
        "",
        "We know it has been 13 years.",
        "We are not fooled. We are",
        "also not coming in.",
    ]
    y = 235
    for ln in lines:
        centered(d, 512, y, ln, font(42), (20, 20, 20))
        y += 56
    ghost(d, 800, 700, 120, 165, coin=True)
    centered(d, 400, 800, "— HR (from Leonida)", font(40), (0, 0, 0))
    centered(d, 400, 855, "via make.fun bounties", font(34), (180, 0, 110))
    img.save(os.path.join(OUT, "variant3-memo.png"))
    print("variant3 done")


if __name__ == "__main__":
    variant_sick_day()
    variant_waited()
    variant_memo()
