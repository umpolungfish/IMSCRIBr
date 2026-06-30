#!/usr/bin/env python3
"""Fix remaining issues in emit_scaffold body."""
import re

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()
lines = src.split('\n')

# Fix 1: n = n_tokens → n = len(tokens)
for i, line in enumerate(lines):
    if line.strip() == 'n = n_tokens':
        lines[i] = line.replace('n = n_tokens', 'n = len(tokens)')
        print(f"  Fixed n_tokens at line {i+1}")

# Fix 2: Remove duplicated 'if use_withgram: out.append("  .withGram Grammar.measure <|")'
dup_count = 0
for i, line in enumerate(lines):
    if 'out.append("  .withGram Grammar.measure <|")' in line:
        dup_count += 1
        if dup_count > 1:
            lines[i] = ''
            print(f"  Removed duplicate withGram at line {i+1}")

# Fix 3: Check for the "out.append(f"  .withGram..." having wrong first indent
# The main function code has - the first `if use_withgram:` is fine, it's the 
# second one that's duplicated. Actually looking at it: there are TWO consecutive
# if use_withgram blocks. The first is right, the second is the duplicate.

# Let me also fix the generated code - the body template has some formatting issues
# Check for 'n = len(tokens)' 
for i, line in enumerate(lines):
    if 'n = len(tokens)' in line:
        # Make sure this appears after the proto_head and before the if/elif
        print(f"  n = len(tokens) at line {i+1}")
        break

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write('\n'.join(lines))
print("Written")
