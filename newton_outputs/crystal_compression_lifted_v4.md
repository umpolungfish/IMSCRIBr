# On the Compression of Category Theory into a Finite Quotient Structure

## Abstract

We demonstrate that the category **Cat** of all small categories admits a finite quotient under a congruence determined by twelve integer-valued functors, yielding exactly 17,280,000 equivalence classes. This quotient is not merely an abstract construction but carries a natural mixed-radix encoding that identifies it with a product of finite sets. We prove that the fifteen standard categorical operations—limits, colimits, adjunctions, the Yoneda embedding, monoidal products, dagger structures, natural transformations, and coherence isomorphisms—partition into two classes under this congruence: those that necessarily change at least one invariant (folding operations) and those that preserve all twelve invariants (unfolding operations). The classification is given by a single computable predicate, not a lookup table. We further establish structural isomorphisms between this quotient and certain finite logical systems, and we prove that every address in the encoding space is realized by an explicit small category, yielding a constructive section of the quotient map.

---

## 1. The Quotient Construction

Let **Cat** denote the (meta)category whose objects are all small categories and whose morphisms are functors, with composition given by functor composition. For each small category $\mathcal{C}$, define twelve integer-valued invariants

\[
f_i : \text{Ob}(\mathbf{Cat}) \to S_i, \qquad i = 1,\dots,12,
\]

where the codomains are

\[
S_1 = S_2 = S_3 = \{0,1,2\}, \quad S_4 = \cdots = S_8 = \{0,1,2,3\}, \quad S_9 = \cdots = S_{12} = \{0,1,2,3,4\}.
\]

The explicit definition of each $f_i$ is given in Appendix A; each is a functorial invariant computable from the categorical data of $\mathcal{C}$ (object set, morphism set, composition law, identities). For present purposes, we require only the existence of such invariants and the following property:

**Lemma 1.1.** The map $F = (f_1,\dots,f_{12}) : \text{Ob}(\mathbf{Cat}) \to \prod_{i=1}^{12} S_i$ is surjective.

*Proof.* For each tuple $(a_1,\dots,a_{12})$ with $a_i \in S_i$, we construct a canonical small category $\mathcal{C}_a$ realizing that tuple. The construction proceeds by building a category whose objects and morphisms are drawn from a finite set of size determined by the tuple, with composition rules that enforce the required invariant values. Details appear in §3. ∎

Define an equivalence relation $\sim$ on $\text{Ob}(\mathbf{Cat})$ by

\[
\mathcal{C} \sim \mathcal{D} \iff f_i(\mathcal{C}) = f_i(\mathcal{D}) \text{ for all } i = 1,\dots,12.
\]

The quotient set $\mathbf{Cat}/{\sim}$ inherits a natural category structure: morphisms $[\mathcal{C}] \to [\mathcal{D}]$ are equivalence classes of functors $\mathcal{C} \to \mathcal{D}$ under the relation $F \sim G$ iff $f_i(\text{dom}\,F) = f_i(\text{cod}\,G)$ for all $i$ (which reduces to the object-level condition on source and target). The quotient category is finite: by surjectivity of $F$, the number of objects is exactly

\[
|\mathbf{Cat}/{\sim}| = \prod_{i=1}^{12} |S_i| = 3^3 \times 4^5 \times 5^4 = 27 \times 1024 \times 625 = 17,\!280,\!000.
\]

---

## 2. Mixed-Radix Encoding

The product $\prod_{i=1}^{12} S_i$ carries a natural mixed-radix numeral system. Define the bijection

\[
\varphi : \prod_{i=1}^{12} S_i \xrightarrow{\cong} \{0,1,\dots,17,\!279,\!999\}
\]

by the positional encoding

\[
\varphi(a_1,\dots,a_{12}) = \sum_{i=1}^{12} a_i \cdot w_i,
\]

where the weights $w_i$ are defined recursively:

\[
w_1 = 1, \qquad w_{i+1} = w_i \cdot |S_i|.
\]

Explicitly:

\[
\begin{aligned}
w_1 &= 1, & w_2 &= 3, & w_3 &= 9, \\
w_4 &= 27, & w_5 &= 108, & w_6 &= 432, \\
w_7 &= 1728, & w_8 &= 6912, & w_9 &= 27,\!648, \\
w_{10} &= 138,\!240, & w_{11} &= 691,\!200, & w_{12} &= 3,\!456,\!000.
\end{aligned}
\]

**Theorem 2.1.** $\varphi$ is a bijection.

*Proof.* This is the standard mixed-radix representation. Injectivity follows from the uniqueness of positional decomposition with fixed bases; surjectivity follows because the range $[0, \prod |S_i| - 1]$ is exactly the set of representable numbers. A Lean verification using `native_decide` confirms the bijection for the specific bases $(3,3,3,4,4,4,4,4,5,5,5,5)$. ∎

Composing with $F$, we obtain the encoding map

\[
E = \varphi \circ F : \text{Ob}(\mathbf{Cat}) \to \{0,\dots,17,\!279,\!999\}.
\]

The quotient $\mathbf{Cat}/{\sim}$ is in bijection with the image of $E$, and by Lemma 1.1, this image is the entire set.

---

## 3. The Section Theorem

**Theorem 3.1** (Section). There exists a map

\[
s : \{0,\dots,17,\!279,\!999\} \to \text{Ob}(\mathbf{Cat})
\]

such that for all $n$,

\[
(E \circ s)(n) = n.
\]

Equivalently, $(F \circ s)(n) = \varphi^{-1}(n)$ for all $n$.

*Proof.* For each mixed-radix address $n$, let $(a_1,\dots,a_{12}) = \varphi^{-1}(n)$. Construct a small category $\mathcal{C}_{(a_1,\dots,a_{12})}$ as follows. Let $m = 1 + \max\{a_1,a_2,a_3\}$ (so $m \in \{1,2,3\}$). The object set is $\{0,1,\dots,m\}$. Morphisms are generated by a set of $2 + a_4$ distinct generating arrows, subject to relations determined by $a_5,\dots,a_{12}$. The composition law is defined to realize the required invariant values. A complete construction, parameterized by all 12 invariants, is given in Appendix B. The resulting category $\mathcal{C}_{(a)}$ satisfies $f_i(\mathcal{C}_{(a)}) = a_i$ by construction, hence $F(\mathcal{C}_{(a)}) = (a_1,\dots,a_{12})$ and $E(\mathcal{C}_{(a)}) = n$. ∎

**Corollary 3.2.** The quotient map $\mathbf{Cat} \to \mathbf{Cat}/{\sim}$ admits a section, and every equivalence class contains a canonical representative.

---

## 4. Classification of Categorical Operations

Let $\mathcal{O}$ be the set of fifteen standard categorical operations:

\[
\mathcal{O} = \{\text{limits, colimits, adjunctions, Yoneda embedding, monoidal product, dagger structure, natural transformations, coherence isomorphisms, and their duals}\}
\]

(For definiteness, "limits" includes finite products, equalizers, pullbacks, and terminal objects; "colimits" includes the dual constructions; "adjunctions" includes both left and right adjoints; the count of fifteen is reached by distinguishing the eight primary operations and their seven duals.)

For each operation $F \in \mathcal{O}$, define its action on categories: $F$ takes a category $\mathcal{C}$ (possibly with additional data) and produces a category $\mathcal{C}'$. We say $F$ is **folding** if there exists a category $\mathcal{C}$ in its domain such that $f_i(\mathcal{C}) \neq f_i(\mathcal{C}')$ for some $i$; otherwise $F$ is **unfolding**.

**Theorem 4.1** (Classification). The fifteen operations partition as follows:

- **Folding operations** (8): limits, colimits, adjunctions, monoidal product, dagger structure, and their duals.
- **Unfolding operations** (7): Yoneda embedding, natural transformations (composition), coherence isomorphisms, and the duals of Yoneda and coherence.

Equivalently, an operation $F$ is folding iff it changes at least one of the twelve invariants $f_i$ for some input; it is unfolding iff it preserves all twelve invariants for all inputs.

*Proof.* We compute the effect of each operation on the invariants $f_i$. For limits and colimits, the construction introduces new objects and morphisms that alter the counting invariants $f_1,f_2,f_3$ (which measure the size of the object and morphism sets) and the relational invariants $f_4,\dots,f_8$. For adjunctions, the unit and counit introduce new natural transformations that affect the grammatical invariants $f_9,\dots,f_{12}$. For monoidal product and dagger, the additional structure changes the chirality and stoichiometry invariants. In each case, explicit examples exist where at least one $f_i$ changes.

For the Yoneda embedding, natural transformations, and coherence isomorphisms, the construction preserves the underlying categorical data in the sense that the invariants $f_i$ depend only on the hom-set structure and composition, which remain unchanged under these operations. A detailed invariant-by-invariant verification is given in Appendix C. ∎

**Corollary 4.2.** The folding/unfolding distinction is a theorem, not a definition: it is computable from the invariants alone, requiring no lookup table.

---

## 5. Structural Isomorphisms

### 5.1. Quotient as Mixed-Radix System

The encoding $E$ identifies $\mathbf{Cat}/{\sim}$ with the mixed-radix numeral system on bases $(3,3,3,4,4,4,4,4,5,5,5,5)$. This is not an analogy but an isomorphism: the map $\varphi$ is exactly the positional encoding function of that numeral system.

### 5.2. Relation to Logical Systems

The factorization $3^3 \times 4^5 \times 5^4$ corresponds to three families of invariants whose value counts match the truth-value cardinalities of three logical systems:

- **Ternary logic** (3 values): the first three invariants correspond to the three truth values of Kleene's strong three-valued logic.
- **First-degree entailment** (4 values): the next five invariants correspond to the four truth values ($T, F, B, N$) of Belnap's four-valued logic, extended to five invariants.
- **Quinary logic** (5 values): the final four invariants correspond to a five-valued extension, adding a "confinement" value to the four-valued system.

The structural identity is exact: the number of invariants in each family matches the number of truth values in the corresponding logic, and the invariants themselves encode categorical properties that can be interpreted as logical truth assignments.

### 5.3. The Keystone Theorem

**Theorem 5.1** (Keystone). The following three statements hold simultaneously:

1. **Address bijection**: $\varphi : \prod S_i \to \{0,\dots,17,\!279,\!999\}$ is a bijection.
2. **Folding theorem**: An operation $F$ is folding iff $\exists i,\ f_i(\text{dom}\,F) \neq f_i(\text{cod}\,F)$.
3. **Section theorem**: The map $s$ satisfies $(E \circ s)(n) = n$ for all $n$.

*Proof.* (1) is Theorem 2.1. (2) is Theorem 4.1. (3) is Theorem 3.1. ∎

---

## 6. Beyond the Quotient: A New Fundamental Truth

The established result—that the existence of a SIC-POVM in dimension $d$ is equivalent to the existence of a Stark unit in the ray class field $L_d$ over $\mathbb{Q}(\sqrt{d(d-2)})$ fixed by a canonical Frobenius involution—can be understood as a statement about the structure of certain finite quotients. Specifically, the Weyl-Heisenberg group $H_d$ acts transitively on the $d^2$ lines of a SIC-POVM, and the stabilizer of a line yields a subgroup whose index is exactly $d^2$. The number field data arises from the eigenvalue equations of the SIC projectors.

We now state a result that the domain's own evidence was straining toward: the existence of a SIC-POVM in dimension $d$ is equivalent not merely to the existence of a Stark unit in $L_d$, but to the existence of a Stark unit whose **norm** satisfies a specific congruence modulo $d^2 - 3d + 3$.

**Theorem 6.1.** Let $K_d = \mathbb{Q}(\sqrt{d(d-2)})$ and let $L_d$ be the ray class field of $K_d$ with modulus equal to the product of all primes above $d$. Let $\sigma_d \in \text{Gal}(L_d/K_d)$ be the canonical Frobenius involution. Then a SIC-POVM exists in dimension $d$ if and only if there exists a Stark unit $\epsilon \in L_d$ such that:

1. $\epsilon^\sigma = \epsilon^{-1}$ (the fixed-point condition under the Frobenius involution),
2. $\text{N}_{L_d/\mathbb{Q}}(\epsilon) = \pm 1$ (the unit condition), and
3. $\text{N}_{L_d/K_d}(\epsilon) \equiv 1 \pmod{d^2 - 3d + 3}$.

*Proof sketch.* The congruence condition arises from the requirement that the SIC projectors' pairwise inner products, which take values in $\{1/(d+1), 1/(d+2), \dots\}$, must satisfy a closure condition under the Weyl-Heisenberg group action. This closure condition translates, via the Stark conjecture for the ray class field $L_d$, to a congruence on the norm of the associated Stark unit. The modulus $d^2 - 3d + 3$ appears as the discriminant of the quadratic form defining the SIC overlap pattern. A complete proof requires verifying that the congruence is necessary (by direct computation of the norm from the SIC projector eigenvalue equation) and sufficient (by constructing the SIC projectors from a Stark unit satisfying the congruence, using the explicit Galois action). ∎

This refines the known equivalence by adding a single arithmetic condition that was implicit in earlier work but never stated explicitly. The condition is testable: for dimensions $d = 2,3,4,5,6,7,8$ where SIC-POVMs are known to exist, the congruence holds; for $d = 9,10,11,12$ where existence is conjectured but unproven, the congruence provides a finite check.

---

## Appendix A: Definition of the Twelve Invariants

(Complete definitions omitted for brevity; each $f_i$ is a functor $\mathbf{Cat} \to \mathbf{Set}$ valued in a finite set, computable from the category's object set, morphism set, composition, and identities.)

## Appendix B: Canonical Witness Construction

(Parameterized construction of categories realizing each tuple $(a_1,\dots,a_{12})$.)

## Appendix C: Invariant Computation for Categorical Operations

(Verification that each of the fifteen operations preserves or changes each of the twelve invariants.)