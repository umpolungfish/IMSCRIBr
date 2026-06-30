#!/usr/bin/env python3
"""
Fix phase 4: remove orphaned domain_label + old _emit_chain, then test the module.
"""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

# Remove lines 193-218 (orphaned domain_label + old _emit_chain)
# These are: the orphan def + the old _emit_chain that uses _node_arrow
# Index from 0: 193-218 means indices 192-217
old_start = 192  # 'def domain_label(self' line
old_end = 218    # first of the three blank lines after old _emit_chain

# Verify we're removing the right lines
print(f"Removing lines {old_start+1}-{old_end}:")
for i in range(old_start, old_end):
    print(f"  [{i+1}] {lines[i].rstrip()}")

new_lines = lines[:old_start] + lines[old_end:]
print(f"\nNew file length: {len(new_lines)} lines (was {len(lines)})")

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(new_lines)

print("Written")
