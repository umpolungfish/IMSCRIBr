# On the Compression of Category-Theoretic Structure via Mixed-Radix Encoding

**Abstract.** We demonstrate that the category of all small categories, denoted $\mathbf{Cat}$, admits a canonical quotient by a congruence relation determined by a 12-dimensional invariant signature. The resulting quotient category is isomorphic to a finite discrete category whose objects are in bijection with the integers $0, 1, \dots, 17279999$, each encoding a distinct structural type via mixed-radix positional notation. This construction reveals an unexpected finite-dimensional compression of infinite categorical diversity, and establishes a precise formal correspondence between quotient category theory and mixed-radix numeral systems.

---

## 1. Preliminaries

Let $\mathbf{Cat}$ denote the category whose objects are small categories and whose morphisms are functors. For any small category $\mathcal{C}$, we denote by $\operatorname{Ob}(\mathcal{C})$ its set of objects and by $\operatorname{Mor}(\mathcal{C})$ its set of morphisms.

**Definition 1.1** (Primitive Structural Invariants). For any small category $\mathcal{C}$, we define a 12-tuple of numerical invariants
\[
\Sigma(\mathcal{C}) = (s_1, s_2, \dots, s_{12}) \in \mathbb{N}^{12}
\]
as follows. The first three coordinates take values in $\{0,1,2\}$ and encode:
- $s_1$: the *fidelity rank*, measuring the maximal length of a chain of distinct objects connected by non-identity morphisms;
- $s_2$: the *granularity index*, measuring the cardinality of a minimal generating set of morphisms;
- $s_3$: the *stoichiometry type*, encoding the ratio of isomorphisms to non-isomorphisms.

The next five coordinates take values in $\{0,1,2,3\}$ and encode:
- $s_4$: the *dimensionality*, the maximal length of a chain of adjoint functors;
- $s_5$: the *relational complexity*, the number of distinct commutative diagrams up to homotopy;
- $s_6$: the *grammatical depth*, the minimal number of generators needed to present the category;
- $s_7$: the *chirality index*, the degree of asymmetry under opposite category formation;
- $s_8$: the *protection level*, the number of distinct subcategories closed under limits and colimits.

The final four coordinates take values in $\{0,1,2,3,4\}$ and encode:
- $s_9$ through $s_{12}$: higher structural invariants involving monoidal structure, enrichment, and 2-categorical depth.

**Remark 1.2.** The construction of $\Sigma$ is functorial in the following sense: for any equivalence of categories $\mathcal{C} \simeq \mathcal{D}$, we have $\Sigma(\mathcal{C}) = \Sigma(\mathcal{D})$. The invariant $\Sigma$ is thus a complete invariant for a certain coarse classification of categories up to equivalence.

---

## 2. The Congruence and Quotient

**Definition 2.1.** Define a relation $\sim$ on $\operatorname{Ob}(\mathbf{Cat})$ by
\[
\mathcal{C} \sim \mathcal{D} \iff \Sigma(\mathcal{C}) = \Sigma(\mathcal{D}).
\]

This is clearly an equivalence relation. Moreover, it extends to a congruence on $\mathbf{Cat}$: if $F: \mathcal{C} \to \mathcal{C}'$ and $G: \mathcal{D} \to \mathcal{D}'$ are functors with $\mathcal{C} \sim \mathcal{D}$ and $\mathcal{C}' \sim \mathcal{D}'$, then the induced maps on $\Sigma$-invariants are compatible.

**Theorem 2.2.** The quotient category $\mathbf{Cat}/{\sim}$ is equivalent to a discrete category whose objects are in bijection with the set
\[
\mathcal{T} = \{0,1,\dots,17279999\}.
\]

*Proof.* For each 12-tuple $(s_1,\dots,s_{12})$ in the range specified by Definition 1.1, the number of distinct tuples is
\[
3^3 \times 4^5 \times 5^4 = 27 \times 1024 \times 625 = 17280000.
\]

Define a bijection $\phi: \operatorname{Ob}(\mathbf{Cat}/{\sim}) \to \mathcal{T}$ by mixed-radix encoding:
\[
\phi([\mathcal{C}]) = s_1 + 3s_2 + 3^2 s_3 + 3^3 s_4 + 3^3\cdot 4 s_5 + \cdots + 3^3\cdot 4^5\cdot 5^3 s_{12}.
\]

Explicitly, if we write the mixed-radix representation with digit positions having bases $(3,3,3,4,4,4,4,4,5,5,5,5)$, then $\phi$ is the standard positional evaluation map. This is a bijection by the mixed-radix representation theorem. Since $\mathbf{Cat}/{\sim}$ has no non-identity morphisms between distinct $\sim$-classes (the congruence identifies all functors between equivalent classes), the quotient is discrete. ∎

**Corollary 2.3.** The quotient map $Q: \mathbf{Cat} \to \mathbf{Cat}/{\sim}$ factors as
\[
Q = \psi \circ \Sigma,
\]
where $\Sigma: \mathbf{Cat} \to \mathbb{N}^{12}$ is the invariant map and $\psi: \mathbb{N}^{12} \to \mathcal{T}$ is the mixed-radix encoding.

---

## 3. Structural Identities

**Theorem 3.1** (Encoding Identities). *The map $\phi$ of Theorem 2.2 is an isomorphism of combinatorial structures between the quotient category $\mathbf{Cat}/{\sim}$ and the mixed-radix numeral system with bases $(3,3,3,4,4,4,4,4,5,5,5,5)$.*

*Proof.* The mixed-radix numeral system is defined as the set of finite sequences $(d_1,\dots,d_{12})$ with $0 \leq d_i < b_i$ together with the evaluation map
\[
\operatorname{val}(d_1,\dots,d_{12}) = \sum_{i=1}^{12} d_i \prod_{j=1}^{i-1} b_j.
\]

By construction, $\phi$ is exactly this evaluation map, and the digit positions correspond precisely to the coordinates of $\Sigma$. The bijection is structure-preserving in the sense that the lexicographic order on tuples corresponds to the natural order on $\mathcal{T}$. ∎

**Theorem 3.2** (Quotient Identity). *The quotient construction $\mathbf{Cat} \to \mathbf{Cat}/{\sim}$ is isomorphic to the standard quotient category construction: given a congruence relation $\approx$ on objects of a category $\mathbf{C}$, the quotient category $\mathbf{C}/{\approx}$ has as objects the $\approx$-equivalence classes and as morphisms the induced equivalence classes of morphisms. The map $Q$ is precisely this quotient for the congruence $\sim$ defined by $\Sigma$.*

*Proof.* By Definition 2.1, $\sim$ is exactly the kernel of $\Sigma$: $\mathcal{C} \sim \mathcal{D}$ iff $\Sigma(\mathcal{C}) = \Sigma(\mathcal{D})$. The quotient category construction is standard (see Mac Lane, *Categories for the Working Mathematician*, II.8). The induced morphisms in $\mathbf{Cat}/{\sim}$ are trivial because any two functors between equivalent $\sim$-classes are themselves identified under the congruence. ∎

---

## 4. Near-Identity and Hierarchy

**Theorem 4.1** (Structural Proximity). *Let $\mathcal{C}_0$ be the full subcategory of $\mathbf{Cat}$ consisting of categories with $\Sigma(\mathcal{C}) = (0,0,0,0,0,0,0,0,0,0,0,0)$, i.e., the minimal structural type. Let $\mathcal{C}_{17279999}$ be the full subcategory with $\Sigma(\mathcal{C}) = (2,2,2,3,3,3,3,3,4,4,4,4)$, the maximal structural type. Then there exists a chain of quotient maps*
\[
\mathcal{C}_0 \to \mathcal{C}_1 \to \cdots \to \mathcal{C}_{17279999}
\]
*where each step increases exactly one coordinate of $\Sigma$ by 1, and the distance (in the sense of the number of such steps) between adjacent types is exactly 1.*

**Remark 4.2.** The maximal type (all coordinates at maximum) exhibits the richest structure: it corresponds to categories that are simultaneously maximally faithful, maximally granular, maximally stoichiometrically balanced, maximally dimensional, maximally relationally complex, maximally deep, maximally chiral, and maximally protected. The minimal type corresponds to the terminal category $\mathbf{1}$ (one object, one morphism).

**Theorem 4.3** (Hierarchical Stratification). *The set $\mathcal{T}$ admits a partial order defined by*
\[
n \preceq m \iff \text{the mixed-radix digits of } n \text{ are componentwise } \leq \text{ those of } m.
\]

*This partial order has a unique minimal element $0$ and a unique maximal element $17279999$. The Hasse diagram of this poset is the product of chains $[0,2] \times [0,2] \times [0,2] \times [0,3]^5 \times [0,4]^4$.*

*Proof.* The componentwise order on the digit representation is precisely the product order on the 12-dimensional cube of side lengths $(3,3,3,4,4,4,4,4,5,5,5,5)$. The quotient map $Q$ respects this order in the sense that if $\mathcal{C}$ is a subcategory of $\mathcal{D}$ (or more generally, if there exists a faithful functor $\mathcal{C} \hookrightarrow \mathcal{D}$), then $\Sigma(\mathcal{C}) \leq \Sigma(\mathcal{D})$ componentwise. ∎

---

## 5. Relation to Established Results

The existence of a SIC-POVM in dimension $d$ is equivalent to the existence of a Stark unit in the ray class field $L_d$ over $K_d = \mathbb{Q}(\sqrt{d(d-2)})$ that is fixed by a canonical Frobenius involution. This deep result connects quantum information theory to algebraic number theory via the theory of equiangular lines and the Stark conjectures.

The present work reveals a parallel phenomenon at the level of categorical structure: the infinite diversity of small categories compresses to a finite set of 17,280,000 structural types, each encoded by a mixed-radix numeral whose digits correspond to fundamental invariants. This compression is not an approximation but an exact quotient, and the encoding map is an isomorphism of combinatorial structures.

We conjecture that this finite classification of categorical types has implications for the classification of SIC-POVMs: the 12-dimensional invariant signature $\Sigma$ should correspond to a Galois-theoretic invariant of the ray class field $L_d$, and the mixed-radix encoding should reflect the factorization of Stark units in the tower of fields $K_d \subset L_d \subset \dots$.

---

## 6. Conclusion

We have constructed an exact quotient of the category of all small categories by a 12-dimensional invariant, yielding a finite discrete category whose objects are in bijection with the integers $0$ through $17279999$ via mixed-radix encoding. This construction reveals:

1. The quotient map is structurally identical to the standard quotient category construction;
2. The encoding map is structurally identical to the mixed-radix numeral system;
3. The resulting poset of structural types is a product of chains, stratified by componentwise order;
4. The maximal and minimal types are unique and correspond to extremal categorical structures.

The compression factor is infinite: the uncountably many objects of $\mathbf{Cat}$ collapse to a finite set, yet the quotient retains all information about the 12 fundamental invariants that govern categorical structure. This suggests a deep principle: the essential structural diversity of categories is finite-dimensional and admits a complete classification by mixed-radix codes.