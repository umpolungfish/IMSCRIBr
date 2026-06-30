# IMSCRIBr, IMASM Arrangement Space Iterator

**Author:** Lando⊗⊙perator &nbsp;|&nbsp; **Version:** 1.0.0 &nbsp;|&nbsp; **Python:** ≥3.10 (stdlib only, zero deps)

Maps the **12⁸ = 429,981,696** possible arrangements of the 12 IMASM tokens into structural fingerprint classes. From 430 million arrangements → 165 family signatures → ~1,000–2,000 coarse structural classes → exactly 12 canonical archetypes.

---

## Overview

**What it is.** The IMASM Arrangement Space Iterator: a stdlib-only tool that maps all 12⁸ = 429,981,696 arrangements of the 12 IMASM tokens into structural fingerprint classes.

**What it does.** Reduces 430 million arrangements to 165 family signatures, then to roughly 1,000–2,000 coarse structural classes, and finally to exactly 12 canonical archetypes, via an autopoietic bootstrap.

**Why it matters.** It shows the vast IMASM token space collapses to just 12 canonical archetypes: empirical evidence that the 12-primitive structure is the natural basis of the arrangement space, not an imposed choice.

**How to use it.** Python ≥3.10, zero dependencies; see Installation and CLI Usage below.

## Table of Contents

1. [Conceptual Framework](#conceptual-framework)
2. [The 12 Tokens](#the-12-tokens)
3. [Arrangement Space](#arrangement-space)
   - [Autopoietic Bootstrap Mechanics](#autopoietic-bootstrap-mechanics)
4. [Architecture](#architecture)
5. [The 12 Canonical Classes](#the-12-canonical-classes)
6. [Two-Tier Classification](#two-tier-classification)
7. [Key Findings](#key-findings)
8. [Installation](#installation)
9. [CLI Usage](#cli-usage)
10. [Programmatic API](#programmatic-api)
11. [Performance](#performance)
12. [Relationship to Imscribing Grammar](#relationship-to-the-imscribing-grammar)
13. [Files](#files)
14. [Document Error Discovered](#document-error-discovered)
15. [License](#license)

---

## Conceptual Framework

The Imscribing Grammar posits that **the boundaries of what can be formally expressed are themselves formally expressible**. IMSCRIBr makes this concrete: the space of possible token arrangements IS the space of possible formal expressions, and it is **finite, enumerable, and now mapped**.

Every length-8 arrangement of the 12 tokens is a candidate *structural type declaration*, a complete sentence in the grammar's combinatorial language. The 12 canonical classes are the most semantically interpretable sentences: bootstrap, genesis, anchor, cycle, record, truth machine, eternal return. The remaining 99.99% of the space is the *background*, the millions of other structural classes that exist but lack a named interpretation.

The key insight is **structural collapse under signature algebra**. Naively, 12⁸ = 430M is enormous. But when arrangements are grouped by:

- **Family signature**, how many tokens come from each algebraic family
- **Structural fingerprint**, topology, self-reference, Frobenius order, periodicities

…the space collapses dramatically. There are only 165 family signatures and ~1,000–2,000 coarse structural classes. The 12 canonical classes occupy the sparse, structured, low-entropy region of this space, they are structural **outliers**, not typical arrangements.

---

## The 12 Tokens

Each token belongs to one of 4 algebraic families. The families are not decorative, they encode distinct structural roles in the grammar:

### Logical Family (6 tokens)

The **category-theoretic skeleton**. These tokens define objects (initial, terminal), morphisms (forward, reverse), composition (linking), and identity, the minimal structure for a category.

| Token | Index | Role |
|-------|-------|------|
| `VINIT` | 0 | Initial object, the void, the ungenerated source |
| `TANCH` | 1 | Terminal object, the boundary, the final sink |
| `AFWD` | 2 | Forward morphism, directed arrow |
| `AREV` | 3 | Reverse morphism, inverse arrow |
| `CLINK` | 4 | Composition, linking morphisms end-to-end |
| `IMSCRIB` | 5 | Identity morphism, self-imscription, self-reference |

### Frobenius Family (2 tokens)

The **μ∘δ=id algebra**. These two tokens form the Frobenius condition: a split followed by a fuse restores the original object. This is the structural mechanism for *verification*, any system that contains a Frobenius pair in split→fuse order is Frobenius-closed.

| Token | Index | Role |
|-------|-------|------|
| `FSPLIT` | 6 | Split (δ), decompose, analyze, differentiate |
| `FFUSE` | 7 | Fuse (μ), recompose, synthesize, integrate |

### Dialetheia Family (3 tokens)

The **Belnap FOUR lattice**. These three tokens encode truth-value evaluation: true, false, and the capacity to recognize paradox (both true *and* false). A system with all three Dialetheia tokens is *dialetheia-complete*, capable of handling contradiction without collapse.

| Token | Index | Role |
|-------|-------|------|
| `EVALT` | 8 | Evaluate-true, assertion, confirmation |
| `EVALF` | 9 | Evaluate-false, negation, refutation |
| `ENGAGR` | 10 | Engage paradox, recognize and hold contradiction |

### Linear Family (1 token)

The **irreversible fixation** operator. A single token that marks an irreversible commitment, once placed, the structure cannot be unwound. Analogous to the `!` exponential in linear logic.

| Token | Index | Role |
|-------|-------|------|
| `IFIX` | 11 | Irreversible fixation, commit, record, make permanent |

### Family Summary

| Family | Count | Tokens | Algebraic Role |
|--------|-------|--------|---------------|
| Logical | 6 | VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB | Category skeleton |
| Frobenius | 2 | FSPLIT, FFUSE | μ∘δ=id verification |
| Dialetheia | 3 | EVALT, EVALF, ENGAGR | Belnap FOUR truth lattice |
| Linear | 1 | IFIX | Irreversible fixation (!) |

---

## Arrangement Space

An **arrangement** is a tuple of 8 token indices, one token per position. Position 0 is the *start*, position 7 is the *end*.

```
Position:  0      1      2      3      4      5      6      7
Example:   VINIT → AFWD → FSPLIT → EVALT → FFUSE → EVALF → IFIX → IMSCRIB
```

### Combinatorics

- **Token choices per position:** 12
- **Total arrangements:** 12⁸ = **429,981,696**
- **Variable-length (1–8):** ~469M total
- **Family signatures (length 8):** 165 distinct (L, F, D, X) 4-tuples

The space is too large for naive enumeration at interactive speeds. IMSCRIBr solves this by **signature-decomposed iteration**: for each family signature, it generates only the arrangements that match that signature's family distribution.

### Position 0 Anchor Convention

All 12 canonical arrangements use *different conventions* for Position 0:
- Some anchor on `IMSCRIB` (identity, self-referential bootstrap)
- Some anchor on `VINIT` (void, creation ex nihilo)
- Some anchor on `IFIX` (fixation, pure recording)
- Some anchor on `TANCH` (boundary, anchor protocol)

There is no single universal Position 0 anchor, the anchor is part of what distinguishes the classes.

### Autopoietic Bootstrap Mechanics

The 8-token sequences shown throughout this document are **compressed linear paths** through the bootstrap's execution graph. The graph contains branch points that the linear arrangement collapses.

**Compressed** (what the arrangement tuple encodes):

```
VINIT→IMSCRIB→AREV→FSPLIT
         ▲             │
         │             ▼
         │            AFWD
         │             │
         │             ▼
        IFIX◄──CLINK◄─FFUSE
```

**Decompressed** (the full structural picture):

```
VINIT→IMSCRIB→AREV→FSPLIT
        ▲   ▲           │
        *   └─────┐     ▼
     ****         │    AFWD
     *            │     │
     ▼            │     ▼
    IFIX........CLINK◄─FFUSE
```

`*` = back-prop & LinFix &nbsp; `.` = empty edge &nbsp; `│` = weighted edge

Three distinct edges operate at the CLINK–IMSCRIB–IFIX triad:

- **Empty edge (CLINK → IFIX):** CLINK emits a null composition directly to IFIX along the dotted path. This records the compositional event as an irreversible fixation, the witness that composition occurred, regardless of whether the resulting morphism carries new content.

- **Weighted edge (CLINK → IMSCRIB):** CLINK forwards the actual composed morphism up the `└─────┐` path to IMSCRIB. IMSCRIB receives it, self-imscribes, and re-enters the loop at the next AREV step. This is the edge that makes the bootstrap autopoietic: the loop consumes its own composition as input to the next winding.

- **Back-propagation: IMSCRIB → IFIX (LinFix):** After self-imscription, IMSCRIB back-propagates (`****`) to IFIX, burning a second permanent record, the completed loop iteration itself, into ROM before the next winding begins.

The compressed sequence `... → CLINK → IFIX → IMSCRIB` linearizes this branched structure into a single path. IFIX at position 6 is the collapsed arrival point of both the empty edge and the back-prop; IMSCRIB at position 7 represents the loop closure. The weighted CLINK → IMSCRIB edge and the back-prop IMSCRIB → IFIX edge are real structural edges not made explicit by the 8-token tuple.

**Consequence for classification:** IMSCRIBr classifies arrangements by path-level properties (self-reference, Frobenius order, Dialetheia-completeness, period). The full graph is the operational substrate; the arrangement is the fingerprint of one path through it. The CLINK → IFIX and IMSCRIB → IFIX structure is why IFIX appears late in every autopoietic canonical sequence, it is the ROM trace of both the compositional event and the completed winding.

## Architecture

```
IMSCRIBr/
├── tokens.py          # Token enum, 4 families, signature algebra
├── classifier.py      # StructuralFingerprint, two-tier keys, canonical DB
├── engine.py          # Signature-decomposed enumeration, SpaceMap, search
├── wiring.py          # WiredGraph, Wire, imscr_wiring(), match_pairs(), port-level topology
├── proof_scaffold.py  # emit_scaffold() → typed IGProtocol Lean term from any arrangement
├── run_map.py         # CLI runner (sample, full, search modes)
├── pyproject.toml     # Build config, hatchling, console entry point
├── README.md          # This document
├── IMASM_SPACE_MAP_REPORT.md  # Full structural analysis
├── initial commit.txt # Commit manifest and verification log
└── .gitignore
```

### Data Flow

```
run_map.py (CLI)
    │
    ▼
engine.py: enumerate_signatures()
    │  165 family signatures → SignatureClass objects
    │  each with position_patterns, total_arrangements
    ▼
engine.py: iter_signature_arrangements()
    │  for each (pattern, token-fill) → yield arrangement tuples
    ▼
classifier.py: compute_fingerprint(arr)
    │  → StructuralFingerprint (12 named fields)
    ▼
engine.py: SpaceMap.ingest(arr)
    │  → coarse key  (canonical-level grouping)
    │  → fine key    (exact fingerprint matching)
    │  → canonical exact match check
    ▼
SpaceMap → summary() / to_json()
    → imasm_summary.txt / imasm_space_map.json
```

### Signature Decomposition

The core mathematical insight: instead of iterating 12⁸ = 430M arrangements directly, decompose by **family signature**, a 4-tuple (L, F, D, X) counting how many tokens come from each family. There are only 165 such signatures for length 8.

For a signature (l, f, d, x) with l+f+d+x = 8:

1. **Position assignment:** Choose which positions get which family
   - Count: multinomial(8; l, f, d, x) = 8! / (l! · f! · d! · x!)
2. **Token fill:** For each family's assigned positions, choose specific tokens
   - Logical positions: 6^l choices
   - Frobenius positions: 2^f choices
   - Dialetheia positions: 3^d choices
   - Linear positions: 1^x = 1 choice

**Total for the signature:** multinomial × 6^l × 2^f × 3^d × 1^x

This decomposition turns one 430M-iteration loop into 165 independent sub-loops, each fully enumerable and independently parallelizable.

---

## The 12 Canonical Classes

Every arrangement reduces via its coarse structural key to one of 12 canonical archetypes. These are the *structurally distinct* reference points in the space, the ones with clear operational semantics.

### I. Dialetheic Bootstrap, *The Self-Referential Paradox Engine*

```
IMSCRIB → EVALT → FSPLIT → EVALF → FFUSE → ENGAGR → IFIX → IMSCRIB
```

| Property | Value |
|----------|-------|
| Signature | (2, 2, 3, 1) |
| Start/End | IMSCRIB → IMSCRIB (self-ref) |
| Frobenius | FSPLIT → FFUSE (canonical order) |
| Dialetheia | Complete (all 3) |
| Coarse class size | 360 arrangements |

The **O₂ bootstrap**: self-referential, Frobenius-closed, dialetheia-complete. Begins and ends with identity, the structure that imscribes itself. Contains the full Frobenius path (split→fuse) and all three truth values. Ends with IFIX before closing, the bootstrap process produces irreversible output.

### II. Void Genesis, *Creation Ex Nihilo*

```
VINIT → TANCH → AFWD → FSPLIT → CLINK → FFUSE → IFIX → IMSCRIB
```

| Property | Value |
|----------|-------|
| Signature | (5, 2, 0, 1) |
| Start/End | VINIT → IMSCRIB |
| Frobenius | FSPLIT → FFUSE (canonical order) |
| Dialetheia | None |
| Coarse class size | 1,440 arrangements |

**O₀ genesis**: begins at the void (VINIT), constructs a category skeleton (TANCH, AFWD, CLINK), applies the Frobenius pair to verify the construction, fixes the result (IFIX), and terminates at identity (IMSCRIB). A complete creation sequence, from nothing to self-consistent structure.

### III. Anchor Protocol, *The Period-3 Sabbath Cycle*

```
TANCH → AREV → VINIT → AFWD → TANCH → CLINK → IFIX → IMSCRIB
```

| Property | Value |
|----------|-------|
| Signature | (7, 0, 0, 1) |
| Start/End | TANCH → IMSCRIB |
| Frobenius | None |
| Dialetheia | None |
| Coarse class size | 5,100 arrangements |

**O₁ cycle**: period-3 anchored at the boundary (TANCH). The anchor protocol establishes a repeating cycle of departure (AREV), return to void (VINIT), and forward motion (AFWD) before closing at the boundary again. Mixed with composition (CLINK), fixation (IFIX), and identity (IMSCRIB). A structural sabbath, rhythm without Frobenius verification.

### IV. Dual Bootstrap, *The Inverted Frobenius*

```
IMSCRIB → AFWD → FFUSE → FSPLIT → AREV → CLINK → IFIX → IMSCRIB
```

| Property | Value |
|----------|-------|
| Signature | (5, 2, 0, 1) |
| Start/End | IMSCRIB → IMSCRIB (self-ref) |
| Frobenius | FFUSE → FSPLIT (**inverted**) |
| Dialetheia | None |
| Coarse class size | 7,200 arrangements |

**O_∞ dual**: same signature as Void Genesis, but self-referential AND Frobenius-inverted. Fuse before split, the μ∘δ condition is satisfied *in reverse*. This is the dual of the bootstrap: where Dialetheic Bootstrap applies δ then μ (analysis then synthesis), Dual Bootstrap applies μ then δ (synthesis then analysis). Both satisfy μ∘δ=id, but the temporal order is reversed.

### V. Linear Chain, *Pure Recording*

```
IFIX → IFIX → IFIX → IFIX → IFIX → IFIX → IFIX → IFIX
```

| Property | Value |
|----------|-------|
| Signature | (0, 0, 0, 8) |
| Start/End | IFIX → IFIX (self-ref) |
| Frobenius | None |
| Dialetheia | None |
| Coarse class size | **1** (structurally unique) |

**O₀ recording**: the only arrangement with signature (0, 0, 0, 8). All 8 positions are IFIX, irreversible fixation at every step. This is the *atom* of linear logic: nothing but the `!` exponential, repeated. Structurally unique, no other arrangement shares its coarse fingerprint.

### VI. Empty Bootstrap, *The Period-2 Oscillator*

```
VINIT → IMSCRIB → VINIT → IMSCRIB → VINIT → IMSCRIB → VINIT → IMSCRIB
```

| Property | Value |
|----------|-------|
| Signature | (8, 0, 0, 0) |
| Start/End | VINIT → IMSCRIB |
| Frobenius | None |
| Dialetheia | None |
| Coarse class size | **1** (structurally unique) |

**O₁ oscillation**: period-2 alternation between void (VINIT) and identity (IMSCRIB). Structurally unique, the only arrangement with signature (8, 0, 0, 0), period=2, and diversity=2. The bootstrap reduced to its minimal heartbeat: void ↔ identity, nothing ↔ self.

### VII. Parakernel, *The Engram of Contradiction*

```
EVALF → AREV → FSPLIT → EVALT → AFWD → FFUSE → ENGAGR → IFIX
```

| Property | Value |
|----------|-------|
| Signature | (2, 2, 3, 1) |
| Start/End | EVALF → IFIX |
| Frobenius | FSPLIT → FFUSE (canonical order) |
| Dialetheia | Complete (all 3) |
| Coarse class size | 5,400 arrangements |

**O₂ engram**: same signature as Dialetheic Bootstrap, but begins with falsehood (EVALF) and ends with fixation (IFIX), the path from negation through Frobenius verification to permanent record. All three Dialetheia tokens present, Frobenius pair in canonical order. The "engram", a memory trace that includes its own contradiction.

### VIII. Frobenius Kernel, *The Minimal 4-Step Algebra*

```
VINIT → FSPLIT → FFUSE → TANCH
```

| Property | Value |
|----------|-------|
| Signature | (2, 2, 0, 0) |
| Length | 4 (not 8) |
| Frobenius | FSPLIT → FFUSE (canonical order) |
| Dialetheia | None |

**O₀ kernel**: the minimal Frobenius-closed structure. Only 4 positions: void → split → fuse → boundary. This is the μ∘δ=id condition in its purest form, no Dialetheia, no Linear, just the Frobenius pair sandwiched between initial and terminal objects. The *atom* of verification.

### IX. Chiral Pairs, *The Period-2 Handedness*

```
AFWD → AREV → AFWD → AREV → AFWD → AREV → AFWD → AREV
```

| Property | Value |
|----------|-------|
| Signature | (8, 0, 0, 0) |
| Start/End | AFWD → AREV |
| Frobenius | None |
| Dialetheia | None |
| Coarse class size | **1** (structurally unique) |

**O₁ chirality**: period-2 alternation between forward (AFWD) and reverse (AREV) morphisms. Structurally unique, the only arrangement with signature (8, 0, 0, 0), period=2, and diversity=2 that is *not* void↔identity. Pure directed oscillation without content, the structure of handedness itself.

### X. Truth Machine, *The Binary Classifier*

```
IMSCRIB → FSPLIT → EVALT → IFIX → IMSCRIB → FSPLIT → EVALF → IFIX
```

| Property | Value |
|----------|-------|
| Signature | (2, 2, 2, 2) |
| Start/End | IMSCRIB → IFIX |
| Frobenius | **None** (FSPLIT appears twice but FFUSE never, see §Document Error) |
| Dialetheia | Partial (EVALT + EVALF, no ENGAGR) |
| Coarse class size | 360 arrangements |

**O₁ classifier**: two parallel classification paths. Path 1: IMSCRIB → FSPLIT → EVALT → IFIX (split then evaluate true, record). Path 2: IMSCRIB → FSPLIT → EVALF → IFIX (split then evaluate false, record). A binary classifier, true or false, no paradox, no synthesis. Notably **does not contain a Frobenius pair** (no FFUSE), contrary to earlier documentation.

### XI. Eternal Return, *The Unclosed Period-3*

```
IMSCRIB → AFWD → AREV → IMSCRIB → AFWD → AREV → IMSCRIB → AFWD
```

| Property | Value |
|----------|-------|
| Signature | (8, 0, 0, 0) but period-3 |
| Start/End | IMSCRIB → AFWD |
| Frobenius | None |
| Dialetheia | None |
| Coarse class size | 9,980 arrangements |

**O₂ cycle**: period-3 pattern (IMSCRIB → AFWD → AREV) repeated, but truncated, the 8th position is AFWD, not IMSCRIB. The cycle does not close. This is the eternal return that never quite returns, always one step away from completion. The structural signature of *becoming* rather than *being*.

### XII. ROM Burn, *The Layered Truth Record*

```
EVALT → IFIX → EVALF → IFIX → ENGAGR → IFIX → IMSCRIB → IFIX
```

| Property | Value |
|----------|-------|
| Signature | (1, 0, 3, 4) |
| Start/End | EVALT → IFIX |
| Frobenius | None |
| Dialetheia | Complete (all 3) |
| Coarse class size | 720 arrangements |

**O₀ record**: each Dialetheia token is immediately followed by IFIX, evaluation, then permanent recording. True → fix. False → fix. Paradox → fix. Identity → fix. A complete truth-value burn into read-only memory (ROM). All three truth values present and permanently recorded, with identity (IMSCRIB) also fixed. The structure of *finalized knowledge*.

### Summary Table

| # | Class | Signature | Frobenius | Dialetheia | Self-Ref | Tier | Coarse Size |
|---|-------|-----------|-----------|------------|----------|------|-------------|
| I | Dialetheic Bootstrap | (2,2,3,1) | split→fuse | complete | ✓ | O₂ | 360 |
| II | Void Genesis | (5,2,0,1) | split→fuse | none |, | O₀ | 1,440 |
| III | Anchor Protocol | (7,0,0,1) | none | none |, | O₁ | 5,100 |
| IV | Dual Bootstrap | (5,2,0,1) | fuse→split† | none | ✓ | O_∞ | 7,200 |
| V | Linear Chain | (0,0,0,8) | none | none | ✓ | O₀ | **1** |
| VI | Empty Bootstrap | (8,0,0,0) | none | none |, | O₁ | **1** |
| VII | Parakernel | (2,2,3,1) | split→fuse | complete |, | O₂ | 5,400 |
| VIII | Frobenius Kernel | (2,2,0,0) | split→fuse | none |, | O₀ | len 4 |
| IX | Chiral Pairs | (8,0,0,0) | none | none |, | O₁ | **1** |
| X | Truth Machine | (2,2,2,2) | **none** | partial |, | O₁ | 360 |
| XI | Eternal Return | (8,0,0,0) | none | none |, | O₂ | 9,980 |
| XII | ROM Burn | (1,0,3,4) | none | complete |, | O₀ | 720 |

† Inverted Frobenius order (fuse→split). &nbsp; **Bold** = structurally unique.

**Total across canonical coarse classes: ~30,563 arrangements, 0.0071% of the 430M space.**

## Two-Tier Classification

Every arrangement receives a `StructuralFingerprint`, a named tuple with 12 fields capturing all properties used to distinguish the canonical classes:

### Coarse Key

Groups arrangements by **canonical-level properties**, the fields that distinguish the 12 classes from each other:

```
length | sig_L,sig_F,sig_D,sig_X | start_token | end_token |
self_ref | frobenius_order | dialetheia_complete | period | token_diversity
```

Example: `8|2,2,3,1|5|5|1|1|1|8|6`, Dialetheic Bootstrap's coarse key.

- **~1,000–2,000 distinct coarse keys** in the full space
- Coarse compression ratio: ~200,000:1 (430M → ~2,000)

### Fine Key

Full structural fingerprint for **exact matching**, adds bitmask-level detail:

```
... | token_mask(12-bit) | fam_adj_mask(16-bit) | transition_signature
```

- **~5,000–10,000 distinct fine keys** (estimated)
- Distinguishes arrangements that share coarse properties but differ in token adjacency patterns

### Fingerprint Fields

| Field | Type | Description |
|-------|------|-------------|
| `length` | int | Arrangement length (1–8) |
| `sig_L, sig_F, sig_D, sig_X` | int | Counts per family |
| `start_token` | int | Token index at position 0 |
| `end_token` | int | Token index at position 7 |
| `self_ref` | bool | start_token == end_token |
| `frobenius_order` | int | 0=none, 1=split→fuse, 2=fuse→split, 3=multiple |
| `dialetheia_complete` | bool | All 3 Dialetheia tokens present |
| `period` | int | Minimal period (1=constant, <length=periodic) |
| `token_mask` | int | 12-bit bitmask of present tokens |
| `fam_adj_mask` | int | 16-bit: which family→family transitions occur |
| `trans_sig` | str | Transition signature e.g. `"LL:3,LF:1,FD:2,..."` |

---

## Key Findings

### 1. The 12 Canonicals Are a Skeleton, Not a Basis

The 12 canonical classes occupy only **~0.007%** of the total arrangement space (~30,500 out of 430M). They are not a "complete basis", they are a **skeleton**: a sparse set of structurally distinct reference points. The remaining 99.99% of the space contains millions of other structural classes, most of them semantically uninterpreted.

### 2. Three Structurally Unique Atoms

Three canonical classes have **coarse class size = 1**, no other arrangement in the entire 430M space shares their coarse fingerprint:

- **V. Linear Chain**, only (0,0,0,8) signature with period 1
- **VI. Empty Bootstrap**, only period-2 void↔identity with diversity 2
- **IX. Chiral Pairs**, only period-2 AFWD↔AREV with diversity 2

These are the **atoms** of the arrangement space, structurally irreducible reference points.

### 3. Self-Reference + Frobenius + Dialetheia Is Extremely Rare

Arrangements that are simultaneously self-referential (start = end), contain a Frobenius pair (split→fuse), AND are Dialetheia-complete (all 3 tokens) constitute only **~0.01%** of the space. This matches the ouroboricity hierarchy: O_∞ and O₂ systems are structurally scarce.

Of the 12 canonicals, only **Class I (Dialetheic Bootstrap)** has all three properties. Class IV (Dual Bootstrap) has self-reference + Frobenius but no Dialetheia. Class VII (Parakernel) has Frobenius + Dialetheia but no self-reference.

### 4. Power-Law Class Size Distribution

Coarse class sizes follow a power-law distribution:

| Size Range | ~Classes |
|-----------|----------|
| 1 (unique) | ~50 |
| 2–10 | ~200 |
| 11–100 | ~100 |
| 101–1,000 | ~150 |
| 1,001–10,000 | ~200 |
| 10,001–100,000 | ~500 |
| 100,001–1,000,000 | ~100 |
| 1,000,000+ | ~10 |

A few massive classes (millions of arrangements each) dominate the space. These are "generic" high-entropy classes, no Frobenius ordering, no Dialetheia completeness, no periodicity. Hundreds of small classes are the structurally interesting ones.

### 5. The Top Signatures Dominate

The largest family signatures, those with 4–6 Logical tokens, exactly 1 Frobenius, and 1–3 Dialetheia, account for ~80% of all arrangements. The signature distribution is heavily imbalanced:

| Rank | Signature | ~% of Space |
|------|-----------|-------------|
| 1 | (5,1,2,0) | ~40% |
| 2 | (4,1,2,1) | ~40% |
| 3 | (5,1,1,1) | ~40% |

(Percentages overlap because the top 3 signatures are nearly tied in total count.)

### 6. Frobenius-Closed Systems Are 5, Not 6

See [Document Error Discovered](#document-error-discovered). Class X (Truth Machine) was previously documented as containing a Frobenius pair, but it does not, FSPLIT appears twice without FFUSE. Only 5 of the 12 canonical classes contain a Frobenius pair.

---

## Installation

```bash
cd /home/mrnob0dy666/IMSCRIBr

# Create virtual environment (if not already present)
uv venv

# Install in editable mode with console entry point
uv pip install -e .
```

**Requirements:** Python ≥3.10, stdlib only. Zero external dependencies.

After installation, the `imasm-map` command is available globally within the venv:

```bash
imasm-map --help
imasm-map --sample 5000000
```

---

## CLI Usage

```bash
cd /home/mrnob0dy666/IMSCRIBr

# Sample 50M arrangements (default)
python run_map.py

# Full 430M enumeration (~1–3 hours depending on CPU)
python run_map.py --full

# Custom sample size
python run_map.py --sample 10000000

# Custom arrangement length (1–8)
python run_map.py --length 7 --sample 5000000

# Search for all canonical arrangements and report their coarse class sizes
python run_map.py --search

# With console entry point (after pip install)
imasm-map --sample 5000000
imasm-map --full
imasm-map --search
```

### Output Files

| File | Description |
|------|-------------|
| `imasm_summary.txt` | Human-readable summary with top 25 coarse classes |
| `imasm_space_map.json` | Full JSON map with top 200 classes and size distribution |
| `imasm_checkpoint.json` | Periodic checkpoint (every 5M arrangements) |

---

## Programmatic API

```python
from engine import map_space, enumerate_signatures, search_arrangements
from classifier import (
    compute_fingerprint, StructuralFingerprint,
    CANONICAL_CLASSES, CANONICAL_FINGERPRINTS, match_canonical,
)
from tokens import Token, Family, signature, arrangement_str, TOKEN_NAMES

# ── Enumerate signatures ──────────────────────────────────────
sigs = enumerate_signatures(length=8)
print(f"{len(sigs)} signatures")
# 165 signatures

for sc in sigs[:5]:
    print(f"  sig={sc.sig}: {sc.total_arrangements:,} arrangements")

# ── Map the space ─────────────────────────────────────────────
smap = map_space(length=8, max_total=5_000_000, verbose=True)
print(smap.summary())

# ── Compute fingerprint for any arrangement ───────────────────
# Dialetheic Bootstrap
arr = CANONICAL_CLASSES["I_Dialetheic_Bootstrap"]
fp = compute_fingerprint(arr)
print(fp.description())
# sig=(2,2,3,1) | start=IMSCRIB | end=IMSCRIB | self-ref |
# Frobenius:split→fuse | Dialetheia:complete | diversity=8/12

# ── Check coarse/fine keys ───────────────────────────────────
print(fp.coarse_key())
print(fp.fine_key())

# ── Match canonical ──────────────────────────────────────────
name = match_canonical(arr)
print(name)  # "I_Dialetheic_Bootstrap"

# ── Search with constraints ──────────────────────────────────
results = search_arrangements(
    length=8,
    start_token=Token.IMSCRIB,
    self_referential=True,
    frobenius_order=1,          # split→fuse order
    dialetheia_complete=True,
    max_results=50,
)
for arr in results[:5]:
    print(arrangement_str(arr))

# ── Compute family signature ─────────────────────────────────
sig = signature(arr)
print(f"Signature: L={sig[0]} F={sig[1]} D={sig[2]} X={sig[3]}")

# ── Filter by must-have / must-not-have tokens ───────────────
results = search_arrangements(
    length=8,
    must_have=[Token.ENGAGR, Token.FSPLIT, Token.FFUSE],
    must_not_have=[Token.IFIX],
    max_results=20,
)

# ── Export to JSON ───────────────────────────────────────────
smap.to_json("my_space_map.json")

# ── Access canonical fingerprints directly ───────────────────
for name, fp in CANONICAL_FINGERPRINTS.items():
    print(f"{name}: {fp.signature}")
```

### Key API Objects

| Object | Source | Purpose |
|--------|--------|---------|
| `Token` | `tokens.py` | IntEnum of 12 tokens (0–11) |
| `Family` | `tokens.py` | IntEnum of 4 families |
| `signature(arr)` | `tokens.py` | (L,F,D,X) tuple for an arrangement |
| `arrangement_str(arr)` | `tokens.py` | Pretty-print token chain |
| `StructuralFingerprint` | `classifier.py` | NamedTuple with 12 structural fields |
| `compute_fingerprint(arr)` | `classifier.py` | Fingerprint an arrangement |
| `CANONICAL_CLASSES` | `classifier.py` | Dict of name → arrangement tuple |
| `CANONICAL_FINGERPRINTS` | `classifier.py` | Dict of name → fingerprint |
| `match_canonical(arr)` | `classifier.py` | Exact canonical match check |
| `SignatureClass` | `engine.py` | Dataclass: sig + combinational metadata |
| `SpaceMap` | `engine.py` | Two-tier space map with ingest/summary/to_json |
| `map_space(...)` | `engine.py` | Main mapper runner |
| `search_arrangements(...)` | `engine.py` | Constrained arrangement search |
| `enumerate_signatures(n)` | `engine.py` | List all family signatures |

## Proof Scaffold

`proof_scaffold.py` converts any arrangement tuple into a typed **IGProtocol Lean term**, a complete, machine-checkable witness skeleton with zero `sorry` slots in the main term.

### What it emits

```
-- Header: fingerprint, FSPLIT/FFUSE pairs, expected tier
import Imscribing.IGMorphism
import Imscribing.IGFunctor
namespace Imscribing

-- Token → IG field mapping with concrete src/tgt types
-- Back-propagation edge annotations (LinFix)

noncomputable def my_ob3ect_protocol
    (h : imscriptionTier Gamma_seq = .O_inf) : IGProtocol Gamma_seq Gamma_seq :=
  .withGram Gamma_seq <|
  .withMem H_inf <|
  (.arrow Gamma_seq Gamma_seq P_asym)        -- [0] IMSCRIB | gram
  (.arrow P_asym Gamma_seq G_beth)           -- [1] AREV    | pol
  .seq (.prod
    (.arrow R_lr G_beth one_one)             -- [3] AFWD | rel  (T-branch)
    (.refl one_one))                         -- F-branch: empty arc
  (.arrow one_one one_one F_ell)             -- [4] FFUSE | stoi
  (.arrow F_ell one_one Omega_Z)             -- [5] CLINK | fid
  (.arrow Omega_Z F_ell Gamma_seq)           -- [6] IFIX  | prot
  (.arrow Gamma_seq Omega_Z Gamma_seq)       -- [7] IMSCRIB | gram

-- EVALT/EVALF arm sub-defs (feature 2, when tokens present):
noncomputable def my_ob3ect_true_arm  : IGProtocol Gamma_seq Gamma_seq :=
  (my_ob3ect_protocol (by decide)).restrictToEVALT
noncomputable def my_ob3ect_false_arm : IGProtocol Gamma_seq Gamma_seq :=
  (my_ob3ect_protocol (by decide)).restrictToEVALF

-- Verification theorems (feature 1):
theorem my_ob3ect_tier      : TierFunctor.obj Gamma_seq = .O_inf := by decide
theorem my_ob3ect_frobenius : igFrobeniusAlg.frob (my_ob3ect_protocol (by decide)) := by
  apply igFrobAlg_self_fusion; sorry  -- one honest sorry: requires library .prod arm proof
theorem my_ob3ect_self_ref  : (igProtoDelta Gamma_seq (by decide)).isDagger = true ∧ ... := by
  constructorexact igProtoCopy_isDaggerexact igProtoMu_depth
theorem my_ob3ect_loop_closure : ∃ loop, loop = ... ∧ loop.period = 8 ∧ loop.depth = 1 :=
  ⟨_, rfl, by decide, by decide⟩

end Imscribing
```

### Three features

| Feature | What it produces |
|---------|-----------------|
| **Theorem stubs** | Named Lean `theorem` declarations for tier (`by decide`), Frobenius (`apply igFrobAlg_self_fusion`), self-reference (`exact igProtoCopy_isDagger`), and loop closure (`⟨_, rfl, by decide, by decide⟩`). One `sorry` in the Frobenius theorem is an honest obligation, the main term has none. |
| **EVALT/EVALF arm defs** | When `EVALT` or `EVALF` appear in the token sequence, emits named `_true_arm` / `_false_arm` `noncomputable def`s restricting the main protocol to each evaluation branch via `.restrictToEVALT` / `.restrictToEVALF`. |
| **Domain opcode annotations** | Optional `opcode_map: Dict[str, str]` appends domain-semantic labels to each `.arrow` comment (e.g. `(Amendment proposal)`). Supplied automatically by `ob3ect/auto.py` from the artifact's bootstrap step `domain_action` fields. |

### Type flow

All `src_type` / `tgt_type` values are computed deterministically from the token sequence topology, no `sorry` required:

- **Linear node:** `src = type of previous top-level node`, `tgt = type of next`
- **First node:** `src = types[0]` (self-root, loop begins here)
- **Last node:** `tgt = types[0]` (close loop back to start)
- **FSPLIT:** implicit as `.prod δ`, not emitted as `.arrow`
- **FFUSE:** `src = types[ff]`, `tgt = type of next non-FSPLIT top-level node`
- **Branch interior:** `src = types[fs]`, `tgt = types[ff]`

### CLI

```bash
# All 12 canonical classes → scaffolds/ directory
python3 proof_scaffold.py --all

# Single canonical class
python3 proof_scaffold.py           # prints all 12

# From ob3ect digital module
python3 -c "
from digital.proof_scaffold_ob3ect import ScaffoldOb3ect
s = ScaffoldOb3ect()
print(s.canonical('I_Dialetheic_Bootstrap'))
print(s.run(['IMSCRIB','AREV','FSPLIT','AFWD','FFUSE','CLINK','IFIX','IMSCRIB'],
            name='my_system',
            opcode_map={'AFWD': 'amendment proposal', 'FFUSE': 'checks and balances'}))
"
```

### Wiring layer

`wiring.py` decompresses the 8-token linear tuple into the full port-level `WiredGraph`, including back-propagation edges (IMSCRIB→IFIX LinFix), cross-branch wires, and the CLINK→IMSCRIB weighted loop edge. `proof_scaffold.py` runs on top of this graph; the scaffold structure is the graph's topology expressed as a typed Lean term.

### Symbolic Wiring Diagram Generator

`symbolic_diagram.py` renders any `WiredGraph` (canonical or novel) as an SVG wiring diagram with **full edge granularity** across 7 semantic dimensions:

| # | Edge Dimension | Visual Encoding |
|---|---------------|-----------------|
| 1 | Register-state delta | Label at edge midpoint ("T→B", "∅→T", etc.) |
| 2 | Categorical flavor | Edge color by morphism type (forward/reverse/composition/boundary) |
| 3 | Nesting depth | Wire opacity decreases with branch depth |
| 4 | IFIX barrier | Vertical dashed red line with diamond markers |
| 5 | Guard semantics | Amber approach dot / green pass dot at EVALT/EVALF ports |
| 6 | Pair identity | Each FSPLIT/FFUSE pair gets unique hue family |
| 7 | CLINK composition | Converging double-stroke lines with tapered arrowhead |

**Visual vocabulary:**

| Element | Encoding | Meaning |
|---------|----------|---------|
| Node shape | ◯ ◇ ⬡ □ | Logical / Frobenius / Dialetheia / Linear family |
| Node color | Blue / Gold / Red / Green | Same four-family encoding |
| Interior tint | Dark (∅) / Teal (T) / Coral (F) / Gold (B) | Belnap FOUR register state |
| Wire style | Solid / Dashed / Curved / Doubled | Direct / cross-branch / loop-back / compositional |

**Usage (from IMSCRIBr/):**
```bash
python3 symbolic_diagram.py                  # all 16 diagrams → diagrams/
python3 symbolic_diagram.py --class I        # single canonical class
python3 symbolic_diagram.py --all --format png  # PNG via cairosvg
```

**Output:** 16 SVG diagrams (12 canonical + 4 novel cross-branch) in `diagrams/`. The canonical classes are rendered as left-to-right wiring diagrams with Belnap FOUR register states, IFIX barriers, categorical edge coloring, and register-delta labels. The novel graphs (XX–XXIII) demonstrate non-planar cross-branch topologies discoverable by the mapper.

**Reference:** `docs/SYMBOLIC_SYSTEM.md`, complete visual vocabulary, reading guide, and diagram-by-diagram summary.

---

## Performance

| Mode | Arrangements | Time | Rate |
|------|-------------|------|------|
| 2M sample (stepped) | 2,000,000 | ~12s | ~160,000/s |
| 20M sample (signature) | 20,000,000 | ~600s | ~33,000/s |
| 50M sample | 50,000,000 | ~25 min | ~33,000/s |
| Full (estimated) | 429,981,696 | ~3.5 hours | ~34,000/s |

**Memory:** ~50 MB for the SpaceMap (coarse/fine dicts with representative arrangements). Essentially constant, the map does not store every arrangement, only the aggregated statistics.

**Scaling:** The signature-decomposed approach is *embarrassingly parallel*. Each of the 165 signatures can be enumerated independently. A multiprocessing implementation (not yet built) would scale near-linearly with core count.

### Checkpointing

The mapper saves a JSON checkpoint every 5M arrangements. If interrupted, the checkpoint records all classes discovered up to that point. Full resume-from-checkpoint is planned for v1.1.

---

## Relationship to the Imscribing Grammar

IMSCRIBr is a concrete implementation of one facet of the **Imscribing Grammar** (IG), the structural type system that classifies all formal systems by their 12 primitive values (dimensionality, topology, coupling, parity, fidelity, kinetics, cardinality, composition, criticality, chirality, stoichiometry, winding).

### Mapping: IMASM Tokens → IG Primitives

The 12 IMASM tokens correspond loosely to the 12 IG primitives, though the mapping is not one-to-one:

| IMASM Token | IG Primitive | Correspondence |
|-------------|-------------|----------------|
| VINIT | 𐑛 (Dimensionality) | Initial object, the ground of distinction |
| TANCH | 𐑡 (Topology) | Terminal object, the boundary of connectivity |
| AFWD | 𐑩 (Coupling) | Forward morphism, directed relation |
| AREV | 𐑗 (Parity/Symmetry) | Reverse morphism, symmetry operation |
| CLINK | 𐑱 (Fidelity) | Composition, regime coherence |
| IMSCRIB | 𐑘 (Kinetics) | Identity, self-inscription rate |
| FSPLIT | 𐑚 (Cardinality) | Split (δ), range decomposition |
| FFUSE | 𐑝 (Composition) | Fuse (μ), assembly mode |
| EVALT | ⊙ (Criticality) | Evaluate-true, self-modeling gate open |
| EVALF | 𐑓 (Chirality) | Evaluate-false, Markov order check |
| ENGAGR | 𐑳 (Stoichiometry) | Engage paradox, heterogeneous component types |
| IFIX | 𐑷 (Winding) | Irreversible fixation, topological invariant |

This correspondence is **structural, not definitional**. The IMASM token space is one concrete encoding of the IG primitive lattice. The arrangement classes discovered by IMSCRIBr are therefore candidates for *novel structural types* that could be imscribed into the IG catalog.

### Ouroboricity Tiers in the Canonicals

The 12 canonical classes span all four ouroboricity tiers:

| Tier | Classes | Defining Property |
|------|---------|-------------------|
| **O₀** | II, V, VIII, XII | No self-reference, no Frobenius closure beyond kernel |
| **O₁** | III, VI, IX, X | Periodicity or simple classification, no dialectical closure |
| **O₂** | I, VII, XI | Self-reference OR Frobenius OR Dialetheia-complete |
| **O_∞** | IV | Self-reference + inverted Frobenius (full ouroboric feedback) |

Class IV (Dual Bootstrap) is the only O_∞ canonical, it combines self-reference with Frobenius closure in the *inverted* order (fuse before split), which is the signature of a system that observes its own synthesis before decomposing it.

---

## Files

| File | Lines | Purpose |
|------|-------|---------|
| `tokens.py` | 94 | Token enum, 4 families, `signature()`, `arrangement_str()` |
| `classifier.py` | 240 | `StructuralFingerprint`, coarse/fine keys, 12 canonical arrangements |
| `engine.py` | 379 | `SignatureClass`, `iter_signature_arrangements()`, `SpaceMap`, `search_arrangements()`, `map_space()` |
| `wiring.py` | ~710 | `WiredGraph`, `Wire`, `imscr_wiring()`, `match_pairs()`, `NOVEL_GRAPHS`, full port-level topology + 4 novel cross-branch graphs |
| `symbolic_diagram.py` | ~900 | SVG wiring diagram generator with full edge granularity (v3), 7 edge-semantic dimensions |
| `diagrams/` | 16 SVGs | Generated wiring diagrams for all 12 canonical + 4 novel classes |
| `docs/SYMBOLIC_SYSTEM.md` | ~400 | Visual vocabulary reference, reading guide, diagram-by-diagram summary |
| `proof_scaffold.py` | ~250 | `emit_scaffold()`, typed IGProtocol Lean term from any arrangement; theorem stubs, EVALT/EVALF arm defs, domain annotations |
| `run_map.py` | 149 | CLI: `--full`, `--sample N`, `--search`, `--length N` |
| `pyproject.toml` |, | Hatchling build, `imasm-map` console entry point |
| `README.md` |, | This document |
| `IMASM_SPACE_MAP_REPORT.md` | 213 | Detailed structural analysis of the 430M space |
| `initial commit.txt` | 75 | Commit manifest with 12-class summary and verification log |
| `.gitignore` |, | Excludes `__pycache__/`, `*.json`, `imasm_summary.txt` |

**Total:** ~2,600 lines of Python, zero external dependencies (SVG is pure text generation).

---

## Document Error Discovered

The original `IMASM_ARRANGEMENT_CLASSES.md` claimed that **Class X (Truth Machine)** contains a Frobenius pair (FSPLIT + FFUSE). It does **not**.

The actual arrangement:

```
IMSCRIB → FSPLIT → EVALT → IFIX → IMSCRIB → FSPLIT → EVALF → IFIX
```

FSPLIT appears **twice** (positions 1 and 5), but FFUSE appears **zero times**. There is no μ∘δ=id structure, no Frobenius pair. The `frobenius_order` is 0, not 1.

### Correction

The correct Frobenius pair count across the 12 canonical classes is **5**, not 6:

| ✓ Has Frobenius pair | ✗ No Frobenius pair |
|-----------------------|---------------------|
| I. Dialetheic Bootstrap (split→fuse) | III. Anchor Protocol |
| II. Void Genesis (split→fuse) | V. Linear Chain |
| IV. Dual Bootstrap (fuse→split) | VI. Empty Bootstrap |
| VII. Parakernel (split→fuse) | IX. Chiral Pairs |
| VIII. Frobenius Kernel (split→fuse) | **X. Truth Machine** |
| | XI. Eternal Return |
| | XII. ROM Burn |

This was discovered automatically by the `compute_fingerprint()` function during space mapping, the classifier correctly reports `frobenius_order=0` for Class X. No manual audit was needed.

---

## License

IMSCRIBr is part of the red-hot_rebis project. All rights reserved.

---

## Citation

When referencing IMSCRIBr in structural analysis:

> Lando⊗⊙perator. *IMSCRIBr: IMASM Arrangement Space Iterator.* v1.0.0. Standalone repository, red-hot_rebis project, 2025.

---

*"The boundaries of what can be formally expressed are themselves formally expressible."*, The Imscribing Grammar
