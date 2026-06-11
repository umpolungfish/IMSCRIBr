#!/usr/bin/env python3
"""
DAG-structured CFGs for the 12 canonical IMASM arrangement classes.

FSPLIT/FFUSE pairs become genuine fork/join nodes:
  T-branch renders on an upper lane (Y_T)
  F-branch renders on a lower lane (Y_F)
  Empty branches render as dashed arcs
Linear sequences render flat on the main lane.

Output: docs/cfg_dag_{class_key}.gif  (12 files)
Run: python3 cfg_dag.py
"""

from __future__ import annotations
import io
from dataclasses import dataclass
from pathlib import Path
from typing import NamedTuple

import numpy as np
from PIL import Image
from matplotlib.font_manager import FontProperties
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors

DOCS = Path(__file__).parent / "docs"
BG   = "#0a0a15"

_EVERSON = "/home/mrnob0dy666/.local/share/fonts/Everson Mono.ttf"
try:
    _FP_SHAVIAN = FontProperties(fname=_EVERSON)
except Exception:
    _FP_SHAVIAN = FontProperties()

# ── Token constants ──────────────────────────────────────────────────────────
VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB = 0, 1, 2, 3, 4, 5
FSPLIT, FFUSE = 6, 7
EVALT, EVALF, ENGAGR = 8, 9, 10
IFIX = 11

TOKEN_NAMES  = ["VINIT","TANCH","AFWD","AREV","CLINK","IMSCRIB",
                "FSPLIT","FFUSE","EVALT","EVALF","ENGAGR","IFIX"]
TOKEN_SHORT  = ["VI","TA","AF","AR","CL","IM","FS","FF","ET","EF","EG","IX"]
TOKEN_FAMILY = {0:0,1:0,2:0,3:0,4:0,5:0, 6:1,7:1, 8:2,9:2,10:2, 11:3}

FAM_COLOR = {0:"#4e79a7", 1:"#ffd700", 2:"#e15759", 3:"#59a14f"}
FAM_NAME  = {0:"LOGICAL", 1:"FROBENIUS", 2:"DIALETHEIA", 3:"LINEAR"}

Y_MAIN, Y_T, Y_F = 0.50, 0.76, 0.24

VOID, TRUE, FALSE, BOTH = 0, 1, 2, 3
REG_COLOR = {VOID:"#666688", TRUE:"#20b2aa", FALSE:"#cc4455", BOTH:"#ffd700"}
REG_NAME  = {VOID:"VO⌀",    TRUE:"T",       FALSE:"F",       BOTH:"B⬡"}

_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))
_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))


# ── Sequence metadata ────────────────────────────────────────────────────────
class SeqMeta(NamedTuple):
    display: str
    steps:   tuple[int, ...]
    ig_type: str
    ourobor: str

SEQUENCES: dict[str, SeqMeta] = {
    "I_Dialetheic_Bootstrap": SeqMeta(
        "I — Dialetheic Bootstrap", (5,8,6,9,7,10,11,5),
        "⟨𐑦·𐑸·𐑾·𐑬·𐑐·𐑧·𐑲·𐑠·𐑻·𐑫·𐑳·𐑴⟩", "O₂"),
    "II_Void_Genesis": SeqMeta(
        "II — Void Genesis", (0,1,2,6,4,7,11,5),
        "⟨𐑨·𐑡·𐑑·𐑗·𐑱·𐑘·𐑔·𐑝·𐑢·𐑓·𐑙·𐑷⟩", "O₀"),
    "III_Anchor_Protocol": SeqMeta(
        "III — Anchor Protocol", (1,3,0,2,1,4,11,5),
        "⟨𐑨·𐑰·𐑾·𐑬·𐑱·𐑤·𐑚·𐑜·𐑢·𐑒·𐑙·𐑴⟩", "O₁"),
    "IV_Dual_Bootstrap": SeqMeta(
        "IV — Dual Bootstrap", (5,2,7,6,3,4,11,5),
        "⟨𐑦·𐑸·𐑾·𐑹·𐑐·𐑧·𐑲·𐑝·⊙·𐑖·𐑳·𐑭⟩", "O_∞"),
    "V_Linear_Chain": SeqMeta(
        "V — Linear Chain", (11,11,11,11,11,11,11,11),
        "⟨𐑛·𐑡·𐑩·𐑗·𐑱·𐑘·𐑔·𐑝·𐑢·𐑓·𐑙·𐑷⟩", "O₀"),
    "VI_Empty_Bootstrap": SeqMeta(
        "VI — Empty Bootstrap", (0,5,0,5,0,5,0,5),
        "⟨𐑦·𐑥·𐑾·𐑿·𐑐·𐑤·𐑲·𐑝·⊙·𐑒·𐑙·𐑷⟩", "O₁"),
    "VII_Parakernel": SeqMeta(
        "VII — Parakernel", (9,3,6,8,2,7,10,11),
        "⟨𐑦·𐑸·𐑾·𐑬·𐑐·𐑧·𐑲·𐑟·𐑻·𐑫·𐑳·𐑴⟩", "O₂"),
    "VIII_Frobenius_Kernel": SeqMeta(
        "VIII — Frobenius Kernel", (0,6,7,1),
        "⟨𐑛·𐑡·𐑩·𐑗·𐑱·𐑘·𐑚·𐑝·𐑢·𐑓·𐑙·𐑷⟩", "O₀"),
    "IX_Chiral_Pairs": SeqMeta(
        "IX — Chiral Pairs", (2,3,2,3,2,3,2,3),
        "⟨𐑦·𐑡·𐑑·𐑗·𐑱·𐑘·𐑚·𐑝·⊙·𐑒·𐑙·𐑷⟩", "O₁"),
    "X_Truth_Machine": SeqMeta(
        "X — Truth Machine", (5,6,8,11,5,6,9,11),
        "⟨𐑦·𐑡·𐑩·𐑗·𐑱·𐑘·𐑚·𐑜·𐑢·𐑓·𐑳·𐑷⟩", "O₁"),
    "XI_Eternal_Return": SeqMeta(
        "XI — Eternal Return", (5,2,3,5,2,3,5,2),
        "⟨𐑦·𐑸·𐑾·𐑗·𐑐·𐑤·𐑲·𐑝·⊙·𐑖·𐑳·𐑷⟩", "O₂"),
    "XII_ROM_Burn": SeqMeta(
        "XII — ROM Burn", (8,11,9,11,10,11,5,11),
        "⟨𐑨·𐑡·𐑩·𐑗·𐑱·𐑪·𐑚·𐑝·𐑢·𐑒·𐑳·𐑷⟩", "O₀"),
}


# ── Register simulation (unchanged from cfg_sequences) ───────────────────────
def simulate_register(steps: tuple[int, ...]) -> list[int]:
    reg = VOID; fixed = False
    in_split = False; pre_split_evalt = False
    in_split_evals: set[str] = set()
    result: list[int] = []
    for tok in steps:
        if fixed and tok not in (IFIX, IMSCRIB):
            result.append(reg); continue
        if tok == VINIT:
            reg = VOID; in_split = False
            pre_split_evalt = False; in_split_evals = set()
        elif tok == AFWD:
            if reg == VOID: reg = TRUE
            elif reg == FALSE: reg = BOTH
        elif tok == AREV:
            if reg == VOID: reg = FALSE
            elif reg == TRUE: reg = BOTH
        elif tok == CLINK:
            if reg in (TRUE, FALSE): reg = VOID
        elif tok == IMSCRIB:
            if reg == VOID: reg = TRUE
        elif tok == FSPLIT:
            in_split = True
            if pre_split_evalt: in_split_evals.add("T")
        elif tok == FFUSE:
            if "T" in in_split_evals and "F" in in_split_evals: reg = BOTH
            elif reg == BOTH: reg = TRUE
            in_split = False; in_split_evals = set(); pre_split_evalt = False
        elif tok == EVALT:
            if in_split: in_split_evals.add("T")
            else: pre_split_evalt = True
            if reg == FALSE: reg = BOTH
            elif reg == VOID: reg = TRUE
        elif tok == EVALF:
            if in_split: in_split_evals.add("F")
            if reg == TRUE: reg = BOTH
            elif reg == VOID: reg = FALSE
        elif tok == IFIX:
            fixed = True
        result.append(reg)
    return result


# ── DAG structure ────────────────────────────────────────────────────────────
@dataclass
class DagStructure:
    seq:      tuple[int, ...]
    pre:      list[int]   # seq indices before FSPLIT
    fsplit:   int | None  # seq index of FSPLIT (or None)
    t_branch: list[int]   # seq indices in T-branch
    f_branch: list[int]   # seq indices in F-branch
    ffuse:    int | None  # seq index of FFUSE (or None)
    post:     list[int]   # seq indices after FFUSE
    has_fork: bool


def parse_dag(seq: tuple[int, ...]) -> DagStructure:
    n  = len(seq)
    fs = next((i for i in range(n) if seq[i] == FSPLIT), None)
    if fs is None:
        return DagStructure(seq, list(range(n)), None, [], [], None, [], False)
    ff = next((i for i in range(fs + 1, n) if seq[i] == FFUSE), None)
    if ff is None:
        return DagStructure(seq, list(range(n)), None, [], [], None, [], False)

    pre   = list(range(fs))
    block = list(range(fs + 1, ff))
    post  = list(range(ff + 1, n))
    blk   = [seq[i] for i in block]

    t_a = next((j for j, t in enumerate(blk) if t == EVALT), None)
    f_a = next((j for j, t in enumerate(blk) if t == EVALF), None)

    if t_a is None and f_a is None:
        tb, fb = block[:], []
    elif t_a is not None and f_a is None:
        tb, fb = block[:], []
    elif t_a is None:
        tb, fb = [], block[:]
    elif t_a < f_a:
        tb, fb = block[:f_a], block[f_a:]
    else:
        fb, tb = block[:t_a], block[t_a:]

    return DagStructure(seq=seq, pre=pre, fsplit=fs, t_branch=tb,
                        f_branch=fb, ffuse=ff, post=post, has_fork=True)


# ── Layout ────────────────────────────────────────────────────────────────────
@dataclass
class Layout:
    pos:       dict[int, tuple[float, float]]
    depth:     dict[int, int]
    max_depth: int
    has_fork:  bool
    dag:       DagStructure


def compute_layout(dag: DagStructure) -> Layout:
    n   = len(dag.seq)
    pos: dict[int, tuple[float, float]] = {}
    dep: dict[int, int] = {}

    if not dag.has_fork:
        xs = np.linspace(0.10, 0.90, max(n, 2))[:n]
        for i in range(n):
            pos[i] = (float(xs[i]), Y_MAIN)
            dep[i] = i
        return Layout(pos, dep, n - 1, False, dag)

    n_pre   = len(dag.pre)
    n_t     = len(dag.t_branch)
    n_f     = len(dag.f_branch)
    n_post  = len(dag.post)
    n_inner = max(n_t, n_f, 1)

    total   = n_pre + 1 + n_inner + 1 + n_post
    slot_w  = 0.80 / max(total - 1, 1)
    x0      = 0.10

    for rank, idx in enumerate(dag.pre):
        pos[idx] = (x0 + rank * slot_w, Y_MAIN)
        dep[idx] = rank

    x_fs = x0 + n_pre * slot_w
    pos[dag.fsplit] = (x_fs, Y_MAIN)
    dep[dag.fsplit] = n_pre

    x_ff = x_fs + (n_inner + 1) * slot_w
    pos[dag.ffuse] = (x_ff, Y_MAIN)
    dep[dag.ffuse] = n_pre + 1 + n_inner

    for rank, idx in enumerate(dag.t_branch):
        frac = (rank + 1) / (n_t + 1)
        pos[idx] = (x_fs + frac * (x_ff - x_fs), Y_T)
        dep[idx] = n_pre + 1 + rank

    for rank, idx in enumerate(dag.f_branch):
        frac = (rank + 1) / (n_f + 1)
        pos[idx] = (x_fs + frac * (x_ff - x_fs), Y_F)
        dep[idx] = n_pre + 1 + rank

    for rank, idx in enumerate(dag.post):
        pos[idx] = (x_ff + (rank + 1) * slot_w, Y_MAIN)
        dep[idx] = n_pre + 2 + n_inner + rank

    return Layout(pos, dep, n_pre + 1 + n_inner + n_post, True, dag)


def _build_groups(layout: Layout) -> list[list[int]]:
    by_d: dict[int, list[int]] = {}
    for idx, d in layout.depth.items():
        by_d.setdefault(d, []).append(idx)
    return [by_d[d] for d in sorted(by_d)]


# ── Rendering ─────────────────────────────────────────────────────────────────
def _draw_arrow(ax, x0, y0, x1, y1, color, lw, alpha, connstyle=None):
    ap = dict(arrowstyle="-|>", color=color, lw=lw, alpha=alpha)
    if connstyle:
        ap["connectionstyle"] = connstyle
    ax.annotate("", xy=(x1, y1), xytext=(x0, y0), arrowprops=ap, zorder=2)


def _draw_empty_arc(ax, x0, y0, x1, y1, lane_y, color):
    t  = np.linspace(0, 1, 60)
    mx = (x0 + x1) / 2
    bx = (1-t)**2 * x0 + 2*(1-t)*t * mx + t**2 * x1
    by = (1-t)**2 * y0 + 2*(1-t)*t * lane_y + t**2 * y1
    ax.plot(bx, by, "--", color=color, lw=0.7, alpha=0.25, zorder=1)


def render_dag_frame(
    ax:      plt.Axes,
    meta:    SeqMeta,
    layout:  Layout,
    states:  list[int],
    visible: set[int],
    pulse_d: float | None,
    sigma:   float,
    title:   str,
) -> None:
    seq = meta.steps
    n   = len(seq)
    pos = layout.pos
    dep = layout.depth
    dag = layout.dag

    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.set_title(title, color="#cccccc", fontsize=6.5, pad=4)

    w = ({i: float(np.exp(-0.5 * ((dep[i] - pulse_d) / sigma) ** 2)) for i in range(n)}
         if pulse_d is not None else {i: 0.0 for i in range(n)})

    # ── Branch lane labels ──────────────────────────────────────────────────
    if layout.has_fork and dag.fsplit in visible:
        x_fs = pos[dag.fsplit][0]
        x_ff = pos[dag.ffuse][0]
        mid  = (x_fs + x_ff) / 2
        ax.text(mid, Y_T + 0.10, "T", ha="center", va="bottom",
                fontsize=5.5, color="#20c0b0", alpha=0.55, zorder=5)
        ax.text(mid, Y_F - 0.10, "F", ha="center", va="top",
                fontsize=5.5, color="#e04060", alpha=0.55, zorder=5)

    # ── Edges ───────────────────────────────────────────────────────────────
    if not layout.has_fork:
        for i in range(n - 1):
            if i not in visible: continue
            x0, y0 = pos[i]; x1, y1 = pos[i+1]
            pw   = max(w[i], w[i+1])
            frob = TOKEN_FAMILY[seq[i]] == 1 or TOKEN_FAMILY[seq[i+1]] == 1
            if pw > 0.25:
                col, lw, al = ("#ffd700" if frob else "#aaaaff"), 2.2, 0.85
            elif frob:
                col, lw, al = "#ffd700", 1.8, 0.70
            else:
                col, lw, al = "#3a5f80", 0.8, 0.30 + 0.5 * pw
            _draw_arrow(ax, x0, y0, x1, y1, col, lw, al)
    else:
        # Pre-fork chain
        for i in range(len(dag.pre) - 1):
            u, v = dag.pre[i], dag.pre[i+1]
            if u not in visible: continue
            xu, yu = pos[u]; xv, yv = pos[v]
            pw = max(w[u], w[v])
            col = "#ffd700" if pw > 0.25 else "#3a5f80"
            _draw_arrow(ax, xu, yu, xv, yv, col, 0.9, 0.35 + 0.5 * pw)
        if dag.pre and dag.pre[-1] in visible:
            u = dag.pre[-1]; v = dag.fsplit
            xu, yu = pos[u]; xv, yv = pos[v]
            pw = max(w[u], w[v])
            _draw_arrow(ax, xu, yu, xv, yv,
                        "#ffd700" if pw > 0.25 else "#3a5f80", 0.9, 0.35 + 0.5 * pw)

        # Fork arms
        if dag.fsplit in visible:
            x_fs, y_fs = pos[dag.fsplit]
            x_ff, y_ff = pos[dag.ffuse]

            if dag.t_branch:
                x1, y1 = pos[dag.t_branch[0]]
                pw = max(w[dag.fsplit], w[dag.t_branch[0]])
                _draw_arrow(ax, x_fs, y_fs, x1, y1,
                            "#20d0b8" if pw > 0.25 else "#1a8070", 1.2, 0.55 + 0.4 * pw)
            else:
                _draw_empty_arc(ax, x_fs, y_fs, x_ff, y_ff, Y_T, "#228888")

            if dag.f_branch:
                x1, y1 = pos[dag.f_branch[0]]
                pw = max(w[dag.fsplit], w[dag.f_branch[0]])
                _draw_arrow(ax, x_fs, y_fs, x1, y1,
                            "#ff6688" if pw > 0.25 else "#883344", 1.2, 0.55 + 0.4 * pw)
            else:
                _draw_empty_arc(ax, x_fs, y_fs, x_ff, y_ff, Y_F, "#883344")

        # T-branch body
        for j in range(len(dag.t_branch) - 1):
            u, v = dag.t_branch[j], dag.t_branch[j+1]
            if u not in visible: continue
            xu, yu = pos[u]; xv, yv = pos[v]
            pw = max(w[u], w[v])
            _draw_arrow(ax, xu, yu, xv, yv,
                        "#20d0b8" if pw > 0.25 else "#1a8070", 0.9, 0.45 + 0.4 * pw)

        # F-branch body
        for j in range(len(dag.f_branch) - 1):
            u, v = dag.f_branch[j], dag.f_branch[j+1]
            if u not in visible: continue
            xu, yu = pos[u]; xv, yv = pos[v]
            pw = max(w[u], w[v])
            _draw_arrow(ax, xu, yu, xv, yv,
                        "#ff6688" if pw > 0.25 else "#883344", 0.9, 0.45 + 0.4 * pw)

        # Join arms → FFUSE
        if dag.ffuse in visible:
            x_ff, y_ff = pos[dag.ffuse]
            if dag.t_branch and dag.t_branch[-1] in visible:
                xu, yu = pos[dag.t_branch[-1]]
                pw = max(w[dag.t_branch[-1]], w[dag.ffuse])
                _draw_arrow(ax, xu, yu, x_ff, y_ff,
                            "#20d0b8" if pw > 0.25 else "#1a8070", 1.2, 0.55 + 0.4 * pw)
            if dag.f_branch and dag.f_branch[-1] in visible:
                xu, yu = pos[dag.f_branch[-1]]
                pw = max(w[dag.f_branch[-1]], w[dag.ffuse])
                _draw_arrow(ax, xu, yu, x_ff, y_ff,
                            "#ff6688" if pw > 0.25 else "#883344", 1.2, 0.55 + 0.4 * pw)

        # Post-fuse chain
        if dag.post and dag.ffuse in visible:
            x0, y0 = pos[dag.ffuse]; x1, y1 = pos[dag.post[0]]
            pw = max(w[dag.ffuse], w[dag.post[0]])
            col = "#ffd700" if (TOKEN_FAMILY[seq[dag.ffuse]] == 1 and pw > 0.25) else \
                  ("#ffd700" if pw > 0.25 else "#3a5f80")
            _draw_arrow(ax, x0, y0, x1, y1, col, 0.9, 0.35 + 0.5 * pw)
        for j in range(len(dag.post) - 1):
            u, v = dag.post[j], dag.post[j+1]
            if u not in visible: continue
            xu, yu = pos[u]; xv, yv = pos[v]
            pw = max(w[u], w[v])
            _draw_arrow(ax, xu, yu, xv, yv,
                        "#ffd700" if pw > 0.25 else "#3a5f80", 0.9, 0.35 + 0.5 * pw)

    # ── Ouroboric arc ───────────────────────────────────────────────────────
    if meta.ourobor != "O₀" and len(visible) == n:
        x0, y0 = pos[0]; xn, yn = pos[n-1]
        pw_back = max(w[0], w[n-1])
        arc_col = "#ffd700" if pw_back > 0.25 else "#554422"
        ax.annotate("", xy=(x0, y0), xytext=(xn, yn),
                    arrowprops=dict(arrowstyle="-|>", color=arc_col, lw=1.2,
                                    alpha=0.70 if pw_back > 0.25 else 0.25,
                                    connectionstyle="arc3,rad=0.45"), zorder=2)
        ax.text((x0+xn)/2, max(y0,yn) + 0.16, meta.ourobor,
                ha="center", va="bottom", fontsize=5.5,
                color="#9988aa", style="italic", zorder=5)

    # ── Nodes ───────────────────────────────────────────────────────────────
    bsz = max(300.0, 1400.0 / max(n, 1))
    for i in sorted(visible):
        if i not in pos: continue
        xi, yi = pos[i]
        fam  = TOKEN_FAMILY[seq[i]]
        base = np.array(mcolors.to_rgba(FAM_COLOR[fam]))
        wi   = w[i]
        if pulse_d is not None:
            tgt = _PULSE_GOLD if fam == 1 else _PULSE_WHITE
            col = np.clip(base * (1 - wi) + tgt * wi, 0, 1)
            sz  = bsz * (1 + 1.6 * wi)
        else:
            col, sz = base, bsz

        ax.scatter([xi], [yi], c=[col], s=[sz], zorder=3,
                   linewidths=0.6, edgecolors="#ffffff22")

        nv  = len(visible)
        fsi = 5.0 if nv >= 7 else 6.5
        fsn = 3.5 if nv >= 7 else 4.5
        fsr = 4.2 if nv >= 7 else 5.2
        tc  = "#000000" if fam == 1 else "#ffffff"

        ax.text(xi, yi, TOKEN_SHORT[seq[i]], ha="center", va="center",
                fontsize=fsi, color=tc, fontweight="bold", zorder=4)
        ax.text(xi, yi + 0.105, TOKEN_NAMES[seq[i]], ha="center", va="bottom",
                fontsize=fsn, color="#999999", zorder=4)
        ax.text(xi, yi - 0.090, REG_NAME[states[i]], ha="center", va="top",
                fontsize=fsr, color=REG_COLOR[states[i]], fontweight="bold", zorder=4)

    # ── Footer ──────────────────────────────────────────────────────────────
    ax.text(0.5, 0.09, meta.ig_type, ha="center", va="center", fontsize=5.5,
            color="#6688aa", fontproperties=_FP_SHAVIAN, zorder=5)
    ax.text(0.5, 0.03, meta.ourobor, ha="center", va="center", fontsize=6.5,
            color="#aaaadd", fontweight="bold", zorder=5)
    for fi in range(4):
        lx = 0.70 + fi * 0.075
        ax.scatter([lx], [0.06], c=[FAM_COLOR[fi]], s=22, zorder=6)
        ax.text(lx + 0.01, 0.06, FAM_NAME[fi][0], va="center",
                fontsize=3.5, color="#666666", zorder=6)


def _fig_to_pil(fig: plt.Figure, dpi: int) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def generate_dag_one(
    key:          str,
    meta:         SeqMeta,
    build_frames: int = 20,
    flow_frames:  int = 48,
    fps:          int = 14,
    dpi:          int = 200,
) -> Path:
    seq    = meta.steps
    states = simulate_register(seq)
    dag    = parse_dag(seq)
    layout = compute_layout(dag)
    sigma  = max(0.7, layout.max_depth / 7.0)
    groups = _build_groups(layout)
    all_i  = set(range(len(seq)))

    fig, ax = plt.subplots(figsize=(10, 4.4), facecolor=BG)
    frames: list[Image.Image] = []

    # Build phase: reveal by depth group
    visible: set[int] = set()
    for f in range(build_frames):
        target = max(1, int((f + 1) / build_frames * len(groups)))
        for g in groups[:target]:
            visible.update(g)
        last  = groups[target - 1][0]
        tok   = seq[last]
        title = (f"{meta.display}  │  {TOKEN_NAMES[tok]} "
                 f"[{FAM_NAME[TOKEN_FAMILY[tok]]}]  d={layout.depth[last]}"
                 f"  →  {REG_NAME[states[last]]}")
        render_dag_frame(ax, meta, layout, states, set(visible), None, sigma, title)
        frames.append(_fig_to_pil(fig, dpi))

    # Flow phase: pulse by DAG depth
    for pd in np.linspace(-0.5, layout.max_depth + 0.5, flow_frames):
        i_near = min(range(len(seq)), key=lambda i: abs(layout.depth[i] - pd))
        tok    = seq[i_near]
        title  = (f"{meta.display}  │  ◎ {TOKEN_NAMES[tok]} "
                  f"[{FAM_NAME[TOKEN_FAMILY[tok]]}]"
                  f"  reg: {REG_NAME[states[i_near]]}  {meta.ourobor}")
        render_dag_frame(ax, meta, layout, states, all_i, pd, sigma, title)
        frames.append(_fig_to_pil(fig, dpi))

    plt.close(fig)
    DOCS.mkdir(parents=True, exist_ok=True)
    out = DOCS / f"cfg_dag_{key}.gif"
    rgb = [fr.convert("RGB") for fr in frames]
    rgb[0].save(str(out), save_all=True, append_images=rgb[1:],
                duration=1000 // fps, loop=0, optimize=False)
    return out


def main() -> None:
    print(f"Generating {len(SEQUENCES)} DAG CFGs → {DOCS}/\n")
    for i, (key, meta) in enumerate(SEQUENCES.items(), 1):
        dag    = parse_dag(meta.steps)
        layout = compute_layout(dag)
        tag    = (f"fork@d={layout.depth[dag.fsplit]}" if dag.has_fork else "linear")
        print(f"[{i:02d}/{len(SEQUENCES)}] {meta.display}  [{tag}]",
              end="  ", flush=True)
        out = generate_dag_one(key, meta)
        print(f"→ {out.name}  ({out.stat().st_size/1e3:.0f} KB)")
    print("\nDone.")


# ── Wired graph rendering ──────────────────────────────────────────────────────
#
# Renders WiredGraph objects (from wiring.py) — supports multi-fork,
# nested, and cross-branch topologies.
#
# Wire color coding:
#   T-port wires   : teal   #20d0b8
#   F-port wires   : red    #ff6688
#   cross-branch   : gold   #ffd700  (dashed)
#   main/o wires   : blue   #4e79a7


def _belnap_join(a: int, b: int) -> int:
    """Belnap information lattice join (∨): N<T,F<B."""
    if a == VOID: return b
    if b == VOID: return a
    if a == b:    return a
    return BOTH   # T∨F = F∨T = B; anything with B = B handled above


_AFWD_TABLE  = {VOID: TRUE,  TRUE: TRUE,  FALSE: BOTH, BOTH: BOTH}
_AREV_TABLE  = {VOID: FALSE, TRUE: BOTH,  FALSE: FALSE, BOTH: BOTH}
_CLINK_TABLE = {VOID: VOID,  TRUE: VOID,  FALSE: VOID,  BOTH: BOTH}
_IMSCRIB_TABLE = {VOID: TRUE, TRUE: TRUE, FALSE: FALSE, BOTH: BOTH}


def simulate_wired(graph) -> list[int]:
    """Dataflow simulation following the explicit wire topology of a WiredGraph.

    Processes nodes in topological layer order. Each node fires when all its
    input ports are satisfied (guaranteed by layer ordering). Input values are
    read from the source node's stored output via the connecting wire.
    Open input ports (no incoming wire) receive VOID.

    For FSPLIT: the single input value is duplicated to both T and F outputs;
    node_output stores that value so any downstream node reading from FSPLIT
    receives the same value regardless of which port it connected to.

    For FFUSE: T and F input port values are joined via Belnap ∨.
    """
    n      = len(graph.tokens)
    output = [VOID] * n

    for layer in graph.topological_layers():
        for node in layer:
            tok = graph.tokens[node].value
            in_ws = graph.in_wires(node)

            if tok == VINIT:
                output[node] = VOID

            elif tok == FFUSE:
                t_val = f_val = VOID
                for w in in_ws:
                    v = output[w.src_node]
                    if w.dst_port == 'T':
                        t_val = v
                    else:
                        f_val = v
                output[node] = _belnap_join(t_val, f_val)

            else:
                # single input (or open if no wires)
                in_val = VOID
                for w in in_ws:
                    in_val = output[w.src_node]

                if tok == AFWD:
                    output[node] = _AFWD_TABLE[in_val]
                elif tok == AREV:
                    output[node] = _AREV_TABLE[in_val]
                elif tok == CLINK:
                    output[node] = _CLINK_TABLE[in_val]
                elif tok == IMSCRIB:
                    output[node] = _IMSCRIB_TABLE[in_val]
                elif tok == FSPLIT:
                    output[node] = in_val   # same value on both T and F out-ports
                elif tok == EVALT:
                    output[node] = TRUE if in_val == TRUE else VOID
                elif tok == EVALF:
                    output[node] = FALSE if in_val == FALSE else VOID
                elif tok == ENGAGR:
                    output[node] = BOTH
                elif tok == IFIX:
                    output[node] = in_val
                elif tok == TANCH:
                    output[node] = in_val   # store for display; token sinks it
                else:
                    output[node] = in_val

    return output


def _wired_layout(
    graph,
) -> dict[int, tuple[float, float]]:
    """Compute (x, y) for each node in a WiredGraph.

    X: topological layer, linearly spaced 0.10–0.90.
    Y: determined by the first incoming wire's port:
       T-input → Y_T (0.76), F-input → Y_F (0.24), otherwise Y_MAIN (0.50).
    """
    layers = graph.topological_layers()
    n_layers = len(layers)
    pos: dict[int, tuple[float, float]] = {}

    for li, layer in enumerate(layers):
        x = 0.10 + 0.80 * li / max(n_layers - 1, 1)
        for node in layer:
            in_ws = graph.in_wires(node)
            y = Y_MAIN
            if in_ws:
                # src_port carries the branch signal: FSPLIT emits 'T' or 'F'
                # dst_port is always 'i' for non-FFUSE tokens, so useless here
                p = in_ws[0].src_port
                if p == 'T':
                    y = Y_T
                elif p == 'F':
                    y = Y_F
            # FSPLIT/FFUSE are decision/merge nodes — keep on the main lane
            if graph.tokens[node].value in (FSPLIT, FFUSE):
                y = Y_MAIN
            pos[node] = (x, y)

    return pos


def _wire_color(wire, cross_set: set) -> tuple[str, float, float]:
    """Return (color, linewidth, alpha) for a wire."""
    is_cross = wire in cross_set
    if wire.src_port == 'T' or wire.dst_port == 'T':
        return ("#ffd700" if is_cross else "#20d0b8"), (2.0 if is_cross else 1.3), 0.85
    if wire.src_port == 'F' or wire.dst_port == 'F':
        return ("#ffd700" if is_cross else "#ff6688"), (2.0 if is_cross else 1.3), 0.85
    return "#4e79a7", 0.9, 0.45


def render_wired_dag_frame(
    ax:        "plt.Axes",
    graph,
    pos:       dict[int, tuple[float, float]],
    states:    list[int],
    visible:   set[int],
    pulse_d:   "float | None",
    sigma:     float,
    title:     str,
) -> None:
    """Render one frame of a WiredGraph animation."""
    n      = graph.n()
    cross  = set(graph.cross_branch_wires())
    depths = {node: i for i, layer in enumerate(graph.topological_layers())
              for node in layer}

    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.set_title(title, color="#cccccc", fontsize=6.5, pad=4)

    w_pulse = ({node: float(np.exp(-0.5 * ((depths.get(node, 0) - pulse_d) / sigma) ** 2))
                for node in range(n)}
               if pulse_d is not None else {node: 0.0 for node in range(n)})

    # Branch lane labels
    has_fork = any(t.value == FSPLIT for t in graph.tokens)
    if has_fork and visible:
        ax.text(0.5, Y_T + 0.10, "T", ha="center", va="bottom",
                fontsize=5.5, color="#20c0b0", alpha=0.55, zorder=5)
        ax.text(0.5, Y_F - 0.10, "F", ha="center", va="top",
                fontsize=5.5, color="#e04060", alpha=0.55, zorder=5)

    # Draw wires
    for wire in graph.wires:
        if wire.src_node not in visible:
            continue
        x0, y0 = pos[wire.src_node]
        x1, y1 = pos[wire.dst_node]
        pw = max(w_pulse[wire.src_node], w_pulse.get(wire.dst_node, 0.0))
        col, lw, al = _wire_color(wire, cross)

        if pw > 0.25:
            col = "#ffd700"
            lw  = lw * 1.4
            al  = min(al + 0.1, 1.0)

        is_cross_wire = wire in cross
        conn = "arc3,rad=0.35" if is_cross_wire else None
        style = "--" if is_cross_wire else "-"

        if conn:
            ax.annotate("", xy=(x1, y1), xytext=(x0, y0),
                        arrowprops=dict(arrowstyle="-|>", color=col, lw=lw,
                                        alpha=al, connectionstyle=conn),
                        zorder=2)
        else:
            _draw_arrow(ax, x0, y0, x1, y1, col, lw, al)

    # Draw ouroboric back-arc if self-referential
    first_tok = graph.tokens[0]
    last_tok  = graph.tokens[n - 1]
    if first_tok == last_tok and len(visible) == n:
        x0, y0 = pos[0]; xn, yn = pos[n - 1]
        pw_back = max(w_pulse[0], w_pulse[n - 1])
        arc_col = "#ffd700" if pw_back > 0.25 else "#554422"
        ax.annotate("", xy=(x0, y0), xytext=(xn, yn),
                    arrowprops=dict(arrowstyle="-|>", color=arc_col, lw=1.2,
                                    alpha=0.65 if pw_back > 0.25 else 0.25,
                                    connectionstyle="arc3,rad=0.45"), zorder=2)

    # Draw nodes
    bsz = max(280.0, 1300.0 / max(n, 1))
    for node in sorted(visible):
        if node not in pos:
            continue
        xi, yi = pos[node]
        tok  = graph.tokens[node]
        tv   = tok.value
        fam  = TOKEN_FAMILY[tv]
        base = np.array(mcolors.to_rgba(FAM_COLOR[fam]))
        wi   = w_pulse[node]
        if pulse_d is not None:
            tgt = _PULSE_GOLD if fam == 1 else _PULSE_WHITE
            col = np.clip(base * (1 - wi) + tgt * wi, 0, 1)
            sz  = bsz * (1 + 1.6 * wi)
        else:
            col, sz = base, bsz

        ax.scatter([xi], [yi], c=[col], s=[sz], zorder=3,
                   linewidths=0.7, edgecolors="#ffffff22")

        nv  = len(visible)
        fsi = 5.0 if nv >= 7 else 6.5
        fsn = 3.5 if nv >= 7 else 4.5
        fsr = 4.2 if nv >= 7 else 5.2
        tc  = "#000000" if fam == 1 else "#ffffff"

        ax.text(xi, yi, TOKEN_SHORT[tv], ha="center", va="center",
                fontsize=fsi, color=tc, fontweight="bold", zorder=4)
        ax.text(xi, yi + 0.105, TOKEN_NAMES[tv], ha="center", va="bottom",
                fontsize=fsn, color="#999999", zorder=4)
        if node < len(states):
            ax.text(xi, yi - 0.090, REG_NAME[states[node]], ha="center", va="top",
                    fontsize=fsr, color=REG_COLOR[states[node]],
                    fontweight="bold", zorder=4)

    # Footer
    cross_tag = f"  [×{len(cross)} cross-branch]" if cross else ""
    ax.text(0.5, 0.04, (graph.name or "") + cross_tag,
            ha="center", va="center", fontsize=5.5,
            color="#aaaadd", fontweight="bold", zorder=5)
    for fi in range(4):
        lx = 0.70 + fi * 0.075
        ax.scatter([lx], [0.06], c=[FAM_COLOR[fi]], s=22, zorder=6)
        ax.text(lx + 0.01, 0.06, FAM_NAME[fi][0], va="center",
                fontsize=3.5, color="#666666", zorder=6)


def generate_wired_dag_gif(
    graph,
    build_frames: int = 22,
    flow_frames:  int = 50,
    fps:          int = 14,
    dpi:          int = 200,
) -> Path:
    """Generate an animated GIF for a WiredGraph."""
    states = simulate_wired(graph)
    pos    = _wired_layout(graph)
    layers = graph.topological_layers()
    n_layers = len(layers)
    n      = graph.n()
    sigma  = max(0.7, n_layers / 7.0)
    all_i  = set(range(n))

    # Depth map for pulse
    depths = {node: i for i, layer in enumerate(layers) for node in layer}

    fig, ax = plt.subplots(figsize=(10, 4.4), facecolor=BG)
    frames: list[Image.Image] = []

    # Build phase: reveal by topological layer
    visible: set[int] = set()
    for f in range(build_frames):
        target = max(1, int((f + 1) / build_frames * n_layers))
        for layer in layers[:target]:
            visible.update(layer)
        last_node = layers[target - 1][0]
        tok       = graph.tokens[last_node]
        tv        = tok.value
        title     = (f"{graph.name}  │  {TOKEN_NAMES[tv]} "
                     f"[{FAM_NAME[TOKEN_FAMILY[tv]]}]  d={depths[last_node]}")
        render_wired_dag_frame(ax, graph, pos, states, set(visible), None, sigma, title)
        frames.append(_fig_to_pil(fig, dpi))

    # Flow phase: pulse sweeps by DAG depth
    for pd in np.linspace(-0.5, n_layers + 0.5, flow_frames):
        nearest = min(range(n), key=lambda i: abs(depths.get(i, 0) - pd))
        tok     = graph.tokens[nearest]
        tv      = tok.value
        title   = (f"{graph.name}  │  ◎ {TOKEN_NAMES[tv]} "
                   f"[{FAM_NAME[TOKEN_FAMILY[tv]]}]  reg: {REG_NAME[states[nearest]]}")
        render_wired_dag_frame(ax, graph, pos, states, all_i, pd, sigma, title)
        frames.append(_fig_to_pil(fig, dpi))

    plt.close(fig)
    DOCS.mkdir(parents=True, exist_ok=True)
    key = graph.name.replace(" ", "_")
    out = DOCS / f"cfg_dag_{key}.gif"
    rgb = [fr.convert("RGB") for fr in frames]
    rgb[0].save(str(out), save_all=True, append_images=rgb[1:],
                duration=1000 // fps, loop=0, optimize=False)
    return out


def main_wired() -> None:
    """Render all novel wired graphs."""
    from wiring import NOVEL_GRAPHS
    print(f"Generating {len(NOVEL_GRAPHS)} wired DAG CFGs → {DOCS}/\n")
    for i, (key, graph) in enumerate(NOVEL_GRAPHS.items(), 1):
        errs = graph.validate()
        if errs:
            print(f"[{i:02d}] {key} — INVALID: {errs}")
            continue
        cross_n = len(graph.cross_branch_wires())
        print(f"[{i:02d}/{len(NOVEL_GRAPHS)}] {key}  "
              f"[{len(graph.tokens)} tokens, {cross_n} cross-branch wires]",
              end="  ", flush=True)
        out = generate_wired_dag_gif(graph)
        print(f"→ {out.name}  ({out.stat().st_size/1e3:.0f} KB)")
    print("\nDone.")


if __name__ == "__main__":
    main()
