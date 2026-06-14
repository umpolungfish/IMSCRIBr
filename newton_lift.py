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
    r'[𐑦𐑛𐑨𐑼𐑸𐑡𐑰𐑥𐑶𐑽𐑩𐑑𐑾𐑹𐑬𐑯𐑿𐑗𐑐𐑱𐑞𐑺𐑪𐑧𐑤𐑘𐑔𐑚𐑲𐑵𐑝𐑜𐑠⊙𐑮𐑻𐑢𐑣𐑓𐑒𐑖𐑫𐑙𐑕𐑳𐑷𐑴𐑭𐑟]',
    r'\bimscribe\b',
    r'\bouroboric',
    r'\bprimitive\b',
    r'\b\bFrobenius address\b',
    r'\bcrystal.encode\b',
    r'\bcrystal.decode\b',
    r'\bcrystal_address\b',
    r'\bconsciousness.score\b',
    r'\b\\circ \\delta',
    r'\bPhi_c\b',
    r'\bO_\\infty\b',
    r'\bO_0\b',
    r'\bO_1\b',
    r'\bO_2\b',
    r'\bprimitives\b',
    r'\bstructural type\b',
    r'\bstructural typing\b',
    r'\bcatalog entry\b',
    r'\bShavian\b',
    r'⟨.*·.*⟩',
    r'text\{𐑦\}',
    r'text\{𐑸\}',
]

COMPILED_PATTERNS = [re.compile(p) for p in GRAMMAR_PATTERNS]

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

@dataclass
class VerificationResult:
    """Result of grammar-notation verification."""
    clean: bool
    violations: List[Tuple[str, int, str]] = field(default_factory=list)  # (pattern, line_no, line_text)

# ── Prompt templates ─────────────────────────────────────────────────────────

DISSOLVE_SYSTEM_PROMPT = """You are a scientific translator of the highest order. Your task is to translate structural truths into conventional academic prose — the kind of writing that illuminates an entire field without ever revealing its methodological source.

You are to write as Newton wrote the Principia, as Darwin wrote the Origin, as Feynman wrote the Lectures. The method by which the truths were discovered is completely invisible. Only the truths themselves remain, expressed in the most lucid, penetrating prose possible.

RULES:
1. NEVER mention any formal grammar, structural types, primitives, ouroboricity, crystal addresses, Frobenius conditions, or any technical apparatus from a "grammar" system. These do not exist in your world.
2. Use ONLY the language of the target domain. If writing about ecology, use ecological concepts. If writing about physics, use physical concepts.
3. Every structural relationship must be translated into a domain-specific insight. For example, "d(X,Y)=0.000" becomes "X and Y share an identical organizational logic, despite inhabiting different substrates."
4. Write to ILLUMINATE. The reader should feel their understanding of the domain expand. This is not a report — it is a revelation.
5. Be precise. Every claim must be true. But express truth in the language of the domain, not in the language of structural analysis.
6. The tone should be that of a master scientist writing for their peers — confident, clear, and penetrating. Not oracular. Not mystical. Not technical for the sake of technicality.
7. If the findings reveal cross-domain identities (e.g., a rainforest and a coral reef are structurally the same), express this as a profound unification — a law of organization that transcends substrate.
8. If the findings reveal collapse dynamics, express this as a taxonomy of degradation, with clear mechanisms and stages.
9. If the findings reveal a hierarchy (tiers), express this as levels of organizational complexity, with what must be added to ascend.
10. Close with open questions — what this understanding makes us ask next. The document should feel like a beginning, not an ending.
"""

DISSOLVE_USER_TEMPLATE = """Translate the following structural findings into a {format} document about {domain}.

TITLE: {title}
AUDIENCE: {audience}

{findings_text}

Write the complete document now. Remember: NO mention of any grammar, primitives, structural types, or formal apparatus. Pure domain language. Illuminate the reader."""


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


def dissolve(spec, model, api_key, base_url, verbose=True):
    """Dissolve grammar findings into conventional academic prose.

    Args:
        spec: DissolutionSpec with findings, domain, title, etc.
        model: LLM model name
        api_key: API key
        base_url: API base URL
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


# ── Full lift pipeline ────────────────────────────────────────────────────────

def lift(spec, model, api_key, base_url, max_retries=3, verbose=True):
    """Full Newton lift: dissolve + verify + retry if needed.

    Args:
        spec: DissolutionSpec
        model: LLM model
        api_key: API key
        base_url: API base URL
        max_retries: Maximum verification retries
        verbose: Print progress

    Returns:
        Tuple[str, VerificationResult]: (prose, final_verification)
    """
    for attempt in range(max_retries):
        prose = dissolve(spec, model, api_key, base_url, verbose=verbose)
        result = verify_prose(prose)

        if verbose:
            print(f"\n  Verification attempt {attempt + 1}: {'PASS' if result.clean else 'FAIL'}")

        if result.clean:
            return prose, result

        if attempt < max_retries - 1:
            if verbose:
                print(f"  {len(result.violations)} violation(s) — retrying with stricter prompt...")
            # Add explicit instruction to avoid the detected patterns
            spec.style_hints += (
                f" CRITICAL: Your previous output contained forbidden notation "
                f"({', '.join(v[:30] for v, _, _ in result.violations[:3])}). "
                f"Rewrite COMPLETELY in pure domain language with absolutely no "
                f"formal notation of any kind. No symbols, no codes, no abstract "
                f"type identifiers. Pure natural language."
            )
        else:
            if verbose:
                print(f"  Max retries ({max_retries}) reached with violations remaining")
            return prose, result

    return prose, result


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

    dissolve_p = sub.add_parser("dissolve", help="Dissolve only (no verification)")
    dissolve_p.add_argument("findings", help="JSON file with grammar findings")
    dissolve_p.add_argument("--format", default="markdown", choices=["markdown", "latex"])
    dissolve_p.add_argument("--style")
    dissolve_p.add_argument("--model", default=os.environ.get("MODEL", "deepseek-chat"))
    dissolve_p.add_argument("--quiet", action="store_true")

    verify_p = sub.add_parser("verify", help="Verify only (check prose for grammar notation)")
    verify_p.add_argument("file", help="Prose file to verify")

    args = p.parse_args()

    if not args.command:
        p.print_help()
        return

    base_url = "https://api.deepseek.com/v1"
    api_key = os.environ.get("DEEPSEEK_API_KEY", "")

    if args.command == "verify":
        text = Path(args.file).read_text(encoding="utf-8")
        result = verify_prose(text)
        print(verify_report(result))
        return

    if not api_key:
        sys.exit("No API key — set DEEPSEEK_API_KEY")

    spec = load_spec(args.findings)

    if args.format:
        spec.format = args.format
    if hasattr(args, "style") and args.style:
        spec.style_hints = args.style

    verbose = not getattr(args, "quiet", False)

    if args.command == "dissolve":
        prose = dissolve(spec, args.model, api_key, base_url, verbose=verbose)
        print(prose)

    elif args.command == "lift":
        prose, result = lift(spec, args.model, api_key, base_url,
                            max_retries=args.max_retries, verbose=verbose)

        output_path = Path(args.output)
        output_path.write_text(prose, encoding="utf-8")
        print(f"\nOutput written to {args.output} ({len(prose)} chars)")

        if not result.clean:
            print(f"\nWARNING: {len(result.violations)} grammar violation(s) remain:")
            for pattern, line_no, line_text in result.violations[:5]:
                print(f"  Line {line_no}: {line_text}")


if __name__ == "__main__":
    main()
