#!/usr/bin/env python3
"""Fix missing closing paren on line 485 of proof_scaffold.py"""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

for i, line in enumerate(lines):
    if 'FFUSE closure, no post-chain' in line:
        print(f"Found at line {i+1}: {line.rstrip()}")
        # The line has: out.append(f"...") but closes f-string with " without )
        # Add ) at the end before the \n
        lines[i] = line.rstrip() + ")\n"
        print(f"Fixed to: {lines[i].rstrip()}")
        break

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(lines)
print("Fixed")
