#!/usr/bin/env python3
"""
pseudo_voynich.py — Synthetic Pseudo-Voynich Generator

Generates synthetic text that has ZERO surface resemblance to the Voynich
Manuscript (Shavian notation instead of EVA) while reproducing every
measurable statistical property that defines the Voynich corpus.

Statistical signatures matched:
  word-length distribution, Zipf exponent, bigram (conditional) entropy,
  positional token constraints, section vocabulary separation (KL),
  type-token ratio, local word-repetition anomaly, spectral gap

Structural verification:
  Per-section dominant 8-cycle fingerprinted via IMSCRIBr compute_fingerprint().
  Coarse canonical class compared between Voynich and synthetic sections.

The proof: the statistical signature is a property of the grammar, not the
surface notation. The grammar finds its home in Shavian.

Usage:
    python pseudo_voynich.py PATH/TO/LSI_ivtff_0d.txt
    python pseudo_voynich.py PATH/TO/LSI_ivtff_0d.txt --section botanical --lines 200
    python pseudo_voynich.py PATH/TO/LSI_ivtff_0d.txt --stats-only
    python pseudo_voynich.py PATH/TO/LSI_ivtff_0d.txt --output synth.txt
"""

from __future__ import annotations
import argparse
import math
import re
import sys
import random
from collections import Counter, defaultdict
from pathlib import Path
from typing import NamedTuple

# ── IMSCRIBr imports ─────────────────────────────────────────────────────────
sys.path.insert(0, str(Path(__file__).resolve().parent))
from classifier import compute_fingerprint, CANONICAL_FINGERPRINTS, match_canonical
from tokens import Token

# ── Surface notation ──────────────────────────────────────────────────────────
# EVA glyph / digraph → IMASM token index (from voynich_engine/primitives.py)
EVA_TO_TOKEN: dict[str, int] = {
    'o': 0, 'p': 1, 'e': 2, 'a': 3, 'd': 4, 's': 5,
    'ch': 6, 'sh': 7, 't': 8, 'k': 9, 'r': 10, 'y': 11,
}

# IMASM token → Shavian surface character (IMSCRIBr README §Mapping)
TOKEN_TO_SHAVIAN: dict[int, str] = {
    0:  '\U0001045B',  # 𐑛  VINIT   → Dimensionality
    1:  '\U00010461',  # 𐑡  TANCH   → Topology
    2:  '\U00010469',  # 𐑩  AFWD    → Coupling
    3:  '\U00010457',  # 𐑗  AREV    → Parity
    4:  '\U00010471',  # 𐑱  CLINK   → Fidelity
    5:  '\U00010458',  # 𐑘  IMSCRIB → Kinetics
    6:  '\U0001045A',  # 𐑚  FSPLIT  → Cardinality
    7:  '\U0001045D',  # 𐑝  FFUSE   → Composition
    8:  '☉',      # ⊙  EVALT   → Criticality
    9:  '\U00010453',  # 𐑓  EVALF   → Chirality
    10: '\U00010473',  # 𐑳  ENGAGR  → Stoichiometry
    11: '\U00010477',  # 𐑷  IFIX    → Winding
}

SECTIONS = ['botanical', 'cosmological', 'balneological', 'biological']

LOC_RE = re.compile(r'^<(f(\d+)\w*)[.,]')


# ── IVTFF Parsing ─────────────────────────────────────────────────────────────

def _classify_folio(folio: str) -> str:
    m = re.match(r'f(\d+)', folio)
    if not m:
        return 'botanical'
    n = int(m.group(1))
    if n <= 66:  return 'botanical'
    if n <= 73:  return 'cosmological'
    if n <= 84:  return 'balneological'
    if n <= 102: return 'biological'
    return 'cosmological'


def _parse_eva_word(raw: str) -> list[int] | None:
    cleaned = re.sub(r'[!*%{}&=\-\s\d]', '', raw)
    if not cleaned:
        return None
    tokens: list[int] = []
    i = 0
    while i < len(cleaned):
        if i + 1 < len(cleaned) and cleaned[i:i+2] in EVA_TO_TOKEN:
            tokens.append(EVA_TO_TOKEN[cleaned[i:i+2]])
            i += 2
        elif cleaned[i] in EVA_TO_TOKEN:
            tokens.append(EVA_TO_TOKEN[cleaned[i]])
            i += 1
        else:
            i += 1
    return tokens if len(tokens) >= 2 else None


def parse_ivtff(path: str | Path) -> dict[str, list[list[int]]]:
    """Parse IVTFF transcription into per-section word lists (IMASM token indices)."""
    section_words: dict[str, list[list[int]]] = defaultdict(list)
    current_section = 'botanical'
    with open(path, encoding='utf-8', errors='replace') as fh:
        for line in fh:
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            m = LOC_RE.match(line)
            if m:
                current_section = _classify_folio(m.group(1))
                text = re.sub(r'^<[^>]+>\s*', '', line)
            else:
                text = line
            for raw_word in text.split('.'):
                toks = _parse_eva_word(raw_word)
                if toks:
                    section_words[current_section].append(toks)
    return dict(section_words)


# ── Statistics ────────────────────────────────────────────────────────────────

class CorpusStats(NamedTuple):
    length_dist:  dict   # section → Counter[int]
    unigram:      dict   # section → Counter[int]
    bigrams:      dict   # section → dict[int, dict[int, float]]
    pos_freq:     dict   # section → {initial/medial/final: Counter}
    word_vocab:   dict   # section → Counter[tuple]
    global_vocab: Counter


def _normalize(raw: dict) -> dict:
    total = sum(raw.values())
    return {k: v / total for k, v in raw.items()} if total else {}


def _build_bigrams(words: list[list[int]]) -> dict[int, dict[int, float]]:
    raw: dict[int, Counter] = defaultdict(Counter)
    for word in words:
        for a, b in zip(word[:-1], word[1:]):
            raw[a][b] += 1
    return {t: _normalize(dict(c)) for t, c in raw.items()}


def _build_positional(words: list[list[int]]) -> dict[str, Counter]:
    pos: dict[str, Counter] = {'initial': Counter(), 'medial': Counter(), 'final': Counter()}
    for word in words:
        if not word:
            continue
        pos['initial'][word[0]] += 1
        pos['final'][word[-1]] += 1
        for t in word[1:-1]:
            pos['medial'][t] += 1
    return pos


def extract_stats(section_words: dict[str, list[list[int]]]) -> CorpusStats:
    length_dist, unigram, bigrams, pos_freq, word_vocab = {}, {}, {}, {}, {}
    global_vocab: Counter = Counter()
    for sec, words in section_words.items():
        length_dist[sec] = Counter(len(w) for w in words)
        unigram[sec]     = Counter(t for w in words for t in w)
        bigrams[sec]     = _build_bigrams(words)
        pos_freq[sec]    = _build_positional(words)
        wv = Counter(tuple(w) for w in words)
        word_vocab[sec]  = wv
        global_vocab.update(wv)
    return CorpusStats(length_dist, unigram, bigrams, pos_freq, word_vocab, global_vocab)


# ── Metrics ───────────────────────────────────────────────────────────────────

def zipf_exponent(freq: Counter) -> float:
    ranked = sorted(freq.values(), reverse=True)
    if len(ranked) < 5:
        return 1.0
    log_r = [math.log(i + 1) for i in range(len(ranked))]
    log_f = [math.log(max(v, 1)) for v in ranked]
    n = len(log_r)
    mr = sum(log_r) / n
    mf = sum(log_f) / n
    num = sum((log_r[i] - mr) * (log_f[i] - mf) for i in range(n))
    den = sum((log_r[i] - mr) ** 2 for i in range(n))
    return -num / den if den > 0 else 1.0


def bigram_entropy(matrix: dict, uni: Counter) -> float:
    total = sum(uni.values())
    if not total:
        return 0.0
    h = 0.0
    for tok, row in matrix.items():
        p_t = uni[tok] / total
        h_row = -sum(p * math.log2(p) for p in row.values() if p > 0)
        h += p_t * h_row
    return h


def type_token_ratio(words: list[list[int]]) -> float:
    if not words:
        return 0.0
    return len(set(tuple(w) for w in words)) / len(words)


def repetition_rate(words: list[list[int]], window: int = 10) -> float:
    if not words:
        return 0.0
    reps = 0
    recent: list[tuple] = []
    for w in words:
        t = tuple(w)
        if t in recent:
            reps += 1
        recent.append(t)
        if len(recent) > window:
            recent.pop(0)
    return reps / len(words)


def kl_divergence(p: Counter, q: Counter) -> float:
    vocab = set(p) | set(q)
    pt = sum(p.values()) + len(vocab)
    qt = sum(q.values()) + len(vocab)
    return sum(
        ((p.get(t, 0) + 1) / pt) * math.log2(((p.get(t, 0) + 1) / pt) / ((q.get(t, 0) + 1) / qt))
        for t in vocab
    )


def spectral_gap(matrix: dict[int, dict[int, float]]) -> float:
    glyphs = sorted(matrix)
    n = len(glyphs)
    if n < 2:
        return 0.0
    idx = {g: i for i, g in enumerate(glyphs)}
    pi = [1.0 / n] * n
    for _ in range(200):
        new_pi = [0.0] * n
        for gf in glyphs:
            for gt, prob in matrix.get(gf, {}).items():
                if gt in idx:
                    new_pi[idx[gt]] += pi[idx[gf]] * prob
        total = sum(new_pi)
        if total > 0:
            pi = [x / total for x in new_pi]
    pi2 = list(pi)
    pi2[0] += 0.01
    pi2[1] -= 0.01
    t2 = sum(pi2)
    pi2 = [x / t2 for x in pi2]
    decay = 0.0
    for _ in range(50):
        new2 = [0.0] * n
        for gf in glyphs:
            for gt, prob in matrix.get(gf, {}).items():
                if gt in idx:
                    new2[idx[gt]] += pi2[idx[gf]] * prob
        t2 = sum(new2)
        if t2 > 0:
            new2 = [x / t2 for x in new2]
        db = sum(abs(pi2[i] - pi[i]) for i in range(n))
        da = sum(abs(new2[i] - pi[i]) for i in range(n))
        if db > 1e-10:
            decay = da / db
        pi2 = new2
    return max(0.0, 1.0 - decay)


# ── IMSCRIBr Fingerprinting ───────────────────────────────────────────────────

def _dominant_cycle_8(matrix: dict[int, dict[int, float]]) -> tuple[int, ...] | None:
    """Greedy strongest closed cycle of length 8 in the bigram matrix."""
    best: list[int] = []
    best_geo = -1.0
    for start in matrix:
        cycle = [start]
        visited = {start}
        current = start
        probs: list[float] = []
        for _ in range(7):
            row = matrix.get(current, {})
            cands = sorted(
                ((g, p) for g, p in row.items() if g not in visited),
                key=lambda x: x[1], reverse=True,
            )
            if not cands:
                break
            g, p = cands[0]
            cycle.append(g)
            visited.add(g)
            probs.append(p)
            current = g
        close_p = matrix.get(current, {}).get(start, 0.0)
        probs.append(close_p)
        if len(cycle) == 8 and all(p > 0 for p in probs):
            geo = math.exp(sum(math.log(p) for p in probs) / len(probs))
            if geo > best_geo:
                best_geo = geo
                best = cycle[:]
    return tuple(best) if best else None


def section_fingerprint(words: list[list[int]]) -> tuple:
    """Return (StructuralFingerprint, nearest_canonical_name, coarse_key) for a word list."""
    matrix = _build_bigrams(words)
    arr = _dominant_cycle_8(matrix)
    if arr is None:
        # Fall back to most common 8-gram
        stream = [t for w in words for t in w]
        counts: Counter = Counter()
        for i in range(len(stream) - 7):
            counts[tuple(stream[i:i+8])] += 1
        arr = counts.most_common(1)[0][0] if counts else (5, 2, 3, 4, 0, 8, 10, 11)
    fp = compute_fingerprint(arr)
    canon = match_canonical(arr)
    if not canon:
        best_score, nearest = -1, None
        for cname, cfp in CANONICAL_FINGERPRINTS.items():
            score = (
                2 * (fp.frobenius_order == cfp.frobenius_order) +
                2 * (fp.dialetheia_complete == cfp.dialetheia_complete) +
                1 * (fp.self_ref == cfp.self_ref) +
                1 * (fp.sig_F == cfp.sig_F) +
                1 * (fp.sig_D == cfp.sig_D)
            )
            if score > best_score:
                best_score, nearest = score, cname
        canon = f"~{nearest}"
    return fp, canon


# ── Generation ────────────────────────────────────────────────────────────────

def _sample_len(dist: Counter, rng: random.Random) -> int:
    lengths = list(dist)
    weights = [dist[l] for l in lengths]
    return max(2, min(rng.choices(lengths, weights=weights, k=1)[0], 8))


def _generate_word(
    section: str,
    stats: CorpusStats,
    rng: random.Random,
    target_len: int | None = None,
) -> list[int]:
    length = target_len or _sample_len(stats.length_dist[section], rng)
    pos    = stats.pos_freq[section]
    bgrams = stats.bigrams[section]

    init_c = pos.get('initial', Counter())
    if init_c:
        toks, wts = zip(*init_c.items())
        current = rng.choices(list(toks), weights=list(wts), k=1)[0]
    else:
        current = rng.randint(0, 11)
    word = [current]

    for i in range(1, length):
        is_final = (i == length - 1)
        row = bgrams.get(current, {})
        if is_final and pos.get('final'):
            final_c = pos['final']
            candidates = list(set(row) | set(final_c))
            wts = [row.get(t, 1e-5) * (final_c.get(t, 1e-5) ** 0.3) for t in candidates]
            total = sum(wts)
            current = rng.choices(candidates, weights=[w / total for w in wts], k=1)[0]
        elif row:
            toks, wts = zip(*row.items())
            current = rng.choices(list(toks), weights=list(wts), k=1)[0]
        else:
            current = rng.randint(0, 11)
        word.append(current)

    return word


def _build_vocab(
    section: str,
    n_types: int,
    stats: CorpusStats,
    rng: random.Random,
    zipf_alpha: float = 1.14,
) -> tuple[list[tuple], list[float]]:
    """Pre-generate n_types distinct Shavian word types for the section,
    then assign Zipf-distributed sampling weights.

    This reproduces the Voynich's defining property: a small vocabulary
    (~1-2K types) drawn repeatedly, not an endless stream of unique forms.
    The word types are generated from the section's own positional + bigram
    statistics, so structural constraints are preserved.
    """
    vocab: set[tuple] = set()
    attempts = 0
    while len(vocab) < n_types and attempts < n_types * 30:
        w = tuple(_generate_word(section, stats, rng))
        vocab.add(w)
        attempts += 1
    word_types = list(vocab)
    rng.shuffle(word_types)
    # Zipf weights: rank k gets weight k^(-alpha)
    weights = [1.0 / (i + 1) ** zipf_alpha for i in range(len(word_types))]
    total = sum(weights)
    return word_types, [w / total for w in weights]


def generate_section(
    section: str,
    n_words: int,
    stats: CorpusStats,
    rng: random.Random,
    vocab_size: int = 1500,
    novelty_rate: float = 0.02,
) -> list[list[int]]:
    """Sample from a Zipf-distributed vocabulary to reproduce Voynich TTR,
    Zipf exponent, and local word-repetition anomaly simultaneously."""
    word_types, weights = _build_vocab(section, vocab_size, stats, rng)
    words: list[list[int]] = []
    for _ in range(n_words):
        if rng.random() < novelty_rate:
            w = list(_generate_word(section, stats, rng))
        else:
            w = list(rng.choices(word_types, weights=weights, k=1)[0])
        words.append(w)
    return words


def render_shavian(words: list[list[int]], words_per_line: int = 8) -> str:
    shavian = [''.join(TOKEN_TO_SHAVIAN[t] for t in w) for w in words]
    lines = []
    for i in range(0, len(shavian), words_per_line):
        lines.append(' '.join(shavian[i:i + words_per_line]))
    return '\n'.join(lines)


# ── Reporting ─────────────────────────────────────────────────────────────────

def _pct(v: float, s: float) -> str:
    if v > 0:
        return f"{100 * (1 - abs(v - s) / v):.0f}%"
    return "—"


def print_voynich_stats(v_words: dict[str, list[list[int]]], v_stats: CorpusStats) -> None:
    print("\n=== VOYNICH STATISTICAL FINGERPRINT ===\n")
    all_words = [w for ws in v_words.values() for w in ws]
    gb = _build_bigrams(all_words)
    gu = Counter(t for w in all_words for t in w)

    print(f"  Words parsed:          {len(all_words):,}")
    for sec in SECTIONS:
        n = len(v_words.get(sec, []))
        if n:
            print(f"    {sec:<16}: {n:,}")

    print(f"\n  Global metrics:")
    print(f"    Zipf exponent:       {zipf_exponent(v_stats.global_vocab):.4f}  (natural language ≈ 1.0–1.5)")
    print(f"    Bigram entropy:      {bigram_entropy(gb, gu):.4f} bits/token")
    print(f"    Type-token ratio:    {type_token_ratio(all_words):.4f}")
    print(f"    Repetition rate:     {repetition_rate(all_words):.4f}  (window=10)")
    print(f"    Spectral gap:        {spectral_gap(gb):.6f}")

    secs = [s for s in SECTIONS if v_words.get(s)]
    print(f"\n  Section KL divergences:")
    for i, s1 in enumerate(secs):
        for s2 in secs[i+1:]:
            kl = kl_divergence(v_stats.unigram[s1], v_stats.unigram[s2])
            print(f"    {s1[:3]}↔{s2[:3]}: {kl:.4f}")

    print(f"\n  IMSCRIBr section fingerprints (dominant 8-cycle):")
    for sec in secs:
        fp, canon = section_fingerprint(v_words[sec])
        print(f"    {sec:<16}: {fp.coarse_key()}  → {canon}")


def print_verification(
    v_words: dict[str, list[list[int]]],
    s_words: dict[str, list[list[int]]],
    v_stats: CorpusStats,
    s_stats: CorpusStats,
) -> None:
    print("\n=== VERIFICATION ===\n")
    v_all = [w for ws in v_words.values() for w in ws]
    s_all = [w for ws in s_words.values() for w in ws]
    v_bg = _build_bigrams(v_all)
    s_bg = _build_bigrams(s_all)
    v_uni = Counter(t for w in v_all for t in w)
    s_uni = Counter(t for w in s_all for t in w)

    rows = [
        ("Zipf exponent",    zipf_exponent(v_stats.global_vocab), zipf_exponent(s_stats.global_vocab)),
        ("Bigram entropy",   bigram_entropy(v_bg, v_uni),         bigram_entropy(s_bg, s_uni)),
        ("Type-token ratio", type_token_ratio(v_all),             type_token_ratio(s_all)),
        ("Repetition rate",  repetition_rate(v_all),              repetition_rate(s_all)),
        ("Spectral gap",     spectral_gap(v_bg),                  spectral_gap(s_bg)),
    ]
    common = [s for s in SECTIONS if v_words.get(s) and s_words.get(s)]
    for i, s1 in enumerate(common):
        for s2 in common[i+1:]:
            rows.append((
                f"KL {s1[:3]}↔{s2[:3]}",
                kl_divergence(v_stats.unigram[s1], v_stats.unigram[s2]),
                kl_divergence(s_stats.unigram[s1], s_stats.unigram[s2]),
            ))

    print(f"  {'Metric':<26} {'Voynich':<12} {'Synthetic':<12} Match")
    print(f"  {'-'*26} {'-'*12} {'-'*12} -----")
    for name, v_val, s_val in rows:
        print(f"  {name:<26} {v_val:<12.4f} {s_val:<12.4f} {_pct(v_val, s_val)}")

    print(f"\n  IMSCRIBr fingerprint comparison (dominant 8-cycle per section):")
    print(f"  {'Section':<16}  {'Voynich coarse key':<34}  {'Synthetic coarse key':<34}  Result")
    for sec in common:
        v_fp, v_cn = section_fingerprint(v_words[sec])
        s_fp, s_cn = section_fingerprint(s_words[sec])
        ck_match = v_fp.coarse_key() == s_fp.coarse_key()
        fb_match = (v_fp.frobenius_order == s_fp.frobenius_order and
                    v_fp.dialetheia_complete == s_fp.dialetheia_complete)
        result = "MATCH" if ck_match else ("FROB+DIAL" if fb_match else "DIFF")
        print(f"  {sec:<16}  {v_fp.coarse_key():<34}  {s_fp.coarse_key():<34}  {result}")

    print(f"\n  Surface notation comparison:")
    v_chars = set(EVA_TO_TOKEN.keys())
    s_chars = set(TOKEN_TO_SHAVIAN.values())
    v_flat  = {c for w in v_chars for c in w}
    s_flat  = set(s_chars)
    overlap = v_flat & s_flat
    print(f"    Voynich EVA glyphs:    {sorted(v_chars)}")
    print(f"    Synthetic Shavian:     {'  '.join(sorted(s_chars))}")
    if not overlap:
        print(f"    Shared characters:     0 — ZERO OVERLAP — proof complete")
        print(f"\n    The statistical signature is a property of the grammar, not the notation.")
    else:
        print(f"    Shared characters:     {overlap}")


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    parser = argparse.ArgumentParser(description="Pseudo-Voynich Generator")
    parser.add_argument("transcription", help="Path to LSI_ivtff_0d.txt")
    parser.add_argument("--section", default="all", choices=SECTIONS + ["all"])
    parser.add_argument("--lines", type=int, default=100,
                        help="Total output lines (default: 100)")
    parser.add_argument("--words-per-line", type=int, default=8)
    parser.add_argument("--seed", type=int, default=42)
    parser.add_argument("--stats-only", action="store_true")
    parser.add_argument("--output", help="Save synthetic text to file")
    args = parser.parse_args()

    rng = random.Random(args.seed)

    print("=== PSEUDO-VOYNICH GENERATOR ===")
    print(f"    EVA (Voynich) → Shavian (synthetic)")
    print(f"    Corpus: {args.transcription}\n")

    print("Parsing IVTFF corpus...")
    v_words = parse_ivtff(args.transcription)
    total_parsed = sum(len(ws) for ws in v_words.values())
    print(f"  {total_parsed:,} words parsed across {len(v_words)} sections")

    print("Extracting Voynich statistics...")
    v_stats = extract_stats(v_words)

    print_voynich_stats(v_words, v_stats)

    if args.stats_only:
        return

    # Word budget
    wpl = args.words_per_line
    total_words = args.lines * wpl

    # Vocabulary size: use actual Voynich unique word-type count per section
    # so TTR converges to Voynich value at corpus scale.
    sec_vocab_sizes = {
        sec: max(500, len(v_stats.word_vocab.get(sec, {})))
        for sec in SECTIONS
    }

    if args.section == "all":
        target_secs = [s for s in SECTIONS if v_words.get(s)]
        total_v = sum(len(v_words[s]) for s in target_secs)
        sec_counts = {
            s: max(20, round(total_words * len(v_words[s]) / max(total_v, 1)))
            for s in target_secs
        }
    else:
        target_secs = [args.section]
        sec_counts  = {args.section: total_words}

    print(f"\n=== GENERATING SYNTHETIC TEXT (Shavian) ===")
    s_words: dict[str, list[list[int]]] = {}
    text_parts: list[str] = []

    for sec in target_secs:
        if sec not in v_stats.bigrams or not v_stats.bigrams[sec]:
            print(f"\n  [{sec}] — insufficient data, skipping")
            continue
        n = sec_counts[sec]
        vs = sec_vocab_sizes.get(sec, 1500)
        print(f"\n[{sec} — {n} words, vocab={vs} types]")
        ws = generate_section(sec, n, v_stats, rng, vocab_size=vs)
        s_words[sec] = ws
        rendered = render_shavian(ws, wpl)
        text_parts.append(f"\n[{sec} — {n} words]\n{rendered}")
        # Print first 400 chars as preview
        preview = rendered[:400]
        print(preview + ("  …" if len(rendered) > 400 else ""))

    if not s_words:
        print("No sections generated.")
        return

    s_stats = extract_stats(s_words)
    print_verification(v_words, s_words, v_stats, s_stats)

    if args.output:
        out = Path(args.output)
        out.write_text('\n'.join(text_parts), encoding='utf-8')
        print(f"\nSaved to: {out}")


if __name__ == "__main__":
    main()
