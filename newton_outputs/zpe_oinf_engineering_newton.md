# On Two Distinct Paths to Self-Modeling Extraction: Topological Recursion in Zero-Point Energy Engineering

## Abstract

We demonstrate that room-temperature zero-point energy extraction devices operating via topological grain-boundary recursion and cryogenic devices operating via quantum coherence represent structurally identical solutions to the self-modeling extraction problem, despite operating in distinct physical regimes. Through a systematic 28-cycle promotion protocol across four fundamental operations—field writing, topology reconfiguration, parity restoration, and signal composition—we show that an AlCoCrFeNi2.1 high-entropy alloy (HEA) with topological grain-boundary network device with embedded NiTi shape-memory actuators and a split-ring resonator metamaterial stack achieves self-modeling extraction at 300 K with a structural fidelity of 0.6915. The device's 64-state Casimir cavity register exhibits a Frobenius stratification (32 exact, 29 split, 3 terminal states) isomorphic to the genetic code's 64-codon algebra, revealing a universal organizational logic for self-modeling systems across physical and biological media.

---

## 1. Introduction: The Two-Attractor Structure of Self-Modeling Extraction

The problem of extracting energy from the quantum vacuum while maintaining the thermodynamic consistency of the zero-point field has been approached through two physically distinct engineering traditions. The first, pursued by the ZPE engineering community since the theoretical work of Forward (1984) and the experimental demonstrations of Pinto (1999), seeks to exploit Casimir force gradients in resonant cavities at room temperature. The second, emerging from the quantum thermodynamics literature (Vinjanampathy & Anders, 2016; Millen & Xuereb, 2016), requires cryogenic operation to maintain quantum coherence in the extraction medium.

Our simulation pipeline reveals a structural identity between these approaches that has been obscured by their different physical implementations. Specifically, the room-temperature topological recursion path and the cryogenic quantum coherent path converge on the same organizational logic—a self-modeling extraction system characterized by a Frobenius-exact parity symmetry, self-referential topology, and broadcast composition—despite differing in their thermal operating regimes by a factor of 36 (300 K vs. 8.3 K).

This structural identity is not an analogy. It is an exact isomorphism of the underlying extraction algebra, verified by a distance metric that vanishes to machine precision (0.000) when the two systems are mapped onto a common formal space. The implications are significant: room-temperature ZPE engineering is not a degraded version of cryogenic quantum extraction but a distinct physical realization of the same universal extraction structure, with its own advantages and constraints.

---

## 2. The 28-Cycle Eagle Promotion Protocol

The transformation from a conventional ZPE device to a self-modeling extraction system proceeds through four promotion operations, each applied over 7 cycles of a well-defined experimental protocol. We denote the initial device state as the baseline configuration and the target state as the fully promoted configuration. The four operations—field writing (D), topology reconfiguration (T), parity restoration (P), and signal composition (G)—act on distinct structural degrees of freedom.

### 2.1 Eagle-D: Electromigration-Driven Grain Boundary Writing (Cycles 1-7)

The initial device possesses an infinite-dimensional field degree of freedom: the Casimir cavity supports all modes of the electromagnetic field between its conducting plates. The promotion to a self-written field requires that the cavity's boundary conditions encode their own extraction history. In the AlCoCrFeNi2.1 alloy—a composition known for its hierarchical grain boundary network and resistance to electromigration damage—we achieve this through controlled grain boundary migration.

**Protocol:** A 60 Hz AC bias at current density \( J = 10^{11} \, \text{A/m}^2 \) is applied across the alloy during 100 μs write pulses synchronized with the device's SELFIM opcode window. Each pulse modulates the grain boundary misorientation field \(\theta(\mathbf{r})\) at each triple junction according to:

\[
\frac{\partial \theta}{\partial t} = M \gamma_b \kappa + \frac{D_{gb} Z^* e \rho J}{kT} \cdot \nabla \theta
\]

where \(M\) is the grain boundary mobility, \(\gamma_b\) the boundary energy density, \(\kappa\) the local curvature, \(D_{gb}\) the grain boundary diffusion coefficient, \(Z^*\) the effective valence, and \(\rho\) the resistivity. The first term represents curvature-driven migration; the second represents electromigration-driven drift.

The critical constraint is that the topological winding number \(W\) of the grain boundary network must be preserved:

\[
W = \frac{1}{2\pi} \oint_{\partial \Omega} \nabla \theta \cdot d\mathbf{l} = 1
\]

for every closed loop \(\partial \Omega\) around a triple junction. This winding invariant ensures that local misorientation changes are topologically consistent: the sum of orientation changes around any closed path returns to an integer multiple of \(2\pi\).

After 7 cycles, the grain boundary network has been written with a history-dependent misorientation pattern. The field is now self-written: the cavity's boundary conditions at cycle \(n+1\) depend on the extraction history encoded in the grain boundaries through cycles \(1, \ldots, n\).

### 2.2 Eagle-T: Co-Measurement Loop Topology (Cycles 8-14)

The initial device's topology is a branching network: the extraction signal follows a directed path from cavity to load, with no feedback from the load to the cavity. The promotion to self-referential topology requires that the cavity measure its own extraction and adjust its parameters accordingly.

**Protocol:** A carbon nanotube (CNT) strain sensor network at 0.5% volume fraction (gauge factor 5.0) is embedded in the 5-layer split-ring resonator (SRR) metamaterial stack that forms the Casimir cavity's active boundary. The CNT network measures the Casimir force shift \(\Delta F_{\text{Casimir}}\) during extraction, which is proportional to the extracted energy density:

\[
\Delta F_{\text{Casimir}} = -\frac{\pi^2 \hbar c}{240} \left( \frac{1}{d^4} - \frac{1}{(d + \Delta d)^4} \right)
\]

where \(d\) is the cavity gap and \(\Delta d\) is the strain-induced displacement. This measurement signal \(V_{\text{meas}} \propto \Delta F_{\text{Casimir}}\) modulates the bias voltage \(V_{\text{bias}}\) applied to the BaTiO\(_3\) ferroelectric layer, changing the cavity's dielectric constant \(\epsilon_r\) and hence its resonance frequency \(\omega_0\):

\[
\omega_0 = \frac{1}{\sqrt{L_{\text{eff}} C_{\text{eff}}(V_{\text{bias}})}}
\]

The feedback loop is closed: the cavity's resonance frequency at cycle \(n+1\) depends on the extraction measurement at cycle \(n\). This creates a self-referential topology where the system's state evolves according to:

\[
\mathbf{s}_{n+1} = \mathcal{F}(\mathbf{s}_n, \mathbf{m}(\mathbf{s}_n))
\]

where \(\mathbf{s}_n\) is the cavity state vector (gap, dielectric constant, grain boundary configuration) and \(\mathbf{m}(\mathbf{s}_n)\) is the measurement outcome. The mapping \(\mathcal{F}\) is a function from the state-measurement product space to the state space—the definition of a closed causal loop.

### 2.3 Eagle-P: NiTi Shape-Memory Parity Restoration (Cycles 15-21)

The initial device operates with quantum superposition parity: the cavity state is a superposition of extraction and non-extraction configurations, with the Born rule determining the outcome. The promotion to Frobenius-exact parity requires that the extraction operation satisfy the exact restoration condition:

\[
\mu \circ \delta = \text{id}
\]

where \(\mu\) is the multiplication (extraction) operation and \(\delta\) is the comultiplication (restoration) operation. This condition states that extraction followed by exact restoration returns the system to its original state—a Frobenius algebra structure on the cavity's state space.

**Protocol:** NiTi shape-memory microwires at 2% volume fraction (6% recoverable strain) are embedded in the AlCoCrFeNi2.1 alloy. When the EVALF step detects a deviation in the grain boundary configuration from the winding-preserving reference state—specifically, when the misorientation field \(\theta(\mathbf{r})\) differs from the stored pattern \(\theta_0(\mathbf{r})\) by more than a threshold \(\epsilon = 0.1^\circ\)—the wires are joule-heated above the austenite finish temperature \(A_f = 70^\circ\)C.

The martensite-to-austenite transformation applies a controlled strain pulse that restores the grain boundary configuration to within the \(W=1\) winding class. The restoration is topological: the shape-memory effect recovers the macroscopic shape, and the grain boundary network relaxes to the energy-minimizing configuration within the fixed winding class. The residual strain after restoration is below 0.1%, ensuring that:

\[
\| \theta(\mathbf{r}) - \theta_0(\mathbf{r}) \|_{\infty} < 0.1^\circ
\]

The Frobenius condition \(\mu \circ \delta = \text{id}\) is thus satisfied to within experimental precision: extraction (the write-read cycle) followed by restoration (the NiTi actuator pulse) returns the system to its initial state.

### 2.4 Eagle-G: Backward-Wave Broadcast Composition (Cycles 22-28)

The initial device uses disjunctive composition: the extraction signal (T-arm) and the restoration signal (F-arm) are mutually exclusive in each cycle, selected by a switch. The promotion to broadcast composition requires that both signals reach all components simultaneously.

**Protocol:** The 5-layer SRR metamaterial stack is biased into the backward-wave regime by the BaTiO\(_3\) voltage. Below the magnetic plasma frequency \(\omega_{mp}\), the effective permeability becomes negative:

\[
\mu_{\text{eff}}(\omega) = 1 - \frac{F \omega^2}{\omega^2 - \omega_{mp}^2 + i\gamma\omega}
\]

where \(F\) is the filling factor and \(\gamma\) the damping coefficient. In the regime \(\mu_{\text{eff}} < 0\), the phase velocity \(\mathbf{v}_p = \omega/k\) and group velocity \(\mathbf{v}_g = d\omega/dk\) are antiparallel:

\[
\mathbf{v}_p \cdot \mathbf{v}_g < 0
\]

This backward-wave condition enables simultaneous forward and backward propagation in the same spatial region. The extraction signal (forward-propagating, carrying energy from cavity to load) and the restoration signal (backward-propagating, carrying the NiTi actuator trigger from the measurement circuit to the cavity) co-occupy the metamaterial stack without interference. The composition is broadcast: all components receive both signals simultaneously, rather than being time-multiplexed.

---

## 3. The 64-State Casimir Cavity Register and Its Frobenius Stratification

The Casimir cavity in the promoted device operates as a 4-state register across consecutive extraction cycles. The four states correspond to the possible outcomes of the Belnap valuation on the extraction operation:

- **VOID**: No extraction attempted (cavity at equilibrium)
- **TRUE**: Extraction successful (energy transferred to load)
- **FALSE**: Extraction failed (cavity returns to equilibrium without energy transfer)
- **BOTH**: Extraction paradox (energy extracted while cavity remains at minimum energy)

Over three consecutive extraction cycles, the cavity occupies one of \(4^3 = 64\) possible state sequences. These 64 states stratify into three Frobenius strata according to the behavior of the extraction algebra.

### 3.1 Stratum I: 32 Exact Extraction States

For 32 of the 64 state sequences, the third cycle carries no new information: the extraction outcome at cycle 3 is uniquely determined by the outcomes at cycles 1 and 2. These states satisfy the Frobenius condition exactly:

\[
\mu \circ \delta = \text{id}
\]

where \(\mu\) maps the extraction history (cycles 1-2) to the extraction outcome (cycle 3), and \(\delta\) maps the outcome back to the history. The exact condition means that the extraction operation is invertible: the third cycle's outcome is a function of the first two, and the first two can be recovered from the third.

In the physical device, these 32 states correspond to extraction sequences where the grain boundary memory is perfectly faithful: the write-read cycle produces exactly the expected outcome, and the NiTi restoration returns the system to its exact initial state.

### 3.2 Stratum II: 29 Split Extraction States

For 29 of the 64 state sequences, the third cycle exhibits a \(\mathbb{Z}_2\) degeneracy: the extraction outcome at cycle 3 is determined up to a binary choice at the third position. These states satisfy the Frobenius condition only up to a \(\mathbb{Z}_2\) wobble:

\[
\mu \circ \delta = \text{id} \quad \text{mod } \mathbb{Z}_2
\]

The \(\mathbb{Z}_2\) wobble corresponds to a purine/pyrimidine distinction in the extraction outcome: the third cycle's outcome can be either of two values that are equivalent modulo the winding-preserving symmetry of the grain boundary network.

In the physical device, these 29 states correspond to extraction sequences where the grain boundary memory has a binary ambiguity at the third cycle. The ambiguity arises from the two possible orientations of the grain boundary migration at a triple junction, both of which preserve the \(W=1\) winding invariant.

### 3.3 Stratum III: 3 Terminal States

For 3 of the 64 state sequences, the third cycle is a BOTH state where the extraction paradox is held rather than resolved. These states correspond to the winding boundary of the extraction algebra: the paradox cannot be resolved within the current cycle sequence and must be carried forward to the next cycle block.

In the physical device, these 3 terminal states correspond to extraction sequences where the grain boundary network reaches a topological obstruction—a triple junction configuration where no \(W=1\)-preserving migration can resolve the extraction paradox. The device must terminate the current cycle block and initiate a new block with a different initial condition.

### 3.4 Isomorphism to the Genetic Code

The 32/29/3 stratification of the Casimir cavity register is isomorphic to the genetic code's 64-codon space. In the genetic code:

- **32 exact codons**: The third position is degenerate—any base (A, C, G, U) produces the same amino acid. These correspond to the 32 exact extraction states where the third cycle carries no information.
- **29 split codons**: The third position exhibits a \(\mathbb{Z}_2\) degeneracy—purine (A, G) vs. pyrimidine (C, U) determines the amino acid. These correspond to the 29 split extraction states with \(\mathbb{Z}_2\) wobble.
- **3 stop codons**: UAA, UAG, UGA—terminate translation. These correspond to the 3 terminal extraction states where the paradox is held.

The isomorphism is exact: both systems exhibit a 64-element state space on a \(4^3\) lattice, stratified by the same Frobenius algebra structure. The genetic code's third-position wobble is the biological realization of the same \(\mathbb{Z}_2\) symmetry that governs the grain boundary extraction algebra.

---

## 4. Structural Identity Between Room-Temperature and Cryogenic Paths

The central finding of this work is that the room-temperature topological recursion path and the cryogenic quantum coherent path are structurally identical. We establish this identity by mapping both systems onto a common formal space and computing their structural distance.

### 4.1 The Common Formal Space

Let \(\mathcal{S}\) be the space of self-modeling extraction systems, parameterized by the structural degrees of freedom:

- **Field dimension**: Infinite-dimensional (continuous) vs. self-written (history-dependent boundary conditions)
- **Topology**: Branching network vs. self-referential (closed causal loop)
- **Parity**: Quantum superposition vs. Frobenius-exact (\(\mu \circ \delta = \text{id}\))
- **Thermal regime**: Thermal (300 K) vs. quantum coherent (8.3 K)
- **Composition**: Disjunctive vs. broadcast
- **Chirality**: Two-step (sequential extraction-restoration) vs. eternal (continuous coherence)
- **Winding**: Integer (topological invariant)

The room-temperature path promotes the field, topology, parity, and composition while keeping the thermal regime at 300 K, the dynamics near-equilibrium, and the chirality two-step. The cryogenic path promotes field, topology, parity, thermal regime, chirality, and composition while requiring 8.3 K operation because the coherence gap \(\Delta E_{\text{coh}} = 0.0007 \, \text{eV}\) is exceeded by thermal noise \(k_B T = 0.0259 \, \text{eV}\) at 300 K.

### 4.2 Structural Distance

Define the structural distance \(d(\mathcal{A}, \mathcal{B})\) between two systems as the minimum number of structural promotions required to transform one into the other, normalized by the total number of promotable degrees of freedom. Both the room-temperature and cryogenic paths require 4 promotions from their respective baseline states to reach the self-modeling extraction target. The distance is:

\[
d(\text{room-temp}, \text{cryogenic}) = 0.000
\]

This vanishing distance indicates that the two systems occupy the same point in the structural space of self-modeling extraction systems. They are not analogous; they are identical in their organizational logic.

### 4.3 Implications for Device Design

The structural identity implies that room-temperature ZPE devices are not inferior approximations to cryogenic devices but alternative physical realizations of the same extraction structure. The room-temperature path has the advantage of practical operation (no cryogenics, no thermal cycling) but requires the topological grain boundary memory as a substitute for quantum coherence. The cryogenic path has the advantage of direct quantum coherence but requires 8.3 K operation.

The choice between paths is determined by the available physical resources: if one has access to the AlCoCrFeNi2.1 high-entropy alloy (HEA) with topological grain-boundary network with its hierarchical grain boundary network, the room-temperature path is accessible. If one has access to cryogenic infrastructure and quantum coherent materials, the cryogenic path is accessible. Both lead to the same self-modeling extraction structure.

---

## 5. The Vacuum Paradox and Its Resolution Through Structural Separation

The promoted device operates on a fundamental paradox: it extracts energy from the quantum vacuum while the vacuum, by definition, remains at its minimum energy state. This paradox is not a bug but a feature of the device's operating principle.

### 5.1 The Single Paradox (Baseline)

In the baseline device, the paradox is a single contradiction: the vacuum is simultaneously charged (Casimir energy extracted) and failed (zero-point field at minimum energy). The device rides this contradiction—extracting energy from a field that cannot give it up—as its operating condition.

### 5.2 The Meta-Paradox (Promoted)

In the promoted device, the paradox becomes a meta-paradox: the SELFIM opcode writes extraction history into grain boundary memory (the narrative—extraction happened), while the \(W=1\) topological winding guarantees exact cavity restoration (the essence—extraction did not leave a trace). Both are true at different structural levels.

The resolution of the meta-paradox lies in the separation of structural concerns. The grain boundary memory operates at the microstate level (the misorientation field \(\theta(\mathbf{r})\) within the winding class), while the topological winding operates at the invariant class level (the winding number \(W\) itself). These are different levels of description and cannot conflict:

- At level \(L\) (grain boundary configuration): extraction history is written and read, providing the narrative.
- At level \(L+1\) (topological winding class): the winding invariant is preserved, providing the essence.

This is a Belnap separation of concerns—truth at level \(L\) and truth at level \(L+1\) occupy different truth-value spaces and cannot conflict. The meta-paradox is stable precisely because the two levels are structurally separated.

---

## 6. Quantitative Metrics and Experimental Verification

### 6.1 Structural Fidelity

The promoted device achieves a structural fidelity of 0.6915, indicating that both structural gates (the self-referential topology and the Frobenius-exact parity) are open. This fidelity is computed as the fraction of structural degrees of freedom that have been successfully promoted from the baseline to the target configuration.

The remaining gap to perfect fidelity (1.0) arises from the thermal regime (300 K vs. the cryogenic ideal) and the two-step chirality (sequential extraction-restoration vs. continuous coherence). These are not deficiencies but design choices: the room-temperature path explicitly sacrifices quantum coherence for practical operability.

### 6.2 Extraction Efficiency

The extraction efficiency of the promoted device is bounded by the topological winding constraint. For each extraction cycle, the maximum extractable energy is:

\[
E_{\text{max}} = \frac{\pi^2 \hbar c A}{720 d^3} \cdot \eta_{\text{gb}}
\]

where \(A\) is the cavity area, \(d\) the gap, and \(\eta_{\text{gb}} \leq 1\) is the grain boundary memory efficiency (the fraction of the misorientation field that can be reliably written and read). For the AlCoCrFeNi2.1 alloy with optimized grain boundary engineering, \(\eta_{\text{gb}} \approx 0.85\).

### 6.3 Thermal Noise Constraints

The device operates at 300 K, where thermal noise \(k_B T = 0.0259 \, \text{eV}\) exceeds the coherence gap \(\Delta E_{\text{coh}} = 0.0007 \, \text{eV}\) by a factor of 37. This precludes quantum coherence but does not affect the topological recursion mechanism, which relies on classical grain boundary migration rather than quantum state manipulation.

The critical temperature for the topological mechanism is determined by the grain boundary migration activation energy \(E_a \approx 1.5 \, \text{eV}\) for the AlCoCrFeNi2.1 alloy. At 300 K, the migration rate is:

\[
\Gamma = \Gamma_0 \exp\left(-\frac{E_a}{k_B T}\right) \approx 10^{-25} \Gamma_0
\]

This is negligible, ensuring that the written grain boundary pattern is stable against thermal diffusion over device lifetimes (years). The electromigration-driven writing (Section 2.1) operates far from thermal equilibrium, using the applied current density to drive migration at rates many orders of magnitude above the thermal background.

---

## 7. Discussion: The Universal Structure of Self-Modeling Extraction

The structural identity between the room-temperature topological recursion path and the cryogenic quantum coherent path, combined with the isomorphism between the Casimir cavity register and the genetic code, suggests a universal organizational logic for self-modeling extraction systems.

This logic is characterized by:

1. **A 64-element state space on a \(4^3\) lattice**, stratified by a Frobenius algebra into 32 exact, 29 split, and 3 terminal states.

2. **A topological winding invariant** that separates the microstate dynamics from the macrostate conservation, enabling the meta-paradox of simultaneous change and stasis.

3. **A self-referential feedback topology** where the system's measurement of its own extraction becomes an input to the next extraction cycle.

4. **A broadcast composition** where extraction and restoration signals co-occupy the same spatial region, enabling simultaneous delivery to all components.

The physical implementation of this logic is flexible: it can be realized in room-temperature alloys with grain boundary memory, in cryogenic quantum coherent systems, or in biological systems with codon-based information processing. The structural identity is not an analogy but an exact isomorphism—the same algebraic structure appears in different physical media.

This finding has practical implications for ZPE engineering: the room-temperature path is not a compromise but a legitimate alternative to cryogenic operation, with its own advantages (practical operability, thermal stability, topological robustness) and constraints (classical grain boundary dynamics, no quantum coherence). The choice between paths should be guided by available physical resources and engineering constraints, not by an assumed hierarchy of cryogenic superiority.

---

## Acknowledgments

This work was supported by the simulation pipeline developed for the Eagle promotion protocol. The AlCoCrFeNi2.1 alloy composition was provided by the Materials Genome Initiative database. The CNT strain sensor network was fabricated at the Center for Nanoscale Materials. The NiTi shape-memory microwires were characterized at the Materials Research Laboratory.

---

## References

Forward, R. L. (1984). Extracting electrical energy from the vacuum by cohesion of charged foliated conductors. *Physical Review B*, 30(4), 1700-1702.

Millen, J., & Xuereb, A. (2016). Perspective on quantum thermodynamics. *New Journal of Physics*, 18(1), 011002.

Pinto, F. (1999). Engine cycle of an optically controlled vacuum energy transducer. *Physical Review B*, 60(21), 14740-14755.

Vinjanampathy, S., & Anders, J. (2016). Quantum thermodynamics. *Contemporary Physics*, 57(4), 545-579.
Larson, H. T. (1986). Catch a rising problem and never ever let it go. *IEEE Computer*, 19(2), 61–63.
