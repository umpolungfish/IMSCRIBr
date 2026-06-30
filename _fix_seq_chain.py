#!/usr/bin/env python3
"""Rewrite _seq_chain to produce properly parenthesized .seq terms."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()

old = '''        def _seq_chain(arrs, depth=0):
                if len(arrs) == 1:
                    return "  " * depth + arrs[0]
                return ("  " * depth + ".seq\\n" +
                        "  " * (depth + 1) + arrs[0] + "\\n" +
                        _seq_chain(arrs[1:], depth + 1))'''

new = '''        def _seq_chain(arrs, depth=0):
                """Recursive right-nested .seq chain, each subterm paren-wrapped."""
                if len(arrs) == 1:
                    return "  " * depth + arrs[0]
                head = arrs[0]
                tail = arrs[1:]
                rest = _seq_chain(tail, depth + 1)
                return ("  " * depth + "(.seq\\n" +
                        "  " * (depth + 1) + head + "\\n" +
                        rest + "\\n" +
                        "  " * depth + ")")'''

if old in src:
    src = src.replace(old, new)
    print("_seq_chain rewritten")
else:
    print("WARNING: old _seq_chain not found!")
    idx = src.find('def _seq_chain')
    if idx >= 0:
        print(src[idx:idx+300])

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write(src)
print("Done")
