"""
IMASM-16_3 TOKEN SPACE — 14 tokens in 5 algebraic families, purely symbolic.

Sibling to `tokens.py` (the classic 12-token space), not a replacement: this file
does NOT renumber or extend the 0-11 `Token` enum (that would corrupt every
existing arrangement encoding built on it — the 12^8 iterator, cfg_dag.py,
proof_scaffold.py, and everything downstream that treats index 0-11 as closed).
`Token16_3` is its own 0-13 enum.

THE REAL CONSTRUCTION. This is IMASM's grammar for the real trilattice
SIXTEEN_3: Shramko, Y., Dunn, J.M., Takenaka, T., "The Trilattice of
Constructive Truth Values", J. Logic and Computation 11(6):761-788, 2001
(§5) — verified against the source PDF, not reconstructed from memory or from
this project's own prior secondary references to it.

The base set is FOUR initial truth values, not two and not a product of two
FOURs:

    I = {T, F, t, f}
      T — a sentence is constructively PROVEN
      F — a sentence is constructively REFUTED
      t — a sentence is (non-constructively) ACCEPTABLE
      f — a sentence is (non-constructively) REJECTABLE

SIXTEEN_3 is the full powerset P(I) — all 16 subsets of these four base
values (N = {} = empty/no-info, A = {T,F,t,f} = full/all-info). Three
independent partial orderings are defined on P(I) (Definition 5.2):

    x ≤_i y  ⟺  x ⊆ y                                        (information)
    x ≤_t y  ⟺  x∩{T,t} ⊆ y∩{T,t}  and  y∩{F,f} ⊆ x∩{F,f}     (truth)
    x ≤_c y  ⟺  x∩{T,F} ⊆ y∩{T,F}  and  y∩{t,f} ⊆ x∩{t,f}     (constructivity)

Verified against the paper's own worked example (§5, pp.776-777): T ∧ t = N
under ≤_t — the conjunction of two "truths" gives NOTHING, because neither
conjunct is both T and t simultaneously. `meet_t` below reproduces this
exactly (see the `if __name__` sanity check at the bottom of this file).

Opcode → base-value mapping for IMASM-16_3's EVALT/EVALF/EVALI/TNEG/INEG:

    EVALT sets T (constructive truth touched)
    EVALF sets F (constructive falsity touched)
    EVALI sets BOTH t and f (the acceptable/rejectable pair IS the
          information layer beyond classical T/F)
    TNEG  swaps T ↔ F   (the paper's negation: inverts ≤_t, leaves ≤_i
          exactly unchanged — a swap preserves |x|, the defining property
          the paper requires of a bilattice/trilattice negation)
    INEG  swaps t ↔ f   (the same negation, on the acceptable/rejectable pair)

No token uses a Latin letter as its GLYPH (see TOKEN_GLYPH) — a trilattice
verdict (T, N, B, F) can never be confused with a graph node.

This is the canonical arity/family/algebra reference for IMASM-16_3, in the
same role `tokens.py::TOKEN_ARITY` plays for the classic grammar; the
runnable register-machine siblings (ask_native/src/imasm16_3.rs,
ob3ect/digital/imasm16_3_core.py) should be read against THIS file's algebra.
"""

from enum import IntEnum
from itertools import combinations
from typing import Tuple, List, Dict, FrozenSet, Optional


class Family16_3(IntEnum):
    LOGICAL = 0      # 6 tokens: VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB
    TRILATTICE = 1   # 2 tokens: FSPLIT3, FFUSE3 (3-way fork/join)
    EVAL = 2         # 3 tokens: EVALT, EVALF, EVALI (the three orthogonal axes)
    NEGATION = 3     # 2 tokens: TNEG, INEG
    LINEAR = 4       # 1 token:  IFIX


class Token16_3(IntEnum):
    """The 14 IMASM-16_3 tokens. Integer value = index (0-13)."""
    VINIT   = 0    # Logical: initial object (void), glyph ⊢
    TANCH   = 1    # Logical: terminal object (boundary), glyph ⊣
    AFWD    = 2    # Logical: forward morphism, glyph >
    AREV    = 3    # Logical: reverse morphism, glyph <
    CLINK   = 4    # Logical: composition of morphisms, glyph =
    IMSCRIB = 5    # Logical: identity morphism, glyph ⊙
    FSPLIT3 = 6    # Trilattice: 3-way split (δ₃), glyph ☊
    FFUSE3  = 7    # Trilattice: 3-way fuse (μ₃), glyph ☋
    EVALT   = 8    # Eval: sets T (constructively proven), glyph +
    EVALF   = 9    # Eval: sets F (constructively refuted), glyph ×
    EVALI   = 10   # Eval: sets t AND f (the information layer), glyph ⊞
    TNEG    = 11   # Negation: swaps T ↔ F, glyph ~
    INEG    = 12   # Negation: swaps t ↔ f, glyph ≁
    IFIX    = 13   # Linear: irreversible fixation, glyph ¬


TOKEN16_3_NAMES: List[str] = [t.name for t in Token16_3]
TOKEN16_3_COUNT: int = 14

# ─── Symbolic glyphs — no Latin letters ─────────────────────────────────────
TOKEN_GLYPH: Dict[Token16_3, str] = {
    Token16_3.VINIT:   "⊢",
    Token16_3.TANCH:   "⊣",
    Token16_3.AFWD:    ">",
    Token16_3.AREV:    "<",
    Token16_3.CLINK:   "=",
    Token16_3.IMSCRIB: "⊙",
    Token16_3.FSPLIT3: "☊",
    Token16_3.FFUSE3:  "☋",
    Token16_3.EVALT:   "+",
    Token16_3.EVALF:   "×",
    Token16_3.EVALI:   "⊞",
    Token16_3.TNEG:    "~",
    Token16_3.INEG:    "≁",
    Token16_3.IFIX:    "¬",
}
GLYPH_TO_TOKEN: Dict[str, Token16_3] = {g: t for t, g in TOKEN_GLYPH.items()}
assert len(TOKEN_GLYPH) == len(GLYPH_TO_TOKEN) == 14, "glyphs must be unique"
for _g in TOKEN_GLYPH.values():
    assert not _g.isalpha(), f"glyph {_g!r} is a Latin letter — violates the no-Latin-opcode rule"

# ─── DAG arity ─────────────────────────────────────────────────────────────
TOKEN_ARITY: Dict[Token16_3, Tuple[int, int]] = {
    Token16_3.VINIT:   (0, 1),
    Token16_3.TANCH:   (1, 1),
    Token16_3.AFWD:    (1, 1),
    Token16_3.AREV:    (1, 1),
    Token16_3.CLINK:   (1, 1),
    Token16_3.IMSCRIB: (1, 1),
    Token16_3.FSPLIT3: (1, 3),  # tri-fork: one in, three out (T/F/I arms)
    Token16_3.FFUSE3:  (3, 1),  # tri-join: three in (T/F/I arms), one out
    Token16_3.EVALT:   (1, 1),
    Token16_3.EVALF:   (1, 1),
    Token16_3.EVALI:   (1, 1),
    Token16_3.TNEG:    (1, 1),
    Token16_3.INEG:    (1, 1),
    Token16_3.IFIX:    (1, 1),
}

TOKEN_ARM: Dict[Token16_3, str] = {
    Token16_3.EVALT: 'T',
    Token16_3.EVALF: 'F',
    Token16_3.EVALI: 'I',
}

FORK_TOKENS: frozenset = frozenset({Token16_3.FSPLIT3})
JOIN_TOKENS: frozenset = frozenset({Token16_3.FFUSE3})

WORK_TOKENS: frozenset = frozenset({
    Token16_3.AFWD, Token16_3.AREV, Token16_3.CLINK,
    Token16_3.EVALT, Token16_3.EVALF, Token16_3.EVALI,
    Token16_3.TNEG, Token16_3.INEG, Token16_3.IFIX,
})

TOKEN_FAMILY: Dict[Token16_3, Family16_3] = {
    Token16_3.VINIT:   Family16_3.LOGICAL,
    Token16_3.TANCH:   Family16_3.LOGICAL,
    Token16_3.AFWD:    Family16_3.LOGICAL,
    Token16_3.AREV:    Family16_3.LOGICAL,
    Token16_3.CLINK:   Family16_3.LOGICAL,
    Token16_3.IMSCRIB: Family16_3.LOGICAL,
    Token16_3.FSPLIT3: Family16_3.TRILATTICE,
    Token16_3.FFUSE3:  Family16_3.TRILATTICE,
    Token16_3.EVALT:   Family16_3.EVAL,
    Token16_3.EVALF:   Family16_3.EVAL,
    Token16_3.EVALI:   Family16_3.EVAL,
    Token16_3.TNEG:    Family16_3.NEGATION,
    Token16_3.INEG:    Family16_3.NEGATION,
    Token16_3.IFIX:    Family16_3.LINEAR,
}

FAMILY_SIZE: Dict[Family16_3, int] = {
    Family16_3.LOGICAL: 6, Family16_3.TRILATTICE: 2, Family16_3.EVAL: 3,
    Family16_3.NEGATION: 2, Family16_3.LINEAR: 1,
}
FAMILY_NAMES: Dict[Family16_3, str] = {
    Family16_3.LOGICAL: "Logical", Family16_3.TRILATTICE: "Trilattice",
    Family16_3.EVAL: "Eval", Family16_3.NEGATION: "Negation", Family16_3.LINEAR: "Linear",
}
FAMILY_TOKENS: Dict[Family16_3, List[Token16_3]] = {
    Family16_3.LOGICAL:    [Token16_3.VINIT, Token16_3.TANCH, Token16_3.AFWD,
                             Token16_3.AREV, Token16_3.CLINK, Token16_3.IMSCRIB],
    Family16_3.TRILATTICE: [Token16_3.FSPLIT3, Token16_3.FFUSE3],
    Family16_3.EVAL:       [Token16_3.EVALT, Token16_3.EVALF, Token16_3.EVALI],
    Family16_3.NEGATION:   [Token16_3.TNEG, Token16_3.INEG],
    Family16_3.LINEAR:     [Token16_3.IFIX],
}
assert sum(FAMILY_SIZE.values()) == TOKEN16_3_COUNT


def token16_3_name(idx: int) -> str:
    return Token16_3(idx).name


def token16_3_family(idx: int) -> Family16_3:
    return TOKEN_FAMILY[Token16_3(idx)]


def signature16_3(arr: Tuple[int, ...]) -> Tuple[int, int, int, int, int]:
    counts = [0, 0, 0, 0, 0]
    for t in arr:
        counts[token16_3_family(t)] += 1
    return tuple(counts)  # type: ignore[return-value]


def glyph_word(arr: Tuple[int, ...]) -> str:
    return "".join(TOKEN_GLYPH[Token16_3(t)] for t in arr)


def parse_glyph_word(word: str) -> List[Token16_3]:
    return [GLYPH_TO_TOKEN[ch] for ch in word if ch in GLYPH_TO_TOKEN]


# ═════════════════════════════════════════════════════════════════════════
# THE SIXTEEN_3 TRILATTICE ALGEBRA — the real carrier and its three orders
# ═════════════════════════════════════════════════════════════════════════

BASE = ('T', 'F', 't', 'f')  # display order
Reg = FrozenSet[str]
EMPTY: Reg = frozenset()
FULL: Reg = frozenset(BASE)


def reg_name(r: Reg) -> str:
    if not r:
        return "N"
    if r == FULL:
        return "A"
    return "".join(b for b in BASE if b in r)


def reg_from_name(name: str) -> Reg:
    if name in ("N", "∅", ""):
        return EMPTY
    if name == "A":
        return FULL
    return frozenset(name)


def leq_i(x: Reg, y: Reg) -> bool:
    """Information order: x ≤_i y ⟺ x ⊆ y."""
    return x <= y


def leq_t(x: Reg, y: Reg) -> bool:
    """Truth order: positive part (T,t) grows, negative part (F,f) shrinks."""
    return (x & {'T', 't'}) <= (y & {'T', 't'}) and (y & {'F', 'f'}) <= (x & {'F', 'f'})


def leq_c(x: Reg, y: Reg) -> bool:
    """Constructivity order: constructive part (T,F) grows, non-constructive (t,f) shrinks."""
    return (x & {'T', 'F'}) <= (y & {'T', 'F'}) and (y & {'t', 'f'}) <= (x & {'t', 'f'})


def meet_i(x: Reg, y: Reg) -> Reg: return x & y
def join_i(x: Reg, y: Reg) -> Reg: return x | y

def meet_t(x: Reg, y: Reg) -> Reg:
    return ((x & {'T', 't'}) & (y & {'T', 't'})) | ((x & {'F', 'f'}) | (y & {'F', 'f'}))

def join_t(x: Reg, y: Reg) -> Reg:
    return ((x & {'T', 't'}) | (y & {'T', 't'})) | ((x & {'F', 'f'}) & (y & {'F', 'f'}))

def meet_c(x: Reg, y: Reg) -> Reg:
    return ((x & {'T', 'F'}) & (y & {'T', 'F'})) | ((x & {'t', 'f'}) | (y & {'t', 'f'}))

def join_c(x: Reg, y: Reg) -> Reg:
    return ((x & {'T', 'F'}) | (y & {'T', 'F'})) | ((x & {'t', 'f'}) & (y & {'t', 'f'}))

# Sanity check against the paper's own worked example (§5, pp.776-777): T ∧ t = N.
assert meet_t(frozenset('T'), frozenset('t')) == EMPTY, \
    "meet_t formula does not match the paper's own T∧t=N worked example"

ALL_16: List[Reg] = [frozenset(c) for k in range(5) for c in combinations(BASE, k)]
assert len(ALL_16) == 16


# ─── Tri-ancestral close condition ──────────────────────────────────────────
def tri_ancestral_verdict(arr: Tuple[int, ...]) -> Tuple[str, str]:
    """
      T — every FSPLIT3 pairs with a later FFUSE3, and at least one WORK token
          ran somewhere in that interval (a real transformation).
      N — paired, but no WORK token ran inside — μ∘δ=id verifies nothing.
      B — a FSPLIT3 has no matching later FFUSE3 — a fork left open.
      F — a FFUSE3 has no preceding FSPLIT3 — ill-typed.
    """
    tokens = [Token16_3(t) for t in arr]
    split_idx = [i for i, t in enumerate(tokens) if t == Token16_3.FSPLIT3]
    fuse_idx = [i for i, t in enumerate(tokens) if t == Token16_3.FFUSE3]

    for fj in fuse_idx:
        if not any(si < fj for si in split_idx):
            return ("F", f"FFUSE3 at step {fj + 1} has no preceding FSPLIT3 — ill-typed")

    if not split_idx and not fuse_idx:
        return ("N", "No fork/fuse — void, never weighed alternatives")

    for si in split_idx:
        if not any(fj > si for fj in fuse_idx):
            return ("B", f"FSPLIT3 at step {si + 1} dangles — no matching FFUSE3")

    for si in split_idx:
        fj = next(fj for fj in fuse_idx if fj > si)
        interval = tokens[si + 1:fj]
        if any(t in WORK_TOKENS for t in interval):
            return ("T", "Tri-ancestral reconnection over a transformed object — closes")
    return ("N", "Split/fused with no work on any arm — μ∘δ=id verifies nothing")


if __name__ == "__main__":
    example = parse_glyph_word("⊢>☊+×⊞≁☋¬⊣")
    print("Example word:", glyph_word(tuple(int(t) for t in example)))
    print("Names:       ", " → ".join(t.name for t in example))
    print("Signature:   ", signature16_3(tuple(int(t) for t in example)))
    verdict, msg = tri_ancestral_verdict(tuple(int(t) for t in example))
    print(f"Verdict:      {verdict} — {msg}")

    neutral = parse_glyph_word("⊢☊⊙⊙⊙☋⊣")
    print("\nNeutral inflation word:", glyph_word(tuple(int(t) for t in neutral)))
    verdict, msg = tri_ancestral_verdict(tuple(int(t) for t in neutral))
    print(f"Verdict:      {verdict} — {msg}")

    print("\nSanity check — the paper's own worked example, T ∧ t = N (§5, p.776-777):")
    print(f"  meet_t({{T}}, {{t}}) = {reg_name(meet_t(frozenset('T'), frozenset('t')))}")

    print("\nThe 16-element carrier (Table 1 of the paper), by level:")
    by_level: Dict[int, List[Reg]] = {}
    for r in ALL_16:
        by_level.setdefault(len(r), []).append(r)
    for k in sorted(by_level):
        print(f"  Level {k+1} ({len(by_level[k])}): {', '.join(reg_name(r) for r in by_level[k])}")
