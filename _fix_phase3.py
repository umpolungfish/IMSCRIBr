#!/usr/bin/env python3
"""
Fix the broken ScaffoldState, _val, _emit_chain removal from phase 2.
"""
import re

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()
lines = src.split('\n')

# Find and fix the orphaned domain_label method (line ~198-202)
# It was the body of ScaffoldState.domain_label but now floats without a class
for i, line in enumerate(lines):
    if 'def domain_label(self' in line and not line.startswith('    def'):
        # Replace from this line to the next blank-line-terminated block
        lines[i] = ''  # blank the orphan
        print(f"Blanked orphan domain_label at line {i}")

# Now reinsert the missing _val, ScaffoldState, _emit_chain before _emit_fork_lean
# Find the position of _emit_fork_lean
fork_start = None
for i, line in enumerate(lines):
    if line.strip().startswith('def _emit_fork_lean'):
        fork_start = i
        break

if fork_start:
    insert = [
        '',
        '',
        '# ── Helpers ─────────────────────────────────────────────────────────────',
        '',
        'def _val(tok: Token) -> str:',
        '    return _TOKEN_IG[tok][1]',
        '',
        '',
        '@dataclass',
        'class ScaffoldState:',
        '    graph: WiredGraph',
        '    flow: Dict[int, Tuple[str, str]]',
        '    opcode_map: Dict[str, str] = field(default_factory=dict)',
        '    position_labels: Dict[int, str] = field(default_factory=dict)',
        '    visited: set = field(default_factory=set)',
        '',
        '    def domain_label(self, tok: Token, idx: int = -1) -> str:',
        '        if idx >= 0 and idx in self.position_labels:',
        '            return self.position_labels[idx]',
        '        return self.opcode_map.get(tok.name, "")',
        '',
        '',
        'def _emit_chain(state: ScaffoldState, nodes: List[int]) -> List[str]:',
        '    """Emit a linear chain of nodes as nested .seq terms (bare glyphs — kept for compat)."""',
        '    if not nodes:',
        '        return []',
        '    if len(nodes) == 1:',
        '        idx = nodes[0]',
        '        tok = state.graph.tokens[idx]',
        '        src, tgt = state.flow.get(idx, (_val(tok), _val(tok)))',
        "        return [_node_arrow_lean('', idx, tok, src, tgt, state.domain_label(tok, idx))]",
        '    lines = []',
        '    for i, idx in enumerate(nodes):',
        '        tok = state.graph.tokens[idx]',
        '        src, tgt = state.flow.get(idx, (_val(tok), _val(tok)))',
        "        arrow = _node_arrow_lean('', idx, tok, src, tgt, state.domain_label(tok, idx))",
        '        if i < len(nodes) - 1:',
        '            lines.append(".seq")',
        '            lines.append("  " + arrow)',
        '        else:',
        '            lines.append("  " + arrow)',
        '    return lines',
        '',
    ]
    lines[fork_start:fork_start] = insert
    print(f"Inserted _val, ScaffoldState, _emit_chain at line {fork_start}")
else:
    print("WARNING: could not find _emit_fork_lean")

# Write back
with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write('\n'.join(lines))
print("Written proof_scaffold.py")
