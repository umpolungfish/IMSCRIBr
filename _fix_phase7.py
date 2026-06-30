#!/usr/bin/env python3
"""Fix the indentation error around use_withgram."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

# Find the block from the second 'if use_withgram:' through 'n = len(tokens)'
for i, line in enumerate(lines):
    if line.strip() == 'if use_withgram:' and i > 420:  # only in the body section
        # Check if the next line is blank or has wrong content
        next_lines = ''.join(lines[i:i+5])
        if 'out.append' not in next_lines:
            # This is the orphaned if — fix the entire block
            # Replace the doubled if block with a clean version
            lines[i-1] = '    use_withgram = bool(pairs) or has_dialetheia or has_frobenius\n'
            lines[i] = '    if use_withgram:\n'
            lines[i+1] = '        out.append("  .withGram Grammar.measure <|")\n'
            # Now remove the following blank line and the old second `if use_withgram:`
            for j in range(i+2, i+6):
                if j < len(lines):
                    stripped = lines[j].strip()
                    if stripped == 'if use_withgram:' or stripped == '':
                        lines[j] = ''  # blank the orphan
                    else:
                        break
            print(f"Fixed use_withgram block at line {i+1}")
            break

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(lines)
print("Written")
