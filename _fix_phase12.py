#!/usr/bin/env python3
"""Fix phase 12: direct section replacement for the post-FFUSE chain."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()

# The buggy section spans from "# Chain from ff to end (nested .seq)" 
# to "# end if ff_idx + 1 < n"
# Replace with a working implementation

old_section = '''        # Chain from ff to end
        # Chain from ff to end (nested .seq)
        if ff_idx + 1 < n:
            # Build right-nested .seq: (.seq arrow_i (.seq arrow_{i+1} ...))
            # Post-FFUSE arrows: indices ff_idx+1 ... n-1
            # We generate from inside out: the innermost is just an arrow,
            # and each outer level wraps with .seq
            post_indices = list(range(ff_idx + 1, n))
            for depth, i in enumerate(post_indices):
                s_src = _stages[i-1][0]
                s_tgt = _stages[i][0]
                lbl = _labels[i-1][0]
                indent = "    " + "  " * (len(post_indices) - 1 - depth)
                if depth < len(post_indices) - 1:
                    out.append(f"{indent}.seq")
                    inner_indent = "    " + "  " * (len(post_indices) - 2 - depth)
                    out.append(f"{inner_indent}(.arrow {lbl} {s_src} {s_tgt})")
                else:
                    out.append(f"{indent}(.arrow {lbl} {s_src} {s_tgt})")
        # end if ff_idx + 1 < n'''

new_section = '''        # Chain from ff to end (right-nested .seq)
        if ff_idx + 1 < n:
            # Collect arrows after FFUSE
            _post_arrows = []
            for _i in range(ff_idx + 1, n):
                _ss = _stages[_i-1][0]
                _st = _stages[_i][0]
                _lb = _labels[_i-1][0]
                _post_arrows.append(f"(.arrow {_lb} {_ss} {_st})")
            _K = len(_post_arrows)
            if _K == 1:
                out.append(f"    {_post_arrows[0]}")
            elif _K >= 2:
                # Build right-nested .seq from innermost pair outward
                # Innermost: depth K-2
                _inner = f".seq\\n      {_post_arrows[_K-2]}\\n      {_post_arrows[_K-1]}"
                for _d in range(_K-3, -1, -1):
                    _io = "    " + "  " * _d
                    _ii = "    " + "  " * (_d + 1)
                    _inner = f".seq\\n{_ii}{_post_arrows[_d]}\\n{_io}{_inner}"
                for _ln in _inner.split("\\n"):
                    out.append(f"    {_ln}")
        # end if ff_idx + 1 < n'''

if old_section in src:
    src = src.replace(old_section, new_section)
    with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
        f.write(src)
    print("Section replaced successfully")
else:
    print("WARNING: old section not found!")
    # Show what we have around that area
    idx = src.find('Chain from ff to end')
    if idx >= 0:
        print(src[idx:idx+800])
