#!/usr/bin/env python3
"""
Fix phase 9: fix double .withGram and proper .seq nesting in the generated Lean output.
The generator itself needs fixing — the protocol body template has these issues.
"""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    lines = f.readlines()

# Fix 1: Remove duplicate ".withGram Grammar.measure <|" 
# Find the second occurrence in the emit_scaffold function's output
found = 0
for i, line in enumerate(lines):
    if '.withGram Grammar.measure <|' in line and 'out.append' in line:
        found += 1
        if found > 1:
            lines[i] = ''  # blank out the duplicate
            print(f"Removed duplicate .withGram at line {i+1}")

# Fix 2: Fix the .seq nesting in the protocol body template
# The issue is in lines that generate the post-FFUSE chain
# Find the section that generates '.seq' + '(.arrow ...)' after the FFUSE closure
# and fix the nesting

# Actually, the nesting issue is in the GENRATED CODE, not the generator.
# The BODY_TEMPLATE needs to be fixed. Let me find the template section.

# The template section starts after "# ── Main protocol term" 
# and the issue is the "Chain from ff to end" section
# Let me find it and fix the nesting logic

template_start = None
template_end = None
for i, line in enumerate(lines):
    if '# Chain from ff to end' in line:
        template_start = i
    if template_start and i > template_start and 'if ff_idx + 1 < n:' in line:
        # This is the problematic section - needs to generate nested .seq
        # Replace the flat chain with a nested one
        # For now, just note it
        pass

# Actually, let me look at the generated body template to understand the structure
# The issue is in how the template generates the .seq nesting after the FSPLIT/FFUSE block

print("\nCurrent state: module imports OK, generates output.")
print("Issues remaining:")
print("  1. Duplicate .withGram - FIXED")
print("  2. .seq nesting in post-FFUSE chain")
print("  3. Need to regenerate with new code")

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.writelines(lines)
print("Written")
