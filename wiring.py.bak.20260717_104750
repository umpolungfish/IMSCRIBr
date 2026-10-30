"""
IMASM Wire Graph — explicit port-level graph model for token arrangements.

Models each token as a node with typed input/output ports. Enables
cross-branch topology: a FSPLIT's F-output can route to any compatible
input port, not only its stack-matched FFUSE.

Port conventions (following IMSCRIBr TOKEN_ARITY — every token is 1→1
except VINIT source, FSPLIT fork, FFUSE join):

  VINIT:  in=[]         out=['o']         0→1 source
  FSPLIT: in=['i']      out=['T','F']     1→2 fork
  FFUSE:  in=['T','F']  out=['o']         2→1 join
  others: in=['i']      out=['o']         1→1 linear

Cross-branch: any wire connecting a FSPLIT out-port to a FFUSE in-port
that is NOT the stack-matched pair is a cross-branch wire.
"""
from __future__ import annotations

import itertools
from dataclasses import dataclass, field
from typing import Dict, Iterator, List, Optional, Set, Tuple

from tokens import Token


# ── Port helpers ─────────────────────────────────────────────────────────────

def out_ports(tok: Token) -> List[str]:
    if tok == Token.FSPLIT:
        return ['T', 'F']
    return ['o']


def in_ports(tok: Token) -> List[str]:
    if tok == Token.VINIT:
        return []
    if tok == Token.FFUSE:
        return ['T', 'F']
    return ['i']


# ── Wire ─────────────────────────────────────────────────────────────────────

class Wire:
    __slots__ = ('src_node', 'src_port', 'dst_node', 'dst_port')

    def __init__(self, src_node: int, src_port: str,
                 dst_node: int, dst_port: str) -> None:
        self.src_node = src_node
        self.src_port = src_port
        self.dst_node = dst_node
        self.dst_port = dst_port

    def __repr__(self) -> str:
        return f"Wire({self.src_node}.{self.src_port}→{self.dst_node}.{self.dst_port})"

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Wire):
            return NotImplemented
        return (self.src_node, self.src_port, self.dst_node, self.dst_port) == \
               (other.src_node, other.src_port, other.dst_node, other.dst_port)

    def __hash__(self) -> int:
        return hash((self.src_node, self.src_port, self.dst_node, self.dst_port))

    def is_T(self) -> bool:
        return self.src_port == 'T' or self.dst_port == 'T'

    def is_F(self) -> bool:
        return self.src_port == 'F' or self.dst_port == 'F'


# ── WiredGraph ────────────────────────────────────────────────────────────────

@dataclass
class WiredGraph:
    """A token arrangement with explicit port-level wiring."""
    tokens:      Tuple[Token, ...]
    wires:       List[Wire]
    name:        str = ""
    description: str = ""

    # ── accessors ──

    def n(self) -> int:
        return len(self.tokens)

    def out_wires(self, node: int) -> List[Wire]:
        return [w for w in self.wires if w.src_node == node]

    def in_wires(self, node: int) -> List[Wire]:
        return [w for w in self.wires if w.dst_node == node]

    def successors(self, node: int) -> List[int]:
        return [w.dst_node for w in self.wires if w.src_node == node]

    def predecessors(self, node: int) -> List[int]:
        return [w.src_node for w in self.wires if w.dst_node == node]

    # ── topology queries ──

    def cross_branch_wires(self) -> List[Wire]:
        """Wires where a FSPLIT F-output connects to a FFUSE other than its matched pair.

        Only FSPLIT→FFUSE arcs are considered; FSPLIT→FSPLIT nesting (T-wire
        routing outer FSPLIT.T into inner FSPLIT.i) is standard topology, not cross.
        """
        pairs = match_pairs(self.tokens)
        default_ff = {fs: ff for fs, ff in pairs}
        ffuse_nodes = {ff for _, ff in pairs}
        result = []
        for w in self.wires:
            if self.tokens[w.src_node] != Token.FSPLIT:
                continue
            if w.src_port not in ('T', 'F'):
                continue
            if w.dst_node not in ffuse_nodes:
                continue  # not going to a FFUSE — normal nesting, not cross
            if default_ff.get(w.src_node) != w.dst_node:
                result.append(w)
        return result

    def has_cross_branch(self) -> bool:
        return bool(self.cross_branch_wires())

    # ── validation ──

    def validate(self) -> List[str]:
        """Return list of violations; empty list = valid."""
        n = len(self.tokens)
        errs: List[str] = []
        src_used: Set[Tuple[int, str]] = set()
        dst_used: Set[Tuple[int, str]] = set()

        for w in self.wires:
            if w.src_node >= n or w.dst_node >= n:
                errs.append(f"node index out of range: {w}")
                continue
            ks = (w.src_node, w.src_port)
            kd = (w.dst_node, w.dst_port)
            if ks in src_used:
                errs.append(f"duplicate out-port {ks}")
            src_used.add(ks)
            if kd in dst_used:
                errs.append(f"duplicate in-port {kd}")
            dst_used.add(kd)
            if w.src_port not in out_ports(self.tokens[w.src_node]):
                errs.append(
                    f"no out-port '{w.src_port}' on "
                    f"{self.tokens[w.src_node].name}@{w.src_node}"
                )
            if w.dst_port not in in_ports(self.tokens[w.dst_node]):
                errs.append(
                    f"no in-port '{w.dst_port}' on "
                    f"{self.tokens[w.dst_node].name}@{w.dst_node}"
                )

        # All ports must be connected (positions 0 and n-1 get slack for open ends)
        for i, tok in enumerate(self.tokens):
            for p in out_ports(tok):
                if (i, p) not in src_used:
                    if i == n - 1 and p == 'o':
                        pass  # open end at last position
                    else:
                        errs.append(f"unconnected out-port ({i},{p}) on {tok.name}")
            for p in in_ports(tok):
                if (i, p) not in dst_used:
                    if i == 0 and p == 'i':
                        pass  # open end at first position
                    else:
                        errs.append(f"unconnected in-port ({i},{p}) on {tok.name}")
        return errs

    # ── layout ──

    def topological_layers(self) -> List[List[int]]:
        """Kahn's algorithm; returns list of layers, each a sorted list of node indices."""
        n = len(self.tokens)
        in_deg: Dict[int, int] = {i: 0 for i in range(n)}
        adj:    Dict[int, List[int]] = {i: [] for i in range(n)}
        for w in self.wires:
            in_deg[w.dst_node] += 1
            adj[w.src_node].append(w.dst_node)

        queue   = sorted(i for i in range(n) if in_deg[i] == 0)
        layers: List[List[int]] = []
        visited: Set[int] = set()

        while queue:
            layers.append(list(queue))
            visited.update(queue)
            nxt: List[int] = []
            for node in queue:
                for nb in adj[node]:
                    if nb not in visited:
                        in_deg[nb] -= 1
                        if in_deg[nb] == 0:
                            nxt.append(nb)
            queue = sorted(set(nxt))
        return layers

    def wire_y_hint(self, wire: Wire) -> float:
        """Y-lane hint for a wire (for layout): T=high, F=low, main=mid."""
        if wire.src_port == 'T' or wire.dst_port == 'T':
            return 0.76
        if wire.src_port == 'F' or wire.dst_port == 'F':
            return 0.24
        return 0.50


# ── FSPLIT/FFUSE stack matching ───────────────────────────────────────────────

def match_pairs(tokens: Tuple[Token, ...]) -> List[Tuple[int, int]]:
    """Match FSPLIT/FFUSE pairs by depth-first stack. Returns [(fsplit_idx, ffuse_idx)]."""
    stack: List[int] = []
    pairs: List[Tuple[int, int]] = []
    for i, tok in enumerate(tokens):
        if tok == Token.FSPLIT:
            stack.append(i)
        elif tok == Token.FFUSE and stack:
            pairs.append((stack.pop(), i))
    return pairs


# ── Standard IMASM wiring ─────────────────────────────────────────────────────

def imscr_wiring(tokens: Tuple[Token, ...]) -> WiredGraph:
    """Build the standard IMASM wiring matching the existing cfg_dag parse_dag() logic.

    For each FSPLIT/FFUSE pair (processed inner-first so outer pairs exclude
    tokens already claimed by nested pairs):
      - FSPLIT.T → first T-branch node (anchored by EVALT) or directly to FFUSE.T
      - FSPLIT.F → first F-branch node (anchored by EVALF) or directly to FFUSE.F
      - T/F-branch chains end at FFUSE.T / FFUSE.F
    Linear sections chain sequentially; FFUSE outputs chain to next linear node.

    Nesting: tokens inside a nested FSPLIT/FFUSE block are excluded from the
    outer pair's branch computation so each token is owned by exactly one pair.
    """
    n = len(tokens)
    pairs = match_pairs(tokens)
    fsplit_to_ffuse = {fs: ff for fs, ff in pairs}
    ffuse_to_fsplit = {ff: fs for fs, ff in pairs}
    fork_nodes: Set[int] = set(fsplit_to_ffuse) | set(ffuse_to_fsplit)

    # Build nesting depth for each position so outer pairs skip inner-pair tokens.
    # nesting[i] = nesting depth: 0 = top-level, 1 = inside one pair, etc.
    nesting = [0] * n
    depth = 0
    for i, tok in enumerate(tokens):
        if tok == Token.FSPLIT:
            depth += 1
            nesting[i] = depth
        elif tok == Token.FFUSE:
            nesting[i] = depth
            depth = max(0, depth - 1)
        else:
            nesting[i] = depth

    # For each pair, the "own depth" is the depth AT the FSPLIT token.
    # Branch tokens belong to this pair if their nesting depth == own_depth.
    pair_depth = {fs: nesting[fs] for fs, _ in pairs}

    t_owner: Dict[int, int] = {}
    f_owner: Dict[int, int] = {}

    for fs, ff in pairs:
        own_d = pair_depth[fs]
        # Block: tokens strictly between fs and ff at exactly own_d depth
        block = [i for i in range(fs + 1, ff)
                 if i not in fork_nodes and nesting[i] == own_d]
        blk   = [tokens[i] for i in block]
        t_a   = next((j for j, t in enumerate(blk) if t == Token.EVALT), None)
        f_a   = next((j for j, t in enumerate(blk) if t == Token.EVALF), None)
        # Branch polarity rule: AREV (parity flip) anchors F-branch when EVALF absent;
        # AFWD (forward morphism) anchors T-branch when EVALT absent.
        if f_a is None:
            f_a = next((j for j, t in enumerate(blk) if t == Token.AREV), None)
        if t_a is None:
            t_a = next((j for j, t in enumerate(blk) if t == Token.AFWD), None)

        if t_a is not None and f_a is not None:
            if t_a < f_a:
                t_nodes, f_nodes = block[:f_a], block[f_a:]
            else:
                f_nodes, t_nodes = block[:t_a], block[t_a:]
        elif f_a is not None:
            t_nodes, f_nodes = [], block
        else:
            t_nodes, f_nodes = block, []

        for idx in t_nodes:
            t_owner[idx] = fs
        for idx in f_nodes:
            f_owner[idx] = fs

    wires: List[Wire] = []
    branch_internal = set(t_owner) | set(f_owner)

    for fs, ff in pairs:
        t_nodes = [i for i in range(fs + 1, ff) if t_owner.get(i) == fs]
        f_nodes = [i for i in range(fs + 1, ff) if f_owner.get(i) == fs]

        # T-branch: FSPLIT.T → chain → FFUSE.T
        # But if T-branch is empty and there's a nested FSPLIT immediately after,
        # route FSPLIT.T → nested_FSPLIT.i
        if t_nodes:
            wires.append(Wire(fs, 'T', t_nodes[0], 'i'))
            for j in range(len(t_nodes) - 1):
                wires.append(Wire(t_nodes[j], 'o', t_nodes[j + 1], 'i'))
            wires.append(Wire(t_nodes[-1], 'o', ff, 'T'))
        else:
            # Check for nested FSPLIT immediately after fs in T position
            inner_fs = next(
                (i for i in range(fs + 1, ff) if tokens[i] == Token.FSPLIT
                 and i not in t_owner and i not in f_owner),
                None
            )
            if inner_fs is not None:
                wires.append(Wire(fs, 'T', inner_fs, 'i'))
                # inner_fs output (FFUSE) will connect via the FFUSE-chain below
            else:
                wires.append(Wire(fs, 'T', ff, 'T'))

        if f_nodes:
            wires.append(Wire(fs, 'F', f_nodes[0], 'i'))
            for j in range(len(f_nodes) - 1):
                wires.append(Wire(f_nodes[j], 'o', f_nodes[j + 1], 'i'))
            wires.append(Wire(f_nodes[-1], 'o', ff, 'F'))
        else:
            wires.append(Wire(fs, 'F', ff, 'F'))

    # Linear chain: connect non-fork, non-branch tokens in sequence.
    # Skips branch_internal tokens (they're wired by the branch section above).
    # Does NOT skip fork nodes as j-target — VINIT must connect to FSPLIT, etc.
    for i in range(n - 1):
        tok_i = tokens[i]
        if i in fork_nodes or i in branch_internal:
            continue
        j = i + 1
        if j in branch_internal:
            continue
        if out_ports(tok_i) and in_ports(tokens[j]):
            dp = 'T' if tokens[j] == Token.FFUSE else 'i'
            wires.append(Wire(i, 'o', j, dp))

    # FFUSE outputs: skip branch_internal tokens, connect to next reachable node.
    # Works for all depths — inner FFUSEs skip their enclosing branch tokens.
    for ff in ffuse_to_fsplit:
        j = ff + 1
        while j < n and j in branch_internal:
            j += 1
        if j < n and in_ports(tokens[j]):
            dp = 'T' if tokens[j] == Token.FFUSE else 'i'
            wires.append(Wire(ff, 'o', j, dp))

    return WiredGraph(tokens=tokens, wires=wires)


# ── Cross-branch wiring ───────────────────────────────────────────────────────

def cross_wiring(
    tokens: Tuple[Token, ...],
    overrides: List[Tuple[int, str, int, str]],
) -> WiredGraph:
    """Build wiring from imscr_wiring() but replace specific output-port connections.

    Each override is (src_node, src_port, dst_node, dst_port).
    Any existing wire from (src_node, src_port) is replaced.
    """
    base = imscr_wiring(tokens)
    override_map = {(s, sp): (d, dp) for s, sp, d, dp in overrides}
    new_wires: List[Wire] = []
    for w in base.wires:
        key = (w.src_node, w.src_port)
        if key in override_map:
            d, dp = override_map[key]
            new_wires.append(Wire(w.src_node, w.src_port, d, dp))
        else:
            new_wires.append(w)
    return WiredGraph(tokens=tokens, wires=new_wires)


def cross_wiring_variants(
    tokens: Tuple[Token, ...],
) -> Iterator[WiredGraph]:
    """Enumerate all valid wirings where ≥1 FSPLIT F-output connects to a
    non-default FFUSE. Requires ≥2 matched FSPLIT/FFUSE pairs.
    """
    pairs = match_pairs(tokens)
    if len(pairs) < 2:
        return

    fsplit_nodes = [fs for fs, _ in pairs]
    ffuse_nodes  = [ff for _, ff in pairs]

    # Try all permutations of FSPLIT F-output → FFUSE F-input assignments
    for perm in itertools.permutations(range(len(pairs))):
        is_default = all(perm[i] == i for i in range(len(pairs)))
        if is_default:
            continue
        overrides = [(fsplit_nodes[i], 'F', ffuse_nodes[perm[i]], 'F')
                     for i in range(len(pairs))]
        g = cross_wiring(tokens, overrides)
        g.name = f"cross_{''.join(str(p) for p in perm)}"
        if not g.validate():
            yield g


# ── Named novel wired sequences ───────────────────────────────────────────────
#
# Each novel graph is a hand-crafted cross-branch wiring with full wire list.
# All port assignments are verified to be complete and non-duplicate.
#
#   XX   — Branch Entangle  : two nested FSPLITs with crossed F-outputs (X-topology)
#   XXI  — Paradox Bridge   : ENGAGR-fed fork; outer F crosses into inner FFUSE
#   XXII — Fold Back        : AREV/AFWD tokens with inner F crossing to outer join
#   XXIII— Möbius Fork      : ISCRIB-bounded, ENGAGR on inner T; CLINK on post path


def _build_novel_graphs() -> Dict[str, WiredGraph]:
    graphs: Dict[str, WiredGraph] = {}

    # ── XX — Branch Entangle ─────────────────────────────────────────────────
    # Tokens: VINIT(0) FSPLIT(1) FSPLIT(2) EVALT(3) FFUSE(4) EVALF(5) FFUSE(6) TANCH(7)
    #
    # Default wiring:
    #   FSPLIT1.T → FSPLIT2 → EVALT → FFUSE2.T ; FSPLIT2.F → FFUSE2.F (empty arc)
    #   FSPLIT1.F → FFUSE1.F (empty arc)
    #   FFUSE2 → EVALF → FFUSE1.T
    #
    # Cross wiring (X-topology):
    #   FSPLIT1.F → FFUSE2(4).F   (outer F enters inner join)
    #   FSPLIT2.F → FFUSE1(6).F   (inner F enters outer join)
    #
    # Port verification:
    #   VINIT(0):  out.o✓→1.i
    #   FSPLIT(1): in.i✓←0; out.T✓→2.i; out.F✓→4.F  [CROSS: to inner FFUSE]
    #   FSPLIT(2): in.i✓←1.T; out.T✓→3.i; out.F✓→6.F [CROSS: to outer FFUSE]
    #   EVALT(3):  in.i✓←2.T; out.o✓→4.T
    #   FFUSE(4):  in.T✓←3; in.F✓←1.F; out.o✓→5.i
    #   EVALF(5):  in.i✓←4; out.o✓→6.T
    #   FFUSE(6):  in.T✓←5; in.F✓←2.F; out.o✓→7.i
    #   TANCH(7):  in.i✓←6; (end of chain)
    toks_xx = (Token.VINIT, Token.FSPLIT, Token.FSPLIT, Token.EVALT,
               Token.FFUSE, Token.EVALF, Token.FFUSE, Token.TANCH)
    graphs["XX_Branch_Entangle"] = WiredGraph(
        tokens=toks_xx,
        wires=[
            Wire(0, 'o', 1, 'i'),
            Wire(1, 'T', 2, 'i'),
            Wire(1, 'F', 4, 'F'),   # outer FSPLIT.F → inner FFUSE.F  [CROSS]
            Wire(2, 'T', 3, 'i'),
            Wire(2, 'F', 6, 'F'),   # inner FSPLIT.F → outer FFUSE.F  [CROSS]
            Wire(3, 'o', 4, 'T'),
            Wire(4, 'o', 5, 'i'),
            Wire(5, 'o', 6, 'T'),
            Wire(6, 'o', 7, 'i'),
        ],
        name="XX_Branch_Entangle",
        description=(
            "Two nested FSPLITs with fully crossed F-outputs. "
            "FSPLIT1.F→FFUSE_inner; FSPLIT2.F→FFUSE_outer. "
            "Creates an X-crossing: depth-1 F-wire terminates at depth-2 join, "
            "depth-2 F-wire terminates at depth-1 join. "
            "Non-planar wiring — cannot be embedded in a plane without crossing."
        ),
    )

    # ── XXI — Paradox Bridge ─────────────────────────────────────────────────
    # Tokens: ENGAGR(0) FSPLIT(1) FSPLIT(2) EVALT(3) EVALF(4) FFUSE(5) FFUSE(6) IMSCRIB(7)
    #
    # ENGAGR produces B; feeds FSPLIT1.
    # Cross: FSPLIT1.F bridges OVER the inner FSPLIT2/FFUSE5 block into FFUSE5.F.
    # Inner block: FSPLIT2.T→EVALT→FFUSE5.T; FSPLIT2.F→EVALF→FFUSE6.T
    # FFUSE5 (inner) receives: T from EVALT, F from FSPLIT1.F  [CROSS]
    # FFUSE6 (outer) receives: T from EVALF(4), F from FFUSE5.o
    #
    # Port verification:
    #   ENGAGR(0):  in.i (open at pos 0); out.o→1.i
    #   FSPLIT(1):  in.i←0; out.T→2.i; out.F→5.F  [CROSS: bridges inner block]
    #   FSPLIT(2):  in.i←1.T; out.T→3.i; out.F→4.i
    #   EVALT(3):   in.i←2.T; out.o→5.T
    #   EVALF(4):   in.i←2.F; out.o→6.T
    #   FFUSE(5):   in.T←3; in.F←1.F; out.o→6.F
    #   FFUSE(6):   in.T←4; in.F←5.o; out.o→7.i
    #   IMSCRIB(7): in.i←6; (end)
    toks_xxi = (Token.ENGAGR, Token.FSPLIT, Token.FSPLIT, Token.EVALT,
                Token.EVALF, Token.FFUSE, Token.FFUSE, Token.IMSCRIB)
    graphs["XXI_Paradox_Bridge"] = WiredGraph(
        tokens=toks_xxi,
        wires=[
            Wire(0, 'o', 1, 'i'),
            Wire(1, 'T', 2, 'i'),
            Wire(1, 'F', 5, 'F'),   # FSPLIT1.F bridges into inner FFUSE  [CROSS]
            Wire(2, 'T', 3, 'i'),
            Wire(2, 'F', 4, 'i'),
            Wire(3, 'o', 5, 'T'),
            Wire(4, 'o', 6, 'T'),
            Wire(5, 'o', 6, 'F'),
            Wire(6, 'o', 7, 'i'),
        ],
        name="XXI_Paradox_Bridge",
        description=(
            "ENGAGR-sourced fork with outer F-wire bridging into the inner FFUSE. "
            "B-state from ENGAGR splits: T-path reaches inner split where gates "
            "EVALT/EVALF discriminate; F-path bypasses inner FSPLIT entirely and "
            "enters inner FFUSE directly. B penetrates a gate boundary it normally "
            "cannot cross."
        ),
    )

    # ── XXII — Fold Back ─────────────────────────────────────────────────────
    # Tokens: VINIT(0) FSPLIT(1) FSPLIT(2) AREV(3) FFUSE(4) AFWD(5) FFUSE(6) TANCH(7)
    #
    # No dialetheia tokens — pure Logical+Frobenius cross-wiring.
    # Cross: inner FSPLIT2.F → outer FFUSE6.F
    #        (default would be FSPLIT2.F → FFUSE4.F)
    #
    # Port verification:
    #   VINIT(0):  out.o→1.i
    #   FSPLIT(1): in.i←0; out.T→2.i; out.F→4.F
    #   FSPLIT(2): in.i←1.T; out.T→3.i; out.F→6.F  [CROSS: inner F → outer join]
    #   AREV(3):   in.i←2.T; out.o→4.T
    #   FFUSE(4):  in.T←3; in.F←1.F; out.o→5.i
    #   AFWD(5):   in.i←4; out.o→6.T
    #   FFUSE(6):  in.T←5; in.F←2.F; out.o→7.i
    #   TANCH(7):  in.i←6
    toks_xxii = (Token.VINIT, Token.FSPLIT, Token.FSPLIT, Token.AREV,
                 Token.FFUSE, Token.AFWD, Token.FFUSE, Token.TANCH)
    graphs["XXII_Fold_Back"] = WiredGraph(
        tokens=toks_xxii,
        wires=[
            Wire(0, 'o', 1, 'i'),
            Wire(1, 'T', 2, 'i'),
            Wire(1, 'F', 4, 'F'),
            Wire(2, 'T', 3, 'i'),
            Wire(2, 'F', 6, 'F'),   # inner FSPLIT.F folds back to outer join [CROSS]
            Wire(3, 'o', 4, 'T'),
            Wire(4, 'o', 5, 'i'),
            Wire(5, 'o', 6, 'T'),
            Wire(6, 'o', 7, 'i'),
        ],
        name="XXII_Fold_Back",
        description=(
            "Pure Logical+Frobenius X-topology (no dialetheia). "
            "AREV on inner T-path; AFWD on post-inner path. "
            "Inner FSPLIT.F folds back past the inner FFUSE to the outer FFUSE. "
            "Demonstrates cross-branch wiring without paradox stabilization."
        ),
    )

    # ── XXIII — Möbius Fork ──────────────────────────────────────────────────
    # Tokens: IMSCRIB(0) FSPLIT(1) FSPLIT(2) ENGAGR(3) FFUSE(4) CLINK(5) FFUSE(6) IMSCRIB(7)
    #
    # Self-referential (IMSCRIB at both ends). ENGAGR on inner T-path.
    # CLINK on post-inner path (composition/meet).
    # Same X-topology as XX but with ENGAGR/CLINK semantics.
    #
    # Port verification:
    #   IMSCRIB(0): in.i (open); out.o→1.i
    #   FSPLIT(1):  in.i←0; out.T→2.i; out.F→4.F  [CROSS]
    #   FSPLIT(2):  in.i←1.T; out.T→3.i; out.F→6.F [CROSS]
    #   ENGAGR(3):  in.i←2.T; out.o→4.T
    #   FFUSE(4):   in.T←3; in.F←1.F; out.o→5.i
    #   CLINK(5):   in.i←4; out.o→6.T
    #   FFUSE(6):   in.T←5; in.F←2.F; out.o→7.i
    #   IMSCRIB(7): in.i←6 (end)
    toks_xxiii = (Token.IMSCRIB, Token.FSPLIT, Token.FSPLIT, Token.ENGAGR,
                  Token.FFUSE, Token.CLINK, Token.FFUSE, Token.IMSCRIB)
    graphs["XXIII_Mobius_Fork"] = WiredGraph(
        tokens=toks_xxiii,
        wires=[
            Wire(0, 'o', 1, 'i'),
            Wire(1, 'T', 2, 'i'),
            Wire(1, 'F', 4, 'F'),   # outer F → inner join  [CROSS]
            Wire(2, 'T', 3, 'i'),
            Wire(2, 'F', 6, 'F'),   # inner F → outer join  [CROSS]
            Wire(3, 'o', 4, 'T'),
            Wire(4, 'o', 5, 'i'),
            Wire(5, 'o', 6, 'T'),
            Wire(6, 'o', 7, 'i'),
        ],
        name="XXIII_Mobius_Fork",
        description=(
            "IMSCRIB-bounded self-referential fork with Möbius-like X-crossing. "
            "ENGAGR on inner T-branch injects B into inner FFUSE; outer F-wire "
            "from FSPLIT1 also feeds inner FFUSE, creating a dual-source B-path. "
            "CLINK composes the two join results. Non-planar topology."
        ),
    )

    return graphs


NOVEL_GRAPHS: Dict[str, WiredGraph] = _build_novel_graphs()
