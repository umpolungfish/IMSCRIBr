#!/usr/bin/env python3
"""Clean replacement of the mangled use_withgram block."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

# Find the mangled block: around line 430-436
for i in range(425, 445):
    if i < len(lines):
        print(f"  [{i+1}] {lines[i].rstrip()}")

# Replace lines 431-434 (0-indexed: 430-433) with clean version
replacement = [
    '    use_withgram = bool(pairs) or has_dialetheia or has_frobenius\n',
    '    if use_withgram:\n',
    '        out.append("  .withGram Grammar.measure <|")\n',
]
lines[430:434] = replacement
print(f"\nReplaced lines 431-434")

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(lines)
print("Written")
