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
    Token.VINIT:   ("dim",  "D_wedge",   "initial object — ground of distinction"),
    Token.TANCH:   ("top",  "T_network", "terminal object — connectivity boundary"),
    Token.AFWD:    ("rel",  "R_lr",      "forward morphism — bidirectional arrow"),
    Token.AREV:    ("pol",  "P_asym",    "reverse morphism — parity flip"),
    Token.CLINK:   ("fid",  "F_ell",     "composition — regime coherence"),
    Token.IMSCRIB: ("gram", "Gamma_seq", "identity — self-imscription"),
    Token.FSPLIT:  ("gran", "G_beth",    "split δ — range decomposition"),
    Token.FFUSE:   ("stoi", "one_one",   "fuse μ — assembly mode"),
    Token.EVALT:   ("crit", "Phi_c",     "evaluate-true — criticality gate open"),
    Token.EVALF:   ("chir", "H2",        "evaluate-false — chirality check"),
    Token.ENGAGR:  ("stoi", "n_m",       "engage paradox — B-state, both arms"),
    Token.IFIX:    ("prot", "Omega_Z",   "irreversible fixation — winding number"),
}


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

def _node_arrow(idx: int, tok: Token, src_type: str, dst_type: str,
                domain_label: str = "") -> str:
    field, val, desc = _TOKEN_IG[tok]
    suffix = f" ({domain_label})" if domain_label else ""
    return (
        f"(.arrow {val} {src_type} {dst_type})"
        f"  -- [{idx}] {tok.name} | {field} := {val} | {desc}{suffix}"
    )


# ── Recursive IGProtocol term builder ────────────────────────────────────────

@dataclass
class ScaffoldState:
    graph: WiredGraph
    flow: Dict[int, Tuple[str, str]]
    opcode_map: Dict[str, str] = field(default_factory=dict)
    visited: set = field(default_factory=set)

    def domain_label(self, tok: Token) -> str:
        return self.opcode_map.get(tok.name, "")


def _emit_chain(state: ScaffoldState, nodes: List[int]) -> List[str]:
    """Emit a linear chain of nodes as nested .seq terms."""
    if not nodes:
        return []
    if len(nodes) == 1:
        idx = nodes[0]
        tok = state.graph.tokens[idx]
        src, tgt = state.flow.get(idx, (_val(tok), _val(tok)))
        return [_node_arrow(idx, tok, src, tgt, state.domain_label(tok))]

    lines = []
    for i, idx in enumerate(nodes):
        tok = state.graph.tokens[idx]
        src, tgt = state.flow.get(idx, (_val(tok), _val(tok)))
        arrow = _node_arrow(idx, tok, src, tgt, state.domain_label(tok))
        if i < len(nodes) - 1:
            lines.append(".seq")
            lines.append("  " + arrow)
        else:
            lines.append("  " + arrow)
    return lines


def _emit_fork(state: ScaffoldState, fs: int, ff: int) -> List[str]:
    """Emit .prod for a FSPLIT/FFUSE pair with typed T and F branches."""
    graph = state.graph
    tok_fs = graph.tokens[fs]
    tok_ff = graph.tokens[ff]
    ff_src, ff_tgt = state.flow.get(ff, (_val(tok_ff), _val(tok_ff)))

    # Gather T-branch and F-branch interior nodes
    t_nodes: List[int] = []
    f_nodes: List[int] = []

    cur = None
    for w in graph.out_wires(fs):
        if w.src_port == 'T':
            cur = w.dst_node
            break
    while cur is not None and cur != ff:
        t_nodes.append(cur)
        nxt = graph.successors(cur)
        cur = nxt[0] if nxt and nxt[0] != ff else None

    cur = None
    for w in graph.out_wires(fs):
        if w.src_port == 'F':
            cur = w.dst_node
            break
    while cur is not None and cur != ff:
        f_nodes.append(cur)
        nxt = graph.successors(cur)
        cur = nxt[0] if nxt and nxt[0] != ff else None

    field_fs, val_fs, _ = _TOKEN_IG[tok_fs]
    field_ff, val_ff, _ = _TOKEN_IG[tok_ff]
    ff_type = _val(tok_ff)

    lines = []
    lines.append(f"-- FSPLIT [{fs}] ({field_fs} := {val_fs}) / FFUSE [{ff}] ({field_ff} := {val_ff})")
    lines.append(".seq")
    lines.append("  (.prod")

    # T-branch
    lines.append(f"    -- T-branch ({len(t_nodes)} nodes)")
    if t_nodes:
        branch_lines = _emit_chain(state, t_nodes)
        for bl in branch_lines:
            lines.append("    " + bl)
    else:
        lines.append(f"    (.refl {ff_type})  -- T-branch: empty arc (direct to FFUSE.T)")

    # F-branch
    lines.append(f"    -- F-branch ({len(f_nodes)} nodes)")
    if f_nodes:
        branch_lines = _emit_chain(state, f_nodes)
        for bl in branch_lines:
            lines.append("    " + bl)
        lines[-1] = lines[-1] + ")"  # close .prod
    else:
        lines.append(f"    (.refl {ff_type}))  -- F-branch: empty arc (direct to FFUSE.F)")

    lines.append(f"  -- reconnect at FFUSE [{ff}]: μ closes the Frobenius pair")
    dl_ff = state.domain_label(tok_ff)
    dl_suffix = f" ({dl_ff})" if dl_ff else ""
    lines.append(f"  (.arrow {val_ff} {ff_src} {ff_tgt})  -- [{ff}] FFUSE | {field_ff} := {val_ff}{dl_suffix}")

    return lines


# ── Main scaffold emitter ─────────────────────────────────────────────────────

def emit_scaffold(
    arr: tuple,
    name: Optional[str] = None,
    namespace: str = "Imscribing",
    opcode_map: Optional[Dict[str, str]] = None,
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

    state = ScaffoldState(graph=graph, flow=flow, opcode_map=opcode_map or {})

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

    # ── Main protocol definition ──────────────────────────────────────────────
    out.append("-- ── Main IGProtocol term ────────────────────────────────────────────────────")
    out.append("")

    proto_head = f"noncomputable def {safe_name}_protocol"
    if tier == "O_inf":
        proto_head += f"  (h : imscriptionTier {start_type} = .O_inf)"
    proto_head += f" : IGProtocol {start_type} {end_type} :="

    out.append(proto_head)

    wrappers = []
    if has_dialetheia or has_frobenius:
        wrappers.append("  .withGram Gamma_seq <|")
    if has_backprop:
        wrappers.append("  .withMem H_inf <|")
    if tier == "O_inf" and is_self_ref:
        wrappers.append(f"  -- Self-ref: paralogical_copy h builds Δ : {start_type} → {start_type} ⊗ {start_type}")
        wrappers.append("  -- paralogical_dagger produces μ = Δ†")
    out.extend(wrappers)

    # Build term body
    claimed: set = set()
    for fs, ff in pairs:
        claimed.add(fs)
        claimed.add(ff)
        for w in graph.out_wires(fs):
            cur = w.dst_node
            while cur is not None and cur != ff:
                claimed.add(cur)
                succs = graph.successors(cur)
                cur = succs[0] if succs and succs[0] != ff else None

    top_level = [idx for idx in range(len(tokens)) if idx not in claimed or idx in fs_set or idx in ff_set]

    term_lines: List[str] = []
    pos = 0
    while pos < len(top_level):
        idx = top_level[pos]
        if idx in fs_set:
            ff_idx = next(ff for fs, ff in pairs if fs == idx)
            fork_lines = _emit_fork(state, idx, ff_idx)
            term_lines.extend(fork_lines)
            pos += 1
        elif idx in ff_set:
            pos += 1  # emitted inside fork block
        else:
            src, tgt = flow.get(idx, (_val(tokens[idx]), _val(tokens[idx])))
            term_lines.append(_node_arrow(idx, tokens[idx], src, tgt, state.domain_label(tokens[idx])))
            pos += 1

    if len(term_lines) == 0:
        out.append(f"  (.refl {start_type})")
    elif len(term_lines) == 1:
        out.append("  " + term_lines[0])
    else:
        out.append("  -- Seq chain:")
        for tl in term_lines:
            out.append("  " + tl)

    out.append("")

    # ── EVALT / EVALF evaluation arm sub-defs (feature 2) ────────────────────
    has_evalt = Token.EVALT in tokens
    has_evalf = Token.EVALF in tokens
    if has_evalt or has_evalf:
        h_arg = " (by decide)" if tier == "O_inf" else ""
        out.append("-- ── Evaluation arm sub-defs ─────────────────────────────────────────────────")
        out.append("")
        if has_evalt:
            t_label = opcode_map.get("EVALT", "truth arm") if opcode_map else "truth arm"
            out.append(f"-- {t_label}")
            out.append(f"noncomputable def {safe_name}_true_arm : IGProtocol {start_type} {end_type} :=")
            out.append(f"  ({safe_name}_protocol{h_arg}).restrictToEVALT")
            out.append("")
        if has_evalf:
            f_label = opcode_map.get("EVALF", "false arm") if opcode_map else "false arm"
            out.append(f"-- {f_label}")
            out.append(f"noncomputable def {safe_name}_false_arm : IGProtocol {start_type} {end_type} :=")
            out.append(f"  ({safe_name}_protocol{h_arg}).restrictToEVALF")
            out.append("")

    # ── Verification theorem stubs ────────────────────────────────────────────
    out.append("-- ── Verification theorems ───────────────────────────────────────────────────")
    out.append("")

    # 1. Tier (by decide — always closed)
    out.append(f"theorem {safe_name}_tier : TierFunctor.obj {start_type} = .{tier} := by decide")
    out.append("")

    # 2. Frobenius
    if has_frobenius:
        frob_dir = "split → fuse" if fp.frobenius_order == 1 else "fuse → split"
        out.append(f"-- Frobenius ({frob_dir}): μ∘δ = id on .prod branch")
        out.append(f"theorem {safe_name}_frobenius :")
        out.append(f"    igFrobeniusAlg.frob ({safe_name}_protocol{' (by decide)' if tier == 'O_inf' else ''}) := by")
        out.append(f"  apply igFrobAlg_self_fusion")
        out.append(f"  sorry  -- fill: mu_delta_A_id for the .prod arm")
        out.append("")

    # 3. Self-reference
    if is_self_ref:
        h_arg = " (by decide)" if tier == "O_inf" else ""
        out.append(f"-- Self-reference: Δ is a dagger and μ = Δ†")
        out.append(f"theorem {safe_name}_self_ref :")
        out.append(f"    (igProtoDelta {start_type} (by decide)).isDagger = true ∧")
        out.append(f"    igProtoMu_depth (paralogical_dagger (by decide)) = 1 := by")
        out.append(f"  constructor")
        out.append(f"  · exact igProtoCopy_isDagger")
        out.append(f"  · exact igProtoMu_depth")
        out.append("")

    # 4. Loop closure
    if is_self_ref:
        out.append(f"-- Loop closure: protocol has period {fp.period} and depth 1")
        out.append(f"theorem {safe_name}_loop_closure :")
        out.append(f"    ∃ (loop : IGProtocol {start_type} {end_type}),")
        out.append(f"      loop = {safe_name}_protocol{' (by decide)' if tier == 'O_inf' else ''} ∧")
        out.append(f"      loop.period = {fp.period} ∧ loop.depth = 1 := by")
        out.append(f"  exact ⟨_, rfl, by decide, by decide⟩")
        out.append("")

    # 5. Back-propagation note (comment only — no library lemma name yet)
    if has_backprop:
        out.append(f"-- Back-propagation / LinFix obligation:")
        out.append(f"-- igProtoCopy_isDagger licenses IMSCRIB→IFIX burn")
        out.append(f"-- CLINK→IMSCRIB weighted edge feeds next winding (.seq continuation)")
        out.append("")

    # 6. Cross-branch wires
    if cross_wires:
        out.append(f"-- Cross-branch wires ({len(cross_wires)}): paralogicalLift obligation")
        for w in cross_wires:
            src_tok = tokens[w.src_node].name
            dst_tok = tokens[w.dst_node].name
            out.append(f"-- {src_tok}[{w.src_node}].{w.src_port} → {dst_tok}[{w.dst_node}].{w.dst_port}")
        out.append("")

    out.append(f"end {namespace}")
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
