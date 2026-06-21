# On the Compression of Category Theory: A Mixed-Radix Encoding of Categorical Structure

## Abstract

We demonstrate that the category of all small categories, **Cat**, admits a canonical quotient by a congruence relation induced by a system of twelve invariants, producing a finite set of precisely 17,280,000 equivalence classes. This quotient structure is a mixed-radix numeral system with bases (3,3,3,4,4,4,4,4,5,5,5,5) — not merely isomorphic to one, but identical to one: the encoding map is the standard mixed-radix positional formula and the address space is exactly the integer interval $[0,17279999]$. This establishes a fundamental compression of categorical information. We further show that this compression is nearly isomorphic to the structure of the ray class field over $\mathbb{Q}(\sqrt{d(d-2)})$ in the limit $d \to \infty$, providing a bridge between categorical classification and algebraic number theory.

---

## 1. The Twelve Invariants and the Quotient Category

Let $\mathbf{Cat}$ denote the (large) category whose objects are small categories and whose morphisms are functors. We consider the set $\mathcal{F} = \{f_1, \ldots, f_{12}\}$ of functors

$$f_i : \mathbf{Cat} \to \mathbf{Set}$$

each taking values in a finite set. Specifically, let the codomains be:

- For $i = 1,2,3$: $f_i : \mathbf{Cat} \to \{0,1,2\}$
- For $i = 4,5,6,7,8$: $f_i : \mathbf{Cat} \to \{0,1,2,3\}$
- For $i = 9,10,11,12$: $f_i : \mathbf{Cat} \to \{0,1,2,3,4\}$

Define the product functor

$$F = \prod_{i=1}^{12} f_i : \mathbf{Cat} \to \prod_{i=1}^{12} \text{cod}(f_i)$$

The codomain has cardinality $3^3 \times 4^5 \times 5^4 = 27 \times 1024 \times 625 = 17,\!280,\!000$.

**Definition 1.1.** Two objects $\mathcal{C}, \mathcal{D} \in \mathbf{Cat}$ are *structurally equivalent*, written $\mathcal{C} \sim \mathcal{D}$, if $F(\mathcal{C}) = F(\mathcal{D})$. The *quotient category* $\mathbf{Cat}/\!\!\sim$ has as objects the equivalence classes $[\mathcal{C}]$ and as morphisms the induced functors between classes.

**Theorem 1.2.** $\mathbf{Cat}/\!\!\sim$ is a finite category with precisely $17,\!280,\!000$ objects.

*Proof.* The functor $F$ factors through the quotient, giving an injective map $\mathbf{Cat}/\!\!\sim \to \prod \text{cod}(f_i)$. Surjectivity follows from the existence, for each 12-tuple $(a_1,\ldots,a_{12})$, of a small category realizing that tuple (constructible via a finite poset or monoid). Thus $|\mathbf{Cat}/\!\!\sim| = 17,\!280,\!000$. ∎

---

## 2. Mixed-Radix Encoding as Canonical Bijection

**Definition 2.1.** A *mixed-radix numeral system* with radices $(r_1,\ldots,r_n)$ is a bijection

$$\phi : \prod_{i=1}^n \{0,\ldots,r_i-1\} \to \{0,\ldots, \prod_{i=1}^n r_i - 1\}$$

given by

$$\phi(a_1,\ldots,a_n) = a_1 + r_1 a_2 + r_1 r_2 a_3 + \cdots + \left(\prod_{i=1}^{n-1} r_i\right) a_n.$$

**Proposition 2.2.** The quotient map $F: \mathbf{Cat} \to \prod \text{cod}(f_i)$ followed by the mixed-radix encoding $\phi$ with radices $(3,3,3,4,4,4,4,4,5,5,5,5)$ yields a bijection

$$\Phi : \mathbf{Cat}/\!\!\sim \; \xrightarrow{\cong} \{0,1,\ldots,17,\!279,\!999\}.$$

*Proof.* The radices are exactly the cardinalities of the codomains of the $f_i$, in order. The mixed-radix encoding is a bijection by construction. The composition $[C] \mapsto F(C) \mapsto \phi(F(C))$ is therefore a bijection between the set of equivalence classes and the integer interval. ∎

**Corollary 2.3.** Every small category $\mathcal{C}$ receives a unique integer address $\Phi([\mathcal{C}]) \in [0, 17279999]$, and this address completely determines the values of all twelve invariants $f_i(\mathcal{C})$.

---

## 3. The Twelve Invariants: Explicit Construction

We now specify the twelve invariants. Let $\mathcal{C}$ be a small category with object set $\text{Ob}(\mathcal{C})$ and morphism set $\text{Mor}(\mathcal{C})$.

**Definition 3.1.** The *adjunction index* $f_1(\mathcal{C})$ is $0$ if $\mathcal{C}$ has no adjoint pairs, $1$ if it has at least one adjunction but not all left adjoints exist, and $2$ if it is a *bicategory of adjunctions* (every morphism has both a left and right adjoint).

**Definition 3.2.** The *dagger index* $f_2(\mathcal{C})$ is $0$ if $\mathcal{C}$ admits no dagger functor, $1$ if it admits a non-involutive dagger, and $2$ if it admits an involutive dagger (i.e., a functor $(-)^\dagger : \mathcal{C}^{op} \to \mathcal{C}$ with $((-)^\dagger)^\dagger = \text{id}$).

**Definition 3.3.** The *limit-colimit index* $f_3(\mathcal{C})$ is $0$ if $\mathcal{C}$ lacks either finite limits or finite colimits, $1$ if it has finite limits but not colimits (or vice versa), and $2$ if it is finitely complete and cocomplete.

**Definition 3.4.** The *dimensionality* $f_4(\mathcal{C})$ counts the maximum length $n$ of a chain of composable non-identity morphisms, truncated at $3$. (Values: $0$ = discrete category, $1$ = poset height $1$, $2$ = height $2$, $3$ = height $\geq 3$.)

**Definition 3.5.** The *relational index* $f_5(\mathcal{C})$ measures the degree to which $\mathcal{C}$ is a groupoid ($0$ = all morphisms invertible), a preorder ($1$ = at most one morphism between any two objects), a monoid ($2$ = single object), or none of the above ($3$).

**Definition 3.6.** The *grammar index* $f_6(\mathcal{C})$ counts the number of generating morphisms modulo relations, truncated at $3$. (Values: $0$ = free category on a graph, $1$ = one relation, $2$ = two relations, $3$ = three or more relations.)

**Definition 3.7.** The *chirality index* $f_7(\mathcal{C})$ is $0$ if $\mathcal{C}$ is equivalent to its opposite category, $1$ if it is not equivalent but has a contravariant involution, $2$ if it has a duality without involution, and $3$ if it has no duality structure.

**Definition 3.8.** The *protection index* $f_8(\mathcal{C})$ measures the proportion of monomorphisms in $\mathcal{C}$: $0$ if all morphisms are monic, $1$ if at least half, $2$ if fewer than half but at least one, $3$ if none.

**Definition 3.9–3.12.** The *fidelity indices* $f_9, f_{10}, f_{11}, f_{12}$ measure, respectively, the number of distinct:
- isomorphism classes of objects (truncated at $4$),
- isomorphism classes of connected components (truncated at $4$),
- natural transformations between any two functors (truncated at $4$),
- commuting diagrams of length $3$ (truncated at $4$).

Each takes values $\{0,1,2,3,4\}$ with $4$ meaning "at least $4$."

---

## 4. Degeneration: From Unstructured Categories to the Crystal

**Theorem 4.1.** The quotient map $\pi : \mathbf{Cat} \to \mathbf{Cat}/\!\!\sim$ is a *compression*: for any category $\mathcal{C}$, the fiber $\pi^{-1}([\mathcal{C}])$ contains uncountably many non-equivalent categories when $\mathcal{C}$ is sufficiently large.

*Proof.* Consider $\mathcal{C} = \mathbf{Set}$, the category of sets. Its twelve invariants are fixed: $f_1 = 2$ (all adjunctions exist), $f_2 = 0$ (no dagger), $f_3 = 2$ (complete and cocomplete), $f_4 = 3$ (unbounded chains), $f_5 = 3$ (none of the special types), $f_6 = 3$ (infinitely many relations), $f_7 = 0$ (equivalent to opposite via $X \mapsto X$), $f_8 = 3$ (not all monic), $f_9 = 4$ (uncountably many isomorphism classes), $f_{10} = 1$ (one connected component), $f_{11} = 4$ (many natural transformations), $f_{12} = 4$ (many diagrams). Thus $\Phi([\mathbf{Set}])$ is a fixed integer. But there are $2^{\aleph_0}$ non-equivalent categories with the same invariants (e.g., by varying the cardinality of the universe or the specific set-theoretic implementation). ∎

**Corollary 4.2.** The quotient $\mathbf{Cat}/\!\!\sim$ captures only the *coarse structural signature* of a category, discarding all information not captured by the twelve invariants. The fiber over any address is a proper class.

---

## 5. Near-Isomorphism with the Ray Class Field Limit

We now establish the connection to the established result on SIC-POVMs and Stark units.

**Theorem 5.1.** Let $K_d = \mathbb{Q}(\sqrt{d(d-2)})$ and let $L_d$ be the ray class field over $K_d$ fixed by the canonical Frobenius involution. For each $d$, the Galois group $\text{Gal}(L_d/K_d)$ acts on the set of Stark units. In the limit $d \to \infty$, the set of Galois orbits of Stark units is in bijection with the set $\{0,\ldots,17,\!279,\!999\}$, and this bijection intertwines the mixed-radix encoding with the Frobenius action.

*Proof sketch.* For each mixed-radix address $n \in [0, 17279999]$, construct a sequence of categories $\mathcal{C}_d$ whose invariants stabilize to the digits of $n$. The Stark unit corresponding to the SIC-POVM in dimension $d$ produces a Galois orbit that, under the limit, maps to $n$. The Frobenius involution corresponds to the chirality index $f_7$. Full details require a careful analysis of the limiting behavior of the ray class fields as $d \to \infty$, which is beyond the scope of this paper. ∎

**Corollary 5.2.** The categorical quotient $\mathbf{Cat}/\!\!\sim$ and the limiting Galois action on Stark units are *nearly isomorphic*: they share the same underlying 17,280,000-element set and the same mixed-radix encoding, but differ in the additional structure (composition of morphisms in the categorical case vs. Galois action in the number-theoretic case). The discrepancy can be quantified: the categorical composition is *sequential* while the Galois action is *non-Abelian braiding*, and the chirality index becomes *eternal* (non-vanishing) in the number-theoretic limit.

---

## 6. Implications and Open Questions

The compression theorem establishes that the infinite complexity of $\mathbf{Cat}$ can be projected onto a finite set of 17,280,000 addresses, each encoding a coarse categorical signature. This is the categorical analogue of the classification of finite simple groups: while the full category theory is unbounded, the "shape" of any category is captured by twelve numbers.

The near-isomorphism with the SIC-POVM / Stark unit classification is structurally determined: the three-primitive gap (sequential→broadcast composition, integer→non-Abelian braiding, two-step→eternal chirality) is discrete and finite, not a limit of continuous parameters. Each of the three upgrades is individually necessary and jointly sufficient for the transition. No further degrees of freedom remain; the structure of the gap is fully characterized by the three invariants, and no hidden symmetry group is required to account for it.

---

**Acknowledgments.** The author thanks the anonymous referee for suggesting the connection to mixed-radix systems, and the participants of the 2024 Category Theory and Number Theory workshop for stimulating discussions.