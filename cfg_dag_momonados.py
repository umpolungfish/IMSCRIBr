#!/usr/bin/env python3
"""
DAG CFGs for the 12 mOMonadOS canonical programs (src/tokens.rs).

Extends cfg_dag.py with multi-segment decomposition so sequences with
multiple FSPLIT/FFUSE pairs (e.g. VIII: FSPLIT FFUSE FSPLIT FFUSE)
render as consecutive fork blocks rather than collapsing to flat.

Output: docs/cfg_dag_momonados_{key}.gif
Run: python3 cfg_dag_momonados.py
"""

from __future__ import annotations
import io, sys
from dataclasses import dataclass
from pathlib import Path

import numpy as np
from PIL import Image
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.colors as mcolors
from matplotlib.font_manager import FontProperties

# ── Shared constants / helpers from cfg_dag ──────────────────────────────────
sys.path.insert(0, str(Path(__file__).parent))
from cfg_dag import (
    simulate_register, _draw_arrow, _draw_empty_arc, _fig_to_pil,
    TOKEN_NAMES, TOKEN_SHORT, TOKEN_FAMILY, FAM_COLOR, FAM_NAME,
    Y_MAIN, Y_T, Y_F, REG_COLOR, REG_NAME, _PULSE_WHITE, _PULSE_GOLD,
    BG, _FP_SHAVIAN, DOCS,
    VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB,
    FSPLIT, FFUSE, EVALT, EVALF, ENGAGR, IFIX,
)

# ── mOMonadOS canonical sequences (from src/tokens.rs) ───────────────────────
# Token indices identical: VINIT=0 TANCH=1 AFWD=2 AREV=3 CLINK=4 ISCRIB=5
# FSPLIT=6 FFUSE=7 EVALT=8 EVALF=9 ENGAGR=10 IFIX=11
MOM_SEQS: dict[str, tuple[int, ...]] = {
    "I_Dialetheic_Bootstrap": (5,8,6,9,7,10,11,5),   # same as IMSCRIBr
    "II_Void_Genesis":        (0,6,8,7,9,4,11,5),    # VINIT FSPLIT EVALT FFUSE EVALF CLINK IFIX ISCRIB
    "III_Anchor_Protocol":    (1,2,8,3,9,4,11,1),    # TANCH AFWD EVALT AREV EVALF CLINK IFIX TANCH
    "IV_Dual_Bootstrap":      (5,2,7,6,3,4,11,5),    # same
    "V_Linear_Chain":         (11,)*8,                # same
    "VI_Empty_Bootstrap":     (0,5,0,5,0,5,0,5),     # same
    "VII_Parakernel":         (10,2,6,8,7,9,11,10),  # ENGAGR AFWD FSPLIT EVALT FFUSE EVALF IFIX ENGAGR
    "VIII_Frobenius_Kernel":  (6,7,6,7),              # FSPLIT FFUSE FSPLIT FFUSE — double Frobenius
    "IX_Chiral_Pairs":        (2,3,2,3,2,3,2,3),     # same
    "X_Truth_Machine":        (5,6,8,11,5,6,9,11),   # same
    "XI_Eternal_Return":      (1,2,3,1,2,3,1,2),     # TANCH AFWD AREV × period
    "XII_ROM_Burn":           (8,11,9,11,10,11,5,11), # same
}

MOM_DISPLAY: dict[str, str] = {
    k: f"mOM — {k.replace('_', ' ')}" for k in MOM_SEQS
}

# ── Ouroboricity from mOMonadOS compute_tier logic ───────────────────────────
def _minimal_period(seq: tuple[int, ...]) -> int:
    n = len(seq)
    for p in range(1, n + 1):
        if n % p == 0 and all(seq[i] == seq[i % p] for i in range(n)):
            return p
    return n

def _visual_period(seq: tuple[int, ...]) -> int:
    """Smallest p where seq[:p] == seq[p:2p] — catches cut-short repeating prefixes.

    Needed for sequences like (1,2,3,1,2,3,1,2) where period=3 is visible
    but 8%3≠0 so _minimal_period returns 8.
    """
    n = len(seq)
    for p in range(1, n // 2 + 1):
        if seq[:p] == seq[p:2*p]:
            return p
    return n

def ourobor(seq: tuple[int, ...]) -> str:
    n = len(seq)
    self_ref = n > 0 and seq[0] == seq[-1]
    has_s = FSPLIT in seq; has_f = FFUSE in seq
    if not has_s and not has_f:
        frob = 0
    elif has_s and not has_f:
        frob = 1
    elif not has_s and has_f:
        frob = 2
    else:
        fs = next(i for i, t in enumerate(seq) if t == FSPLIT)
        ff = next(i for i, t in enumerate(seq) if t == FFUSE)
        frob = 1 if fs < ff else 2
    dial = EVALT in seq and EVALF in seq and ENGAGR in seq
    if dial and self_ref and frob > 0:
        p = _minimal_period(seq)
        return "O_∞" if p >= 3 else ("O₂" if p == 2 else "O₁")
    elif frob > 0 or dial:
        return "O₁"
    return "O₀"


# ── Multi-segment DAG decomposition ──────────────────────────────────────────
@dataclass
class Seg:
    """One segment of a decompressed sequence."""
    kind:     str        # 'linear' | 'fork'
    nodes:    list[int]  # linear: seq indices; fork: unused (empty)
    fsplit:   int | None
    t_branch: list[int]
    f_branch: list[int]
    ffuse:    int | None


def decompose(seq: tuple[int, ...]) -> list[Seg]:
    """Split sequence into alternating linear runs and matched fork blocks."""
    segs: list[Seg] = []
    n = len(seq)
    i = 0
    run: list[int] = []

    while i < n:
        if seq[i] == FSPLIT:
            j = next((k for k in range(i + 1, n) if seq[k] == FFUSE), None)
            if j is None:
                run.append(i); i += 1; continue
            if run:
                segs.append(Seg('linear', run[:], None, [], [], None))
                run = []
            block = list(range(i + 1, j))
            blk   = [seq[k] for k in block]
            t_a = next((m for m, t in enumerate(blk) if t == EVALT), None)
            f_a = next((m for m, t in enumerate(blk) if t == EVALF), None)
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
            segs.append(Seg('fork', [], i, tb, fb, j))
            i = j + 1
        else:
            run.append(i); i += 1

    if run:
        segs.append(Seg('linear', run[:], None, [], [], None))
    return segs


# ── Multi-segment layout ──────────────────────────────────────────────────────
def layout_segs(seq: tuple[int, ...], segs: list[Seg]):
    """Returns pos, depth, max_depth dicts indexed by seq position."""
    def slots(seg: Seg) -> int:
        if seg.kind == 'linear':
            return len(seg.nodes)
        return 1 + max(len(seg.t_branch), len(seg.f_branch), 1) + 1

    total = sum(slots(s) for s in segs)
    if total < 2: total = 2
    sw = 0.80 / (total - 1)
    x0 = 0.10

    pos:   dict[int, tuple[float, float]] = {}
    depth: dict[int, int] = {}
    sl = 0; d = 0

    for seg in segs:
        if seg.kind == 'linear':
            for idx in seg.nodes:
                pos[idx]   = (x0 + sl * sw, Y_MAIN)
                depth[idx] = d
                sl += 1; d += 1
        else:
            n_t = len(seg.t_branch); n_f = len(seg.f_branch)
            n_inner = max(n_t, n_f, 1)

            x_fs = x0 + sl * sw
            pos[seg.fsplit]   = (x_fs, Y_MAIN)
            depth[seg.fsplit] = d
            sl += 1; d += 1

            x_ff = x0 + (sl + n_inner) * sw
            for rank, idx in enumerate(seg.t_branch):
                frac = (rank + 1) / (n_t + 1)
                pos[idx]   = (x_fs + frac * (x_ff - x_fs), Y_T)
                depth[idx] = d + rank
            for rank, idx in enumerate(seg.f_branch):
                frac = (rank + 1) / (n_f + 1)
                pos[idx]   = (x_fs + frac * (x_ff - x_fs), Y_F)
                depth[idx] = d + rank

            sl += n_inner; d += n_inner
            pos[seg.ffuse]   = (x0 + sl * sw, Y_MAIN)
            depth[seg.ffuse] = d
            sl += 1; d += 1

    return pos, depth, d - 1


def build_groups(depth: dict[int, int]) -> list[list[int]]:
    by_d: dict[int, list[int]] = {}
    for idx, dv in depth.items():
        by_d.setdefault(dv, []).append(idx)
    return [by_d[k] for k in sorted(by_d)]


# ── Frame rendering ───────────────────────────────────────────────────────────
def render_frame(
    ax, seq, segs, pos, depth, states,
    visible, pulse_d, sigma, title, ouro, period=None,
):
    n = len(seq)
    w = ({i: float(np.exp(-0.5 * ((depth[i] - pulse_d) / sigma) ** 2))
          for i in range(n)} if pulse_d is not None else {i: 0.0 for i in range(n)})

    ax.clear()
    ax.set_facecolor(BG); ax.set_axis_off()
    ax.set_xlim(0, 1); ax.set_ylim(0, 1)
    ax.set_aspect("auto")
    ax.set_title(title, color="#cccccc", fontsize=6.5, pad=4)

    # ── Edges ──────────────────────────────────────────────────────────────
    prev_tail: int | None = None  # last node of previous segment (for inter-seg edges)

    for seg in segs:
        if seg.kind == 'linear':
            # Inter-segment connection from previous fork's FFUSE
            if prev_tail is not None and seg.nodes and prev_tail in visible:
                u, v = prev_tail, seg.nodes[0]
                if v in visible:
                    pw = max(w[u], w[v])
                    _draw_arrow(ax, *pos[u], *pos[v],
                                "#ffd700" if pw > 0.25 else "#3a5f80", 0.9, 0.35 + 0.5 * pw)
            for j in range(len(seg.nodes) - 1):
                u, v = seg.nodes[j], seg.nodes[j + 1]
                if u not in visible: continue
                pw = max(w[u], w[v])
                frob = TOKEN_FAMILY[seq[u]] == 1 or TOKEN_FAMILY[seq[v]] == 1
                col = "#ffd700" if (frob and pw > 0.25) else ("#ffd700" if pw > 0.25 else "#3a5f80")
                _draw_arrow(ax, *pos[u], *pos[v], col, 0.9, 0.35 + 0.5 * pw)
            prev_tail = seg.nodes[-1] if seg.nodes else prev_tail

        else:  # fork
            x_fs, y_fs = pos[seg.fsplit]
            x_ff, y_ff = pos[seg.ffuse]
            mid_x = (x_fs + x_ff) / 2

            # Branch lane labels
            if seg.fsplit in visible:
                ax.text(mid_x, Y_T + 0.10, "T", ha="center", va="bottom",
                        fontsize=5, color="#20c0b0", alpha=0.55, zorder=5)
                ax.text(mid_x, Y_F - 0.10, "F", ha="center", va="top",
                        fontsize=5, color="#e04060", alpha=0.55, zorder=5)

            # Inter-segment edge from previous tail to FSPLIT
            if prev_tail is not None and prev_tail in visible and seg.fsplit in visible:
                pw = max(w[prev_tail], w[seg.fsplit])
                _draw_arrow(ax, *pos[prev_tail], *pos[seg.fsplit],
                            "#ffd700" if pw > 0.25 else "#3a5f80", 0.9, 0.35 + 0.5 * pw)

            if seg.fsplit in visible:
                # T-arm
                if seg.t_branch:
                    x1, y1 = pos[seg.t_branch[0]]
                    pw = max(w[seg.fsplit], w[seg.t_branch[0]])
                    _draw_arrow(ax, x_fs, y_fs, x1, y1,
                                "#20d0b8" if pw > 0.25 else "#1a8070", 1.2, 0.55 + 0.4 * pw)
                else:
                    _draw_empty_arc(ax, x_fs, y_fs, x_ff, y_ff, Y_T, "#228888")

                # F-arm
                if seg.f_branch:
                    x1, y1 = pos[seg.f_branch[0]]
                    pw = max(w[seg.fsplit], w[seg.f_branch[0]])
                    _draw_arrow(ax, x_fs, y_fs, x1, y1,
                                "#ff6688" if pw > 0.25 else "#883344", 1.2, 0.55 + 0.4 * pw)
                else:
                    _draw_empty_arc(ax, x_fs, y_fs, x_ff, y_ff, Y_F, "#883344")

            # T-branch body
            for j in range(len(seg.t_branch) - 1):
                u, v = seg.t_branch[j], seg.t_branch[j + 1]
                if u not in visible: continue
                pw = max(w[u], w[v])
                _draw_arrow(ax, *pos[u], *pos[v],
                            "#20d0b8" if pw > 0.25 else "#1a8070", 0.9, 0.45 + 0.4 * pw)

            # F-branch body
            for j in range(len(seg.f_branch) - 1):
                u, v = seg.f_branch[j], seg.f_branch[j + 1]
                if u not in visible: continue
                pw = max(w[u], w[v])
                _draw_arrow(ax, *pos[u], *pos[v],
                            "#ff6688" if pw > 0.25 else "#883344", 0.9, 0.45 + 0.4 * pw)

            # Join arms → FFUSE
            if seg.ffuse in visible:
                if seg.t_branch and seg.t_branch[-1] in visible:
                    pw = max(w[seg.t_branch[-1]], w[seg.ffuse])
                    _draw_arrow(ax, *pos[seg.t_branch[-1]], *pos[seg.ffuse],
                                "#20d0b8" if pw > 0.25 else "#1a8070", 1.2, 0.55 + 0.4 * pw)
                if seg.f_branch and seg.f_branch[-1] in visible:
                    pw = max(w[seg.f_branch[-1]], w[seg.ffuse])
                    _draw_arrow(ax, *pos[seg.f_branch[-1]], *pos[seg.ffuse],
                                "#ff6688" if pw > 0.25 else "#883344", 1.2, 0.55 + 0.4 * pw)

            prev_tail = seg.ffuse

    # ── Ouroboric arc ───────────────────────────────────────────────────────
    # Fire when ouroboricity > O₀, OR when the sequence is genuinely periodic
    # (period < length) — catches "eternal return" classes whose period gives
    # them their name even when compute_tier returns O₀.
    is_periodic = period is not None and 1 < period < n
    if (ouro != "O₀" or is_periodic) and len(visible) == n:
        x0p, y0p = pos[0]; xnp, ynp = pos[n - 1]
        pb = max(w[0], w[n - 1])
        arc_label = ouro if ouro != "O₀" else f"p={period}"
        ax.annotate("", xy=(x0p, y0p), xytext=(xnp, ynp),
                    arrowprops=dict(arrowstyle="-|>", color="#ffd700" if pb > 0.25 else "#554422",
                                    lw=1.2, alpha=0.70 if pb > 0.25 else 0.25,
                                    connectionstyle="arc3,rad=0.45"), zorder=2)
        ax.text((x0p + xnp) / 2, max(y0p, ynp) + 0.16, arc_label,
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

        nv = len(visible)
        tc = "#000000" if fam == 1 else "#ffffff"
        fsi = 5.0 if nv >= 7 else 6.5
        fsn = 3.5 if nv >= 7 else 4.5
        fsr = 4.2 if nv >= 7 else 5.2

        ax.text(xi, yi, TOKEN_SHORT[seq[i]], ha="center", va="center",
                fontsize=fsi, color=tc, fontweight="bold", zorder=4)
        ax.text(xi, yi + 0.105, TOKEN_NAMES[seq[i]], ha="center", va="bottom",
                fontsize=fsn, color="#999999", zorder=4)
        ax.text(xi, yi - 0.090, REG_NAME[states[i]], ha="center", va="top",
                fontsize=fsr, color=REG_COLOR[states[i]], fontweight="bold", zorder=4)

    # ── Footer ──────────────────────────────────────────────────────────────
    ax.text(0.5, 0.03, ouro, ha="center", va="center",
            fontsize=6.5, color="#aaaadd", fontweight="bold", zorder=5)
    for fi in range(4):
        lx = 0.70 + fi * 0.075
        ax.scatter([lx], [0.06], c=[FAM_COLOR[fi]], s=22, zorder=6)
        ax.text(lx + 0.01, 0.06, FAM_NAME[fi][0], va="center",
                fontsize=3.5, color="#666666", zorder=6)


def generate_one(
    key:          str,
    seq:          tuple[int, ...],
    build_frames: int = 20,
    flow_frames:  int = 48,
    fps:          int = 14,
    dpi:          int = 200,
) -> Path:
    states  = simulate_register(seq)
    segs    = decompose(seq)
    pos, dep, max_d = layout_segs(seq, segs)
    sigma   = max(0.7, max_d / 7.0)
    groups  = build_groups(dep)
    all_i   = set(range(len(seq)))
    ouro    = ourobor(seq)
    period  = _visual_period(seq)
    display = MOM_DISPLAY[key]

    fig, ax = plt.subplots(figsize=(10, 4.4), facecolor=BG)
    frames: list[Image.Image] = []

    # Build phase
    visible: set[int] = set()
    for f in range(build_frames):
        target = max(1, int((f + 1) / build_frames * len(groups)))
        for g in groups[:target]:
            visible.update(g)
        last = groups[target - 1][0]
        tok  = seq[last]
        title = (f"{display}  │  {TOKEN_NAMES[tok]}"
                 f" [{FAM_NAME[TOKEN_FAMILY[tok]]}]"
                 f"  d={dep[last]}  →  {REG_NAME[states[last]]}")
        render_frame(ax, seq, segs, pos, dep, states,
                     set(visible), None, sigma, title, ouro, period)
        frames.append(_fig_to_pil(fig, dpi))

    # Flow phase
    for pd in np.linspace(-0.5, max_d + 0.5, flow_frames):
        i_near = min(range(len(seq)), key=lambda i: abs(dep[i] - pd))
        tok    = seq[i_near]
        title  = (f"{display}  │  ◎ {TOKEN_NAMES[tok]}"
                  f" [{FAM_NAME[TOKEN_FAMILY[tok]]}]"
                  f"  reg: {REG_NAME[states[i_near]]}  {ouro}")
        render_frame(ax, seq, segs, pos, dep, states,
                     all_i, pd, sigma, title, ouro, period)
        frames.append(_fig_to_pil(fig, dpi))

    plt.close(fig)
    DOCS.mkdir(parents=True, exist_ok=True)
    out = DOCS / f"cfg_dag_momonados_{key}.gif"
    rgb = [fr.convert("RGB") for fr in frames]
    rgb[0].save(str(out), save_all=True, append_images=rgb[1:],
                duration=1000 // fps, loop=0, optimize=False)
    return out


def main() -> None:
    print(f"Generating {len(MOM_SEQS)} mOMonadOS DAG CFGs → {DOCS}/\n")
    for i, (key, seq) in enumerate(MOM_SEQS.items(), 1):
        segs = decompose(seq)
        fork_segs = [s for s in segs if s.kind == 'fork']
        ouro = ourobor(seq)
        n_forks = len(fork_segs)
        tag = (f"{n_forks} fork(s)" if n_forks else "linear") + f"  {ouro}"
        print(f"[{i:02d}/{len(MOM_SEQS)}] {MOM_DISPLAY[key]}  [{tag}]",
              end="  ", flush=True)
        out = generate_one(key, seq)
        print(f"→ {out.name}  ({out.stat().st_size/1e3:.0f} KB)")
    print("\nDone.")


if __name__ == "__main__":
    main()
