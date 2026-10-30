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
            if not (0 <= w.src_node < self.n() and 0 <= w.dst_node < self.n()):
                raise ValueError(f"node index out of range: {w}")
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
            if not (0 <= w.src_node < n and 0 <= w.dst_node < n):
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
            if not (0 <= w.src_node < n and 0 <= w.dst_node < n):
                raise ValueError(f"node index out of range: {w}")
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
        if len(visited) != n:
            raise ValueError("Graph contains a directed cycle; no complete topological layering exists")
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
    pairs = dict(match_pairs(tokens))
    wires: List[Wire] = []

    # A nested fork/fuse block is one composable arm segment. Its input is
    # the fork and its output is the fuse, so neither end can be skipped when
    # ordinary operations occur before or after it on an enclosing arm.
    def segments(lo: int, hi: int) -> List[Tuple[int, int]]:
        result = []
        i = lo
        while i < hi:
            end = pairs.get(i, i)
            result.append((i, end))
            i = end + 1
        return result

    def connect(src: int, dst: int, sp: str = None, dp: str = None) -> None:
        # Unmatched nodes keep their other ports open. Never invent an 'o'
        # output on a fork or an 'i' input on a source.
        if not in_ports(tokens[dst]):
            return
        wires.append(Wire(src, sp or out_ports(tokens[src])[0],
                          dst, dp or in_ports(tokens[dst])[0]))

    def chain(parts: List[Tuple[int, int]]) -> None:
        for entry, exit in parts:
            if entry != exit:
                fork(entry, exit)
        for (_, exit), (entry, _) in zip(parts, parts[1:]):
            connect(exit, entry)

    def fork(fs: int, ff: int) -> None:
        parts = segments(fs + 1, ff)
        # Only immediate operations choose the enclosing arm. The contents of
        # a nested segment belong to that segment's own branch assignment.
        def anchor(primary: Token, secondary: Token):
            for token in (primary, secondary):
                found = next((j for j, (a, b) in enumerate(parts)
                              if a == b and tokens[a] == token), None)
                if found is not None:
                    return found
            return None

        ta = anchor(Token.EVALT, Token.AFWD)
        fa = anchor(Token.EVALF, Token.AREV)
        if ta is not None and fa is not None:
            if ta < fa:
                t_parts, f_parts = parts[:fa], parts[fa:]
            else:
                f_parts, t_parts = parts[:ta], parts[ta:]
        elif fa is not None:
            t_parts, f_parts = [], parts
        else:
            t_parts, f_parts = parts, []
        for port, arm in (("T", t_parts), ("F", f_parts)):
            chain(arm)
            if arm:
                connect(fs, arm[0][0], sp=port)
                connect(arm[-1][1], ff, dp=port)
            else:
                connect(fs, ff, sp=port, dp=port)

    chain(segments(0, len(tokens)))
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
    override_map = {}
    existing = {(w.src_node, w.src_port) for w in base.wires}
    for s, sp, d, dp in overrides:
        if not (0 <= s < len(tokens) and 0 <= d < len(tokens)):
            raise ValueError("override node index out of range")
        if (s, sp) not in existing:
            raise ValueError(f"override has no existing source wire: {(s, sp)}")
        if dp not in in_ports(tokens[d]):
            raise ValueError(f"override destination has no port: {(d, dp)}")
        if (s, sp) in override_map:
            raise ValueError(f"duplicate override source: {(s, sp)}")
        override_map[s, sp] = (d, dp)
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
            "Crossed port routing in this layout; the underlying graph is planar."
        ),
    )

    # ── XXI — Paradox Bridge ─────────────────────────────────────────────────
    # Tokens: ENGAGR(0) FSPLIT(1) FSPLIT(2) EVALT(3) EVALF(4) FFUSE(5) FFUSE(6) IMSCRIB(7)
    #
    # Native ENGAGR adds the information values t,f; feeds FSPLIT1.
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
            "ENGAGR adds t,f: T-path reaches inner split where gates "
            "EVALT/EVALF discriminate; F-path bypasses inner FSPLIT entirely and "
            "enters inner FFUSE directly. The returned information support remains "
            "attached to its routed arms."
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
            "ENGAGR on inner T-branch adds t,f before inner FFUSE; outer F-wire "
            "from FSPLIT1 also feeds inner FFUSE. "
            "CLINK carries the join result. Crossed planar port routing."
        ),
    )

    return graphs


NOVEL_GRAPHS: Dict[str, WiredGraph] = _build_novel_graphs()
