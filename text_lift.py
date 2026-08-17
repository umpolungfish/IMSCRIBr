#!/usr/bin/env python3
"""
text_lift.py — IMASM structural lift for text documents.

Two-scale analysis:
  Macro: section token sequence → StructuralFingerprint → canonical class
  Micro: each section assigned one IMASM token describing its structural operation

The two scales are coupled: micro-tokens must collectively instantiate the macro
fingerprint (μ∘δ=id at text level). frobenius_order, dialetheia_complete,
self_ref, period, trans_sig are structural facts about the document, not style.

Lift operation: given current fingerprint, target a canonical class.
Output: structural rewrite instructions — not stylistic prompts.

Usage:
  python text_lift.py doc.md
  python text_lift.py doc.md --target VII_Parakernel
  python text_lift.py doc.md --list-canonicals
  python text_lift.py doc.md --model qwen/qwen-2.5-72b-instruct
"""

import os
import re
import sys
import argparse
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

try:
    import requests
except ImportError:
    sys.exit("requests not installed — run: uv pip install requests")

from tokens import Token, token_name, arrangement_str
from classifier import (
    StructuralFingerprint, compute_fingerprint,
    CANONICAL_CLASSES, CANONICAL_FINGERPRINTS, match_canonical,
)


# ── Token structural semantics ────────────────────────────────────────────────

TOKEN_SEMANTICS = {
    Token.VINIT:   "establishes void / initial conditions; clears the slate before argument begins",
    Token.TANCH:   "anchors a boundary, definition, or fixed point; stakes a claim that doesn't move",
    Token.AFWD:    "traces implications forward; follows consequences of what is already established",
    Token.AREV:    "traces what must hold for this to be true; unpacks preconditions backward",
    Token.CLINK:   "links / composes; bridges this passage to an adjacent structural domain",
    Token.IMSCRIB: "asserts structural identity or equivalence; this IS that",
    Token.FSPLIT:  "decomposes into independent parallel threads; the argument forks",
    Token.FFUSE:   "recombines; finds the invariant multiple threads share; the argument converges",
    Token.EVALT:   "evaluates the truth-face; what is correct, verified, or holds",
    Token.EVALF:   "evaluates the falsity-face; where this fails, breaks, or is wrong",
    Token.ENGAGR:  "holds T and F simultaneously; stabilizes rather than resolves the contradiction",
    Token.IFIX:    "irreversible fixation; burns the bridge; makes a commitment that cannot be undone",
}

_TOKEN_PROMPT_LINES = "\n".join(
    f"  {t.name}: {TOKEN_SEMANTICS[t]}" for t in Token
)

_CLASSIFY_PROMPT = """\
You are assigning a single IMASM structural token to a passage of text.
The token describes the STRUCTURAL OPERATION the passage performs — not its topic, style, or subject matter.

The 12 tokens:
{token_lines}

Return ONLY the token name, exactly as written above (one of: {token_list}).
Nothing else — no explanation, no punctuation.

Passage:
{passage}"""


# ── Data types ────────────────────────────────────────────────────────────────

@dataclass
class Section:
    index: int
    heading: str
    body: str
    token: Optional[Token] = None


@dataclass
class ImscribedDoc:
    path: str
    sections: list
    arrangement: tuple = field(default_factory=tuple)

    def fingerprint(self) -> StructuralFingerprint:
        return compute_fingerprint(self.arrangement or (Token.IFIX.value,))


@dataclass
class LiftInstruction:
    section_index: int
    heading: str
    current_token: Optional[Token]
    target_token: Optional[Token]
    instruction: str


@dataclass
class LiftPlan:
    target_name: str
    current_arrangement: tuple
    target_arrangement: tuple
    current_fp: StructuralFingerprint
    target_fp: StructuralFingerprint
    fp_diffs: list
    section_instructions: list


# ── Document parsing ──────────────────────────────────────────────────────────

def _detex(chunk: str) -> str:
    """Strip the markup so a section reads as the prose it is."""
    chunk = re.sub(r'\\begin\{(tabular|center|thebibliography|tcolorbox)\}.*?\\end\{\1\}',
                   ' ', chunk, flags=re.S)
    chunk = re.sub(r'\\(cite|ref|Cref|label)\{[^}]*\}', ' ', chunk)
    chunk = re.sub(r'\\ig\{([^}]*)\}', r'\1', chunk)
    chunk = re.sub(r'\\(emph|textbf|texttt)\{([^}]*)\}', r'\2', chunk)
    chunk = re.sub(r'\\begin\{[^}]*\}|\\end\{[^}]*\}', ' ', chunk)
    chunk = re.sub(r'\\[a-zA-Z]+\*?', ' ', chunk)
    chunk = re.sub(r'[{}$&]', ' ', chunk)
    return re.sub(r'\s+', ' ', chunk).strip()


def parse_sections(text: str) -> list:
    """
    Split document into sections by ## headers.
    Falls back to paragraph split if no headers found.
    Caps at 8 sections — IMASM arrangement length.
    """
    text = re.sub(r'^---\n.*?\n---\n', '', text, flags=re.DOTALL)

    sections = []

    # A LaTeX manuscript carries its sections in \section and its argument in
    # braces; reading it as Markdown finds no headings at all and falls through
    # to a paragraph split, which imscribes the preamble rather than the paper.
    if '\\begin{document}' in text or re.search(r'^\\section\{', text, re.M):
        body = text.split('\\begin{document}', 1)[-1]
        body = body.split('\\end{document}', 1)[0]
        abstract = re.search(r'\\begin\{abstract\}(.*?)\\end\{abstract\}', body, re.S)
        parts_tex = re.split(r'^\\section\*?\{([^}]*)\}', body, flags=re.M)
        if len(parts_tex) > 1:
            if abstract:
                sections.append(Section(0, "Abstract", _detex(abstract.group(1))))
            i = 1
            while i + 1 < len(parts_tex):
                heading = parts_tex[i].strip()
                sec_body = _detex(parts_tex[i + 1])
                if sec_body:
                    sections.append(Section(len(sections), heading, sec_body))
                i += 2
            if len(sections) > 8:
                merged = "\n\n".join(x.body for x in sections[7:])
                sections = sections[:7] + [Section(7, "…", merged)]
            return sections

    parts = re.split(r'^(#{1,3} .+)$', text, flags=re.MULTILINE)
    if len(parts) > 1:
        if parts[0].strip():
            sections.append(Section(0, "", parts[0].strip()))
        i = 1
        while i + 1 < len(parts):
            heading = parts[i].lstrip('#').strip()
            body = parts[i + 1].strip()
            if body:
                sections.append(Section(len(sections), heading, body))
            i += 2
    else:
        paras = [p.strip() for p in re.split(r'\n{2,}', text) if p.strip()]
        for i, para in enumerate(paras):
            sections.append(Section(i, "", para[:600]))

    if len(sections) > 8:
        merged = "\n\n".join(s.body for s in sections[7:])
        sections = sections[:7] + [Section(7, "…", merged)]

    return sections


# ── LLM ──────────────────────────────────────────────────────────────────────

def _llm_native(prompt: str) -> str:
    """This project's own inference, through the ask binary.

    The lift used to require a key for an outside service, which made a
    structural tool depend on an account. The native lane needs neither.
    """
    import shutil
    import subprocess
    ask = shutil.which("ask") or str(Path.home() / "imsgct" / "MoDoT" / "ask")
    proc = subprocess.run(
        [ask, "--raw", "--ask", prompt],
        capture_output=True, text=True, timeout=600,
    )
    if proc.returncode != 0:
        raise RuntimeError(f"native lane failed: {proc.stderr.strip()[:200]}")
    return proc.stdout.strip()


def _llm(prompt: str, model: str, api_key: str, base_url: str) -> str:
    # The native lane is the default. An outside service is used only when one
    # is named, so the presence of a key in the environment does not silently
    # route a structural tool through an account.
    if not model or model == "native":
        return _llm_native(prompt)
    r = requests.post(
        f"{base_url.rstrip('/')}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
        json={
            "model": model,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.0,
        },
        timeout=60,
    )
    r.raise_for_status()
    return r.json()["choices"][0]["message"]["content"].strip()


def classify_section(sec: Section, model: str, api_key: str, base_url: str) -> Token:
    passage = (f"[{sec.heading}]\n{sec.body[:700]}" if sec.heading else sec.body[:700])
    prompt = _CLASSIFY_PROMPT.format(
        token_lines=_TOKEN_PROMPT_LINES,
        token_list=", ".join(t.name for t in Token),
        passage=passage,
    )
    raw = _llm(prompt, model, api_key, base_url).strip().upper()
    for t in Token:
        if t.name in raw:
            return t
    return Token.CLINK


def classify_sections(sections, model: str, api_key: str, base_url: str,
                       verbose: bool = True):
    """Classify every section in one pass.

    Returns one token per section, in order. A missing or unreadable answer
    falls back to CLINK for that section alone rather than failing the run.
    """
    numbered = []
    for sec in sections:
        head = f"[{sec.heading}] " if sec.heading else ""
        numbered.append(f"{sec.index}. {head}{sec.body[:600]}")
    prompt = (
        "Each numbered passage below is one section of a document, and each performs "
        "exactly one structural operation. Name the operation for every passage.\n\n"
        f"{_TOKEN_PROMPT_LINES}\n\n"
        "Answer with one line per passage, in order, formatted exactly as\n"
        "  <index>: <TOKEN>\n"
        f"using only these names: {', '.join(t.name for t in Token)}.\n\n"
        + "\n\n".join(numbered)
    )
    if verbose:
        print(f"    classifying {len(sections)} sections in one pass...", flush=True)
    raw = _llm(prompt, model, api_key, base_url)

    answers = {}
    for line in raw.splitlines():
        m = re.match(r'\s*(\d+)\s*[:.\)-]\s*([A-Z]+)', line.strip().upper())
        if m:
            idx = int(m.group(1))
            for t in Token:
                if t.name == m.group(2):
                    answers[idx] = t
                    break
    return [answers.get(sec.index, Token.CLINK) for sec in sections]


def imscribe_document(text: str, path: str, model: str, api_key: str, base_url: str,
                       verbose: bool = True) -> ImscribedDoc:
    sections = parse_sections(text)
    if verbose:
        print(f"  {len(sections)} section(s) parsed")

    # One call for the whole document. Classifying section by section meant a
    # separate invocation each time, and on the native lane every invocation
    # loads the model again, so eight sections cost eight cold loads.
    tokens = classify_sections(sections, model, api_key, base_url, verbose=verbose)
    for sec, tok in zip(sections, tokens):
        sec.token = tok
        if verbose:
            label = sec.heading or sec.body[:50].replace('\n', ' ')
            print(f"    [{sec.index}] {sec.token.name:8s}  \"{label}\"")

    arrangement = tuple(s.token.value for s in sections)
    return ImscribedDoc(path=path, sections=sections, arrangement=arrangement)


# ── Fingerprint report ────────────────────────────────────────────────────────

_FROB_DESC = {
    0: "none",
    1: "FSPLIT → FFUSE  (correct order)",
    2: "FFUSE → FSPLIT  (inverted — convergence precedes divergence)",
    3: "multiple pairs",
}


def fingerprint_report(doc: ImscribedDoc) -> str:
    arr = doc.arrangement
    fp  = compute_fingerprint(arr)
    canon = match_canonical(arr)

    lines = []
    lines.append("── IMASM ARC FINGERPRINT ──────────────────────────────────────")
    lines.append(f"  Arrangement:     {arrangement_str(arr)}")
    lines.append(f"  Signature:       L={fp.sig_L}  F={fp.sig_F}  D={fp.sig_D}  X={fp.sig_X}")
    lines.append(f"  Start → End:     {token_name(fp.start_token)} → {token_name(fp.end_token)}")
    lines.append(f"  Self-ref:        {fp.self_ref}  {'(ouroborotic)' if fp.self_ref else ''}")
    lines.append(f"  Frobenius:       {_FROB_DESC[fp.frobenius_order]}")
    lines.append(f"  Dialetheia:      {'complete  (EVALT + EVALF + ENGAGR)' if fp.dialetheia_complete else 'incomplete'}")
    lines.append(f"  Period:          {fp.period}  {'(periodic)' if fp.is_periodic else '(aperiodic)'}")
    lines.append(f"  Token diversity: {fp.token_diversity}/12")
    lines.append(f"  Transitions:     {fp.trans_sig}")
    if canon:
        lines.append(f"  Canonical match: *** {canon} ***")
    else:
        lines.append(f"  Canonical match: none  (novel arc)")
    lines.append("")
    lines.append("── SECTION MAP ────────────────────────────────────────────────")
    for sec in doc.sections:
        label = sec.heading or (sec.body[:55].replace('\n', ' ') + "…")
        lines.append(f"  [{sec.index}] {sec.token.name:8s}  {label}")
    return "\n".join(lines)


# ── Lift ──────────────────────────────────────────────────────────────────────

def _diff_fingerprints(current_fp: StructuralFingerprint,
                        target_fp: StructuralFingerprint,
                        current_arr: tuple) -> list:
    diffs = []

    if current_fp.start_token != target_fp.start_token:
        diffs.append(("start_token",
            token_name(current_fp.start_token),
            token_name(target_fp.start_token),
            f"Rewrite the opening section as {token_name(target_fp.start_token)}: "
            f"{TOKEN_SEMANTICS[Token(target_fp.start_token)]}"))

    if current_fp.end_token != target_fp.end_token:
        diffs.append(("end_token",
            token_name(current_fp.end_token),
            token_name(target_fp.end_token),
            f"Rewrite the closing section as {token_name(target_fp.end_token)}: "
            f"{TOKEN_SEMANTICS[Token(target_fp.end_token)]}"))

    if current_fp.self_ref != target_fp.self_ref:
        if target_fp.self_ref:
            diffs.append(("self_ref", False, True,
                f"Make ouroborotic: opening and closing sections must share the same structural "
                f"token ({token_name(target_fp.start_token)}). The document must loop back to its own opening move."))
        else:
            diffs.append(("self_ref", True, False,
                "Break ouroboricity: opening and closing sections should enact different structural operations."))

    if current_fp.frobenius_order != target_fp.frobenius_order:
        if target_fp.frobenius_order == 1:
            diffs.append(("frobenius_order", _FROB_DESC[current_fp.frobenius_order], "FSPLIT→FFUSE",
                "Add Frobenius structure: introduce an FSPLIT section (argument decomposes into "
                "independent threads) followed later by FFUSE (threads recombine into a single invariant). "
                "This is μ∘δ=id at text level."))
        elif target_fp.frobenius_order == 0:
            diffs.append(("frobenius_order", _FROB_DESC[current_fp.frobenius_order], "none",
                "Remove Frobenius structure: eliminate fork/join. Argument should flow without decomposition."))
        elif target_fp.frobenius_order == 2:
            diffs.append(("frobenius_order", _FROB_DESC[current_fp.frobenius_order], "FFUSE→FSPLIT (inverted)",
                "Invert Frobenius order: FFUSE before FSPLIT. Convergence precedes divergence — "
                "the argument recombines something from before it splits into new threads."))

    if current_fp.dialetheia_complete != target_fp.dialetheia_complete:
        if target_fp.dialetheia_complete:
            have = set()
            if current_arr and Token.EVALT.value in current_arr:  have.add("EVALT")
            if current_arr and Token.EVALF.value in current_arr:  have.add("EVALF")
            if current_arr and Token.ENGAGR.value in current_arr: have.add("ENGAGR")
            missing = [t for t in ("EVALT", "EVALF", "ENGAGR") if t not in have]
            diffs.append(("dialetheia_complete", False, True,
                f"Complete the dialetheic register. Missing: {', '.join(missing)}. "
                "EVALT section = what is correct and holds. "
                "EVALF section = where this fails or is wrong. "
                "ENGAGR section = hold both simultaneously without resolving — stabilize the contradiction."))
        else:
            diffs.append(("dialetheia_complete", True, False,
                "Collapse the dialetheic register: resolve or eliminate one face. "
                "The argument should not hold EVALT and EVALF open simultaneously."))

    if current_fp.period != target_fp.period:
        if target_fp.is_periodic:
            diffs.append(("period", current_fp.period, target_fp.period,
                f"Impose period-{target_fp.period} structure: sections should repeat the same "
                f"structural pattern every {target_fp.period} section(s)."))
        else:
            diffs.append(("period", current_fp.period, "aperiodic",
                "Break periodicity: each section should enact a distinct structural operation."))

    sig_c = current_fp.signature
    sig_t = target_fp.signature
    if sig_c != sig_t:
        dl = sig_t[0] - sig_c[0]
        df = sig_t[1] - sig_c[1]
        dd = sig_t[2] - sig_c[2]
        dx = sig_t[3] - sig_c[3]
        moves = []
        if dl > 0: moves.append(f"add {dl} Logical section(s)  (VINIT/TANCH/AFWD/AREV/CLINK/IMSCRIB)")
        if dl < 0: moves.append(f"remove {-dl} Logical section(s)")
        if df > 0: moves.append(f"add {df} Frobenius section(s)  (FSPLIT/FFUSE)")
        if df < 0: moves.append(f"remove {-df} Frobenius section(s)")
        if dd > 0: moves.append(f"add {dd} Dialetheia section(s)  (EVALT/EVALF/ENGAGR)")
        if dd < 0: moves.append(f"remove {-dd} Dialetheia section(s)")
        if dx > 0: moves.append(f"add {dx} Linear section(s)  (IFIX)")
        if dx < 0: moves.append(f"remove {-dx} Linear section(s)")
        diffs.append(("signature",
            f"L={sig_c[0]} F={sig_c[1]} D={sig_c[2]} X={sig_c[3]}",
            f"L={sig_t[0]} F={sig_t[1]} D={sig_t[2]} X={sig_t[3]}",
            "Rebalance family mix: " + " | ".join(moves)))

    return diffs


def _section_instructions(doc: ImscribedDoc, target_arr: tuple) -> list:
    current_arr = doc.arrangement
    n_c = len(current_arr)
    n_t = len(target_arr)
    instructions = []

    for i in range(max(n_c, n_t)):
        c_tok = Token(current_arr[i]) if i < n_c else None
        t_tok = Token(target_arr[i]) if i < n_t else None
        if c_tok == t_tok:
            continue
        sec = doc.sections[i] if i < len(doc.sections) else None
        label = (sec.heading if sec and sec.heading else
                 (sec.body[:40].replace('\n', ' ') + "…") if sec else f"position {i}")

        if c_tok is None:
            instr = (f"ADD section at position {i}: {t_tok.name}\n"
                     f"    {TOKEN_SEMANTICS[t_tok]}")
        elif t_tok is None:
            instr = (f"REMOVE or MERGE \"{label}\"  (token {c_tok.name} not present in target arc)")
        else:
            instr = (f"REWRITE \"{label}\"\n"
                     f"    {c_tok.name} → {t_tok.name}\n"
                     f"    was:  {TOKEN_SEMANTICS[c_tok]}\n"
                     f"    now:  {TOKEN_SEMANTICS[t_tok]}")

        instructions.append(LiftInstruction(
            section_index=i,
            heading=sec.heading if sec else "",
            current_token=c_tok,
            target_token=t_tok,
            instruction=instr,
        ))

    return instructions


def lift_to(doc: ImscribedDoc, target_name: str) -> LiftPlan:
    if target_name not in CANONICAL_CLASSES:
        avail = ", ".join(CANONICAL_CLASSES)
        raise ValueError(f"Unknown canonical class '{target_name}'. Available: {avail}")

    target_arr = CANONICAL_CLASSES[target_name]
    current_fp  = compute_fingerprint(doc.arrangement)
    target_fp   = CANONICAL_FINGERPRINTS[target_name]

    return LiftPlan(
        target_name=target_name,
        current_arrangement=doc.arrangement,
        target_arrangement=target_arr,
        current_fp=current_fp,
        target_fp=target_fp,
        fp_diffs=_diff_fingerprints(current_fp, target_fp, doc.arrangement),
        section_instructions=_section_instructions(doc, target_arr),
    )


def render_plan(plan: LiftPlan) -> str:
    lines = []
    lines.append("── LIFT PLAN ───────────────────────────────────────────────────")
    lines.append(f"  Current arc:  {arrangement_str(plan.current_arrangement)}")
    lines.append(f"  Target class: {plan.target_name}")
    lines.append(f"  Target arc:   {arrangement_str(plan.target_arrangement)}")

    if not plan.fp_diffs and not plan.section_instructions:
        lines.append("\n  ✓ Document already matches target fingerprint. No changes needed.")
        return "\n".join(lines)

    if plan.fp_diffs:
        lines.append("\n── STRUCTURAL GAPS ─────────────────────────────────────────────")
        for prop, cur, tgt, instr in plan.fp_diffs:
            lines.append(f"\n  {prop}:  {cur}  →  {tgt}")
            for ln in instr.split(". "):
                lines.append(f"    {ln.strip()}.")
            lines[-1] = lines[-1].rstrip(".")  # clean trailing double dot

    if plan.section_instructions:
        lines.append("\n── SECTION REWRITES ────────────────────────────────────────────")
        for instr in plan.section_instructions:
            lines.append("")
            for ln in instr.instruction.split("\n"):
                lines.append(f"  {ln}")

    return "\n".join(lines)


# ── List canonicals ───────────────────────────────────────────────────────────

def list_canonicals() -> str:
    lines = ["── 12 CANONICAL IMASM ARCS ─────────────────────────────────────────"]
    for name, arr in CANONICAL_CLASSES.items():
        fp = CANONICAL_FINGERPRINTS[name]
        lines.append(f"\n  {name}")
        lines.append(f"    {arrangement_str(arr)}")
        lines.append(f"    {fp.description()}")
    return "\n".join(lines)


# ── CLI ───────────────────────────────────────────────────────────────────────

# ── The verdict on the document itself ───────────────────────────────────────
# A document is a word. It divides where it opens something, rejoins where it
# answers it, and does work in between. Whether it closes is the same question
# the closure engine answers for a gene or a compiled function, so it is asked
# here in the same way rather than by comparing the document against a menu of
# preferred shapes. There is no target arc. A paper that closes closes; a paper
# that forks and never comes back is told where.

_TOKEN_MARK = {
    "VINIT": "\u22a2", "TANCH": "\u22a3", "AFWD": "\u227b", "AREV": "\u227a",
    "CLINK": "\u22c8", "EVALT": "\u22a4", "FSPLIT": "\u2208", "FFUSE": "\u220b",
    "IMSCRIB": "\u2299", "EVALF": "\u22a5", "ENGAGR": "\u229e", "IFIX": "\u25fb",
}
_WORK_MARKS = frozenset("\u227b\u227a\u22c8\u22a4\u22a5\u229e\u25fb")


def document_word(doc) -> str:
    """The document as a word in the twelve."""
    return "".join(_TOKEN_MARK[s.token.name] for s in doc.sections if s.token)


def document_verdict(word: str):
    """Does the document close? The engine decides, not a preferred shape."""
    import sys as _sys
    from pathlib import Path as _Path
    vox = _Path.home() / "imsgct" / "Vox"
    if vox.exists() and str(vox) not in _sys.path:
        _sys.path.insert(0, str(vox))
    import vox as _vox
    return _vox.verdict(list(word))


def closure_report(doc) -> str:
    """What the document does, and whether it comes back."""
    word = document_word(doc)
    verdict, why = document_verdict(word)
    forks = word.count("\u2208")
    fuses = word.count("\u220b")
    reading = {
        "T": "closes: it opens something, works on it, and comes back",
        "B": "hangs open: it opens something it never answers",
        "F": "ill-typed: it answers something it never opened",
        "N": "null: it opens and closes without doing work between",
    }
    lines = ["", "\u2500\u2500 THE DOCUMENT AS A WORD " + "\u2500" * 40, ""]
    lines.append(f"  word       {word}")
    lines.append(f"  divisions  {forks}   rejoinings  {fuses}   difference {forks - fuses:+d}")
    lines.append(f"  verdict    {verdict}   {reading.get(verdict, '')}")
    lines.append(f"  {why}")
    lines.append("")
    for sec in doc.sections:
        if sec.token:
            lines.append(f"    {_TOKEN_MARK[sec.token.name]}  {sec.token.name:<8} {sec.heading[:56]}")
    if verdict == "B":
        depth = 0
        for sec in doc.sections:
            if not sec.token:
                continue
            m = _TOKEN_MARK[sec.token.name]
            if m == "\u2208":
                depth += 1
                opened = sec.heading
            elif m == "\u220b" and depth:
                depth -= 1
        if depth:
            lines.append("")
            lines.append(f"  The unanswered division is \"{opened}\". Either answer it later"
                         " in the paper or fold it into the section that raises it.")
    if verdict == "N":
        lines.append("")
        lines.append("  Nothing between the division and the rejoining does work. The paper"
                     " states and restates without transforming what it holds.")
    return "\n".join(lines)


def main():
    p = argparse.ArgumentParser(
        description="IMASM structural lift for text documents.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python text_lift.py paper.md
  python text_lift.py paper.tex
  python text_lift.py paper.md --list-canonicals

The verdict is whether the document closes. There is no target shape: a paper
that opens something and answers it closes, and one that forks and never comes
back is told where it forked.
""",
    )
    p.add_argument("file", nargs="?", help="Document to read: Markdown or LaTeX")
    p.add_argument("--target", help="Compare against one of the twelve arcs (optional; the verdict does not need it)")
    p.add_argument("--list-canonicals", action="store_true")
    p.add_argument("--model",
                   default="native",
                   help="Inference lane; 'native' is this project's own")
    args = p.parse_args()

    if args.list_canonicals:
        print(list_canonicals())
        return

    if not args.file:
        p.print_help()
        return

    text = Path(args.file).read_text(encoding="utf-8")

    base_url = "https://api.deepseek.com/v1"
    api_key  = os.environ.get("DEEPSEEK_API_KEY", "")

    if not api_key:
        sys.exit("No API key — set DEEPSEEK_API_KEY")

    print(f"\nImscribing: {args.file}  [{args.model}]\n")
    doc = imscribe_document(text, args.file, args.model, api_key, base_url, verbose=True)

    print()
    print(fingerprint_report(doc))
    print(closure_report(doc))

    if args.target:
        print()
        plan = lift_to(doc, args.target)
        print(render_plan(plan))


if __name__ == "__main__":
    main()
