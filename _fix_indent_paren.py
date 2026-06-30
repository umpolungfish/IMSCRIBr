#!/usr/bin/env python3
"""Fix indentation and paren balancing in the FSPLIT/FFUSE section."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()

# Fix 1: Change first arrow indent from 2 to 4 spaces
old_chain = '''        # Chain from start to fs
        out.append(f"  .seq")
        for i in range(1, fs_idx + 1):
            indent = "  " * (1 if i == 1 else 2)
            s_src = _stages[i-1][0]
            s_tgt = _stages[i][0]
            lbl = _labels[i-1][0]
            out.append(f"{indent}(.arrow {lbl} {s_src} {s_tgt})")'''

new_chain = '''        # Chain from start to fs (arg1 of outer .seq)
        out.append(f"  .seq")
        for i in range(1, fs_idx + 1):
            indent = "    "  # 4-space, same as arg2 indent
            s_src = _stages[i-1][0]
            s_tgt = _stages[i][0]
            lbl = _labels[i-1][0]
            out.append(f"{indent}(.arrow {lbl} {s_src} {s_tgt})")'''

if old_chain in src:
    src = src.replace(old_chain, new_chain)
    print("Fix 1: Chain indent updated")
else:
    print("WARNING: Fix 1 chain section not found!")
    # Debug: show what's around there
    idx = src.find('Chain from start to fs')
    if idx >= 0:
        print(src[idx:idx+400])

# Fix 2: Replace the entire FSPLIT/FFUSE block + post-chain with corrected version
old_fsplit = '''        # FSPLIT/FFUSE block + post-chain (single continuation)
        out.append("    (.seq")
        out.append("      (.prod")
        out.append(f"        (.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})  -- T-arm (δ)")
        out.append(f"        (.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})) -- F-arm (μ, Dual-Link mirror)")
        # Post-FFUSE: FFUSE closure (arg1) + continuation chain (arg2)
        if ff_idx + 1 < n:
            # Collect arrows after FFUSE
            _post_arrows = []
            for _i in range(ff_idx + 1, n):
                _ss = _stages[_i-1][0]
                _st = _stages[_i][0]
                _lb = _labels[_i-1][0]
                _post_arrows.append(f"(.arrow {_lb} {_ss} {_st})")
            def _seq_chain(arrs, depth=0):
                if len(arrs) == 1:
                    return "  " * depth + arrs[0]
                return ("  " * depth + ".seq\\n" +
                        "  " * (depth + 1) + arrs[0] + "\\n" +
                        _seq_chain(arrs[1:], depth + 1))
            _chain_str = _seq_chain(_post_arrows, 0)
            # FFUSE closure as arg1 of a continuation .seq, then post-chain as arg2
            out.append(f"      (.seq")
            out.append(f"        (.arrow {ff_label} {ff_stage} {ff_stage})  -- FFUSE closure")
            for _ln in _chain_str.split("\\n"):
                out.append("        " + _ln)
            out.append("      )   -- close continuation .seq")
        else:
            # No post-chain — just FFUSE closure as arg2
            out.append(f"      (.arrow {ff_label} {ff_stage} {ff_stage}))  -- FFUSE closure, no post-chain)")'''

new_fsplit = '''        # FSPLIT/FFUSE block + post-chain (single continuation)
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
                if len(arrs) == 1:
                    return "  " * depth + arrs[0]
                return ("  " * depth + ".seq\\n" +
                        "  " * (depth + 1) + arrs[0] + "\\n" +
                        _seq_chain(arrs[1:], depth + 1))
            _chain_str = _seq_chain(_post_arrows, 0)
            # Continuation .seq: FFUSE closure (arg1) + post-chain (arg2)
            out.append("      (.seq")
            out.append(f"        (.arrow {ff_label} {ff_stage} {ff_stage})  -- FFUSE closure")
            for _ln in _chain_str.split("\\n"):
                out.append("        " + _ln)
            out.append("      )   -- close continuation .seq")
            # Close inner .seq (the one opened at line "    (.seq")
            out.append("    )   -- close inner .seq")
        else:
            # No post-chain — FFUSE closure IS arg2 of inner .seq
            # Need: (.arrow ff ff ff)) — ) closes arrow, ) closes inner .seq
            out.append(f"      (.arrow {ff_label} {ff_stage} {ff_stage}))  -- FFUSE closure, closes inner .seq")'''

if old_fsplit in src:
    src = src.replace(old_fsplit, new_fsplit)
    print("Fix 2: FSPLIT/FFUSE block updated")
else:
    print("WARNING: Fix 2 FSPLIT/FFUSE block not found!")
    # Find what's actually there
    idx = src.find('FSPLIT/FFUSE block')
    if idx >= 0:
        print("Found at", idx)
        print(src[idx:idx+800])

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write(src)

print("Written")
