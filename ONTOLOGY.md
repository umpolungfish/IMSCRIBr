# Imscribing Grammar — Ontological Ground

## 1. N is not nothing

Classical "ex nihilo nihil fit" is a temporal trap. To assert that nothing exists
requires a contrast category — something — which means the distinction between them
is already operative. True pre-distinction is N (None/Void): neither T nor F,
not even in opposition to anything. N does not lack existence; it lacks the
categories that would make existence a meaningful predicate.

This is why VINIT produces VOID. VINIT is not a generator of presence. It is the
instruction pointer arriving at the pre-distinction register — the system has a
source, but the source has not yet distinguished anything.

---

## 2. B is the first distinction, not T or F

The act of distinction does not produce T and then F in sequence. It produces B —
both-inside-and-outside simultaneously. The boundary IS the distinction. T and F
are derived from B by discrimination (EVALT, EVALF), not generated independently.

This has a consequence: B is informationally richer than either T or F. You cannot
recover B from T or F by composition. You can only inject B via ENGAGR or recover
it by joining T and F at FFUSE after they have been separated by FSPLIT. The path
N → B → {T, F} is the direction of distinction. The path {T, F} → B → single
output is the direction of closure.

---

## 3. The geometric series

The Belnap lattice has a natural geometric reading:

**Point = B**
Zero-dimensional. Pure location, no extension. Both here and not-here — it exists
on the boundary between "is" and "is not" before either is defined. The first
distinction compressed to a singularity. This is ENGAGR: produces B regardless
of input, without requiring prior T or F processing.

**Line = B + N**
One-dimensional. The boundary point (B) extended in an unwritten direction (N).
A trajectory exists, but no content has been written to it yet. This is the wire
between FSPLIT and its matched FFUSE with nothing on either branch — a pure
directed potential, arity satisfied, no tokens in between.

**Square = {B, N, T, F}**
Two-dimensional closure. Inside (T), outside (F), the boundary (B), and the
unmanifest grid that the whole thing sits in (N). The minimal topology that creates
a genuine interior isolated from a genuine exterior. This is the minimal closed
composition: VINIT → FSPLIT → [T-branch | F-branch] → FFUSE → TANCH. The square
does not exist before FSPLIT fires and FFUSE closes it. The closing IS the
creation of inside and outside.

The Euler characteristic V - E + F = 2 holds for every closed convex polyhedron
(all five Platonic solids). This is the topological invariant of a sphere —
any stable, closed, simply-connected 3D boundary satisfies it. In the
imscriptive model this is the checksum: a composition is "closed" (no dangling
shunts, no orphaned tokens) if and only if its shunt graph satisfies the analogous
balance condition. `validate()` in WiredGraph enforces exactly this.

---

## 4. Token mapping

| Token   | Belnap | Geometric role |
|---------|--------|----------------|
| VINIT   | N      | pre-distinction source; unmapped register |
| TANCH   | —      | terminal sink; closes a path |
| FSPLIT  | B act  | the act of making the distinction; δ (co-multiplication) |
| FFUSE   | B close| collecting both branches; μ (multiplication); closes the square |
| EVALT   | T disc | discriminator; extracts T from stream, blocks all else |
| EVALF   | F disc | discriminator; extracts F from stream, blocks all else |
| ENGAGR  | B gen  | unconditional B-generator; the boundary injected as value |
| AFWD    | T lift | VOID→T, FALSE→B; forward morphism adds information |
| AREV    | F lift | VOID→F, TRUE→B; contravariant inversion adds information |
| CLINK   | N sink | TRUE→VOID, FALSE→VOID; collapses discriminated values back to void |
| IMSCRIB | id/T   | VOID→TRUE; identity that lifts from pre-distinction to presence |
| IFIX    | brand  | identity; locks value in place |

EVALT and EVALF do not create T and F. They are filters that pass only the value
that matches their type, returning VOID for everything else. Applied to B, both
return VOID — B contains both T and F but is not reducible to either by filtering.
This is not a defect; it means B can only propagate through the composition
structure itself (wires, FFUSE joins), not through gate-discrimination.

---

## 5. Imscriptive, not holographic

Holographic: the boundary passively encodes the bulk. The boundary is a record.

Imscriptive: the boundary actively reads, writes, and executes on the bulk. The
boundary is an operator. The kernel does not store the world; it runs the world.

In the shunt-graph model: the wires are the boundary. They are not passive
connections between nodes — they carry values, establish ordering, and define what
compositions are possible. Rerouting a wire is not renaming something; it changes
the categorical morphism entirely. This is why cross-branch wiring (wiring.py)
produces genuinely distinct morphisms, not notational variants of the standard
wiring.

The r/w/x loop:
- **Read**: EVALT/EVALF sample the stream and return only what matches their type
- **Write**: FSPLIT distributes a value to two output shunts; FFUSE collects two
  inputs into one; the wire network propagates values forward
- **Execute**: topological layer ordering is the execution sequence; each layer
  is one tick; the composition closes when all shunts are satisfied

---

## 6. Time as execution ordering

Time is not a pre-existing container that computation happens inside. Time is the
partial order induced by the topological sort of the wire graph. Two nodes at the
same topological depth are simultaneous. A node at a deeper layer is "later." A
cross-branch wire that deposits a value from layer 1 to a node at layer 3
(skipping layers 2) is not violating causality — it is establishing that the
layer-1 source is a cause of the layer-3 destination, with no intermediate
computational dependency.

This resolves the apparent paradox from SHAPES.txt: something cannot come from
nothing *in time*, because time IS the execution ordering, and the first
distinction (FSPLIT) is what creates the ordering in the first place. You cannot
ask what happened "before" VINIT for the same reason you cannot stand at the
North Pole and ask which way is North — the reference frame is generated by the
operation, not prior to it.

---

## 7. Why gates fail on B and why that matters

EVALT: B → VOID. EVALF: B → VOID.

The gates are designed to discriminate the classical Boolean values. B is not a
classical value — it is the pre-discriminatory state. Applying a discriminator to
B produces VOID because no discrimination has been made yet; the filter cannot
resolve what is unresolved.

This means a system receiving B as input cannot extract T or F from it by
sequential gate application. It can only:
1. Let B propagate via wires (bypassing gates entirely)
2. Apply ENGAGR (which re-injects B regardless)
3. Route B into FFUSE where it joins with other values (B ∨ x = B for all x)

Cross-branch wires are specifically the mechanism by which B bypasses gate
filtering. In XXI_Paradox_Bridge: ENGAGR produces B; gates on the filtered paths
return VOID; the cross-branch wire delivers B directly to FFUSE's F-shunt,
bypassing the gate entirely. The boundary-level wire is structurally prior to the
gate. This is the imscriptive claim made concrete: the composition structure (the
wire) executes at a deeper layer than the token function (the gate).

---

## 8. The square as the minimal program

VINIT → FSPLIT → FFUSE → TANCH

With empty T and F branches (direct arcs), this is: source a pre-distinction
value, make the distinction, immediately close it, terminate. The result is VOID
in (FFUSE joins VOID+VOID = VOID) and VOID out.

This is not trivially empty. It is the assertion that a distinction can be made
and closed without adding information — that the act of distinguishing is
reversible. This is the Frobenius law μ∘δ = id: splitting and immediately fusing
is identity.

Put tokens between FSPLIT and FFUSE and you add information: T-branch tokens
transform the T-value; F-branch tokens transform the F-value; FFUSE joins them.
The square becomes a computation. The minimal closed form with one token in the
T-branch is the simplest non-trivial program: the act of making a distinction,
processing one branch, closing the distinction. All more complex programs are
composed of these.
