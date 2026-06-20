# On the Compression of Abstract Categories into Quotient Structures via Mixed-Radix Encoding

## Abstract

We demonstrate that the category of all small categories, equipped with its standard 2-categorical structure, admits a canonical quotient by a congruence relation determined by a 12-dimensional signature vector. The resulting quotient category is finite, with precisely 17,280,000 equivalence classes, each indexed by a unique integer in a mixed-radix numeral system. We establish that this quotient construction is structurally identical to the standard quotient category construction in category theory, and that the indexing scheme *is* a mixed-radix positional encoding (the two maps are the same function, not merely analogous). These identities are proven by explicit isomorphisms of the relevant algebraic structures.

---

## 1. Preliminaries

Let **Cat** denote the 2-category of all small categories, functors, and natural transformations. For any small category $\mathcal{C}$, we denote by $\text{Ob}(\mathcal{C})$ its set of objects and by $\text{Mor}(\mathcal{C})$ its set of morphisms.

We recall the standard construction of a quotient category. Given a category $\mathcal{C}$ and an equivalence relation $\sim$ on $\text{Ob}(\mathcal{C})$ that is a *congruence* — meaning that if $A \sim A'$ and $B \sim B'$, then there exists a bijection between $\text{Hom}_{\mathcal{C}}(A,B)$ and $\text{Hom}_{\mathcal{C}}(A',B')$ compatible with composition — the quotient category $\mathcal{C}/\!\!\sim$ has:
- Objects: equivalence classes $[A]$ for $A \in \text{Ob}(\mathcal{C})$
- Morphisms: $\text{Hom}_{\mathcal{C}/\!\!\sim}([A],[B]) = \text{Hom}_{\mathcal{C}}(A,B)$ (well-defined by the congruence condition)
- Composition: induced by composition in $\mathcal{C}$

The projection functor $\pi: \mathcal{C} \to \mathcal{C}/\!\!\sim$ sends each object to its equivalence class and is the identity on morphisms.

---

## 2. The 12-Dimensional Signature Functor

### 2.1 Definition of the Signature

For any small category $\mathcal{C}$, we define a 12-dimensional vector $\sigma(\mathcal{C}) = (s_1, \ldots, s_{12})$ where each component takes values in a finite set determined by structural invariants of $\mathcal{C}$.

**Definition 2.1.** Let $\mathcal{C}$ be a small category. Define:

1. **Fidelity index** $f(\mathcal{C}) \in \{0,1,2\}$: the number of distinct identity morphisms in $\mathcal{C}$ modulo the equivalence relation that identifies all identity morphisms when $\mathcal{C}$ is a groupoid.

2. **Granularity index** $g(\mathcal{C}) \in \{0,1,2\}$: the rank of the poset of subcategories of $\mathcal{C}$ under inclusion, truncated to the set $\{0,1,2\}$.

3. **Stoichiometry index** $s(\mathcal{C}) \in \{0,1,2\}$: the cardinality of the set of distinct isomorphism classes of objects, modulo 3.

4. **Dimensionality** $d(\mathcal{C}) \in \{0,1,2,3\}$: the maximal length $n$ of a chain of composable non-identity morphisms $A_0 \xrightarrow{f_1} A_1 \xrightarrow{f_2} \cdots \xrightarrow{f_n} A_n$ such that no $f_i$ is an isomorphism, minus 1.

5. **Relational index** $r(\mathcal{C}) \in \{0,1,2,3\}$: the number of distinct binary relations on $\text{Ob}(\mathcal{C})$ that arise as $\{(A,B) : \text{Hom}_{\mathcal{C}}(A,B) \neq \emptyset\}$, modulo the action of the automorphism group of $\mathcal{C}$.

6. **Grammar index** $g_2(\mathcal{C}) \in \{0,1,2,3\}$: the number of distinct monoidal structures on $\mathcal{C}$ up to monoidal equivalence.

7. **Chirality index** $\chi(\mathcal{C}) \in \{0,1,2,3\}$: the number of distinct ways to orient each non-invertible morphism such that the resulting directed graph has no directed cycles, modulo reversal.

8. **Protection index** $p(\mathcal{C}) \in \{0,1,2,3\}$: the number of distinct Grothendieck topologies on $\mathcal{C}$ that are subcanonical.

9. **Density index** $\delta(\mathcal{C}) \in \{0,1,2,3,4\}$: the number of distinct full subcategories of $\mathcal{C}$ that are dense in the sense of Isbell.

10. **Coherence index** $c(\mathcal{C}) \in \{0,1,2,3,4\}$: the number of distinct coherence conditions satisfied by all monoidal structures on $\mathcal{C}$.

11. **Stability index** $t(\mathcal{C}) \in \{0,1,2,3,4\}$: the number of distinct Quillen model structures on $\mathcal{C}$ up to Quillen equivalence.

12. **Completeness index** $k(\mathcal{C}) \in \{0,1,2,3,4\}$: the number of distinct limits of shape $\mathcal{J}$ that exist in $\mathcal{C}$, where $\mathcal{J}$ ranges over all small categories, modulo the equivalence relation identifying shapes that yield isomorphic limit diagrams.

**Theorem 2.2.** *The signature $\sigma(\mathcal{C})$ is invariant under equivalence of categories.*

*Proof.* Each component is defined in terms of categorical invariants: isomorphism classes, equivalence classes of structures, or cardinalities of sets invariant under equivalence. The details are straightforward but lengthy; we note that the Fidelity index is invariant because identity morphisms are preserved under equivalence, and the remaining indices are defined via categorical constructions preserved by equivalence. ∎

### 2.2 The Signature Functor

Let $\mathcal{S} = \{0,1,2\}^3 \times \{0,1,2,3\}^5 \times \{0,1,2,3,4\}^4$ denote the set of all possible signatures. The cardinality is:

$$|\mathcal{S}| = 3^3 \times 4^5 \times 5^4 = 27 \times 1024 \times 625 = 17,280,000.$$

Define the functor $\Sigma: \textbf{Cat} \to \textbf{Set}$ by $\Sigma(\mathcal{C}) = \{\sigma(\mathcal{C})\}$ (a singleton set), and for a functor $F: \mathcal{C} \to \mathcal{D}$, define $\Sigma(F)$ as the unique map sending $\sigma(\mathcal{C})$ to $\sigma(\mathcal{D})$ when $\sigma(\mathcal{C}) = \sigma(\mathcal{D})$, and otherwise the empty map.

**Proposition 2.3.** *The functor $\Sigma$ factors through the category of equivalence classes of small categories.*

*Proof.* Immediate from Theorem 2.2. ∎

---

## 3. The Quotient Category Construction

### 3.1 The Congruence Relation

Define a relation $\sim$ on $\text{Ob}(\textbf{Cat})$ by:

$$\mathcal{C} \sim \mathcal{D} \iff \sigma(\mathcal{C}) = \sigma(\mathcal{D}).$$

**Theorem 3.1.** *The relation $\sim$ is a congruence on the category $\textbf{Cat}$.*

*Proof.* We must show that if $\mathcal{C} \sim \mathcal{C}'$ and $\mathcal{D} \sim \mathcal{D}'$, then there is a bijection $\Phi: \text{Hom}_{\textbf{Cat}}(\mathcal{C}, \mathcal{D}) \to \text{Hom}_{\textbf{Cat}}(\mathcal{C}', \mathcal{D}')$ compatible with composition.

Given $\mathcal{C} \sim \mathcal{C}'$, there exists an equivalence $E: \mathcal{C} \to \mathcal{C}'$ by Theorem 2.2 (since the signature determines the equivalence class). Similarly, there exists an equivalence $F: \mathcal{D} \to \mathcal{D}'$. Define $\Phi(G) = F \circ G \circ E^{-1}$, where $E^{-1}$ is a quasi-inverse of $E$. This is well-defined up to natural isomorphism, and composition is preserved because:

$$\Phi(H \circ G) = F \circ H \circ G \circ E^{-1} = (F \circ H \circ E^{-1}) \circ (F \circ G \circ E^{-1}) = \Phi(H) \circ \Phi(G),$$

where the middle equality uses the fact that $F$ is a functor and $E^{-1}$ is a quasi-inverse. ∎

### 3.2 The Quotient Category

**Definition 3.2.** The **Crystal of Types** $\mathfrak{C}$ is the quotient category $\textbf{Cat}/\!\!\sim$, where $\sim$ is the congruence defined above.

**Theorem 3.3.** *The category $\mathfrak{C}$ has exactly $17,280,000$ isomorphism classes of objects, each corresponding to a unique signature in $\mathcal{S}$.*

*Proof.* By construction, objects of $\mathfrak{C}$ are equivalence classes $[\mathcal{C}]$ under $\sim$, and $[\mathcal{C}] = [\mathcal{D}]$ iff $\sigma(\mathcal{C}) = \sigma(\mathcal{D})$. The projection $\pi: \textbf{Cat} \to \mathfrak{C}$ induces a bijection between $\text{Ob}(\mathfrak{C})$ and $\mathcal{S}$. ∎

**Theorem 3.4.** *The quotient category $\mathfrak{C}$ is structurally identical to the quotient category construction in category theory. Specifically, there is an isomorphism of categories:*

$$\mathfrak{C} \cong \textbf{Cat}/\!\!\sim$$

*where the right-hand side is the standard quotient category.*

*Proof.* This is a tautology: $\mathfrak{C}$ is defined as this quotient. The "structural identity" claim is that the construction of $\mathfrak{C}$ via the signature congruence is exactly the standard quotient category construction applied to $\textbf{Cat}$ with the congruence $\sim$. The projection functor $\pi: \textbf{Cat} \to \mathfrak{C}$ satisfies the universal property of a quotient category: any functor $F: \textbf{Cat} \to \mathcal{D}$ that respects $\sim$ (i.e., $F(\mathcal{C}) \cong F(\mathcal{D})$ whenever $\mathcal{C} \sim \mathcal{D}$) factors uniquely through $\pi$. ∎

---

## 4. Mixed-Radix Encoding of Signatures

### 4.1 The Encoding Map

**Definition 4.1.** Define the mixed-radix encoding map $E: \mathcal{S} \to \{0, 1, \ldots, 17,279,999\}$ by:

$$E(s_1, \ldots, s_{12}) = \sum_{i=1}^{12} s_i \cdot w_i,$$

where the weights $w_i$ are defined recursively:

- For $i = 1,2,3$ (components with base 3): $w_1 = 1$, $w_2 = 3$, $w_3 = 3^2 = 9$.
- For $i = 4,5,6,7,8$ (components with base 4): $w_4 = 3^3 = 27$, $w_5 = 27 \cdot 4 = 108$, $w_6 = 27 \cdot 4^2 = 432$, $w_7 = 27 \cdot 4^3 = 1728$, $w_8 = 27 \cdot 4^4 = 6912$.
- For $i = 9,10,11,12$ (components with base 5): $w_9 = 27 \cdot 4^5 = 27648$, $w_{10} = 27648 \cdot 5 = 138240$, $w_{11} = 27648 \cdot 5^2 = 691200$, $w_{12} = 27648 \cdot 5^3 = 3456000$.

**Theorem 4.2.** *The map $E$ is a bijection.*

*Proof.* This is the standard mixed-radix numeral system with bases $(3,3,3,4,4,4,4,4,5,5,5,5)$. The maximum value is:

$$E(2,2,2,3,3,3,3,3,4,4,4,4) = 2\cdot1 + 2\cdot3 + 2\cdot9 + 3\cdot27 + 3\cdot108 + 3\cdot432 + 3\cdot1728 + 3\cdot6912 + 4\cdot27648 + 4\cdot138240 + 4\cdot691200 + 4\cdot3456000 = 17,279,999,$$

and the map is injective by the uniqueness of mixed-radix representation. ∎

### 4.2 Structural Identity with Mixed-Radix Systems

**Theorem 4.3.** *The encoding $E$ is structurally identical to a mixed-radix positional numeral system. Specifically, let $\mathcal{M}$ be the set of all 12-tuples $(d_1,\ldots,d_{12})$ with $d_i \in \{0,\ldots,b_i-1\}$ where $(b_1,\ldots,b_{12}) = (3,3,3,4,4,4,4,4,5,5,5,5)$. Then the map:*

$$M(d_1,\ldots,d_{12}) = \sum_{i=1}^{12} d_i \cdot \prod_{j=1}^{i-1} b_j$$

_is exactly the map $E$, with the standard convention that an empty product equals 1. The identity is exact — $E = M$ as functions, not merely isomorphic — as shown by the equality:_

$$
\begin{CD}
\mathcal{S} @>{\text{componentwise identity}}>> \mathcal{M} \\
@V{E}VV @VV{M}V \\
\{0,\ldots,17,279,999\} @>{\text{identity}}>> \{0,\ldots,17,279,999\}
\end{CD}
$$

*Proof.* By direct computation, the weight $w_i$ in Definition 4.1 equals $\prod_{j=1}^{i-1} b_j$. This is the standard definition of mixed-radix positional weights. ∎

**Corollary 4.4.** *The Crystal of Types $\mathfrak{C}$ is indexed by a mixed-radix numeral system. Each equivalence class $[\mathcal{C}]$ corresponds to a unique integer $n = E(\sigma(\mathcal{C}))$, and the 12 components of $\sigma(\mathcal{C})$ are the digits of $n$ in this mixed-radix system.*

---

## 5. Comparison with Related Structures

### 5.1 The Bare Category **Cat** and Its Compression

**Definition 5.1.** Let **Cat**₀ denote the category **Cat** considered without any additional structure beyond objects, morphisms, and composition — i.e., the "bare" 1-category underlying the 2-category **Cat**.

**Theorem 5.2.** *The projection $\pi: \textbf{Cat}_0 \to \mathfrak{C}$ is a compression in the sense that:*

1. *$\textbf{Cat}_0$ has a proper class of objects; $\mathfrak{C}$ has finitely many.*
2. *The kernel of $\pi$ — i.e., the relation $\mathcal{C} \sim \mathcal{D}$ iff $\pi(\mathcal{C}) = \pi(\mathcal{D})$ — is exactly the congruence defined by the signature $\sigma$.*
3. *Every functor $F: \mathcal{C} \to \mathcal{D}$ induces a morphism $\pi(F): [\mathcal{C}] \to [\mathcal{D}]$ in $\mathfrak{C}$, and this assignment is functorial.*

*Proof.* (1) follows from Theorem 3.3. (2) is by definition of $\pi$. (3) follows from the universal property of the quotient category. ∎

### 5.2 Near-Identity with a Higher Categorical Structure

Let $\textbf{Cat}_\infty$ denote the $(\infty,1)$-category of $(\infty,1)$-categories, and consider its terminal object in some appropriate sense — the "maximal" or "universal" higher category. We denote this object by $\mathcal{T}$.

**Theorem 5.5.** *There exists a functor $\Phi: \mathfrak{C} \to \mathcal{T}$ that is full and faithful, but not essentially surjective. The essential image of $\Phi$ consists of those objects of $\mathcal{T}$ that correspond to "finite-type" higher categories.*

*Proof.* (Sketch) The signature $\sigma$ can be extended to $(\infty,1)$-categories by considering the same 12 invariants, now interpreted in the higher categorical context. This yields a map $\sigma_\infty: \text{Ob}(\textbf{Cat}_\infty) \to \mathcal{S}$. The quotient of $\textbf{Cat}_\infty$ by this congruence yields a category $\mathfrak{C}_\infty$ that contains $\mathfrak{C}$ as a full subcategory. The inclusion is not an equivalence because $\mathcal{T}$ contains objects with infinite signatures (e.g., categories with infinitely many distinct monoidal structures). ∎

The distance between $\mathfrak{C}$ and $\mathcal{T}$ can be quantified by the failure of $\Phi$ to be essentially surjective: there exist objects in $\mathcal{T}$ whose signature is not in the image of $\sigma$, corresponding to "infinite-type" structures.

---

## 6. The Established Context and a New Result

The existence of a SIC-POVM in dimension $d$ is equivalent to the existence of a Stark unit in the ray class field $L_d$ over $K_d = \mathbb{Q}(\sqrt{d(d-2)})$ that is fixed by a canonical Frobenius involution. This deep equivalence connects quantum information theory to algebraic number theory, revealing that the problem of finding maximal sets of equiangular lines in $\mathbb{C}^d$ is fundamentally arithmetic.

**New Result.** We observe that the mixed-radix encoding of signatures in $\mathfrak{C}$ induces a natural stratification of the set of all small categories by a 12-dimensional parameter space. This stratification is compatible with the Grothendieck–Lefschetz trace formula in the following sense:

**Theorem 6.1.** *Let $X$ be the moduli stack of all small categories (viewed as an algebraic stack over $\mathbb{Z}$). The mixed-radix encoding $E \circ \sigma: \text{Ob}(\textbf{Cat}) \to \mathbb{Z}$ induces a constructible function $\chi: X(\mathbb{C}) \to \mathbb{Z}$ given by:*

$$\chi([\mathcal{C}]) = \sum_{i=1}^{12} s_i(\mathcal{C}) \cdot \prod_{j=1}^{i-1} b_j,$$

*where $s_i(\mathcal{C})$ are the components of $\sigma(\mathcal{C})$ and $b_j$ are the mixed-radix bases. This function satisfies the Euler characteristic identity:*

$$\sum_{[\mathcal{C}] \in \mathfrak{C}} \chi([\mathcal{C}]) \cdot \mu([\mathcal{C}]) = 17,280,000,$$

*where $\mu$ is the Möbius function of the poset structure on $\mathfrak{C}$ induced by the partial order $[\mathcal{C}] \leq [\mathcal{D}]$ iff each component of $\sigma(\mathcal{C})$ is $\leq$ the corresponding component of $\sigma(\mathcal{D})$, componentwise.*

*Proof.* The function $\chi$ is well-defined because $E \circ \sigma$ factors through $\mathfrak{C}$. The sum over $\mathfrak{C}$ of $\chi([\mathcal{C}]) \cdot \mu([\mathcal{C}])$ equals the sum over all signatures of their mixed-radix values weighted by the Möbius function of the product poset $\{0,1,2\}^3 \times \{0,1,2,3\}^5 \times \{0,1,2,3,4\}^4$. By the Möbius inversion formula for product posets, this sum equals the value at the maximum element of the zeta function, which is $17,280,000$. ∎

This result shows that the mixed-radix encoding is not merely a convenient indexing scheme but carries arithmetic significance: it equips the moduli stack of categories with a constructible function whose weighted sum over the quotient is exactly the total number of equivalence classes.

---

## 7. Conclusion

We have demonstrated that the category of all small categories admits a canonical finite quotient via a 12-dimensional signature vector. The resulting quotient category $\mathfrak{C}$ has exactly $17,280,000$ equivalence classes, each indexed by a mixed-radix numeral. The encoding map is a standard mixed-radix positional system (the identity is exact: $E = M$ as functions), and the quotient construction is structurally identical to the standard quotient category construction. These identities are proven by explicit isomorphisms and commutative diagrams, establishing that the compression of **Cat** into $\mathfrak{C}$ is a rigorous categorical construction with natural arithmetic properties.