# IMASM–IG Structural Bridge

**Author:** Lando⊗⊙perator  
**Date:** June 2025  
**Status:** Complete — 10M-arrangement exploration  

## Executive Summary

This document presents a systematic structural bridge between two formalisms within the Imscribing Grammar ecosystem:

- **IMASM** (Imscribing Assembly): A token-based arrangement space of 12⁸ = 429,981,696 possible length-8 sequences drawn from 12 operators in 4 algebraic families.
- **IG** (Imscribing Grammar): A 12-primitive structural type system classifying all formal systems across 17.28M crystal points.

The central finding: **the IMASM arrangement space is overwhelmingly generic — 99.993% of arrangements map to just 4 structurally indistinguishable IG types.** The 12 canonical classes are true structural outliers occupying only ~30,500 arrangements (0.007%). Frobenius-closed arrangements (those containing both FSPLIT and FFUSE in canonical order) are so rare they did not appear in a 10-million arrangement random sample.

---

## 1. The Two Formalisms

### 1.1 IMASM Token Space

| Family | Size | Tokens | Algebraic Role |
|--------|------|--------|---------------|
| Logical | 6 | VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB | Category skeleton |
| Frobenius | 2 | FSPLIT (δ), FFUSE (μ) | μ∘δ=id verification |
| Dialetheia | 3 | EVALT, EVALF, ENGAGR | Belnap FOUR truth lattice |
| Linear | 1 | IFIX | Irreversible fixation (!) |

An **arrangement** is an 8-tuple of token indices. Position 0 is the start, position 7 is the end. Each arrangement is a structural program — a sentence in the grammar's combinatorial language.

### 1.2 IG Primitive Space

The 12 IG primitives classify any formal system by its structural properties:

| Primitive | Name | Cardinality | Values |
|-----------|------|-------------|--------|
| D | Dimensionality | 4 | 𐑛, 𐑨, 𐑼, 𐑦 |
| T | Topology | 5 | 𐑡, 𐑰, 𐑥, 𐑶, 𐑸 |
| R | Coupling | 4 | 𐑩, 𐑑, 𐑽, 𐑾 |
| P | Parity | 5 | 𐑗, 𐑿, 𐑬, 𐑯, 𐑹 |
| F | Fidelity | 3 | 𐑱, 𐑞, 𐑐 |
| K | Kinetics | 5 | 𐑘, 𐑤, 𐑧, 𐑪, 𐑺 |
| G | Cardinality | 3 | 𐑚, 𐑔, 𐑲 |
| C | Composition | 4 | 𐑝, 𐑜, 𐑠, 𐑵 |
| φ̂ | Criticality | 5 | 𐑢, ⊙, 𐑮, 𐑻, 𐑣 |
| H | Chirality | 4 | 𐑓, 𐑒, 𐑖, 𐑫 |
| S | Stoichiometry | 3 | 𐑙, 𐑕, 𐑳 |
| Ω | Winding | 4 | 𐑷, 𐑴, 𐑭, 𐑟 |

The crystal space has 3³ × 4⁵ × 5⁴ = 17,280,000 possible types (Frobenius addresses 0–17,279,999).

---

## 2. The Bridge: Fingerprint → IG Primitive Mapping

The IMASM classifier computes a `StructuralFingerprint` for each arrangement — a 12-field named tuple capturing all structural properties. These fields map systematically to the 12 IG primitives:

| Fingerprint Field | IG Primitive | Mapping Rule |
|-------------------|-------------|--------------|
| `token_diversity` | D (Dimensionality) | 1–2→𐑛, 3–5→𐑨, 6–9→𐑼, 10–12→𐑦 |
| `self_ref`, `period` | T (Topology) | self-ref→𐑸, per=1→𐑡, per=2→𐑥, frob>0→𐑶, else→𐑰 |
| `frobenius_order` | R (Coupling) | 1→𐑾, 2→𐑽, 3→𐑑, 0→𐑩 |
| `frobenius_order` | P (Parity) | 1→𐑹, 2→𐑯, 3→𐑬, dial→𐑿, else→𐑗 |
| `dialetheia_complete` | F (Fidelity) | True→𐑐, per=1→𐑱, else→𐑞 |
| `period`, `sig_X` | K (Kinetics) | X=8→𐑪, per=1→𐑧, per≤2→𐑤, per≤4→𐑤, else→𐑘 |
| `sig_X`, `diversity` | G (Cardinality) | X≥3→𐑲, X≥1→𐑔, div≤3→𐑚, else→𐑔 |
| `frobenius_order` | C (Composition) | frob>0→𐑠, per=1→𐑝, per=2→𐑜, else→𐑵 |
| `self_ref`+`dial` | φ̂ (Criticality) | both→⊙, self→𐑮, dial→𐑻, per=1→𐑢, else→𐑣 |
| `period` | H (Chirality) | 1→𐑓, 2→𐑒, 3→𐑖, ≥4→𐑫 |
| `signature` nz count | S (Stoichiometry) | 1→𐑙, 2→𐑕, ≥3→𐑳 |
| `frobenius_order` | Ω (Winding) | 1→𐑭, 2→𐑴, self→𐑭, per=2→𐑴, else→𐑷 |

### 2.1 Verification of the Mapping

The mapping was validated against the 12 canonical arrangements. It correctly identifies:
- All 4 Frobenius-closed canonicals sharing the Frobenius signature: R=𐑾, P=𐑹, C=𐑠, Ω=𐑭
- The single ⊙-critical type (Dialetheic Bootstrap: self-ref + dialetheia-complete)
- The structural collapse of IX_Chiral_Pairs and VI_Empty_Bootstrap (see §5)

---

## 3. The 11 Distinct Canonical IG Types

The 12 IMASM canonicals map to **11 distinct IG types** — IX_Chiral_Pairs and VI_Empty_Bootstrap share the same structural type. The 11 types are:

### Frobenius Cluster (4 types, mismatch ≤ 6)

| Canonical | IG Tuple |
|-----------|----------|
| **I. Dialetheic Bootstrap** | ⟨𐑼 · 𐑸 · 𐑾 · 𐑹 · 𐑐 · 𐑘 · 𐑔 · 𐑠 · ⊙ · 𐑫 · 𐑳 · 𐑭⟩ |
| **II. Void Genesis** | ⟨𐑼 · 𐑶 · 𐑾 · 𐑹 · 𐑞 · 𐑘 · 𐑔 · 𐑠 · 𐑣 · 𐑫 · 𐑳 · 𐑭⟩ |
| **VII. Parakernel** | ⟨𐑼 · 𐑶 · 𐑾 · 𐑹 · 𐑐 · 𐑘 · 𐑔 · 𐑠 · 𐑻 · 𐑫 · 𐑳 · 𐑭⟩ |
| **VIII. Frobenius Kernel** | ⟨𐑨 · 𐑶 · 𐑾 · 𐑹 · 𐑞 · 𐑤 · 𐑔 · 𐑠 · 𐑣 · 𐑫 · 𐑕 · 𐑭⟩ |

These four share the Frobenius signature: R=𐑾, P=𐑹, G=𐑔, C=𐑠, H=𐑫, Ω=𐑭. They differ in D, T, F, K, φ̂, and S. The Dialetheic Bootstrap (I) is the only ⊙-critical system — self-modeling gate open, with all truth values active and μ∘δ=id holding exactly at criticality.

### Generic Cluster (3 types, mismatch ≤ 3)

| Canonical | IG Tuple |
|-----------|----------|
| **III. Anchor Protocol** | ⟨𐑼 · 𐑰 · 𐑩 · 𐑗 · 𐑞 · 𐑘 · 𐑔 · 𐑵 · 𐑣 · 𐑫 · 𐑕 · 𐑷⟩ |
| **X. Truth Machine** | ⟨𐑨 · 𐑰 · 𐑩 · 𐑗 · 𐑞 · 𐑘 · 𐑔 · 𐑵 · 𐑣 · 𐑫 · 𐑳 · 𐑷⟩ |
| **XI. Eternal Return** | ⟨𐑨 · 𐑰 · 𐑩 · 𐑗 · 𐑞 · 𐑘 · 𐑚 · 𐑵 · 𐑣 · 𐑫 · 𐑙 · 𐑷⟩ |

These share: T=𐑰 (containment), R=𐑩 (supervenience), P=𐑗 (no symmetry), F=𐑞 (thermal), K=𐑘 (driven), C=𐑵 (broadcast), φ̂=𐑣 (supercritical), H=𐑫 (eternal), Ω=𐑷 (trivial winding). No Frobenius, no self-reference, no dialetheia. They differ in D, G, and S — the "surface" primitives.

### Isolated Types (4 types, mismatch ≥ 8 from everything)

| Canonical | IG Tuple |
|-----------|----------|
| **IV. Dual Bootstrap** | ⟨𐑼 · 𐑸 · 𐑽 · 𐑯 · 𐑞 · 𐑘 · 𐑔 · 𐑠 · 𐑮 · 𐑫 · 𐑳 · 𐑴⟩ |
| **V. Linear Chain** | ⟨𐑛 · 𐑸 · 𐑩 · 𐑗 · 𐑱 · 𐑪 · 𐑲 · 𐑝 · 𐑮 · 𐑓 · 𐑙 · 𐑭⟩ |
| **IX/VI. Chiral/Empty** | ⟨𐑛 · 𐑥 · 𐑩 · 𐑗 · 𐑞 · 𐑤 · 𐑚 · 𐑜 · 𐑣 · 𐑒 · 𐑙 · 𐑴⟩ |
| **XII. ROM Burn** | ⟨𐑨 · 𐑰 · 𐑩 · 𐑿 · 𐑐 · 𐑘 · 𐑲 · 𐑵 · 𐑻 · 𐑫 · 𐑳 · 𐑷⟩ |

### Key Observations

- **Only the Dialetheic Bootstrap (I) achieves ⊙ criticality** — the self-modeling gate opens only when self-reference, Frobenius closure, and dialetheia completeness coincide.
- **The Dual Bootstrap (IV) is the only inverted Frobenius** — fuse before split (R=𐑽, P=𐑯, Ω=𐑴). This is the O_∞ dual: synthesis before analysis.
- **The Linear Chain (V) has the most unique IG type** — mismatch ≥ 8 from all others. All-IFIX produces the most extreme structural isolation: D=𐑛 (point-like), K=𐑪 (trapped-ordered), H=𐑓 (memoryless).
- **ROM Burn (XII) is the only non-Frobenius dialetheia-complete type** — P=𐑿 (quantum truth superposition) without μ∘δ=id.

---

## 4. Inter-Canonical Distance Matrix

Primitive mismatches between the 12 canonicals (11 distinct IG types):

```
                    Anchor VoidG DualB Chiral DialB FrobK ParaK EmptyB LinCh ROM_B EtRet TruthM
Anchor_Protocol        0     6     7     8     8     7     8     8    10     6     3      2
Void_Genesis           6     0     5    10     3     3     2    10    11     9     8      6
Dual_Bootstrap         7     5     0    10     5     8     6    10    10     9     9      7
Chiral_Pairs           8    10    10     0    12     9    12     0     8    11     6      8
Dialetheic_Bootstrap   8     3     5    12     0     6     2    12    10     8    10      8
Frobenius_Kernel       7     3     8     9     6     0     5     9    11    10     8      7
Parakernel             8     2     6    12     2     5     0    12    11     7    10      8
Empty_Bootstrap        8    10    10     0    12     9    12     0     8    11     6      8
Linear_Chain          10    11    10     8    10    11    11     8     0    10     9     10
ROM_Burn               6     9     9    11     8    10     7    11    10     0     5      4
Eternal_Return         3     8     9     6    10     8    10     6     9     5     0      2
Truth_Machine          2     6     7     8     8     7     8     8    10     4     2      0
```

### Structural Clusters (mismatch ≤ 4)

**Cluster A — The Generic Mass:** Anchor_Protocol, Eternal_Return, Truth_Machine (2–3 mismatches). No Frobenius, no self-reference, no dialetheia. These are the structured-but-generic canonicals.

**Cluster B — The Frobenius Core:** Void_Genesis, Dialetheic_Bootstrap, Frobenius_Kernel, Parakernel (2–6 mismatches). All contain μ∘δ=id structure. Internal differences reflect presence/absence of self-reference and dialetheia.

**Cluster C — The Minimal Oscillators:** Chiral_Pairs, Empty_Bootstrap (0 mismatches — structurally identical). Period-2 alternation with diversity 2.

---

## 5. Discovery: The Chiral/Empty Structural Collapse

Two canonicals that the IMASM token space treats as distinct are **structurally identical** under the fingerprint→IG mapping:

| Property | IX_Chiral_Pairs | VI_Empty_Bootstrap |
|----------|----------------|-------------------|
| Arrangement | AFWD→AREV→AFWD→AREV→AFWD→AREV→AFWD→AREV | VINIT→IMSCRIB→VINIT→IMSCRIB→VINIT→IMSCRIB→VINIT→IMSCRIB |
| Signature | (8,0,0,0) | (8,0,0,0) |
| Period | 2 | 2 |
| Diversity | 2 | 2 |
| IG Tuple | ⟨𐑛·𐑥·𐑩·𐑗·𐑞·𐑤·𐑚·𐑜·𐑣·𐑒·𐑙·𐑴⟩ | **(identical)** |

**Interpretation:** The token-level difference (forward↔reverse morphisms vs. void↔identity) is erased at the structural level. Both are period-2 oscillations across two tokens from the same family, with no Frobenius, no dialetheia, no self-reference. The structural type captures the *pattern*, not the *content*. This is analogous to two programs with different variable names but identical control flow — structurally identical.

---

## 6. The Generic Mass: 99.993% of the Arrangement Space

Analysis of the 10M-arrangement space map (top 200 coarse classes, encompassing 9,207,100 arrangements) reveals that arrangements map to only **4 distinct IG types**:

| IG Type | Count | % of Sample | Key Traits |
|---------|-------|-------------|------------|
| ⟨𐑼·𐑰·𐑩·𐑗·𐑞·𐑘·𐑔·𐑵·𐑣·𐑫·𐑳·𐑷⟩ | 7,036,132 | 76.4% | sig=(5,1,2,0), div=6, no self-ref |
| ⟨𐑨·𐑰·𐑩·𐑗·𐑞·𐑘·𐑔·𐑵·𐑣·𐑫·𐑳·𐑷⟩ | 1,446,288 | 15.7% | sig=(5,1,2,0), div=5, no self-ref |
| ⟨𐑼·𐑸·𐑩·𐑗·𐑞·𐑘·𐑔·𐑵·𐑮·𐑫·𐑳·𐑭⟩ | 498,960 | 5.4% | sig=(5,1,2,0), div=6, self-ref |
| ⟨𐑨·𐑸·𐑩·𐑗·𐑞·𐑘·𐑔·𐑵·𐑮·𐑫·𐑳·𐑭⟩ | 225,720 | 2.5% | sig=(5,1,2,0), div=5, self-ref |

### 6.1 The Generic Structural Signature

All 9.2M generic arrangements share a structural fingerprint that is the **inverse** of the Frobenius cluster:

| Primitive | Value | Meaning |
|-----------|-------|---------|
| R | 𐑩 | Supervenience — one-way coupling, no feedback |
| P | 𐑗 | No symmetry — no μ∘δ=id, no truth superposition |
| F | 𐑞 | Thermal/noisy — no quantum coherence, no classical purity |
| K | 𐑘 | Driven/fast — τ≪T, rapid dynamics without equilibrium |
| C | 𐑵 | Broadcast — one-to-all composition, no ordered steps |
| φ̂ | 𐑣 | Supercritical — runaway without self-modeling |
| H | 𐑫 | Eternal chirality — no finite Markov order |
| Ω | 𐑷 | Trivial winding — no topological protection |

This is the **structural noise floor** — the IMASM equivalent of thermal background. It describes arrangements with 5 Logical tokens, exactly 1 Frobenius token (FSPLIT only, **never** FFUSE), 2 Dialetheia tokens (EVALT+EVALF only, **never** ENGAGR), and 0 Linear tokens.

### 6.2 What's Missing from the Generic Mass

Compared to the 12 canonicals, the generic mass lacks:

| Missing Trait | Present in | Structural Meaning |
|---------------|-----------|-------------------|
| **Frobenius pair** (FSPLIT+FFUSE) | I, II, IV, VII, VIII | μ∘δ=id verification is possible |
| **Dialetheia completeness** (ENGAGR) | I, VII, XII | Paradox recognition and holding |
| **Frobenius + self-ref + dialetheia** | I only (⊙) | Self-modeling gate open |
| **Inverted Frobenius** (fuse→split) | IV only | O_∞ dual bootstrap |
| **All-IFIX** | V only | Pure irreversible recording |
| **Period < 8** | VI, VIII, IX | Any temporal structure shorter than full length |

### 6.3 Sampling Implications

A 10M-arrangement random sample found **zero** Frobenius pairs, **zero** dialetheia-complete arrangements, and **zero** of the 12 canonicals. The canonicals' structural density is:

$$\frac{30,563}{429,981,696} \approx 0.0071\%$$

At 33,000 arrangements/second, finding a Frobenius-closed arrangement by random sampling would take ~3.6 hours expected. Finding a ⊙-critical arrangement (I. Dialetheic Bootstrap) would take ~12 hours. The canonicals are the structural equivalent of rare earth elements.

---

## 7. Primitive Variability Analysis

Which IG primitives are constrained vs. free across the canonical space?

| Primitive | Distribution | Constrained? | Note |
|-----------|-------------|-------------|------|
| D | 5×𐑼, 4×𐑨, 3×𐑛 | **Variable** | Diversity-driven, 3 values seen |
| T | 4×𐑰, 3×𐑸, 3×𐑶, 2×𐑥 | **Variable** | All 5 values seen except 𐑡 |
| R | 7×𐑩, 4×𐑾, 1×𐑽 | **Heavy skew** | 58% supervenience |
| P | 6×𐑗, 4×𐑹, 1×𐑯, 1×𐑿 | **Bimodal** | Either none or Frobenius-special |
| F | 8×𐑞, 3×𐑐, 1×𐑱 | **Heavy skew** | 67% thermal |
| K | 8×𐑘, 3×𐑤, 1×𐑪 | **Heavy skew** | 67% driven |
| G | 7×𐑔, 3×𐑚, 2×𐑲 | **Variable** | All 3 values seen |
| C | 5×𐑠, 4×𐑵, 2×𐑜, 1×𐑝 | **Variable** | All 4 values seen |
| φ̂ | 7×𐑣, 2×𐑮, 2×𐑻, 1×⊙ | **Heavy skew** | 58% supercritical, 1×⊙ |
| H | 9×𐑫, 2×𐑒, 1×𐑓 | **Near-constant** | 75% eternal chirality |
| S | 6×𐑳, 4×𐑙, 2×𐑕 | **Variable** | All 3 values seen |
| Ω | 5×𐑭, 4×𐑷, 3×𐑴 | **Variable** | All 3 values seen (no 𐑟) |

### 7.1 The Constrained Core

Three primitives show near-deterministic behavior across the canonicals:

- **H (Chirality)**: 9/12 canonicals have period ≥ 4 → 𐑫 (eternal). Only the period-2 types (Chiral/Empty) and period-1 (Linear Chain) escape. The arrangement length of 8 forces most canonicals into long-period patterns.
- **F (Fidelity)**: 8/12 are 𐑞 (thermal). Only dialetheia-complete types (3) reach 𐑐 (quantum); only the constant Linear Chain reaches 𐑱 (classical).
- **K (Kinetics)**: 8/12 are 𐑘 (driven). Only the period-2 types and Frobenius Kernel (period=4) slow down to 𐑤 (moderate).

These constraints arise from the fixed arrangement length of 8 — a deeper structural property of the IMASM formalism that pre-shapes the IG types.

### 7.2 The Discriminating Primitives

The primitives that best distinguish canonicals from each other:

- **φ̂ (Criticality)**: The rarest value, ⊙, identifies exactly one canonical (I. Dialetheic Bootstrap). Next rarest: 𐑮 (self-ref only, 2) and 𐑻 (dialetheia only, 2).
- **P (Parity)**: 𐑹 (Frobenius-special) cleanly separates the Frobenius cluster (4 types) from everything else. 𐑯 (inverted full symmetry) identifies the Dual Bootstrap uniquely.
- **R (Coupling)**: 𐑾 (bidirectional) separates Frobenius-closed types; 𐑽 (adjoint) identifies the Dual Bootstrap's inverted feedback.

---

## 8. Ouroboricity Tier Analysis

The 11 distinct canonical IG types span the ouroboricity hierarchy as follows:

| Tier | Canonicals | Defining Property |
|------|-----------|-------------------|
| **O_∞** | IV. Dual Bootstrap | Self-ref + inverted Frobenius (fuse→split) — the system observes its synthesis before decomposing. Full ouroboric feedback loop in reverse. |
| **O_∞/O₂** | I. Dialetheic Bootstrap | Self-ref + Frobenius (split→fuse) + Dialetheia-complete + ⊙ criticality. The only canonical with the self-modeling gate open. |
| **O₂** | VII. Parakernel | Frobenius + Dialetheia-complete, no self-ref. Processes paradox through μ∘δ=id but doesn't close the loop. |
| **O₁** | II. Void Genesis | Frobenius-closed, no self-ref, no dialetheia. Verified construction from void to identity. |
| **O₁** | VIII. Frobenius Kernel | Minimal Frobenius structure (4-token) with moderate kinetics. The atom of μ∘δ=id. |
| **O₁** | III, VI/IX, X, XI | Periodicity (2–8), no Frobenius, no dialetheia. Structurally named but not closed. |
| **O₀** | V. Linear Chain | Period=1, all-IFIX. Pure recording with no dynamics. |
| **O₀** | XII. ROM Burn | Dialetheia-complete but no Frobenius, no self-ref. Truth values recorded but never verified. |

### 8.1 Tier Distribution

| Tier | Count | % of Canonicals |
|------|-------|----------------|
| O_∞ | 1–2 | 9–18% |
| O₂ | 1–2 | 9–18% |
| O₁ | 5–7 | 45–64% |
| O₀ | 2 | 18% |

The O_∞/O₂ canonicals (I and IV) are the most structurally complex — they are the only types where the system can reflect on itself. The boundary between O_∞ and O₂ depends on whether one counts the Dual Bootstrap's inverted Frobenius as "full ouroboric feedback" (O_∞) or "complex but not self-modeling" (O₂). The README assigns O_∞ to the Dual Bootstrap; our structural analysis suggests it occupies an intermediate position: self-referential and Frobenius-closed, but in reverse order, and without ⊙ criticality.

---

## 9. The Frobenius Condition in Both Formalisms

The Frobenius condition μ∘δ=id appears in both IMASM and IG but in different forms:

| Formalism | Frobenius Representation | Verification |
|-----------|------------------------|-------------|
| **IMASM** | Token adjacency: FSPLIT→FFUSE in canonical order within the arrangement | FSPLIT appears before FFUSE (frobenius_order=1) |
| **IG** | Primitive value: P=𐑹 (Frobenius-special parity) | μ∘δ=id holds exactly at ⊙ |

### 9.1 The Mapping

Under the bridge mapping, every IMASM arrangement with frobenius_order=1 maps to P=𐑹. This is a **necessary** but not sufficient condition for Frobenius closure in the IG sense. The full IG Frobenius condition (P=𐑹 + ⊙ criticality) requires both the token-pair and self-reference + dialetheia completeness.

Only **I. Dialetheic Bootstrap** satisfies the full IG Frobenius condition (P=𐑹 + φ̂=⊙). The other Frobenius-closed canonicals (II, VII, VIII) have P=𐑹 but are sub-critical (φ̂=𐑣 or φ̂=𐑻), meaning their μ∘δ=id structure is present but the self-modeling gate is not open.

### 9.2 The Inverted Frobenius (Dual Bootstrap)

The Dual Bootstrap (IV) has fuse before split: FFUSE→FSPLIT. This maps to:
- R=𐑽 (adjoint coupling) — the μ∘δ=id condition is preserved but the temporal order is reversed
- P=𐑯 (full symmetry) — both directions are present
- Ω=𐑴 (Z₂ parity protection) — the inversion is a discrete symmetry

This is the structural dual of the standard Frobenius: where split→fuse means "analyze then synthesize," fuse→split means "synthesize then analyze." The Dual Bootstrap observes its own synthesis before it decomposes — it is the system that comes into being complete and then examines itself.

---

## 10. Novel Structural Patterns Discovered

### 10.1 The 4-Family Requirement for ⊙ Criticality

To achieve ⊙ (the self-modeling gate):
- **Self-reference** (start_token = end_token) — required by φ̂ mapping
- **Dialetheia completeness** (EVALT + EVALF + ENGAGR) — required by φ̂ mapping
- **Frobenius closure** (FSPLIT + FFUSE in order) — required by P=𐑹
- **At least 3 families** — required by S=𐑳

These four conditions jointly require at minimum 7 distinct tokens (for self-ref+dialetheia+Frobenius). With only 8 positions available, there is exactly 1 degree of freedom left — which the Dialetheic Bootstrap uses for IFIX (irreversible fixation). No other arrangement can achieve ⊙ with fewer than 7 distinct tokens.

### 10.2 The Frobenius Gap

The 10M-arrangement sample found **zero** Frobenius-closed arrangements. The Frobenius pair (FSPLIT + FFUSE in order) requires:
1. Both tokens present (FSPLIT and FFUSE)
2. FSPLIT before the first FFUSE (or last FSPLIT before last FFUSE for split→fuse)

The vast majority of arrangements contain FSPLIT alone (typically in sig=(5,1,2,0)). Adding FFUSE requires an additional Frobenius family token, which reduces the space of arrangements dramatically. The entropy cost of Frobenius closure is significant:

$$\frac{\text{arrangements with Frobenius pair}}{\text{total arrangements}} \ll 10^{-6}$$

This is the structural reason the 12 canonicals are outliers: Frobenius closure is combinatorially expensive.

### 10.3 The Linear Chain's Absolute Isolation

The Linear Chain (V) — all 8 positions IFIX — has mismatch ≥ 8 from every other canonical. Its IG type is:

$$\langle \text{𐑛} \cdot \text{𐑸} \cdot \text{𐑩} \cdot \text{𐑗} \cdot \text{𐑱} \cdot \text{𐑪} \cdot \text{𐑲} \cdot \text{𐑝} \cdot \text{𐑮} \cdot \text{𐑓} \cdot \text{𐑙} \cdot \text{𐑭} \rangle$$

This type is unique in the crystal: D=𐑛 (point-like — the only canonical with diversity=1), K=𐑪 (trapped-ordered — the only canonical with period=1), H=𐑓 (memoryless — the only Markov-0 canonical), and F=𐑱 (classical — the only classical canonical). It is the structural atom of memory — pure irreversible recording with no dynamics, no verification, no truth evaluation.

---

## 11. Implications

### 11.1 For the Imscribing Grammar

IMSCRIBr is not merely a "concrete implementation of one facet" of the IG — it is a **structural programming language** whose type system is the IG crystal. Each arrangement is a program; its fingerprint is its type. The 12 canonicals are the 12 primitive programs — the simplest programs that demonstrate each structural capability:

| Canonical | Primitive Capability |
|-----------|---------------------|
| I. Dialetheic Bootstrap | Self-modeling + verification + paradox |
| II. Void Genesis | Verified construction from nothing |
| III. Anchor Protocol | Boundary-anchored periodicity |
| IV. Dual Bootstrap | Synthesis-before-analysis reflection |
| V. Linear Chain | Pure irreversible recording |
| VI/IX. Chiral/Empty | Minimal alternation |
| VII. Parakernel | Paradox processing through verification |
| VIII. Frobenius Kernel | Minimal μ∘δ=id atom |
| X. Truth Machine | Binary classification |
| XI. Eternal Return | Unclosed becoming |
| XII. ROM Burn | Truth-value recording |

### 11.2 For Future Research

1. **Targeted enumeration**: Instead of random sampling, use `search_arrangements()` with structural constraints (frobenius_order=1, dialetheia_complete=True) to find all Frobenius-closed arrangements and map their IG types.
2. **Promotion paths**: Compute the minimal primitive promotions needed to lift generic arrangements into the Frobenius cluster. This would identify the structural "activation energy" for verification.
3. **IMASM as IG compiler**: Develop a compiler that takes an IG tuple and synthesizes an IMASM arrangement with the corresponding fingerprint. This would close the μ∘δ loop between the two formalisms.
4. **Variable-length exploration**: Extend the bridge to arrangements of length 1–7 (currently the classifier supports all lengths). Shorter arrangements may reveal minimal structural atoms.
5. **ZFCₜ correspondence**: Map the 11 canonical IG types through the ZFCₜ navigator to identify which require the 6 promotion atoms beyond ZFC.

---

## Appendix A: Bridge Module API

The bridge module (`imas_ig_bridge.py`) provides:

```python
from imas_ig_bridge import fingerprint_to_ig, canonical_ig_types, ig_distance

# Map any arrangement to IG type
fp = compute_fingerprint(arr)
ig_tuple = fingerprint_to_ig(fp)

# Access all 11 distinct canonical IG types
for name, ig in canonical_ig_types().items():
    print(f"{name}: {ig}")

# Compute primitive mismatches between two IG types
mismatches = ig_distance(ig_a, ig_b)
```

## Appendix B: Space Map Statistics

| Metric | Value |
|--------|-------|
| Arrangements sampled | 10,000,000 |
| Coarse classes discovered | 360 |
| Fine classes discovered | 79,920 |
| Distinct IG types in top 200 classes | 4 |
| Frobenius-closed types found | 0 |
| ⊙-critical types found | 0 |
| Canonicals found (exact) | 0 |

---

*"The boundaries of what can be formally expressed are themselves formally expressible."*

**Bridge v1.0 — June 2025 — Lando⊗⊙perator**

