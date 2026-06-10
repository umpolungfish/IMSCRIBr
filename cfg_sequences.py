#!/usr/bin/env python3
"""
Animated token-sequence CFGs for the 12 canonical IMASM arrangement classes.

For each class, generates an animated GIF showing the step sequence as a
directed linear graph:
  - nodes coloured by token family
  - register state annotated below each node (after that step)
  - ouroboric back-arc when ouroboricity > O₀
  - Phase 1: nodes build up one by one
  - Phase 2: Gaussian pulse flows along the sequence

Output: docs/cfg_seq_{class_key}.gif  (12 files)
"""

from __future__ import annotations
import io
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

# Everson Mono for Shavian IG-type strings
_EVERSON = "/home/mrnob0dy666/.local/share/fonts/Everson Mono.ttf"
try:
    _FP_SHAVIAN = FontProperties(fname=_EVERSON)
except Exception:
    _FP_SHAVIAN = FontProperties()

# ── Token constants (mirror of tokens.py) ────────────────────────────────────
VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB = 0, 1, 2, 3, 4, 5
FSPLIT, FFUSE = 6, 7
EVALT, EVALF, ENGAGR = 8, 9, 10
IFIX = 11

TOKEN_NAMES = [
    "VINIT", "TANCH", "AFWD", "AREV", "CLINK", "IMSCRIB",
    "FSPLIT", "FFUSE", "EVALT", "EVALF", "ENGAGR", "IFIX",
]
TOKEN_SHORT = ["VI", "TA", "AF", "AR", "CL", "IM", "FS", "FF", "ET", "EF", "EG", "IX"]

TOKEN_FAMILY = {0:0, 1:0, 2:0, 3:0, 4:0, 5:0, 6:1, 7:1, 8:2, 9:2, 10:2, 11:3}

FAM_COLOR = {0: "#4e79a7", 1: "#ffd700", 2: "#e15759", 3: "#59a14f"}
FAM_NAME  = {0: "LOGICAL", 1: "FROBENIUS", 2: "DIALETHEIA", 3: "LINEAR"}

# ── Register states ───────────────────────────────────────────────────────────
VOID, TRUE, FALSE, BOTH = 0, 1, 2, 3
REG_COLOR = {VOID: "#666688", TRUE: "#20b2aa", FALSE: "#cc4455", BOTH: "#ffd700"}
REG_NAME  = {VOID: "VO⌀", TRUE: "T", FALSE: "F", BOTH: "B⬡"}

_PULSE_WHITE = np.array(mcolors.to_rgba("#ffffff"))
_PULSE_GOLD  = np.array(mcolors.to_rgba("#ffd700"))


# ── Canonical sequence metadata ───────────────────────────────────────────────
class SeqMeta(NamedTuple):
    display:  str
    steps:    tuple[int, ...]
    ig_type:  str
    ourobor:  str    # O₀ O₁ O₂ O_∞

SEQUENCES: dict[str, SeqMeta] = {
    "I_Dialetheic_Bootstrap": SeqMeta(
        "I — Dialetheic Bootstrap",
        (5, 8, 6, 9, 7, 10, 11, 5),
        "⟨𐑦 · 𐑸 · 𐑾 · 𐑬 · 𐑐 · 𐑧 · 𐑲 · 𐑠 · 𐑻 · 𐑫 · 𐑳 · 𐑴⟩",
        "O₂",
    ),
    "II_Void_Genesis": SeqMeta(
        "II — Void Genesis",
        (0, 1, 2, 6, 4, 7, 11, 5),
        "⟨𐑨 · 𐑡 · 𐑑 · 𐑗 · 𐑱 · 𐑘 · 𐑔 · 𐑝 · 𐑢 · 𐑓 · 𐑙 · 𐑷⟩",
        "O₀",
    ),
    "III_Anchor_Protocol": SeqMeta(
        "III — Anchor Protocol",
        (1, 3, 0, 2, 1, 4, 11, 5),
        "⟨𐑨 · 𐑰 · 𐑾 · 𐑬 · 𐑱 · 𐑤 · 𐑚 · 𐑜 · 𐑢 · 𐑒 · 𐑙 · 𐑴⟩",
        "O₁",
    ),
    "IV_Dual_Bootstrap": SeqMeta(
        "IV — Dual Bootstrap",
        (5, 2, 7, 6, 3, 4, 11, 5),
        "⟨𐑦 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑧 · 𐑲 · 𐑝 · ⊙ · 𐑖 · 𐑳 · 𐑭⟩",
        "O_∞",
    ),
    "V_Linear_Chain": SeqMeta(
        "V — Linear Chain",
        (11, 11, 11, 11, 11, 11, 11, 11),
        "⟨𐑛 · 𐑡 · 𐑩 · 𐑗 · 𐑱 · 𐑘 · 𐑔 · 𐑝 · 𐑢 · 𐑓 · 𐑙 · 𐑷⟩",
        "O₀",
    ),
    "VI_Empty_Bootstrap": SeqMeta(
        "VI — Empty Bootstrap",
        (0, 5, 0, 5, 0, 5, 0, 5),
        "⟨𐑦 · 𐑥 · 𐑾 · 𐑿 · 𐑐 · 𐑤 · 𐑲 · 𐑝 · ⊙ · 𐑒 · 𐑙 · 𐑷⟩",
        "O₁",
    ),
    "VII_Parakernel": SeqMeta(
        "VII — Parakernel",
        (9, 3, 6, 8, 2, 7, 10, 11),
        "⟨𐑦 · 𐑸 · 𐑾 · 𐑬 · 𐑐 · 𐑧 · 𐑲 · 𐑟 · 𐑻 · 𐑫 · 𐑳 · 𐑴⟩",
        "O₂",
    ),
    "VIII_Frobenius_Kernel": SeqMeta(
        "VIII — Frobenius Kernel",
        (0, 6, 7, 1),
        "⟨𐑛 · 𐑡 · 𐑩 · 𐑗 · 𐑱 · 𐑘 · 𐑚 · 𐑝 · 𐑢 · 𐑓 · 𐑙 · 𐑷⟩",
        "O₀",
    ),
    "IX_Chiral_Pairs": SeqMeta(
        "IX — Chiral Pairs",
        (2, 3, 2, 3, 2, 3, 2, 3),
        "⟨𐑦 · 𐑡 · 𐑑 · 𐑗 · 𐑱 · 𐑘 · 𐑚 · 𐑝 · ⊙ · 𐑒 · 𐑙 · 𐑷⟩",
        "O₁",
    ),
    "X_Truth_Machine": SeqMeta(
        "X — Truth Machine",
        (5, 6, 8, 11, 5, 6, 9, 11),
        "⟨𐑦 · 𐑡 · 𐑩 · 𐑗 · 𐑱 · 𐑘 · 𐑚 · 𐑜 · 𐑢 · 𐑓 · 𐑳 · 𐑷⟩",
        "O₁",
    ),
    "XI_Eternal_Return": SeqMeta(
        "XI — Eternal Return",
        (5, 2, 3, 5, 2, 3, 5, 2),
        "⟨𐑦 · 𐑸 · 𐑾 · 𐑗 · 𐑐 · 𐑤 · 𐑲 · 𐑝 · ⊙ · 𐑖 · 𐑳 · 𐑷⟩",
        "O₂",
    ),
    "XII_ROM_Burn": SeqMeta(
        "XII — ROM Burn",
        (8, 11, 9, 11, 10, 11, 5, 11),
        "⟨𐑨 · 𐑡 · 𐑩 · 𐑗 · 𐑱 · 𐑪 · 𐑚 · 𐑝 · 𐑢 · 𐑒 · 𐑳 · 𐑷⟩",
        "O₀",
    ),
}


# ── Register simulation ───────────────────────────────────────────────────────
def simulate_register(steps: tuple[int, ...]) -> list[int]:
    """Return register state after each step (initial state is VOID)."""
    reg   = VOID
    fixed = False
    in_split           = False
    pre_split_evalt    = False
    in_split_evals: set[str] = set()
    result: list[int]  = []

    for tok in steps:
        if fixed and tok not in (IFIX, IMSCRIB):
            result.append(reg)
            continue

        if tok == VINIT:
            reg = VOID; in_split = False
            pre_split_evalt = False; in_split_evals = set()
        elif tok == AFWD:
            if reg == VOID:  reg = TRUE
            elif reg == FALSE: reg = BOTH
        elif tok == AREV:
            if reg == VOID:  reg = FALSE
            elif reg == TRUE: reg = BOTH
        elif tok == CLINK:
            if reg in (TRUE, FALSE): reg = VOID
        elif tok == IMSCRIB:
            if reg == VOID: reg = TRUE
        elif tok == FSPLIT:
            in_split = True
            if pre_split_evalt: in_split_evals.add("T")
        elif tok == FFUSE:
            if "T" in in_split_evals and "F" in in_split_evals:
                reg = BOTH
            elif reg == BOTH:
                reg = TRUE
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
        # TANCH, ENGAGR: no register change

        result.append(reg)

    return result


# ── Frame rendering ───────────────────────────────────────────────────────────
def _nx(i: int, n: int) -> float:
    """X position for step i in a sequence of n steps."""
    if n == 1: return 0.5
    return 0.10 + 0.80 * i / (n - 1)


def _base_size(n: int) -> float:
    """Scatter marker size scaled for sequence length."""
    return max(350.0, 1600.0 / n)


def render_frame(
    ax: plt.Axes,
    seq:    SeqMeta,
    states: list[int],
    k:      int | None,    # None = all revealed (flow phase)
    pulse:  float | None,  # pulse center in step-units; None = build phase
    sigma:  float,
    title:  str,
) -> None:
    n = len(seq.steps)
    ax.clear()
    ax.set_facecolor(BG)
    ax.set_axis_off()
    ax.set_xlim(0.0, 1.0)
    ax.set_ylim(0.0, 1.0)
    ax.set_aspect("auto")
    ax.set_title(title, color="#cccccc", fontsize=7.0, pad=4)

    xs      = np.array([_nx(i, n) for i in range(n)])
    y_node  = 0.55
    visible = list(range(k)) if k is not None else list(range(n))

    # Pulse weights (flow phase only)
    if pulse is not None:
        dists   = np.array([abs(i - pulse) for i in range(n)], dtype=float)
        weights = np.exp(-0.5 * (dists / sigma) ** 2)
    else:
        weights = np.zeros(n)

    # ── Edges ──
    for idx in range(len(visible) - 1):
        u, v = visible[idx], visible[idx + 1]
        fam_u = TOKEN_FAMILY[seq.steps[u]]
        fam_v = TOKEN_FAMILY[seq.steps[v]]
        frob  = (fam_u == 1 or fam_v == 1)

        if pulse is not None:
            w = max(weights[u], weights[v])
            if frob and w > 0.25:
                col, lw, al = "#ffd700", 2.5, 0.90
            elif w > 0.25:
                col, lw, al = "#8888ff", 1.5, 0.70
            elif frob:
                col, lw, al = "#aa8800", 1.5, 0.50
            else:
                col, lw, al = "#3a5f80", 0.7, 0.25
        else:
            if frob:
                col, lw, al = "#ffd700", 2.0, 0.80
            else:
                col, lw, al = "#4a7aaa", 1.0, 0.40

        ax.annotate("", xy=(xs[v], y_node), xytext=(xs[u], y_node),
                    arrowprops=dict(arrowstyle="-|>", color=col, lw=lw, alpha=al),
                    zorder=2)

    # Ouroboric back-arc (last → first) when ouroboricity > O₀
    if seq.ourobor != "O₀" and len(visible) == n:
        if pulse is not None:
            w_back = max(weights[0], weights[-1])
            arc_col = "#ffd700" if w_back > 0.25 else "#666644"
            arc_al  = 0.75 if w_back > 0.25 else 0.30
        else:
            arc_col, arc_al = "#776644", 0.35

        ax.annotate("", xy=(xs[0], y_node), xytext=(xs[-1], y_node),
                    arrowprops=dict(
                        arrowstyle="-|>", color=arc_col, lw=1.2, alpha=arc_al,
                        connectionstyle="arc3,rad=0.45",
                    ),
                    zorder=2)
        ax.text((xs[0] + xs[-1]) / 2, y_node + 0.19,
                seq.ourobor, ha="center", va="bottom",
                fontsize=5.5, color="#9988aa", style="italic", zorder=5)

    # ── Nodes ──
    if visible:
        bsize = _base_size(n)
        node_xs = xs[visible]
        node_ys = np.full(len(visible), y_node)
        colors, sizes = [], []

        for i in visible:
            fam  = TOKEN_FAMILY[seq.steps[i]]
            base = np.array(mcolors.to_rgba(FAM_COLOR[fam]))
            if pulse is not None:
                tgt = _PULSE_GOLD if fam == 1 else _PULSE_WHITE
                col = np.clip(base * (1 - weights[i]) + tgt * weights[i], 0, 1)
                sz  = bsize + bsize * 1.8 * weights[i]
            else:
                col = base
                sz  = bsize
            colors.append(col)
            sizes.append(sz)

        ax.scatter(node_xs, node_ys, c=colors, s=sizes,
                   zorder=3, linewidths=0.7, edgecolors="#ffffff22")

        fs_inner = 5.0 if n >= 7 else 6.5
        fs_name  = 3.5 if n >= 7 else 4.5
        fs_reg   = 4.5 if n >= 7 else 5.5

        for idx, i in enumerate(visible):
            fam = TOKEN_FAMILY[seq.steps[i]]
            tc  = "#000000" if fam == 1 else "#ffffff"

            # Short code inside node
            ax.text(node_xs[idx], y_node, TOKEN_SHORT[seq.steps[i]],
                    ha="center", va="center", fontsize=fs_inner,
                    color=tc, fontweight="bold", zorder=4)

            # Full token name above node
            ax.text(node_xs[idx], y_node + 0.115,
                    TOKEN_NAMES[seq.steps[i]],
                    ha="center", va="bottom", fontsize=fs_name,
                    color="#999999", zorder=4)

            # Register state below node
            reg  = states[i]
            rcol = REG_COLOR[reg]
            ax.text(node_xs[idx], y_node - 0.095,
                    REG_NAME[reg],
                    ha="center", va="top", fontsize=fs_reg,
                    color=rcol, fontweight="bold", zorder=4)

    # IG type (Everson Mono for Shavian) + ouroboricity footer
    ax.text(0.5, 0.11, seq.ig_type,
            ha="center", va="center", fontsize=5.5,
            color="#6688aa", fontproperties=_FP_SHAVIAN, zorder=5)
    ax.text(0.5, 0.04, seq.ourobor,
            ha="center", va="center", fontsize=6.5,
            color="#aaaadd", fontweight="bold", zorder=5)

    # Family colour legend bottom-right
    leg_y = 0.06
    for fi, fam_id in enumerate(range(4)):
        lx = 0.70 + fi * 0.075
        ax.scatter([lx], [leg_y], c=[FAM_COLOR[fam_id]], s=25, zorder=6)
        ax.text(lx + 0.01, leg_y, FAM_NAME[fam_id][0],
                va="center", fontsize=3.5, color="#666666", zorder=6)


def _fig_to_pil(fig: plt.Figure, dpi: int) -> Image.Image:
    buf = io.BytesIO()
    fig.savefig(buf, format="png", dpi=dpi, facecolor=BG, bbox_inches="tight")
    buf.seek(0)
    return Image.open(buf).copy()


def generate_one(
    key:           str,
    seq:           SeqMeta,
    build_frames:  int = 20,
    flow_frames:   int = 45,
    fps:           int = 14,
    dpi:           int = 110,
) -> Path:
    n      = len(seq.steps)
    states = simulate_register(seq.steps)
    sigma  = max(0.6, n / 7.0)

    fig, ax = plt.subplots(figsize=(10, 3.8), facecolor=BG)
    frames: list[Image.Image] = []

    # Phase 1: build nodes one by one
    for f in range(build_frames):
        k   = max(1, int((f + 1) / build_frames * n))
        tok = seq.steps[k - 1]
        fam = TOKEN_FAMILY[tok]
        reg = states[k - 1]
        title = (
            f"{seq.display}  │  step {k}/{n}: "
            f"{TOKEN_NAMES[tok]} [{FAM_NAME[fam]}]  →  {REG_NAME[reg]}"
        )
        render_frame(ax, seq, states, k, None, sigma, title)
        frames.append(_fig_to_pil(fig, dpi))

    # Phase 2: Gaussian pulse flows
    pulse_pos = np.linspace(0, n - 1, flow_frames)
    for f, pc in enumerate(pulse_pos):
        i_near = min(int(round(pc)), n - 1)
        tok    = seq.steps[i_near]
        fam    = TOKEN_FAMILY[tok]
        reg    = states[i_near]
        title  = (
            f"{seq.display}  │  ◎ {TOKEN_NAMES[tok]} "
            f"[{FAM_NAME[fam]}]  reg: {REG_NAME[reg]}  {seq.ourobor}"
        )
        render_frame(ax, seq, states, None, pc, sigma, title)
        frames.append(_fig_to_pil(fig, dpi))

    plt.close(fig)

    DOCS.mkdir(parents=True, exist_ok=True)
    out  = DOCS / f"cfg_seq_{key}.gif"
    rgb  = [fr.convert("RGB") for fr in frames]
    rgb[0].save(str(out), save_all=True, append_images=rgb[1:],
                duration=1000 // fps, loop=0, optimize=False)
    return out


def main() -> None:
    print(f"Generating {len(SEQUENCES)} canonical sequence CFGs → {DOCS}/\n")
    for i, (key, seq) in enumerate(SEQUENCES.items(), 1):
        n = len(seq.steps)
        print(f"[{i:02d}/{len(SEQUENCES)}] {seq.display}  ({n} steps)", end="  ", flush=True)
        out = generate_one(key, seq)
        size_kb = out.stat().st_size / 1e3
        print(f"→ {out.name}  ({size_kb:.0f} KB)")
    print("\nDone.")


if __name__ == "__main__":
    main()
