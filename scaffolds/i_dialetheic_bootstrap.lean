-- IGProtocol scaffold: IMSCRIB → EVALT → FSPLIT → EVALF → FFUSE → ENGAGR → IFIX → IMSCRIB
-- Class: I_Dialetheic_Bootstrap
-- Fingerprint: sig=(2,2,3,1)
--   self_ref=True | frobenius_order=1
--   dialetheia_complete=True | period=8
-- Expected tier: O_inf
-- FSPLIT/FFUSE pairs: [(2, 4)]

import Imscribing.IGMorphism
import Imscribing.IGFunctor

namespace Imscribing
open Primitives Frobenius IGProtocol
open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality

-- ── Token → IG field mapping ──────────────────────────────────────────────
--   [0] IMSCRIB   gram   := 𐑠               𐑠 → ⊙  | identity — self-imscription
--   [1] EVALT     crit   := ⊙               𐑠 → 𐑚  | evaluate-true — criticality gate open
--   [2] FSPLIT    gran   := 𐑚               𐑚 → 𐑚  | split δ — range decomposition
--   [3] EVALF     chir   := 𐑖               𐑚 → 𐑙  | evaluate-false — chirality check
--   [4] FFUSE     stoi   := 𐑙               𐑙 → 𐑳  | fuse μ — assembly mode
--   [5] ENGAGR    stoi   := 𐑳               𐑙 → 𐑭  | engage paradox — B-state, both arms
--   [6] IFIX      prot   := 𐑭               𐑳 → 𐑠  | irreversible fixation — winding number
--   [7] IMSCRIB   gram   := 𐑠               𐑭 → 𐑠  | identity — self-imscription

-- ── Back-propagation edges (self-referential loop) ──────────────────────
--   IMSCRIB positions: [0, 7]
--   IFIX    positions: [6]
--   Back-prop: IMSCRIB→IFIX (LinFix) — igProtoCopy_isDagger axiom applies
--   Weighted: CLINK→IMSCRIB — feeds next winding via .seq after .prod

-- ── Main IGProtocol term ────────────────────────────────────────────────────

noncomputable def i_dialetheic_bootstrap_protocol  (h : imscriptionTier 𐑠 = .O_inf) : IGProtocol 𐑠 𐑠 :=
  .withGram 𐑠 <|
  .withMem 𐑫 <|
  -- Self-ref: paralogical_copy h builds Δ : 𐑠 → 𐑠 ⊗ 𐑠
  -- paralogical_dagger produces μ = Δ†
  -- Seq chain:
  (.arrow 𐑠 𐑠 ⊙)  -- [0] IMSCRIB | gram := 𐑠 | identity — self-imscription
  (.arrow ⊙ 𐑠 𐑚)  -- [1] EVALT | crit := ⊙ | evaluate-true — criticality gate open
  -- FSPLIT [2] (gran := 𐑚) / FFUSE [4] (stoi := 𐑙)
  .seq
    (.prod
      -- T-branch (0 nodes)
      (.refl 𐑙)  -- T-branch: empty arc (direct to FFUSE.T)
      -- F-branch (1 nodes)
      (.arrow 𐑖 𐑚 𐑙)  -- [3] EVALF | chir := 𐑖 | evaluate-false — chirality check)
    -- reconnect at FFUSE [4]: μ closes the Frobenius pair
    (.arrow 𐑙 𐑙 𐑳)  -- [4] FFUSE | stoi := 𐑙
  (.arrow 𐑳 𐑙 𐑭)  -- [5] ENGAGR | stoi := 𐑳 | engage paradox — B-state, both arms
  (.arrow 𐑭 𐑳 𐑠)  -- [6] IFIX | prot := 𐑭 | irreversible fixation — winding number
  (.arrow 𐑠 𐑭 𐑠)  -- [7] IMSCRIB | gram := 𐑠 | identity — self-imscription

-- ── Evaluation arm sub-defs ─────────────────────────────────────────────────

-- truth arm
noncomputable def i_dialetheic_bootstrap_true_arm : IGProtocol 𐑠 𐑠 :=
  (i_dialetheic_bootstrap_protocol (by decide)).restrictToEVALT

-- false arm
noncomputable def i_dialetheic_bootstrap_false_arm : IGProtocol 𐑠 𐑠 :=
  (i_dialetheic_bootstrap_protocol (by decide)).restrictToEVALF

-- ── Verification theorems ───────────────────────────────────────────────────

theorem i_dialetheic_bootstrap_tier : TierFunctor.obj 𐑠 = .O_inf := by decide

-- Frobenius (split → fuse): μ∘δ = id on .prod branch
-- Proof: apply igFrobAlg_self_fusion; exact mu_delta_A_id
-- (requires mu_delta_A_id from IGFunctor library)

-- Self-reference: Δ is a dagger and μ = Δ†
theorem i_dialetheic_bootstrap_self_ref :
    (igProtoDelta 𐑠 (by decide)).isDagger = true ∧
    igProtoMu_depth (paralogical_dagger (by decide)) = 1 := by
  constructor
  · exact igProtoCopy_isDagger
  · exact igProtoMu_depth

-- Loop closure: protocol has period 8 and depth 1
theorem i_dialetheic_bootstrap_loop_closure :
    ∃ (loop : IGProtocol 𐑠 𐑠),
      loop = i_dialetheic_bootstrap_protocol (by decide) ∧
      loop.period = 8 ∧ loop.depth = 1 := by
  exact ⟨_, rfl, by decide, by decide⟩

-- Back-propagation / LinFix obligation:
-- igProtoCopy_isDagger licenses IMSCRIB→IFIX burn
-- CLINK→IMSCRIB weighted edge feeds next winding (.seq continuation)

end Imscribing
