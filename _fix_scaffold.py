#!/usr/bin/env python3
"""
Fix proof_scaffold.py: emit proper Imscription-stage-indexed IGProtocol terms.
replaces bare primitive glyphs with named Imscription stage objects.
"""
import re

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py") as f:
    src = f.read()

# 1. Inject _IG_TO_LEAN_CONS mapping after _TOKEN_IG
_IG_VAL_TO_LEAN = '''# ── IG value → Lean constructor suffix ──────────────────────────────

_IG_VAL_TO_LEAN_CONS = {
    # Dimensionality (dim)
    "𐑛": "dead", "𐑨": "ash", "𐑼": "array", "𐑦": "if'",
    # Topology (top)
    "𐑡": "judge", "𐑰": "eat", "𐑥": "mime", "𐑶": "oil", "𐑸": "are",
    # Relational (rel)
    "𐑩": "ado", "𐑑": "tot", "𐑽": "ear", "𐑾": "ian",
    # Polarity (pol)
    "𐑗": "church", "𐑿": "yew", "𐑬": "out", "𐑯": "nun", "𐑹": "or'",
    # Fidelity (fid)
    "𐑱": "age", "𐑞": "they", "𐑐": "peep",
    # KineticChar (kin)
    "𐑺": "yea", "𐑪": "loll", "𐑧": "egg", "𐑤": "on", "𐑘": "air",
    # Granularity (gran)
    "𐑲": "bib", "𐑚": "thigh", "𐑔": "ice",
    # Grammar (gram)
    "𐑝": "vow", "𐑜": "gag", "𐑠": "measure", "𐑵": "ooze",
    # Criticality (crit)
    "𐑢": "woe", "⊙": "monad", "𐑮": "roar", "𐑻": "err", "𐑣": "haha",
    # Chirality (chir)
    "𐑓": "fee", "𐑒": "kick", "𐑖": "sure", "𐑫": "wool",
    # Stoichiometry (stoi)
    "𐑙": "hung", "𐑕": "so", "𐑳": "up",
    # Protection (prot)
    "𐑷": "awe", "𐑴": "oak", "𐑭": "ah", "𐑟": "zoo",
}

_IG_FIELD_TO_TYPENAME = {
    "dim": "Dimensionality", "top": "Topology", "rel": "Relational",
    "pol": "Polarity", "fid": "Fidelity", "kin": "KineticChar",
    "gran": "Granularity", "gram": "Grammar", "crit": "Criticality",
    "chir": "Chirality", "stoi": "Stoichiometry", "prot": "Protection",
}

def _lean_val(v: str) -> str:
    """Map IG glyph to full Lean constructor: e.g. 𐑠 → Grammar.measure"""
    for field, typename in _IG_FIELD_TO_TYPENAME.items():
        if any(tok_val == v for _, (tf, tv, _) in _TOKEN_IG.items() if tf == field):
            cons = _IG_VAL_TO_LEAN_CONS.get(v)
            if cons:
                return f"{typename}.{cons}"
    # Fallback: search all type names
    for typename in _IG_FIELD_TO_TYPENAME.values():
        for igv, cons in _IG_VAL_TO_LEAN_CONS.items():
            if igv == v:
                return f"{typename}.{cons}"
    return v  # passthrough if unknown

def _lean_field_val(field: str, v: str) -> str:
    """Map (field, IG glyph) to full Lean expression: e.g. (gram, 𐑠) → Grammar.measure"""
    tn = _IG_FIELD_TO_TYPENAME.get(field, "?")
    cons = _IG_VAL_TO_LEAN_CONS.get(v, v)
    return f"{tn}.{cons}"

'''

# Insert after _TOKEN_IG definition
insert_after = "# ── Token → dominant IG field ─────────────────────────────────────────────────\n\n"
pos = src.find(insert_after)
if pos >= 0:
    eol = src.find('\n', pos)
    rest = src.find('\n\n', eol)
    # find the end of _TOKEN_IG dict
    dict_end = src.find('\n\n', src.find('}', src.find('_TOKEN_IG')))
    insert_pos = dict_end + 2
    src = src[:insert_pos] + '\n' + _IG_VAL_TO_LEAN + src[insert_pos:]
    print(f"Inserted _IG_VAL_TO_LEAN_CONS at position {insert_pos}")
else:
    print("WARNING: could not find insertion point")

with open("/home/mrnob0dy666/imsgct/IMSCRIBr/proof_scaffold.py", "w") as f:
    f.write(src)
print("Written phase 1")
