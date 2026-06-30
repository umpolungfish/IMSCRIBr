#!/usr/bin/env python3
"""Rewrite emit_scaffold to use IGScaffold API (scaf, ▷, mkFSplit).
Replaces the per-node stage/label Imscription approach with uniform scaf."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()

# Find the emit_scaffold function body start
idx = src.find("def emit_scaffold(")
if idx < 0:
    print("ERROR: emit_scaffold not found!")
    exit(1)

# Find the triple-quoted docstring
doc_start = src.find('"""', idx)
doc_end = src.find('"""', doc_start + 3) + 3

# Find what comes after the docstring
after_doc = src[doc_end:]

# Parse the function signature
sig_end = after_doc.find(":")
sig_line = after_doc[:sig_end]
print(f"Signature: {sig_line.strip()}")

# The function body starts after the first ":"
# Find the indented body
lines = after_doc.split("\n")
body_start_line = 0
for i, line in enumerate(lines):
    stripped = line.strip()
    if stripped and not stripped.startswith("#") and not stripped.startswith('"""'):
        # Check if this is the beginning of the body
        if i > 0 and lines[i-1].strip().endswith(":"):
            body_start_line = i
            break

print(f"Body starts at line offset {body_start_line}")

# Read old body up to "return" statement
old_body_end_idx = after_doc.find("    return out")
if old_body_end_idx < 0:
    old_body_end_idx = after_doc.find("\nout.append(")
    # Find the return
    ret_idx = after_doc.find("return out", old_body_end_idx)
    if ret_idx >= 0:
        old_body_end_idx = ret_idx + len("return out")

new_body = '''    n = len(tokens)
    safe_name = _safe(name if name else arrangement_str(arr))
    tier = _tier_str(fp)
    
    out = []
    out.append(f"-- IGProtocol scaffold: {arrangement_str(arr)}")
    out.append(f"-- Class: {safe_name}")
    out.append(f"-- Fingerprint: sig={fp.sig}")
    out.append(f"--   self_ref={fp.self_ref} | frobenius_order={fp.frobenius_order}")
    out.append(f"--   dialetheia_complete={fp.dialetheia_complete} | period={fp.period}")
    out.append(f"-- Expected tier: {tier}")
    if pairs:
        out.append(f"-- FSPLIT/FFUSE pairs: {[(p[0], p[1]) for p in pairs]}")
    out.append("")
    out.append("import Imscribing.IGScaffold")
    out.append("")
    out.append(f"namespace {namespace}")
    out.append("open Primitives Frobenius IGProtocol")
    out.append("open Dimensionality Topology Relational Polarity Grammar")
    out.append("     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality")
    out.append("")
    out.append("-- ── Token → IG field mapping ──────────────────────────────────────────────")
    for i, tok in enumerate(tokens):
        f_, v_, d_ = _TOKEN_IG[tok]
        cons = _IG_VAL_TO_LEAN_CONS.get(v_, v_)
        out.append(f"--   [{i}] {tok.name:8s}  {f_:6s} := {v_:14s}  | {d_}")
    out.append("")
    
    # ── Main protocol term ────────────────────────────────────────────────────
    has_evalt = Token.EVALT in tokens
    has_evalf = Token.EVALF in tokens
    
    out.append("-- ── Main IGProtocol term ────────────────────────────────────")
    out.append(f"noncomputable def {safe_name}_protocol : IGProtocol scaf scaf :=")
    out.append("  .withGram .measure <|")
    
    if n == 1:
        out.append("  .arrow scaf scaf scaf")
    elif pairs:
        # Dual-Link: chain up to first FSPLIT, then mkFSplit, then chain after
        fs_idx = min(p[0] for p in pairs)
        ff_idx = min(p[1] for p in pairs)
        
        # Arrows before FSPLIT
        pre_arrows = list(range(0, fs_idx))
        # Post-chain (after FFUSE)
        post_arrows = list(range(ff_idx + 1, n))
        
        if not pre_arrows:
            out.append("  mkFSplit")
        else:
            out.append("  " + " ▷\\n    ".join(
                [".arrow scaf scaf scaf"] * len(pre_arrows)
            ))
            out.append("    ▷ mkFSplit")
        
        # T and F arms
        out.append("    (.arrow scaf scaf scaf)  -- T-arm (δ)")
        out.append("    (.arrow scaf scaf scaf)  -- F-arm (μ, Dual-Link mirror)")
        
        # FFUSE closure + post-chain (3rd arg to mkFSplit)
        if post_arrows:
            num_chain = len(post_arrows) + 1  # +1 for FFUSE closure
            chain_parts = ["(.arrow scaf scaf scaf)"] * num_chain
            out.append("    (" + " ▷\\n      ".join(chain_parts) + ")")
        else:
            out.append("    (.arrow scaf scaf scaf)  -- FFUSE closure")
    else:
        # Simple linear chain
        out.append("  " + " ▷\\n    ".join(
            [".arrow scaf scaf scaf"] * n
        ))
    
    out.append("")
    
    # ── EVALT / EVALF evaluation arm sub-defs ────────────────────────────────
    if has_evalt or has_evalf:
        out.append("-- ── Evaluation arm sub-defs ───────────────────────────────────")
        if has_evalt:
            out.append("")
            out.append(f"-- truth arm")
            out.append(f"noncomputable def {safe_name}_true_arm : IGProtocol scaf scaf :=")
            out.append(f"  ({safe_name}_protocol).restrictToEVALT")
        if has_evalf:
            out.append("")
            out.append(f"-- false arm")
            out.append(f"noncomputable def {safe_name}_false_arm : IGProtocol scaf scaf :=")
            out.append(f"  ({safe_name}_protocol).restrictToEVALF")
        out.append("")
    
    # ── Verification theorems ─────────────────────────────────────────────────
    out.append("-- ── Verification theorems ─────────────────────────────────────")
    out.append("")
    out.append(f"theorem {safe_name}_tier : TierFunctor.obj scaf = .{tier} := by decide")
    out.append("")
    if pairs:
        out.append("-- Frobenius (split → fuse): μ∘δ = id on .prod branch")
        out.append("-- Proof: apply igFrobAlg_self_fusion; exact mu_delta_A_id")
        out.append("")
    
    out.append(f"end {namespace}")
    return out'''

# Replace the body of emit_scaffold
# Find where to cut and paste
# Strategy: replace everything from the beginning of the body to "return out"
old_body_start = src.find("    n = len(tokens)", doc_end)
if old_body_start < 0:
    print("ERROR: Could not find body start marker 'n = len(tokens)'")
    # Debug: show what comes after doc
    print(f"After doc ({doc_end}): {src[doc_end:doc_end+200]}")
    exit(1)

ret_idx = src.find("\n    return out", old_body_start)
if ret_idx < 0:
    print("ERROR: Could not find 'return out'")
    exit(1)
old_body_end = ret_idx + len("\n    return out")

old_body = src[old_body_start:old_body_end]
print(f"Old body: {len(old_body)} chars")
print(f"New body: {len(new_body)} chars")

src = src.replace(old_body, new_body, 1)

# Also fix the imports at the top if needed
# Remove import of IGMorphism/IGFunctor from the header
# (They'll be imported indirectly via IGScaffold)

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write(src)
print("Done")
