#!/usr/bin/env python3
"""Fix the .seq nesting and duplicate .withGram in proof_scaffold.py template."""
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()
lines = src.split('\n')

# Working area: lines 431-500

# Fix 1: Remove duplicate out.append for .withGram (around line 434)
for i in range(430, 440):
    if i < len(lines) and '.withGram Grammar.measure' in lines[i]:
        # Check if the next line is ALSO a .withGram
        if i+1 < len(lines) and '.withGram Grammar.measure' in lines[i+1]:
            lines[i+1] = ''  # blank the duplicate
            print(f"Fix 1: Blanked duplicate .withGram at line {i+2}")

# Fix 2: Fix the post-FFUSE chain nesting (lines ~470-472)
# Replace the flat `.seq / (.arrow ...)` pattern with proper nested `.seq`
# Current (lines ~468-472):
#   out.append(f"{cur_indent}.seq")
#   out.append(f"{cur_indent}  (.arrow {lbl} {s_src} {s_tgt})")
# 
# Should be:
#   out.append(f"{cur_indent}.seq")
#   # accumulate arrows with proper nesting depth
#   nesting_depth = ...
#   out.append(f"{'  ' * nesting_depth}(.arrow {lbl} {s_src} {s_tgt})")

# Find the post-FFUSE chain section
chain_section_start = None
chain_section_end = None
for i, line in enumerate(lines):
    if 'if ff_idx + 1 < n:' in line:
        chain_section_start = i
    if chain_section_start and i > chain_section_start and 'else:' in line and i > chain_section_start + 5:
        chain_section_end = i
        break

if chain_section_start and chain_section_end:
    # Log what we found
    print(f"Chain section: lines {chain_section_start+1}-{chain_section_end}")
    for j in range(chain_section_start, min(chain_section_end, chain_section_start + 20)):
        print(f"  [{j+1}] {lines[j].rstrip()}")
    
    # Replace with nested .seq logic
    # The post-FFUSE chain needs to build a right-nested .seq tree
    new_chain = [
        '        # Chain from ff to end (nested .seq)',
        '        if ff_idx + 1 < n:',
        '            # Build right-nested .seq: (.seq arrow_i (.seq arrow_{i+1} ...))',
        '            # Post-FFUSE arrows: indices ff_idx+1 ... n-1',
        '            # We generate from inside out: the innermost is just an arrow,',
        '            # and each outer level wraps with .seq',
        '            post_indices = list(range(ff_idx + 1, n))',
        '            for depth, i in enumerate(post_indices):',
        '                s_src = _stages[i-1][0]',
        '                s_tgt = _stages[i][0]',
        '                lbl = _labels[i-1][0]',
        '                indent = "    " + "  " * (len(post_indices) - 1 - depth)',
        '                if depth < len(post_indices) - 1:',
        '                    out.append(f"{indent}.seq")',
        '                    inner_indent = "    " + "  " * (len(post_indices) - 2 - depth)',
        '                    out.append(f"{inner_indent}(.arrow {lbl} {s_src} {s_tgt})")',
        '                else:',
        '                    out.append(f"{indent}(.arrow {lbl} {s_src} {s_tgt})")',
        '        # end if ff_idx + 1 < n',
    ]
    lines[chain_section_start:chain_section_end] = new_chain
    print(f"Replaced chain section")

# Fix 3: Fix the FSPLIT/F-branch naming — fs_stage used as label but should be label name
# Actually this is in the output. The line:
#   (.arrow {fs_stage} {fs_stage} {ff_stage})
# should be:
#   (.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})
# Wait, looking at the template code: the fs_stage is the stage name, not the label name.
# The label should be the FSPLIT token's label.

# Let me find where the FSPLIT/FFUSE block generates the .prod arrows
for i, line in enumerate(lines):
    if '(.arrow {fs_stage} {fs_stage} {ff_stage})' in line:
        # This uses stage name as label — should use label name instead
        old_line = line
        # The label should be the label at fs_idx
        new_line = old_line.replace(
            '(.arrow {fs_stage} {fs_stage} {ff_stage})',
            '(.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage})'
        ).replace(
            '(.arrow {fs_stage} {fs_stage} {ff_stage}))',
            '(.arrow {_labels[fs_idx][0]} {fs_stage} {ff_stage}))'
        )
        lines[i] = new_line
        print(f"Fix 3: Fixed FSPLIT arrow label at line {i+1}")

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write('\n'.join(lines))
print("Written")
