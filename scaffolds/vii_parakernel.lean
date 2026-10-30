-- IGProtocol scaffold: EVALF → AREV → FSPLIT → EVALT → AFWD → FFUSE → ENGAGR → IFIX
-- Class: VII_Parakernel
-- Fingerprint: sig=(2,2,3,1)
--   self_ref=False | frobenius_order=1
--   dialetheia_complete=True | period=8
-- Expected tier: O₂
-- FSPLIT/FFUSE pairs: [(2, 5)]

import Imscribing.IGMorphism
import Imscribing.IGFunctor

namespace Imscribing
open Primitives Frobenius IGProtocol
open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality

-- ── Token → IG field mapping ──────────────────────────────────────────────
--   [0] EVALF     chir   := 𐑖               𐑖 → 𐑗  | evaluate-false — chirality check
--   [1] AREV      pol    := 𐑗               𐑖 → 𐑚  | reverse morphism — parity flip
--   [2] FSPLIT    gran   := 𐑚               𐑚 → 𐑚  | split δ — range decomposition
--   [3] EVALT     crit   := ⊙               𐑚 → 𐑙  | evaluate-true — criticality gate open
--   [4] AFWD      rel    := 𐑾               𐑚 → 𐑙  | forward morphism — bidirectional arrow
--   [5] FFUSE     stoi   := 𐑙               𐑙 → 𐑳  | fuse μ — assembly mode
--   [6] ENGAGR    stoi   := 𐑳               𐑙 → 𐑭  | engage paradox — B-state, both arms
--   [7] IFIX      prot   := 𐑭               𐑳 → 𐑖  | irreversible fixation — winding number

-- ── Main IGProtocol term ────────────────────────────────────────────────────

noncomputable def vii_parakernel_protocol : IGProtocol 𐑖 𐑭 :=
  .withGram 𐑠 <|
  -- Seq chain:
  (.arrow 𐑖 𐑖 𐑗)  -- [0] EVALF | chir := 𐑖 | evaluate-false — chirality check
  (.arrow 𐑗 𐑖 𐑚)  -- [1] AREV | pol := 𐑗 | reverse morphism — parity flip
  -- FSPLIT [2] (gran := 𐑚) / FFUSE [5] (stoi := 𐑙)
  .seq
    (.prod
      -- T-branch (2 nodes)
      .seq
        (.arrow ⊙ 𐑚 𐑙)  -- [3] EVALT | crit := ⊙ | evaluate-true — criticality gate open
        (.arrow 𐑾 𐑚 𐑙)  -- [4] AFWD | rel := 𐑾 | forward morphism — bidirectional arrow
      -- F-branch (0 nodes)
      (.refl 𐑙))  -- F-branch: empty arc (direct to FFUSE.F)
    -- reconnect at FFUSE [5]: μ closes the Frobenius pair
    (.arrow 𐑙 𐑙 𐑳)  -- [5] FFUSE | stoi := 𐑙
  (.arrow 𐑳 𐑙 𐑭)  -- [6] ENGAGR | stoi := 𐑳 | engage paradox — B-state, both arms
  (.arrow 𐑭 𐑳 𐑖)  -- [7] IFIX | prot := 𐑭 | irreversible fixation — winding number

-- ── Evaluation arm sub-defs ─────────────────────────────────────────────────

-- truth arm
noncomputable def vii_parakernel_true_arm : IGProtocol 𐑖 𐑭 :=
  (vii_parakernel_protocol).restrictToEVALT

-- false arm
noncomputable def vii_parakernel_false_arm : IGProtocol 𐑖 𐑭 :=
  (vii_parakernel_protocol).restrictToEVALF

-- ── Verification theorems ───────────────────────────────────────────────────

theorem vii_parakernel_tier : TierFunctor.obj 𐑖 = .O₂ := by decide

-- Frobenius (split → fuse): μ∘δ = id on .prod branch
-- Proof: apply igFrobAlg_self_fusion; exact mu_delta_A_id
-- (requires mu_delta_A_id from IGFunctor library)

end Imscribing
