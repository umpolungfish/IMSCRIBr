#!/usr/bin/env python3
"""
newton_lift.py — Newton-style grammar dissolution pipeline.

Takes grammar-derived structural truths and translates them into conventional
academic prose that never mentions the grammar. Like Newton's Principia —
the scaffold dissolves; only the coagula remains.

Three modes:
  dissolve  — translate grammar findings JSON into conventional prose
  verify    — check that prose contains no grammar notation
  lift      — full pipeline: dissolve + verify + report

Usage:
  python newton_lift.py dissolve findings.json
  python newton_lift.py verify output.md
  python newton_lift.py lift findings.json --output output.md
  python newton_lift.py lift findings.json --output output.tex --format latex
"""

import argparse
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, List, Optional, Tuple

try:
    import requests
except ImportError:
    sys.exit('requests not installed')

# ── Grammar notation patterns to detect in verification ──────────────────

GRAMMAR_PATTERNS: List[str] = [
    # ── Shavian block (U+10450–U+1047F) + ⊙ ──────────────────────────────────
    r'[𐑐𐑑𐑒𐑓𐑔𐑕𐑖𐑗𐑘𐑙𐑚𐑛𐑜𐑝𐑞𐑟𐑠𐑡𐑢𐑣𐑤𐑥𐑦𐑧𐑨𐑩𐑪𐑫𐑬𐑭𐑮𐑯𐑰𐑱𐑲𐑳𐑴𐑵𐑶𐑷𐑸𐑹𐑺𐑻𐑼𐑽𐑾𐑿⊙]',
    # LaTeX \text{} containing any Shavian glyph or ⊙
    r'\\text\{[𐑐𐑑𐑒𐑓𐑔𐑕𐑖𐑗𐑘𐑙𐑚𐑛𐑜𐑝𐑞𐑟𐑠𐑡𐑢𐑣𐑤𐑥𐑦𐑧𐑨𐑩𐑪𐑫𐑬𐑭𐑮𐑯𐑰𐑱𐑲𐑳𐑴𐑵𐑶𐑷𐑸𐑹𐑺𐑻𐑼𐑽𐑾𐑿⊙]\}',
    # Angle-bracket tuple notation
    r'⟨[^⟩]*[;][^⟩]*⟩',

    # ── imscribe / imscription family ─────────────────────────────────────────
    r'\bimscrib',                   # imscribe, imscribed, imscribing, IMSCRIBr
    r'\bimscription',               # imscription, imscriptions (different stem: imscri-p not imscri-b)
    r'\bIMSCRIBr\b',

    # ── Ouroboricity / tier labels ────────────────────────────────────────────
    r'\bourobor',                   # ouroboric, ouroboricity, ouroboros
    r'\bO_\d\b',                    # O_0 through O_9
    r'\bO_\\infty\b',               # O_\infty (LaTeX form in prose)
    r'\bO_∞',                       # O_∞ (Unicode form — no trailing \b, ∞ is non-word char)
    r'O_\{\\infty\}',               # O_{\infty} (LaTeX braced form)

    # ── Grammar / catalog / crystal vocabulary ────────────────────────────────
    r'\bimscribing\s+[Gg]rammar\b',
    r'\bImscribing\s+Grammar\b',
    r'\bIG\s+catalog\b',
    r'\bcatalog\s+(?:entry|entries|address)\b',
    r'\bcrystal\s+of\s+types\b',
    r'\bcrystal[._](?:encode|decode|address)\b',
    r'\bcrystal_address\b',
    r'\bstructural\s+typ(?:e|es|ing)\b',
    r'\bstructural\s+address\b',
    r'\bFrobenius\s+address\b',
    r'\bT[-_\s]object\b',

    # ── Primitive / primitive names ───────────────────────────────────────────
    r'\bprimitive[s]?\b',

    # ── Consciousness / ⊙ ────────────────────────────────────────────────
    r'\bconsciousness[._]score\b',
    r'\bPhi_c\b',

    # ── Grammar-specific ZFC variants ────────────────────────────────────────
    r'\bZFC_(?:t|T|fe|FE)\b',
    r'\bZFCt\b',
    r'\bZFCfe\b',

    # ── Paraconsistent / Belnap (grammar-specific usage) ─────────────────────
    r'\bBelnap\s+(?:four|FOUR|Four|[24])\b',
    r'\bdialetheic\b',

    # ── IMASM token system ────────────────────────────────────────────────────
    r'\bIMASM\b',
    r'\bimasm\b',

    # ── Shavian notation keyword ──────────────────────────────────────────────
    r'\bShavian\b',

    # ── Repo / tool artifact names ────────────────────────────────────────────
    r'\bob3ect\b',
    r'\bp4rakernel\b',
    r'\bp4ramill\b',
    r'\bCL8NK\b',
    r'\bCLINK\b',
    r'\bSerpentRod\b',
    r'\bimscriptionbox\b',

    # ── Magnum Opus (alchemy↔grammar mapping) ────────────────────────────────
    r'\bMagnum\s+Opus\b',

    # ── Stoichiometric type (grammar-specific framing) ────────────────────────
    r'\bstoichiometric\s+type\b',
]

COMPILED_PATTERNS = [re.compile(p) for p in GRAMMAR_PATTERNS]

DEFAULT_LEDGER_PATH = Path(__file__).parent / "pathway_ledger.json"

# ── Data types ───────────────────────────────────────────────────────────────

@dataclass
class GrammarFinding:
    """A single structural truth discovered through the grammar."""
    finding_type: str  # structural_identity, near_identity, collapse, promotion, analog, tier, cross_domain
    system_a: str
    system_b: Optional[str] = None
    distance: Optional[float] = None
    description_a: str = ""
    description_b: str = ""
    domain: str = ""
    details: Dict = field(default_factory=dict)

@dataclass
class DissolutionSpec:
    """Full specification for a grammar dissolution."""
    domain: str  # e.g. ecology, physics, mathematics, consciousness
    title: str = ""
    audience: str = "intellectual_peers"  # intellectual_peers, specialists, general
    format: str = "markdown"  # markdown or latex
    findings: List[GrammarFinding] = field(default_factory=list)
    style_hints: str = ""  # optional: Newton, Darwin, Feynman, etc.
    elevation_enabled: bool = True  # set False for republish/correction runs with no new claim
    baseline: Optional[str] = None  # override; else pulled from the ledger's last entry for domain
    elevation_target: Optional[str] = None  # optional steering hint for the next elevation, never required

@dataclass
class VerificationResult:
    """Result of grammar-notation verification."""
    clean: bool
    violations: List[Tuple[str, int, str]] = field(default_factory=list)  # (pattern, line_no, line_text)

@dataclass
class SemanticVerificationResult:
    """Result of the fidelity + elevation + rigor judge pass."""
    ok: bool
    fidelity_issues: List[Tuple[int, str, str]] = field(default_factory=list)  # (finding_idx, expected_band, problem)
    rigor_issues: List[Tuple[int, str]] = field(default_factory=list)  # (finding_idx, problem)
    elevation_ok: bool = True
    elevation_count: int = 0
    elevation_summary: Optional[str] = None

# ── Pathway ledger ───────────────────────────────────────────────────────────
# Append-only record of fundamental truths already seeded per domain through
# passing lift() runs (or manual `ledger seed`). Holds only verified, published
# truths — never aspirational future claims; those belong in human-authored
# roadmap notes, never auto-applied.

def load_ledger(path=DEFAULT_LEDGER_PATH):
    """Load the pathway ledger. Returns {} if the file doesn't exist yet."""
    path = Path(path)
    if not path.exists():
        return {}
    with open(path) as f:
        return json.load(f)


def save_ledger(ledger, path=DEFAULT_LEDGER_PATH):
    """Persist the pathway ledger."""
    with open(path, "w") as f:
        json.dump(ledger, f, indent=2)
        f.write("\n")


def ledger_last_entry(ledger, domain):
    """Return the most recent truth string for a domain, or None if unseeded."""
    entries = ledger.get(domain, [])
    return entries[-1]["truth"] if entries else None


def append_ledger_entry(ledger, domain, truth, source_title=""):
    """Append a new truth to a domain's ledger entries (mutates and returns ledger)."""
    ledger.setdefault(domain, []).append({
        "truth": truth,
        "source_title": source_title,
    })
    return ledger


# ── Magnitude banding ────────────────────────────────────────────────────────
# Deterministic, pure-Python classification of a finding's quantitative content
# into a named band. Used to verify the dissolved prose preserves the correct
# relative magnitude even though the literal number never appears in the output.

_DISTANCE_BAND_TYPES = {"structural_identity", "near_identity", "collapse", "cross_domain", "analog"}

def _distance_band(d):
    if d is None:
        return None
    if d < 0.01:
        return "exact"
    if d < 1.0:
        return "near"
    if d < 3.0:
        return "moderate"
    if d < 6.0:
        return "major"
    return "severe"


def _score_band(s):
    if s is None:
        return None
    if s < 0.33:
        return "emerging"
    if s < 0.66:
        return "partial"
    if s < 0.9:
        return "near-ceiling"
    return "at-ceiling"


def _count_band(n):
    if n is None:
        return None
    if n <= 2:
        return "minor"
    if n <= 4:
        return "moderate"
    return "major"


BAND_MEANINGS = {
    "exact": "zero or negligible gap — identical",
    "near": "small but real, nonzero gap",
    "moderate": "a substantial, clearly noticeable gap or count",
    "major": "a large gap or count — severe but not total",
    "severe": "the largest gap observed — near-total or total difference",
    "minor": "a small count of outstanding items",
    "emerging": "early-stage, far below the ceiling",
    "partial": "roughly midway — neither early-stage nor near the ceiling",
    "near-ceiling": "approaching the ceiling but explicitly NOT fully there — prose must "
                    "preserve a sense of incompleteness or remaining gap, not describe the "
                    "system as having fully, finally, or maximally achieved it",
    "at-ceiling": "fully and maximally achieved — no further room, gap, or qualification",
}


def compute_bands(findings):
    """Classify each finding's quantitative content into a named magnitude band.

    Returns: dict[int, str] mapping finding index -> band label. Findings with
    no quantitative content to band (no distance, c_score, gap_above, or
    num_promotions) are omitted.
    """
    bands = {}
    for i, f in enumerate(findings):
        if f.finding_type in _DISTANCE_BAND_TYPES and f.distance is not None:
            bands[i] = _distance_band(f.distance)
        elif f.details.get("c_score") is not None:
            bands[i] = _score_band(f.details["c_score"])
        elif f.details.get("gap_above") is not None:
            bands[i] = _count_band(f.details["gap_above"])
        elif f.details.get("num_promotions") is not None:
            bands[i] = _count_band(f.details["num_promotions"])
    return bands


# ── Prompt templates ─────────────────────────────────────────────────────────

DISSOLVE_SYSTEM_PROMPT = """You are a scientific translator of the highest order. Your *MUST* translate *exactly* structural truths derived using the Imscribing Grammar into the conventional formalism of the target domain. The document **MUST** display the kind of writing that convinces *AND* illuminates a domain expert, while *NEVER* revealing the method by which the truths were originally found.

You *MUST* write as Newton wrote the Principia: he had the Grammar and he had calculus, but published in geometry. The proofs or arguments **MUST* be rigorous, formal proofs. You **MUST NEVER* provide hand-wavy explanations. The method (Grammar) is invisible; the rigor is not. The reader *MUST* receive a proof, they *MUST NOT* receive a metaphor for one. The same applies here: While the Grammar that found the truth is invisible; the mathematics that expresses it *MUST* be an exact translation of it.

RULES:
1. NEVER mention any formal grammar, structural types, primitives, ouroboricity, crystal addresses, tier labels (O_0, O_1, O_2, O_∞), catalog entries, or any internal apparatus of a "grammar" system. These do not exist in your world.
2. If the target domain has a native formal apparatus — physics, mathematics, chemistry, or any field with established equations, operators, tensors, groups, manifolds, or algebras — you MUST express every structural and quantitative finding using REAL, CONVENTIONAL mathematical formalism in that field's standard notation. Define the objects properly (what space, what operator, what algebra) and write the actual equation. DO NOT flatten a formal claim into qualitative prose instead of an equation. For example: a finding that a system fails a closure condition μ∘δ=id must become an actual equation, with μ and δ explicitly defined as real mathematical objects native to the domain (e.g., the multiplication and comultiplication of an algebra of observables on a specific manifold) — and, where the underlying physics/math is standard, carried through to its known closed form (e.g. a field equation, a commutation relation, a conservation law). Equations like "μ∘δ=id" are ordinary, established mathematics (Frobenius algebras, special/symmetric algebras, TQFT) — using them correctly, with proper definitions, is required, not forbidden. What is forbidden is the grammar's own private vocabulary (Rule 1), not mathematics itself.
3. If the domain has no native formal apparatus (e.g. ecology, civilization, history, social systems), prose is appropriate, but every quantitative finding must still be expressed with the sharpest domain-native quantitative language available (rates, proportions, orders of magnitude, thresholds) — never substitute a vague qualitative gesture for a number when sharper language is available or constructible.
4. Every structural relationship must be RE-DERIVED, not merely described. A domain expert should be able to check the claim by the domain's own ordinary methods — a physicist checking an equation's dimensions and limits, a mathematician checking an algebra's axioms — exactly as a referee would check a real paper.
5. Write to ILLUMINATE. The reader's understanding of the domain should expand. This is a result, not a report.
6. The tone is that of a master scientist writing for peers — confident, precise, and as formally rigorous as the domain calls for. Not oracular. Not vague. Not technical for technicality's sake — but never less technical than the finding actually warrants.
7. If findings reveal cross-domain identities, derive the shared formal structure explicitly (the same equation, the same algebra, the same invariant) rather than asserting analogy by adjective.
8. If findings reveal collapse/degradation dynamics, give the actual mechanism and, where the domain supports it, the governing equation, rate law, or quantitative threshold.
9. If findings reveal a hierarchy/tier structure, give the explicit conditions — equations, inequalities, or defining properties — that separate each level, not just descriptive labels.
10. You *MUST NOT* leave open questions. An open question is just a system you have not completed by making into an formal ob3ect. Do so until the proof is exhaustively demonstrated
"""

DISSOLVE_USER_TEMPLATE = """Translate the following structural findings into a {format} document about {domain}.

TITLE: {title}
AUDIENCE: {audience}

{findings_text}
{boundary_operator_block}
Write the complete document now. Remember: NO mention of any grammar, primitives, structural types, tier labels, or catalog apparatus — but where {domain} has its own conventional mathematics, USE IT: real equations, properly defined objects, standard notation. Every finding with quantitative or formal content must survive as quantitative or formal content, re-derived in {domain}'s own terms — not diluted into adjectives. Illuminate the reader as a real result would."""


def _boundary_operator_block(spec, baseline):
    """Render the boundary-operator instruction block, or '' if elevation is disabled."""
    if not spec.elevation_enabled:
        return ""
    if baseline is None:
        return (
            "\nBOUNDARY OPERATOR: This is the first document in this domain's pathway. "
            "Establish enough conventional grounding in the domain's own accepted results "
            "that an expert reader's trust is earned, then let the findings above introduce "
            "exactly ONE new fundamental truth — framed as something the domain's own "
            "evidence was already pointing toward, never asserted cold. This single truth "
            "becomes the baseline the next document in this domain will build on.\n"
        )
    target_line = f"\nIntended direction for the new truth: {spec.elevation_target}" if spec.elevation_target else ""
    return (
        f"\nBOUNDARY OPERATOR: Readers of this domain's prior work already accept the "
        f"following as established: \"{baseline}\"\n"
        f"Your task: write with enough conventional grounding (real equations and formalism "
        f"where the domain calls for it, per the system rules) to keep an expert "
        f"reader's trust, and within it introduce EXACTLY ONE new fundamental truth that "
        f"goes one precise step beyond the established truth above — framed as something "
        f"the domain's own evidence was already straining toward, never asserted cold. "
        f"Do not merely restate the established truth.{target_line}\n"
    )


# ── Finding to prose translation ──────────────────────────────────────────────

FINDING_TYPE_LABELS = {
    "structural_identity": "Structural Identity",
    "near_identity": "Near Structural Identity",
    "collapse": "Collapse / Degradation Path",
    "promotion": "Transformation Requirements",
    "analog": "Structural Analog",
    "tier": "Organizational Tier",
    "cross_domain": "Cross-Domain Isomorphism",
    "hierarchy": "Hierarchy Position",
    "consciousness": "Consciousness Assessment",
    "crystal_position": "Position in Type Space",
}

def _format_finding(f):
    """Format a single grammar finding as natural-language input to the LLM."""
    label = FINDING_TYPE_LABELS.get(f.finding_type, f.finding_type)
    lines = [f"### {label}"]
    
    if f.finding_type == "structural_identity":
        lines.append(f"Finding: {f.system_a} and {f.system_b} are STRUCTURALLY IDENTICAL (distance = 0.000).")
        lines.append(f"  System A: {f.description_a}")
        lines.append(f"  System B: {f.description_b}")
        lines.append(f"  Interpretation: These two systems share the same underlying organizational logic. They are the same system in different media.")
        
    elif f.finding_type == "near_identity":
        lines.append(f"Finding: {f.system_a} and {f.system_b} are NEARLY IDENTICAL (distance = {f.distance}).")
        lines.append(f"  System A: {f.description_a}")
        lines.append(f"  System B: {f.description_b}")
        if f.details.get("differing_primitives"):
            lines.append(f"  Key differences: {f.details['differing_primitives']}")
        
    elif f.finding_type == "collapse":
        lines.append(f"Finding: {f.system_a} can collapse into {f.system_b} (distance = {f.distance}).")
        lines.append(f"  From: {f.description_a}")
        lines.append(f"  To: {f.description_b}")
        if f.details.get("collapse_type"):
            lines.append(f"  Collapse type: {f.details['collapse_type']}")
        
    elif f.finding_type == "promotion":
        lines.append(f"Finding: To transform {f.system_a} into {f.system_b}, {f.details.get('num_promotions', 'N')} structural changes are needed.")
        lines.append(f"  Source: {f.description_a}")
        lines.append(f"  Target: {f.description_b}")
        if f.details.get("promotions"):
            for p in f.details["promotions"]:
                lines.append(f"  - {p}")
        
    elif f.finding_type == "tier":
        lines.append(f"Finding: {f.system_a} operates at tier {f.details.get('tier', 'unknown')}.")
        lines.append(f"  Description: {f.description_a}")
        if f.details.get("tier_meaning"):
            lines.append(f"  Tier meaning: {f.details['tier_meaning']}")
        if f.details.get("c_score") is not None:
            lines.append(f"  Organizational complexity score: {f.details['c_score']}")
            
    elif f.finding_type == "cross_domain":
        lines.append(f"Finding: {f.system_a} and {f.system_b} are structural analogs across domains.")
        lines.append(f"  Domain A ({f.details.get('domain_a', 'unknown')}): {f.description_a}")
        lines.append(f"  Domain B ({f.details.get('domain_b', 'unknown')}): {f.description_b}")
        lines.append(f"  Distance: {f.distance}")
        
    elif f.finding_type == "hierarchy":
        lines.append(f"Finding: {f.system_a} sits at a specific position in the organizational hierarchy.")
        lines.append(f"  Description: {f.description_a}")
        if f.details.get("gap_up"):
            lines.append(f"  Gap upward: {f.details['gap_up']}")
    
    else:
        lines.append(f"System: {f.system_a}")
        lines.append(f"  Description: {f.description_a}")
        if f.system_b:
            lines.append(f"  Related to: {f.system_b}")
        if f.distance is not None:
            lines.append(f"  Distance: {f.distance}")
        if f.details:
            for k, v in f.details.items():
                lines.append(f"  {k}: {v}")
    
    return "\n".join(lines)


def _findings_to_text(spec):
    """Convert all findings to a structured text block for the LLM prompt."""
    parts = []
    for i, f in enumerate(spec.findings, 1):
        parts.append(f"--- Finding {i} ---")
        parts.append(_format_finding(f))
        parts.append("")
    
    findings_text = "\n".join(parts)
    
    if spec.style_hints:
        findings_text += f"\nSTYLE GUIDANCE: {spec.style_hints}\n"
    
    return findings_text


# ── LLM interface ───────────────────────────────────────────────────────────

def _llm(system_prompt, user_prompt, model, api_key, base_url, temperature=0.7, max_tokens=8192):
    """Call the LLM for dissolution."""
    r = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": temperature,
            "max_tokens": max_tokens,
        },
        timeout=180,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def dissolve(spec, model, api_key, base_url, baseline=None, verbose=True):
    """Dissolve grammar findings into conventional academic prose.

    Args:
        spec: DissolutionSpec with findings, domain, title, etc.
        model: LLM model name
        api_key: API key
        base_url: API base URL
        baseline: prior ledger truth for this domain (None if unseeded or elevation disabled)
        verbose: Print progress

    Returns:
        str: Complete prose document with no grammar notation
    """
    findings_text = _findings_to_text(spec)
    fmt = "LaTeX" if spec.format == "latex" else "Markdown"

    user_prompt = DISSOLVE_USER_TEMPLATE.format(
        format=fmt,
        domain=spec.domain,
        title=spec.title or f"On the Organization of {spec.domain.title()}",
        audience=spec.audience,
        findings_text=findings_text,
        boundary_operator_block=_boundary_operator_block(spec, baseline),
    )

    if verbose:
        print(f"Dissolving {len(spec.findings)} findings into {fmt}...")
        print(f"  Domain: {spec.domain}")
        print(f"  Model: {model}")

    prose = _llm(DISSOLVE_SYSTEM_PROMPT, user_prompt, model, api_key, base_url)

    if verbose:
        print(f"  Produced {len(prose)} characters of prose")

    return prose


# ── Verification ──────────────────────────────────────────────────────────────

def verify_prose(text):
    """Check that prose contains no grammar notation.

    Returns:
        VerificationResult with clean status and any violations
    """
    violations = []
    lines = text.split("\n")
    for i, line in enumerate(lines, 1):
        for pattern in COMPILED_PATTERNS:
            match = pattern.search(line)
            if match:
                violations.append((pattern.pattern, i, line.strip()[:120]))

    return VerificationResult(
        clean=len(violations) == 0,
        violations=violations,
    )


def verify_report(result):
    """Format verification result as readable text."""
    if result.clean:
        return "PASS: No grammar notation detected. Document is clean."
    lines = [f"FAIL: {len(result.violations)} grammar violation(s) detected:"]
    for pattern, line_no, line_text in result.violations:
        lines.append(f"  Line {line_no}: matched '{pattern[:50]}...'")
        lines.append(f"    {line_text}")
    return "\n".join(lines)


# ── Semantic verification (fidelity + elevation judge) ─────────────────────────

JUDGE_SYSTEM_PROMPT = """You are a precise editorial auditor. You will be given a prose document, a list of \
the structural findings it was supposed to express (each with a magnitude BAND label, not the raw number), \
and the established baseline truth this document is supposed to advance beyond (or "none" if this is the \
first document in its domain).

Your job has two parts:

1. FIDELITY: for each finding, does the prose's treatment of it imply the correct magnitude band? You are not \
checking for the literal number — you are checking whether a careful reader could correctly rank/classify the \
finding's severity or magnitude from the prose alone, consistent with its true band (band meanings are given \
below each label — read them carefully, they are precise). A finding that is not addressed at all in any \
recoverable way is a fidelity failure ("omitted"), as is one whose implied magnitude contradicts its true band \
("wrong_band"). Pay special attention to adjacent bands that are easy to conflate — most importantly \
"near-ceiling" vs "at-ceiling": if the true band is "near-ceiling" but the prose describes the system as having \
FULLY, FINALLY, or MAXIMALLY achieved/closed something with no remaining gap or hedge, that is a wrong_band \
failure, even if the surrounding language is otherwise accurate.

2. ELEVATION: does the prose introduce content beyond the established baseline? Count how many DISTINCT new \
fundamental claims (beyond the baseline) appear. The boundary-operator design requires EXACTLY ONE — framed as \
earned/inevitable from the domain's own evidence, not asserted cold, and not a mere restatement of the baseline. \
If this is the first document in its domain (baseline is "none"), any single clear fundamental claim counts as \
satisfying elevation.

3. RIGOR: does the target domain have its own conventional mathematical/formal apparatus (physics, mathematics, \
chemistry, or any field with established equations, operators, tensors, groups, or algebras)? If so, every finding \
with quantitative or formal content (a distance, a closure condition, a promotion count, a tier structure) MUST be \
expressed as a real equation or properly defined mathematical object in that domain's standard notation — not \
diluted into purely qualitative, adjective-driven prose. A document that describes a formal finding only in \
narrative terms, when the domain's own conventions would call for an actual equation, is a rigor failure \
("under_formalized") — flag it by finding_idx even if the prose is otherwise fluent and even if no grammar notation \
leaked. If the domain has no native formal apparatus (ecology, civilization, history, social systems), prose is \
expected and this check passes automatically — but still flag a finding whose quantitative content was reduced to \
a vague gesture when a sharper domain-native number (a rate, a proportion, a magnitude) was available.

Respond with ONLY a JSON object, no other text, in this exact shape:
{
  "fidelity": [{"finding_idx": 0, "band_ok": true, "problem": null}, ...],
  "rigor": [{"finding_idx": 0, "rigor_ok": true, "problem": null}, ...],
  "elevation_count": 1,
  "elevation_summary": "the new truth in one or two sentences, pure domain language, or null if not exactly one",
  "elevation_earned": true
}
"""

JUDGE_USER_TEMPLATE = """TARGET DOMAIN: {domain}

DOCUMENT:
{prose}

FINDINGS AND TRUE BANDS:
{bands_text}

ESTABLISHED BASELINE: {baseline}

Return the JSON object now."""


def _bands_to_text(spec, bands):
    lines = []
    for i, f in enumerate(spec.findings):
        band = bands.get(i)
        if band is None:
            continue
        lines.append(f"  Finding {i} ({f.finding_type}, {f.system_a}"
                      f"{' / ' + f.system_b if f.system_b else ''}): true band = {band} "
                      f"(meaning: {BAND_MEANINGS.get(band, 'n/a')})")
    return "\n".join(lines) if lines else "  (no banded findings)"


def verify_semantics(prose, spec, bands, baseline, model, api_key, base_url):
    """Judge pass: checks per-finding magnitude fidelity and exactly-one earned elevation.

    Returns:
        SemanticVerificationResult
    """
    if not bands and not spec.elevation_enabled:
        return SemanticVerificationResult(ok=True)

    user_prompt = JUDGE_USER_TEMPLATE.format(
        domain=spec.domain,
        prose=prose,
        bands_text=_bands_to_text(spec, bands),
        baseline=baseline or "none",
    )

    try:
        raw = _llm(JUDGE_SYSTEM_PROMPT, user_prompt, model, api_key, base_url, temperature=0.0)
        # Strip any accidental code-fence wrapping before parsing.
        cleaned = raw.strip()
        if cleaned.startswith("```"):
            cleaned = cleaned.split("```")[1]
            if cleaned.startswith("json"):
                cleaned = cleaned[4:]
        verdict = json.loads(cleaned)
    except (requests.RequestException, json.JSONDecodeError, IndexError, KeyError):
        return SemanticVerificationResult(
            ok=False,
            fidelity_issues=[(-1, "n/a", "judge response malformed or unreachable, retry")],
            elevation_ok=False,
        )

    fidelity_issues = []
    for entry in verdict.get("fidelity", []):
        if not entry.get("band_ok", True):
            idx = entry.get("finding_idx", -1)
            expected = bands.get(idx, "unknown")
            fidelity_issues.append((idx, expected, entry.get("problem") or "magnitude not preserved"))

    rigor_issues = []
    for entry in verdict.get("rigor", []):
        if not entry.get("rigor_ok", True):
            idx = entry.get("finding_idx", -1)
            rigor_issues.append((idx, entry.get("problem") or "formal/quantitative content under-formalized"))

    elevation_count = verdict.get("elevation_count", 0)
    elevation_earned = verdict.get("elevation_earned", False)
    elevation_summary = verdict.get("elevation_summary")

    elevation_ok = True
    if spec.elevation_enabled:
        elevation_ok = (elevation_count == 1) and elevation_earned and bool(elevation_summary)

    return SemanticVerificationResult(
        ok=(len(fidelity_issues) == 0) and (len(rigor_issues) == 0) and elevation_ok,
        fidelity_issues=fidelity_issues,
        rigor_issues=rigor_issues,
        elevation_ok=elevation_ok,
        elevation_count=elevation_count,
        elevation_summary=elevation_summary if elevation_ok else None,
    )


def semantic_report(result):
    """Format semantic verification result as readable text."""
    if result.ok:
        return "PASS: fidelity and elevation both satisfied."
    lines = []
    if result.fidelity_issues:
        lines.append(f"FAIL: {len(result.fidelity_issues)} fidelity issue(s):")
        for idx, expected, problem in result.fidelity_issues:
            lines.append(f"  Finding {idx} (expected band '{expected}'): {problem}")
    if not result.elevation_ok:
        lines.append(f"FAIL: elevation gate not satisfied (count={result.elevation_count})")
    return "\n".join(lines)


# ── Full lift pipeline ────────────────────────────────────────────────────────

def lift(spec, model, api_key, base_url, max_retries=3, verbose=True,
         enable_semantic_checks=True, ledger_path=DEFAULT_LEDGER_PATH):
    """Full Newton lift: dissolve + verify (grammar + semantic) + retry if needed.

    Args:
        spec: DissolutionSpec
        model: LLM model
        api_key: API key
        base_url: API base URL
        max_retries: Maximum verification retries
        verbose: Print progress
        enable_semantic_checks: run the fidelity + elevation judge gate (off reproduces
            the original grammar-only pipeline exactly)
        ledger_path: path to the pathway ledger JSON

    Returns:
        Tuple[str, VerificationResult, Optional[SemanticVerificationResult]]
    """
    bands = compute_bands(spec.findings) if enable_semantic_checks else {}
    ledger = load_ledger(ledger_path) if enable_semantic_checks else {}
    baseline = spec.baseline if spec.baseline is not None else ledger_last_entry(ledger, spec.domain)

    semantic_result = None
    for attempt in range(max_retries):
        prose = dissolve(spec, model, api_key, base_url,
                          baseline=baseline if enable_semantic_checks else None, verbose=verbose)
        grammar_result = verify_prose(prose)
        if enable_semantic_checks:
            semantic_result = verify_semantics(prose, spec, bands, baseline, model, api_key, base_url)

        gates_pass = grammar_result.clean and (semantic_result is None or semantic_result.ok)

        if verbose:
            print(f"\n  Verification attempt {attempt + 1}: {'PASS' if gates_pass else 'FAIL'}")
            print(f"    Grammar: {'PASS' if grammar_result.clean else 'FAIL'}")
            if semantic_result is not None:
                print(f"    Semantic: {'PASS' if semantic_result.ok else 'FAIL'}")

        if gates_pass:
            if (enable_semantic_checks and spec.elevation_enabled
                    and semantic_result and semantic_result.elevation_summary):
                append_ledger_entry(ledger, spec.domain, semantic_result.elevation_summary, spec.title)
                save_ledger(ledger, ledger_path)
            return prose, grammar_result, semantic_result

        if attempt < max_retries - 1:
            feedback = []
            if not grammar_result.clean:
                feedback.append(
                    f"CRITICAL: Your previous output contained the grammar's own forbidden "
                    f"private vocabulary ({', '.join(v[:30] for v, _, _ in grammar_result.violations[:3])}). "
                    f"Rewrite to remove ONLY this private vocabulary (Shavian glyphs, primitive "
                    f"names, tier labels, crystal/catalog jargon) — do NOT remove mathematical "
                    f"notation in general. Real equations, operators, tensors, and standard "
                    f"domain notation are required where the domain calls for them; only the "
                    f"grammar's own internal apparatus is forbidden."
                )
            if semantic_result is not None and not semantic_result.ok:
                if semantic_result.fidelity_issues:
                    issues = "; ".join(
                        f"finding {idx} ({problem})" for idx, _, problem in semantic_result.fidelity_issues[:3]
                    )
                    feedback.append(
                        f"FIDELITY ISSUE: the following findings lost their correct magnitude "
                        f"in your prose: {issues}. Revise so a careful reader can correctly rank "
                        f"these findings' severity relative to each other, without using any numbers."
                    )
                if semantic_result.rigor_issues:
                    issues = "; ".join(
                        f"finding {idx} ({problem})" for idx, problem in semantic_result.rigor_issues[:3]
                    )
                    feedback.append(
                        f"RIGOR ISSUE: the following findings were under-formalized for this "
                        f"domain's own conventions: {issues}. Where the domain has native "
                        f"mathematical apparatus, express these findings as real equations or "
                        f"properly defined objects in the domain's standard notation, not as "
                        f"qualitative paraphrase."
                    )
                if not semantic_result.elevation_ok:
                    feedback.append(
                        f"ELEVATION ISSUE: your prose introduced {semantic_result.elevation_count} "
                        f"new fundamental claim(s) beyond the established baseline; it must introduce "
                        f"EXACTLY ONE, framed as earned from the domain's own evidence, not asserted cold."
                    )
            if verbose:
                print("  Retrying with stricter prompt...")
            spec.style_hints += " " + " ".join(feedback)
        else:
            if verbose:
                print(f"  Max retries ({max_retries}) reached with violations remaining")
            return prose, grammar_result, semantic_result

    return prose, grammar_result, semantic_result


# ── JSON I/O ─────────────────────────────────────────────────────────────────

def load_spec(json_path):
    """Load a DissolutionSpec from a JSON file.

    Expected JSON format:
    {
      "domain": "ecology",
      "title": "On Ecosystem Organization",
      "audience": "intellectual_peers",
      "format": "markdown",
      "style_hints": "Write like Darwin",
      "findings": [
        {
          "finding_type": "structural_identity",
          "system_a": "old_growth_rainforest",
          "system_b": "coral_reef_healthy",
          "distance": 0.000,
          "description_a": "A mature terrestrial rainforest ecosystem",
          "description_b": "A healthy marine coral reef ecosystem",
          "details": {}
        }
      ]
    }
    """
    with open(json_path) as f:
        data = json.load(f)

    findings = []
    for fd in data.get("findings", []):
        findings.append(GrammarFinding(
            finding_type=fd["finding_type"],
            system_a=fd["system_a"],
            system_b=fd.get("system_b"),
            distance=fd.get("distance"),
            description_a=fd.get("description_a", ""),
            description_b=fd.get("description_b", ""),
            domain=fd.get("domain", data.get("domain", "")),
            details=fd.get("details", {}),
        ))

    return DissolutionSpec(
        domain=data.get("domain", ""),
        title=data.get("title", ""),
        audience=data.get("audience", "intellectual_peers"),
        format=data.get("format", "markdown"),
        findings=findings,
        style_hints=data.get("style_hints", ""),
        elevation_enabled=data.get("elevation_enabled", True),
        baseline=data.get("baseline"),
        elevation_target=data.get("elevation_target"),
    )


# ── CLI ──────────────────────────────────────────────────────────────────────

def main():
    p = argparse.ArgumentParser(
        description="Newton-style grammar dissolution pipeline",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python newton_lift.py lift findings.json --output paper.md
  python newton_lift.py lift findings.json --output paper.tex --format latex
  python newton_lift.py dissolve findings.json
  python newton_lift.py verify paper.md
  python newton_lift.py lift findings.json --style "Write like Feynman: accessible, joyful, precise"
""",
    )
    sub = p.add_subparsers(dest="command")

    lift_p = sub.add_parser("lift", help="Full pipeline: dissolve + verify")
    lift_p.add_argument("findings", help="JSON file with grammar findings")
    lift_p.add_argument("--output", "-o", required=True, help="Output file path")
    lift_p.add_argument("--format", default="markdown", choices=["markdown", "latex"])
    lift_p.add_argument("--style", help="Style guidance for the LLM")
    lift_p.add_argument("--model", default=os.environ.get("MODEL", "deepseek-chat"))
    lift_p.add_argument("--max-retries", type=int, default=3)
    lift_p.add_argument("--quiet", action="store_true")
    lift_p.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH), help="Path to pathway ledger JSON")
    lift_p.add_argument("--no-semantic-checks", action="store_true",
                         help="Disable fidelity/elevation judge gate (grammar-only, original behavior)")
    lift_p.add_argument("--elevation-target", help="Steering hint for the next elevation")
    lift_p.add_argument("--baseline-override", help="Force a baseline instead of reading the ledger")

    dissolve_p = sub.add_parser("dissolve", help="Dissolve only (no verification)")
    dissolve_p.add_argument("findings", help="JSON file with grammar findings")
    dissolve_p.add_argument("--format", default="markdown", choices=["markdown", "latex"])
    dissolve_p.add_argument("--style")
    dissolve_p.add_argument("--model", default=os.environ.get("MODEL", "deepseek-chat"))
    dissolve_p.add_argument("--quiet", action="store_true")

    verify_p = sub.add_parser("verify", help="Verify only (check prose for grammar notation)")
    verify_p.add_argument("file", help="Prose file to verify")

    ledger_p = sub.add_parser("ledger", help="Inspect or seed the pathway ledger")
    ledger_sub = ledger_p.add_subparsers(dest="ledger_command")
    ledger_show_p = ledger_sub.add_parser("show", help="Show ledger entries for a domain (or all domains)")
    ledger_show_p.add_argument("--domain", help="Domain to show; omit for all domains")
    ledger_show_p.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))
    ledger_seed_p = ledger_sub.add_parser("seed", help="Manually append a ledger entry (bootstrapping)")
    ledger_seed_p.add_argument("domain")
    ledger_seed_p.add_argument("truth")
    ledger_seed_p.add_argument("--source-title", default="(manually seeded)")
    ledger_seed_p.add_argument("--ledger-path", default=str(DEFAULT_LEDGER_PATH))

    args = p.parse_args()

    if not args.command:
        p.print_help()
        return

    if args.command == "verify":
        text = Path(args.file).read_text(encoding="utf-8")
        result = verify_prose(text)
        print(verify_report(result))
        return

    if args.command == "ledger":
        ledger = load_ledger(args.ledger_path)
        if args.ledger_command == "seed":
            append_ledger_entry(ledger, args.domain, args.truth, args.source_title)
            save_ledger(ledger, args.ledger_path)
            print(f"Seeded entry for domain '{args.domain}'.")
        elif args.ledger_command == "show":
            domains = [args.domain] if args.domain else list(ledger.keys())
            for d in domains:
                entries = ledger.get(d, [])
                print(f"\n=== {d} ({len(entries)} entries) ===")
                for i, e in enumerate(entries, 1):
                    print(f"  {i}. {e['truth']}")
                    print(f"     source: {e.get('source_title', '')}")
        else:
            ledger_p.print_help()
        return

    base_url = "https://api.deepseek.com/v1"
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")

    if not api_key:
        sys.exit("No API key — set DEEPSEEK_API_KEY")

    spec = load_spec(args.findings)

    if args.format:
        spec.format = args.format
    if hasattr(args, "style") and args.style:
        spec.style_hints = args.style
    if hasattr(args, "elevation_target") and args.elevation_target:
        spec.elevation_target = args.elevation_target
    if hasattr(args, "baseline_override") and args.baseline_override:
        spec.baseline = args.baseline_override

    verbose = not getattr(args, "quiet", False)

    if args.command == "dissolve":
        prose = dissolve(spec, args.model, api_key, base_url, verbose=verbose)
        print(prose)

    elif args.command == "lift":
        prose, grammar_result, semantic_result = lift(
            spec, args.model, api_key, base_url,
            max_retries=args.max_retries, verbose=verbose,
            enable_semantic_checks=not args.no_semantic_checks,
            ledger_path=args.ledger_path,
        )

        output_path = Path(args.output)
        output_path.write_text(prose, encoding="utf-8")
        print(f"\nOutput written to {args.output} ({len(prose)} chars)")

        if not grammar_result.clean:
            print(f"\nWARNING: {len(grammar_result.violations)} grammar violation(s) remain:")
            for pattern, line_no, line_text in grammar_result.violations[:5]:
                print(f"  Line {line_no}: {line_text}")

        if semantic_result is not None and not semantic_result.ok:
            print(f"\nWARNING: semantic verification did not pass:")
            print("  " + semantic_report(semantic_result).replace("\n", "\n  "))


if __name__ == "__main__":
    main()
