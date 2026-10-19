#!/usr/bin/env python3
"""Draw the blog's in-body diagrams into img/blog/<name>.webp.

Every diagram is described once as data and drawn twice: a wide desktop
layout and a stacked `-mobile` layout that the article serves below 640px.
Boxes size themselves to their text, and saving fails when the smallest text
would render under 12 CSS px in the article column (760px on desktop, 343px
on a 375px phone), so a label can never quietly shrink out of reach.
Colors come from the site tokens in styles.css. Output is deterministic.

    python3 scripts/build_blog_diagrams.py            # all diagrams
    python3 scripts/build_blog_diagrams.py remote     # names containing "remote"
"""

from __future__ import annotations

import subprocess
import sys
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

from PIL import Image, ImageDraw, ImageFont

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / "img" / "blog"

PAPER = (245, 244, 237)      # --parchment
CARD = (250, 249, 245)       # --ivory
LINE = (216, 213, 200)       # --line
INK = (20, 20, 19)           # --near-black
DIM = (61, 61, 58)           # --dark-warm
MUTED = (107, 106, 100)      # --stone
BRAND = (27, 54, 93)         # --brand
TINT = (238, 242, 247)       # --brand-tint
GREEN = (13, 125, 77)        # --green
ON_BRAND = (245, 244, 237)

DESK_COL, PHONE_COL, MIN_CSS_PX = 760, 343, 12
# `out` is the saved pixels per layout unit, at twice the CSS size it shows at:
# desktop layouts show at 0.68 of their units (capped by the column), phone
# layouts on a 680 canvas show at 340 CSS px. `k` scales the spacing.
DESK = {"title": 26, "line": 22, "note": 22, "k": 1.0, "out": 1.36}
PHONE = {"title": 31, "line": 26, "note": 26, "k": 1.0, "out": 1}
PAD = 56

SS = 3  # supersampling factor
FONT_DIR = Path.home() / "Library" / "Fonts"
FONT_FILES = {
    "regular": ["JetBrainsMono-Regular.ttf", "/System/Library/Fonts/Menlo.ttc"],
    "medium": ["JetBrainsMono-Medium.ttf", "JetBrainsMono-Bold.ttf", "/System/Library/Fonts/Menlo.ttc"],
}
_fonts: dict[tuple[str, int], ImageFont.FreeTypeFont] = {}


def font(size: int, weight: str = "regular") -> ImageFont.FreeTypeFont:
    key = (weight, size)
    if key not in _fonts:
        for name in FONT_FILES[weight]:
            path = Path(name) if name.startswith("/") else FONT_DIR / name
            if path.exists():
                _fonts[key] = ImageFont.truetype(str(path), size * SS)
                break
        else:
            raise SystemExit("JetBrains Mono or Menlo is required to draw diagrams")
    return _fonts[key]


def tw(s: str, size: int, weight: str = "regular") -> float:
    return font(size, weight).getlength(s) / SS


class Canvas:
    def __init__(self, w: int, h: int, column: int, out: int = 1):
        self.w, self.h, self.column, self.out = int(w), int(h), column, out
        self.min_font = 99
        self.im = Image.new("RGB", (self.w * SS, self.h * SS), PAPER)
        self.d = ImageDraw.Draw(self.im)

    def box(self, x, y, w, h, fill=CARD, stroke=LINE, r=14, width=2):
        self.d.rounded_rectangle([x * SS, y * SS, (x + w) * SS, (y + h) * SS], r * SS,
                                 fill=fill, outline=stroke, width=int(width * SS))

    def text(self, x, y, s, size, color=INK, anchor="mm", weight="regular"):
        self.min_font = min(self.min_font, size)
        self.d.text((x * SS, y * SS), s, font=font(size, weight), fill=color, anchor=anchor)

    def line(self, pts, color=BRAND, width=2.5, dash=0):
        pts = [(x * SS, y * SS) for x, y in pts]
        if not dash:
            self.d.line(pts, fill=color, width=int(width * SS), joint="curve")
            return
        for (x1, y1), (x2, y2) in zip(pts, pts[1:]):
            length = ((x2 - x1) ** 2 + (y2 - y1) ** 2) ** 0.5 or 1
            step = dash * SS * 2
            t = 0.0
            while t < length:
                a, b = t / length, min(1.0, (t + dash * SS) / length)
                self.d.line([(x1 + (x2 - x1) * a, y1 + (y2 - y1) * a),
                             (x1 + (x2 - x1) * b, y1 + (y2 - y1) * b)], fill=color, width=int(width * SS))
                t += step

    def arrow(self, pts, color=BRAND, width=2.5, head=11, dash=0, both=False):
        self.line(pts, color, width, dash)
        self._head(pts[-2], pts[-1], color, head)
        if both:
            self._head(pts[1], pts[0], color, head)

    def _head(self, a, b, color, head):
        (x1, y1), (x2, y2) = a, b
        dx, dy = x2 - x1, y2 - y1
        n = (dx * dx + dy * dy) ** 0.5 or 1
        ux, uy = dx / n, dy / n
        px, py = -uy, ux
        pts = [(x2, y2), (x2 - ux * head + px * head * 0.6, y2 - uy * head + py * head * 0.6),
               (x2 - ux * head - px * head * 0.6, y2 - uy * head - py * head * 0.6)]
        self.d.polygon([(x * SS, y * SS) for x, y in pts], fill=color)

    def save(self, name: str):
        css_w = min(self.w * self.out / 2, self.column)
        css = self.min_font * css_w / self.w
        if css < MIN_CSS_PX:
            raise SystemExit(f"{name}: smallest text renders at {css:.1f}px in a {self.column}px column")
        OUT.mkdir(parents=True, exist_ok=True)
        im = self.im.resize((round(self.w * self.out), round(self.h * self.out)), Image.LANCZOS)
        with tempfile.TemporaryDirectory() as tmp:
            png = Path(tmp) / f"{name}.png"
            im.save(png)
            subprocess.run(["cwebp", "-quiet", "-q", "90", "-metadata", "none", str(png),
                            "-o", str(OUT / f"{name}.webp")], check=True)
        print(f"img/blog/{name}.webp shown at {css_w:.0f}px wide, smallest text {css:.1f}px")


# ---------------------------------------------------------------- nodes

@dataclass
class Node:
    title: str
    lines: list[str] = field(default_factory=list)
    style: str = "card"  # card | brand | tint | quiet


STYLES = {
    "card": (CARD, LINE, INK, DIM),
    "brand": (BRAND, BRAND, ON_BRAND, (214, 223, 236)),
    "tint": (TINT, (196, 208, 224), BRAND, DIM),
    "quiet": (PAPER, LINE, MUTED, MUTED),
}


def node_w(n: Node, f: dict) -> float:
    return max([tw(n.title, f["title"], "medium")] + [tw(s, f["line"]) for s in n.lines]) + 52 * f["k"]


def node_h(n: Node, f: dict) -> float:
    return 44 * f["k"] + f["title"] + (len(n.lines) * (f["line"] + 12 * f["k"]) + 6 * f["k"] if n.lines else 0)


def draw_node(c: Canvas, n: Node, x, y, w, h, f: dict):
    fill, stroke, tcol, lcol = STYLES[n.style]
    c.box(x, y, w, h, fill=fill, stroke=stroke, r=14 * f["k"], width=2 * f["k"])
    total = f["title"] + (len(n.lines) * (f["line"] + 12 * f["k"]) + 6 * f["k"] if n.lines else 0)
    ty = y + (h - total) / 2 + f["title"] / 2
    c.text(x + w / 2, ty, n.title, f["title"], color=tcol, weight="medium")
    ly = ty + f["title"] / 2 + 18 * f["k"] + f["line"] / 2
    for s in n.lines:
        c.text(x + w / 2, ly, s, f["line"], color=lcol)
        ly += f["line"] + 12 * f["k"]


def wrap(s: str, size: int, width: float) -> list[str]:
    out, cur = [], ""
    for word in s.split():
        trial = (cur + " " + word).strip()
        if cur and tw(trial, size) > width:
            out.append(cur)
            cur = word
        else:
            cur = trial
    return out + ([cur] if cur else [])


def fits_phone(name: str, items: list[Node], width: float):
    for it in items:
        if node_w(it, PHONE) > width:
            raise SystemExit(f"{name}: '{it.title}' is too wide for the phone layout")


# ---------------------------------------------------------------- layouts

def flow(name: str, nodes: list[Node], *, back: str | None = None, both: bool = False, gap: int = 72,
         equal_width: bool = True):
    """A left-to-right chain on desktop, top-to-bottom on phones.

    `back` draws a dashed return arrow from the last node to the first.
    `both` makes every link two-headed.
    `equal_width=False` lets a long chain use each node's natural width.
    """
    f = DESK
    nw = max(max(node_w(n, f) for n in nodes), 200)
    widths = [nw if equal_width else node_w(n, f) for n in nodes]
    nh = max(node_h(n, f) for n in nodes)
    w = PAD * 2 + sum(widths) + (len(nodes) - 1) * gap
    h = PAD * 2 + nh + (84 if back else 0)
    c = Canvas(w, h, DESK_COL, DESK["out"])
    x = PAD
    for i, (n, width) in enumerate(zip(nodes, widths)):
        draw_node(c, n, x, PAD, width, nh, f)
        if i < len(nodes) - 1:
            c.arrow([(x + width + 8, PAD + nh / 2), (x + width + gap - 8, PAD + nh / 2)], both=both)
        x += width + gap
    if back:
        y0, y1 = PAD + nh, PAD + nh + 48
        xa, xb = PAD + widths[0] / 2, w - PAD - widths[-1] / 2
        c.arrow([(xb, y0 + 6), (xb, y1), (xa, y1), (xa, y0 + 8)], color=MUTED, width=2, dash=6)
        label_w = tw(back, f["note"]) + 24
        c.box((xa + xb) / 2 - label_w / 2, y1 - 18, label_w, 36, fill=PAPER, stroke=PAPER, r=6, width=0)
        c.text((xa + xb) / 2, y1, back, f["note"], color=MUTED)
    c.save(name)

    f = PHONE
    mw, mgap = 680, 64
    left = 92 if back else 40
    bw = mw - left - 40
    fits_phone(name, nodes, bw)
    heights = [node_h(n, f) for n in nodes]
    note_lines = wrap(back, f["note"], bw) if back else []
    mh = PAD * 2 + sum(heights) + (len(nodes) - 1) * mgap + (len(note_lines) * (f["note"] + 10) + 30 if back else 0)
    m = Canvas(mw, mh, PHONE_COL)
    y = PAD
    centers = []
    for i, n in enumerate(nodes):
        draw_node(m, n, left, y, bw, heights[i], f)
        centers.append(y + heights[i] / 2)
        if i < len(nodes) - 1:
            m.arrow([(left + bw / 2, y + heights[i] + 8), (left + bw / 2, y + heights[i] + mgap - 8)], both=both)
        y += heights[i] + mgap
    if back:
        m.arrow([(left, centers[-1]), (40, centers[-1]), (40, centers[0]), (left - 6, centers[0])],
                color=MUTED, width=2, dash=6)
        ny = y - mgap + 30 + f["note"] / 2
        for s in note_lines:
            m.text(left, ny, s, f["note"], color=MUTED, anchor="lm")
            ny += f["note"] + 10
    m.save(name + "-mobile")


def layers(name: str, bands: list[Node], side: list[str], *, note: str = ""):
    """Stacked bands read top to bottom: config precedence, load order."""
    f = DESK
    bw = max(max(node_w(b, f) for b in bands), 420)
    bh = max(node_h(b, f) for b in bands)
    sw = max([tw(s, f["note"]) for s in side if s] + [0])
    gap = 18
    w = PAD * 2 + bw + (36 + sw if sw else 0)
    h = PAD * 2 + len(bands) * bh + (len(bands) - 1) * gap + (52 if note else 0)
    c = Canvas(w, h, DESK_COL, DESK["out"])
    for i, b in enumerate(bands):
        y = PAD + i * (bh + gap)
        draw_node(c, b, PAD, y, bw, bh, f)
        if side[i]:
            c.text(PAD + bw + 36, y + bh / 2, side[i], f["note"], color=MUTED, anchor="lm")
    if note:
        c.text(PAD, h - PAD - 8, note, f["note"], color=MUTED, anchor="lm")
    c.save(name)

    f = PHONE
    mw = 680
    rows = [Node(b.title, b.lines + ([side[i]] if side[i] else []), b.style) for i, b in enumerate(bands)]
    fits_phone(name, rows, mw - 80)
    heights = [node_h(r, f) for r in rows]
    note_lines = wrap(note, f["note"], mw - 80) if note else []
    mh = PAD * 2 + sum(heights) + (len(rows) - 1) * gap + (len(note_lines) * (f["note"] + 10) + 24 if note else 0)
    m = Canvas(mw, mh, PHONE_COL)
    y = PAD
    for r, hh in zip(rows, heights):
        draw_node(m, r, 40, y, mw - 80, hh, f)
        y += hh + gap
    ny = y + 10 + f["note"] / 2
    for s in note_lines:
        m.text(40, ny, s, f["note"], color=MUTED, anchor="lm")
        ny += f["note"] + 10
    m.save(name + "-mobile")


def fan_in(name: str, sources: list[Node], hub: Node, out: Node, gate: str = ""):
    """Several sources into one hub, then one output, with an optional condition."""
    f = DESK
    sw = max(node_w(s, f) for s in sources)
    sh = max(node_h(s, f) for s in sources)
    hw, hh = node_w(hub, f), node_h(hub, f)
    ow, oh = node_w(out, f), node_h(out, f)
    sgap, link = 24, 96
    col_h = len(sources) * sh + (len(sources) - 1) * sgap
    body_h = max(col_h, hh, oh)
    w = PAD * 2 + sw + link + hw + link + ow
    h = PAD * 2 + body_h + (52 if gate else 0)
    c = Canvas(w, h, DESK_COL, DESK["out"])
    hx, hy = PAD + sw + link, PAD + (body_h - hh) / 2
    mid = PAD + body_h / 2
    for i, s in enumerate(sources):
        y = PAD + (body_h - col_h) / 2 + i * (sh + sgap)
        draw_node(c, s, PAD, y, sw, sh, f)
        sy, ty = y + sh / 2, mid + (i - (len(sources) - 1) / 2) * 30
        xm = PAD + sw + link / 2
        c.arrow([(PAD + sw + 8, sy), (xm, sy), (xm, ty), (hx - 8, ty)])
    draw_node(c, hub, hx, hy, hw, hh, f)
    ox = hx + hw + link
    draw_node(c, out, ox, PAD + (body_h - oh) / 2, ow, oh, f)
    c.arrow([(hx + hw + 8, mid), (ox - 8, mid)])
    if gate:
        c.text(w - PAD, h - PAD - 6, gate, f["note"], color=GREEN, anchor="rm")
    c.save(name)

    f = PHONE
    mw, gap = 680, 64
    items = sources + [hub, out]
    fits_phone(name, items, mw - 80)
    heights = [node_h(it, f) for it in items]
    gate_lines = wrap(gate, f["note"], mw - 200) if gate else []
    out_gap = max(gap, len(gate_lines) * (f["note"] + 10) + 30)
    mh = PAD * 2 + sum(heights) + (len(sources) - 1) * 22 + gap + out_gap
    m = Canvas(mw, mh, PHONE_COL)
    y = PAD
    for i, s in enumerate(sources):
        draw_node(m, s, 40, y, mw - 80, heights[i], f)
        y += heights[i] + (22 if i < len(sources) - 1 else 0)
    m.arrow([(mw / 2, y + 8), (mw / 2, y + gap - 8)])
    y += gap
    draw_node(m, hub, 40, y, mw - 80, heights[-2], f)
    y += heights[-2]
    m.arrow([(110, y + 8), (110, y + out_gap - 8)])
    gy = y + out_gap / 2 - (len(gate_lines) - 1) * (f["note"] + 10) / 2
    for s in gate_lines:
        m.text(140, gy, s, f["note"], color=GREEN, anchor="lm")
        gy += f["note"] + 10
    draw_node(m, out, 40, y + out_gap, mw - 80, heights[-1], f)
    m.save(name + "-mobile")


def fan_out(name: str, source: Node, rows: list[tuple[str, Node | None, str, Node | None]]):
    """Labeled branches through optional state nodes to optional outputs."""
    f = DESK
    sw, sh = node_w(source, f), node_h(source, f)
    states = [state for _, state, _, _ in rows if state]
    outputs = [out for _, _, _, out in rows if out]
    bw = max([node_w(n, f) for n in states] + [0])
    ow = max([node_w(n, f) for n in outputs] + [0])
    trunk = PAD + sw / 2
    bx = max(PAD + sw + 64, trunk + max(tw(label, f["note"]) for label, _, _, _ in rows) + 40)
    link = max([tw(label, f["note"]) + 32 for _, _, label, _ in rows] + [96])
    ox = bx + bw + link
    heights = [max(node_h(n, f) for n in (state, out) if n) for _, state, _, out in rows]
    top, gap = PAD + sh + 64, 40
    c = Canvas(ox + ow + PAD, top + sum(heights) + (len(rows) - 1) * gap + PAD, DESK_COL, DESK["out"])
    draw_node(c, source, PAD, PAD, sw, sh, f)
    c.line([(trunk, PAD + sh + 8), (trunk, c.h - PAD - heights[-1] / 2)])
    y = top
    for (label, state, onward, out), hh in zip(rows, heights):
        cy, target = y + hh / 2, bx if state else ox
        c.arrow([(trunk, cy), (target - 8, cy)])
        c.text((trunk + target) / 2, cy - 22, label, f["note"], color=MUTED)
        if state:
            draw_node(c, state, bx, y, bw, hh, f)
        if out:
            draw_node(c, out, ox, y, ow, hh, f)
            if state:
                c.arrow([(bx + bw + 8, cy), (ox - 8, cy)])
                c.text((bx + bw + ox) / 2, cy - 22, onward, f["note"], color=MUTED)
        y += hh + gap
    c.save(name)

    f = PHONE
    mw, left, bw, inner, between = 680, 92, 548, 64, 40
    fits_phone(name, [source] + states + outputs, bw)
    label_heights = [len(wrap(label, f["note"], bw)) * (f["note"] + 10) + 14 for label, _, _, _ in rows]
    row_heights = [sum(node_h(n, f) for n in (state, out) if n) + (inner if state and out else 0)
                   for _, state, _, out in rows]
    mh = PAD * 2 + node_h(source, f) + sum(label_heights) + sum(row_heights) + len(rows) * between
    m = Canvas(mw, mh, PHONE_COL)
    sy = PAD + node_h(source, f) / 2
    draw_node(m, source, left, PAD, bw, node_h(source, f), f)
    y = PAD + node_h(source, f) + between
    last = y + sum(label_heights) + sum(row_heights[:-1]) + (len(rows) - 1) * between
    last += node_h(rows[-1][1] or rows[-1][3], f) / 2
    m.line([(left - 8, sy), (40, sy), (40, last)])
    for (label, state, onward, out), label_h, row_h in zip(rows, label_heights, row_heights):
        for i, line in enumerate(wrap(label, f["note"], bw)):
            m.text(left, y + f["note"] / 2 + i * (f["note"] + 10), line, f["note"], color=MUTED, anchor="lm")
        y += label_h
        first = state or out
        hh = node_h(first, f)
        m.arrow([(40, y + hh / 2), (left - 8, y + hh / 2)])
        draw_node(m, first, left, y, bw, hh, f)
        if state and out:
            m.arrow([(left + 60, y + hh + 8), (left + 60, y + hh + inner - 8)])
            m.text(left + 90, y + hh + inner / 2, onward, f["note"], color=MUTED, anchor="lm")
            draw_node(m, out, left, y + hh + inner, bw, node_h(out, f), f)
        y += row_h + between
    m.save(name + "-mobile")


def pairs(name: str, rows: list[tuple[Node, Node]], *, head: tuple[str, str] = ("", "")):
    """Rows of `left -> right`, for "if you want X, start with Y" mappings."""
    f = DESK
    lw = max(node_w(a, f) for a, _ in rows)
    rw = max(node_w(b, f) for _, b in rows)
    rh = max(max(node_h(a, f), node_h(b, f)) for a, b in rows)
    gap, mid = 16, 84
    top = 44 if head[0] else 0
    w = PAD * 2 + lw + mid + rw
    h = PAD * 2 + top + len(rows) * rh + (len(rows) - 1) * gap
    c = Canvas(w, h, DESK_COL, DESK["out"])
    if head[0]:
        c.text(PAD + 2, PAD + 12, head[0], f["note"], color=MUTED, anchor="lm")
        c.text(PAD + lw + mid + 2, PAD + 12, head[1], f["note"], color=MUTED, anchor="lm")
    for i, (a, b) in enumerate(rows):
        y = PAD + top + i * (rh + gap)
        draw_node(c, a, PAD, y, lw, rh, f)
        draw_node(c, b, PAD + lw + mid, y, rw, rh, f)
        c.arrow([(PAD + lw + 10, y + rh / 2), (PAD + lw + mid - 10, y + rh / 2)])
    c.save(name)

    f = PHONE
    mw, inner, between = 680, 40, 36
    fits_phone(name, [it for row in rows for it in row], mw - 80)
    mh = PAD * 2 + sum(node_h(a, f) + inner + node_h(b, f) for a, b in rows) + (len(rows) - 1) * between
    m = Canvas(mw, mh, PHONE_COL)
    y = PAD
    for a, b in rows:
        ah, bh = node_h(a, f), node_h(b, f)
        draw_node(m, a, 40, y, mw - 80, ah, f)
        m.arrow([(mw / 2, y + ah + 6), (mw / 2, y + ah + inner - 6)])
        draw_node(m, b, 40, y + ah + inner, mw - 80, bh, f)
        y += ah + inner + bh + between
    m.save(name + "-mobile")


def gated_flow(name: str, nodes: list[Node], stop: Node, *, stops: dict[int, str],
               bypass: tuple[int, int, str], onward: dict[int, str]):
    """A vertical chain with a shared stop and one bypass around a decision.

    Desktop places the stop beside the chain; phones stack it below, with
    separate outer rails for the stop and bypass so paths never cross.
    """
    for mobile, f in [(False, DESK), (True, PHONE)]:
        left = 92
        bw = 496 if mobile else max(node_w(n, f) for n in nodes)
        if mobile:
            fits_phone(name, nodes + [stop], bw)
        gap = 100
        heights = [node_h(n, f) for n in nodes]
        ys = [PAD]
        for hh in heights[:-1]:
            ys.append(ys[-1] + hh + gap)
        centers = [y + hh / 2 for y, hh in zip(ys, heights)]
        stop_w, stop_h = (bw if mobile else node_w(stop, f)), node_h(stop, f)
        stop_x = left if mobile else left + bw + 220
        stop_y = ys[-1] + heights[-1] + gap if mobile else centers[max(stops)] - stop_h / 2
        w = 680 if mobile else stop_x + stop_w + PAD
        h = max(ys[-1] + heights[-1], stop_y + stop_h) + PAD
        c = Canvas(w, h, PHONE_COL if mobile else DESK_COL, f["out"])
        for i, (n, y, hh) in enumerate(zip(nodes, ys, heights)):
            draw_node(c, n, left, y, bw, hh, f)
            if i < len(nodes) - 1:
                # Offset labeled links to leave room for text on phones.
                ax = left + 120 if i in onward else left + bw / 2
                c.arrow([(ax, y + hh + 8), (ax, ys[i + 1] - 8)])
                if i in onward:
                    c.text(ax + 24, y + hh + gap / 2, onward[i], f["note"],
                           color=MUTED, anchor="lm")

        start, end, label = bypass
        # Join the destination from the left, clear of the main chain.
        c.arrow([(left - 8, centers[start]), (40, centers[start]),
                 (40, centers[end]), (left - 8, centers[end])])
        c.text(left, ys[end] - 28, label, f["note"], color=MUTED, anchor="lm")

        rail = w - 40 if mobile else left + bw + 180
        stop_cy = stop_y + stop_h / 2
        branch_ys = []
        for i, label in stops.items():
            # Exit near the bottom corner; label sits in the following gap.
            by = ys[i] + heights[i] - 24
            branch_ys.append(by)
            c.line([(left + bw + 8, by), (rail, by)], color=MUTED)
            c.text(left + bw if mobile else left + bw + 24,
                   ys[i] + heights[i] + 28 if mobile else by - 22,
                   label, f["note"], color=MUTED, anchor="rm" if mobile else "lm")
        c.line([(rail, min(branch_ys + [stop_cy])),
                (rail, max(branch_ys + [stop_cy]))], color=MUTED)
        target = stop_x + stop_w + 8 if mobile else stop_x - 8
        c.arrow([(rail, stop_cy), (target, stop_cy)], color=MUTED)
        draw_node(c, stop, stop_x, stop_y, stop_w, stop_h, f)
        c.save(name + ("-mobile" if mobile else ""))


# ---------------------------------------------------------------- diagrams

DIAGRAMS = {}


def diagram(fn):
    DIAGRAMS[fn.__name__.replace("_", "-")] = fn
    return fn


@diagram
def claude_code_permission_layers(name):
    gated_flow(name, [
        Node("Tool call"),
        Node("PreToolUse hook", ["Claude Code decides"], "tint"),
        Node("Deny, ask, allow", ["Rules", "Claude Code decides"], "brand"),
        Node("Permission mode", ["Claude Code decides"], "tint"),
        Node("Bash sandbox", ["OS-level limits"], "tint"),
        Node("Command runs"),
    ], Node("Blocked", [], "quiet"), stops={1: "exit 2", 2: "deny"},
        bypass=(2, 4, "allow"), onward={2: "no match", 3: "approved"})


@diagram
def claude_md_load_order(name):
    fan_in(name, [
        Node("1 Managed policy file", ["at launch"], "tint"),
        Node("2 ~/.claude/CLAUDE.md", ["at launch"], "card"),
        Node("3 Ancestor files", ["CLAUDE.md", "at launch"], "card"),
        Node("4 Working directory", ["CLAUDE.md + local", "at launch"], "card"),
        Node("Subdirectory CLAUDE.md", ["on demand", "when a file is touched"], "quiet"),
    ], Node("Concatenated", ["all loaded files", "in load order"], "tint"),
        Node("Claude context", [], "brand"))


@diagram
def claude_code_session_loop(name):
    flow(name, [
        Node("Prompt", ["Shift+Enter", "adds a line"], "tint"),
        Node("Claude works", ["minutes", "to hours"], "brand"),
        Node("Needs you", ["notification", "in background"], "card"),
        Node("Review", ["Cmd+Click", "path:line"], "card"),
    ], back="after a restart, tabs and last screens return")


@diagram
def claude_code_notifications(name):
    fan_in(name, [
        Node("Claude Code", ["channel \"ghostty\""], "card"),
        Node("Codex", ["bell or osc9"], "card"),
        Node("Your scripts", ["OSC 9 or 777"], "quiet"),
    ], Node("Kaku", ["reads the", "sequence"], "brand"), Node("macOS", ["Notification", "Center"], "tint"),
        gate="only while Kaku is in the background")


@diagram
def remote_access_architecture(name):
    flow(name, [
        Node("Browser", ["another", "computer"], "tint"),
        Node("Relay", ["forwards bytes", "it cannot read"], "quiet"),
        Node("Kaku", ["your Mac,", "awake"], "brand"),
    ], both=True, back="encrypted from the browser to Kaku")


@diagram
def codex_config_layers(name):
    layers(name, [
        Node("Command line flags", ["-m, -s, -c key=value"], "brand"),
        Node("Project config", [".codex/config.toml"], "tint"),
        Node("User config", ["~/.codex/config.toml"], "card"),
        Node("Built-in defaults", [], "quiet"),
    ], ["this run", "this repo", "every session", "if unset"])


@diagram
def mac_terminal_picker(name):
    pairs(name, [
        (Node("Nothing to install"), Node("Terminal.app", [], "quiet")),
        (Node("Every feature, a GUI"), Node("iTerm2", [], "card")),
        (Node("Fast, native, text config"), Node("Ghostty", [], "card")),
        (Node("Lua, every platform"), Node("WezTerm", [], "card")),
        (Node("An agent built in"), Node("Warp", [], "card")),
        (Node("Ready for AI coding CLIs"), Node("Kaku", [], "brand")),
    ], head=("If you want", "Start with"))


@diagram
def terminal_config_models(name):
    pairs(name, [
        (Node("iTerm2"), Node("Settings window", ["saved to a plist"], "card")),
        (Node("Ghostty"), Node("Text file", ["key = value"], "card")),
        (Node("WezTerm"), Node("Lua script", ["hot reload"], "brand")),
    ], head=("Terminal", "Configured with"))


@diagram
def kaku_zsh_load_order(name):
    layers(name, [
        Node("1 PATH, Kaku check", [], "card"),
        Node("2 Starship prompt", ["cached init"], "tint"),
        Node("3 History, keys", [], "card"),
        Node("4 compinit -C", ["full check daily"], "tint"),
        Node("5 z, autosuggestions", ["yours win"], "card"),
        Node("6 Syntax highlighting", ["after first prompt"], "brand"),
    ], ["", "", "", "", "", ""], note="the whole file is zcompiled")


@diagram
def lazygit_delta_pipeline(name):
    fan_in(name, [
        Node("git diff / log -p", ["core.pager"], "card"),
        Node("lazygit", ["diffRenderers"], "card"),
    ], Node("delta", ["colors,", "line numbers"], "brand"), Node("Kaku pane", ["Cmd+Shift+G", "for lazygit"], "tint"))


@diagram
def kaku_config_layers(name):
    layers(name, [
        Node("Your overrides", ["in kaku.lua"], "brand"),
        Node("Kaku bundled config", ["fonts, keys, 1.28"], "tint"),
        Node("WezTerm defaults", [], "quiet"),
    ], ["applied last", "loaded first", "underneath"])


@diagram
def session_restore_flow(name):
    flow(name, [
        Node("Panes", ["agents, shells"], "card"),
        Node("Snapshot", ["every 60s"], "tint"),
        Node("Restart", ["update, crash"], "quiet"),
        Node("Restored", ["text, no re-run"], "brand"),
    ])


@diagram
def claude_code_hooks_lifecycle(name):
    flow(name, [
        Node("PreToolUse", ["exit 2 blocks"], "brand"),
        Node("Tool runs", ["Edit, Bash"], "card"),
        Node("PostToolUse", ["format, lint"], "card"),
        Node("Stop", ["notify you"], "tint"),
    ])


@diagram
def claude_code_statusline(name):
    flow(name, [
        Node("Claude Code", ["session JSON"], "tint"),
        Node("Your script", ["stdin, jq, git"], "brand"),
        Node("Status line", ["row under", "the input"], "card"),
    ], back="runs again on each new message")


@diagram
def claude_code_git_worktrees(name):
    pairs(name, [
        (Node("repo", ["main"]), Node("Tab 1", ["claude"], "brand")),
        (Node("repo-feature", ["feature-auth"]), Node("Tab 2", ["claude"], "card")),
        (Node("repo-fix", ["fix-login"]), Node("Tab 3", ["codex"], "card")),
    ], head=("Worktree, branch", "Kaku tab"))


@diagram
def shell_integration_osc(name):
    fan_out(name, Node("Shell or program"), [
        ("OSC 7 / process cwd", Node("Working directory", [], "tint"), "Cmd+T", Node("New tab")),
        ("OSC 133", Node("Prompt zones", [], "tint"), "", None),
        ("OSC 1337", Node("Assistant hook", [], "brand"), "", None),
        ("OSC 9 / 777", None, "", Node("macOS notification", [], "tint")),
        ("OSC 8", None, "", Node("Clickable link", [], "tint")),
    ])


@diagram
def how_terminal_emulators_work(name):
    flow(name, [
        Node("Shell", ["on slave", "output bytes"], "card"),
        Node("PTY", ["master", "read"], "quiet"),
        Node("Escape", ["parser", "text and CSI"], "tint"),
        Node("Cell grid", ["graphemes"], "tint"),
        Node("HarfBuzz", ["shaper", "glyphs"], "tint"),
        Node("WebGPU", ["window"], "brand"),
    ], back="key bytes to PTY master, then stdin to shell", gap=32, equal_width=False)


@diagram
def claude_code_mcp_servers(name):
    # A fork and join needs a shared result, unlike the fan_out row outputs.
    nodes = [
        Node("Claude Code", [], "tint"),
        Node("MCP client", [], "brand"),
        Node("Stdio process"),
        Node("HTTP server"),
        Node("Tool list", [], "tint"),
    ]
    f = {**DESK, "note": DESK["title"]}
    widths = [node_w(n, f) for n in nodes]
    hh = max(node_h(n, f) for n in nodes)
    server_w = max(widths[2:4])
    branch_gap = tw("stdin and stdout", f["note"]) + 64
    join_gap = tw("tools/list", f["note"]) + 64
    client_x = PAD + widths[0] + 96
    server_x = client_x + widths[1] + branch_gap
    tool_x = server_x + server_w + join_gap
    row_step = hh + 110
    upper, lower = PAD + hh / 2, PAD + hh / 2 + row_step
    cy = (upper + lower) / 2
    c = Canvas(tool_x + widths[4] + PAD, lower + hh / 2 + PAD, DESK_COL, f["out"])
    for i, x in [(0, PAD), (1, client_x), (4, tool_x)]:
        draw_node(c, nodes[i], x, cy - hh / 2, widths[i], hh, f)
    for i, y in [(2, upper), (3, lower)]:
        draw_node(c, nodes[i], server_x, y - hh / 2, server_w, hh, f)

    c.arrow([(PAD + widths[0] + 8, cy), (client_x - 8, cy)])
    c.text((PAD + widths[0] + client_x) / 2, cy - hh / 2 - 28,
           "one per server", f["note"], color=MUTED)
    # Split before the two peer transports, then merge after them.
    split_x = client_x + widths[1] + 32
    c.line([(client_x + widths[1] + 8, cy), (split_x, cy)])
    c.line([(split_x, upper), (split_x, lower)])
    merge_x = server_x + server_w + 32
    for y, label in [(upper, "stdin and stdout"), (lower, "HTTP")]:
        c.arrow([(split_x, y), (server_x - 8, y)])
        c.text((split_x + server_x) / 2, y - 28, label, f["note"], color=MUTED)
        c.line([(server_x + server_w + 8, y), (merge_x, y)])
    c.line([(merge_x, upper), (merge_x, lower)])
    c.arrow([(merge_x, cy), (tool_x - 8, cy)])
    c.text((merge_x + tool_x) / 2, cy - 28, "tools/list", f["note"], color=MUTED)
    c.save(name)

    f = PHONE
    mw, left, bw = 680, 92, 496
    fits_phone(name, nodes, bw)
    heights = [node_h(n, f) for n in nodes]
    gaps = [80, 100, 112, 100]
    ys = [PAD]
    for height, gap in zip(heights[:-1], gaps):
        ys.append(ys[-1] + height + gap)
    m = Canvas(mw, ys[-1] + heights[-1] + PAD, PHONE_COL)
    for n, y, height in zip(nodes, ys, heights):
        draw_node(m, n, left, y, bw, height, f)
    m.arrow([(mw / 2, ys[0] + heights[0] + 8), (mw / 2, ys[1] - 8)])
    m.text(mw / 2 + 24, (ys[0] + heights[0] + ys[1]) / 2,
           "one per server", f["note"], color=MUTED, anchor="lm")
    centers = [y + height / 2 for y, height in zip(ys, heights)]
    m.line([(left - 8, centers[1]), (40, centers[1]), (40, centers[3])])
    for i, label in [(2, "stdin and stdout"), (3, "HTTP")]:
        m.arrow([(40, centers[i]), (left - 8, centers[i])])
        m.text(left, ys[i] - 28, label, f["note"], color=MUTED, anchor="lm")
        m.line([(left + bw + 8, centers[i]), (mw - 40, centers[i])])
        m.text(left + bw, ys[i] + heights[i] + 28, "tools/list", f["note"], color=MUTED, anchor="rm")
    m.arrow([(mw - 40, centers[2]), (mw - 40, centers[4]), (left + bw + 8, centers[4])])
    m.save(name + "-mobile")


def main() -> int:
    wanted = sys.argv[1:]
    for name, fn in DIAGRAMS.items():
        if not wanted or any(w in name for w in wanted):
            fn(name)
    return 0


if __name__ == "__main__":
    sys.exit(main())
