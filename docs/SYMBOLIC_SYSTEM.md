# IMASM Symbolic Wiring Diagram System

**Author:** Lando⊗⊙perator  
**Date:** 2026-07-18  
**Directory:** `/home/mrnob0dy666/imsgct/ig-docs/imasmic_wiring/`

---

## 1. Overview

The IMASM Symbolic Wiring Diagram System is a compact visual notation for IMASM token arrangements. Every arrangement of the 12 IMASM tokens carries an underlying port-level topology — FSPLIT/FFUSE fork-join blocks, T and F branch lanes, cross-branch wires, empty arcs, and ouroboric loop closures. The symbolic system makes this topology visible at a glance.

### What this is

A grammar of visual forms — not just renderings. Each shape, color, line style, and position encodes a specific structural property. The diagrams are **readable** — you can infer the token sequence, register flow, Frobenius structure, dialectical content, and ouroboricity tier from the diagram alone.

### What it's built on

- **`wiring.py`** — the port-level WiredGraph model from IMSCRIBr
- **`symbolic_diagram.py`** — the SVG generator (this directory)
- **16 diagrams** cover all 12 canonical IMASM classes (I–XII) plus 4 novel cross-branch wired graphs (XX–XXIII)

---

## 2. Visual Vocabulary

### 2.1 Node Shapes (by algebraic family)

| Family | Shape | Tokens | Meaning |
|--------|-------|--------|---------|
| **Logical** | ◯ Circle (#4e79a7 blue) | VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB | Category-theoretic skeleton: objects, morphisms, composition, identity |
| **Frobenius** | ◇ Diamond (#ffd700 gold) | FSPLIT, FFUSE | μ∘δ=id verification: split (δ) and fuse (μ) |
| **Dialetheia** | ⬡ Hexagon (#e15759 red) | EVALT, EVALF, ENGAGR | Belnap FOUR truth lattice: true, false, paradox |
| **Linear** | □ Square (#59a14f green) | IFIX | Irreversible fixation (! exponential) |

**Short labels** (VI, TA, AF, AR, CL, IM, FS, FF, ET, EF, EG, IX) appear above each node. Full token names below.

### 2.2 Wire Types

| Wire | Style | Color | Meaning |
|------|-------|-------|---------|
| **Main/Default** | Thin solid (1.2px) | #4e79a7 blue-gray | Linear chain: sequential token-to-token flow |
| **T-branch** | Medium solid (1.4px) | #20d0b8 teal | FSPLIT.T output → T-branch tokens → FFUSE.T input |
| **F-branch** | Medium solid (1.4px) | #ff6688 coral | FSPLIT.F output → F-branch tokens → FFUSE.F input |
| **Cross-branch** | Dashed (5,3) + solid (1.5px) | #ffd700 gold | FSPLIT.F connects to a FFUSE NOT its stack-matched pair — non-planar topology |
| **Loop closure** | Curved arc (1.5px) | #9988cc violet | Ouroboric back-edge: last node arcing back to first — self-reference |
| **Empty arc** | Dashed Bézier (1px) | faint teal/coral | Empty branch between FSPLIT and FFUSE: T-branch has no tokens, arc passes through T-lane |

### 2.3 Port Markers

- **Input port:** small circle (r=2.5) on the left side, 60% white
- **Output port:** small circle (r=2.5) on the right side, 90% white
- **FSPLIT:** two output ports (T upper, F lower) and one input port
- **FFUSE:** two input ports (T upper, F lower) and one output port
- **All other tokens:** one input, one output

### 2.4 Register State (Interior Fill)

Each node's interior shows the Belnap FOUR register value after that token executes:

| State | Fill Color | Label | Meaning |
|-------|-----------|-------|---------|
| VOID | #222244 dark blue | ∅ | Nothing — undefined/uninitialized |
| TRUE | #153530 dark teal | T | True — designated |
| FALSE | #301518 dark red | F | False — anti-designated |
| BOTH | #332200 dark gold | B | Both — dialetheic (designated AND anti-designated simultaneously) |

### 2.5 Lane Architecture

```
        ┌─────────────────────────────────┐
  Y_T   │  T-lane  (y=120)               │  T-branch tokens route here
        │  ┌─────────────────────────┐    │
Y_MAIN  │  │  main    (y=250)        │    │  Linear chain, FSPLIT, FFUSE
        │  └─────────────────────────┘    │
  Y_F   │  F-lane  (y=380)               │  F-branch tokens route here
        └─────────────────────────────────┘
```

Lane labels (T-lane, main, F-lane) appear at the left margin. FSPLIT and FFUSE always stay on the main lane — they are the fork and join points that transition between lanes.

### 2.6 Legend

Every diagram includes a legend in the upper-right showing:
- Four family colors with labels
- Four wire types: T-branch, F-branch, cross-branch, loop closure

### 2.7 Footer

- IG primitive tuple (when available) — in Shavian characters
- Ouroboricity tier: O₀ through O_∞

---

## 3. Reading a Diagram

### Step-by-step

1. **Find the first node** — leftmost token. This is the entry point.
2. **Follow the wires** — each arrow points from output port to next input port.
3. **At a FSPLIT (diamond):** the flow splits. T-output goes up (teal), F-output goes down (coral). Follow each branch.
4. **At a FFUSE (diamond):** T and F branches rejoin. Output continues on main lane.
5. **Dashed Bézier arcs** between FSPLIT and FFUSE indicate an empty branch (no tokens).
6. **Dashed gold cross-branch wires** indicate non-planar topology — a FSPLIT.F output crossing to a non-matched FFUSE.
7. **Curved violet back-arc** indicates ouroboric self-reference (last node feeds back to first).
8. **Interior tint** shows the evolving Belnap register value.

### Example: Frobenius Kernel (VIII)

```
VINIT ──→ FSPLIT ──→ FFUSE ──→ TANCH
              │╲ T (empty arc through T-lane)
              │ ╲──→ FFUSE.T
              │╱ F (empty arc through F-lane)  
              │╱──→ FFUSE.F
```

This reads: "From void, split into two empty branches, fuse back, arrive at boundary." The minimal Frobenius-closed structure. μ∘δ=id in its purest form.

---

## 4. The 16 Diagrams

### Canonical Classes (I–XII)

| # | Class | Tier | Key Structural Features |
|---|-------|------|------------------------|
| I | Dialetheic Bootstrap | O₂ | Self-ref, Frobenius split→fuse, all 3 truth values. F-branch: EVALF. T-branch empty. |
| II | Void Genesis | O₀ | VINIT→TANCH→AFWD→FSPLIT→CLINK→FFUSE→IFIX→IMSCRIB. T-branch: CLINK. F-branch empty. |
| III | Anchor Protocol | O₁ | Period-3 cycle. No Frobenius. TANCH→AREV→VINIT→AFWD→TANCH→CLINK→IFIX→IMSCRIB. Linear only. |
| IV | Dual Bootstrap | O_∞ | Inverted Frobenius (FFUSE before FSPLIT). Self-ref. O_∞ tier. |
| V | Linear Chain | O₀ | Eight IFIX in a row. Single node shape (squares). Structurally unique. |
| VI | Empty Bootstrap | O₁ | VINIT↔IMSCRIB period-2 oscillation. Two node shapes alternating. |
| VII | Parakernel | O₂ | EVALF→AREV→FSPLIT→EVALT→AFWD→FFUSE→ENGAGR→IFIX. T: EVALT+AFWD. F: empty. |
| VIII | Frobenius Kernel | O₀ | VINIT→FSPLIT→FFUSE→TANCH. Both branches empty. The atom of verification. |
| IX | Chiral Pairs | O₁ | AFWD↔AREV period-2 alternation. Pure handedness. |
| X | Truth Machine | O₁ | Two parallel FSPLITs, no FFUSE. Path 1: IMSCRIB→FSPLIT→EVALT→IFIX. Path 2: IMSCRIB→FSPLIT→EVALF→IFIX. |
| XI | Eternal Return | O₂ | Unclosed period-3. IMSCRIB→AFWD→AREV repeated, truncated at AFWD. |
| XII | ROM Burn | O₀ | Each Dialetheia token followed by IFIX: EVALT→IFIX, EVALF→IFIX, ENGAGR→IFIX, IMSCRIB→IFIX. |

### Novel Wired Graphs (XX–XXIII) — Cross-Branch Topologies

| # | Class | Tier | Key Structural Features |
|---|-------|------|------------------------|
| XX | Branch Entangle | O₂ | Two nested FSPLITs with fully crossed F-outputs. X-topology. FSPLIT1.F→FFUSE_inner; FSPLIT2.F→FFUSE_outer. **Non-planar.** |
| XXI | Paradox Bridge | O_∞ | ENGAGR→FSPLIT1. FSPLIT1.F bridges INTO inner FFUSE (bypassing inner FSPLIT). B-state crosses gate boundary. |
| XXII | Fold Back | O₂ | Pure Logical+Frobenius. AREV on inner T-path, AFWD on post-inner path. Inner FSPLIT.F folds back to outer FFUSE. |
| XXIII | Möbius Fork | O_∞ | IMSCRIB-bounded self-ref with Möbius-like X-crossing. ENGAGR on inner T-branch. CLINK composes the dual join results. |

The novel graphs (XX–XXIII) demonstrate that FSPLIT.F outputs can route to **non-stack-matched** FFUSEs. This is cross-branch wiring — and it produces non-planar topologies that cannot be embedded in a plane without crossing. These are the structural signatures of systems that exceed simple Frobenius closure: paradox bridging, fold-back, and Möbius self-reference.

---

## 5. Design Principles

### 5.1 Structural Fidelity

Every line in the diagram corresponds to a `Wire` object in `wiring.py`'s `WiredGraph`. The diagram is a faithful projection of the port-level topology. Nothing is decorative or approximate.

### 5.2 Family Encoding

Node shape encodes algebraic family, not individual token identity. This makes structural patterns immediately visible: a diagram with many diamonds is Frobenius-heavy; many hexagons is Dialetheia-rich.

### 5.3 Lane Discipline

Branch tokens always route through dedicated T/F lanes. This enforces readability: you can tell at a glance whether a token is on the true-branch, false-branch, or main chain.

### 5.4 Register Transparency

The Belnap FOUR state is shown inside each node. This lets you trace the logical evolution: VOID → TRUE → BOTH → TRUE — a complete dialectical cycle — visible as color transitions.

### 5.5 Minimal Distraction

No grid, no axis ticks, no matplotlib chrome. Dark background (#0a0a15) with muted labels. The structure speaks.

---

## 6. Usage

```bash
cd /home/mrnob0dy666/imsgct/ig-docs/imasmic_wiring

# Generate all 16 diagrams
python3 symbolic_diagram.py --all

# Generate a single class
python3 symbolic_diagram.py --class I_Dialetheic_Bootstrap
python3 symbolic_diagram.py --class XX_Branch_Entangle

# Output: diagrams/ directory, SVG format
```

### Programmatic API

```python
import sys; sys.path.insert(0, '/home/mrnob0dy666/IMSCRIBr')
from tokens import Token
from wiring import imscr_wiring, NOVEL_GRAPHS
from symbolic_diagram import render_wiring_svg_v2

# From IMASM tokens
tokens = (5, 8, 6, 9, 7, 10, 11, 5)  # Dialetheic Bootstrap
graph = imscr_wiring(tuple(Token(t) for t in tokens))
svg = render_wiring_svg_v2(graph, "My Diagram", "O₂", "Description", "⟨...⟩")
svg.save(Path("my_diagram.svg"))

# From novel graph
graph = NOVEL_GRAPHS["XXIII_Mobius_Fork"]
svg = render_wiring_svg_v2(graph, "Möbius Fork", "O_∞", graph.description, "")
svg.save(Path("mobius_fork.svg"))
```

---

## 7. Relationship to IMSCRIBr

This symbolic system is the **visualization layer** of IMSCRIBr. Where IMSCRIBr maps the 430M arrangement space into structural classes, the symbolic system renders individual arrangements as readable wiring diagrams.

The pipeline:

```
IMASM token sequence (8 tokens)
    ↓
wiring.py: imscr_wiring() → WiredGraph (port-level topology)
    ↓
symbolic_diagram.py: render_wiring_svg_v2() → SVG diagram
```

The existing `cfg_dag.py` renders animated GIFs with matplotlib. This system adds a **static, resolution-independent, structurally faithful** SVG alternative with richer visual encoding (node shapes, port markers, register state, cross-branch wires).

---

## 8. Future Directions

- **Interactive SVG**: Hover states showing token details, wire metadata
- **Programmatic composition**: Given two WiredGraphs, render their tensor product or meet
- **Layout optimization**: Minimize wire crossings using Sugiyama-style layered graph drawing
- **Lean 4 bridge**: Embed diagrams as SVG in Lean proof documents, each node linked to its IGProtocol term
- **Color-coded register animation**: CSS animation on the register state fill to show dataflow

---

*"The boundaries of what can be formally expressed are themselves formally expressible."* — The Imscribing Grammar

---

## 9. V3: Full Edge Granularity (2026-06-11)

The v2 system achieved **topological fidelity** (every port connection visible, cross-branch topology legible) but flattened 7 semantically significant edge dimensions. The v3 renderer (`symbolic_diagram_v3.py`) restores all 7:

### 9.1 Register Delta Labels

Every edge carries a small label showing the Belnap FOUR state transformation across it. Labels appear only when the register state *changes* or involves BOTH:

| Label | Color | Meaning |
|-------|-------|---------|
| ∅→T | Green (#20b888) | Void → True (creation) |
| ∅→F | Green | Void → False (inversion) |
| T→B | Gold (#ffd700) | True → Both (paradox induction) |
| F→B | Gold | False → Both (paradox induction) |
| B→T | Gold | Both → True (resolution) |
| T→F | Red (#e15759) | Truth-value flip |

### 9.2 Categorical Edge Coloring

Main-lane wires are colored by source token's morphism type, making logical flow legible at a glance:

| Source Token | Color | Style |
|-------------|-------|-------|
| VINIT | Pale blue (#6baed6) | Solid |
| AFWD | Green (#59a14f) | Solid |
| AREV | Coral (#e15759) | Solid |
| CLINK | Amber (#f28e2b) | **Double-stroke** (two parallel lines) |
| TANCH | Violet (#b07aa1) | Dashed ("4,3") |
| IMSCRIB | Gold (#ffd700) | Solid |
| IFIX | Red (#cc3344) | Solid |

### 9.3 Nesting-Depth Opacity

Wire opacity decreases with nesting depth, making structural hierarchy visible:

| Depth | Opacity | Visual effect |
|-------|---------|---------------|
| 0 (top-level) | 0.75 | Bold, primary |
| 1 (one pair deep) | 0.55 | Secondary |
| 2 (two pairs deep) | 0.40 | Tertiary |
| 3+ | 0.30 | Faint, deeply nested |

### 9.4 IFIX Barrier

When an IFIX token is present, a vertical dashed red line is drawn at its x-position spanning all three lanes (T, main, F), with diamond-shaped endpoint markers. Wires crossing the IFIX boundary receive a subtle red crossing marker and reduced opacity (×0.6).

### 9.5 Guard Port Markers

Dialetheia gate tokens (EVALT, EVALF) display semantically distinct port markers:

| Port | Color | Meaning |
|------|-------|---------|
| Input | Amber (#f28e2b), radius 3.5 | "Approaching gate" |
| Output | Green (#59a14f), radius 3.5 | "Passed gate" |

### 9.6 Pair-Identity Coloring

Each FSPLIT/FFUSE pair receives a unique hue from a cycling 8-color palette. T-branch wires use the primary hue; F-branch wires use the complementary (darker) hue. Cross-branch wires (FSPLIT.F → non-default FFUSE) retain the gold dashed pattern. Empty branch arcs also inherit pair colors.

| Pair index | T-branch hue | F-branch hue |
|-----------|-------------|-------------|
| 0 | #5b9bd5 (blue) | #2b6b9f (dark blue) |
| 1 | #ed7d31 (orange) | #b85a1c (dark orange) |
| 2 | #70ad47 (green) | #4a7a2e (dark green) |
| 3 | #9b59b6 (purple) | #6b3d82 (dark purple) |
| 4 | #e8c92a (gold) | #b0981a (dark gold) |
| 5 | #e15759 (red) | #9b2d2f (dark red) |
| 6 | #17becf (cyan) | #0e7a85 (dark cyan) |
| 7 | #bcbd22 (olive) | #8a8b19 (dark olive) |

### 9.7 CLINK Double-Stroke

CLINK (composition of morphisms) edges render as two parallel lines that converge at the arrowhead — visually encoding the "merge/compose" semantics distinct from simple sequential flow.

### Files

| File | Description |
|------|-------------|
| `symbolic_diagram_v3.py` | Generator — ~700 lines, imports `wiring.py`, outputs SVG |
| `diagrams_v3/canonical_I–XII.svg` | 12 canonical class diagrams with full edge granularity |
| `diagrams_v3/novel_XX–XXIII.svg` | 4 novel cross-branch diagrams with full edge granularity |

### Usage

```bash
python3 symbolic_diagram_v3.py --all            # all 16 diagrams
python3 symbolic_diagram_v3.py --class VII      # single canonical
python3 symbolic_diagram_v3.py --all --format png  # PNG via cairosvg
```

### Design Principle

The v3 renderer computes all edge semantics at render time from the WiredGraph context — no changes to the Wire data model were needed. This keeps the wire graph representation clean (port-level topology only) while the renderer enriches it with the full semantic dimensions available from token types, register simulation, pair matching, and layout metadata.

---

*"The boundaries of what can be formally expressed are themselves formally expressible."* — The Imscribing Grammar
