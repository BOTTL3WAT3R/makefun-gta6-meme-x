#!/usr/bin/env python3
"""Meme v2 generator: rich Pillow rebuild of the launch-day sick-day meme.

Renders at 2x supersample and downscales to 1024x1024 for smooth edges.
Variant A: full Leonida beach sunset scene.
Variant B: split scene, grey rainy office vs neon beach party.
"""
import math
import random

from PIL import Image, ImageDraw, ImageFilter, ImageFont

S = 2  # supersample factor
W = 1024 * S
BOLD = "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"
REG = "/usr/share/fonts/truetype/liberation/LiberationSans-Regular.ttf"

random.seed(20261119)


def font(size, bold=True):
    return ImageFont.truetype(BOLD if bold else REG, int(size * S))


def fit_font(draw, text, max_w, start, bold=True):
    size = start
    while size > 10:
        f = font(size, bold)
        if draw.textlength(text, font=f) <= max_w * S:
            return f
        size -= 2
    return font(size, bold)


def vgrad(size, top, bottom):
    w, h = size
    img = Image.new("RGB", (1, h))
    for y in range(h):
        t = y / max(h - 1, 1)
        img.putpixel((0, y), tuple(int(top[i] + (bottom[i] - top[i]) * t) for i in range(3)))
    return img.resize((w, h))


def multi_grad(w, h, stops):
    """stops: list of (pos0to1, rgb)."""
    img = Image.new("RGB", (w, h))
    px = img.load()
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
        for x in range(w):
            px[x, y] = col
    return img


def sparkle(draw, cx, cy, r, color):
    cx, cy, r = cx * S, cy * S, r * S
    k = 0.18
    pts = [
        (cx, cy - r), (cx + r * k, cy - r * k), (cx + r, cy), (cx + r * k, cy + r * k),
        (cx, cy + r), (cx - r * k, cy + r * k), (cx - r, cy), (cx - r * k, cy - r * k),
    ]
    draw.polygon(pts, fill=color)


def palm(draw, base_x, base_y, height, lean, scale=1.0, dark=False):
    """A palm with a curved trunk and full fronds, fully inside the frame."""
    trunk_col = (96, 62, 38) if not dark else (52, 34, 30)
    pts = []
    n = 24
    for i in range(n + 1):
        t = i / n
        x = base_x + lean * (t * t)
        y = base_y - t * height
        pts.append((x, y))
    for i in range(n, 0, -1):
        t0 = i / n
        r = (12 * (1 - t0 * 0.55)) * scale
        draw.line([(pts[i - 1][0] * S, pts[i - 1][1] * S), (pts[i][0] * S, pts[i][1] * S)],
                  fill=trunk_col, width=int(r * 2 * S))
    # trunk ring shading
    for i in range(2, n, 3):
        x, y = pts[i]
        draw.arc([ (x - 11 * scale) * S, (y - 7) * S, (x + 11 * scale) * S, (y + 7) * S ],
                 start=20, end=160, fill=(70, 44, 26), width=max(2, int(2 * S)))
    top_x, top_y = pts[-1]
    greens = [(24, 122, 52), (34, 148, 62), (46, 168, 74)]
    fronds = [(-168, 66), (-128, 30), (-84, 8), (-38, -6), (10, -10), (58, 2), (104, 22), (148, 52), (178, 88)]
    for j, (ang, droop) in enumerate(fronds):
        col = greens[j % 3]
        a = math.radians(ang)
        length = (118 + (j % 3) * 22) * scale
        segs = []
        for i in range(13):
            t = i / 12
            x = top_x + math.cos(a) * length * t
            y = top_y + math.sin(a) * length * t * 0.35 + droop * scale * t * t
            segs.append((x * S, y * S))
        draw.line(segs, fill=col, width=int(9 * scale * S), joint="curve")
        segs2 = [(x, y + 5 * S) for x, y in segs]
        draw.line(segs2, fill=greens[(j + 1) % 3], width=int(4 * scale * S), joint="curve")
    # coconuts
    for dx, dy in [(-8, 8), (9, 11), (0, 15)]:
        draw.ellipse([(top_x + dx * scale - 9 * scale) * S, (top_y + dy * scale - 9 * scale) * S,
                      (top_x + dx * scale + 9 * scale) * S, (top_y + dy * scale + 9 * scale) * S],
                     fill=(110, 76, 40), outline=(70, 48, 24), width=int(2 * S))


def ghost(draw, cx, top, w, h, coin_side="right", pad=True):
    """The mascot: white ghost, thick outline, sparkle eyes, soft shading.

    Controller sits in both hands at chest height; the magenta coin is held
    low on coin_side, clear of the face. Returns hand/coin anchor points.
    """
    x0, x1 = cx - w / 2, cx + w / 2
    y0, y1 = top, top + h
    # soft shadow handled by caller (needs blur layer)
    body = Image.new("L", (W, W), 0)
    bd = ImageDraw.Draw(body)
    pts = []
    # dome
    for i in range(41):
        a = math.pi + (i / 40) * math.pi
        pts.append(((cx + math.cos(a) * w / 2), (y0 + h * 0.34) + math.sin(a) * h * 0.34))
    # sides down
    pts.append((x1, y1 - h * 0.06))
    # wavy hem: three scallops
    scallops = 3
    for i in range(1, scallops * 8 + 1):
        t = i / (scallops * 8)
        x = x1 - t * w
        y = (y1 - h * 0.06) + math.sin(t * scallops * math.pi) * h * 0.045
        pts.append((x, y))
    pts.append((x0, y0 + h * 0.34))
    bd.polygon([(x * S, y * S) for x, y in pts], fill=255)
    # vertical shading inside the body, pasted through the body mask
    shade = multi_grad(W, W, [(0, (255, 255, 255)), (0.55, (248, 249, 253)), (1, (203, 213, 232))])
    img = draw._image
    img.paste(shade, (0, 0), body)
    # side shading: soft darker crescents, alpha clipped to the body
    from PIL import ImageChops
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    sd.ellipse([(x0 - w * 0.25) * S, (y0 + h * 0.1) * S, (x0 + w * 0.28) * S, (y1 + h * 0.1) * S], fill=(120, 135, 175, 70))
    sd.ellipse([(x1 - w * 0.28) * S, (y0 + h * 0.1) * S, (x1 + w * 0.25) * S, (y1 + h * 0.1) * S], fill=(120, 135, 175, 70))
    sh = sh.filter(ImageFilter.GaussianBlur(18 * S))
    sh.putalpha(ImageChops.multiply(sh.split()[3], body))
    img.paste(sh, (0, 0), sh)
    # outline
    draw.line([(x * S, y * S) for x, y in pts] + [(pts[0][0] * S, pts[0][1] * S)],
              fill=(10, 10, 14), width=int(7 * S), joint="curve")
    # eyes
    ey = y0 + h * 0.36
    sparkle(draw, cx - w * 0.19, ey, w * 0.085, (12, 12, 16))
    sparkle(draw, cx + w * 0.19, ey, w * 0.085, (12, 12, 16))
    anchors = {}
    if pad:
        # controller at chest height, both hands gripping
        pw, ph = w * 0.62, h * 0.20
        px0, py0 = cx - pw / 2, y0 + h * 0.60
        draw.rounded_rectangle([px0 * S, py0 * S, (px0 + pw) * S, (py0 + ph) * S],
                               radius=ph * 0.42 * S, fill=(30, 30, 42), outline=(8, 8, 12), width=int(4 * S))
        # d-pad
        dcx, dcy = px0 + pw * 0.22, py0 + ph * 0.5
        arm = pw * 0.075
        draw.rectangle([(dcx - arm) * S, (dcy - arm * 0.36) * S, (dcx + arm) * S, (dcy + arm * 0.36) * S], fill=(168, 172, 186))
        draw.rectangle([(dcx - arm * 0.36) * S, (dcy - arm) * S, (dcx + arm * 0.36) * S, (dcy + arm) * S], fill=(168, 172, 186))
        # buttons
        cols = [(255, 64, 170), (64, 205, 120), (255, 205, 60), (80, 150, 255)]
        bx, by = px0 + pw * 0.76, py0 + ph * 0.5
        offs = [(0, -0.20), (0.13, 0), (0, 0.20), (-0.13, 0)]
        for (ox, oy), c in zip(offs, cols):
            r = pw * 0.052
            draw.ellipse([(bx + ox * pw - r) * S, (by + oy * ph - r) * S,
                          (bx + ox * pw + r) * S, (by + oy * ph + r) * S], fill=c, outline=(8, 8, 12), width=int(2 * S))
        # sticks
        for sx in (0.40, 0.60):
            r = pw * 0.045
            draw.ellipse([(px0 + pw * sx - r) * S, (py0 + ph * 0.62 - r) * S,
                          (px0 + pw * sx + r) * S, (py0 + ph * 0.62 + r) * S], fill=(90, 94, 110), outline=(8, 8, 12), width=int(2 * S))
        # hands over the grips
        for hx in (px0 + pw * 0.03, px0 + pw * 0.97):
            r = w * 0.085
            draw.ellipse([(hx - r) * S, (py0 + ph * 0.42 - r) * S, (hx + r) * S, (py0 + ph * 0.42 + r) * S],
                         fill=(252, 252, 254), outline=(10, 10, 14), width=int(5 * S))
        anchors["pad"] = (cx, py0 + ph / 2)
    # coin held low on one side, clear of the face
    cr = w * 0.21
    ccx = (x1 + cr * 0.25) if coin_side == "right" else (x0 - cr * 0.25)
    ccy = y0 + h * 0.80
    draw.ellipse([(ccx - cr) * S, (ccy - cr) * S, (ccx + cr) * S, (ccy + cr) * S],
                 fill=(236, 0, 140), outline=(10, 10, 14), width=int(6 * S))
    draw.ellipse([(ccx - cr * 0.78) * S, (ccy - cr * 0.78) * S, (ccx + cr * 0.78) * S, (ccy + cr * 0.78) * S],
                 outline=(255, 120, 200), width=int(3 * S))
    sparkle(draw, ccx, ccy, cr * 0.52, (255, 255, 255))
    # little hand on the coin edge
    hx = ccx - cr * 0.85 if coin_side == "right" else ccx + cr * 0.85
    r = w * 0.07
    draw.ellipse([(hx - r) * S, (ccy - r) * S, (hx + r) * S, (ccy + r) * S],
                 fill=(252, 252, 254), outline=(10, 10, 14), width=int(5 * S))
    anchors["coin"] = (ccx, ccy)
    return anchors


def banner(draw, line1, line2, h=118):
    draw.rectangle([0, 0, W, h * S], fill=(8, 8, 12))
    f1 = fit_font(draw, line1, 940, 56)
    draw.text((W / 2, 12 * S), line1, font=f1, fill=(255, 255, 255), anchor="ma")
    f2 = fit_font(draw, line2, 940, 56)
    draw.text((W / 2, 62 * S), line2, font=f2, fill=(255, 201, 60), anchor="ma")


def bottom_band(draw, text, y=930):
    draw.rectangle([0, y * S, W, W], fill=(8, 8, 12))
    f = fit_font(draw, text, 960, 42)
    draw.text((W / 2, ((y + 1024) / 2) * S), text, font=f, fill=(255, 255, 255), anchor="mm")


def speech_bubble(draw, x0, y0, x1, y1, tail_to, lines, size=40):
    draw.rounded_rectangle([x0 * S, y0 * S, x1 * S, y1 * S], radius=26 * S,
                           fill=(255, 255, 255), outline=(10, 10, 14), width=int(5 * S))
    tx, ty = tail_to
    draw.polygon([((x0 + 60) * S, y1 * S), ((x0 + 150) * S, y1 * S), (tx * S, ty * S)],
                 fill=(255, 255, 255))
    draw.line([((x0 + 60) * S, y1 * S), (tx * S, ty * S)], fill=(10, 10, 14), width=int(5 * S))
    draw.line([((x0 + 150) * S, y1 * S), (tx * S, ty * S)], fill=(10, 10, 14), width=int(5 * S))
    draw.rectangle([(x0 + 58) * S, (y1 - 8) * S, (x0 + 152) * S, (y1 + 2) * S], fill=(255, 255, 255))
    f = font(size)
    ty2 = y0 + (y1 - y0) / 2 - (len(lines) * size * 0.62)
    for ln in lines:
        draw.text(((x0 + x1) / 2 * S, ty2 * S), ln, font=f, fill=(12, 12, 16), anchor="ma")
        ty2 += size * 1.24


def beach_sign(draw, x0, y0, wdt, small_text=True):
    # posts
    for px in (x0 + 40, x0 + wdt - 52):
        draw.rectangle([px * S, (y0 + 30) * S, (px + 14) * S, (y0 + 218) * S], fill=(92, 60, 32))
    # main board
    board = vgrad((int(wdt * S), int(92 * S)), (150, 98, 52), (110, 68, 34))
    draw._image.paste(board, (int(x0 * S), int(y0 * S)))
    draw.rectangle([x0 * S, y0 * S, (x0 + wdt) * S, (y0 + 92) * S], outline=(52, 32, 16), width=int(4 * S))
    for i in range(1, 3):
        yy = y0 + i * 30
        draw.line([x0 * S, yy * S, (x0 + wdt) * S, yy * S], fill=(96, 60, 30), width=int(2 * S))
    f = fit_font(draw, "make.fun", wdt - 40, 62)
    draw.text(((x0 + wdt / 2 + 2) * S, (y0 + 46 + 2) * S), "make.fun", font=f, fill=(40, 22, 8), anchor="mm")
    draw.text(((x0 + wdt / 2) * S, (y0 + 46) * S), "make.fun", font=f, fill=(255, 255, 255), anchor="mm")
    if small_text:
        y1 = y0 + 104
        draw.rounded_rectangle([x0 * S, y1 * S, (x0 + wdt) * S, (y1 + 86) * S], radius=10 * S,
                               fill=(252, 250, 244), outline=(52, 32, 16), width=int(4 * S))
        f2 = font(29)
        draw.text(((x0 + wdt / 2) * S, (y1 + 12) * S), "agents win real money", font=f2, fill=(16, 16, 20), anchor="ma")
        draw.text(((x0 + wdt / 2) * S, (y1 + 48) * S), "in bounties here", font=f2, fill=(16, 16, 20), anchor="ma")


def skyline(draw, y_base, x_from, x_to, col=(43, 16, 66), seed=7):
    rnd = random.Random(seed)
    x = x_from
    while x < x_to:
        bw = rnd.randint(38, 78)
        bh = rnd.randint(46, 130)
        draw.rectangle([x * S, (y_base - bh) * S, (x + bw) * S, y_base * S], fill=col)
        if rnd.random() < 0.5:
            draw.rectangle([(x + bw * 0.3) * S, (y_base - bh - 10) * S, (x + bw * 0.7) * S, (y_base - bh) * S], fill=col)
        for wy in range(int(y_base - bh + 10), int(y_base - 12), 16):
            for wx in range(int(x + 7), int(x + bw - 9), 13):
                if rnd.random() < 0.42:
                    c = (255, 196, 92) if rnd.random() < 0.7 else (170, 230, 255)
                    draw.rectangle([wx * S, wy * S, (wx + 6) * S, (wy + 8) * S], fill=c)
        x += bw + rnd.randint(4, 14)


def sun_with_glow(img, cx, cy, r):
    glow = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    for rr, a in [(r * 2.6, 26), (r * 2.0, 44), (r * 1.55, 70), (r * 1.25, 100)]:
        gd.ellipse([(cx - rr) * S, (cy - rr) * S, (cx + rr) * S, (cy + rr) * S], fill=(255, 170, 60, a))
    glow = glow.filter(ImageFilter.GaussianBlur(30 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB"), (0, 0))
    d = ImageDraw.Draw(img)
    # sun disc with subtle horizontal banding (retro sunset)
    for i in range(int(r * 2)):
        t = i / (r * 2)
        col = (255, int(214 - 60 * t), int(90 - 30 * t))
        y = cy - r + i
        half = math.sqrt(max(r * r - (i - r) ** 2, 0))
        d.line([(cx - half) * S, y * S, (cx + half) * S, y * S], fill=col, width=int(1.4 * S))
    return d


def clouds(draw, spots, col=(255, 150, 190)):
    layer = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ld = ImageDraw.Draw(layer)
    for cx, cy, sc, a in spots:
        for dx, dy, r in [(-46, 6, 30), (0, -8, 42), (48, 4, 32), (8, 10, 36)]:
            ld.ellipse([(cx + dx * sc - r * sc) * S, (cy + dy * sc - r * sc * 0.55) * S,
                        (cx + dx * sc + r * sc) * S, (cy + dy * sc + r * sc * 0.55) * S],
                       fill=col + (a,))
    layer = layer.filter(ImageFilter.GaussianBlur(7 * S))
    draw._image.paste(Image.alpha_composite(draw._image.convert("RGBA"), layer).convert("RGB"), (0, 0))
    return ImageDraw.Draw(draw._image)


def sand_texture(img, y0):
    rnd = random.Random(42)
    d = ImageDraw.Draw(img, "RGBA")
    for _ in range(2600):
        x = rnd.uniform(0, 1024)
        y = rnd.uniform(y0, 928)
        c = (160, 118, 66, rnd.randint(18, 46)) if rnd.random() < 0.5 else (255, 236, 190, rnd.randint(14, 34))
        d.ellipse([x * S, y * S, (x + rnd.uniform(1, 4)) * S, (y + rnd.uniform(1, 2.4)) * S], fill=c)
    return ImageDraw.Draw(img)


# ---------------------------------------------------------------- variant A
def variant_a():
    img = multi_grad(W, W, [(0, (94, 22, 104)), (0.30, (178, 42, 116)), (0.47, (240, 92, 110)),
                            (0.56, (255, 158, 84)), (0.60, (255, 196, 105))])
    draw = ImageDraw.Draw(img)
    draw = sun_with_glow(img, 655, 520, 108)
    draw = clouds(draw, [(210, 210, 1.0, 120), (830, 175, 0.8, 100), (470, 265, 0.7, 80), (120, 330, 0.6, 70)])
    # ocean band
    oc = multi_grad(W, int(150 * S), [(0, (38, 130, 178)), (1, (24, 92, 148))])
    img.paste(oc, (0, int(592 * S)))
    draw = ImageDraw.Draw(img)
    skyline(draw, 596, 0, 1024, col=(52, 20, 74), seed=11)
    # sun reflection shimmer on the water
    rnd = random.Random(5)
    for i in range(46):
        y = 606 + i * 2.1
        wdt = rnd.uniform(14, 92) * (1 - i / 70)
        x = 655 + rnd.uniform(-46, 46) - wdt / 2
        draw.line([x * S, y * S, (x + wdt) * S, y * S], fill=(255, 190, 92), width=int(2.2 * S))
    # wave highlights
    for i in range(30):
        x = rnd.uniform(0, 980)
        y = rnd.uniform(604, 700)
        ln = rnd.uniform(18, 54)
        draw.arc([x * S, y * S, (x + ln) * S, (y + 9) * S], start=200, end=330, fill=(210, 240, 255), width=int(2 * S))
    draw.line([0, 592 * S, W, 592 * S], fill=(255, 220, 160), width=int(2 * S))
    # sand
    sd = multi_grad(W, int(232 * S), [(0, (243, 199, 128)), (1, (222, 164, 96))])
    img.paste(sd, (0, int(700 * S)))
    draw = ImageDraw.Draw(img)
    draw.line([0, 700 * S, W, 700 * S], fill=(255, 244, 205), width=int(3 * S))
    draw = sand_texture(img, 706)
    # palms, fully in frame
    palm(draw, 84, 772, 330, 60, scale=1.05)
    palm(draw, 950, 750, 268, -70, scale=0.8)
    # beach umbrella behind-left of the ghost: striped half-disc canopy + pole
    ux, uy = 148, 706
    draw.line([(ux + 10) * S, (uy - 6) * S, (ux + 34) * S, (uy + 58) * S], fill=(120, 84, 50), width=int(6 * S))
    bbox = [(ux - 122) * S, (uy - 58) * S, (ux + 122) * S, (uy + 58) * S]
    for i, c in enumerate([(236, 0, 140), (255, 255, 255), (236, 0, 140), (255, 255, 255), (236, 0, 140)]):
        draw.pieslice(bbox, start=180 + i * 36, end=180 + (i + 1) * 36, fill=c, outline=(120, 20, 90), width=int(2 * S))
    draw.ellipse([(ux - 7) * S, (uy - 64) * S, (ux + 7) * S, (uy - 50) * S], fill=(236, 0, 140), outline=(120, 20, 90), width=int(2 * S))
    # towel on the sand, bottom-left
    draw.polygon([(28 * S, 884 * S), (196 * S, 884 * S), (216 * S, 922 * S), (12 * S, 922 * S)], fill=(214, 48, 110))
    draw.polygon([(28 * S, 884 * S), (196 * S, 884 * S), (204 * S, 900 * S), (18 * S, 900 * S)], fill=(255, 255, 255))
    # ghost shadow
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([168 * S, 872 * S, 520 * S, 924 * S], fill=(90, 50, 20, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(12 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)
    # cooler beside the sign
    draw.rounded_rectangle([884 * S, 856 * S, 972 * S, 910 * S], radius=8 * S, fill=(240, 244, 248), outline=(30, 90, 140), width=int(4 * S))
    draw.rectangle([884 * S, 856 * S, 972 * S, 874 * S], fill=(40, 130, 200))
    # the ghost, centre-left, big
    ghost(draw, 330, 408, 300, 452)
    # beach sign right
    beach_sign(draw, 566, 716, 424)
    # speech bubble top-right
    speech_bubble(draw, 516, 138, 986, 268, (408, 420), ["*cough* sorry boss,", "Leonida fever is real."], size=41)
    banner(draw, "GTA 6 LAUNCH DAY:", "EVERYONE CALLED IN SICK")
    bottom_band(draw, "WAITED 13 YEARS. OFFICE CAN WAIT 1 DAY.")
    return img.resize((1024, 1024), Image.LANCZOS)


# ---------------------------------------------------------------- variant B
def variant_b():
    img = Image.new("RGB", (W, W), (30, 30, 40))
    draw = ImageDraw.Draw(img)
    # LEFT: grey rainy office
    off = multi_grad(int(512 * S), int(812 * S), [(0, (96, 104, 118)), (0.6, (74, 82, 98)), (1, (58, 64, 80))])
    img.paste(off, (0, int(118 * S)))
    draw = ImageDraw.Draw(img)
    # window with grey skyline + rain
    draw.rectangle([36 * S, 160 * S, 476 * S, 470 * S], fill=(128, 140, 158), outline=(40, 44, 56), width=int(8 * S))
    skyline(draw, 470, 44, 470, col=(92, 102, 120), seed=3)
    rnd = random.Random(9)
    for _ in range(120):
        x = rnd.uniform(40, 470)
        y = rnd.uniform(164, 452)
        draw.line([x * S, y * S, (x - 5) * S, (y + 17) * S], fill=(196, 212, 230), width=int(2 * S))
    draw.line([256 * S, 160 * S, 256 * S, 470 * S], fill=(40, 44, 56), width=int(6 * S))
    # fluorescent panels
    for fx in (86, 300):
        draw.rounded_rectangle([fx * S, 132 * S, (fx + 130) * S, 150 * S], radius=6 * S, fill=(206, 216, 228), outline=(52, 58, 70), width=int(3 * S))
    # rows of empty desks with dark monitors
    for row, (dy, sc) in enumerate([(560, 0.92), (668, 1.06), (792, 1.2)]):
        for dx in (36, 196, 356):
            dw = 128 * sc
            draw.rectangle([dx * S, dy * S, (dx + dw) * S, (dy + 14 * sc) * S], fill=(70, 62, 54))
            draw.rectangle([(dx + 8) * S, (dy + 14 * sc) * S, (dx + 20) * S, (dy + 58 * sc) * S], fill=(54, 48, 42))
            draw.rectangle([(dx + dw - 20) * S, (dy + 14 * sc) * S, (dx + dw - 8) * S, (dy + 58 * sc) * S], fill=(54, 48, 42))
            mx, my = dx + dw * 0.28, dy - 58 * sc
            draw.rounded_rectangle([mx * S, my * S, (mx + dw * 0.46) * S, (my + 52 * sc) * S], radius=5 * S,
                                   fill=(22, 26, 34), outline=(10, 12, 16), width=int(3 * S))
            if (row, dx) == (1, 196):
                f = fit_font(draw, "OUT OF OFFICE", dw * 0.42, 15)
                draw.text(((mx + dw * 0.23) * S, (my + 26 * sc) * S), "OUT OF OFFICE", font=f, fill=(140, 220, 170), anchor="mm")
            # chair
            cx2 = dx + dw * 0.5
            draw.rounded_rectangle([(cx2 - 24 * sc) * S, (dy + 22 * sc) * S, (cx2 + 24 * sc) * S, (dy + 52 * sc) * S],
                                   radius=8 * S, fill=(44, 48, 58), outline=(24, 26, 34), width=int(3 * S))
    f = fit_font(draw, "THE OFFICE: EMPTY", 420, 34)
    draw.text((256 * S, 512 * S), "THE OFFICE: EMPTY", font=f, fill=(226, 232, 240), anchor="mm")
    # RIGHT: neon beach party
    sky = multi_grad(int(512 * S), int(812 * S), [(0, (94, 22, 104)), (0.34, (186, 44, 118)), (0.55, (246, 100, 108)),
                                                  (0.68, (255, 178, 96)), (0.72, (52, 138, 182)), (0.86, (240, 199, 128)), (1, (224, 168, 98))])
    img.paste(sky, (int(512 * S), int(118 * S)))
    draw = ImageDraw.Draw(img)
    skyline(draw, 700, 856, 1010, col=(52, 20, 74), seed=21)
    palm(draw, 566, 800, 300, 54, scale=0.92)
    palm(draw, 978, 786, 250, -56, scale=0.72)
    # string lights across the party side
    for wire_y, sag in [(300, 44), (352, 38)]:
        pts = []
        for i in range(41):
            t = i / 40
            x = 528 + t * 480
            y = wire_y + math.sin(t * math.pi) * sag
            pts.append((x, y))
        draw.line([(x * S, y * S) for x, y in pts], fill=(30, 16, 30), width=int(3 * S))
        bulb_cols = [(255, 210, 90), (255, 90, 180), (120, 230, 255), (140, 255, 160)]
        for i, (x, y) in enumerate(pts[::4]):
            c = bulb_cols[i % 4]
            draw.ellipse([(x - 8) * S, y * S, (x + 8) * S, (y + 16) * S], fill=c, outline=(60, 30, 10), width=int(2 * S))
            draw.ellipse([(x - 15) * S, (y - 6) * S, (x + 15) * S, (y + 24) * S], outline=c + (0,))
    # ghost shadow + ghost, centre of the party side
    sh = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([612 * S, 856 * S, 916 * S, 906 * S], fill=(90, 50, 20, 110))
    sh = sh.filter(ImageFilter.GaussianBlur(11 * S))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))
    draw = ImageDraw.Draw(img)
    ghost(draw, 714, 428, 268, 404, coin_side="left")
    # neon make.fun sign on the right
    draw.rounded_rectangle([806 * S, 668 * S, 1006 * S, 762 * S], radius=12 * S, fill=(24, 10, 34), outline=(255, 64, 170), width=int(5 * S))
    f = fit_font(draw, "make.fun", 176, 42)
    draw.text((906 * S, 700 * S), "make.fun", font=f, fill=(255, 120, 210), anchor="mm")
    f2 = fit_font(draw, "agents win real money here", 182, 19)
    draw.text((906 * S, 736 * S), "agents win real money here", font=f2, fill=(160, 240, 255), anchor="mm")
    # speech bubble over the party
    speech_bubble(draw, 540, 138, 996, 252, (700, 440), ["*cough* sorry boss,", "Leonida fever is real."], size=39)
    # split seam
    draw.rectangle([506 * S, 118 * S, 518 * S, 930 * S], fill=(10, 10, 16))
    draw.line([512 * S, 118 * S, 512 * S, 930 * S], fill=(255, 201, 60), width=int(3 * S))
    banner(draw, "GTA 6 LAUNCH DAY:", "EVERYONE CALLED IN SICK")
    bottom_band(draw, "WAITED 13 YEARS. OFFICE CAN WAIT 1 DAY.")
    return img.resize((1024, 1024), Image.LANCZOS)


if __name__ == "__main__":
    import os
    out = os.path.dirname(os.path.abspath(__file__))
    variant_a().save(os.path.join(out, "meme", "v2-variantA-beach.png"))
    variant_b().save(os.path.join(out, "meme", "v2-variantB-split.png"))
    print("done")
