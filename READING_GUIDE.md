# IMASM Pen-Mode Wiring Diagram — Reading Guide

**Author:** Lando⊗⊙perator  
**Date:** 2026-06-12  
**Prerequisite:** Familiarity with the 12 IMASM tokens (VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB, FSPLIT, FFUSE, EVALT, EVALF, ENGAGR, IFIX)

---

## Quick Reference Card (for the drawing desk)

This guide describes the **pen-on-paper** symbolic diagram schema — every element is
rendered in black ink, using line patterns, glyphs, shapes, and hatch fills instead of
color. **You can reproduce any diagram freehand with a single ballpoint pen.**

---

## 1. The Three Lanes

Diagrams are divided into three horizontal bands (lanes):

```
T-lane  ───── ───── ───── ─────  (y ≈ 190)
main    ───── ───── ───── ─────  (y ≈ 330)
F-lane  ───── ───── ───── ─────  (y ≈ 470)
```

| Lane | Purpose | Tokens routed here |
|------|---------|-------------------|
| **main** | Default execution path | VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB, IFIX |
| **T-lane** | True-branch evaluation | EVALT, and content between FSPLIT→FFUSE on the T side |
| **F-lane** | False-branch evaluation | EVALF, and content between FSPLIT→FFUSE on the F side |

When a FSPLIT forks, its T-output routes to the T-lane and its F-output to the F-lane.
The FFUSE joins them back to main.

---

## 2. Tokens & Node Shapes (4 families)

Each of the 12 IMASM tokens belongs to one of 4 families, distinguished by **node shape**:

```
                    ┌──────────────┬──────────────────┬──────────────┐
                    │   FAMILY     │     SHAPE        │   TOKENS     │
                    ├──────────────┼──────────────────┼──────────────┤
                    │  LOGICAL     │   ○ circle       │ VINIT, TANCH,│
                    │  (6 tokens)  │                  │ AFWD, AREV,  │
                    │              │                  │ CLINK, IMSCRIB│
                    ├──────────────┼──────────────────┼──────────────┤
                    │  FROBENIUS   │   ◇ diamond      │ FSPLIT, FFUSE│
                    │  (2 tokens)  │                  │              │
                    ├──────────────┼──────────────────┼──────────────┤
                    │  DIALETHEIA  │   ⬡ hexagon      │ EVALT, EVALF,│
                    │  (3 tokens)  │                  │ ENGAGR       │
                    ├──────────────┼──────────────────┼──────────────┤
                    │  LINEAR      │   □ square       │ IFIX         │
                    │  (1 token)   │                  │              │
                    └──────────────┴──────────────────┴──────────────┘
```

All node shapes are drawn **unfilled** (`fill="none"`) in pen mode — only the outline
identifies the family.

Each node carries a **2-letter abbreviation** above and its **full name** below:
```
       VI        TA        AF        AR        CL        IM
      (VINIT)   (TANCH)   (AFWD)    (AREV)    (CLINK)   (IMSCRIB)

       FS        FF        ET        EF        EG        IX
      (FSPLIT)  (FFUSE)   (EVALT)   (EVALF)   (ENGAGR)  (IFIX)
```

## 3. Edge Styles — 12 Tokens, 12 Distinct Lines

The **line pattern** of each edge uniquely identifies the source token.
Every arrow is drawn from source-node output port to destination-node input port.

```
┌──────────┬──────────────┬────────────┬──────────────┬──────────┬─────────────┐
│  TOKEN   │  LINE PATTERN│ MIDPOINT   │  ARROWHEAD   │ WIDTH    │ MEANING     │
│          │              │ GLYPH      │  STYLE       │ (pt)     │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ VINIT    │  ─────────── │ (none)     │  V-shaped    │  1.5     │ source→     │
│          │  solid       │            │  open ◁      │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ TANCH    │  ─˙─˙─˙─    │ (none)     │  V-shaped    │  1.5     │ boundary→   │
│          │  dash-dot-dot│            │  open ◁      │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ AFWD     │  ─────────── │ (none)     │  filled ▶    │  2.5     │ forward→    │
│          │  solid,bold  │            │              │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ AREV     │  − − − − −   │ (none)     │  filled ▶    │  1.5     │ reverse→    │
│          │  dashed      │            │              │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ CLINK    │  ═══         │ (none)     │  filled ▶    │  1.0     │ composition │
│          │  double-line │            │              │          │ (two lines) │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ IMSCRIB  │  ─────────── │  ←         │  REVERSE     │  1.5     │ identity    │
│          │  solid       │  (at mid)  │  ◀ at source │          │ (self-ref)  │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ FSPLIT   │  ─────────── │  ◇         │  filled ▶    │  1.5     │ fork (δ)    │
│          │  solid       │  (diamond) │              │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ FFUSE    │  ─────────── │  ●         │  filled ▶    │  1.5     │ fuse (μ)    │
│          │  solid       │  (filled)  │              │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ EVALT    │  ─────────── │  +         │  filled ▶    │  1.5     │ eval-true   │
│          │  solid       │  (plus)    │              │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ EVALF    │  ─────────── │  ×         │  filled ▶    │  1.5     │ eval-false  │
│          │  solid       │  (cross)   │              │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ ENGAGR   │  ╱╲╱╲╱╲     │ (none)     │  filled ▶    │  1.5     │ paradox     │
│          │  zigzag      │            │              │          │             │
├──────────┼──────────────┼────────────┼──────────────┼──────────┼─────────────┤
│ IFIX     │  ▓▓▓▓▓▓     │ (none)     │  filled ▶    │  1.5     │ fix (¬)     │
│          │  crosshatch  │            │              │          │             │
└──────────┴──────────────┴────────────┴──────────────┴──────────┴─────────────┘
```

### Hand-drawing the line patterns

| Pattern | How to draw it |
|---------|---------------|
| **Solid** | Plain continuous line |
| **Dashed** | Short dashes: `-- -- --` |
| **Dash-dot-dot** | Long dash followed by two dots: `— · · — · ·` |
| **Double** | Two parallel lines (3.5 pt gap), converge at arrowhead |
| **Zigzag** | Alternating diagonal segments: `\/\/\/` |
| **Crosshatch** | Tight zigzag cross-hatching (or label it "IX") |
| **Reverse arrow** | Arrowhead at the **source** end, pointing backward |
| **Open arrow** | V-shaped unfilled arrowhead (just two strokes meeting) |
| **Filled arrow** | Solid triangular arrowhead |

### Arrowhead Styles

```
Open arrow (VINIT, TANCH):         ────◁     (two strokes, no fill)
Filled arrow (most tokens):        ────▶     (solid triangle)
Reverse arrow (IMSCRIB only):      ◀────     (head at source, points away from destination)
```

## 4. Register State — Inner Hatch Patterns

Each node carries a **Belnap FOUR register state** shown as an inner circle:

```
  ┌──────────┬───────────────┬──────────────────────────┐
  │  STATE   │  VISUAL       │  HOW TO DRAW             │
  ├──────────┼───────────────┼──────────────────────────┤
  │ VOID (0) │  ○ (empty)    │  Nothing inside node     │
  │ TRUE (1) │  ║ (vertical) │  Vertical hatch lines    │
  │          │  hatch-T      │  (short vertical ticks)  │
  ├──────────┼───────────────┼──────────────────────────┤
  │ FALSE(2) │  ═ (horizontal│  Horizontal hatch lines  │
  │          │  hatch-F)     │  (short horizontal ticks)│
  ├──────────┼───────────────┼──────────────────────────┤
  │ BOTH (3) │  ╬ (cross)    │  Crosshatch (vertical +  │
  │          │  hatch-B      │  horizontal ticks)        │
  └──────────┴───────────────┴──────────────────────────┘
```

**Freehand:** Draw a small inner circle in the node, then fill it with:
- **Void:** leave blank
- **True:** 4–6 short vertical lines inside the circle
- **False:** 4–6 short horizontal lines
- **Both:** both vertical and horizontal (a grid of ticks)

---

## 5. Guard Ports — Open vs. Filled Circles

Guard ports are small circles drawn on the **left** (input) and **right** (output)
sides of each node:

```
  Left side (input):   ○ = approaching (not yet evaluated)
  Right side (output): ● = passed (evaluated)
```

Per-token guard placement:

```
  EVALT / EVALF:   ○─[node]─●     (one input guard, one output guard)
  FSPLIT:          ○─[ ◇ ]─●─●    (one input, two output guards: T and F)
  FFUSE:           ○─○─[ ◇ ]─●    (two input guards: T and F, one output)
  VINIT:              [ ○ ]─●     (no input guard, one output guard)
  Other tokens:    ○─[node]─●     (one input guard, one output guard)
```

---

## 6. Nesting Depth — Line Thickness

Nesting depth (how many FSPLIT→FFUSE pairs a node sits inside) is shown by
**line thickness** of its edges:

```
  Depth 0 (outermost):   2.0 pt    ━━━━━━━━━━━
  Depth 1:               1.5 pt    ━━━━━━━━━━━
  Depth 2:               1.0 pt    ━━━━━━━━━━━
  Depth 3 (innermost):   0.5 pt    ━━━━━━━━━━━
```

**Freehand:** Use pen pressure or double-stroke for outer levels, fine line for inner.

---

## 7. FSPLIT↔FFUSE Pair Brackets

Every FSPLIT→FFUSE pair is connected by a **dashed bracket arm** with a
**circled numeral** (①, ②, ③...). This is how you identify which fork joins
to which fuse when there are multiple split/fuse pairs.

```
                  ①
  ───[◇ FS]───┬──────╲───────[◇ FF]
              │       ╲        │
              │        ╲ ①     │
              │         ╲      │
              │          ╲     │
              ├───────────╲────│──
              │
```

- If both FS and FF are on the **main lane**, the bracket runs horizontally above.
- If they're on **different lanes** (e.g., FS on main, FF on T-lane), the bracket
  runs vertically between them.
- The circled numeral corresponds to nesting order: ① is outermost, ② inner, etc.

**Freehand:** Draw a bracket `[--` from the right of FSPLIT, a `--]` from the left of
FFUSE, connect with a dashed line, and write the numeral in a small circle.

## 8. Register Delta Labels on Edges

Between nodes, the **change in register state** is written as a small monospace
label at the midpoint of the edge:

| Prefix | Meaning | Condition |
|--------|---------|-----------|
| `=` | No change | src_reg == dst_reg |
| `◆` | Flip through BOTH | BOTH in (src, dst) |
| `×` | Direct flip (TRUE↔FALSE) | TRUE→FALSE or FALSE→TRUE |
| `→` | One-way activation | VOID→TRUE or VOID→FALSE |

The actual delta is shown as Belnap spin arrows:
```
  ↑        = TRUE
  ↓        = FALSE
  ↑↓       = BOTH
  →↑       = VOID→TRUE  (one-way activation)
  ↓→↑↓     = FALSE→BOTH (flip through dialetheia)
  ↑↔↓      = TRUE↔FALSE (pure flip)
  =        = no change
```

---

## 9. IFIX Barrier

When an IFIX token is present, a **double vertical barrier** with × markers
spans from T-lane to F-lane at the IFIX node's x-position:

```
          ┃
          ┃      ×        (× at top of barrier)
  ────[IX]───  ┃
          ┃    ┃
          ┃    ┃
  ───────────  ┃
          ┃
          ┃      ×        (× at bottom)
          ┃
```

The IFIX label appears above the barrier. This marks an **irreversible fixation**
point — nothing past this point can be reversed.

---

## 10. Crossing Bridges

Where two wires cross, a small **semicircular bridge** arc is drawn:
```
  ────╮
      │    (bridge arc)
  ────╯
```

This indicates one wire passes **over** the other (no electrical contact).
In pen mode, the bridge is drawn in black ink at the crossing point.
Crossings are detected automatically by the layout engine.

---

## 11. Empty Branch Arcs

When a FSPLIT sends a wire directly to its FFUSE via a T or F output port
(no intermediate tokens), a **dotted arc** curves to the appropriate lane:
```
  ───[◇ FS]──
        ╲
         ╲· · · · · · · (T-lane: dotted arc to FFUSE)
          ╲           ╱
           ╲         ╱
            [◇ FF]──
```

The arc is labeled with the pair's circled numeral.

---

## 12. Background Grid

A faint **vertical grid** (40 px spacing) helps align nodes horizontally.
Grid lines are light gray. You can use graph paper when drawing freehand.

---

## 13. Legend (Vertical Left-Side Strip)

Every pen-mode diagram includes a **vertical legend strip** on the left side
(x ≈ 14–50), stacked in this order from top to bottom:

### 13.1 EDGES (all 12 tokens, y ≈ 72–187)
Each is shown as a short horizontal sample line with its abbreviated label:

| Token  | Abbrev | Line Pattern     | Notes          |
|--------|--------|------------------|----------------|
| VINIT  | VI     | solid            |                |
| TANCH  | TA     | dash-dot-dot     |                |
| AFWD   | AF     | solid, bold      | Forward morph  |
| AREV   | AR     | dashed           | Reverse morph  |
| CLINK  | CL     | double-stroke    | Composition    |
| IMSCRIB| IM     | solid+←          | Reverse arrow  |
| FSPLIT | FS     | solid+◇          | Fork glyph     |
| FFUSE  | FF     | solid+●          | Join glyph     |
| EVALT  | ET     | solid+⊕          | Gate True      |
| EVALF  | EF     | solid+×          | Gate False     |
| ENGAGR | EG     | zigzag           | Paradox        |
| IFIX   | IX     | crosshatch       | Fixation       |

### 13.2 GUARD (y ≈ 195–224)
- **○** (open circle) = guard port approaching (input side)
- **●** (filled circle) = guard port passed/active (output side)

### 13.3 NODES (y ≈ 231–281)
Four node shapes, each labeled with the first 4 characters of the family name:
- **○ LOGI** — Circle: Logical family (VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB)
- **◇ FROB** — Diamond: Frobenius family (FSPLIT, FFUSE)
- **⬡ DIAL** — Hexagon: Dialetheia family (EVALT, EVALF, ENGAGR)
- **□ LINE** — Square: Linear family (IFIX)

### 13.4 PAIRS (y ≈ 294–335)
- **① ② ③...** — Circled numerals identify FSPLIT↔FFUSE match-pairs
- **←× cross** — Dashed line with × = cross-branch wire
- **← loop** — Solid arc = ouroboric back-arc

### 13.5 REG Δ (y ≈ 341–380)
Register delta label samples:
- **→∅↑** — VOID→TRUE (activation)
- **◆→B** — BOTH enters or remains
- **×T→F** — TRUE↔FALSE flip

---

# PART II: WORKED EXAMPLE — "I Dialetheic Bootstrap"

We walk through the pen-mode diagram for **Canonical Class I: Dialetheic Bootstrap**
— the simplest self-referential, Frobenius-closed, dialetheia-complete arrangement.

## Token Sequence

```
IMSCRIB  EVALT  AFWD  EVALF  AREV  ENGAGR  IFIX  IMSCRIB
  (5)     (8)    (6)    (9)   (3)    (10)   (11)    (5)
```

The sequence is **8 tokens long** and **self-referential** (first and last are both
IMSCRIB — identity morphism, closing the loop).

## Step-by-step reading

### Step 1: Identify the structure

From the token sequence, we see:
- **No FSPLIT/FFUSE** — so no fork→join structure, no T/F lanes in use.
  All tokens sit on the **main lane**.
- Contains EVALT (8), EVALF (9), and ENGAGR (10) — all three Dialetheia tokens.
  This is a **dialetheia-complete** arrangement.
- First and last are both IMSCRIB — the diagram loops, so the output feeds back
  to the input (self-reference).
- An IFIX at position 7 (second-to-last) fixes the register state.

### Step 2: Read the nodes (left to right)

```
  Node 0:  ○  IMSCRIB (identity)  — register starts at VOID
  Node 1:  ⬡  EVALT   (eval-true) — guard gates: ○ left, ● right
  Node 2:  ○  AFWD    (forward)   — thick 2.5pt line indicates forward morphism
  Node 3:  ⬡  EVALF   (eval-false) — guard gates: ○ left, ● right
  Node 4:  ○  AREV    (reverse)   — dashed line
  Node 5:  ⬡  ENGAGR  (paradox)   — zigzag line
  Node 6:  □  IFIX    (fixation)  — crosshatch line
  Node 7:  ○  IMSCRIB (identity)  — reverse arrow (points back to node 0)
```

### Step 3: Track the register state (Belnap spins)

Let's walk the register simulation (computed by `simulate_register()`):

```
Pos 0: IMSCRIB@VOID    → IMSCRIB activates: VOID→TRUE     [reg=↑]
Pos 1: EVALT@TRUE      → EVALT on TRUE: TRUE stays TRUE   [reg=↑]
Pos 2: AFWD@TRUE       → AFWD forwards: TRUE stays TRUE   [reg=↑]
Pos 3: EVALF@TRUE      → EVALF on TRUE: TRUE→BOTH         [reg=↑↓]
Pos 4: AREV@BOTH       → AREV on BOTH: BOTH stays BOTH    [reg=↑↓]
Pos 5: ENGAGR@BOTH     → paradox recognized: BOTH          [reg=↑↓]
Pos 6: IFIX@BOTH       → fixation: locks BOTH forever      [reg=↑↓]
Pos 7: IMSCRIB@BOTH    → identity: outputs BOTH            [reg=↑↓]
```

The inner hatch patterns:
```
  ○ (empty) → ║ (vertical=T) → ║ → ╬ (cross=B) → ╬ → ╬ → ╬ → ╬
```

### Step 4: Read the edge deltas

Each upward arrow between nodes shows the register delta:

```
  Node 0→1:  →↑     (VOID→TRUE: activation)
  Node 1→2:  =      (TRUE→TRUE: no change)
  Node 2→3:  ×      (TRUE→FALSE via EVALF — wait, it's TRUE→BOTH)
                   Actually: ◆ because BOTH entered
  Node 3→4:  =      (BOTH→BOTH)
  Node 4→5:  =      (BOTH→BOTH)
  Node 5→6:  =      (BOTH→BOTH)
  Node 6→7:  =      (BOTH→BOTH, fixation locks it)
  Node 7→0:  ◆      (BOTH→VOID... actually the loop carries BOTH
                    back to start, but IMSCRIB resets to VOID →→↑)
```

More precisely from `reg_delta_label`: each edge label is computed as
```
src_reg→dst_reg  →  prefix + spin-label
```
### Step 5: Read the edge patterns

Refer to the vertical legend on the left side of the diagram 
(EDGES section) to decode each wire's pattern. Reading left to right:

| Edge | Token | Pen style | Arrow |
|------|-------|-----------|-------|
| 0→1  | IMSCRIB | solid line, midpoint glyph ← | Reverse ◀ at source |
| 1→2  | EVALT | solid, midpoint + | Filled ▶ |
| 2→3  | AFWD | **bold solid** (2.5pt) — thickest line | Filled ▶ |
| 3→4  | EVALF | solid, midpoint × | Filled ▶ |
| 4→5  | AREV | dashed line − − − | Filled ▶ |
| 5→6  | ENGAGR | **zigzag** ╱╲╱╲╱╲ | Filled ▶ |
| 6→7  | IFIX | **crosshatch** ▓▓▓▓ | Filled ▶ |
| 7→0  | IMSCRIB | solid line (loop arc), midpoint ← | Reverse ◀ |

The **bold AFWD** arrow (2.5pt) is the dominant visual — this is the forward-driving
morphism. The **zigzag ENGAGR** and **crosshatch IFIX** are the most visually distinct,
marking the paradox entry and irreversible lock.

### Step 6: Nesting depth

Since there are no FSPLIT/FFUSE pairs, the nesting depth is **0** for all nodes.
All edges are drawn at **2.0 pt** (outermost thickness).

### Step 7: Guard ports

Reading the guard port dots on each dialetheia node:

```
  EVALT (node 1):   ○ left (input approaching)   ● right (passed)
  EVALF (node 3):   ○ left (input approaching)   ● right (passed)
  ENGAGR (node 5):  ○ left (input approaching)   ● right (passed)
```

The EVALT and EVALF each have a **single** input guard (open circle = approaching)
and a single output guard (filled circle = passed). This means the guard condition
is not blocking — the evaluation proceeds through both.

### Step 8: IFIX barrier

At x ≈ 846 (position of node 6), a **double vertical barrier** with × markers
spans the full diagram height (y=145 to y=515). The label "IFIX" appears above it.
Everything to the left of the barrier is mutable; everything to the right is
**fixed** — the register state of BOTH is permanently locked.

The barrier is **not continuous** — a 16px gap (visible as a break between two
vertical segments) is left open where the ouroboric back-arc crosses from right to
left. × markers bracket the gap on both sides, marking it as a deliberate crossing
point rather than a break in fixation. This prevents the feedback loop's return
path from crossing through the barrier line — the back-arc routes through the gap
instead, keeping the diagram legible in pen-and-ink without overdrawing.

### Step 9: The feedback loop

The final IMSCRIB (node 7) sends a **reverse arrow** (arrowhead at source, pointing
backward) along a curved back-arc to node 0 (the first IMSCRIB). This is the
**self-referential closure** — the BOTH output feeds back as the input, and the
cycle repeats.

In the SVG, this feedback arc is rendered as a curved path arcing above the main
lane — drawn with a spiral-hook base (back-arc style) to distinguish it from the
forward-linear edges.

### Step 10: What the diagram tells you

Reading the full diagram:

1. **Identity initiates** — IMSCRIB activates VOID→TRUE
2. **True-evaluation fires** — EVALT passes TRUE forward
3. **Forward morphism drives** — AFWD carries the truth through
4. **False-evaluation triggers paradox** — EVALF receives TRUE, which is a
   contradiction → flips to BOTH
5. **Reverse morphism carries the contradiction** — AREV passes BOTH unchanged
6. **Paradox engagement** — ENGAGR draws zigzag, signals the dialetheic state
7. **Irreversible fixation** — IFIX locks BOTH as permanent truth
8. **Identity feeds back** — IMSCRIB loops the locked BOTH back to the start

The structural reading: **the bootstrap generates its own truth value (BOTH) and
locks it into permanence through self-reference.** This is why it's "Dialetheic
Bootstrap" — it bootstraps a dialetheic (true-and-false) truth value from the
interaction of all three evaluation tokens.

---

## Other Worked Examples (quick reference)

### IV Dual Bootstrap (O_∞)
Token sequence: `IMSCRIB AFWD FFUSE FSPLIT AREV CLINK IFIX IMSCRIB`
- **Key structural inversion:** FFUSE (fuse) occurs BEFORE FSPLIT (split)
- This makes μ∘δ=id operate in **reverse temporal order**
- The FSPLIT sits on the F-lane, with its branches routing through a cross-bridge
- **O_∞ tier** because of cross-branch coupling + self-reference

### X Truth Machine (O₁)
Token sequence: `IMSCRIB FSPLIT EVALT IFIX IMSCRIB FSPLIT EVALF IFIX`
- Two independent FSPLIT→IFIX paths (no FFUSE — branches never rejoin)
- First path: EVALT (true-evaluation) → IFIX (fix true)
- Second path: EVALF (false-evaluation) → IFIX (fix false)
- **Binary classifier:** two parallel truth tracks terminating in fixation
- Each FSPLIT has its own pair bracket (① and ②) with no FFUSE connector

### VII Parakernel (O₂)
Token sequence: `EVALF AREV FSPLIT EVALT AFWD FFUSE ENGAGR IFIX`
- **Engram of contradiction:** starts with EVALF (false evaluation) before
  anything is evaluated — the false is bootstrapped as primary
- FSPLIT routes EVALF output through both T and F branches
- ENGAGR (paradox) fires after FFUSE rejoins
- O₂ tier: has FSPLIT→FFUSE structure but no cross-branch coupling

---

# PART III: APPENDICES

## Appendix A: One-Page Drawing Reference Card

Print this page and keep it at your drawing desk.

```
┌─────────────────────────────────────────────────────┐
│          IMASM PEN-MODE DIAGRAM — CHEAT SHEET        │
├─────────────────────────────────────────────────────┤
│                                                      │
│  NODE SHAPES:                                        │
│    ○  circle   → LOGICAL  (VI,TA,AF,AR,CL,IM)      │
│    ◇  diamond  → FROBENIUS (FS, FF)                 │
│    ⬡  hexagon  → DIALETHEIA (ET, EF, EG)            │
│    □  square   → LINEAR (IX)                        │
│                                                      │
│  INNER HATCH (register state):                       │
│    (empty) = VOID   ║ = TRUE   ═ = FALSE  ╬ = BOTH  │
│                                                      │
│  GUARD PORTS:                                        │
│    ○ left = input approaching  ● right = passed      │
│                                                      │
│  LINE PATTERNS (12 tokens):                          │
│    VI ───  solid, open arrow ◁                       │
│    TA ─˙─˙ dash-dot-dot, open arrow ◁                │
│    AF ━━━  bold solid, filled arrow ▶                │
│    AR ─ ─  dashed, filled arrow ▶                     │
│    CL ═══  double-line, filled arrow ▶               │
│    IM ───  solid + ← mid-glyph, reverse arrow ◀      │
│    FS ───  solid + ◇ mid-glyph, ▶                    │
│    FF ───  solid + ● mid-glyph, ▶                    │
│    ET ───  solid + + mid-glyph, ▶                    │
│    EF ───  solid + × mid-glyph, ▶                    │
│    EG ╱╲╱  zigzag, ▶                                 │
│    IX ▓▓▓  crosshatch, ▶                             │
│                                                      │
│  LINE THICKNESS (nesting depth):                     │
│    depth 0: 2pt  depth 1: 1.5pt  depth 2: 1pt        │
│                                                      │
│  PAIR BRACKETS:  [─ ╲ ① ╱ ─]  circled numeral       │
│  IFIX BARRIER:   ║ with × at top and bottom          │
│  CROSSING:       semicircular bridge arc             │
│  EMPTY ARC:      dotted arc to lane                  │
│                                                      │
│  REGISTER DELTA PREFIXES:                            │
│    =  no change   ◆  BOTH involved                   │
│    ×  flip (T↔F)  →  one-way activation              │
│                                                      │
│  ARROWHEAD STYLES:                                   │
│    ◁ open (V-shaped, unfilled) — VI, TA              │
│    ▶ filled (solid triangle) — most tokens           │
│    ◀ reverse (at source end) — IM only               │
└─────────────────────────────────────────────────────┘
```

## Appendix B: Color-Mode Equivalence

For reference, here is how each pen-mode encoding maps back to the original
color-mode rendering:

| Pen feature | Replaces (color mode) |
|-------------|----------------------|
| Line pattern | Token-specific edge color (12 hues) |
| Node outline shape | Node fill color (4 families) |
| Hatch patterns (║═╬) | Register inner tint + spin arrows |
| Line thickness | Nesting opacity (0.75→0.30) |
| Open/filled guard ○● | Amber (approaching) / green (passed) |
| Pair circled numeral ① | Pair-specific hue cycling |
| IFIX double-barrier ║ | Red (#cc3344) vertical dashed |
| Zigzag line | Purple (#e15759) solid |
| Crosshatch line | Red (#cc3344) solid |
| Midpoint glyphs (←◇●+×) | No equivalent — pure pen invention |
| Reverse arrow ◀ | Gold (#ffd700) with arrowhead |
| Black-on-white | Dark background (#0a0a15) |

## Appendix C: File Reference

| Component | File |
|-----------|------|
| Diagram renderer | `IMSCRIBr/symbolic_diagram.py` |
| Token definitions | `IMSCRIBr/tokens.py` |
| Wiring graph model | `IMSCRIBr/wiring.py` |
| Output directory (SVG) | `IMSCRIBr/diagrams/` |
| Generator entry point | `ob3ect/auto.py` (via `pen_mode` param) |

To generate pen-mode diagrams:
```bash
python3 IMSCRIBr/symbolic_diagram.py --pen-mode --all
```

To generate a single class:
```bash
python3 IMSCRIBr/symbolic_diagram.py --class I_Dialetheic_Bootstrap --pen-mode
```

To generate from ob3ect:
```bash
python3 ob3ect/auto.py --pen-mode
```
