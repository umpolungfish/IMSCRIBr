"""
IMASM ARRANGEMENT SPACE ITERATOR ENGINE
Core iteration logic for mapping 12^8 = 429,981,696 arrangements.

Architecture:
  - Enumerates by family signature (165 distinct signatures for length 8)
  - Each signature decomposes into: position assignment × token assignment
  - Structural fingerprint computed per arrangement
  - Two-tier classification: coarse (canonical-level) + fine (exact fingerprint)
  - Supports checkpointing, multiprocessing
"""

import itertools
import json
import os
import time
import hashlib
from collections import defaultdict
from typing import Tuple, List, Dict, Iterator, Optional, Set
from dataclasses import dataclass, field

from tokens import (
    Token, Family, TOKEN_COUNT, FAMILY_SIZE, FAMILY_TOKENS,
    TOKEN_ARITY, TOKEN_BRANCH, FORK_TOKENS, JOIN_TOKENS,
    token_family, signature, arrangement_str, dag_str, TOKEN_NAMES,
)
from classifier import (
    StructuralFingerprint, compute_fingerprint,
    CANONICAL_CLASSES, CANONICAL_FINGERPRINTS, match_canonical,
)


# ─── Signature decomposition ────────────────────────────────────

@dataclass
class SignatureClass:
    """A family signature and its enumeration metadata."""
    sig: Tuple[int, int, int, int]  # (L, F, D, X)
    total_arrangements: int
    position_assignments: int
    token_fill_factor: int
    position_patterns: List[Tuple[int, ...]] = field(default_factory=list)


def enumerate_signatures(length: int = 8) -> List[SignatureClass]:
    """Enumerate all family signatures for arrangements of given length."""
    result = []
    for l in range(length + 1):
        for f in range(length + 1 - l):
            for d in range(length + 1 - l - f):
                x = length - l - f - d
                sig = (l, f, d, x)
                pos_assign = _multinomial(length, [l, f, d, x])
                fill = (6 ** l) * (2 ** f) * (3 ** d) * (1 ** x)
                total = pos_assign * fill
                patterns = list(_generate_position_patterns(length, l, f, d, x))
                sc = SignatureClass(
                    sig=sig,
                    total_arrangements=total,
                    position_assignments=pos_assign,
                    token_fill_factor=fill,
                    position_patterns=patterns,
                )
                result.append(sc)
    result.sort(key=lambda sc: -sc.total_arrangements)
    return result


def _multinomial(n: int, counts: List[int]) -> int:
    from math import factorial
    result = factorial(n)
    for c in counts:
        result //= factorial(c)
    return result


def _generate_position_patterns(
    n: int, l: int, f: int, d: int, x: int
) -> Iterator[Tuple[int, ...]]:
    positions = list(range(n))
    for log_pos in itertools.combinations(positions, l):
        remaining = [p for p in positions if p not in log_pos]
        for frob_pos in itertools.combinations(remaining, f):
            remaining2 = [p for p in remaining if p not in frob_pos]
            for dial_pos in itertools.combinations(remaining2, d):
                lin_pos = [p for p in remaining2 if p not in dial_pos]
                pattern = [0] * n
                for p in log_pos:
                    pattern[p] = 0
                for p in frob_pos:
                    pattern[p] = 1
                for p in dial_pos:
                    pattern[p] = 2
                for p in lin_pos:
                    pattern[p] = 3
                yield tuple(pattern)


# ─── Arrangement iterator ───────────────────────────────────────

def iter_signature_arrangements(sc: SignatureClass) -> Iterator[Tuple[int, ...]]:
    """Iterate all arrangements for a given signature class."""
    for pattern in sc.position_patterns:
        logical_indices = [i for i, fam in enumerate(pattern) if fam == 0]
        frob_indices = [i for i, fam in enumerate(pattern) if fam == 1]
        dial_indices = [i for i, fam in enumerate(pattern) if fam == 2]
        lin_indices = [i for i, fam in enumerate(pattern) if fam == 3]

        arr = [0] * 8
        for i in lin_indices:
            arr[i] = Token.IFIX

        log_tokens = [t.value for t in FAMILY_TOKENS[Family.LOGICAL]]
        frob_tokens = [t.value for t in FAMILY_TOKENS[Family.FROBENIUS]]
        dial_tokens = [t.value for t in FAMILY_TOKENS[Family.DIALETHEIA]]

        if not logical_indices and not frob_indices and not dial_indices:
            yield tuple(arr)
            continue

        iterators = []
        if logical_indices:
            iterators.append((logical_indices, log_tokens))
        if frob_indices:
            iterators.append((frob_indices, frob_tokens))
        if dial_indices:
            iterators.append((dial_indices, dial_tokens))

        yield from _product_assign(arr, iterators)


def _product_assign(
    base: List[int],
    families: List[Tuple[List[int], List[int]]],
) -> Iterator[Tuple[int, ...]]:
    if not families:
        yield tuple(base)
        return
    (indices, tokens), *rest = families
    arr = base.copy()
    n_indices = len(indices)
    for combo in itertools.product(tokens, repeat=n_indices):
        for idx, tok in zip(indices, combo):
            arr[idx] = tok
        if rest:
            yield from _product_assign(arr, rest)
        else:
            yield tuple(arr)


def count_arrangements(length: int = 8) -> int:
    """Count total arrangements (should equal 12^length)."""
    return 12 ** length


# ─── Space Mapper (two-tier) ────────────────────────────────────

@dataclass
class SpaceMap:
    """Result of mapping the arrangement space.

    Two-tier classification:
      - Coarse classes: grouped by canonical-level properties
      - Fine classes: grouped by full structural fingerprint
    """
    length: int
    total_enumerated: int = 0
    distinct_coarse: int = 0
    distinct_fine: int = 0
    # Coarse key -> aggregated info
    coarse_counts: Dict[str, int] = field(default_factory=dict)
    coarse_fingerprints: Dict[str, StructuralFingerprint] = field(default_factory=dict)
    coarse_reprs: Dict[str, Tuple[int, ...]] = field(default_factory=dict)
    # Fine key -> count
    fine_counts: Dict[str, int] = field(default_factory=dict)
    # Canonical matches found (exact)
    canonical_found: Set[str] = field(default_factory=set)
    # Canonical coarse matches
    canonical_coarse_hits: Dict[str, int] = field(default_factory=dict)

    def ingest(self, arr: Tuple[int, ...]) -> None:
        """Process one arrangement."""
        fp = compute_fingerprint(arr)
        ckey = fp.coarse_key()
        fkey = fp.fine_key()
        self.total_enumerated += 1

        # Coarse
        if ckey not in self.coarse_counts:
            self.coarse_counts[ckey] = 0
            self.coarse_fingerprints[ckey] = fp
            self.coarse_reprs[ckey] = arr
        self.coarse_counts[ckey] += 1

        # Fine
        self.fine_counts[fkey] = self.fine_counts.get(fkey, 0) + 1

        # Canonical exact
        canon = match_canonical(arr)
        if canon:
            self.canonical_found.add(canon)

    def finalize(self) -> None:
        """Compute derived statistics."""
        self.distinct_coarse = len(self.coarse_counts)
        self.distinct_fine = len(self.fine_counts)
        # Which canonical coarse keys appear in the space
        for name, canon_fp in CANONICAL_FINGERPRINTS.items():
            ck = canon_fp.coarse_key()
            if ck in self.coarse_counts:
                self.canonical_coarse_hits[name] = self.coarse_counts[ck]

    def summary(self) -> str:
        lines = []
        lines.append(f"=== IMASM ARRANGEMENT SPACE MAP (length={self.length}) ===")
        lines.append(f"Total enumerated:   {self.total_enumerated:>15,}")
        lines.append(f"Coarse classes:     {self.distinct_coarse:>15,}")
        lines.append(f"Fine classes:       {self.distinct_fine:>15,}")
        lines.append(f"Coarse compression: {self.total_enumerated/max(1,self.distinct_coarse):.0f}x")
        lines.append("")

        if self.canonical_found:
            lines.append(f"Canonical EXACT matches: {len(self.canonical_found)}/12")
        if self.canonical_coarse_hits:
            lines.append(f"Canonical COARSE matches: {len(self.canonical_coarse_hits)}/12")
            for name in sorted(self.canonical_coarse_hits.keys()):
                c = self.canonical_coarse_hits[name]
                lines.append(f"  {name}: {c:,} arrangements in coarse class")
        lines.append("")

        # Top coarse classes
        lines.append("TOP 25 COARSE CLASSES:")
        sorted_coarse = sorted(self.coarse_counts.items(), key=lambda x: -x[1])[:25]
        for i, (ck, count) in enumerate(sorted_coarse):
            fp = self.coarse_fingerprints[ck]
            rep = self.coarse_reprs[ck]
            lines.append(f"  #{i+1}: {count:>12,} | {fp.description()}")
            lines.append(f"         eg: {arrangement_str(rep)}")
        return "\n".join(lines)

    def to_json(self, path: str) -> None:
        data = {
            "length": self.length,
            "total_enumerated": self.total_enumerated,
            "distinct_coarse_classes": self.distinct_coarse,
            "distinct_fine_classes": self.distinct_fine,
            "canonical_exact_found": sorted(self.canonical_found),
            "canonical_coarse_hits": self.canonical_coarse_hits,
            "top_coarse_classes": [
                {
                    "count": count,
                    "fingerprint": self.coarse_fingerprints[ck].description(),
                    "representative": arrangement_str(self.coarse_reprs[ck]),
                }
                for ck, count in sorted(
                    self.coarse_counts.items(), key=lambda x: -x[1]
                )[:200]
            ],
            "coarse_size_distribution": _size_distribution(self.coarse_counts),
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)


def _size_distribution(counts: Dict[str, int]) -> Dict[str, int]:
    dist = {"1": 0, "2-10": 0, "11-100": 0, "101-1000": 0,
            "1001-10000": 0, "10001-100000": 0, "100001-1000000": 0, "1000001+": 0}
    for c in counts.values():
        if c == 1: dist["1"] += 1
        elif c <= 10: dist["2-10"] += 1
        elif c <= 100: dist["11-100"] += 1
        elif c <= 1000: dist["101-1000"] += 1
        elif c <= 10000: dist["1001-10000"] += 1
        elif c <= 100000: dist["10001-100000"] += 1
        elif c <= 1000000: dist["100001-1000000"] += 1
        else: dist["1000001+"] += 1
    return dist


# ─── Mapper Runner ──────────────────────────────────────────────

def map_space(
    length: int = 8,
    max_total: Optional[int] = None,
    checkpoint_interval: int = 5_000_000,
    checkpoint_path: Optional[str] = None,
    signatures: Optional[List[SignatureClass]] = None,
    verbose: bool = True,
) -> SpaceMap:
    if signatures is None:
        if verbose:
            print("Enumerating signatures...")
        signatures = enumerate_signatures(length)
        if verbose:
            total = sum(sc.total_arrangements for sc in signatures)
            print(f"  {len(signatures)} signatures, {total:,} total arrangements")

    smap = SpaceMap(length=length)
    total_count = 0
    t0 = time.time()
    last_checkpoint = 0
    last_coarse_count = 0

    for sci, sc in enumerate(signatures):
        if verbose:
            print(f"  Sig {sci+1}/{len(signatures)}: "
                  f"({sc.sig[0]},{sc.sig[1]},{sc.sig[2]},{sc.sig[3]}) "
                  f"→ {sc.total_arrangements:,} arrangements")

        for arr in iter_signature_arrangements(sc):
            smap.ingest(arr)
            total_count += 1

            if total_count % checkpoint_interval == 0 and total_count > last_checkpoint:
                last_checkpoint = total_count
                elapsed = time.time() - t0
                rate = total_count / elapsed if elapsed > 0 else 0
                new_coarse = smap.distinct_coarse - last_coarse_count
                last_coarse_count = smap.distinct_coarse
                if verbose:
                    print(f"    ... {total_count:,} ({rate:,.0f}/s), "
                          f"{smap.distinct_coarse} coarse (+{new_coarse}), "
                          f"{smap.distinct_fine} fine classes")
                if checkpoint_path:
                    smap.finalize()
                    smap.to_json(checkpoint_path)

            if max_total and total_count >= max_total:
                break

        if max_total and total_count >= max_total:
            break

    smap.finalize()
    elapsed = time.time() - t0
    if verbose:
        print(f"\nDone. {total_count:,} in {elapsed:.1f}s ({total_count/elapsed:,.0f}/s)")
    return smap


def search_cross_branch_wirings(
    length: int = 8,
    min_pairs: int = 2,
    max_variants: int = 6,
    max_results: int = 20,
) -> List[Tuple[Tuple[int, ...], list]]:
    """Find arrangements with >= min_pairs matched FSPLIT/FFUSE pairs and
    return their valid cross-branch wiring variants.

    Only arrangements with all-empty F-branches will yield valid variants —
    those are the ones where FSPLIT.F connects directly to matched FFUSE.F
    with no intermediate tokens on the F side.

    Scans all signatures with frob_count >= 2*min_pairs (need at least
    min_pairs FSPLITs and min_pairs FFUSEs) so min_pairs=2 requires f>=4.
    """
    from wiring import cross_wiring_variants, match_pairs
    results: List[Tuple[Tuple[int, ...], list]] = []
    sigs = enumerate_signatures(length)
    frob_floor = 2 * min_pairs  # each pair = 1 FSPLIT + 1 FFUSE

    for sc in sigs:
        if sc.sig[1] < frob_floor:  # not enough Frobenius tokens
            continue
        for arr in iter_signature_arrangements(sc):
            toks = tuple(Token(t) for t in arr)
            pairs = match_pairs(toks)
            if len(pairs) < min_pairs:
                continue
            variants = list(itertools.islice(cross_wiring_variants(toks), max_variants))
            if variants:
                results.append((arr, variants))
                if len(results) >= max_results:
                    return results
    return results


def search_arrangements(
    length: int = 8,
    signature_filter: Optional[Tuple[int,int,int,int]] = None,
    must_have: Optional[List[Token]] = None,
    must_not_have: Optional[List[Token]] = None,
    start_token: Optional[Token] = None,
    end_token: Optional[Token] = None,
    self_referential: Optional[bool] = None,
    frobenius_order: Optional[int] = None,
    dialetheia_complete: Optional[bool] = None,
    period: Optional[int] = None,
    max_results: int = 100,
) -> List[Tuple[int, ...]]:
    results = []
    signatures = enumerate_signatures(length)
    for sc in signatures:
        if signature_filter and sc.sig != signature_filter:
            continue
        for arr in iter_signature_arrangements(sc):
            if must_have and not all(t in arr for t in must_have):
                continue
            if must_not_have and any(t in arr for t in must_not_have):
                continue
            if start_token is not None and arr[0] != start_token:
                continue
            if end_token is not None and arr[-1] != end_token:
                continue
            fp = compute_fingerprint(arr)
            if self_referential is not None and fp.self_ref != self_referential:
                continue
            if frobenius_order is not None and fp.frobenius_order != frobenius_order:
                continue
            if dialetheia_complete is not None and fp.dialetheia_complete != dialetheia_complete:
                continue
            if period is not None and fp.period != period:
                continue
            results.append(arr)
            if len(results) >= max_results:
                return results
    return results
