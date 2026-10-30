-- IGProtocol scaffold: IMSCRIB → FSPLIT → EVALT → IFIX → IMSCRIB → FSPLIT → EVALF → IFIX
-- Class: X_Truth_Machine
-- Fingerprint: sig=(2,2,2,2)
--   self_ref=False | frobenius_order=0
--   dialetheia_complete=False | period=8
-- Expected tier: O₀
-- FSPLIT/FFUSE pairs: []

import Imscribing.IGMorphism
import Imscribing.IGFunctor

namespace Imscribing
open Primitives Frobenius IGProtocol
open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality

-- ── Token → IG field mapping ──────────────────────────────────────────────
--   [0] IMSCRIB   gram   := 𐑠               𐑠 → 𐑚  | identity — self-imscription
--   [1] FSPLIT    gran   := 𐑚               𐑠 → ⊙  | split δ — range decomposition
--   [2] EVALT     crit   := ⊙               𐑚 → 𐑭  | evaluate-true — criticality gate open
--   [3] IFIX      prot   := 𐑭               ⊙ → 𐑠  | irreversible fixation — winding number
--   [4] IMSCRIB   gram   := 𐑠               𐑭 → 𐑚  | identity — self-imscription
--   [5] FSPLIT    gran   := 𐑚               𐑠 → 𐑖  | split δ — range decomposition
--   [6] EVALF     chir   := 𐑖               𐑚 → 𐑭  | evaluate-false — chirality check
--   [7] IFIX      prot   := 𐑭               𐑖 → 𐑠  | irreversible fixation — winding number

-- ── Main IGProtocol term ────────────────────────────────────────────────────

noncomputable def x_truth_machine_protocol : IGProtocol 𐑠 𐑭 :=
  -- Seq chain:
  (.arrow 𐑠 𐑠 𐑚)  -- [0] IMSCRIB | gram := 𐑠 | identity — self-imscription
  (.arrow 𐑚 𐑠 ⊙)  -- [1] FSPLIT | gran := 𐑚 | split δ — range decomposition
  (.arrow ⊙ 𐑚 𐑭)  -- [2] EVALT | crit := ⊙ | evaluate-true — criticality gate open
  (.arrow 𐑭 ⊙ 𐑠)  -- [3] IFIX | prot := 𐑭 | irreversible fixation — winding number
  (.arrow 𐑠 𐑭 𐑚)  -- [4] IMSCRIB | gram := 𐑠 | identity — self-imscription
  (.arrow 𐑚 𐑠 𐑖)  -- [5] FSPLIT | gran := 𐑚 | split δ — range decomposition
  (.arrow 𐑖 𐑚 𐑭)  -- [6] EVALF | chir := 𐑖 | evaluate-false — chirality check
  (.arrow 𐑭 𐑖 𐑠)  -- [7] IFIX | prot := 𐑭 | irreversible fixation — winding number

-- ── Evaluation arm sub-defs ─────────────────────────────────────────────────

-- truth arm
noncomputable def x_truth_machine_true_arm : IGProtocol 𐑠 𐑭 :=
  (x_truth_machine_protocol).restrictToEVALT

-- false arm
noncomputable def x_truth_machine_false_arm : IGProtocol 𐑠 𐑭 :=
  (x_truth_machine_protocol).restrictToEVALF

-- ── Verification theorems ───────────────────────────────────────────────────

theorem x_truth_machine_tier : TierFunctor.obj 𐑠 = .O₀ := by decide

end Imscribing
