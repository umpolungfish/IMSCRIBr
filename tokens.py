"""
IMASM TOKEN SPACE — 12 tokens in 4 algebraic families.

The iterator maps 12^8 = 429,981,696 arrangements of length 8
(plus variable-length arrangements from length 1 to 8, totaling ~469M).

Token index (0-11) is used internally for fast integer encoding.
"""

from enum import IntEnum
from typing import Tuple, List, Dict

class Family(IntEnum):
    LOGICAL = 0     # 6 tokens: VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB
    FROBENIUS = 1   # 2 tokens: FSPLIT, FFUSE
    DIALETHEIA = 2  # 3 tokens: EVALT, EVALF, ENGAGR
    LINEAR = 3      # 1 token:  IFIX

class Token(IntEnum):
    """The 12 IMASM tokens. Integer value = index (0-11)."""
    VINIT   = 0   # Logical: initial object (void)
    TANCH   = 1   # Logical: terminal object (boundary)
    AFWD    = 2   # Logical: forward morphism
    AREV    = 3   # Logical: reverse morphism
    CLINK   = 4   # Logical: composition of morphisms
    IMSCRIB = 5   # Logical: identity morphism
    FSPLIT  = 6   # Frobenius: split (δ)
    FFUSE   = 7   # Frobenius: fuse (μ)
    EVALT   = 8   # Dialetheia: evaluate-true
    EVALF   = 9   # Dialetheia: evaluate-false
    ENGAGR  = 10  # Dialetheia: engage/recognize paradox
    IFIX    = 11  # Linear: irreversible fixation (!)

# Token metadata
TOKEN_NAMES: List[str] = [t.name for t in Token]
TOKEN_COUNT: int = 12

# Family membership
TOKEN_FAMILY: Dict[Token, Family] = {
    Token.VINIT:   Family.LOGICAL,
    Token.TANCH:   Family.LOGICAL,
    Token.AFWD:    Family.LOGICAL,
    Token.AREV:    Family.LOGICAL,
    Token.CLINK:   Family.LOGICAL,
    Token.IMSCRIB: Family.LOGICAL,
    Token.FSPLIT:  Family.FROBENIUS,
    Token.FFUSE:   Family.FROBENIUS,
    Token.EVALT:   Family.DIALETHEIA,
    Token.EVALF:   Family.DIALETHEIA,
    Token.ENGAGR:  Family.DIALETHEIA,
    Token.IFIX:    Family.LINEAR,
}

# Family sizes
FAMILY_SIZE: Dict[Family, int] = {
    Family.LOGICAL: 6,
    Family.FROBENIUS: 2,
    Family.DIALETHEIA: 3,
    Family.LINEAR: 1,
}

FAMILY_NAMES: Dict[Family, str] = {
    Family.LOGICAL: "Logical",
    Family.FROBENIUS: "Frobenius",
    Family.DIALETHEIA: "Dialetheia",
    Family.LINEAR: "Linear",
}

# Tokens per family
FAMILY_TOKENS: Dict[Family, List[Token]] = {
    Family.LOGICAL:    [Token.VINIT, Token.TANCH, Token.AFWD, Token.AREV, Token.CLINK, Token.IMSCRIB],
    Family.FROBENIUS:  [Token.FSPLIT, Token.FFUSE],
    Family.DIALETHEIA: [Token.EVALT, Token.EVALF, Token.ENGAGR],
    Family.LINEAR:     [Token.IFIX],
}

def token_name(idx: int) -> str:
    """Convert index 0-11 to token name string."""
    return Token(idx).name

def token_family(idx: int) -> Family:
    """Get family for token index."""
    return TOKEN_FAMILY[Token(idx)]

def signature(arr: Tuple[int, ...]) -> Tuple[int, int, int, int]:
    """Compute family signature (L, F, D, X) for an arrangement."""
    counts = [0, 0, 0, 0]
    for t in arr:
        counts[token_family(t)] += 1
    return (counts[0], counts[1], counts[2], counts[3])

def arrangement_str(arr: Tuple[int, ...]) -> str:
    """Pretty-print arrangement as token chain."""
    return " → ".join(token_name(t) for t in arr)
