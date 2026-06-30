#!/usr/bin/env python3
"""Fix phase 13: correct right-nested .seq chain with recursive builder."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()

old_section = '''        # Chain from ff to end (right-nested .seq)
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

new_section = '''        # Chain from ff to end (recursive right-nested .seq)
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

if old_section in src:
    src = src.replace(old_section, new_section)
    with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
        f.write(src)
    print("Section replaced successfully")
else:
    print("WARNING: old section not found! Printing snippet...")
    idx = src.find('Chain from ff to end')
    if idx >= 0:
        print(src[idx:idx+500])
