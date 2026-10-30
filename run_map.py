#!/usr/bin/env python3
"""
IMASM ARRANGEMENT SPACE — FULL MAPPING RUNNER
==============================================
Maps the 12^8 = 429,981,696 arrangement space into structural classes,
discovers novel classes beyond the 12 canonical, and exports results.

Usage:
    cd /home/mrnob0dy666/IMSCRIBr
    python run_map.py                    # sample 50M arrangements
    python run_map.py --full             # full 430M enumeration (~1-2 hours)
    python run_map.py --sample 10000000  # custom sample size
    python run_map.py --search           # find all canonical arrangements

Output:
    imasm_space_map.json       — full class map
    imasm_summary.txt          — human-readable summary
"""

import argparse
import json
import sys
import os
import time

# Standalone flat-directory imports — no parent-package hack needed
from engine import (
    map_space, enumerate_signatures, SpaceMap,
    search_arrangements, count_arrangements,
)
from classifier import (
    CANONICAL_CLASSES, CANONICAL_FINGERPRINTS,
    StructuralFingerprint, compute_fingerprint,
    match_canonical,
)
from tokens import Token, arrangement_str, TOKEN_NAMES


OUTPUT_DIR = os.path.dirname(os.path.abspath(__file__))


def main():
    parser = argparse.ArgumentParser(description="Map the IMASM arrangement space")
    parser.add_argument("--full", action="store_true",
                        help="Full 430M enumeration")
    parser.add_argument("--sample", type=int, default=50_000_000,
                        help="Sample size (default: 50M)")
    parser.add_argument("--length", type=int, default=8,
                        help="Arrangement length (default: 8)")
    parser.add_argument("--checkpoint", type=int, default=5_000_000,
                        help="Checkpoint interval")
    parser.add_argument("--search", action="store_true",
                        help="Search for canonical arrangements and report")
    args = parser.parse_args()

    length = args.length
    total_space = count_arrangements(length)
    signatures = enumerate_signatures(length)

    if args.search:
        do_search(signatures, length)
        return

    print(f"IMASM Arrangement Space Mapper")
    print(f"  Length: {length}")
    print(f"  Total space: {total_space:,} arrangements")
    print(f"  Signatures: {len(signatures)}")
    print()

    if args.full:
        max_total = None
        print("Mode: FULL enumeration of all 430M arrangements")
        print("Estimated time: 1-3 hours depending on CPU")
    else:
        max_total = min(args.sample, total_space)
        print(f"Mode: SAMPLING {max_total:,} arrangements "
              f"({100*max_total/total_space:.1f}% of space)")
    print()

    t0 = time.time()
    checkpoint_path = os.path.join(OUTPUT_DIR, "imasm_checkpoint.json")

    smap = map_space(
        length=length,
        max_total=max_total,
        checkpoint_interval=args.checkpoint,
        checkpoint_path=checkpoint_path,
        signatures=signatures,
        verbose=True,
    )

    elapsed = time.time() - t0

    # Summary
    summary = smap.summary()
    print()
    print(summary)

    summary_path = os.path.join(OUTPUT_DIR, "imasm_summary.txt")
    with open(summary_path, 'w') as f:
        f.write(summary)
        f.write(f"\n\nElapsed: {elapsed:.1f}s ({elapsed/3600:.2f}h)\n")

    # Full map JSON
    map_path = os.path.join(OUTPUT_DIR, "imasm_space_map.json")
    smap.to_json(map_path)
    print(f"\nFull map: {map_path}")
    print(f"Summary:  {summary_path}")
    print(f"Total time: {elapsed:.1f}s ({elapsed/3600:.2f}h)")


def do_search(signatures, length):
    """Find all canonical arrangements and report their coarse class sizes."""
    print("=== CANONICAL ARRANGEMENT SEARCH ===\n")
    for name in sorted(CANONICAL_CLASSES.keys()):
        arr = CANONICAL_CLASSES[name]
        if len(arr) != length:
            print(f"{name}: length={len(arr)} (different from scan length {length})")
            fp = compute_fingerprint(arr)
            print(f"  Coarse key: {fp.coarse_key()}")
            print(f"  {fp.description()}")
            print()
            continue

        fp = compute_fingerprint(arr)
        print(f"{name}:")
        print(f"  Sequence:    {arrangement_str(arr)}")
        print(f"  Description: {fp.description()}")
        print(f"  Coarse key:  {fp.coarse_key()}")

        # Find all arrangements with same coarse key
        matches = search_arrangements(
            length=length,
            start_token=Token(arr[0]),
            end_token=Token(arr[-1]),
            frobenius_order=fp.frobenius_order,
            dialetheia_complete=fp.dialetheia_complete,
            period=fp.period,
            max_results=100000,
        )
        # Filter to exact coarse match
        coarse_matches = [a for a in matches
                          if compute_fingerprint(a).coarse_key() == fp.coarse_key()]
        print(f"  Coarse class size: {len(coarse_matches):,} arrangements")
        print()


if __name__ == "__main__":
    main()
