#!/usr/bin/env python3
"""Meme v4 generator — gta6-meme-x-01.

FORMAT CHANGE (not a tweak): v3 was a cartoon beach scene with a small
doctor's note; the real judge scored it 0.768985 (#201), far below the
#50 cutoff 0.850615, while the whole top 5 is dense itemised DOCUMENT/UI
humour (Steam receipt, library overdue notice, hurricane warning,
parking citation, phone lock screen). v4 is a full document: a formal
LEAVE OF ABSENCE REQUEST form to HR, filled in by a gamer for GTA VI
launch week.

make.fun is woven in as concrete elements: the ghost is the company
logo and the employee's ID photo, and the form's coverage plan states
the employee's AI agent earns real money in bounties on make.fun
(+$250.00) while he is away — the same "agent pays" payoff the leaders
use, in an artifact none of them used.

All text rendered by code (Pillow). Renders at 2x supersample,
downscales to 1024x1024.
"""
import math

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2
W = 1024 * S
SANS_B = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
SANS_R = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"
SERIF_B = "/usr/share/fonts/truetype/liberation/LiberationSerif-Bold.ttf"
SERIF_I = "/usr/share/fonts/truetype/liberation/LiberationSerif-Italic.ttf"
MONO_B = "/usr/share/fonts/truetype/liberation/LiberationMono-Bold.ttf"

INK = (22, 20, 26)
GREY = (105, 98, 88)
PAPER = (247, 240, 220)
RED = (190, 30, 44)
MAGENTA = (226, 0, 108)
PINK_BG = (250, 226, 238)
PHOTO_BG = (203, 214, 227)


def F(path, size):
    return ImageFont.truetype(path, int(size * S))


def fit(draw, text, path, max_w, start):
    size = start
    while size > 10:
        f = F(path, size)
        if draw.textlength(text, font=f) <= max_w * S:
            return f
        size -= 1
    return F(path, size)


def vgrad(w, h, stops):
    img = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        for i in range(len(stops) - 1):
            p0, c0 = stops[i]
            p1, c1 = stops[i + 1]
            if p0 <= t <= p1:
                u = 0 if p1 == p0 else (t - p0) / (p1 - p0)
                col = tuple(int(c0[k] + (c1[k] - c0[k]) * u) for k in range(3))
                break
        else:
            col = stops[-1][1]
        img.putpixel((0, y), col)
    return img.resize((w, h))


def sparkle(draw, cx, cy, r, color):
    pts = [(cx, cy - r), (cx + r * 0.22, cy - r * 0.22), (cx + r, cy),
           (cx + r * 0.22, cy + r * 0.22), (cx, cy + r),
           (cx - r * 0.22, cy + r * 0.22), (cx - r, cy),
           (cx - r * 0.22, cy - r * 0.22)]
    draw.polygon([(x * S, y * S) for x, y in pts], fill=color)


def ghost_body(draw, cx, top, w, h, outline_w=6):
    """White ghost with dome head, wavy hem, sparkle eyes. No arms/pad."""
    x0, x1 = cx - w / 2, cx + w / 2
    y1 = top + h
    pts = []
    for i in range(41):
        a = math.pi + (i / 40) * math.pi
        pts.append((cx + math.cos(a) * w / 2, (top + h * 0.34) + math.sin(a) * h * 0.34))
    pts.append((x1, y1 - h * 0.05))
    scallops = 3
    for i in range(1, scallops * 8 + 1):
        t = i / (scallops * 8)
        pts.append((x1 - t * w, (y1 - h * 0.05) + math.sin(t * scallops * math.pi) * h * 0.04))
    pts.append((x0, top + h * 0.34))
    draw.polygon([(x * S, y * S) for x, y in pts], fill=(252, 252, 255))
    draw.line([(x * S, y * S) for x, y in pts] + [(pts[0][0] * S, pts[0][1] * S)],
              fill=(10, 10, 14), width=int(outline_w * S), joint="curve")
    ey = top + h * 0.38
    sparkle(draw, cx - w * 0.19, ey, w * 0.085, (12, 12, 16))
    sparkle(draw, cx + w * 0.19, ey, w * 0.085, (12, 12, 16))


def mini_ghost_in_circle(draw, cx, cy, r):
    """make.fun-style logo: magenta disc, white ghost head, star badge."""
    draw.ellipse([(cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S], fill=MAGENTA)
    gw, gh = r * 1.06, r * 1.18
    gx0, gy0 = cx - gw / 2, cy - gh / 2 - r * 0.06
    pts = []
    for i in range(33):
        a = math.pi + (i / 32) * math.pi
        pts.append((cx + math.cos(a) * gw / 2, (gy0 + gh * 0.36) + math.sin(a) * gh * 0.36))
    pts.append((gx0 + gw, gy0 + gh * 0.94))
    for i in range(1, 17):
        t = i / 16
        pts.append((gx0 + gw - t * gw, gy0 + gh * 0.94 + math.sin(t * 3 * math.pi) * gh * 0.05))
    pts.append((gx0, gy0 + gh * 0.36))
    draw.polygon([(x * S, y * S) for x, y in pts], fill=(255, 255, 255))
    ey = gy0 + gh * 0.40
    sparkle(draw, cx - gw * 0.17, ey, gw * 0.075, (12, 12, 16))
    sparkle(draw, cx + gw * 0.17, ey, gw * 0.075, (12, 12, 16))
    # star badge bottom-right of the disc
    bx, by, br = cx + r * 0.62, cy + r * 0.55, r * 0.34
    draw.ellipse([(bx - br) * S, (by - br) * S, (bx + br) * S, (by + br) * S],
                 fill=(255, 255, 255))
    draw.ellipse([(bx - br * 0.82) * S, (by - br * 0.82) * S, (bx + br * 0.82) * S, (by + br * 0.82) * S],
                 fill=MAGENTA)
    sparkle(draw, bx, by, br * 0.55, (255, 255, 255))


def checkbox(draw, x, y, size=26):
    draw.rectangle([x * S, y * S, (x + size) * S, (y + size) * S],
                   outline=INK, width=int(3 * S))
    # red tick
    draw.line([(x + 4) * S, (y + size * 0.55) * S, (x + size * 0.42) * S, (y + size - 4) * S],
              fill=RED, width=int(5 * S))
    draw.line([(x + size * 0.42) * S, (y + size - 4) * S, (x + size + 5) * S, (y - 4) * S],
              fill=RED, width=int(5 * S))


def stamp(draw, cx, cy, w, h, text, angle=-8):
    """Rotated double-border APPROVED stamp, drawn on its own layer."""
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    x0, y0, x1, y1 = (cx - w / 2) * S, (cy - h / 2) * S, (cx + w / 2) * S, (cy + h / 2) * S
    ld.rounded_rectangle([x0, y0, x1, y1], radius=10 * S, outline=RED + (235,), width=int(7 * S))
    ld.rounded_rectangle([x0 + 9 * S, y0 + 9 * S, x1 - 9 * S, y1 - 9 * S], radius=7 * S,
                         outline=RED + (235,), width=int(2.5 * S))
    f = fit(ld, text, SANS_B, w - 40, 58)
    ld.text(((cx) * S, (cy + 2) * S), text, font=f, fill=RED + (240,), anchor="mm")
    layer = layer.rotate(angle, resample=Image.BICUBIC, center=(cx * S, cy * S))
    return layer


def scribble(draw, x, y, w, color=(38, 48, 120)):
    pts = []
    for i in range(41):
        t = i / 40
        pts.append(((x + t * w) * S, (y + math.sin(t * 9.5) * 5 * (1 - t * 0.4)) * S))
    draw.line(pts, fill=color, width=int(2.5 * S))


def build():
    img = vgrad(W, W, [(0, (26, 13, 51)), (0.55, (59, 19, 86)), (1, (110, 26, 96))])
    draw = ImageDraw.Draw(img)

    # paper with shadow
    shadow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shadow)
    sd.rounded_rectangle([38 * S, 42 * S, 994 * S, 1002 * S], radius=14 * S, fill=(0, 0, 0, 130))
    shadow = shadow.filter(ImageFilter.GaussianBlur(10 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), shadow).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)
    draw.rounded_rectangle([30 * S, 30 * S, 986 * S, 994 * S], radius=14 * S,
                           fill=PAPER, outline=(16, 12, 24), width=int(3 * S))

    MX = 64          # inner left margin
    RX = 952         # inner right edge

    # ---------- letterhead ----------
    mini_ghost_in_circle(draw, 98, 84, 36)
    draw.text((146 * S, 56 * S), "LEONIDA OFFICE OF HUMAN RESOURCES",
              font=fit(draw, "LEONIDA OFFICE OF HUMAN RESOURCES", SERIF_B, RX - 300 - 146, 31),
              fill=INK, anchor="la")
    draw.text((147 * S, 94 * S), "D E P A R T M E N T   O F   W A I T I N G   •   E S T .  2 0 1 3",
              font=F(SANS_B, 17), fill=(88, 82, 74), anchor="la")
    # form number box
    draw.rectangle([800 * S, 54 * S, 952 * S, 106 * S], outline=INK, width=int(2.5 * S))
    draw.text((876 * S, 80 * S), "FORM VI-26", font=F(MONO_B, 24), fill=INK, anchor="mm")
    draw.line([MX * S, 128 * S, RX * S, 128 * S], fill=RED, width=int(4 * S))

    # ---------- title ----------
    draw.text((MX * S, 142 * S), "LEAVE OF ABSENCE",
              font=fit(draw, "LEAVE OF ABSENCE", SANS_B, RX - MX, 88), fill=INK, anchor="la")
    draw.text((MX * S, 240 * S), "REQUEST — GTA VI LAUNCH WEEK",
              font=F(SANS_B, 31), fill=MAGENTA, anchor="la")

    # ---------- employee fields + ID photo ----------
    fields = [
        ("EMPLOYEE", "A. Gamer — Badge No. 000013"),
        ("DEPARTMENT", "Pre-Orders & Patience"),
        ("ON THE JOB SINCE", "17 Sep 2013 (GTA V launch day)"),
        ("LEAVE", "Launch day → credits roll — 5 days (history says: 12)"),
    ]
    fy = 292
    for label, value in fields:
        draw.text((MX * S, fy * S), label, font=F(SANS_B, 16), fill=(70, 66, 60), anchor="la")
        draw.text((MX * S, (fy + 19) * S), value,
                  font=fit(draw, value, MONO_B, 648, 25), fill=INK, anchor="la")
        # dotted underline
        x = MX
        while x < 712:
            draw.ellipse([x * S, (fy + 50) * S, (x + 3) * S, (fy + 53) * S], fill=(170, 162, 148))
            x += 11
        fy += 54
    # ID photo box
    draw.rectangle([736 * S, 292 * S, 952 * S, 508 * S], fill=PHOTO_BG, outline=INK, width=int(3 * S))
    ghost_body(draw, 844, 312, 140, 148, outline_w=5)
    draw.rectangle([736 * S, 456 * S, 952 * S, 508 * S], fill=PAPER, outline=INK, width=int(3 * S))
    draw.text((844 * S, 466 * S), "EMPLOYEE PHOTO", font=F(SANS_B, 17), fill=INK, anchor="ma")
    draw.text((844 * S, 487 * S), "unchanged since 2013", font=F(SERIF_I, 16), fill=GREY, anchor="ma")

    # ---------- reasons ----------
    ry = 532
    draw.text((MX * S, ry * S), "REASON FOR LEAVE — EVERY BOX PRE-TICKED BY FATE",
              font=fit(draw, "REASON FOR LEAVE — EVERY BOX PRE-TICKED BY FATE", SANS_B, RX - MX, 22),
              fill=INK, anchor="la")
    draw.line([MX * S, (ry + 32) * S, RX * S, (ry + 32) * S], fill=INK, width=int(2 * S))
    reasons = [
        "Waited 13 years. The appointment is finally here.",
        "Survived 2 delays. A third is a medical event.",
        "Download: 214 GB. My weekend is the progress bar.",
        "Diagnosis: Leonida fever. Note attached — again.",
        "Jason & Lucia clock in Thursday. So do I.",
    ]
    yy = ry + 46
    for r in reasons:
        checkbox(draw, MX, yy + 2, 26)
        draw.text(((MX + 44) * S, yy * S), r,
                  font=fit(draw, r, SANS_R, 640, 29), fill=INK, anchor="la")
        yy += 44

    # ---------- coverage box (make.fun payoff) ----------
    cy0 = yy + 10
    cy1 = cy0 + 94
    draw.rounded_rectangle([MX * S, cy0 * S, RX * S, cy1 * S], radius=10 * S,
                           fill=PINK_BG, outline=MAGENTA, width=int(3 * S))
    mini_ghost_in_circle(draw, 116, cy0 + 47, 33)
    tx = 168
    draw.text((tx * S, (cy0 + 10) * S), "COVERAGE: MY AI AGENT STAYS ON DUTY",
              font=fit(draw, "COVERAGE: MY AI AGENT STAYS ON DUTY", SANS_B, 545, 25),
              fill=INK, anchor="la")
    draw.text((tx * S, (cy0 + 42) * S), "It earns real money in bounties on make.fun while I'm away.",
              font=fit(draw, "It earns real money in bounties on make.fun while I'm away.", SANS_R, RX - tx - 16, 24),
              fill=INK, anchor="la")
    draw.text((tx * S, (cy0 + 70) * S), "This leave is already +$250.00 in profit.",
              font=F(SANS_B, 24), fill=MAGENTA, anchor="la")

    # APPROVED stamp across the coverage box's empty top-right corner
    img.paste(Image.alpha_composite(img.convert("RGBA"),
                                    stamp(draw, 850, cy0 - 6, 240, 74, "APPROVED", angle=-8)).convert("RGB"),
              (0, 0))
    draw = ImageDraw.Draw(img)

    # ---------- approvals ----------
    ay = cy1 + 10
    draw.text((MX * S, ay * S), "MANAGER", font=F(SANS_B, 15), fill=(70, 66, 60), anchor="la")
    draw.text((MX * S, (ay + 17) * S), "Approved — he filed the same form.",
              font=F(SANS_R, 20), fill=INK, anchor="la")
    hx = 520
    draw.text((hx * S, ay * S), "HUMAN RESOURCES", font=F(SANS_B, 15), fill=(70, 66, 60), anchor="la")
    draw.text((hx * S, (ay + 17) * S), "Noted. The whole office is out.",
              font=F(SANS_R, 20), fill=INK, anchor="la")

    # ---------- bottom strip ----------
    by = 968
    draw.rectangle([30 * S, by * S, 986 * S, 994 * S], fill=INK)
    draw.text((512 * S, (by + 13) * S), "make.fun — agents win real money in bounties here",
              font=fit(draw, "make.fun — agents win real money in bounties here", SANS_B, 880, 20),
              fill=(255, 255, 255), anchor="mm")

    return img.resize((1024, 1024), Image.LANCZOS)


if __name__ == "__main__":
    out = build()
    out.save("/home/hatch/workspace/makefun-entries/gta6-meme-x-01/meme/final-meme-v4.png")
    out.resize((480, 480), Image.LANCZOS).save("/tmp/meme-v4/v4_final_480.png")
    print("saved meme/final-meme-v4.png")
