#!/usr/bin/env python3
"""Fix the post-FFUSE chain nesting with correct right-nested .seq tree."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

# Find the post-FFUSE chain section and replace it
start_search = 450
for i in range(start_search, len(lines)):
    if 'if ff_idx + 1 < n:' in lines[i] and 'post_indices' in lines[i]:
        # This is the buggy section - replace from here until '# end if'
        end = i
        while end < len(lines) and not lines[end].strip().startswith('# end if'):
            end += 1
        end += 1  # include the # end if line
        
        print(f"Replacing chain section lines {i+1}-{end}")
        
        # New clean chain generator using right-nested .seq
        new_chain = [
            '        # Chain from ff to end (right-nested .seq tree)\n',
            '        if ff_idx + 1 < n:\n',
            '            # Collect post-FFUSE arrows\n',
            '            _post_arrows = []\n',
            '            for _i in range(ff_idx + 1, n):\n',
            '                _ss = _stages[_i-1][0]\n',
            '                _st = _stages[_i][0]\n',
            '                _lb = _labels[_i-1][0]\n',
            '                _post_arrows.append(f"(.arrow {_lb} {_ss} {_st})")\n',
            '            # Build right-nested .seq from inside out\n',
            '            # Base indent: same as post-FFUSE block (4 spaces)\n',
            '            # Each nesting level adds 2 spaces\n',
            '            _K = len(_post_arrows)\n',
            '            if _K == 1:\n',
            '                out.append(f"    {_post_arrows[0]}")\n',
            '            elif _K >= 2:\n',
            '                # Build from the innermost pair outward\n',
            '                # innermost: .seq arrow_{K-2} arrow_{K-1}\n',
            '                _inner = f".seq\\n      {_post_arrows[_K-2]}\\n      {_post_arrows[_K-1]}"\n',
            '                for _d in range(_K-3, -1, -1):\n',
            '                    _indent_outer = "    " + "  " * (_d)\n',
            '                    _indent_inner = "    " + "  " * (_d + 1)\n',
            '                    _inner = f".seq\\n{_indent_inner}{_post_arrows[_d]}\\n{_indent_outer}{_inner}"\n',
            '                # Output the built tree\n',
            '                # Split _inner into lines and append with proper base indent\n',
            '                _result_indent = "    "\n',
            '                for _ln in _inner.split("\\n"):\n',
            '                    out.append(f"{_result_indent}{_ln}")\n',
            '        # end if ff_idx + 1 < n\n',
        ]
        lines[i:end] = new_chain
        print("Written new chain section")
        break

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(lines)
print("Written proof_scaffold.py")
