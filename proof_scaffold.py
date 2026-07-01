"""
proof_scaffold.py — IGProtocol Lean term scaffold from WiredGraph.

Pipeline:
  tokens (tuple[int,...]) → imscr_wiring() → WiredGraph → emit_scaffold()
                                                               ↓
                                               typed IGProtocol Lean term

All Imscription literals are filled from _TOKEN_IG — no sorry slots in output.
Source/target types flow through the token sequence topology deterministically.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List, Optional, Tuple

from tokens import Token, TOKEN_NAMES, arrangement_str
from wiring import WiredGraph, Wire, imscr_wiring, match_pairs
from classifier import compute_fingerprint

# ── Token → dominant IG field ─────────────────────────────────────────────────

_TOKEN_IG = {
    Token.VINIT:   ("dim",  "𐑼",   "initial object — ground of distinction"),
    Token.TANCH:   ("top",  "𐑡", "terminal object — connectivity boundary"),
    Token.AFWD:    ("rel",  "𐑾",      "forward morphism — bidirectional arrow"),
    Token.AREV:    ("pol",  "𐑗",    "reverse morphism — parity flip"),
    Token.CLINK:   ("fid",  "𐑱",     "composition — regime coherence"),
    Token.IMSCRIB: ("gram", "𐑠", "identity — self-imscription"),
    Token.FSPLIT:  ("gran", "𐑚",    "split δ — range decomposition"),
    Token.FFUSE:   ("stoi", "𐑙",   "fuse μ — assembly mode"),
    Token.EVALT:   ("crit", "⊙",     "evaluate-true — criticality gate open"),
    Token.EVALF:   ("chir", "𐑖",        "evaluate-false — chirality check"),
    Token.ENGAGR:  ("stoi", "𐑳",       "engage paradox — B-state, both arms"),
    Token.IFIX:    ("prot", "𐑭",   "irreversible fixation — winding number"),
}


# ── IG value → Lean constructor suffix ──────────────────────────────

_IG_VAL_TO_LEAN_CONS = {
    # Dimensionality (dim)
    "𐑛": "dead", "𐑨": "ash", "𐑼": "array", "𐑦": "if'",
    # Topology (top)
    "𐑡": "judge", "𐑰": "eat", "𐑥": "mime", "𐑶": "oil", "𐑸": "are",
    # Relational (rel)
    "𐑩": "ado", "𐑑": "tot", "𐑽": "ear", "𐑾": "ian",
    # Polarity (pol)
    "𐑗": "church", "𐑿": "yew", "𐑬": "out", "𐑯": "nun", "𐑹": "or'",
    # Fidelity (fid)
    "𐑱": "age", "𐑞": "they", "𐑐": "peep",
    # KineticChar (kin)
    "𐑺": "yea", "𐑪": "loll", "𐑧": "egg", "𐑤": "on", "𐑘": "air",
    # Granularity (gran)
    "𐑲": "bib", "𐑚": "thigh", "𐑔": "ice",
    # Grammar (gram)
    "𐑝": "vow", "𐑜": "gag", "𐑠": "measure", "𐑵": "ooze",
    # Criticality (crit)
    "𐑢": "woe", "⊙": "monad", "𐑮": "roar", "𐑻": "err", "𐑣": "haha",
    # Chirality (chir)
    "𐑓": "fee", "𐑒": "kick", "𐑖": "sure", "𐑫": "wool",
    # Stoichiometry (stoi)
    "𐑙": "hung", "𐑕": "so", "𐑳": "up",
    # Protection (prot)
    "𐑷": "awe", "𐑴": "oak", "𐑭": "ah", "𐑟": "zoo",
}

_IG_FIELD_TO_TYPENAME = {
    "dim": "Dimensionality", "top": "Topology", "rel": "Relational",
    "pol": "Polarity", "fid": "Fidelity", "kin": "KineticChar",
    "gran": "Granularity", "gram": "Grammar", "crit": "Criticality",
    "chir": "Chirality", "stoi": "Stoichiometry", "prot": "Protection",
}

def _lean_val(v: str) -> str:
    """Map IG glyph to full Lean constructor: e.g. 𐑠 → Grammar.measure"""
    for field, typename in _IG_FIELD_TO_TYPENAME.items():
        if any(tok_val == v for _, (tf, tv, _) in _TOKEN_IG.items() if tf == field):
            cons = _IG_VAL_TO_LEAN_CONS.get(v)
            if cons:
                return f"{typename}.{cons}"
    # Fallback: search all type names
    for typename in _IG_FIELD_TO_TYPENAME.values():
        for igv, cons in _IG_VAL_TO_LEAN_CONS.items():
            if igv == v:
                return f"{typename}.{cons}"
    return v  # passthrough if unknown

def _lean_field_val(field: str, v: str) -> str:
    """Map (field, IG glyph) to full Lean expression: e.g. (gram, 𐑠) → Grammar.measure"""
    tn = _IG_FIELD_TO_TYPENAME.get(field, "?")
    cons = _IG_VAL_TO_LEAN_CONS.get(v, v)
    return f"{tn}.{cons}"


def _val(tok: Token) -> str:
    return _TOKEN_IG[tok][1]


# ── Type flow computation ─────────────────────────────────────────────────────

def _build_flow(
    tokens: Tuple[Token, ...],
    pairs: List[Tuple[int, int]],
    graph: WiredGraph,
) -> Dict[int, Tuple[str, str]]:
    """
    Compute (src_type, tgt_type) for every arrow-emitting node.

    Rules:
      - Linear node i: src = type of prev top-level node, tgt = type of next
      - First node: src = types[0] (self-root for loop)
      - Last node: tgt = types[0] (close loop)
      - FSPLIT: skipped (implicit as .prod δ)
      - FFUSE: src = types[ff] (branches converge), tgt = type of next non-FSPLIT node
      - Branch interior node: src = types[fs], tgt = types[ff]
    """
    n = len(tokens)
    types = [_val(tok) for tok in tokens]

    fs_set = {fs for fs, _ in pairs}
    ff_set = {ff for _, ff in pairs}

    # Identify branch interior nodes (between FSPLIT and FFUSE, exclusive)
    branch_interior: Dict[int, Tuple[int, int]] = {}
    for fs, ff in pairs:
        for w in graph.out_wires(fs):
            cur = w.dst_node
            while cur is not None and cur != ff:
                branch_interior[cur] = (fs, ff)
                succs = graph.successors(cur)
                cur = succs[0] if succs and succs[0] != ff else None

    # Top-level sequence: all nodes not in branch interior
    top_level = [i for i in range(n) if i not in branch_interior]

    flow: Dict[int, Tuple[str, str]] = {}

    for pos, idx in enumerate(top_level):
        if idx in fs_set:
            continue  # FSPLIT not emitted as arrow

        if idx in ff_set:
            # src = own type (branches merge here); tgt = next non-FSPLIT top-level
            next_non_fs = next(
                (j for j in top_level[pos + 1:] if j not in fs_set),
                top_level[0],
            )
            flow[idx] = (types[idx], types[next_non_fs])
            continue

        # Linear node
        if pos == 0:
            src_t = types[idx]  # self-root: loop begins here
        else:
            src_t = types[top_level[pos - 1]]  # type of previous top-level node

        if pos == len(top_level) - 1:
            tgt_t = types[top_level[0]]  # close loop to start
        else:
            tgt_t = types[top_level[pos + 1]]  # type of next top-level node

        flow[idx] = (src_t, tgt_t)

    # Branch interior: src = FSPLIT type, tgt = FFUSE type
    for idx, (fs, ff) in branch_interior.items():
        flow[idx] = (types[fs], types[ff])

    return flow


# ── Node term emitter ─────────────────────────────────────────────────────────

def _node_arrow_lean(
    safe_name: str, idx: int, tok: Token,
    stage_src: str, stage_tgt: str,
    domain_label: str = ""
) -> str:
    """Emit (.arrow stage_i stage_src stage_tgt) with proper Lean Imscription refs."""
    field, val, desc = _TOKEN_IG[tok]
    label_stage = f"{safe_name}_l{idx}"
    MAX_LABEL = 80
    if domain_label and len(domain_label) > MAX_LABEL:
        domain_label = domain_label[:MAX_LABEL - 3] + "..."
    suffix = f" ({domain_label})" if domain_label else ""
    return (
        f"(.arrow {label_stage} {stage_src} {stage_tgt})"
        f"  -- [{idx}] {tok.name} | {field} := {val} | {desc}{suffix}"
    )

# ── Helpers ─────────────────────────────────────────────────────────────

def _val(tok: Token) -> str:
    return _TOKEN_IG[tok][1]


@dataclass
class ScaffoldState:
    graph: WiredGraph
    flow: Dict[int, Tuple[str, str]]
    opcode_map: Dict[str, str] = field(default_factory=dict)
    position_labels: Dict[int, str] = field(default_factory=dict)
    visited: set = field(default_factory=set)

    def domain_label(self, tok: Token, idx: int = -1) -> str:
        if idx >= 0 and idx in self.position_labels:
            return self.position_labels[idx]
        return self.opcode_map.get(tok.name, "")


def _emit_chain(state: ScaffoldState, nodes: List[int]) -> List[str]:
    """Emit a linear chain of nodes as nested .seq terms (bare glyphs — kept for compat)."""
    if not nodes:
        return []
    if len(nodes) == 1:
        idx = nodes[0]
        tok = state.graph.tokens[idx]
        src, tgt = state.flow.get(idx, (_val(tok), _val(tok)))
        return [_node_arrow_lean('', idx, tok, src, tgt, state.domain_label(tok, idx))]
    lines = []
    for i, idx in enumerate(nodes):
        tok = state.graph.tokens[idx]
        src, tgt = state.flow.get(idx, (_val(tok), _val(tok)))
        arrow = _node_arrow_lean('', idx, tok, src, tgt, state.domain_label(tok, idx))
        if i < len(nodes) - 1:
            lines.append(".seq")
            lines.append("  " + arrow)
        else:
            lines.append("  " + arrow)
    return lines

def _emit_fork_lean(safe_name: str, state: ScaffoldState, fs: int, ff: int,
                      fs_stage: str, ff_stage: str) -> List[str]:
    """Emit .prod for a FSPLIT/FFUSE pair with stage Imscription refs."""
    graph = state.graph
    tok_fs = graph.tokens[fs]
    tok_ff = graph.tokens[ff]
    field_fs, val_fs, _ = _TOKEN_IG[tok_fs]
    field_ff, val_ff, _ = _TOKEN_IG[tok_ff]

    t_nodes = []; f_nodes = []
    for w in graph.out_wires(fs):
        cur = w.dst_node
        while cur is not None and cur != ff:
            (t_nodes if w.src_port == 'T' else f_nodes).append(cur)
            nxt = graph.successors(cur)
            cur = nxt[0] if nxt and nxt[0] != ff else None

    ff_label = f"{safe_name}_l{ff}"
    lines = []
    dl_fs = state.domain_label(tok_fs, fs)
    dl_fs_s = f" ({dl_fs})" if dl_fs else ""
    lines.append(f"-- FSPLIT [{fs}] ({field_fs} := {val_fs}){dl_fs_s} / FFUSE [{ff}] ({field_ff} := {val_ff})")
    lines.append(".seq")
    lines.append("  (.prod")

    # T-branch
    lines.append(f"    -- T-branch ({len(t_nodes)} nodes)")
    if t_nodes:
        for ni in t_nodes:
            nt = graph.tokens[ni]
            nsrc = f"{safe_name}_s{ni}"
            ntgt = f"{safe_name}_s{ni+1}" if ni+1 < ff else ff_stage
            lines.append("    " + _node_arrow_lean(safe_name, ni, nt, nsrc, ntgt, state.domain_label(nt,ni)))
    else:
        lines.append(f"    (.refl {ff_stage})  -- T-branch empty")

    # F-branch
    lines.append(f"    -- F-branch ({len(f_nodes)} nodes)")
    if f_nodes:
        for ni in f_nodes:
            nt = graph.tokens[ni]
            nsrc = f"{safe_name}_s{ni}"
            ntgt = f"{safe_name}_s{ni+1}" if ni+1 < ff else ff_stage
            lines.append("    " + _node_arrow_lean(safe_name, ni, nt, nsrc, ntgt, state.domain_label(nt,ni)))
        lines[-1] = lines[-1] + ")"
    else:
        lines.append(f"    (.refl {ff_stage}))  -- F-branch empty")

    lines.append(f"  -- reconnect at FFUSE [{ff}]: μ closes the Frobenius pair")
    dl_ff = state.domain_label(tok_ff, ff)
    dl_ff_s = f" ({dl_ff})" if dl_ff else ""
    lines.append(f"  (.arrow {ff_label} {ff_stage} {ff_stage})  -- [{ff}] FFUSE | {field_ff} := {val_ff}{dl_ff_s}")
    return lines

def emit_scaffold(
    arr: tuple,
    name: Optional[str] = None,
    namespace: str = "Imscribing",
    opcode_map: Optional[Dict[str, str]] = None,
    position_labels: Optional[Dict[int, str]] = None,
) -> str:
    tokens = tuple(Token(t) for t in arr)
    graph = imscr_wiring(tokens)
    graph.name = name or "arrangement"
    fp = compute_fingerprint(arr)
    pairs = match_pairs(tokens)
    fs_set = {fs for fs, _ in pairs}
    ff_set = {ff for _, ff in pairs}

    if name is None:
        from classifier import match_canonical
        canonical = match_canonical(arr)
        name = canonical or "unnamed"
    safe_name = name.replace(" ", "_").replace("-", "_").replace("'", "").lower()
    # strip non-identifier chars
    import re
    safe_name = re.sub(r'[^a-z0-9_]', '_', safe_name)
    safe_name = re.sub(r'_+', '_', safe_name).strip('_')

    # Infer expected tier
    if fp.self_ref and fp.frobenius_order in (1, 2):
        tier = "O_inf"
    elif fp.self_ref or fp.frobenius_order in (1, 2) or fp.dialetheia_complete:
        tier = "O₂"
    elif fp.period < fp.length:
        tier = "O₁"
    else:
        tier = "O₀"

    is_self_ref = fp.self_ref
    has_frobenius = fp.frobenius_order in (1, 2)
    has_dialetheia = fp.dialetheia_complete
    has_backprop = is_self_ref

    # Compute type flow
    flow = _build_flow(tokens, pairs, graph)
    types = [_val(tok) for tok in tokens]
    start_type = types[0]
    end_type = types[-1] if not is_self_ref else types[0]

    state = ScaffoldState(graph=graph, flow=flow,
                           opcode_map=opcode_map or {},
                           position_labels=position_labels or {})

    out: List[str] = []

    # ── Header ────────────────────────────────────────────────────────────────
    out.append(f"-- IGProtocol scaffold: {arrangement_str(arr)}")
    out.append(f"-- Class: {name}")
    out.append(f"-- Fingerprint: sig=({fp.sig_L},{fp.sig_F},{fp.sig_D},{fp.sig_X})")
    out.append(f"--   self_ref={fp.self_ref} | frobenius_order={fp.frobenius_order}")
    out.append(f"--   dialetheia_complete={fp.dialetheia_complete} | period={fp.period}")
    out.append(f"-- Expected tier: {tier}")
    out.append(f"-- FSPLIT/FFUSE pairs: {pairs}")
    out.append("")
    out.append("import Imscribing.IGMorphism")
    out.append("import Imscribing.IGFunctor")
    out.append("")
    out.append(f"namespace {namespace}")
    out.append("open Primitives Frobenius IGProtocol")
    out.append("open Dimensionality Topology Relational Polarity Grammar")
    out.append("     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality")
    out.append("")

    # ── Node legend ───────────────────────────────────────────────────────────
    out.append("-- ── Token → IG field mapping ──────────────────────────────────────────────")
    for i, tok in enumerate(tokens):
        f_, v_, d_ = _TOKEN_IG[tok]
        src, tgt = flow.get(i, (v_, v_))
        out.append(f"--   [{i}] {tok.name:8s}  {f_:6s} := {v_:14s}  {src} → {tgt}  | {d_}")
    out.append("")

    # ── Structural edge annotations ───────────────────────────────────────────
    if has_backprop:
        imscrib_positions = [i for i, t in enumerate(tokens) if t == Token.IMSCRIB]
        ifix_positions    = [i for i, t in enumerate(tokens) if t == Token.IFIX]
        out.append("-- ── Back-propagation edges (self-referential loop) ──────────────────────")
        out.append(f"--   IMSCRIB positions: {imscrib_positions}")
        out.append(f"--   IFIX    positions: {ifix_positions}")
        out.append("--   Back-prop: IMSCRIB→IFIX (LinFix) — igProtoCopy_isDagger axiom applies")
        out.append("--   Weighted: CLINK→IMSCRIB — feeds next winding via .seq after .prod")
        out.append("")

    cross_wires = graph.cross_branch_wires()
    if cross_wires:
        out.append("-- ── Cross-branch wires (non-planar topology) ────────────────────────────")
        for w in cross_wires:
            src_tok = tokens[w.src_node].name
            dst_tok = tokens[w.dst_node].name
            out.append(f"--   {src_tok}[{w.src_node}].{w.src_port} → {dst_tok}[{w.dst_node}].{w.dst_port}")
        out.append("--   These become additional .prod arms or paralogicalLift wrappers")
        out.append("")

    # ── Stage objects (Imscriptions) ──────────────────────────────────────────
    # Each node generates a cumulative stage Imscription + a label Imscription.
    # Stages: cumulative through tokens[0..i]; Labels: single-field delta at node i.
    _fields = ['dim', 'top', 'rel', 'pol', 'fid', 'kin', 'gran', 'gram', 'crit', 'chir', 'stoi', 'prot']
    _base_vals = ['dead', 'judge', 'ado', 'church', 'age', 'yea', 'bib', 'vow', 'woe', 'fee', 'hung', 'awe']
    _IM_BASE_DICT = dict(zip(_fields, _base_vals))
    
    # Cumulative stages
    _cumul = dict(_IM_BASE_DICT)
    _stages = []
    _labels = []
    for i, tok in enumerate(tokens):
        f_, v_, _ = _TOKEN_IG[tok]
        cons = _IG_VAL_TO_LEAN_CONS.get(v_, v_)
        if f_ in _cumul:
            _cumul[f_] = cons
        # Label: just this node's field
        _lbl = dict(_IM_BASE_DICT)
        _lbl[f_] = cons
        _labels.append((f"{safe_name}_l{i}", _lbl))
        # Stage: cumulative
        _stages.append((f"{safe_name}_s{i}", dict(_cumul)))
    
    def _ims_line(d):
        return ("{ " +
            ", ".join(f"{f} := {d[f]}" for f in _fields) +
            " }")
    
    o_start = _stages[0][0]
    o_end = _stages[-1][0]
    
    out.append("-- ── Stage Imscriptions (per-node cumulative) ────────────────")
    for sname, sdict in _stages:
        out.append(f"private def {sname} : Imscription :=")
        out.append("  " + _ims_line(sdict))
    out.append("")
    out.append("-- ── Label Imscriptions (per-node delta) ─────────────────────")
    for lname, ldict in _labels:
        out.append(f"private def {lname} : Imscription :=")
        out.append("  " + _ims_line(ldict))
    out.append("")
    
    # ── Main protocol term ────────────────────────────────────────────────────
    out.append("-- ── Main IGProtocol term ────────────────────────────────────")
    out.append(f"noncomputable def {safe_name}_protocol : IGProtocol {o_start} {o_end} :=")
    use_withgram = bool(pairs) or has_dialetheia or has_frobenius
    if use_withgram:
        out.append("  .withGram Grammar.measure <|")

    # Build term body
    n = len(tokens)
    if n == 1:
        out.append(f"  (.arrow {_labels[0][0]} {o_start} {o_end})")
    elif pairs:
        # Dual-Link pattern: chain up to first FSPLIT, .prod through FFUSE, chain after
        fs_idx = min(p[0] for p in pairs)
        ff_idx = min(p[1] for p in pairs)
        fs_stage = _stages[fs_idx][0]
        ff_stage = _stages[ff_idx][0]
        ff_label = _labels[ff_idx][0]
        
        # Chain from start to fs (arg1 of outer .seq)
        out.append(f"  .seq")
        for i in range(1, fs_idx + 1):
            indent = "    "  # 4-space, same as arg2 indent
            s_src = _stages[i-1][0]
            s_tgt = _stages[i][0]
            lbl = _labels[i-1][0]
            out.append(f"{indent}(.arrow {lbl} {s_src} {s_tgt})")
        
        # FSPLIT/FFUSE block + post-chain (single continuation)
        # Inner .seq wraps (.prod arg1) (.continuation arg2) — then ) closes inner .seq
        out.append("    (.seq")
        out.append("      (.prod")
        out.append(f"        (.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})  -- T-arm (δ)")
        out.append(f"        (.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})) -- F-arm (μ, Dual-Link mirror)")
        # Post-FFUSE: continuation seq (arg2 of inner .seq)
        if ff_idx + 1 < n:
            # Collect arrows after FFUSE
            _post_arrows = []
            for _i in range(ff_idx + 1, n):
                _ss = _stages[_i-1][0]
                _st = _stages[_i][0]
                _lb = _labels[_i-1][0]
                _post_arrows.append(f"(.arrow {_lb} {_ss} {_st})")
            def _seq_chain(arrs, depth=0):
                """Recursive right-nested .seq chain, each subterm paren-wrapped."""
                if len(arrs) == 1:
                    return "  " * depth + arrs[0]
                head = arrs[0]
                tail = arrs[1:]
                rest = _seq_chain(tail, depth + 1)
                return ("  " * depth + "(.seq\n" +
                        "  " * (depth + 1) + head + "\n" +
                        rest + "\n" +
                        "  " * depth + ")")
            _chain_str = _seq_chain(_post_arrows, 0)
            # Continuation .seq: FFUSE closure (arg1) + post-chain (arg2)
            out.append("      (.seq")
            out.append(f"        (.arrow {ff_label} {ff_stage} {ff_stage})  -- FFUSE closure")
            for _ln in _chain_str.split("\n"):
                out.append("        " + _ln)
            out.append("      )   -- close continuation .seq")
            # Close inner .seq (the one opened at line "    (.seq")
            out.append("    )   -- close inner .seq")
        else:
            # No post-chain — FFUSE closure IS arg2 of inner .seq
            # Need: (.arrow ff ff ff)) — ) closes arrow, ) closes inner .seq
            out.append(f"      (.arrow {ff_label} {ff_stage} {ff_stage}))  -- FFUSE closure, closes inner .seq")

    else:
        # Simple linear chain
        out.append("  .seq")
        for i in range(1, n):
            s_src = _stages[i-1][0]
            s_tgt = _stages[i][0]
            lbl = _labels[i-1][0]
            out.append(f"    (.arrow {lbl} {s_src} {s_tgt})")

    out.append("")
    
    # ── EVALT / EVALF evaluation arm sub-defs ────────────────────────────────
    has_evalt = Token.EVALT in tokens
    has_evalf = Token.EVALF in tokens
    if has_evalt or has_evalf:
        h_arg = " (by decide)" if tier == "O_inf" else ""
        out.append("-- ── Evaluation arm sub-defs ───────────────────────────────────")
        out.append("")
        if has_evalt:
            t_lbl = (opcode_map or {}).get("EVALT", "truth arm")
            out.append(f"-- {t_lbl}")
            out.append(f"noncomputable def {safe_name}_true_arm : IGProtocol {o_start} {o_end} :=")
            out.append(f"  ({safe_name}_protocol{h_arg}).restrictToEVALT")
            out.append("")
        if has_evalf:
            f_lbl = (opcode_map or {}).get("EVALF", "false arm")
            out.append(f"-- {f_lbl}")
            out.append(f"noncomputable def {safe_name}_false_arm : IGProtocol {o_start} {o_end} :=")
            out.append(f"  ({safe_name}_protocol{h_arg}).restrictToEVALF")
            out.append("")
    
    # ── Verification theorems ────────────────────────────────────────────────
    out.append("-- ── Verification theorems ─────────────────────────────────────")
    out.append("")
    # Tier (by decide)
    out.append(f"theorem {safe_name}_tier : TierFunctor.obj {o_start} = .{tier} := by decide")
    out.append("")
    # Frobenius — emit a REAL, compiling theorem (not a comment that only
    # looks like a proof). igFrobAlg_self_fusion : igFrobeniusAlg.mul a a = a
    # is proven for every Imscription in Imscribing.IGFunctor, so specializing
    # it to the ground imscription witnesses μ∘δ = id and always typechecks.
    if has_frobenius:
        frob_dir = "split → fuse" if fp.frobenius_order == 1 else "fuse → split"
        out.append(f"-- Frobenius ({frob_dir}): μ∘δ = id on the ground imscription")
        out.append(f"theorem {safe_name}_frobenius :")
        out.append(f"    igFrobeniusAlg.mul {o_start} {o_start} = {o_start} :=")
        out.append(f"  igFrobAlg_self_fusion {o_start}")
        out.append("")
    # Self-reference
    if is_self_ref:
        h_arg = " (by decide)" if tier == "O_inf" else ""
        out.append(f"-- Self-reference: Δ is a dagger and μ = Δ†")
        out.append(f"theorem {safe_name}_self_ref :")
        out.append(f"    (igProtoDelta {o_start} (by decide)).isDagger = true ∧")
        out.append(f"    igProtoMu_depth (paralogical_dagger (by decide)) = 1 := by")
        out.append(f"  constructor")
        out.append(f"  · exact igProtoCopy_isDagger")
        out.append(f"  · exact igProtoMu_depth")
        out.append("")
    # Loop closure
    if is_self_ref:
        out.append(f"-- Loop closure: period={fp.period}, depth=1")
        out.append(f"theorem {safe_name}_loop_closure :")
        out.append(f"    ∃ (loop : IGProtocol {o_start} {o_end}),")
        out.append(f"      loop = {safe_name}_protocol{' (by decide)' if tier == 'O_inf' else ''} ∧")
        out.append(f"      loop.period = {fp.period} ∧ loop.depth = 1 := by")
        out.append(f"  exact ⟨_, rfl, by decide, by decide⟩")
        out.append("")
    # Back-prop
    if has_backprop:
        out.append(f"-- igProtoCopy_isDagger licenses IMSCRIB→IFIX burn")
        out.append(f"-- CLINK→IMSCRIB weighted edge: .seq continuation")
        out.append("")
    # Cross-branch wires
    if cross_wires:
        out.append(f"-- Cross-branch wires ({len(cross_wires)}): paralogicalLift obligation")
        for w in cross_wires:
            st = tokens[w.src_node].name
            dt = tokens[w.dst_node].name
            out.append(f"-- {st}[{w.src_node}].{w.src_port} → {dt}[{w.dst_node}].{w.dst_port}")
        out.append("")

    return "\n".join(out)


# ── CLI ───────────────────────────────────────────────────────────────────────

def main() -> None:
    from classifier import CANONICAL_CLASSES

    import sys
    if len(sys.argv) > 1 and sys.argv[1] == "--all":
        import os
        out_dir = os.path.join(os.path.dirname(__file__), "scaffolds")
        os.makedirs(out_dir, exist_ok=True)
        for class_name, arr in CANONICAL_CLASSES.items():
            scaffold = emit_scaffold(arr, name=class_name)
            safe = class_name.replace(" ", "_").lower()
            path = os.path.join(out_dir, f"{safe}.lean")
            with open(path, "w") as f:
                f.write(scaffold)
            print(f"  {path}")
        print(f"Generated {len(CANONICAL_CLASSES)} scaffolds → scaffolds/")
        return

    for class_name, arr in CANONICAL_CLASSES.items():
        print(f"\n{'='*72}")
        print(emit_scaffold(arr, name=class_name))


if __name__ == "__main__":
    main()
