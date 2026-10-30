#!/usr/bin/env python3
"""Batch excribe 25 chosen catalog entries to excription log.

Reads from WORDZ library (WORDZ.txt) or wordbook for raw glyph words.
Writes elaborated excriptions to IMSCRIBr/logs/EXCRIPTIONS_<date>.log
"""
import sys, os, json
from datetime import datetime
sys.path.insert(0, os.path.dirname(__file__))

from excriber_v3 import (
    excribe_batched, LlmBackend, resolve_provider_model, render,
    GLYPH_TO_OPCODE, OPCODE_TO_GLYPH, parse_word, OP_SEM, find_pairs_by_ancestry,
    ExcribedStep, Excription, ForkFusePair
)

# ── 25 picks ──────────────────────────────────────────────────
PICKS = [
    'universal_imscriptive_grammar',
    'riemann_hypothesis',
    'yang_mills_mass_gap',
    'navier_stokes_existence_smoothness',
    'collatz_conjecture',
    'goldbach_conjecture',
    'perfect_cuboid',
    'twin_prime_conjecture',
    'beal_conjecture',
    'p_vs_np',
    'human_consciousness',
    'void_genesis',
    'truth_machine',
    'quantum_gravity',
    'dark_energy',
    'monad',
    'belnap_multilattice_sic_povm',
    'clink_l8',
    'emerald_tablet',
    'philosophers_stone',
    'langlands_correspondence',
    'homotopy_type_theory',
    'standard_model',
    'genetic_code_emergence',
    'momonados',
]

WORD_BOOK = os.path.expanduser("/home/mrnob0dy666/imsgct/MoDoT/ob3ects/imasm_catalog_words.json")
WORDZ_LIB = os.path.expanduser("/home/mrnob0dy666/imsgct/WORDZ.txt")
LOG_DIR   = os.path.expanduser("/home/mrnob0dy666/imsgct/IMSCRIBr/logs")
os.makedirs(LOG_DIR, exist_ok=True)

TIMESTAMP = datetime.now().strftime("%Y-%m-%d_%H%M%S")
OUTPUT    = os.path.join(LOG_DIR, f"EXCRIPTIONS_{TIMESTAMP}.log")

def main():
    # Load wordbook
    with open(WORD_BOOK) as f:
        book = json.load(f)

    # Resolve LLM
    provider_name, model_name, api_key = resolve_provider_model()
    print(f"Using {provider_name} / {model_name}", file=sys.stderr)
    llm = LlmBackend(provider=provider_name, model=model_name, api_key=api_key)

    all_text = []
    n = len(PICKS)

    for i, name in enumerate(PICKS):
        word = book.get(name, "")
        if not word:
            print(f"[{i+1}/{n}] SKIP {name}: not in wordbook", file=sys.stderr)
            all_text.append(f"=== {name}: NOT FOUND IN WORDBOOK ===\n")
            continue

        print(f"[{i+1}/{n}] EXCRIBING: {name} ({len(word)}-char word)", file=sys.stderr)
        try:
            exc = excribe_batched(word, name, f"the {name.replace('_', ' ')} system", llm)
            text = render(exc)
        except Exception as e:
            print(f"  ERROR: {e}", file=sys.stderr)
            text = f"=== {name}: ERROR ===\n{e}\n"

        all_text.append(text)
        print(f"  done ({len(exc.steps)} steps, verdict={exc.verdict})", file=sys.stderr)

    # Write to EXCRIPTION LOG (not WORDZ library)
    header = f"""EXCRIPTIONS — {n} IMASM Catalog Entries Excribed
====================================================
Excriber v3 | Provider: {provider_name} | Model: {model_name}
Generated: {datetime.now().isoformat()}
Source library: {WORD_BOOK}

"""
    with open(OUTPUT, 'w') as f:
        f.write(header)
        for i, text in enumerate(all_text):
            f.write(f"\n{'─' * 72}\n")
            f.write(f"ENTRY {i+1} of {n}\n")
            f.write(f"{'─' * 72}\n\n")
            f.write(text)
            f.write("\n")

    print(f"\nWrote excription log: {OUTPUT} ({len(all_text)} entries)", file=sys.stderr)
    print(f"WORDZ library unchanged: {WORDZ_LIB}", file=sys.stderr)

if __name__ == "__main__":
    main()
