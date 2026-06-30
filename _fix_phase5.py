#!/usr/bin/env python3
"""Final fix: remove leftover orphan def domain_label line."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

# Find the orphan def domain_label
for i, line in enumerate(lines):
    if 'def domain_label(self, tok: Token, idx: int = -1) -> str:' in line:
        # Check if it's outside a class block (indentation 4 spaces but no class above)
        before = ''.join(lines[max(0,i-10):i])
        if 'class ScaffoldState' not in before:
            # This is the orphan — remove it and the following return lines
            end = i
            while end < len(lines) and (lines[end].strip() == '' or lines[end].startswith('    ') or 'return' in lines[end]):
                end += 1
            # But stop before the blank-line-separated block ends
            if 'return lines' in lines[end-1]:
                pass  # keep going
            print(f"Removing orphan lines {i}-{end}")
            for j in range(i, end):
                print(f"  [{j+1}] {lines[j].rstrip()}")
            del lines[i:end]
            break

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(lines)
print(f"Written ({len(lines)} lines)")
