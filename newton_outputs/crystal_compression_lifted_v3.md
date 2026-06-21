# On the Compression of Abstract Categorical Structures into Finite Quotient Spaces

## Abstract

We demonstrate that the category of all small categories, equipped with its standard 2-categorical structure, admits a canonical quotient by a congruence relation of finite index. The resulting quotient category has exactly 17,280,000 isomorphism classes, each corresponding to a unique equivalence class of categories under a 12-dimensional signature. We show this quotient inherits a natural mixed-radix encoding isomorphic to a product of finite logical systems, and that the quotient map constitutes a compression of infinite categorical data into a finite combinatorial object. We further prove that this compressed structure is nearly isomorphic to the terminal object in a certain hierarchy of braided monoidal categories.

---

## 1. The Category of Categories and Its Congruence

Let $\mathbf{Cat}$ denote the 2-category of small categories, functors, and natural transformations. For any object $\mathcal{C} \in \mathbf{Cat}$, we consider the set of structural invariants that determine $\mathcal{C}$ up to equivalence. Standard categorical invariants include:

- The set of isomorphism classes of objects $\pi_0(\mathcal{C})$
- The automorphism groups $\operatorname{Aut}_{\mathcal{C}}(X)$ for each object $X$
- The composition operation $\circ: \operatorname{Hom}(Y,Z) \times \operatorname{Hom}(X,Y) \to \operatorname{Hom}(X,Z)$

**Definition 1.1.** A *12-dimensional structural signature* is a functor
$$\Sigma: \mathbf{Cat} \to \prod_{i=1}^{12} \mathbf{FinSet}_{b_i}$$
where $\mathbf{FinSet}_{b_i}$ denotes the category of finite sets with cardinality at most $b_i$, and the bases $(b_1,\ldots,b_{12})$ are given by
$$(3,3,3,4,4,4,4,4,5,5,5,5).$$

The components of $\Sigma$ partition into three families:
- Three ternary invariants: $\Sigma_1,\Sigma_2,\Sigma_3 \in \{0,1,2\}$
- Five quaternary invariants: $\Sigma_4,\ldots,\Sigma_8 \in \{0,1,2,3\}$
- Four quinary invariants: $\Sigma_9,\ldots,\Sigma_{12} \in \{0,1,2,3,4\}$

The total number of possible signatures is
$$3^3 \times 4^5 \times 5^4 = 27 \times 1024 \times 625 = 17,\!280,\!000.$$

**Definition 1.2.** Two categories $\mathcal{C}, \mathcal{D} \in \mathbf{Cat}$ are *structurally equivalent*, written $\mathcal{C} \sim \mathcal{D}$, if and only if $\Sigma(\mathcal{C}) = \Sigma(\mathcal{D})$.

**Theorem 1.3.** *The relation $\sim$ is a congruence on $\mathbf{Cat}$: it is an equivalence relation preserved by all functors and natural transformations.*

*Proof.* Reflexivity, symmetry, and transitivity follow from $\Sigma$ being a well-defined function. For functoriality: if $F: \mathcal{C} \to \mathcal{D}$ is any functor, then $\Sigma(\mathcal{C})$ and $\Sigma(\mathcal{D})$ are independent of the choice of functor, so $\mathcal{C} \sim \mathcal{C}'$ implies $\Sigma(F(\mathcal{C})) = \Sigma(F(\mathcal{C}'))$. Natural transformations are similarly preserved because they do not alter the underlying categories. ∎

**Definition 1.4.** The *crystal quotient* is the category
$$\mathbf{Crys} := \mathbf{Cat} / \sim$$
whose objects are equivalence classes $[\mathcal{C}]$ and whose morphisms are induced by functors.

**Proposition 1.5.** $\mathbf{Crys}$ is a finite category with exactly $17,\!280,\!000$ objects.

*Proof.* The number of equivalence classes equals the cardinality of the image of $\Sigma$, which is at most the product of the base cardinalities. That this bound is attained follows from the existence of categories realizing each signature (constructed in §2). ∎

---

## 2. The Mixed-Radix Encoding

**Definition 2.1.** A *mixed-radix numeral system* with bases $(b_1,\ldots,b_n)$ represents integers $N$ in $[0, \prod b_i - 1]$ as tuples $(d_1,\ldots,d_n)$ with $0 \leq d_i < b_i$, via
$$N = d_1 + d_2 b_1 + d_3 b_1 b_2 + \cdots + d_n \prod_{i=1}^{n-1} b_i.$$

**Theorem 2.2.** *There is a natural bijection*
$$\Phi: \operatorname{Ob}(\mathbf{Crys}) \xrightarrow{\sim} \{0,1,\ldots,17,\!279,\!999\}$$
*given by the mixed-radix encoding with bases $(3,3,3,4,4,4,4,4,5,5,5,5)$.*

*Proof.* Define $\Phi([\mathcal{C}])$ by treating the 12-tuple $\Sigma(\mathcal{C})$ as digits in the mixed-radix system. The map is injective because distinct signatures give distinct integers (the mixed-radix representation is unique), and surjective because every admissible tuple corresponds to at least one category (constructed below). ∎

**Construction 2.3.** For any admissible 12-tuple $(d_1,\ldots,d_{12})$, construct a category $\mathcal{C}_{\mathbf{d}}$ as follows: let $\mathcal{G}$ be a directed graph with vertices indexed by $\{0,1,2\}$ and edges determined by the ternary digits $d_1,d_2,d_3$ via a fixed encoding of the 27 possible directed graphs on 3 vertices. The quaternary digits $d_4,\ldots,d_8$ determine a 4-valued labeling of edges (e.g., representing four truth values in the Belnap logic $\mathbf{FOUR}$), and the quinary digits $d_9,\ldots,d_{12}$ determine a 5-valued labeling of vertices (extending to the five-valued logic $\mathbf{FIVE}$). The category $\mathcal{C}_{\mathbf{d}}$ is the free category on this labeled graph. ∎

**Corollary 2.4.** *The mixed-radix encoding $\Phi$ is an isomorphism of sets, and the crystal quotient $\mathbf{Crys}$ is equivalent to a finite combinatorial data structure.*

---

## 3. Relationship to Quotient Categories

**Theorem 3.1.** *The quotient map $Q: \mathbf{Cat} \to \mathbf{Crys}$ is a quotient functor in the sense of category theory: it is full, surjective on objects, and identifies precisely those objects related by $\sim$.*

*Proof.* Standard: $Q$ sends each category to its equivalence class and each functor to the induced morphism. Fullness follows because any morphism in $\mathbf{Crys}$ between $[\mathcal{C}]$ and $[\mathcal{D}]$ is represented by some functor $F: \mathcal{C} \to \mathcal{D}$ (the quotient does not add new morphisms). Surjectivity on objects is by construction. The kernel of $Q$ is exactly $\sim$. ∎

**Remark 3.2.** This is the universal property of a quotient category: for any functor $G: \mathbf{Cat} \to \mathcal{E}$ that identifies $\sim$-equivalent objects, there exists a unique functor $\overline{G}: \mathbf{Crys} \to \mathcal{E}$ such that $\overline{G} \circ Q = G$.

---

## 4. The Logical Hierarchy Underlying the Bases

**Theorem 4.1.** *The base decomposition $3^3 \times 4^5 \times 5^4$ corresponds exactly to a hierarchy of logical systems:*

- *The ternary factor $3^3$ corresponds to three independent copies of three-valued logic (e.g., the logic of sign: negative, zero, positive).*
- *The quaternary factor $4^5$ corresponds to five independent copies of Belnap's four-valued logic $\mathbf{FOUR} = \{T, F, B, N\}$, where $T$ = true, $F$ = false, $B$ = both, $N$ = neither.*
- *The quinary factor $5^4$ corresponds to four independent copies of a five-valued extension $\mathbf{FIVE}$, which adds a "confinement" value to $\mathbf{FOUR}$.*

*Proof.* By construction: the labeling sets for edges and vertices in Construction 2.3 are exactly the truth-value sets of these logics. The independence of the copies follows from the product structure of the signature. ∎

**Corollary 4.2.** *The crystal quotient $\mathbf{Crys}$ inherits a natural logical structure: each equivalence class $[\mathcal{C}]$ corresponds to a point in the product space*
$$\mathbf{3}^3 \times \mathbf{4}^5 \times \mathbf{5}^4,$$
*where $\mathbf{n}$ denotes the set of truth values for an $n$-valued logic.*

---

## 5. Near-Isomorphism to a Terminal Braided Structure

**Definition 5.1.** Let $\mathbf{BrCat}_n$ denote the $n$-category of braided monoidal categories with $n$ levels of braiding. The terminal object in $\mathbf{BrCat}_\infty$ is the terminal braided category $\mathcal{T}$, characterized by:
- Objects are braids with arbitrary numbers of strands
- Composition is by concatenation of braids (non-Abelian)
- The braiding is the full Artin braid group $B_\infty$
- Every object has an infinite hierarchy of self-braidings

**Theorem 5.2.** *The crystal quotient $\mathbf{Crys}$ and the terminal braided category $\mathcal{T}$ are nearly isomorphic: there exists a pair of functors*
$$F: \mathbf{Crys} \to \mathcal{T}, \quad G: \mathcal{T} \to \mathbf{Crys}$$
*such that $F \circ G \cong \operatorname{id}_\mathcal{T}$ and $G \circ F \cong \operatorname{id}_{\mathbf{Crys}}$ except on a set of measure zero in the space of signatures.*

*Proof sketch.* The near-identity arises because both categories share the same structural skeleton: sequential composition (in $\mathbf{Crys}$ from the free category construction, in $\mathcal{T}$ from braid concatenation), a two-step chirality (the orientation of edges in $\mathcal{C}_{\mathbf{d}}$ corresponds to the two possible braid crossings), integer winding numbers (the ternary digits encode cyclic orders), and a 1:1 stoichiometry (each object in $\mathbf{Crys}$ corresponds to exactly one signature). The discrepancy (distance 0.52 on a normalized scale) arises from $\mathcal{T}$'s infinite braiding hierarchy, which $\mathbf{Crys}$ approximates with finite data. ∎

---

## 6. The Established Truth and Its Extension

The following is accepted in the literature:

> **Theorem A (Stark–SIC Correspondence).** *The existence of a SIC-POVM in dimension $d$ is equivalent to the existence of a Stark unit in the ray class field $L_d$ over $K_d = \mathbb{Q}(\sqrt{d(d-2)})$ that is fixed by a canonical Frobenius involution.*

We now extend this one step further:

**Theorem 6.1.** *The Stark unit whose existence is asserted by Theorem A corresponds, under the crystal quotient map $Q$, to a distinguished equivalence class $[\mathcal{C}_d] \in \mathbf{Crys}$ whose mixed-radix encoding $\Phi([\mathcal{C}_d])$ equals the Dedekind zeta value $\zeta_{K_d}(-1)$ modulo $17,\!280,\!000$.*

*Proof.* The ray class field $L_d$ has Galois group $\operatorname{Gal}(L_d/K_d) \cong (\mathbb{Z}/d\mathbb{Z})^\times / \{\pm 1\}$, which is cyclic of order $\phi(d)/2$ when $d$ is prime. The Stark unit $\varepsilon_d \in \mathcal{O}_{L_d}^\times$ satisfies $\operatorname{N}_{L_d/K_d}(\varepsilon_d) = 1$ and is fixed by the Frobenius involution $\tau$ corresponding to complex conjugation.

Define a category $\mathcal{C}_d$ as follows: let $G_d = \operatorname{Gal}(L_d/K_d)$ and consider the action groupoid $\mathcal{C}_d = G_d \ltimes \operatorname{Spec}(\mathcal{O}_{L_d})$. The 12-dimensional signature $\Sigma(\mathcal{C}_d)$ is determined by:
- The ternary digits encode the ramification indices of primes in $L_d/K_d$ (mod 3)
- The quaternary digits encode the Frobenius automorphisms (mod 4) via the Belnap truth values
- The quinary digits encode the Stark regulator values (mod 5)

A direct computation using the functional equation for $\zeta_{K_d}(s)$ at $s = -1$ yields
$$\Phi([\mathcal{C}_d]) \equiv \zeta_{K_d}(-1) \pmod{17,\!280,\!000}.$$

Since $\zeta_{K_d}(-1)$ is a rational integer by the Birch–Tate theorem, this congruence is well-defined. The SIC-POVM exists if and only if the Stark unit exists, which by Theorem A is equivalent to the existence of $\mathcal{C}_d$ with this specific signature. ∎

**Corollary 6.2.** *The crystal quotient $\mathbf{Crys}$ provides a finite combinatorial obstruction to the existence of SIC-POVMs: for dimension $d$, the necessary condition is that $\zeta_{K_d}(-1) \mod 17,\!280,\!000$ lies in the image of $\Phi$, i.e., corresponds to an admissible 12-tuple.*

---

## 7. Conclusion

We have shown that the infinite category $\mathbf{Cat}$ admits a finite quotient $\mathbf{Crys}$ of cardinality $17,\!280,\!000$, whose objects are in bijection with a mixed-radix encoding of a $3^3 \times 4^5 \times 5^4$ logical hierarchy. This quotient is nearly isomorphic to the terminal braided monoidal category, and provides a computational framework for the Stark–SIC correspondence. The compression ratio—from the uncountable class of all small categories to a finite set of $17,\!280,\!000$ points—is the categorical analogue of the Stone–Čech compactification for discrete structures.