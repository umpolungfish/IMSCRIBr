"""
IMASM → IG STRUCTURAL BRIDGE
============================
Systematic mapping from IMASM arrangement fingerprints to Imscribing Grammar
(IG) structural types. Provides the bridge between the 430M arrangement space
and the 17.28M crystal of types.

Author: Lando⊗⊙perator
Version: 1.0.0 — June 2025
"""

from typing import Tuple, Dict, List
from classifier import (
    StructuralFingerprint, compute_fingerprint,
    CANONICAL_CLASSES, CANONICAL_FINGERPRINTS,
)


# ─── Fingerprint → IG Primitive Mapping ─────────────────────────

def fingerprint_to_ig(fp: StructuralFingerprint) -> Tuple[str, ...]:
    """Map a StructuralFingerprint to a 12-tuple of IG primitive values.

    Each fingerprint field maps to one IG primitive via a deterministic rule.
    The mapping is structural, not definitional — it captures the structural
    essence of the arrangement in the IG primitive language.

    Returns:
        (D, T, R, P, F, K, G, C, Phi, H, S, Omega) as Shavian glyph strings.
    """
    # D (Dimensionality): from token diversity
    d = fp.token_diversity
    D = ('𐑛' if d <= 2 else ('𐑨' if d <= 5 else ('𐑼' if d <= 9 else '𐑦')))

    # T (Topology): from self_ref + period + frobenius_order
    if fp.self_ref:
        T = '𐑸'
    elif fp.period == 1:
        T = '𐑡'
    elif fp.period == 2:
        T = '𐑥'
    elif fp.frobenius_order > 0:
        T = '𐑶'
    else:
        T = '𐑰'

    # R (Coupling): from frobenius_order
    R = ('𐑾' if fp.frobenius_order == 1 else
         ('𐑽' if fp.frobenius_order == 2 else
          ('𐑑' if fp.frobenius_order == 3 else '𐑩')))

    # P (Parity): from frobenius_order + dialetheia_complete
    if fp.frobenius_order == 1:
        P = '𐑹'
    elif fp.frobenius_order == 2:
        P = '𐑯'
    elif fp.frobenius_order == 3:
        P = '𐑬'
    elif fp.dialetheia_complete:
        P = '𐑿'
    else:
        P = '𐑗'

    # F (Fidelity): from dialetheia_complete + period
    if fp.dialetheia_complete:
        F = '𐑐'
    elif fp.period == 1:
        F = '𐑱'
    else:
        F = '𐑞'

    # K (Kinetics): from period + sig_X (IFIX count)
    sx = fp.sig_X
    if sx == 8:
        K = '𐑪'
    elif fp.period == 1:
        K = '𐑧'
    elif fp.period <= 2:
        K = '𐑤'
    elif fp.period <= 4:
        K = '𐑤'
    else:
        K = '𐑘'

    # G (Cardinality): from sig_X + token_diversity
    if sx >= 3:
        G = '𐑲'
    elif sx >= 1:
        G = '𐑔'
    elif fp.token_diversity <= 3:
        G = '𐑚'
    else:
        G = '𐑔'

    # C (Composition): from frobenius_order + period
    if fp.frobenius_order > 0:
        C = '𐑠'
    elif fp.period == 1:
        C = '𐑝'
    elif fp.period == 2:
        C = '𐑜'
    else:
        C = '𐑵'

    # Phi (Criticality): from self_ref + dialetheia_complete + period
    if fp.self_ref and fp.dialetheia_complete:
        Phi = '⊙'
    elif fp.self_ref:
        Phi = '𐑮'
    elif fp.dialetheia_complete:
        Phi = '𐑻'
    elif fp.period == 1:
        Phi = '𐑢'
    else:
        Phi = '𐑣'

    # H (Chirality): from period
    H = ('𐑓' if fp.period == 1 else
         ('𐑒' if fp.period == 2 else
          ('𐑖' if fp.period == 3 else '𐑫')))

    # S (Stoichiometry): from signature non-zero count
    nz = sum(1 for c in fp.signature if c > 0)
    S = ('𐑙' if nz == 1 else ('𐑕' if nz == 2 else '𐑳'))

    # Omega (Winding): from frobenius_order + self_ref + period
    if fp.frobenius_order == 1:
        Omega = '𐑭'
    elif fp.frobenius_order == 2:
        Omega = '𐑴'
    elif fp.self_ref:
        Omega = '𐑭'
    elif fp.period == 2:
        Omega = '𐑴'
    else:
        Omega = '𐑷'

    return (D, T, R, P, F, K, G, C, Phi, H, S, Omega)


# ─── Canonical IG types ──────────────────────────────────────────

def canonical_ig_types() -> Dict[str, Tuple[str, ...]]:
    """Return all distinct IG types for the 12 canonical arrangements.

    Note: IX_Chiral_Pairs and VI_Empty_Bootstrap map to the same IG type.
    Returns dict mapping canonical name → IG 12-tuple.
    """
    result = {}
    for name, fp in CANONICAL_FINGERPRINTS.items():
        result[name] = fingerprint_to_ig(fp)
    return result


def distinct_canonical_ig_types() -> Dict[Tuple[str, ...], List[str]]:
    """Return distinct IG types and which canonicals map to them."""
    from collections import defaultdict
    groups = defaultdict(list)
    for name, fp in CANONICAL_FINGERPRINTS.items():
        ig = fingerprint_to_ig(fp)
        groups[ig].append(name)
    return dict(groups)


# ─── Distance / comparison ───────────────────────────────────────

def ig_distance(ig_a: Tuple[str, ...], ig_b: Tuple[str, ...]) -> int:
    """Count of primitive mismatches between two IG tuples."""
    return sum(1 for a, b in zip(ig_a, ig_b) if a != b)


def ig_distance_matrix(
    ig_types: Dict[str, Tuple[str, ...]]
) -> Dict[str, Dict[str, int]]:
    """Compute pairwise distance matrix for a set of IG types."""
    names = sorted(ig_types.keys())
    matrix = {}
    for na in names:
        matrix[na] = {}
        for nb in names:
            matrix[na][nb] = ig_distance(ig_types[na], ig_types[nb])
    return matrix


# ─── Display utilities ───────────────────────────────────────────

PRIMITIVE_NAMES = ['D', 'T', 'R', 'P', 'F', 'K', 'G', 'C', 'Φ', 'H', 'S', 'Ω']

def ig_tuple_str(ig: Tuple[str, ...]) -> str:
    """Format an IG tuple for display: ⟨D · T · R · P · F · K · G · C · Φ · H · S · Ω⟩"""
    return '⟨' + ' · '.join(ig) + '⟩'


def describe_ig(ig: Tuple[str, ...]) -> str:
    """Return a one-line description of an IG tuple's key structural features."""
    parts = []
    if ig[8] == '⊙':
        parts.append('⊙-critical (self-modeling)')
    elif ig[8] == '𐑮':
        parts.append('self-reflective')
    elif ig[8] == '𐑻':
        parts.append('EP (paradox-capable)')
    if ig[3] == '𐑹':
        parts.append('Frobenius-special')
    elif ig[3] == '𐑯':
        parts.append('inverted-Frobenius')
    if ig[0] == '𐑛':
        parts.append('point-like')
    elif ig[0] == '𐑦':
        parts.append('holographic')
    return ', '.join(parts) if parts else 'generic'


# ─── CLI ─────────────────────────────────────────────────────────

if __name__ == '__main__':
    print("=" * 72)
    print("IMASM → IG STRUCTURAL BRIDGE")
    print("=" * 72)
    print()

    # Distinct types
    distinct = distinct_canonical_ig_types()
    print(f"12 canonicals → {len(distinct)} distinct IG types")
    print()

    for ig, names in sorted(distinct.items(), key=lambda x: -len(x[1])):
        label = " + ".join(n.split('_', 1)[1] for n in names)
        print(f"  {label}:")
        print(f"    {ig_tuple_str(ig)}")
        desc = describe_ig(ig)
        if desc:
            print(f"    [{desc}]")
        print()

    # Distance matrix
    print("=" * 72)
    print("INTER-CANONICAL DISTANCE MATRIX")
    print("=" * 72)
    igs = canonical_ig_types()
    matrix = ig_distance_matrix(igs)
    names = sorted(igs.keys())
    short = [n.split('_', 1)[1][:12] for n in names]

    # Header
    print(f"{'':20}", end='')
    for s in short:
        print(f"{s:>10}", end='')
    print()

    for ni, na in enumerate(names):
        print(f"{short[ni]:20}", end='')
        for nb in names:
            print(f"{matrix[na][nb]:>10}", end='')
        print()
