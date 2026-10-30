#!/usr/bin/env python3
"""
voynich_morphology.py — Voynich Morphological Engine  [ob3ect-generated]

Implements morphological decomposition and generation for the EVA-encoded
Voynich manuscript, following the IMASM bootstrap sequence:
  VINIT → AFWD → FSPLIT → IMSCRIB → CLINK → FFUSE → EVALT

Core operations:
  1. Successor-variety segmentation: identify morpheme boundaries at
     transition-frequency minima within each word.
  2. Component inventory: frequency-ranked prefix, stem, suffix catalogs
     with positional constraints and co-occurrence statistics.
  3. Novel word generation: recombine attested components within
     grammatical constraints to produce words that structurally resemble
     Voynich morphology without being exact corpus copies.

Frobenius closure (μ∘δ=id):
  The component inventory + recombination rules regenerate the original
  corpus up to frequency matching. Words that cannot be decomposed (rare
  hapax legomena) are retained as atomic "frozen forms."

Author: Lando⊗⊙perator  (ob3ect: voynich_morphological_engine_segments_eva_words)
"""
from __future__ import annotations
from collections import Counter, defaultdict
from typing import NamedTuple
import random
import math


# ═══════════════════════════════════════════════════════════════════════════════
# MORPHOLOGICAL ANALYSIS  (δ — the split / FSPLIT arm)
# ═══════════════════════════════════════════════════════════════════════════════

class MorphInventory(NamedTuple):
    """Complete morphological inventory for a Voynich section."""
    prefixes: Counter       # (token1, token2) → freq — initial 1-2 glyphs
    stems:    Counter       # (token1, ..., tokenN) → freq — medial core
    suffixes: Counter       # (token1, token2) → freq — final 1-2 glyphs
    prefix_stem: dict       # prefix → Counter[stem] — co-occurrence
    stem_suffix: dict       # stem → Counter[suffix] — co-occurrence
    frozen:   Counter       # words that cannot be decomposed → freq
    prefix_tokens: list[int]  # tokens that can appear in prefix position
    stem_tokens:   list[int]  # tokens that can appear in stem position
    suffix_tokens: list[int]  # tokens that can appear in suffix position


def _successor_variety_best_split(
    word: list[int],
    min_stem_len: int = 1,
    max_prefix_len: int = 3,
    max_suffix_len: int = 3,
    bigram_counts: dict | None = None,
) -> tuple[int, int] | None:
    """Find best prefix-stem-suffix split points using transition-frequency minima.

    For each possible split point i (prefix boundary) and j (suffix boundary):
      - prefix = word[:i], stem = word[i:j], suffix = word[j:]
      - Score = -(transition frequency at boundary i) - (transition frequency at boundary j)
    Lower transition frequency = more likely morpheme boundary.

    Returns (prefix_end, suffix_start) or None if no valid split exists.
    """
    n = len(word)
    if n < 3:
        return None

    best_score = float('inf')
    best_split = None

    for i in range(1, min(max_prefix_len + 1, n - 1)):
        for j in range(max(i + min_stem_len, n - max_suffix_len), n):
            if j <= i:
                continue
            score = 0.0
            if bigram_counts and i < n:
                bigram_key = (word[i - 1], word[i])
                ct = bigram_counts.get(bigram_key, 0)
                score += 1.0 / (ct + 1)
            if bigram_counts and j < n:
                bigram_key = (word[j - 1], word[j])
                ct = bigram_counts.get(bigram_key, 0)
                score += 1.0 / (ct + 1)
            if score < best_score:
                best_score = score
                best_split = (i, j)

    return best_split


def analyze_morphology(
    words: list[list[int]],
    pos_freq: dict[str, Counter] | None = None,
    rng: random.Random | None = None,
) -> MorphInventory:
    """Analyze corpus words and build the morphological component inventory.

    This is the AFWD → FSPLIT → IMSCRIB sequence:
      AFWD:  successor variety analysis
      FSPLIT: divide words into prefix/stem/suffix
      IMSCRIB: preserve attested component identities

    Args:
        words: List of token-lists (each token-list is one word)
        pos_freq: Positional frequency dict (optional, for constraint checking)
        rng: Random state for tie-breaking

    Returns:
        MorphInventory with all component catalogs and co-occurrence stats
    """
    if rng is None:
        rng = random.Random(42)

    # Build global bigram counts for transition-frequency scoring
    bigram_counts: dict[tuple[int, int], int] = Counter()
    for w in words:
        for a, b in zip(w[:-1], w[1:]):
            bigram_counts[(a, b)] += 1

    # Build positional token sets
    all_initial: Counter = Counter()
    all_medial:  Counter = Counter()
    all_final:   Counter = Counter()
    if pos_freq:
        all_initial = pos_freq.get('initial', Counter())
        all_medial  = pos_freq.get('medial', Counter())
        all_final   = pos_freq.get('final', Counter())
    else:
        for w in words:
            if w:
                all_initial[w[0]] += 1
                all_final[w[-1]] += 1
                for t in w[1:-1]:
                    all_medial[t] += 1

    prefix_tokens_set = set(all_initial.keys())
    suffix_tokens_set = set(all_final.keys())
    stem_tokens_set   = set(all_medial.keys()) | prefix_tokens_set | suffix_tokens_set

    prefixes: Counter = Counter()
    stems:    Counter = Counter()
    suffixes: Counter = Counter()
    prefix_stem: dict = defaultdict(Counter)
    stem_suffix: dict = defaultdict(Counter)
    frozen: Counter = Counter()

    for w in words:
        n = len(w)
        if n < 2:
            frozen[tuple(w)] += 1
            continue

        split = _successor_variety_best_split(w, bigram_counts=bigram_counts)

        if split is None:
            frozen[tuple(w)] += 1
            continue

        i, j = split
        pfx = tuple(w[:i])   # prefix
        stm = tuple(w[i:j])  # stem
        sfx = tuple(w[j:])   # suffix

        # Validate positional constraints:
        # Prefix tokens should be in prefix_tokens_set (or at least initial-allowed)
        # Suffix tokens should be in suffix_tokens_set
        pfx_ok = all(t in prefix_tokens_set or t in stem_tokens_set for t in pfx) if pfx else True
        sfx_ok = all(t in suffix_tokens_set or t in stem_tokens_set for t in sfx) if sfx else True
        stm_ok = len(stm) >= 1

        if pfx_ok and sfx_ok and stm_ok:
            prefixes[pfx] += 1
            stems[stm] += 1
            suffixes[sfx] += 1
            if pfx and stm:
                prefix_stem[pfx][stm] += 1
            if stm and sfx:
                stem_suffix[stm][sfx] += 1
        else:
            frozen[tuple(w)] += 1

    return MorphInventory(
        prefixes=prefixes,
        stems=stems,
        suffixes=suffixes,
        prefix_stem=dict(prefix_stem),
        stem_suffix=dict(stem_suffix),
        frozen=frozen,
        prefix_tokens=sorted(prefix_tokens_set),
        stem_tokens=sorted(stem_tokens_set),
        suffix_tokens=sorted(suffix_tokens_set),
    )


# ═══════════════════════════════════════════════════════════════════════════════
# MORPHOLOGICAL GENERATION  (μ — the fuse / FFUSE arm)
# ═══════════════════════════════════════════════════════════════════════════════

def _sample_from_counter(
    cnt: Counter,
    rng: random.Random,
    min_count: int = 1,
) -> tuple | None:
    """Sample a key from a Counter weighted by frequency."""
    filtered = {k: v for k, v in cnt.items() if v >= min_count}
    if not filtered:
        return None
    keys, weights = zip(*filtered.items())
    total = sum(weights)
    probs = [w / total for w in weights]
    return keys[rng.choices(range(len(keys)), weights=probs, k=1)[0]]


def generate_morphological_word(
    inv: MorphInventory,
    rng: random.Random,
    target_len: int | None = None,
    frozen_fallback: bool = True,
) -> list[int] | None:
    """Generate a novel Voynich word by recombining morphological components.

    This is the CLINK → FFUSE → EVALT sequence:
      CLINK: positional constraint application
      FFUSE: recombine prefix+stem+suffix triplet
      EVALT: validate against statistical constraints

    Sampling strategy:
      1. With p_frozen probability, sample from frozen word list
      2. Otherwise, sample prefix, then stem conditioned on prefix,
         then suffix conditioned on stem
      3. Validate positional token constraints

    Args:
        inv: Morphological inventory from analyze_morphology()
        rng: Random state
        target_len: Approximate target word length (optional)
        frozen_fallback: If True, fall back to frozen words when
                         no valid combination is found

    Returns:
        List of token indices forming a valid Voynich word, or None
    """
    total_composable = sum(inv.prefixes.values()) + sum(inv.frozen.values())
    p_frozen = sum(inv.frozen.values()) / max(total_composable, 1)

    # Decide: frozen or composed?
    if rng.random() < p_frozen and inv.frozen:
        frozen_word = _sample_from_counter(inv.frozen, rng)
        if frozen_word is not None:
            return list(frozen_word)

    # Try recombination up to 20 attempts
    for _ in range(20):
        # Sample prefix
        prefix = _sample_from_counter(inv.prefixes, rng)
        if prefix is None:
            break

        # Sample stem conditioned on prefix (or unconditioned fallback)
        stem = None
        if prefix in inv.prefix_stem and inv.prefix_stem[prefix]:
            stem = _sample_from_counter(inv.prefix_stem[prefix], rng)
        if stem is None:
            stem = _sample_from_counter(inv.stems, rng)
        if stem is None:
            continue

        # Sample suffix conditioned on stem (or unconditioned fallback)
        suffix = None
        stem_key = stem
        if stem_key in inv.stem_suffix and inv.stem_suffix[stem_key]:
            suffix = _sample_from_counter(inv.stem_suffix[stem_key], rng)
        if suffix is None:
            suffix = _sample_from_counter(inv.suffixes, rng)
        if suffix is None:
            # Allow words with no suffix
            suffix = ()

        # Assemble
        word_tokens = list(prefix) + list(stem) + list(suffix)
        n = len(word_tokens)

        # Validate positional constraints
        if n < 2 or n > 15:
            continue
        if target_len is not None and abs(n - target_len) > 3:
            continue

        # Positional token constraints:
        # First token must be in prefix_tokens
        # Last token must be in suffix_tokens
        if word_tokens[0] not in inv.prefix_tokens and inv.prefix_tokens:
            continue
        if word_tokens[-1] not in inv.suffix_tokens and inv.suffix_tokens:
            continue

        return word_tokens

    # Fallback to frozen
    if frozen_fallback and inv.frozen:
        frozen_word = _sample_from_counter(inv.frozen, rng)
        if frozen_word is not None:
            return list(frozen_word)

    return None


# ═══════════════════════════════════════════════════════════════════════════════
# GENERATOR INTEGRATION  — replaces exact-word copying in pseudo_voynich.py
# ═══════════════════════════════════════════════════════════════════════════════

class MorphologicalGenerator:
    """Wraps MorphInventory for use in generate_section().

    Provides:
      - generate(): produce one novel word
      - frozen_set: set of frozen word tuples for recency matching
      - total_morph_types: number of distinct morphological word types
    """

    def __init__(self, words: list[list[int]], pos_freq: dict | None = None,
                 rng: random.Random | None = None):
        self.rng = rng or random.Random(42)
        self.inventory = analyze_morphology(words, pos_freq=pos_freq, rng=self.rng)
        self._words = words

        # Pre-compute frozen as a set for fast recency matching
        self.frozen_set: set[tuple] = set(self.inventory.frozen.keys())

        # Estimate number of possible morphological word types
        n_prefixes = len(self.inventory.prefixes)
        n_stems = len(self.inventory.stems)
        n_suffixes = max(len(self.inventory.suffixes), 1)
        self.total_morph_types = n_prefixes * n_stems * n_suffixes + len(self.inventory.frozen)

    def generate(self, target_len: int | None = None) -> list[int]:
        """Generate one novel Voynich word using morphological recombination."""
        word = generate_morphological_word(
            self.inventory, self.rng,
            target_len=target_len,
            frozen_fallback=True,
        )
        if word is None:
            # Absolute fallback: random word from corpus
            word = list(self.rng.choice(self._words))
        return word

    def generate_with_recency(
        self,
        target_len: int | None = None,
        recency_buffer: list[list[int]] | None = None,
        p_recency: float = 0.45,
    ) -> list[int]:
        """Generate a word with recency-biased sampling.

        Voynich has strong local word repetition. This blends:
          - p_recency: sample from recent words (with decay weighting)
          - p_morph: morphological generation
          - p_frozen: frozen word sampling
        """
        if recency_buffer and self.rng.random() < p_recency:
            n = len(recency_buffer)
            decay = 0.85
            weights = [decay ** (n - 1 - i) for i in range(n)]
            total_w = sum(weights)
            probs = [w / total_w for w in weights]
            idx = self.rng.choices(range(n), weights=probs, k=1)[0]
            return list(recency_buffer[idx])

        return self.generate(target_len=target_len)
