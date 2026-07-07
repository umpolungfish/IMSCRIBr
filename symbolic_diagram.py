#!/usr/bin/env python3
"""
IMASM Symbolic Wiring Diagram Generator v3 — Full Edge Granularity
Part of IMSCRIBr — the IMASM Arrangement Space Iterator & Wiring Diagram Suite

Enhances v2 with 7 edge-semantic dimensions previously flattened:
  1. Register-delta labels — Belnap state transformation across each edge
  2. Categorical edge coloring — distinct hue per logical-morphism type
  3. Nesting-depth opacity — deeper nesting → thinner/fainter wires
  4. IFIX barrier — visible fixation wall with edge crossing markers
  5. Guard semantics — amber "approaching gate" / green "passed gate" port dots
  6. Pair-identity coloring — each FSPLIT/FFUSE pair gets unique hue family
  7. CLINK double-stroke — converging parallel lines for compositional edges

Usage:
    python3 symbolic_diagram.py                  → all 16 diagrams
    python3 symbolic_diagram.py --class I         → single class
    python3 symbolic_diagram.py --all --format png → PNG via cairosvg
"""

from __future__ import annotations
import sys, os, math, argparse
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional, Tuple
from collections import namedtuple

sys.path.insert(0, str(Path(__file__).resolve().parents[3] / "IMSCRIBr"))
from tokens import Token, TOKEN_NAMES, TOKEN_FAMILY

TOKEN_SHORT = ["VI","TA","AF","AR","CL","IM","FS","FF","ET","EF","EG","IX"]

from wiring import (
    imscr_wiring, WiredGraph, Wire, NOVEL_GRAPHS,
    match_pairs,
)

# ── Visual constants ─────────────────────────────────────────────────────────
OUT_DIR   = Path(__file__).parent / "diagrams"
BG        = "#0a0a15"
GRID_COLOR = "#151525"
GRID_SPACING = 40

FG        = "#cccccc"

FAM_COLOR = {0: "#4e79a7", 1: "#ffd700", 2: "#e15759", 3: "#59a14f"}
FAM_NAME  = {0: "LOGICAL", 1: "FROBENIUS", 2: "DIALETHEIA", 3: "LINEAR"}

T_COLOR   = "#20d0b8"
F_COLOR   = "#ff6688"
CROSS_COLOR = "#ffd700"
BACK_COLOR  = "#9988cc"
EMPTY_COLOR = "#333344"
MAIN_COLOR  = "#4e79a7"
IFIX_COLOR  = "#cc3344"

REG_COLOR = {0: "#222244", 1: "#153530", 2: "#301518", 3: "#332200"}
REG_LABEL = {0: "", 1: "↑", 2: "↓", 3: "↑↓"}

SVG_W, SVG_H = 1100, 720
MARGIN_X = 70
MARGIN_Y = 70
LEGEND_Y = 52
Y_MAIN   = 330
Y_T      = 190
Y_F      = 470
NODE_R   = 22

# ── Categorical edge palette (per source token) ──────────────────────────────
CAT_EDGE_COLOR = {
    Token.VINIT:   "#6baed6",  # source → pale blue
    Token.TANCH:   "#b07aa1",  # boundary → violet
    Token.AFWD:    "#59a14f",  # forward → green
    Token.AREV:    "#e15759",  # reverse → coral-red
    Token.CLINK:   "#f28e2b",  # composition → amber
    Token.IMSCRIB: "#ffd700",  # identity → gold
    Token.FSPLIT:  "#ffd700",  # fork (Frobenius gold)
    Token.FFUSE:   "#ffd700",  # join (Frobenius gold)
    Token.EVALT:   "#20d0b8",  # T-guard → teal
    Token.EVALF:   "#ff6688",  # F-guard → coral
    Token.ENGAGR:  "#e15759",  # paradox → dialetheia red
    Token.IFIX:    "#cc3344",  # fix → red
}

CAT_EDGE_STYLE = {
    Token.TANCH:   "4,3",      # boundary → dotted
    Token.IMSCRIB: None,        # identity → solid gold
    Token.CLINK:   "double",    # composition → double-stroke (handled specially)
}

# ── Pair identity palette (cycling hues for FSPLIT/FFUSE pairs) ─────────────
PAIR_PALETTE = [
    ("#5b9bd5", "#2b6b9f"),   # blue family
    ("#ed7d31", "#b85a1c"),   # orange family
    ("#70ad47", "#4a7a2e"),   # green family
    ("#9b59b6", "#6b3d82"),   # purple family
    ("#e8c92a", "#b0981a"),   # gold family
    ("#e15759", "#9b2d2f"),   # red family
    ("#17becf", "#0e7a85"),   # cyan family
    ("#bcbd22", "#8a8b19"),   # olive family
]
# ── Register simulation (Belnap FOUR) ────────────────────────────────────────
VOID, TRUE, FALSE, BOTH = 0, 1, 2, 3

def simulate_register(tokens: Tuple[int, ...]) -> list[int]:
    """Simulate Belnap FOUR register traversal through a token sequence."""
    reg = VOID; fixed = False
    in_split = False; in_split_T = False
    result = []
    for tok in tokens:
        if fixed and tok not in (Token.IFIX.value, Token.IMSCRIB.value):
            result.append(reg); continue
        t = Token(tok)
        if t == Token.VINIT:       reg = VOID; in_split = False; in_split_T = False
        elif t == Token.AFWD:      reg = {VOID:TRUE, FALSE:BOTH}.get(reg, reg)
        elif t == Token.AREV:      reg = {VOID:FALSE, TRUE:BOTH}.get(reg, reg)
        elif t == Token.CLINK:     reg = VOID if reg in (TRUE, FALSE) else reg
        elif t == Token.IMSCRIB:   reg = TRUE if reg == VOID else reg
        elif t == Token.FSPLIT:    in_split = True
        elif t == Token.FFUSE:
            if in_split_T and reg == FALSE: reg = BOTH
            elif reg == BOTH: reg = TRUE
            in_split = False; in_split_T = False
        elif t == Token.EVALT:
            if in_split: in_split_T = True
            if reg == FALSE: reg = BOTH
            elif reg == VOID: reg = TRUE
        elif t == Token.EVALF:
            if reg == TRUE: reg = BOTH
            elif reg == VOID: reg = FALSE
        elif t == Token.IFIX:      fixed = True
        result.append(reg)
    return result


def reg_delta_label(src_reg: int, dst_reg: int) -> str:
    """Human-readable register delta: spin arrows. VOID→X shows only destination spin."""
    if src_reg == VOID:
        return REG_LABEL[dst_reg]  # just show destination spin
    return f"{REG_LABEL[src_reg]}→{REG_LABEL[dst_reg]}"


def reg_delta_color(src_reg: int, dst_reg: int) -> str:
    """Color for register delta label: B-involved gets gold, paradox gets red."""
    if src_reg == dst_reg:
        return "#666688"
    if BOTH in (src_reg, dst_reg):
        return "#ffd700"  # BOTH involvement → gold
    if (src_reg, dst_reg) in ((TRUE, FALSE), (FALSE, TRUE)):
        return "#e15759"  # truth-value flip → red
    return "#20b888"  # void↔value → teal


# ── SVG primitives ───────────────────────────────────────────────────────────
def _svg_attrs(d: dict) -> str:
    return " ".join(f'{k}="{v}"' for k, v in d.items() if v is not None)

def _hexagon_points(cx, cy, r) -> str:
    pts = []
    for i in range(6):
        a = math.pi/6 + i * math.pi/3
        pts.append(f"{cx + r*math.cos(a):.1f},{cy + r*math.sin(a):.1f}")
    return " ".join(pts)

def _diamond_points(cx, cy, r) -> str:
    return f"{cx},{cy-r:.1f} {cx+r:.1f},{cy} {cx},{cy+r:.1f} {cx-r:.1f},{cy}"

def _arrow_head_points(x2, y2, x1, y1, size=8):
    dx, dy = x2 - x1, y2 - y1
    L = math.hypot(dx, dy) or 1
    ux, uy = dx/L, dy/L
    px, py = -uy, ux
    pts = [
        (x2, y2),
        (x2 - size*ux + 0.4*size*px, y2 - size*uy + 0.4*size*py),
        (x2 - size*ux - 0.4*size*px, y2 - size*uy - 0.4*size*py),
    ]
    return " ".join(f"{p[0]:.1f},{p[1]:.1f}" for p in pts)

class SVGBuilder:
    """Streaming SVG builder with enhanced edge primitives."""
    def __init__(self, w=SVG_W, h=SVG_H):
        self.w = w; self.h = h
        self.parts = [f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}">']
        self.parts.append(f'<rect width="{w}" height="{h}" fill="{BG}"/>')
        self._defs = []

    def add_def(self, def_str: str):
        self._defs.append(def_str)

    def add(self, tag: str, attrs: dict = None, text: str = None, close=True):
        a = _svg_attrs(attrs or {})
        if close:
            self.parts.append(f"<{tag} {a}>{text or ''}</{tag}>")
        else:
            self.parts.append(f"<{tag} {a}>")
        return self

    def g(self, attrs=None, close=False):
        return self.add("g", attrs, close=close)

    def line(self, x1, y1, x2, y2, stroke=MAIN_COLOR, width=1.2, dash=None, opacity=0.7):
        d = {"x1": f"{x1:.1f}", "y1": f"{y1:.1f}", "x2": f"{x2:.1f}", "y2": f"{y2:.1f}",
             "stroke": stroke, "stroke-width": str(width), "opacity": str(opacity)}
        if dash: d["stroke-dasharray"] = dash
        return self.add("line", d)

    def draw_arrow(self, x1, y1, x2, y2, color=MAIN_COLOR, width=1.5, opacity=0.7, dash=None):
        """Single-stroke arrow with head."""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if L < 1: return
        ux, uy = dx/L, dy/L
        head_size = 8
        shaft_x = x2 - head_size * ux
        shaft_y = y2 - head_size * uy
        self.line(x1, y1, shaft_x, shaft_y, color, width, dash, opacity)
        self.add("polygon", {
            "points": _arrow_head_points(x2, y2, x1, y1, head_size),
            "fill": color, "opacity": str(opacity)
        })

    def draw_double_arrow(self, x1, y1, x2, y2, color="#f28e2b", width=1.0, opacity=0.7):
        """CLINK double-stroke: two parallel lines that converge at the arrowhead."""
        dx, dy = x2 - x1, y2 - y1
        L = math.hypot(dx, dy)
        if L < 1: return
        ux, uy = dx/L, dy/L
        px, py = -uy, ux  # perpendicular
        gap = 3.5
        head_size = 9
        # Two parallel shafts
        for sign in (-1, 1):
            sx1, sy1 = x1 + sign*gap*px, y1 + sign*gap*py
            sx2, sy2 = x2 - head_size*ux + sign*gap*px, y2 - head_size*uy + sign*gap*py
            self.line(sx1, sy1, sx2, sy2, color, width, None, opacity)
        # Arrowhead
        self.add("polygon", {
            "points": _arrow_head_points(x2, y2, x1, y1, head_size+1),
            "fill": color, "opacity": str(opacity)
        })

    def draw_edge_label(self, mid_x, mid_y, text: str, color="#666688", size=6):
        """Small label at edge midpoint for register delta."""
        # Place slightly above the wire
        self.add("rect", {
            "x": f"{mid_x - len(text)*2.0:.1f}", "y": f"{mid_y - 12:.1f}",
            "width": f"{len(text)*4.0:.1f}", "height": "10",
            "fill": BG, "opacity": "0.7", "rx": "3"
        })
        self.text(mid_x, mid_y - 4, text, size, color, "middle", False, "monospace")

    def draw_ifix_barrier(self, x: float, y_top: float, y_bot: float):
        """Vertical dashed red barrier at the IFIX position."""
        self.line(x, y_top, x, y_bot, IFIX_COLOR, 1.8, "6,4", 0.4)
        # Label
        self.text(x, y_top - 10, "IFIX", 7, IFIX_COLOR, "middle", True, "monospace")
        # Small red diamonds at top and bottom
        for yy in (y_top, y_bot):
            pts = _diamond_points(x, yy, 4)
            self.add("polygon", {"points": pts, "fill": IFIX_COLOR, "opacity": "0.6"})

    def curve_arrow(self, x1, y1, x2, y2, color="#9988cc", width=1.2, opacity=0.5, rad=40):
        """Curved back-arc from x2,y2 arcing above to x1,y1."""
        mid_x = (x1 + x2) / 2; mid_y = min(y1, y2) - rad
        path = f"M{x2:.1f},{y2:.1f} Q{mid_x:.1f},{mid_y:.1f} {x1:.1f},{y1:.1f}"
        self.add("path", {"d": path, "fill": "none", "stroke": color,
                          "stroke-width": str(width), "opacity": str(opacity)})
        dx, dy = x1 - mid_x, y1 - mid_y; L = math.hypot(dx, dy) or 1
        ux, uy = dx/L, dy/L
        hx1 = x1 + 8*ux - 4*uy; hy1 = y1 + 8*uy + 4*ux
        hx2 = x1 + 8*ux + 4*uy; hy2 = y1 + 8*uy - 4*ux
        self.add("polygon", {
            "points": f"{x1:.1f},{y1:.1f} {hx1:.1f},{hy1:.1f} {hx2:.1f},{hy2:.1f}",
            "fill": color, "opacity": str(opacity)
        })

    def curve_empty_arc(self, x1, y1, x2, y2, lane_y, color=EMPTY_COLOR):
        path = f"M{x1:.1f},{y1:.1f} Q{(x1+x2)/2:.1f},{lane_y:.1f} {x2:.1f},{y2:.1f}"
        self.add("path", {
            "d": path, "fill": "none", "stroke": color, "stroke-dasharray": "4,4",
            "stroke-width": "1", "opacity": "0.25"
        })

    def circle_node(self, cx, cy, r, fill, stroke="#ffffff20", sw=1.0):
        self.add("circle", {"cx": f"{cx:.1f}", "cy": f"{cy:.1f}", "r": f"{r:.1f}",
                             "fill": fill, "stroke": stroke, "stroke-width": str(sw)})

    def diamond_node(self, cx, cy, r, fill, stroke="#ffffff20", sw=1.0):
        pts = _diamond_points(cx, cy, r)
        self.add("polygon", {"points": pts, "fill": fill, "stroke": stroke, "stroke-width": str(sw)})

    def hexagon_node(self, cx, cy, r, fill, stroke="#ffffff20", sw=1.0):
        pts = _hexagon_points(cx, cy, r)
        self.add("polygon", {"points": pts, "fill": fill, "stroke": stroke, "stroke-width": str(sw)})

    def square_node(self, cx, cy, r, fill, stroke="#ffffff20", sw=1.0):
        self.add("rect", {"x": f"{cx-r:.1f}", "y": f"{cy-r:.1f}",
                          "width": f"{2*r:.1f}", "height": f"{2*r:.1f}",
                          "fill": fill, "stroke": stroke, "stroke-width": str(sw)})

    def text(self, x, y, text, size=9, color=FG, anchor="middle", bold=False, family="monospace"):
        d = {"x": f"{x:.1f}", "y": f"{y:.1f}", "fill": color, "font-size": str(size),
             "text-anchor": anchor, "font-family": family}
        if bold: d["font-weight"] = "bold"
        return self.add("text", d, text)

    def port_dot(self, cx, cy, fill="#ffffff", r=3):
        self.circle_node(cx, cy, r, fill, None, 0)

    def lane_label(self, x, y, text, color=EMPTY_COLOR):
        return self.text(x, y, text, 7, color, "middle")


    def draw_grid(self):
        """Subtle grid background for schematic feel."""
        for x in range(0, self.w, GRID_SPACING):
            self.line(x, 0, x, self.h, GRID_COLOR, 0.4, None, 0.25)
        for y in range(0, self.h, GRID_SPACING):
            self.line(0, y, self.w, y, GRID_COLOR, 0.4, None, 0.25)

    def draw_orthogonal_arrow(self, x1, y1, x2, y2, color=MAIN_COLOR, width=1.5,
                               opacity=0.7, dash=None, channel_offset=0):
        """Manhattan-routed arrow with 90-degree bends — electrical schematic style.
        channel_offset: integer lane offset (8px per channel) to separate overlapping vertical trunks."""
        dx, dy = x2 - x1, y2 - y1

        # Same lane (~horizontal): straight line with arrow
        if abs(dy) < 10:
            return self.draw_arrow(x1, y1, x2, y2, color, width, opacity, dash)

        # Base mid_x plus channel spread
        ch_dx = channel_offset * 8  # 8px per channel lane
        if dx > 0:
            mid_x = x1 + max(18, min(35, dx * 0.35)) + ch_dx
        else:
            mid_x = x1 - max(18, min(35, -dx * 0.35)) + ch_dx

        segments = [
            (x1, y1, mid_x, y1),
            (mid_x, y1, mid_x, y2),
            (mid_x, y2, x2, y2),
        ]

        for i, (sx, sy, ex, ey) in enumerate(segments):
            seg_len = abs(ex - sx) + abs(ey - sy)
            if seg_len < 2:
                continue
            if i == len(segments) - 1:
                self.draw_arrow(sx, sy, ex, ey, color, width, opacity, dash)
            else:
                self.line(sx, sy, ex, ey, color, width, dash, opacity)

    def draw_orthogonal_double_arrow(self, x1, y1, x2, y2, color="#f28e2b", width=1.0,
                                      opacity=0.7, channel_offset=0):
        """CLINK orthogonal double-stroke: two parallel paths with 90-degree bends.
        channel_offset: integer lane offset (8px per channel) to separate overlapping vertical trunks."""
        import math
        dx, dy = x2 - x1, y2 - y1

        # Same lane: draw parallel horizontal lines (delegated to simple double)
        if abs(dy) < 10:
            return self.draw_double_arrow(x1, y1, x2, y2, color, width, opacity)

        ch_dx = channel_offset * 8
        if dx > 0:
            mid_x = x1 + max(18, min(35, dx * 0.35)) + ch_dx
        else:
            mid_x = x1 - max(18, min(35, -dx * 0.35)) + ch_dx

        segments = [
            (x1, y1, mid_x, y1),
            (mid_x, y1, mid_x, y2),
            (mid_x, y2, x2, y2),
        ]

        for i, (sx, sy, ex, ey) in enumerate(segments):
            seg_len = abs(ex - sx) + abs(ey - sy)
            if seg_len < 2:
                continue
            if i == len(segments) - 1:
                self.draw_double_arrow(sx, sy, ex, ey, color, width, opacity)
            else:
                # Parallel double lines for intermediate segments
                sdx, sdy = ex - sx, ey - sy
                L = math.hypot(sdx, sdy) or 1
                ux, uy = sdx/L, sdy/L
                px, py = -uy, ux
                gap = 3.0
                for sign in (-1, 1):
                    self.line(sx + sign*gap*px, sy + sign*gap*py,
                              ex + sign*gap*px, ey + sign*gap*py,
                              color, width, None, opacity)

    def draw_crossing_bridge(self, cx, cy, under_color="#334", over_color=None):
        """Draw a small semicircular bridge arc at a wire crossing point.
        Indicates 'over wire' jumping above 'under wire' — standard electrical schematic convention.
        cx,cy: the crossing point. The bridge arcs above (smaller y for SVG)."""
        r = 4.5
        # Small semicircle arcing upward (over the crossing)
        path = f"M{cx-r:.1f},{cy:.1f} A{r:.1f},{r:.1f} 0 0,1 {cx+r:.1f},{cy:.1f}"
        color = over_color or "#ffd700"
        self.add("path", {
            "d": path, "fill": "none", "stroke": color,
            "stroke-width": "1.8", "opacity": "0.85"
        })
        # Small filled circle at the crossing point beneath
        self.circle_node(cx, cy, 2.0, under_color, None, 0.5)

    def close(self):
        if self._defs:
            defs = ["<defs>"] + self._defs + ["</defs>"]
            # Insert after the background rect
            self.parts[2:2] = defs
        self.parts.append("</svg>")

    def save(self, path: Path):
        path.parent.mkdir(parents=True, exist_ok=True)
        with open(path, "w") as f:
            f.write("\n".join(self.parts))
        return path


# ── Diagram Layout ──────────────────────────────────────────────────────────

@dataclass
class DiagramLayout:
    """Computed positions for a wiring diagram."""
    tokens:      Tuple[Token, ...]
    pos:         Dict[int, Tuple[float, float]]
    lanes:       Dict[int, str]
    wires:       List[Wire]
    n:           int
    # Enriched data
    states:      List[int]                    # per-node register state
    nesting:     Dict[int, int]               # per-node nesting depth
    pair_of:     Dict[int, int]               # node → pair index (0-based)
    ifix_pos:    Optional[float]              # x-position of first IFIX barrier
    pair_wires:  Dict[int, List[Wire]]        # pair index → wires belonging to it

    def x(self, idx): return self.pos[idx][0]
    def y(self, idx): return self.pos[idx][1]


def compute_layout(graph: WiredGraph) -> DiagramLayout:
    """Full layout with enriched edge-semantic metadata."""
    tokens = graph.tokens
    n = len(tokens)
    states = simulate_register(tuple(t.value for t in tokens))

    # ── Topological layers (Kahn's algorithm) ──
    layers = graph.topological_layers()

    # ── FSPLIT/FFUSE pairs ──
    pairs = match_pairs(tuple(t.value for t in tokens))
    fsplit_set = set(fs for fs, _ in pairs)
    ffuse_set = set(ff for _, ff in pairs)
    fsplit_to_ffuse = {fs: ff for fs, ff in pairs}

    # ── Nesting depth ──
    nesting: Dict[int, int] = {}
    depth = 0
    for i, tok in enumerate(tokens):
        t = tok.value
        if t == Token.FSPLIT.value:
            depth += 1
            nesting[i] = depth
        elif t == Token.FFUSE.value:
            nesting[i] = depth
            depth = max(0, depth - 1)
        else:
            nesting[i] = depth

    pair_depth = {fs: nesting[fs] for fs, _ in pairs}

    # ── Branch ownership ──
    t_owner: Dict[int, int] = {}
    f_owner: Dict[int, int] = {}

    for fs, ff in pairs:
        own_d = pair_depth[fs]
        block = [i for i in range(fs + 1, ff)
                 if i not in fsplit_set and i not in ffuse_set and nesting[i] == own_d]
        blk_toks = [tokens[i].value for i in block]
        t_a = next((j for j, t in enumerate(blk_toks) if t == Token.EVALT.value), None)
        f_a = next((j for j, t in enumerate(blk_toks) if t == Token.EVALF.value), None)
        if f_a is None:
            f_a = next((j for j, t in enumerate(blk_toks) if t == Token.AREV.value), None)
        if t_a is None:
            t_a = next((j for j, t in enumerate(blk_toks) if t == Token.AFWD.value), None)

        if t_a is not None and f_a is not None:
            if t_a < f_a:
                t_nodes, f_nodes = block[:f_a], block[f_a:]
            else:
                f_nodes, t_nodes = block[:t_a], block[t_a:]
        elif f_a is not None:
            t_nodes, f_nodes = [], block
        else:
            t_nodes, f_nodes = block, []

        for idx in t_nodes: t_owner[idx] = fs
        for idx in f_nodes: f_owner[idx] = fs

    # ── Lane assignment ──
    lanes: Dict[int, str] = {}
    for i in range(n):
        if i in t_owner:
            lanes[i] = "T"
        elif i in f_owner:
            lanes[i] = "F"
        else:
            lanes[i] = "main"

    # ── Position computation (sequential ordering preserves nesting structure) ──
    usable_w = SVG_W - 2 * MARGIN_X
    n_tokens = len(tokens)
    span = usable_w / max(n_tokens, 1)
    pos: Dict[int, Tuple[float, float]] = {}

    # Lane Y offsets: deeper nesting pushes branches further from main lane
    # Base lane centers: T=above, F=below, main=center
    # Each nesting level adds an offset so nested pairs are visually distinct
    LANE_OFFSET = 55  # pixels per nesting level
    max_nest = max(nesting.values()) if nesting else 0

    for i in range(n_tokens):
        x = MARGIN_X + i * span + span / 2  # center within each slot
        lane = lanes.get(i, "main")
        nest = nesting.get(i, 0)
        if lane == "T":
            y = Y_T - nest * LANE_OFFSET
        elif lane == "F":
            y = Y_F + nest * LANE_OFFSET
        else:
            y = Y_MAIN
        # Clamp Y to stay within SVG bounds
        y = max(70, min(SVG_H - 70, y))
        pos[i] = (x, y)

    # ── Pair index for each node (0-based into pairs list) ──
    pair_of: Dict[int, int] = {}
    for pi, (fs, ff) in enumerate(pairs):
        pair_of[fs] = pi
        pair_of[ff] = pi
        for i in range(fs + 1, ff):
            if t_owner.get(i) == fs or f_owner.get(i) == fs:
                pair_of[i] = pi

    # ── Pair wires index ──
    pair_wires: Dict[int, List[Wire]] = {pi: [] for pi in range(len(pairs))}
    for w in graph.wires:
        pi = pair_of.get(w.src_node)
        if pi is not None:
            pair_wires[pi].append(w)

    # ── IFIX barrier position ──
    ifix_pos: Optional[float] = None
    for i, tok in enumerate(tokens):
        if tok == Token.IFIX and i in pos:
            ifix_pos = pos[i][0]
            break

    return DiagramLayout(
        tokens=tokens, pos=pos, lanes=lanes, wires=graph.wires, n=n,
        states=states, nesting=nesting, pair_of=pair_of,
        ifix_pos=ifix_pos, pair_wires=pair_wires,
    )


# ── Enhanced Edge-Wire Decider ───────────────────────────────────────────────

def _wire_edge_category(src_tok: Token, dst_tok: Token, w: Wire) -> str:
    """Return the categorical edge flavor for a wire."""
    if w.src_port == 'T':
        return 'T-branch'
    if w.src_port == 'F':
        return 'F-branch'
    if src_tok == Token.AFWD:   return 'forward'
    if src_tok == Token.AREV:   return 'reverse'
    if src_tok == Token.CLINK:  return 'composition'
    if src_tok == Token.TANCH:  return 'boundary'
    if src_tok == Token.IMSCRIB: return 'identity'
    if src_tok == Token.VINIT:  return 'source'
    if src_tok == Token.FSPLIT: return 'fork-out'
    if src_tok == Token.FFUSE:  return 'join-out'
    if src_tok == Token.EVALT:  return 'T-pass'
    if src_tok == Token.EVALF:  return 'F-pass'
    if src_tok == Token.ENGAGR: return 'paradox'
    if src_tok == Token.IFIX:   return 'fixed'
    return 'linear'

# ── THE V3 RENDERER ─────────────────────────────────────────────────────────

def render_wiring_svg_v3(graph: WiredGraph, name: str = "", ourobor: str = "",
                          description: str = "", ig_type: str = "",
                          pen_mode: bool = False, topology_report: dict = None) -> SVGBuilder:
    """
    Render a complete wiring diagram as SVG with full edge granularity:

    1. Register-delta labels on every edge
    2. Categorical edge coloring (AFWD=green, AREV=coral, CLINK=amber, etc.)
    3. Nesting-depth opacity modulation
    4. IFIX barrier with edge-crossing tint
    5. Guard port markers (amber "approaching", green "passed")
    6. Pair-identity coloring (each FSPLIT/FFUSE pair gets unique hue family)
    7. CLINK compositional double-stroke
    """

    if pen_mode:
        return render_wiring_pen_svg(graph, name, ourobor, description, topology_report)

    layout = compute_layout(graph)
    tokens = layout.tokens
    n = layout.n
    states = layout.states
    pos = layout.pos

    svg = SVGBuilder()

    # ── Grid background (schematic feel) ──
    svg.draw_grid()

    # ── Title ──
    title = name.replace("_", " ") if name else ""
    svg.text(SVG_W/2, 26, title, 13, FG, "middle", True)
    if description:
        svg.text(SVG_W/2, 41, description[:155], 7, "#777", "middle")

    # ── Lane labels (depth-aware) ──
    has_T = any(layout.lanes.get(i) == "T" for i in range(n))
    has_F = any(layout.lanes.get(i) == "F" for i in range(n))
    max_nest_t = max((layout.nesting.get(i, 0) for i in range(n) if layout.lanes.get(i) == "T"), default=0)
    max_nest_f = max((layout.nesting.get(i, 0) for i in range(n) if layout.lanes.get(i) == "F"), default=0)
    if has_T:
        svg.lane_label(22, Y_T, "T-lane", "#20c0b0")
        for d in range(1, max_nest_t + 1):
            svg.lane_label(22, Y_T - d * 55, f"T[d{d}]", "#20c0b0")
    if has_F:
        svg.lane_label(22, Y_F, "F-lane", "#e04060")
        for d in range(1, max_nest_f + 1):
            svg.lane_label(22, Y_F + d * 55, f"F[d{d}]", "#e04060")
    svg.lane_label(22, Y_MAIN, "main", "#555")

    # ── Pairs for cross-branch detection and pair coloring ──
    pairs = match_pairs(tuple(t.value for t in tokens))
    fsplit_set = set(fs for fs, _ in pairs)
    ffuse_set = set(ff for _, ff in pairs)
    default_ff = {fs: ff for fs, ff in pairs}

    # Pair index lookup
    pair_idx_of = layout.pair_of

    # ── IFIX barrier ──
    if layout.ifix_pos is not None:
        svg.draw_ifix_barrier(layout.ifix_pos,
            min(p[1] for p in pos.values()) - NODE_R - 10,
            max(p[1] for p in pos.values()) + NODE_R + 10)

    # ── CHANNEL ASSIGNMENT (pre-pass to minimize vertical trunk overlap) ──
    # Group wires by (source_x, source_y, dest_y) and assign channel lanes.
    # Wires between the same y-levels get spread across channels 0,1,2,...
    # Backward wires (dx<0) get negative channels to exit left.
    channel_of: Dict[int, int] = {}
    wire_list = list(layout.wires)
    # Key: (src_layer, dst_lane) roughly — group by source x-region
    wire_groups: Dict[Tuple[int, str], list] = {}
    for wi, w in enumerate(wire_list):
        if w.src_node not in pos or w.dst_node not in pos:
            continue
        xs, ys = pos[w.src_node]
        xd, _ = pos[w.dst_node]
        lane = layout.lanes.get(w.src_node, "main")
        # Build a rough key: layer index (bucketed) + lane
        layer_key = (int(xs // 80), lane)
        wire_groups.setdefault(layer_key, []).append((wi, xs < xd))
    for grp_wires in wire_groups.values():
        fwd_wires = [w for w in grp_wires if w[1]]
        bwd_wires = [w for w in grp_wires if not w[1]]
        for ch, (wi, _) in enumerate(fwd_wires):
            channel_of[wi] = ch
        for ch, (wi, _) in enumerate(bwd_wires):
            channel_of[wi] = -(ch + 1)  # negative channels for backward
    # Also assign channels to wires not in any group
    for wi, w in enumerate(wire_list):
        if wi not in channel_of and w.src_node in pos and w.dst_node in pos:
            channel_of[wi] = 0

    # Track all path segments for crossing detection
    PathSeg = namedtuple("PathSeg", ["x1", "y1", "x2", "y2", "color", "wire_idx"])
    path_segments: List[PathSeg] = []

    def _record_ortho_segments(sx, sy, ex, ey, wire_idx, color):
        """Record the 3 segments of an orthogonal path for later crossing detection."""
        dx, dy = ex - sx, ey - sy
        if abs(dy) < 10:
            path_segments.append(PathSeg(sx, sy, ex, ey, color, wire_idx))
            return
        ch = channel_of.get(wire_idx, 0)
        ch_dx = ch * 8
        if dx > 0:
            mid_x = sx + max(18, min(35, dx * 0.35)) + ch_dx
        else:
            mid_x = sx - max(18, min(35, -dx * 0.35)) + ch_dx
        path_segments.append(PathSeg(sx, sy, mid_x, sy, color, wire_idx))
        path_segments.append(PathSeg(mid_x, sy, mid_x, ey, color, wire_idx))
        path_segments.append(PathSeg(mid_x, ey, ex, ey, color, wire_idx))

    # ── WIRES ── (edge-by-edge with full semantics) ────────────────────────
    for wi, w in enumerate(wire_list):
        if w.src_node not in pos or w.dst_node not in pos:
            continue
        xs, ys = pos[w.src_node]
        xd, yd = pos[w.dst_node]
        src_tok = tokens[w.src_node]
        dst_tok = tokens[w.dst_node]
        src_reg = states[w.src_node]
        dst_reg = states[w.dst_node]

        # ── Determine cross-branch ──
        is_cross = False
        if (src_tok == Token.FSPLIT and w.dst_node in ffuse_set
                and default_ff.get(w.src_node) != w.dst_node):
            is_cross = True

        # ── Nesting depth → opacity ──
        nest_d = layout.nesting.get(w.src_node, 0)
        base_opacity = {0: 0.75, 1: 0.55, 2: 0.40, 3: 0.30}.get(nest_d, 0.30)

        # ── IFIX barrier crossing ──
        crosses_ifix = False
        if layout.ifix_pos is not None:
            crosses_ifix = (xs < layout.ifix_pos < xd) or (xd < layout.ifix_pos < xs)

        # ── Edge midpoint (for labels) ──
        mx, my = (xs + xd) / 2, (ys + yd) / 2

        # ── Pair identity color ──
        pi = pair_idx_of.get(w.src_node)
        pair_color = None
        if pi is not None and pi < len(PAIR_PALETTE):
            pair_color = PAIR_PALETTE[pi][0] if w.src_port in ('T', 'o') else PAIR_PALETTE[pi][1]

        # ── CATEGORICAL ROUTING ──────────────────────────────────────────

        if w.src_port == 'T':
            # T-branch wire — use pair color if available, else T_COLOR
            color = pair_color or T_COLOR
            ch = channel_of.get(wi, 0)
            _record_ortho_segments(xs, ys, xd, yd, wi, color)
            if is_cross:
                svg.draw_orthogonal_arrow(xs, ys, xd, yd, CROSS_COLOR, 1.5, base_opacity, "5,3", ch)
            else:
                svg.draw_orthogonal_arrow(xs, ys, xd, yd, color, 1.4, base_opacity, None, ch)

        elif w.src_port == 'F':
            color = pair_color or F_COLOR
            ch = channel_of.get(wi, 0)
            _record_ortho_segments(xs, ys, xd, yd, wi, color)
            if is_cross:
                svg.draw_orthogonal_arrow(xs, ys, xd, yd, CROSS_COLOR, 1.5, base_opacity, "5,3", ch)
                svg.line(xs, ys, xd, yd, CROSS_COLOR, 1.5, "5,3", 0.5)
            else:
                svg.draw_orthogonal_arrow(xs, ys, xd, yd, color, 1.4, base_opacity, None, ch)

        else:
            # Main-lane: categorical edge coloring + orthogonal (Manhattan) routing
            cat = _wire_edge_category(src_tok, dst_tok, w)
            color = CAT_EDGE_COLOR.get(src_tok, MAIN_COLOR)
            dash = CAT_EDGE_STYLE.get(src_tok, None)

            if crosses_ifix:
                base_opacity = base_opacity * 0.6
                # Add a subtle red tint at the crossing point
                svg.circle_node(layout.ifix_pos, my, 3, IFIX_COLOR, None, 0.4)

            ch = channel_of.get(wi, 0)
            _record_ortho_segments(xs, ys, xd, yd, wi, color)
            if src_tok == Token.CLINK:
                svg.draw_orthogonal_double_arrow(xs, ys, xd, yd, color, 1.0, base_opacity, ch)
            else:
                svg.draw_orthogonal_arrow(xs, ys, xd, yd, color, 1.3, base_opacity, dash, ch)

        # ── Register delta label ──
        if src_reg is not None and dst_reg is not None:
            delta = reg_delta_label(src_reg, dst_reg)
            d_color = reg_delta_color(src_reg, dst_reg)
            # Only show label if there's a change or BOTH involvement
            if src_reg != dst_reg or BOTH in (src_reg, dst_reg):
                svg.draw_edge_label(mx, my, delta, d_color, 6)

    # ── CROSSING DETECTION & BRIDGES ─────────────────────────────────
    # Detect where orthogonal path segments cross and draw bridge indicators.
    # A crossing occurs when a horizontal segment H and a vertical segment V intersect.
    crossings_found = set()  # (cx, cy) rounded to nearest pixel
    for i, si in enumerate(path_segments):
        for j, sj in enumerate(path_segments):
            if i >= j:
                continue
            if si.wire_idx == sj.wire_idx:
                continue
            # Determine which is horizontal and which is vertical
            si_horiz = abs(si.y1 - si.y2) < 2
            sj_horiz = abs(sj.y1 - sj.y2) < 2
            if si_horiz == sj_horiz:
                continue  # both horizontal or both vertical — no crossing
            if si_horiz:
                H, V = si, sj
            else:
                H, V = sj, si
            hx1, hx2 = min(H.x1, H.x2), max(H.x1, H.x2)
            hy = H.y1
            vx = V.x1
            vy1, vy2 = min(V.y1, V.y2), max(V.y1, V.y2)
            margin = 3  # must be strictly interior
            if hx1 + margin < vx < hx2 - margin and vy1 + margin < hy < vy2 - margin:
                cx, cy = round(vx), round(hy)
                key = (cx, cy)
                if key not in crossings_found:
                    crossings_found.add(key)
                    # Determine which wire goes "over" (the one drawn later, i.e., higher j)
                    over_color = sj.color if not sj_horiz else si.color
                    # Use the earlier wire's color for the under dot
                    under_color = si.color if not sj_horiz else sj.color
                    svg.draw_crossing_bridge(cx, cy, under_color, over_color)

    # ── Empty branch arcs ──
    for fs, ff in pairs:
        if fs not in pos or ff not in pos: continue
        x_fs, y_fs = pos[fs]; x_ff, y_ff = pos[ff]
        t_direct = any(w.src_node == fs and w.dst_node == ff and w.src_port == 'T'
                       for w in layout.wires)
        f_direct = any(w.src_node == fs and w.dst_node == ff and w.src_port == 'F'
                       for w in layout.wires)
        if t_direct:
            pi = pair_idx_of.get(fs, -1)
            ec = PAIR_PALETTE[pi][0] if 0 <= pi < len(PAIR_PALETTE) else "#226666"
            svg.curve_empty_arc(x_fs, y_fs, x_ff, y_ff, Y_T, ec)
        if f_direct:
            pi = pair_idx_of.get(fs, -1)
            ec = PAIR_PALETTE[pi][1] if 0 <= pi < len(PAIR_PALETTE) else "#663333"
            svg.curve_empty_arc(x_fs, y_fs, x_ff, y_ff, Y_F, ec)

    # ── NODES ────────────────────────────────────────────────────────
    for i in range(n):
        if i not in pos: continue
        cx, cy = pos[i]
        tok = tokens[i]
        fam = TOKEN_FAMILY[tok.value]
        fill = FAM_COLOR[fam]
        reg = states[i]

        # Node shape by family
        if fam == 1:       svg.diamond_node(cx, cy, NODE_R, fill)
        elif fam == 2:     svg.hexagon_node(cx, cy, NODE_R, fill)
        elif fam == 3:     svg.square_node(cx, cy, NODE_R, fill)
        else:              svg.circle_node(cx, cy, NODE_R, fill)

        # Register state tint (inner)
        if reg != VOID:
            inner_r = NODE_R * 0.55
            svg.circle_node(cx, cy, inner_r, REG_COLOR[reg], None, 0)
            svg.text(cx, cy + 2, REG_LABEL[reg], 7,
                     {TRUE: "#20b2aa", FALSE: "#cc4455", BOTH: "#ffd700"}.get(reg, "#666"),
                     "middle", True)

        # Token labels
        label_color = "#000" if fam == 1 else "#fff"
        svg.text(cx, cy - NODE_R - 8, TOKEN_SHORT[tok.value], 8, FG, "middle", True)
        svg.text(cx, cy + NODE_R + 12, TOKEN_NAMES[tok.value], 5.5, "#888", "middle")

        # ── GUARD PORT MARKERS (dimension 5) ───────────────────────────
        if tok == Token.EVALT or tok == Token.EVALF:
            # Input port: amber = "approaching gate"
            svg.circle_node(cx - NODE_R - 1, cy, 3.5, "#f28e2b", None, 0.8)
            # Output port: green = "passed gate"
            svg.circle_node(cx + NODE_R + 1, cy, 3.5, "#59a14f", None, 0.9)
        elif tok == Token.FFUSE:
            # Two input port dots (standard)
            svg.circle_node(cx - NODE_R - 1, cy - 7, 2.5, "#ffffff60", None, 0)
            svg.circle_node(cx - NODE_R - 1, cy + 7, 2.5, "#ffffff60", None, 0)
            # Output port
            svg.circle_node(cx + NODE_R + 1, cy, 2.5, "#ffffff90", None, 0)
        elif tok == Token.FSPLIT:
            # Input port
            svg.circle_node(cx - NODE_R - 1, cy, 2.5, "#ffffff60", None, 0)
            # Two output port dots
            svg.circle_node(cx + NODE_R + 1, cy - 7, 2.5, "#ffffff90", None, 0)
            svg.circle_node(cx + NODE_R + 1, cy + 7, 2.5, "#ffffff90", None, 0)
        elif tok == Token.VINIT:
            # Only output port
            svg.circle_node(cx + NODE_R + 1, cy, 2.5, "#ffffff90", None, 0)
        else:
            # Standard input/output
            svg.circle_node(cx - NODE_R - 1, cy, 2.5, "#ffffff60", None, 0)
            svg.circle_node(cx + NODE_R + 1, cy, 2.5, "#ffffff90", None, 0)

    # ── Ouroboric back-arc ──
    if ourobor and ourobor != "O₀" and len(pos) >= 2:
        i0, iN = min(pos), max(pos)
        if i0 in pos and iN in pos:
            x0, y0 = pos[i0]; xn, yn = pos[iN]
            svg.curve_arrow(x0, y0, xn, yn, BACK_COLOR, 1.5, 0.5, 55)
            svg.text((x0+xn)/2, min(y0, yn) - 70, ourobor, 8, "#9988cc", "middle", False, "serif")

    # ── Footer ──
    if ig_type:
        svg.text(SVG_W/2, SVG_H - 22, ig_type, 7, "#5577aa", "middle", False, "monospace")
    if ourobor:
        svg.text(SVG_W/2, SVG_H - 9, f"Ouroboricity: {ourobor}", 7, "#9988aa", "middle", False, "serif")

    # ── Legend (horizontal strip at top) ─────────────────────────────────
    LEG_Y = LEGEND_Y
    lx = MARGIN_X
    
    # Row 1: NODES
    svg.text(lx, LEG_Y, "NODES", 6, "#666", "start", True)
    lx += 40
    for fi in range(4):
        if fi == 0:   svg.circle_node(lx, LEG_Y + 7, 4.5, FAM_COLOR[fi], None, 0)
        elif fi == 1: svg.diamond_node(lx, LEG_Y + 7, 4.5, FAM_COLOR[fi])
        elif fi == 2: svg.hexagon_node(lx, LEG_Y + 7, 4.5, FAM_COLOR[fi])
        else:         svg.square_node(lx, LEG_Y + 7, 4.5, FAM_COLOR[fi])
        svg.text(lx + 10, LEG_Y + 10, FAM_NAME[fi][:4], 5, FAM_COLOR[fi], "start")
        lx += 48
    lx += 10
    
    # Row 1: EDGES
    svg.text(lx, LEG_Y, "EDGES", 6, "#666", "start", True)
    lx += 38
    edge_legends = [
        (CAT_EDGE_COLOR[Token.AFWD], "AFWD"),
        (CAT_EDGE_COLOR[Token.AREV], "AREV"),
        (CAT_EDGE_COLOR[Token.CLINK], "CLINK"),
        (CAT_EDGE_COLOR[Token.TANCH], "TANCH"),
        (CAT_EDGE_COLOR[Token.IMSCRIB], "IMSC"),
        (CAT_EDGE_COLOR[Token.IFIX], "IFIX"),
    ]
    for color, label in edge_legends:
        svg.line(lx, LEG_Y + 7, lx + 14, LEG_Y + 7, color, 1.5,
                 "4,3" if label == "TANCH" else None, 0.7)
        svg.text(lx + 18, LEG_Y + 10, label, 5, color, "start")
        lx += 52
    lx += 6
    
    # Row 2: GUARDS
    LEG_Y2 = LEG_Y + 16
    lx = MARGIN_X
    svg.text(lx, LEG_Y2 + 4, "GUARD", 6, "#666", "start", True)
    lx += 40
    svg.circle_node(lx, LEG_Y2 + 11, 3, "#f28e2b", None, 0.8)
    svg.text(lx + 7, LEG_Y2 + 14, "approach", 5, "#f28e2b", "start")
    lx += 52
    svg.circle_node(lx, LEG_Y2 + 11, 3, "#59a14f", None, 0.9)
    svg.text(lx + 7, LEG_Y2 + 14, "passed", 5, "#59a14f", "start")
    lx += 52
    
    # Row 2: REG Δ
    svg.text(lx, LEG_Y2 + 4, "REG Δ", 6, "#666", "start", True)
    lx += 38
    svg.text(lx, LEG_Y2 + 14, "→↑", 5.5, "#20b888", "start"); lx += 28
    svg.text(lx, LEG_Y2 + 14, "↓→↑↓", 5.5, "#ffd700", "start"); lx += 28
    svg.text(lx, LEG_Y2 + 14, "↑↔↓", 5.5, "#e15759", "start"); lx += 32
    
    # Row 2: CROSS / LOOP
    lx += 4
    svg.line(lx, LEG_Y2 + 11, lx + 14, LEG_Y2 + 11, CROSS_COLOR, 1.5, "5,3", 0.6)
    svg.text(lx + 18, LEG_Y2 + 14, "cross-br.", 5.5, CROSS_COLOR, "start")
    lx += 60
    svg.line(lx, LEG_Y2 + 11, lx + 14, LEG_Y2 + 11, BACK_COLOR, 1.5, None, 0.5)
    svg.text(lx + 18, LEG_Y2 + 14, "loop", 5.5, BACK_COLOR, "start")


    # ── NESTING BOUNDING BOXES ──────────────────────────────────────
    # Draw translucent rounded rectangles around each FSPLIT/FFUSE pair
    # to visually delineate nesting structure. Deeper nesting = more transparent
    # and thinner stroke.
    _pair_colors = [
        "#4e79a7", "#70ad47", "#ed7d31", "#e15759",
        "#9b59b6", "#20c0b0", "#ffd700", "#ff6688",
        "#6baed6", "#74c476", "#fd8d3c", "#e6550d",
    ]
    for pi, (fs, ff) in enumerate(pairs):
        if fs not in pos or ff not in pos:
            continue
        x1, y1 = pos[fs]
        x2, y2 = pos[ff]
        nest_d = layout.nesting.get(fs, 0)
        bbox_x = min(x1, x2) - NODE_R - 6
        bbox_y = min(y1, y2) - NODE_R - 6
        bbox_w = abs(x2 - x1) + 2 * (NODE_R + 6)
        bbox_h = abs(y2 - y1) + 2 * (NODE_R + 6)
        bbox_color = _pair_colors[pi % len(_pair_colors)]
        bbox_opacity = max(0.08, 0.25 - nest_d * 0.05)
        stroke_w = max(0.5, 1.5 - nest_d * 0.3)
        svg.add("rect", {
            "x": str(bbox_x), "y": str(bbox_y),
            "width": str(bbox_w), "height": str(bbox_h),
            "fill": "none", "stroke": bbox_color,
            "stroke-width": str(stroke_w),
            "opacity": str(bbox_opacity),
            "rx": "8", "ry": "8",
            "stroke-dasharray": "4,3"
        })
        # Label the pair with its nesting depth
        label_x = bbox_x + 4
        label_y = bbox_y - 2
        svg.text(label_x, label_y, f"d{nest_d}", 5, bbox_color, "start", False, "monospace")

    # ── TOPOLOGY OVERLAY (from TopologyReport) ────────────────────────
    if topology_report:
        tc = topology_report.get("topology_class", "flat_chain")
        nd = topology_report.get("nesting_depth", 0)
        of = topology_report.get("open_forks", 0)
        cb = topology_report.get("cross_branches", 0)
        eb = topology_report.get("empty_branches", 0)
        t_ops = topology_report.get("t_branch_ops", 0)
        f_ops = topology_report.get("f_branch_ops", 0)
        nf = topology_report.get("has_negation_first", False)
        ci = topology_report.get("has_cascading_ifix", False)
        mic = topology_report.get("max_ifix_cascade", 0)
        df = topology_report.get("has_dual_fixation", False)

        # Topology class banner (top-right corner)
        tc_colors = {
            "flat_chain": "#4e79a7", "nested": "#70ad47",
            "open_fork_dag": "#ed7d31", "webbed": "#e15759",
            "mixed": "#9b59b6"
        }
        tc_color = tc_colors.get(tc, "#4e79a7")
        bx, by = SVG_W - 160, 48
        svg.add("rect", {"x": str(bx), "y": str(by), "width": "145", "height": "22",
                         "fill": tc_color, "opacity": "0.15", "rx": "4"})
        svg.add("rect", {"x": str(bx), "y": str(by), "width": "145", "height": "22",
                         "fill": "none", "stroke": tc_color, "stroke-width": "1", "rx": "4"})
        svg.text(bx + 72, by + 15, tc.upper(), 8, tc_color, "middle", True)

        # Topology stats row
        sy = by + 30
        stats_parts = [f"depth:{nd}", f"open-forks:{of}", f"cross:{cb}", f"empty:{eb}"]
        svg.text(bx, sy, "  ".join(stats_parts), 6, "#888", "start", False, "monospace")

        # Branch weight ratio bar (T vs F)
        bar_y = sy + 10
        total_ops = max(1, t_ops + f_ops)
        t_frac = t_ops / total_ops
        f_frac = f_ops / total_ops
        bar_w = 145
        svg.text(bx, bar_y - 2, f"T:{t_ops} / F:{f_ops}", 5.5, "#777", "start", False, "monospace")
        svg.add("rect", {"x": str(bx), "y": str(bar_y), "width": str(bar_w * t_frac),
                         "height": "6", "fill": T_COLOR, "opacity": "0.6", "rx": "2"})
        svg.add("rect", {"x": str(bx + bar_w * t_frac), "y": str(bar_y), "width": str(bar_w * f_frac),
                         "height": "6", "fill": F_COLOR, "opacity": "0.6", "rx": "2"})

        # Modifier badges
        badge_y = bar_y + 14
        badges = []
        if nf: badges.append(("NEG-1ST", "#ff6688"))
        if ci: badges.append((f"IFIX×{mic}", "#cc3344"))
        if df: badges.append(("DUAL-FIX", "#ffd700"))
        for i, (label, color) in enumerate(badges):
            bxx = bx + i * 55
            svg.add("rect", {"x": str(bxx), "y": str(badge_y), "width": "50", "height": "12",
                             "fill": color, "opacity": "0.2", "rx": "2"})
            svg.text(bxx + 25, badge_y + 9, label, 5.5, color, "middle", True, "monospace")

        # Open fork endpoint markers — draw small open circles at unmatched FSPLIT positions
        fork_positions = topology_report.get("fork_positions", [])
        for fp in fork_positions:
            if isinstance(fp, (list, tuple)) and len(fp) >= 1:
                fi = fp[0] if isinstance(fp[0], int) else fp[0]
                if fi in pos:
                    fx, fy = pos[fi]
                    # Open diamond = unmatched fork (never fuses)
                    svg.add("polygon", {
                        "points": _diamond_points(fx, fy + NODE_R + 18, 5),
                        "fill": "none", "stroke": "#ed7d31", "stroke-width": "1.5",
                        "opacity": "0.8"
                    })
                    svg.text(fx, fy + NODE_R + 30, "open", 4.5, "#ed7d31", "middle")

    svg.close()
    return svg


# ── Canonical sequences ─────────────────────────────────────────────────────
CANONICALS: Dict[str, dict] = {
    "I_Dialetheic_Bootstrap": {
        "tokens": (5, 8, 6, 9, 7, 10, 11, 5),
        "ourobor": "O₂",
        "ig_type": "⟨𐑦𐑸𐑾𐑬𐑐𐑧𐑲𐑠𐑻𐑫𐑳𐑴⟩",
        "desc": "Self-ref, Frobenius-closed, dialetheia-complete. Split→fuse, all three truth values."
    },
    "II_Void_Genesis": {
        "tokens": (0, 1, 2, 6, 4, 7, 11, 5),
        "ourobor": "O₀",
        "ig_type": "⟨𐑨𐑡𐑑𐑗𐑱𐑘𐑔𐑝𐑢𐑓𐑙𐑷⟩",
        "desc": "Creation ex nihilo. VINIT→TANCH→AFWD→FSPLIT→CLINK→FFUSE→IFIX→IMSCRIB."
    },
    "III_Anchor_Protocol": {
        "tokens": (1, 3, 0, 2, 1, 4, 11, 5),
        "ourobor": "O₁",
        "ig_type": "⟨𐑨𐑰𐑾𐑬𐑱𐑤𐑚𐑜𐑢𐑒𐑙𐑴⟩",
        "desc": "Period-3 sabbath cycle. TANCH→AREV→VINIT→AFWD→TANCH→CLINK→IFIX→IMSCRIB."
    },
    "IV_Dual_Bootstrap": {
        "tokens": (5, 2, 7, 6, 3, 4, 11, 5),
        "ourobor": "O_∞",
        "ig_type": "⟨𐑦𐑸𐑾𐑹𐑐𐑧𐑲𐑝⊙𐑖𐑳𐑭⟩",
        "desc": "Inverted Frobenius. Fuse BEFORE split. μ∘δ=id in reverse temporal order."
    },
    "V_Linear_Chain": {
        "tokens": (11,)*8,
        "ourobor": "O₀",
        "ig_type": "⟨𐑛𐑡𐑩𐑗𐑱𐑘𐑔𐑝𐑢𐑓𐑙𐑷⟩",
        "desc": "Pure recording. Eight IFIX in a row — the atom of linear logic."
    },
    "VI_Empty_Bootstrap": {
        "tokens": (0, 5, 0, 5, 0, 5, 0, 5),
        "ourobor": "O₁",
        "ig_type": "⟨𐑦𐑥𐑾𐑿𐑐𐑤𐑲𐑝⊙𐑒𐑙𐑷⟩",
        "desc": "Period-2 oscillation. VINIT↔IMSCRIB — void↔identity heartbeat."
    },
    "VII_Parakernel": {
        "tokens": (9, 3, 6, 8, 2, 7, 10, 11),
        "ourobor": "O₂",
        "ig_type": "⟨𐑦𐑸𐑾𐑬𐑐𐑧𐑲𐑟𐑻𐑫𐑳𐑴⟩",
        "desc": "Engram of contradiction. EVALF→AREV→FSPLIT→EVALT→AFWD→FFUSE→ENGAGR→IFIX."
    },
    "VIII_Frobenius_Kernel": {
        "tokens": (0, 6, 7, 1),
        "ourobor": "O₀",
        "ig_type": "⟨𐑛𐑡𐑩𐑗𐑱𐑘𐑚𐑝𐑢𐑓𐑙𐑷⟩",
        "desc": "Minimal Frobenius-closed: VINIT→FSPLIT→FFUSE→TANCH. The atom of verification."
    },
    "IX_Chiral_Pairs": {
        "tokens": (2, 3, 2, 3, 2, 3, 2, 3),
        "ourobor": "O₁",
        "ig_type": "⟨𐑦𐑡𐑑𐑗𐑱𐑘𐑚𐑝⊙𐑒𐑙𐑷⟩",
        "desc": "Period-2 AFWD↔AREV alternation — pure handedness without content."
    },
    "X_Truth_Machine": {
        "tokens": (5, 6, 8, 11, 5, 6, 9, 11),
        "ourobor": "O₁",
        "ig_type": "⟨𐑦𐑡𐑩𐑗𐑱𐑘𐑚𐑜𐑢𐑓𐑳𐑷⟩",
        "desc": "Binary classifier. Two parallel FSPLIT paths: true→IFIX, false→IFIX. No FFUSE."
    },
    "XI_Eternal_Return": {
        "tokens": (5, 2, 3, 5, 2, 3, 5, 2),
        "ourobor": "O₂",
        "ig_type": "⟨𐑦𐑸𐑾𐑗𐑐𐑤𐑲𐑝⊙𐑖𐑳𐑷⟩",
        "desc": "Unclosed period-3. IMSCRIB→AFWD→AREV repeated, truncated — always becoming."
    },
    "XII_ROM_Burn": {
        "tokens": (8, 11, 9, 11, 10, 11, 5, 11),
        "ourobor": "O₀",
        "ig_type": "⟨𐑨𐑡𐑩𐑗𐑱𐑪𐑚𐑝𐑢𐑒𐑳𐑷⟩",
        "desc": "Truth-value burn. EVALT→IFIX, EVALF→IFIX, ENGAGR→IFIX, IMSCRIB→IFIX."
    },
}

# ═══════════════════════════════════════════════════════════════════════════
# PEN MODE — black-and-white pen-on-paper renderer (per READING_GUIDE.md)
# Distinct renderer, not a recolor: unfilled family shapes, 12 token line
# patterns, inner register hatch fills, midpoint glyphs, guard ports, IFIX
# barrier, pair brackets, and a vertical left-side legend. Reproducible by hand.
# ═══════════════════════════════════════════════════════════════════════════

PEN_INK  = "#ffffff"
PEN_GRID = "#333333"
PEN_W    = 1220
PEN_NODE_R = 20
FAM_SHAPE = {0: "circle", 1: "diamond", 2: "hexagon", 3: "square"}

# per source-token edge style: (dash, base_width, arrow, mid_glyph)
_PEN_EDGE = {
    Token.VINIT.value:   (None,             1.5, "open",    None),
    Token.TANCH.value:   ("5,2,1,2,1,2",    1.5, "open",    None),
    Token.AFWD.value:    (None,             2.5, "filled",  None),
    Token.AREV.value:    ("6,4",            1.5, "filled",  None),
    Token.CLINK.value:   ("double",         1.0, "filled",  None),
    Token.IMSCRIB.value: (None,             1.5, "reverse", "←"),
    Token.FSPLIT.value:  (None,             1.5, "filled",  "◇"),
    Token.FFUSE.value:   (None,             1.5, "filled",  "●"),
    Token.EVALT.value:   (None,             1.5, "filled",  "+"),
    Token.EVALF.value:   (None,             1.5, "filled",  "×"),
    Token.ENGAGR.value:  ("zigzag",         1.5, "filled",  None),
    Token.IFIX.value:    ("2,2",            1.5, "filled",  None),
}
_PEN_DEPTH_W = {0: 2.0, 1: 1.5, 2: 1.0, 3: 0.5}


def _pen_shape(svg: 'SVGBuilder', shape: str, cx: float, cy: float, r: float,
               fill: str = "none", sw: float = 1.3):
    a = {"fill": fill, "stroke": PEN_INK, "stroke-width": str(sw)}
    if shape == "circle":
        svg.add("circle", {**a, "cx": f"{cx:.1f}", "cy": f"{cy:.1f}", "r": f"{r:.1f}"})
    elif shape == "diamond":
        svg.add("polygon", {**a, "points": _diamond_points(cx, cy, r)})
    elif shape == "hexagon":
        svg.add("polygon", {**a, "points": _hexagon_points(cx, cy, r)})
    else:  # square
        svg.add("rect", {**a, "x": f"{cx-r:.1f}", "y": f"{cy-r:.1f}",
                         "width": f"{2*r:.1f}", "height": f"{2*r:.1f}"})


def _pen_zigzag(x1, y1, x2, y2, amp=4, step=8):
    L = math.hypot(x2 - x1, y2 - y1) or 1
    ux, uy = (x2 - x1) / L, (y2 - y1) / L
    px, py = -uy, ux
    pts, d, sign = [], 0.0, 1
    while d < L:
        cx, cy = x1 + ux * d, y1 + uy * d
        pts.append(f"{cx + px*amp*sign:.1f},{cy + py*amp*sign:.1f}")
        sign *= -1; d += step
    pts.append(f"{x2:.1f},{y2:.1f}")
    return " ".join(pts)


def _pen_return_target(tokens, last: int, pos) -> int:
    """The node the closure arc returns to. A sequence bootstraps from its start
    token but re-enters at the identity anchor: the first IMSCRIB (self-imscription)
    if one exists and isn't the final node; otherwise the first node. This is why a
    VINIT-start canon returns to IMSCRIB rather than to VINIT."""
    for i in range(len(tokens)):
        if i in pos and i != last and tokens[i].value == Token.IMSCRIB.value:
            return i
    return min(pos)


def _pen_backarc(svg: 'SVGBuilder', src, tgt, label: str, r: float = PEN_NODE_R):
    """Solid ouroboric back-arc from the final node, arcing above the diagram,
    with an arrowhead pointing down into the return-anchor node."""
    xs, ys = src; xt, yt = tgt
    top = max(58, min(ys, yt) - 78)
    y1, y2 = ys - r, yt - r
    svg.add("path", {"d": f"M {xs:.1f},{y1:.1f} C {xs:.1f},{top:.1f} {xt:.1f},{top:.1f} {xt:.1f},{y2:.1f}",
                     "fill": "none", "stroke": PEN_INK, "stroke-width": "1.0"})
    svg.add("polygon", {"points": _arrow_head_points(xt, y2, xt, top, 8), "fill": PEN_INK})
    if label:
        svg.text((xs + xt) / 2, top - 4, label, 7, PEN_INK, "middle")


def render_wiring_pen_svg(graph: WiredGraph, name: str = "", ourobor: str = "",
                          description: str = "", topology_report: dict = None) -> SVGBuilder:
    """Black-and-white pen diagram. Same layout engine as the color renderer;
    every colour dimension is re-expressed as a pen-drawable form."""
    layout = compute_layout(graph)
    tokens, n, states, pos = layout.tokens, layout.n, layout.states, layout.pos

    svg = SVGBuilder(w=PEN_W)
    svg.parts[1] = f'<rect width="{PEN_W}" height="{SVG_H}" fill="#000000"/>'

    # ── register-state hatch patterns ──
    svg.add_def('<pattern id="hatch-T" width="4" height="4" patternUnits="userSpaceOnUse">'
                f'<path d="M2,0 L2,4" stroke="{PEN_INK}" stroke-width="0.8"/></pattern>')
    svg.add_def('<pattern id="hatch-F" width="4" height="4" patternUnits="userSpaceOnUse">'
                f'<path d="M0,2 L4,2" stroke="{PEN_INK}" stroke-width="0.8"/></pattern>')
    svg.add_def('<pattern id="hatch-B" width="4" height="4" patternUnits="userSpaceOnUse">'
                f'<path d="M2,0 L2,4 M0,2 L4,2" stroke="{PEN_INK}" stroke-width="0.8"/></pattern>')
    _HATCH = {1: "url(#hatch-T)", 2: "url(#hatch-F)", 3: "url(#hatch-B)"}

    # ── faint grid ──
    for gx in range(0, PEN_W, GRID_SPACING):
        svg.line(gx, 0, gx, SVG_H, stroke=PEN_GRID, width=0.4, opacity=0.3)
    for gy in range(0, SVG_H, GRID_SPACING):
        svg.line(0, gy, PEN_W, gy, stroke=PEN_GRID, width=0.4, opacity=0.3)

    # ── title ──
    title = name.replace("_", " ") if name else ""
    svg.text(PEN_W/2, 26, title, 13, PEN_INK, "middle", True)
    if description:
        svg.text(PEN_W/2, 41, description[:155], 7, PEN_INK, "middle")

    # ── lane labels (depth-aware) ──
    has_T = any(layout.lanes.get(i) == "T" for i in range(n))
    has_F = any(layout.lanes.get(i) == "F" for i in range(n))
    max_nest_t = max((layout.nesting.get(i, 0) for i in range(n) if layout.lanes.get(i) == "T"), default=0)
    max_nest_f = max((layout.nesting.get(i, 0) for i in range(n) if layout.lanes.get(i) == "F"), default=0)
    if has_T:
        svg.text(66, Y_T, "T-lane", 7, PEN_INK, "start")
        for d in range(1, max_nest_t + 1):
            svg.text(66, Y_T - d * 55, f"T[d{d}]", 7, PEN_INK, "start")
    if has_F:
        svg.text(66, Y_F, "F-lane", 7, PEN_INK, "start")
        for d in range(1, max_nest_f + 1):
            svg.text(66, Y_F + d * 55, f"F[d{d}]", 7, PEN_INK, "start")
    svg.text(66, Y_MAIN, "main", 7, PEN_INK, "start")

    # ── IFIX barrier (double vertical + × markers) ──
    if layout.ifix_pos is not None:
        bx = layout.ifix_pos
        _y_top = min(p[1] for p in pos.values()) - PEN_NODE_R - 10
        _y_bot = max(p[1] for p in pos.values()) + PEN_NODE_R + 10
        for off in (-2.5, 2.5):
            svg.line(bx + off, _y_top, bx + off, _y_bot, stroke=PEN_INK,
                     width=1.0, dash="4,3", opacity=1.0)
        for yy in (_y_top, _y_bot):
            svg.text(bx, yy, "×", 8, PEN_INK, "middle")
        svg.text(bx, _y_top - 7, "IFIX", 6, PEN_INK, "middle")

    # ── pair brackets (dashed arc + circled numeral) ──
    for fs, ff in match_pairs(tuple(t.value for t in tokens)):
        if fs in pos and ff in pos:
            (xs, ys), (xd, yd) = pos[fs], pos[ff]
            yb = min(ys, yd) - 38
            svg.line(xs, ys - PEN_NODE_R, xs, yb, stroke=PEN_INK, width=0.6, dash="3,3", opacity=0.8)
            svg.line(xs, yb, xd, yb, stroke=PEN_INK, width=0.6, dash="3,3", opacity=0.8)
            svg.line(xd, yb, xd, yd - PEN_NODE_R, stroke=PEN_INK, width=0.6, dash="3,3", opacity=0.8)
            pi = (layout.pair_of.get(fs, 0)) + 1
            mxb = (xs + xd) / 2
            svg.add("circle", {"cx": f"{mxb:.1f}", "cy": f"{yb:.1f}", "r": "6",
                               "fill": "#000000", "stroke": PEN_INK, "stroke-width": "0.8"})
            svg.text(mxb, yb + 3, str(pi), 7, PEN_INK, "middle")

    # ── wires ──
    for w in layout.wires:
        if w.src_node not in pos or w.dst_node not in pos:
            continue
        xs, ys = pos[w.src_node]; xd, yd = pos[w.dst_node]
        tokv = tokens[w.src_node].value
        dash, base_w, arrow, glyph = _PEN_EDGE.get(tokv, (None, 1.5, "filled", None))
        depth = layout.nesting.get(w.src_node, 0)
        width = _PEN_DEPTH_W.get(min(depth, 3), 1.0)
        if tokv == Token.AFWD.value:
            width = max(width, 2.5)
        # shorten to node borders
        L = math.hypot(xd - xs, yd - ys) or 1
        ux, uy = (xd - xs) / L, (yd - ys) / L
        sx, sy = xs + ux * PEN_NODE_R, ys + uy * PEN_NODE_R
        ex, ey = xd - ux * PEN_NODE_R, yd - uy * PEN_NODE_R
        if dash == "double":
            px, py = -uy, ux
            for o in (-1.6, 1.6):
                svg.line(sx + px*o, sy + py*o, ex + px*o, ey + py*o, stroke=PEN_INK, width=width, opacity=1.0)
        elif dash == "zigzag":
            svg.add("polyline", {"points": _pen_zigzag(sx, sy, ex, ey), "fill": "none",
                                 "stroke": PEN_INK, "stroke-width": str(width)})
        else:
            svg.line(sx, sy, ex, ey, stroke=PEN_INK, width=width, dash=dash, opacity=1.0)
        # arrowhead
        if arrow == "filled":
            svg.add("polygon", {"points": _arrow_head_points(ex, ey, sx, sy, 8), "fill": PEN_INK})
        elif arrow == "open":
            svg.add("polyline", {"points": _arrow_head_points(ex, ey, sx, sy, 8),
                                 "fill": "none", "stroke": PEN_INK, "stroke-width": "1.0"})
        elif arrow == "reverse":
            svg.add("polygon", {"points": _arrow_head_points(sx, sy, ex, ey, 8), "fill": PEN_INK})
        # midpoint glyph
        if glyph:
            svg.add("circle", {"cx": f"{(sx+ex)/2:.1f}", "cy": f"{(sy+ey)/2:.1f}", "r": "5",
                               "fill": "#000000", "stroke": PEN_INK, "stroke-width": "0.6"})
            svg.text((sx+ex)/2, (sy+ey)/2 + 3, glyph, 7, PEN_INK, "middle")
        # register delta label
        lbl = reg_delta_label(states[w.src_node], states[w.dst_node])
        if lbl and lbl != "=":
            svg.text((sx+ex)/2, (sy+ey)/2 - 8, lbl, 6, PEN_INK, "middle")

    # ── nodes ──
    for i in range(n):
        if i not in pos:
            continue
        cx, cy = pos[i]
        fam = TOKEN_FAMILY[tokens[i].value]
        _pen_shape(svg, FAM_SHAPE.get(fam, "circle"), cx, cy, PEN_NODE_R)
        # inner register hatch
        reg = states[i]
        if reg in _HATCH:
            svg.add("circle", {"cx": f"{cx:.1f}", "cy": f"{cy:.1f}", "r": "8",
                               "fill": _HATCH[reg], "stroke": PEN_INK, "stroke-width": "0.6"})
        # guard ports: open (input, left), filled (output, right)
        svg.add("circle", {"cx": f"{cx-PEN_NODE_R-4:.1f}", "cy": f"{cy:.1f}", "r": "2.5",
                           "fill": "#000000", "stroke": PEN_INK, "stroke-width": "0.8"})
        svg.add("circle", {"cx": f"{cx+PEN_NODE_R+4:.1f}", "cy": f"{cy:.1f}", "r": "2.5", "fill": PEN_INK})
        # labels: 2-letter above, full name below
        svg.text(cx, cy - PEN_NODE_R - 6, TOKEN_SHORT[tokens[i].value], 9, PEN_INK, "middle", True)
        svg.text(cx, cy + PEN_NODE_R + 12, TOKEN_NAMES[tokens[i].value], 5, PEN_INK, "middle")

    # ── ouroboric closure arc: final node → return anchor (first IMSCRIB, else start) ──
    if len(pos) >= 2:
        last = max(pos)
        tgt = _pen_return_target(tokens, last, pos)
        if tgt != last:
            _pen_backarc(svg, pos[last], pos[tgt], ourobor)

    # ── vertical left legend ──
    _pen_legend(svg)

    # ── footer ──
    if ourobor:
        svg.text(PEN_W/2, SVG_H - 12, f"Ouroboricity: {ourobor}", 7, PEN_INK, "middle")

    svg.close()
    return svg


def _pen_legend(svg: 'SVGBuilder'):
    """Vertical left-side legend strip (EDGES / GUARD / NODES / PAIRS / REG Δ)."""
    x0 = 14
    def hdr(y, t): svg.text(x0, y, t, 6, PEN_INK, "start", True)
    def samp(y, dash, glyph, lbl, width=1.2, arrow="filled"):
        svg.line(x0, y, x0 + 22, y, stroke=PEN_INK, width=width, dash=(dash if dash not in ("double", "zigzag") else None))
        svg.text(x0 + 30, y + 2, lbl, 5, PEN_INK, "start")
    # EDGES
    hdr(72, "EDGES")
    ys = 82
    for tv in range(12):
        dash, wdt, arrow, glyph = _PEN_EDGE[tv]
        if dash == "double":
            svg.line(x0, ys-1, x0+22, ys-1, stroke=PEN_INK, width=1.0)
            svg.line(x0, ys+1, x0+22, ys+1, stroke=PEN_INK, width=1.0)
        elif dash == "zigzag":
            svg.add("polyline", {"points": _pen_zigzag(x0, ys, x0+22, ys, amp=2, step=4),
                                 "fill": "none", "stroke": PEN_INK, "stroke-width": "1.0"})
        else:
            svg.line(x0, ys, x0+22, ys, stroke=PEN_INK, width=min(wdt, 2.0), dash=dash)
        svg.text(x0 + 28, ys + 2, TOKEN_SHORT[tv], 5, PEN_INK, "start")
        ys += 9.5
    # GUARD
    hdr(195, "GUARD")
    svg.add("circle", {"cx": f"{x0+3}", "cy": "206", "r": "2.5", "fill": "#000000", "stroke": PEN_INK, "stroke-width": "0.8"})
    svg.text(x0 + 10, 208, "in", 5, PEN_INK, "start")
    svg.add("circle", {"cx": f"{x0+3}", "cy": "216", "r": "2.5", "fill": PEN_INK})
    svg.text(x0 + 10, 218, "out", 5, PEN_INK, "start")
    # NODES
    hdr(231, "NODES")
    for k, (shape, lbl) in enumerate([("circle", "LOGI"), ("diamond", "FROB"),
                                       ("hexagon", "DIAL"), ("square", "LINE")]):
        yy = 246 + k * 12
        _pen_shape(svg, shape, x0 + 4, yy, 4, sw=1.0)
        svg.text(x0 + 14, yy + 2, lbl, 5, PEN_INK, "start")
    # PAIRS
    hdr(294, "PAIRS")
    svg.add("circle", {"cx": f"{x0+4}", "cy": "306", "r": "5", "fill": "#000000", "stroke": PEN_INK, "stroke-width": "0.8"})
    svg.text(x0 + 4, 309, "1", 6, PEN_INK, "middle")
    svg.text(x0 + 14, 308, "pair", 5, PEN_INK, "start")
    # REG Δ
    hdr(324, "REG Δ")
    for k, lbl in enumerate(["↑ T", "↓ F", "↑↓ B"]):
        svg.text(x0, 336 + k * 9, lbl, 5, PEN_INK, "start")


def generate_all_diagrams_v3():
    """Generate all SVG wiring diagrams with full edge granularity."""
    OUT_DIR.mkdir(parents=True, exist_ok=True)
    count = 0

    for key, info in CANONICALS.items():
        tokens = info["tokens"]
        tok_objs = tuple(Token(t) for t in tokens)
        graph = imscr_wiring(tok_objs)
        graph.name = key
        graph.description = info["desc"]
        svg = render_wiring_svg_v3(graph, key, info["ourobor"], info["desc"], info["ig_type"])
        path = OUT_DIR / f"canonical_{key}.svg"
        svg.save(path)
        print(f"  canonical {key} → {path.name}")
        count += 1

    for key, graph in NOVEL_GRAPHS.items():
        tokens_t = tuple(t.value for t in graph.tokens)
        has_frobenius = any(t == Token.FSPLIT for t in graph.tokens) and \
                        any(t == Token.FFUSE for t in graph.tokens)
        self_ref = graph.tokens[0] == graph.tokens[-1]
        has_dialetheia = all(t in graph.tokens for t in (Token.EVALT, Token.EVALF, Token.ENGAGR))
        has_cross = graph.has_cross_branch()
        tier = "O_∞" if (self_ref and has_cross) else ("O₂" if (has_frobenius or has_dialetheia) else "O₁")
        svg = render_wiring_svg_v3(graph, key, tier, graph.description, "")
        path = OUT_DIR / f"novel_{key}.svg"
        svg.save(path)
        print(f"  novel {key} → {path.name}")
        count += 1

    return count


def main():
    parser = argparse.ArgumentParser(description="IMASM Symbolic Wiring Diagram Generator v3 — Full Edge Granularity")
    parser.add_argument("--class", dest="cls", help="Generate a single class")
    parser.add_argument("--all", action="store_true", help="Generate all 16 diagrams")
    parser.add_argument("--format", choices=["svg", "png"], default="svg", help="Output format (svg or png)")
    args = parser.parse_args()

    if args.all or not args.cls:
        n = generate_all_diagrams_v3()
        print(f"\nGenerated {n} diagrams with full edge granularity → {OUT_DIR}/")
    else:
        key = args.cls
        if key in CANONICALS:
            info = CANONICALS[key]
            tokens = info["tokens"]
            graph = imscr_wiring(tuple(Token(t) for t in tokens))
            graph.name = key; graph.description = info["desc"]
            svg = render_wiring_svg_v3(graph, key, info["ourobor"], info["desc"], info["ig_type"])
        elif key in NOVEL_GRAPHS:
            graph = NOVEL_GRAPHS[key]
            has_cross = graph.has_cross_branch()
            self_ref = graph.tokens[0] == graph.tokens[-1]
            tier = "O_∞" if (self_ref and has_cross) else "O₂"
            svg = render_wiring_svg_v3(graph, key, tier, graph.description, "")
        else:
            print(f"Unknown: {key}")
            return
        path = OUT_DIR / f"{key}.svg"
        svg.save(path)
        print(f"→ {path}")

    # Also do PNG conversion if requested
    if args.format == "png":
        try:
            import cairosvg
            for svg_file in OUT_DIR.glob("*.svg"):
                png_file = svg_file.with_suffix(".png")
                cairosvg.svg2png(url=str(svg_file), write_to=str(png_file))
            print(f"Converted to PNG → {OUT_DIR}/")
        except ImportError:
            print("cairosvg not available for PNG conversion")


if __name__ == "__main__":
    main()
