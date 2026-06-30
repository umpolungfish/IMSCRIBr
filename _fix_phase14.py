#!/usr/bin/env python3
"""Fix phase 14: restructure FSPLIT/FFUSE + post-chain as a single continuation."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()

# The section to fix: from "# FSPLIT/FFUSE block" through "# end if ff_idx + 1 < n"
old = '''        # FSPLIT/FFUSE block
        out.append("    (.seq")
        out.append("      (.prod")
        out.append(f"        (.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})  -- T-arm (δ)")
        out.append(f"        (.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})) -- F-arm (μ, Dual-Link mirror)")
        out.append(f"      (.arrow {ff_label} {ff_stage} {ff_stage})  -- FFUSE closure")
        
        # Chain from ff to end (recursive right-nested .seq)
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
            for _ln in _chain_str.split("\\n"):
                out.append("    " + _ln)
        # end if ff_idx + 1 < n'''

new = '''        # FSPLIT/FFUSE block + post-chain (single continuation)
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
            out.append(f"      (.arrow {ff_label} {ff_stage} {ff_stage}))  -- FFUSE closure (no post-chain)" '''

if old in src:
    src = src.replace(old, new)
    with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
        f.write(src)
    print("Section replaced successfully")
else:
    print("WARNING: old section not found!")
    idx = src.find('FSPLIT/FFUSE block')
    if idx >= 0:
        print(src[idx:idx+600])
