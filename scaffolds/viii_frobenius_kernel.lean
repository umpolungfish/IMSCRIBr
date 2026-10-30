-- IGProtocol scaffold: VINIT → FSPLIT → FFUSE → TANCH
-- Class: VIII_Frobenius_Kernel
-- Fingerprint: sig=(2,2,0,0)
--   self_ref=False | frobenius_order=1
--   dialetheia_complete=False | period=4
-- Expected tier: O₂
-- FSPLIT/FFUSE pairs: [(1, 2)]

import Imscribing.IGMorphism
import Imscribing.IGFunctor

namespace Imscribing
open Primitives Frobenius IGProtocol
open Dimensionality Topology Relational Polarity Grammar
     Fidelity KineticChar Granularity Criticality Protection Stoichiometry Chirality

-- ── Token → IG field mapping ──────────────────────────────────────────────
--   [0] VINIT     dim    := 𐑼               𐑼 → 𐑚  | initial object — ground of distinction
--   [1] FSPLIT    gran   := 𐑚               𐑚 → 𐑚  | split δ — range decomposition
--   [2] FFUSE     stoi   := 𐑙               𐑙 → 𐑡  | fuse μ — assembly mode
--   [3] TANCH     top    := 𐑡               𐑙 → 𐑼  | terminal object — connectivity boundary

-- ── Main IGProtocol term ────────────────────────────────────────────────────

noncomputable def viii_frobenius_kernel_protocol : IGProtocol 𐑼 𐑡 :=
  .withGram 𐑠 <|
  -- Seq chain:
  (.arrow 𐑼 𐑼 𐑚)  -- [0] VINIT | dim := 𐑼 | initial object — ground of distinction
  -- FSPLIT [1] (gran := 𐑚) / FFUSE [2] (stoi := 𐑙)
  .seq
    (.prod
      -- T-branch (0 nodes)
      (.refl 𐑙)  -- T-branch: empty arc (direct to FFUSE.T)
      -- F-branch (0 nodes)
      (.refl 𐑙))  -- F-branch: empty arc (direct to FFUSE.F)
    -- reconnect at FFUSE [2]: μ closes the Frobenius pair
    (.arrow 𐑙 𐑙 𐑡)  -- [2] FFUSE | stoi := 𐑙
  (.arrow 𐑡 𐑙 𐑼)  -- [3] TANCH | top := 𐑡 | terminal object — connectivity boundary

-- ── Verification theorems ───────────────────────────────────────────────────

theorem viii_frobenius_kernel_tier : TierFunctor.obj 𐑼 = .O₂ := by decide

-- Frobenius (split → fuse): μ∘δ = id on .prod branch
-- Proof: apply igFrobAlg_self_fusion; exact mu_delta_A_id
-- (requires mu_delta_A_id from IGFunctor library)

end Imscribing
