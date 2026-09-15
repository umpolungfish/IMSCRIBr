# IMSCRIBr, IMASM Arrangement Space Iterator

![language](https://img.shields.io/badge/language-Python-3776AB?style=for-the-badge&logo=python&logoColor=white) ![space](https://img.shields.io/badge/space-12%E2%81%B8%20arrangements-8A2BE2?style=for-the-badge) ![tier](https://img.shields.io/badge/tier-O%E2%88%9E-8A2BE2?style=for-the-badge) ![μ∘δ](https://img.shields.io/badge/%CE%BC%E2%88%98%CE%B4-id-00A86B?style=for-the-badge) ![licence](https://img.shields.io/badge/licence-LUNLICENSE-1A1A1A?style=for-the-badge)

Maps the **12⁸ = 429,981,696** possible arrangements of the 12 IMASM tokens
into structural fingerprint classes: 430M arrangements → 165 family
signatures → ~1,000–2,000 coarse structural classes → exactly 12 canonical
archetypes. The vast token space collapses to 12 archetypes - evidence the
12-primitive structure is the natural basis of the arrangement space.

## The 12 tokens in 4 families

| Family | Tokens | Role |
|---|---|---|
| Logical (6) | VINIT TANCH AFWD AREV CLINK IMSCRIB | category skeleton: objects, morphisms, composition, identity |
| Frobenius (2) | FSPLIT FFUSE | the μ∘δ=id algebra; split→fuse order is verification |
| Dialetheia (3) | EVALT EVALF ENGAGR | the three truth values |
| Linear (1) | IFIX | irreversible fixation |

Grouped by family signature and structural fingerprint (topology,
self-reference, Frobenius order, periodicities), the space collapses: 165
signatures, ~1–2k coarse classes, and the 12 canonical archetypes sit in the
sparse low-entropy outlier region.

## The 12 canonical classes

I Dialetheic Bootstrap (self-referential paradox engine, O₂) ·
II Void Genesis (creation ex nihilo, O₀) ·
III Anchor Protocol (period-3 sabbath cycle, O₁) ·
IV Dual Bootstrap (inverted Frobenius, O_∞) ·
V Linear Chain (pure recording, unique) ·
VI Empty Bootstrap (period-2 oscillator, unique) ·
VII Parakernel (engram of contradiction, O₂) ·
VIII Frobenius Kernel (minimal 4-step algebra) ·
IX Chiral Pairs · X Truth Machine ·
XI Eternal Return · XII ROM Burn.
Full opcode sequences, signatures, and class sizes in the backup.

## Use

Requires Python ≥3.10, stdlib only, zero dependencies:

```bash
cd imsgct/IMSCRIBr
python run_map.py                 # 50M sample (default)
python run_map.py --full          # full 430M (~1–3h)
python run_map.py --sample 10000000
python run_map.py --search        # canonical arrangements + class sizes
```

Outputs `imasm_summary.txt`, `imasm_space_map.json`, `imasm_checkpoint.json`.
Full 943-line original in `README_backups/IMSCRIBr_README.md`. Unlicense.

$\mu\circ\delta = \mathrm{id}$
