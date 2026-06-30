#!/usr/bin/env python3
"""
Phase 2: fix proof_scaffold.py — replace bare glyph types with proper Imscription stage objects.
Strategy: 
  (a) Replace _node_arrow to use _lean_field_val
  (b) Replace _emit_fork to use stage object names
  (c) Replace protocol body with per-node stage definitions + Dual-Link chaining
"""
import re

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()
lines = src.split('\n')

# ---- Helper: find line ranges by content pattern ----
def find_range(start_pattern, end_pattern, start_from=0):
    """Return (start_line, end_line) for block between patterns."""
    s = None
    for i in range(start_from, len(lines)):
        if s is None and start_pattern in lines[i]:
            s = i
        if s is not None and end_pattern in lines[i] and i > s:
            return (s, i)
    return (None, None)

# ---- (1) Replace _node_arrow function ----
s, e = find_range('def _node_arrow(', 'def ', 0)
if s:
    print(f"_node_arrow at {s}-{e}")
    new_fn = [
        "def _node_arrow_lean(",
        "    safe_name: str, idx: int, tok: Token,",
        "    stage_src: str, stage_tgt: str,",
        "    domain_label: str = \"\"",
        ") -> str:",
        '    """Emit (.arrow stage_i stage_src stage_tgt) with proper Lean Imscription refs."""',
        "    field, val, desc = _TOKEN_IG[tok]",
        "    label_stage = f\"{safe_name}_l{idx}\"",
        "    MAX_LABEL = 80",
        "    if domain_label and len(domain_label) > MAX_LABEL:",
        "        domain_label = domain_label[:MAX_LABEL - 3] + \"...\"",
        '    suffix = f" ({domain_label})" if domain_label else ""',
        "    return (",
        '        f"(.arrow {label_stage} {stage_src} {stage_tgt})"',
        '        f"  -- [{idx}] {tok.name} | {field} := {val} | {desc}{suffix}"',
        "    )",
        "",
    ]
    lines[s:e] = new_fn
    print("  replaced _node_arrow → _node_arrow_lean")


# ---- (2) Replace _emit_fork function ----
s, e = find_range('def _emit_fork(', 'def emit_scaffold(', 0)
if s:
    print(f"_emit_fork at {s}-{e}")
    new_fork = [
        'def _emit_fork_lean(safe_name: str, state: ScaffoldState, fs: int, ff: int,',
        '                      fs_stage: str, ff_stage: str) -> List[str]:',
        '    """Emit .prod for a FSPLIT/FFUSE pair with stage Imscription refs."""',
        '    graph = state.graph',
        '    tok_fs = graph.tokens[fs]',
        '    tok_ff = graph.tokens[ff]',
        '    field_fs, val_fs, _ = _TOKEN_IG[tok_fs]',
        '    field_ff, val_ff, _ = _TOKEN_IG[tok_ff]',
        '',
        '    t_nodes = []; f_nodes = []',
        '    for w in graph.out_wires(fs):',
        "        cur = w.dst_node",
        "        while cur is not None and cur != ff:",
        "            (t_nodes if w.src_port == 'T' else f_nodes).append(cur)",
        "            nxt = graph.successors(cur)",
        "            cur = nxt[0] if nxt and nxt[0] != ff else None",
        '',
        '    ff_label = f"{safe_name}_l{ff}"',
        '    lines = []',
        '    dl_fs = state.domain_label(tok_fs, fs)',
        '    dl_fs_s = f" ({dl_fs})" if dl_fs else ""',
        '    lines.append(f"-- FSPLIT [{fs}] ({field_fs} := {val_fs}){dl_fs_s} / FFUSE [{ff}] ({field_ff} := {val_ff})")',
        '    lines.append(".seq")',
        '    lines.append("  (.prod")',
        '',
        '    # T-branch',
        '    lines.append(f"    -- T-branch ({len(t_nodes)} nodes)")',
        '    if t_nodes:',
        '        for ni in t_nodes:',
        '            nt = graph.tokens[ni]',
        '            nsrc = f"{safe_name}_s{ni}"',
        '            ntgt = f"{safe_name}_s{ni+1}" if ni+1 < ff else ff_stage',
        '            lines.append("    " + _node_arrow_lean(safe_name, ni, nt, nsrc, ntgt, state.domain_label(nt,ni)))',
        '    else:',
        '        lines.append(f"    (.refl {ff_stage})  -- T-branch empty")',
        '',
        '    # F-branch',
        '    lines.append(f"    -- F-branch ({len(f_nodes)} nodes)")',
        '    if f_nodes:',
        '        for ni in f_nodes:',
        '            nt = graph.tokens[ni]',
        '            nsrc = f"{safe_name}_s{ni}"',
        '            ntgt = f"{safe_name}_s{ni+1}" if ni+1 < ff else ff_stage',
        '            lines.append("    " + _node_arrow_lean(safe_name, ni, nt, nsrc, ntgt, state.domain_label(nt,ni)))',
        '        lines[-1] = lines[-1] + ")"',
        '    else:',
        '        lines.append(f"    (.refl {ff_stage}))  -- F-branch empty")',
        '',
        '    lines.append(f"  -- reconnect at FFUSE [{ff}]: μ closes the Frobenius pair")',
        '    dl_ff = state.domain_label(tok_ff, ff)',
        '    dl_ff_s = f" ({dl_ff})" if dl_ff else ""',
        '    lines.append(f"  (.arrow {ff_label} {ff_stage} {ff_stage})  -- [{ff}] FFUSE | {field_ff} := {val_ff}{dl_ff_s}")',
        '    return lines',
        '',
    ]
    lines[s:e] = new_fork
    print("  replaced _emit_fork → _emit_fork_lean")
else:
    print("  WARNING: _emit_fork not found")


# ---- (3) Replace emit_scaffold protocol body (stage objects → end of fn) ----
_IM_FIELDS = ["dim","top","rel","pol","fid","kin","gran","gram","crit","chir","stoi","prot"]
_IM_BASE_VALS = ["dead","judge","ado","church","age","yea","bib","vow","woe","fee","hung","awe"]

# Build the replacement text for the protocol body section
# We generate Python source that will be *inserted into* emit_scaffold
BODY_TEMPLATE = '''    # ── Stage objects (Imscriptions) ──────────────────────────────────────────
    # Each node generates a cumulative stage Imscription + a label Imscription.
    # Stages: cumulative through tokens[0..i]; Labels: single-field delta at node i.
    _fields = {FIELDS}
    _base_vals = {BASE_VALS}
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
    if use_withgram:
        out.append("  .withGram Grammar.measure <|")
    
    # Build term body
    n = n_tokens
    if n == 1:
        out.append(f"  (.arrow {_labels[0][0]} {o_start} {o_end})")
    elif pairs:
        # Dual-Link pattern: chain up to first FSPLIT, .prod through FFUSE, chain after
        fs_idx = min(p[0] for p in pairs)
        ff_idx = min(p[1] for p in pairs)
        fs_stage = _stages[fs_idx][0]
        ff_stage = _stages[ff_idx][0]
        ff_label = _labels[ff_idx][0]
        
        # Chain from start to fs
        out.append(f"  .seq")
        for i in range(1, fs_idx + 1):
            indent = "  " * (1 if i == 1 else 2)
            s_src = _stages[i-1][0]
            s_tgt = _stages[i][0]
            lbl = _labels[i-1][0]
            out.append(f"{indent}(.arrow {lbl} {s_src} {s_tgt})")
        
        # FSPLIT/FFUSE block
        out.append("    (.seq")
        out.append("      (.prod")
        out.append(f"        (.arrow {fs_stage} {fs_stage} {ff_stage})  -- T-arm (δ)")
        out.append(f"        (.arrow {fs_stage} {fs_stage} {ff_stage})) -- F-arm (μ, Dual-Link mirror)")
        out.append(f"      (.arrow {ff_label} {ff_stage} {ff_stage})  -- FFUSE closure")
        
        # Chain from ff to end
        if ff_idx + 1 < n:
            cur_indent = "    "
            for i in range(ff_idx + 1, n):
                s_src = _stages[i-1][0]
                s_tgt = _stages[i][0]
                lbl = _labels[i-1][0]
                out.append(f"{cur_indent}.seq")
                out.append(f"{cur_indent}  (.arrow {lbl} {s_src} {s_tgt})")
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
    # Frobenius
    if has_frobenius:
        frob_dir = "split → fuse" if fp.frobenius_order == 1 else "fuse → split"
        out.append(f"-- Frobenius ({frob_dir}): μ∘δ = id on .prod branch")
        out.append(f"-- Proof: apply igFrobAlg_self_fusion; exact mu_delta_A_id")
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
'''

# Inject the _fields and _base_vals arrays
BODY_TEMPLATE = BODY_TEMPLATE.replace("{FIELDS}", str(_IM_FIELDS))
BODY_TEMPLATE = BODY_TEMPLATE.replace("{BASE_VALS}", str(_IM_BASE_VALS))

# Find the section to replace in the file
stage_start = None
for i, line in enumerate(lines):
    if '─ Stage objects (Imscriptions) ─' in line:
        stage_start = i
        break

# Find the return statement
return_end = None
for i, line in enumerate(lines):
    if line.strip() == 'return "\\n".join(out)':
        return_end = i
        break

if stage_start and return_end:
    # We need to insert the BODY_TEMPLATE as lines
    body_lines = BODY_TEMPLATE.split('\n')
    lines[stage_start:return_end] = body_lines
    print(f"Replaced body at lines {stage_start}-{return_end-1} ({len(body_lines)} lines inserted)")
else:
    print(f"WARNING: body not found. start={stage_start} end={return_end}")


# ---- Write result ----
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write('\n'.join(lines))
print("Written proof_scaffold.py")
