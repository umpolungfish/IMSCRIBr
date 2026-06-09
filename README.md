# IMSCRIBr — IMASM Arrangement Space Iterator

Maps the **12⁸ = 429,981,696** possible arrangements of the 12 IMASM tokens into structural fingerprint classes.

## Overview

The IMASM token system consists of 12 tokens in 4 algebraic families:

| Family | Count | Tokens | Role |
|--------|-------|--------|------|
| Logical | 6 | VINIT, TANCH, AFWD, AREV, CLINK, IMSCRIB | Category skeleton |
| Frobenius | 2 | FSPLIT, FFUSE | μ∘δ=id algebra |
| Dialetheia | 3 | EVALT, EVALF, ENGAGR | Belnap FOUR lattice |
| Linear | 1 | IFIX | Irreversible fixation (!) |

Every length-8 arrangement receives a **structural fingerprint** capturing:

- Family signature (L, F, D, X)
- Start/end tokens and self-reference
- Frobenius pair ordering (split→fuse, fuse→split, both, none)
- Dialetheia completeness (all 3 present?)
- Periodicity, token diversity, family adjacency, transition counts

## The 12 Canonical Arrangement Classes

| # | Class | Signature | Tier | Key Property |
|---|-------|-----------|------|--------------|
| I | Dialetheic Bootstrap | (2,2,3,1) | O₂ | Self-referential paradox |
| II | Void Genesis | (4,2,0,1) | O₀ | Creation ex nihilo |
| III | Anchor Protocol | (5,0,0,1) | O₁ | Period-3 Sabbath cycle |
| IV | Dual Bootstrap | (4,2,0,1) | O_∞ | Inverted Frobenius |
| V | Linear Chain | (0,0,0,8) | O₀ | Pure recording |
| VI | Empty Bootstrap | (8,0,0,0) | O₁ | Period-2 oscillation |
| VII | Parakernel | (2,2,3,1) | O₂ | Engram of contradiction |
| VIII | Frobenius Kernel | (2,2,0,0) | O₀ | Minimal 4-step algebra |
| IX | Chiral Pairs | (8,0,0,0) | O₁ | Period-2 handedness |
| X | Truth Machine | (2,2,2,2) | O₁ | Binary classifier |
| XI | Eternal Return | (7,0,0,0) | O₂ | Unclosed period-3 |
| XII | ROM Burn | (1,0,3,4) | O₀ | Layered truth record |

## Files

```
IMSCRIBr/
├── tokens.py          # Token enum, families, signatures
├── classifier.py      # StructuralFingerprint, coarse/fine keys
├── engine.py          # Signature-decomposed enumeration, SpaceMap
├── run_map.py         # CLI runner
├── IMASM_SPACE_MAP_REPORT.md  # Full analysis report
└── README.md
```

## Usage

```bash
cd /home/mrnob0dy666/IMSCRIBr

# Sample 50M arrangements (default)
python run_map.py

# Full 430M enumeration (~1-2 hours)
python run_map.py --full

# Custom sample size
python run_map.py --sample 10000000

# Search for canonical arrangements
python run_map.py --search
```

## Key Findings

- **All 12 canonical classes verified** — exact positions confirmed
- **~1,000–2,000 distinct structural classes** in the full space
- The 12 canonicals occupy only **~0.007%** of total space
- Self-referential + Frobenius + Dialetheia-complete arrangements are extremely rare (~0.01%)
- Power-law class size distribution: a few massive classes, hundreds tiny

## Programmatic API

```python
from engine import map_space, enumerate_signatures, search_arrangements
from classifier import compute_fingerprint
from tokens import Token

# Map the space
smap = map_space(length=8, max_total=5_000_000)
print(smap.summary())

# Compute fingerprint for any arrangement
arr = (5, 8, 6, 9, 7, 10, 11, 5)  # Dialetheic Bootstrap
fp = compute_fingerprint(arr)
print(fp.description())

# Search constrained arrangements
results = search_arrangements(
    length=8, start_token=Token.IMSCRIB,
    self_referential=True, frobenius_order=1,
    max_results=20,
)
```
