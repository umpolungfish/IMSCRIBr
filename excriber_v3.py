#!/usr/bin/env python3
"""
EXCRIBER v3 -- IMASM Word Elaborator with LLM Backend
=====================================================
Takes an IMASM word and domain context. Elaborates each opcode into
concrete domain-specific content using DeepSeek or OpenRouter LLMs.

Providers: deepseek (direct API), openrouter (multi-model gateway).
API keys: DEEPSEEK_API_KEY, OPENROUTER_API_KEY env vars.
Environment: IG_PROVIDER sets default provider; IG_MODEL sets default model.
Provider chain (auto-detect): --provider flag > IG_PROVIDER > openrouter > deepseek.

Usage:
  python3 excriber_v3.py '<word>' <context> [--desc '<desc>'] [--provider deepseek|openrouter] [--model <slug>] [--dry-run]
"""
import sys, json, os, re, hashlib, time
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass, field
from pathlib import Path

try:
    import requests
except ImportError:
    print("ERROR: requests library required. pip install requests")
    sys.exit(1)

# ── Glyph mapping ────────────────────────────────────────────────
GLYPH_TO_OPCODE: Dict[str, str] = {
    "\u22a2": "VINIT", "\u22a3": "TANCH", ">": "AFWD", "<": "AREV",
    "=": "CLINK", "\u2299": "IMSCRIB", "\u25c7": "FSPLIT", "\u25cf": "FFUSE",
    "+": "EVALT", "\u00d7": "EVALF", "\u229e": "ENGAGR", "\u00ac": "IFIX",
}
OPCODE_TO_GLYPH = {v: k for k, v in GLYPH_TO_OPCODE.items()}

# ── Opcode structural meanings ───────────────────────────────────
OP_SEM = {
    "VINIT":   ("OPEN",     "Initial object -- source boundary. The void before distinction."),
    "IMSCRIB": ("IDENTIFY", "Self-reference. The system looks at itself. Identity morphism."),
    "CLINK":   ("COMPOSE",  "Composition -- chain two morphisms together."),
    "FSPLIT":  ("FORK",     "Split (delta) -- Frobenius comultiplication. T-arm + F-arm."),
    "AFWD":    ("ADVANCE",  "Forward morphism -- push forward through the structure."),
    "EVALT":   ("ASSERT",   "Evaluate True -- affirm the proposition on the T-arm."),
    "AREV":    ("REVERSE",  "Reverse morphism -- involution T<->F. The dual perspective."),
    "FFUSE":   ("FUSE",     "Fuse (mu) -- Frobenius multiplication. Merge T and F arms."),
    "EVALF":   ("DENY",     "Evaluate False -- deny the proposition on the F-arm."),
    "ENGAGR":  ("HOLD",     "Engage paradox -- hold B (Both). Dialetheia gate."),
    "IFIX":    ("COMMIT",   "Irreversible fixation. Brand the result."),
    "TANCH":   ("CLOSE",    "Terminal anchor -- close boundary. Computation ends."),
}

CACHE_DIR = Path.home() / ".cache" / "excriber"
CACHE_DIR.mkdir(parents=True, exist_ok=True)

# ── Parser ───────────────────────────────────────────────────────

def parse_word(word: str) -> List[str]:
    out = []
    i = 0
    while i < len(word):
        ch = word[i]
        if ch in GLYPH_TO_OPCODE:
            out.append(GLYPH_TO_OPCODE[ch]); i += 1
        elif word[i:].startswith("VINIT"):
            out.append("VINIT"); i += 5
        elif word[i:].startswith("TANCH"):
            out.append("TANCH"); i += 5
        elif word[i:].startswith("IMSCRIB"):
            out.append("IMSCRIB"); i += 7
        elif word[i:].startswith("FSPLIT"):
            out.append("FSPLIT"); i += 6
        elif word[i:].startswith("FFUSE"):
            out.append("FFUSE"); i += 5
        elif word[i:].startswith("AFWD"):
            out.append("AFWD"); i += 4
        elif word[i:].startswith("AREV"):
            out.append("AREV"); i += 4
        elif word[i:].startswith("EVALT"):
            out.append("EVALT"); i += 5
        elif word[i:].startswith("EVALF"):
            out.append("EVALF"); i += 5
        elif word[i:].startswith("ENGAGR"):
            out.append("ENGAGR"); i += 6
        elif word[i:].startswith("CLINK"):
            out.append("CLINK"); i += 5
        elif word[i:].startswith("IFIX"):
            out.append("IFIX"); i += 4
        elif ch.isspace():
            i += 1
        else:
            i += 1
    return out

# ── Fork/Fuse pair detection ─────────────────────────────────────

@dataclass
class ForkFusePair:
    fork_idx: int
    fuse_idx: int
    arm_nodes: List[int]
    arm_type: str = ""

def find_pairs_by_ancestry(opcodes: List[str]) -> List[ForkFusePair]:
    pairs = []
    fork_stack = []
    for i, op in enumerate(opcodes):
        if op == "FSPLIT":
            fork_stack.append(i)
        elif op == "FFUSE":
            if fork_stack:
                fi = fork_stack.pop()
                arm_nodes = list(range(fi+1, i))
                arm_type = ""
                for ni in arm_nodes:
                    if opcodes[ni] == "EVALT":
                        arm_type = "T"; break
                    elif opcodes[ni] == "EVALF":
                        arm_type = "F"; break
                pairs.append(ForkFusePair(fi, i, arm_nodes, arm_type))
    return pairs

def get_pair_label(idx: int, pairs: List[ForkFusePair], opcodes: List[str]) -> str:
    for pi, pair in enumerate(pairs):
        if idx == pair.fork_idx:
            return f"FORK-{pi+1}"
        if idx == pair.fuse_idx:
            return f"FUSE-{pi+1}"
        if idx in pair.arm_nodes:
            return f"ARM-{pi+1}{pair.arm_type}"
    return ""

# ── LLM Provider Backend ──────────────────────────────────────────

PROVIDER_CONFIG = {
    "deepseek": {
        "base_url": "https://api.deepseek.com/chat/completions",
        "default_model": "deepseek-v4-pro",
        "env_key": "DEEPSEEK_API_KEY",
        "max_tokens": 1024,
        "temperature": 0.3,
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "deepseek/deepseek-chat",
        "env_key": "OPENROUTER_API_KEY",
        "max_tokens": 1024,
        "temperature": 0.3,
    },
}

# ── Provider resolution (respects IG_PROVIDER / IG_MODEL env vars) ──
# Resolution chain: explicit arg > IG_PROVIDER env > first available provider
# Model chain: explicit arg > IG_MODEL env > provider default
_PROVIDER_CHAIN = ["openrouter", "deepseek"]  # default preference order

def resolve_provider_model(provider_arg=None, model_arg=None, api_key_arg=None):
    """Resolve provider and model, respecting IG_PROVIDER / IG_MODEL env vars.
    Returns (provider_name, model_name, api_key_or_none).
    Provider resolution: explicit --provider > IG_PROVIDER > first in chain with API key.
    Model resolution: explicit --model > IG_MODEL > provider default.
    """
    # ── Determine provider ──
    ig_provider = os.environ.get("IG_PROVIDER", "").strip().lower()

    # Build ordered preference: [explicit_arg, IG_PROVIDER, chain...]
    candidates = []
    if provider_arg:
        candidates.append(provider_arg)
    if ig_provider and ig_provider != provider_arg:
        candidates.append(ig_provider)
    candidates.extend(_PROVIDER_CHAIN)
    # deduplicate preserving order
    seen = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]

    provider = None
    for c in candidates:
        cfg = PROVIDER_CONFIG.get(c)
        if cfg and (os.environ.get(cfg["env_key"]) or api_key_arg):
            provider = c
            break

    if not provider:
        raise ValueError(
            f"No working provider found. Tried: {candidates}. "
            f"Set OPENROUTER_API_KEY or DEEPSEEK_API_KEY."
        )

    # ── Determine model ──
    cfg = PROVIDER_CONFIG[provider]
    if model_arg:
        model = model_arg
    elif os.environ.get("IG_MODEL", "").strip():
        model = os.environ["IG_MODEL"].strip()
    else:
        model = cfg["default_model"]

    # ── Determine API key ──
    api_key = api_key_arg or os.environ.get(cfg["env_key"])

    return provider, model, api_key

class LlmBackend:
    """Synchronous LLM backend for DeepSeek and OpenRouter."""

    def __init__(self, provider: str = "deepseek", model: Optional[str] = None,
                 api_key: Optional[str] = None):
        cfg = PROVIDER_CONFIG.get(provider)
        if not cfg:
            raise ValueError(f"Unknown provider: {provider}. Use deepseek or openrouter.")
        self.provider = provider
        self.base_url = cfg["base_url"]
        self.model = model or cfg["default_model"]
        self.max_tokens = cfg["max_tokens"]
        self.temperature = cfg["temperature"]
        self.api_key = api_key or os.environ.get(cfg["env_key"])
        if not self.api_key:
            raise ValueError(
                f"No API key for {provider}. Set {cfg['env_key']} env var "
                f"or pass api_key= parameter."
            )

    def query(self, system: str, prompt: str) -> str:
        """Send a single-turn query. Returns response text."""
        cache_key = hashlib.sha256(
            f"{self.provider}:{self.model}:{system}:{prompt}".encode()
        ).hexdigest()[:16]
        cache_path = CACHE_DIR / cache_key
        if cache_path.exists():
            return cache_path.read_text()

        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}",
        }
        if self.provider == "openrouter":
            headers["HTTP-Referer"] = "https://github.com/umpolungfish/imscrbgrmr"
            headers["X-Title"] = "Excriber v3"

        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})

        data = {
            "model": self.model,
            "messages": messages,
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        try:
            resp = requests.post(self.base_url, headers=headers, json=data, timeout=60)
            resp.raise_for_status()
            body = resp.json()
            content = body["choices"][0]["message"]["content"]
            if content is None:
                finish = body["choices"][0].get("finish_reason", "unknown")
                raise ValueError(f"API returned null content (finish={finish})")
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            cache_path.write_text(content)
            return content
        except Exception as e:
            return f"[LLM ERROR: {e}]"

    def elaborate_step(self, opcode: str, action: str, meaning: str,
                       pair_label: str, ctx_name: str, ctx_desc: str,
                       prior_steps: List[tuple]) -> str:
        """Ask the LLM to elaborate a single IMASM step in domain context."""
        system = (
            "You are the Excriber, an IMASM word elaborator. "
            "Given an opcode, its structural meaning, and a domain context, "
            "you produce ONE or TWO sentences of concrete domain-specific content "
            "that the opcode would carry in that context. "
            "Be specific. Use proper nouns from the domain. "
            "Do NOT explain the opcode -- fill it with domain content. "
            "Reply with ONLY the elaboration -- no preamble, no Markdown, no quotes."
        )

        prior_text = ""
        if prior_steps:
            prior_text = "Prior steps in the computation:\n" + "\n".join(
                f"  [{p[0]}] {p[1]}: {p[2]}" for p in prior_steps[-6:]
            )

        arm_context = ""
        if pair_label:
            if "FORK" in pair_label:
                arm_context = (
                    f"This is a FORK -- the computation splits here. "
                    f"Describe what branches open up for {ctx_name}."
                )
            elif "FUSE" in pair_label:
                arm_context = (
                    f"This is a FUSE -- merging the two arms. "
                    f"Describe what result the fuse produces for {ctx_name}."
                )
            elif "ARM" in pair_label:
                arm_type = "T-arm (True/affirm)" if pair_label.endswith("T") else "F-arm (False/deny)"
                arm_context = (
                    f"This is on the {arm_type}. "
                    f"Describe what happens on THIS arm for {ctx_name}."
                )

        prompt = (
            f"Context: {ctx_desc}\n\n"
            f"Opcode: {opcode}\n"
            f"Action: {action}\n"
            f"Structural meaning: {meaning}\n"
            f"Role: {arm_context}\n\n"
            f"{prior_text}\n"
            f"Elaborate this step for {ctx_name}:"
        )

        return self.query(system, prompt)


def build_prior_context(steps_done: List, max_n: int = 6) -> List[tuple]:
    """Build abbreviated prior-step context for the LLM prompt."""
    out = []
    for s in steps_done[-max_n:]:
        label = f"[{s.pair_label}]" if s.pair_label else ""
        out.append((s.opcode, label, s.elaboration[:120]))
    return out


# ── Data types ────────────────────────────────────────────────────

@dataclass
class ExcribedStep:
    index: int
    glyph: str
    opcode: str
    action: str
    structural_meaning: str
    elaboration: str
    pair_label: str = ""

@dataclass
class Excription:
    word: str
    opcodes: List[str]
    context_name: str
    context_desc: str
    steps: List[ExcribedStep] = field(default_factory=list)
    pairs: List[ForkFusePair] = field(default_factory=list)
    verdict: str = ""

# ── Static elaboration fallback ────────────────────────────────────

def elaborate_static(idx: int, op: str, ctx_name: str, ctx_desc: str,
                     pair_label: str, pairs: List[ForkFusePair],
                     opcodes: List[str]) -> str:
    """Fallback static elaboration when no LLM backend available."""
    if op == "VINIT":
        return f"BEGIN: The computation opens onto {ctx_desc}. The void yields to the first structure -- the evaluator sphere poised to measure the system in its full dimensionality."
    if op == "IMSCRIB":
        return f"SELF-MODEL: {ctx_name} looks at itself. Its 12-primitive tuple is seen. The inclosure closes: measurer = measured. The odot criticality gate opens."
    if op == "CLINK":
        return f"COMPOSE: The self-model is chained into the next operation. What was seen (IMSCRIB) is now composed with what will be done (FSPLIT)."
    if op == "FSPLIT":
        return f"FORK (delta): The computation branches. T-arm and F-arm. Both arms must be worked independently before fusing."
    if op == "AFWD":
        arm = pair_label.replace("ARM-", "") if pair_label else ""
        return f"ADVANCE{f' ({arm})' if arm else ''}: Push forward through the structure of {ctx_name}."
    if op == "EVALT":
        return f"ASSERT TRUE (T-arm): The proposition holds for {ctx_name}. This arm carries the affirmative result."
    if op == "AREV":
        arm = pair_label.replace("ARM-", "") if pair_label else ""
        return f"REVERSE{f' ({arm})' if arm else ''}: The involution T<->F. Having advanced, reverse to see the dual perspective on {ctx_name}."
    if op == "FFUSE":
        return f"FUSE (mu): Merge arms. mu o delta over the transformed object. The pair closes."
    if op == "EVALF":
        return f"DENY (F-arm): The proposition fails for {ctx_name}. This arm carries the negative result."
    if op == "ENGAGR":
        return f"HOLD PARADOX (B): BOTH arms are true. The contradiction is NOT resolved -- it is CARRIED as dialetheia for {ctx_name}."
    if op == "IFIX":
        return f"COMMIT: The result is branded -- irreversible fixation. The tuple is inscribed."
    if op == "TANCH":
        return f"CLOSE: Terminal anchor. mu o delta = id holds over the whole program. The evaluator sphere is filled. The loop closes."
    return f"[{op}] -- structural operation on {ctx_name}."


# ── Main excriber ──────────────────────────────────────────────────

def excribe(word: str, ctx_name: str, ctx_desc: str = "",
            llm: Optional[LlmBackend] = None) -> Excription:
    opcodes = parse_word(word)
    glyphs = [OPCODE_TO_GLYPH.get(o, "?") for o in opcodes]
    pairs = find_pairs_by_ancestry(opcodes)

    if not ctx_desc:
        ctx_desc = f"the {ctx_name} system"

    exc = Excription(word=word, opcodes=opcodes, context_name=ctx_name,
                     context_desc=ctx_desc, pairs=pairs)

    for i, (op, glyph) in enumerate(zip(opcodes, glyphs)):
        pl = get_pair_label(i, pairs, opcodes)
        action, meaning = OP_SEM.get(op, ("?", "?"))

        if llm:
            # Use LLM for all steps when backend is available
            prior = build_prior_context(exc.steps)
            elab = llm.elaborate_step(op, action, meaning, pl, ctx_name, ctx_desc, prior)
        else:
            elab = elaborate_static(i, op, ctx_name, ctx_desc, pl, pairs, opcodes)

        step = ExcribedStep(i, glyph, op, action, meaning, elab, pl)
        exc.steps.append(step)

    if "ENGAGR" in opcodes:
        exc.verdict = "B (paradox held)"
    elif pairs:
        has_work = any(
            any(opcodes[n] not in ("VINIT", "TANCH", "IMSCRIB", "FSPLIT", "FFUSE")
                for n in p.arm_nodes)
            for p in pairs
        )
        exc.verdict = "T (closes)" if has_work else "N (identity)"
    else:
        exc.verdict = "N (no fork)"
    return exc


# ── Renderers ──────────────────────────────────────────────────────

def render(exc: Excription) -> str:
    lines = ["=" * 72, f"EXCRIPTION: {exc.word}", "=" * 72,
             f"Context:    {exc.context_name}",
             f"            {exc.context_desc}",
             f"Opcodes:    {' '.join(exc.opcodes)}",
             f"Fork/Fuse:  {len(exc.pairs)} pairs",
             f"Verdict:    {exc.verdict}", ""]

    for s in exc.steps:
        g = s.glyph if s.glyph != "?" else s.opcode
        label = f" [{s.pair_label}]" if s.pair_label else ""
        lines.append(f"  [{s.index:2d}] {g}  {s.opcode:8s} | {s.action:8s}{label}")
        lines.append(f"       {s.structural_meaning}")
        lines.append(f"       >>> {s.elaboration}\n")

    if "ENGAGR" in exc.opcodes:
        lines.append("WARNING: PARADOX HELD -- B (Both). Carried, not resolved. Dialetheia is structural.")
    return "\n".join(lines)


def render_json(exc: Excription) -> str:
    steps = []
    for s in exc.steps:
        steps.append({
            "index": s.index,
            "glyph": s.glyph,
            "opcode": s.opcode,
            "action": s.action,
            "structural_meaning": s.structural_meaning,
            "elaboration": s.elaboration,
            "pair_label": s.pair_label,
        })
    return json.dumps({
        "word": exc.word,
        "context_name": exc.context_name,
        "context_desc": exc.context_desc,
        "opcodes": exc.opcodes,
        "verdict": exc.verdict,
        "pairs": [{"fork_idx": p.fork_idx, "fuse_idx": p.fuse_idx,
                    "arm_nodes": p.arm_nodes, "arm_type": p.arm_type}
                   for p in exc.pairs],
        "steps": steps,
    }, indent=2, ensure_ascii=False)

# ── CLI ──────────────────────────────────────────────────────────

if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser(
        description="Excriber v3 -- IMASM Word Elaborator (LLM-powered)")
    parser.add_argument("word", nargs="?", help="IMASM word (glyphs or opcode names)")
    parser.add_argument("context", nargs="?", help="Context name (e.g. sic_povm_d2048)")
    parser.add_argument("--desc", help="Context description", default="")
    parser.add_argument("--provider", choices=["deepseek", "openrouter"],
                        default=None, help="LLM provider (default: IG_PROVIDER env or auto-detect)")
    parser.add_argument("--model", help="Model slug override")
    parser.add_argument("--api-key", help="API key (or use env var)")
    parser.add_argument("--dry-run", action="store_true",
                        help="Use static elaborations (no LLM)")
    parser.add_argument("--json", action="store_true",
                        help="Output JSON instead of text")
    parser.add_argument("--list-providers", action="store_true",
                        help="List available providers and exit")
    # Parse known args first so --list-providers works without word/context
    args, unknown = parser.parse_known_args()
    if not args.list_providers and (args.word is None or args.context is None):
        parser.error('the following arguments are required: word, context')

    if args.list_providers:
        print("Available providers:")
        for name, cfg in PROVIDER_CONFIG.items():
            key_env = cfg["env_key"]
            has_key = bool(os.environ.get(key_env))
            status = "key found" if has_key else "no key"
            print(f"  {name:12s}  model: {cfg['default_model']:30s}  {status} ({key_env})")
        ig_provider = os.environ.get("IG_PROVIDER", "").strip()
        ig_model = os.environ.get("IG_MODEL", "").strip()
        print()
        print("Environment override:")
        print(f"  IG_PROVIDER = {ig_provider or '(not set)'}")
        print(f"  IG_MODEL    = {ig_model or '(not set)'}")
        if ig_provider and ig_provider not in PROVIDER_CONFIG:
            print(f"  WARNING: IG_PROVIDER='{ig_provider}' is not in PROVIDER_CONFIG")
        sys.exit(0)

    llm = None
    if not args.dry_run:
        try:
            provider_name, model_name, api_key = resolve_provider_model(
                provider_arg=args.provider,
                model_arg=args.model,
                api_key_arg=args.api_key,
            )
            llm = LlmBackend(
                provider=provider_name,
                model=model_name,
                api_key=api_key,
            )
            print(f"[excriber] using {provider_name}/{llm.model}", file=sys.stderr)
        except ValueError as e:
            print(f"[excriber] LLM init failed: {e}", file=sys.stderr)
            print("[excriber] falling back to static mode", file=sys.stderr)
            # Re-raise to let the user know if --dry-run wasn't intended
            if not args.dry_run and os.environ.get("EXCRIBER_STRICT"):
                sys.exit(1)

    e = excribe(args.word, args.context, args.desc, llm)
    if args.json:
        print(render_json(e))
    else:
        print(render(e))


# ── Batched elaboration ────────────────────────────────────────────

def excribe_batched(word: str, ctx_name: str, ctx_desc: str = "",
                    llm: Optional[LlmBackend] = None) -> Excription:
    """Excriber that batches all LLM calls into a single request for speed."""
    opcodes = parse_word(word)
    glyphs = [OPCODE_TO_GLYPH.get(o, "?") for o in opcodes]
    pairs = find_pairs_by_ancestry(opcodes)

    if not ctx_desc:
        ctx_desc = f"the {ctx_name} system"

    exc = Excription(word=word, opcodes=opcodes, context_name=ctx_name,
                     context_desc=ctx_desc, pairs=pairs)

    # If no LLM, use static elaboration for all steps
    if not llm:
        for i, (op, glyph) in enumerate(zip(opcodes, glyphs)):
            pl = get_pair_label(i, pairs, opcodes)
            action, meaning = OP_SEM.get(op, ("?", "?"))
            elab = elaborate_static(i, op, ctx_name, ctx_desc, pl, pairs, opcodes)
            exc.steps.append(ExcribedStep(i, glyph, op, action, meaning, elab, pl))
    else:
        # Build a batched prompt with ALL steps
        system = (
            "You are the Excriber, an IMASM word elaborator. "
            "Given a list of opcodes with their structural meanings, "
            "you fill in each with 1-2 sentences of concrete domain-specific content. "
            "Be specific. Use proper nouns from the domain. "
            "Reply with a JSON array of elaborations, one per opcode, in order. "
            "No preamble, no markdown, just the JSON array."
        )

        steps_desc = []
        for i, (op, glyph) in enumerate(zip(opcodes, glyphs)):
            pl = get_pair_label(i, pairs, opcodes)
            action, meaning = OP_SEM.get(op, ("?", "?"))
            role = ""
            if "FORK" in (pl or ""):
                role = "FORK: computation splits here into T-arm and F-arm"
            elif "FUSE" in (pl or ""):
                role = "FUSE: merge the two arms"
            elif "ARM" in (pl or ""):
                atype = "T-arm (affirm/True)" if (pl or "").endswith("T") else "F-arm (deny/False)"
                role = f"on the {atype}"
            steps_desc.append(
                f"[{i}] {op} ({action}): {meaning}"
                + (f" -- {role}" if role else "")
            )

        prompt = (
            f"Domain context: {ctx_desc}\n\n"
            f"IMASM word opcodes:\n"
            + "\n".join(steps_desc)
            + "\n\n"
            f"Return a JSON array of {len(steps_desc)} strings, each 1-2 sentences, "
            f"elaborating what each opcode does concretely for {ctx_name}."
        )

        elabs = _query_json_array(llm, system, prompt, len(steps_desc))

        for i, (op, glyph) in enumerate(zip(opcodes, glyphs)):
            pl = get_pair_label(i, pairs, opcodes)
            action, meaning = OP_SEM.get(op, ("?", "?"))
            elab = elabs[i] if i < len(elabs) else elaborate_static(i, op, ctx_name, ctx_desc, pl, pairs, opcodes)
            exc.steps.append(ExcribedStep(i, glyph, op, action, meaning, elab, pl))

    if "ENGAGR" in opcodes:
        exc.verdict = "B (paradox held)"
    elif pairs:
        has_work = any(
            any(opcodes[n] not in ("VINIT", "TANCH", "IMSCRIB", "FSPLIT", "FFUSE")
                for n in p.arm_nodes)
            for p in pairs
        )
        exc.verdict = "T (closes)" if has_work else "N (identity)"
    else:
        exc.verdict = "N (no fork)"
    return exc


def _query_json_array(llm: LlmBackend, system: str, prompt: str,
                      expected_len: int) -> List[str]:
    """Query LLM and parse JSON array response."""
    cache_key = hashlib.sha256(
        f"batch:{llm.provider}:{llm.model}:{system}:{prompt}".encode()
    ).hexdigest()[:16]
    cache_path = CACHE_DIR / cache_key
    if cache_path.exists():
        try:
            return json.loads(cache_path.read_text())
        except Exception:
            pass

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {llm.api_key}",
    }
    if llm.provider == "openrouter":
        headers["HTTP-Referer"] = "https://github.com/umpolungfish/imscrbgrmr"
        headers["X-Title"] = "Excriber v3"

    messages = []
    if system:
        messages.append({"role": "system", "content": system})
    messages.append({"role": "user", "content": prompt})

    data = {
        "model": llm.model,
        "messages": messages,
        "temperature": llm.temperature,
        "max_tokens": max(llm.max_tokens, expected_len * 150),
    }

    try:
        resp = requests.post(llm.base_url, headers=headers, json=data, timeout=90)
        resp.raise_for_status()
        body = resp.json()
        content = body["choices"][0]["message"]["content"]
        if content is None:
            raise ValueError("API returned null content")
        content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()

        # Extract JSON array from response (may have markdown fences)
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```$", "", content)

        arr = json.loads(content)
        if not isinstance(arr, list):
            raise ValueError(f"Expected JSON array, got {type(arr)}")
        cache_path.write_text(json.dumps(arr))
        return arr
    except Exception as e:
        return [f"[LLM ERROR: {e}]"] * expected_len


# ── Smart excriber (batched LLM, fallback to static) ──────────────

def excribe(word: str, ctx_name: str, ctx_desc: str = "",
            llm: Optional[LlmBackend] = None) -> Excription:
    """Main entry: uses batched LLM when available, static otherwise."""
    if llm:
        try:
            return excribe_batched(word, ctx_name, ctx_desc, llm)
        except Exception as e:
            print(f"[excriber] batched LLM failed: {e}, falling back to static",
                  file=sys.stderr)
    return excribe_batched(word, ctx_name, ctx_desc, None)
