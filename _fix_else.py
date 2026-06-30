#!/usr/bin/env python3
"""Fix the syntax error on line 485 — stray unclosed paren in comment."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

# Find and fix line 485 (0-indexed: 484)
for i, line in enumerate(lines):
    if 'FFUSE closure (no post-chain)' in line:
        print(f"Fixing line {i+1}: {line.rstrip()}")
        # Replace with clean version — avoid unclosed paren in comment
        lines[i] = line.replace(
            'FFUSE closure (no post-chain)" ',
            'FFUSE closure, no post-chain)"\n'
        ).replace(
            'FFUSE closure (no post-chain)"',
            'FFUSE closure, no post-chain)"\n'
        )
        break

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(lines)

print("Fixed else branch line")
