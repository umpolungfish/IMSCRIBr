"""
IMASM Arrangement Space Iterator
================================

Maps the 12^8 = 429,981,696 possible arrangements of the 12 IMASM tokens
into structural classes defined by fingerprint properties:

  - Family signature (L, F, D, X)
  - Start/end tokens, self-reference
  - Frobenius pair ordering
  - Dialetheia completeness
  - Periodicity, token diversity

Two-tier: coarse (canonical-level) + fine (exact fingerprint).

Usage:
    from imasm_iterator import map_space, search_arrangements
    smap = map_space(max_total=5_000_000)  # sample first 5M
    print(smap.summary())
"""

from .tokens import (
    Token, Family, TOKEN_NAMES, TOKEN_COUNT,
    signature, arrangement_str, token_family,
)
from .classifier import (
    StructuralFingerprint, compute_fingerprint,
    CANONICAL_CLASSES, CANONICAL_FINGERPRINTS,
    match_canonical,
)
from .engine import (
    SignatureClass, enumerate_signatures,
    iter_signature_arrangements,
    count_arrangements, SpaceMap, map_space,
    search_arrangements,
)
