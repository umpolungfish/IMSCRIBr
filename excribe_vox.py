#!/usr/bin/env python3
"""
EXCRIBE-VOX — IMASM word → exact isomorphic processes in a target register
==========================================================================
Combines the excriber (word → per-token elaboration) with Vox (the substrate
judge) to translate each token of an IMASM word into the exact isomorphic
process that realizes it in a desired computational register, with runtime
commands for the project architectures (G-mOMonadOS, Vox, the IMASM language
CLI, the native numeral, ParaVM).

Design rules (from the excriber review):
  - the word is judged by the REAL judge (vox verdict), never re-implemented;
  - only the canonical twelve marks parse (strict: anything else raises);
  - fork/fuse pairing is read from `vox pairs`, not re-derived by stack rule.

Usage:
  python3 excribe_vox.py '<word>' '<register>' [--runtime auto|gmonados|vox|imas|native|para]
                         [--emit] [--json] [--list-registers]

  python3 excribe_vox.py '⊢∈⊞⊙≻≺⋈⊤⊥∋⊡⊣' 'anyonic ququart computation'
"""
import sys, os, json, re, hashlib, argparse, subprocess
from dataclasses import dataclass
from typing import List, Dict, Optional, Tuple

HERE = "/home/mrnob0dy666/imsgct/IMSCRIBr"
VOX_BIN = "/home/mrnob0dy666/imsgct/Vox/target/release/vox"
CANON = "⊢ ⊣ ≻ ≺ ⋈ ⊙ ∈ ∋ ⊤ ⊥ ⊞ ⊡"

# ── strict canonical parser (from the fixed excriber_v3; inline fallback) ──
try:
    sys.path.insert(0, HERE)
    from excriber_v3 import parse_word
except Exception:
    _GL = {"⊢": "VINIT", "⊣": "TANCH", "≻": "AFWD", "≺": "AREV", "⋈": "CLINK",
           "⊤": "EVALT", "∈": "FSPLIT", "∋": "FFUSE", "⊙": "IMSCRIB", "⊥": "EVALF",
           "⊞": "ENGAGR", "⊡": "IFIX"}
    _NAMES = ["VINIT", "TANCH", "IMSCRIB", "FSPLIT", "FFUSE", "AFWD", "AREV",
              "EVALT", "EVALF", "ENGAGR", "CLINK", "IFIX"]
    def parse_word(word: str) -> List[str]:
        out, i = [], 0
        while i < len(word):
            ch = word[i]
            if ch in _GL:
                out.append(_GL[ch]); i += 1
            elif ch.isspace():
                i += 1
            else:
                for n in _NAMES:
                    if word[i:].startswith(n):
                        out.append(n); i += len(n); break
                else:
                    raise ValueError(
                        f"non-canonical mark {ch!r} at position {i} in {word!r}; "
                        f"only the twelve canonical glyphs parse: {CANON}")
        return out

GLYPHS = {v: k for k, v in {
    "⊢": "VINIT", "⊣": "TANCH", "≻": "AFWD", "≺": "AREV", "⋈": "CLINK",
    "⊤": "EVALT", "∈": "FSPLIT", "∋": "FFUSE", "⊙": "IMSCRIB", "⊥": "EVALF",
    "⊞": "ENGAGR", "⊡": "IFIX"}.items()}

# ── the real judge (Vox) ──────────────────────────────────────────
def judge(word: str) -> Tuple[Optional[str], str]:
    """Call Vox — the substrate judge. Returns (verdict_letter, raw)."""
    try:
        r = subprocess.run([VOX_BIN, "verdict", word],
                           capture_output=True, text=True, timeout=120)
        out = ((r.stdout or "") + (r.stderr or "")).strip()
        m = re.search(r"verdict\s+([TBNF])", out)
        if m:
            return m.group(1), out
    except Exception:
        pass
    return None, "vox unavailable — UNJUDGED"

def pair_report(word: str) -> str:
    try:
        r = subprocess.run([VOX_BIN, "pairs", word],
                           capture_output=True, text=True, timeout=120)
        return (r.stdout or "").strip()
    except Exception:
        return ""

# ── runtime catalog: the project architectures (real command surfaces) ──
# ── LLM Provider Backend (mirrors excriber_v3; local llama.cpp first) ──

try:
    import requests as _requests
    _HAVE_REQUESTS = True
except ImportError:
    _HAVE_REQUESTS = False

LLM_CACHE_DIR = HERE + "/.exv_cache"

PROVIDER_CONFIG = {
    "local": {
        "base_url": os.environ.get("IG_LOCAL_URL", "http://127.0.0.1:8000").rstrip("/") + "/v1/chat/completions",
        "models_url": os.environ.get("IG_LOCAL_URL", "http://127.0.0.1:8000").rstrip("/") + "/v1/models",
        "default_model": "/home/mrnob0dy666/imsgct/.modelz/q38/Q3p8.gguf",
        "env_key": "IG_LOCAL_API_KEY",
        "max_tokens": 16384,
        "temperature": 0.3,
    },
    "deepseek": {
        "base_url": "https://api.deepseek.com/chat/completions",
        "default_model": "deepseek-v4-pro",
        "env_key": "DEEPSEEK_API_KEY",
        "max_tokens": 4096,
        "temperature": 0.3,
    },
    "openrouter": {
        "base_url": "https://openrouter.ai/api/v1/chat/completions",
        "default_model": "deepseek/deepseek-chat",
        "env_key": "OPENROUTER_API_KEY",
        "max_tokens": 4096,
        "temperature": 0.3,
    },
}

_PROVIDER_CHAIN = ["local", "openrouter", "deepseek"]   # local first, like the operator itself


def local_server_up(cfg) -> bool:
    if not _HAVE_REQUESTS:
        return False
    try:
        r = _requests.get(cfg["models_url"], timeout=2)
        return r.status_code == 200
    except Exception:
        return False


def resolve_provider_model(provider_arg=None, model_arg=None, api_key_arg=None):
    """Resolution chain (same shape as excriber_v3):
    provider: explicit arg > IG_PROVIDER env > first available in chain (local needs no key, only a live server)
    model:    explicit --model > IG_MODEL env > provider default (local: live model name from /v1/models)"""
    ig_provider = os.environ.get("IG_PROVIDER", "").strip().lower()
    candidates = []
    if provider_arg:
        candidates.append(provider_arg)
    if ig_provider and ig_provider != provider_arg:
        candidates.append(ig_provider)
    candidates.extend(_PROVIDER_CHAIN)
    seen = set()
    candidates = [c for c in candidates if not (c in seen or seen.add(c))]
    provider = None
    for c in candidates:
        cfg = PROVIDER_CONFIG.get(c)
        if not cfg:
            continue
        if c == "local":
            if local_server_up(cfg):
                provider = c
                break
            continue
        if os.environ.get(cfg["env_key"]) or api_key_arg:
            provider = c
            break
    if not provider:
        raise ValueError(
            f"No working provider. Tried: {candidates}. "
            f"Start llama-server (llama.cpp) on :8000 or set OPENROUTER_API_KEY / DEEPSEEK_API_KEY.")
    cfg = PROVIDER_CONFIG[provider]
    if model_arg:
        model = model_arg
    elif os.environ.get("IG_MODEL", "").strip():
        model = os.environ["IG_MODEL"].strip()
    else:
        model = cfg["default_model"]
        if provider == "local" and _HAVE_REQUESTS:
            try:
                names = _requests.get(cfg["models_url"], timeout=2).json().get("models") or []
                if names and names[0].get("name"):
                    model = names[0]["name"]
            except Exception:
                pass
    api_key = api_key_arg or os.environ.get(cfg["env_key"])
    return provider, model, api_key


class LlmBackend:
    """Synchronous LLM backend — same shape as excriber_v3's: sha256 cache,
    single-turn chat completion, </think> stripping, error → marker string."""

    def __init__(self, provider: str = "local", model: Optional[str] = None,
                 api_key: Optional[str] = None):
        cfg = PROVIDER_CONFIG.get(provider)
        if not cfg:
            raise ValueError(f"Unknown provider: {provider}. Use local, deepseek or openrouter.")
        if not _HAVE_REQUESTS:
            raise ValueError("requests library required for LLM backend. pip install requests")
        self.provider = provider
        self.base_url = cfg["base_url"]
        self.model = model or cfg["default_model"]
        self.max_tokens = cfg["max_tokens"]
        self.temperature = cfg["temperature"]
        self.api_key = api_key or os.environ.get(cfg["env_key"])

    def cache_path_for(self, system: str, prompt: str) -> str:
        k = hashlib.sha256(
            f"{self.provider}:{self.model}:{system}:{prompt}".encode()).hexdigest()[:16]
        return os.path.join(LLM_CACHE_DIR, k)

    def query(self, system: str, prompt: str) -> str:
        os.makedirs(LLM_CACHE_DIR, exist_ok=True)
        cache_path = self.cache_path_for(system, prompt)
        if os.path.exists(cache_path):
            return open(cache_path).read()
        headers = {"Content-Type": "application/json"}
        if self.api_key:
            headers["Authorization"] = f"Bearer {self.api_key}"
        messages = []
        if system:
            messages.append({"role": "system", "content": system})
        messages.append({"role": "user", "content": prompt})
        data = {"model": self.model, "messages": messages,
                "temperature": self.temperature, "max_tokens": self.max_tokens}
        try:
            resp = _requests.post(self.base_url, headers=headers, json=data, timeout=300)
            resp.raise_for_status()
            content = resp.json()["choices"][0]["message"]["content"]
            if content is None:
                finish = resp.json()["choices"][0].get("finish_reason", "unknown")
                raise ValueError(f"API returned null content (finish={finish})")
            content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
            open(cache_path, "w").write(content)
            return content
        except Exception as e:
            return f"[LLM ERROR: {e}]"


def extract_json_object(text):
    """Robust JSON object recovery: direct parse, fence strip, then a
    string-aware balanced-bracket scan; returns the last object that has a
    'tokens' key, else the last parseable object, else None."""
    if not text:
        return None
    text = text.strip()
    if text.startswith("```"):
        text = re.sub(r"^```[a-zA-Z]*\s*|\s*```$", "", text, flags=re.MULTILINE).strip()
    try:
        return json.loads(text)
    except Exception:
        pass
    found = []
    n = len(text)
    i = 0
    while True:
        i = text.find("{", i)
        if i < 0:
            break
        depth, in_str, esc = 0, False, False
        for j in range(i, n):
            c = text[j]
            if in_str:
                if esc: esc = False
                elif c == "\\": esc = True
                elif c == '"': in_str = False
            else:
                if c == '"': in_str = True
                elif c == "{": depth += 1
                elif c == "}":
                    depth -= 1
                    if depth == 0:
                        try:
                            found.append(json.loads(text[i:j+1]))
                        except Exception:
                            pass
                        break
        i += 1
    if not found:
        return None
    for o in reversed(found):
        if isinstance(o, dict) and "tokens" in o:
            return o
    return found[-1] if isinstance(found[-1], dict) else None


STRUCT_ACTIONS = {
    "VINIT":   "0→1 source boundary; the only mark that creates",
    "TANCH":   "terminal anchor; sink, out-port may stay open (living end)",
    "AFWD":    "forward morphism; WORK",
    "AREV":    "self-inverse clearing reverse; WORK, T↔F, t↔f",
    "CLINK":   "compose/link; WORK",
    "IMSCRIB": "identity / self-reference; the neutral generator, no work",
    "FSPLIT":  "fork δ; the only brancher",
    "FFUSE":   "fuse μ; the only merger",
    "EVALT":   "evaluate/deposit TRUE; WORK",
    "EVALF":   "evaluate/deposit FALSE; WORK",
    "ENGAGR":  "hold paradox (Belnap diagonal); WORK",
    "IFIX":    "irreversible commit; WORK",
}

LLM_SYSTEM = ("You are the IMASM→register morphism translator. An IMASM word is a node list of the twelve "
"opcodes; the judge (vox) has already verdicted it. Given the word, its verdict, and a target register "
"(a physical/computational substrate), produce the EXACT isomorphic process each token realizes in that "
"register. Answer with ONE strict JSON object and nothing else, no markdown fences: "
'{"register": {"name": string, "dim": string}, "tokens": [{"i": int, "process": string (short, <=6 words), '
'"concrete": string (the concrete operation in the register), "rationale": string (one sentence: why this '
'process is the isomorphic image of that opcode)}]}. tokens must cover every token index in order. '
"Be concrete to the substrate: name the actual physical/computational operation, not abstractions.")


def llm_translate(ops, glyphs, word, verdict, register_text, reg, generic, braidword,
                  provider, model, dry_run=False):
    """Query the LLM for per-token isomorphic processes.
    Returns (rows_or_None, meta). rows is None on LLM failure → caller keeps the canonical table."""
    lines = [f"IMASM word: {word}  ({len(ops)} tokens)",
             f"Judge (vox verdict): {verdict or 'UNJUDGED'}",
             f"Braid word assembled from AFWD/AREV/CLINK: {braidword}",
             f"Target register (user text): {register_text}"]
    if not generic:
        lines.append(f"Matched built-in register: {reg.name} — {reg.dim}")
    lines.append("Tokens (index: mark opcode — structural action):")
    for i, (g, op) in enumerate(zip(glyphs, ops)):
        lines.append(f"  {i}: {g} {op} — {STRUCT_ACTIONS.get(op, '')}")
    prompt = "\n".join(lines) + "\nProduce the JSON."
    if dry_run:
        return None, {"provider": provider, "model": model, "dry_run": True,
                      "prompt": prompt, "system": LLM_SYSTEM}
    be = LlmBackend(provider, model)
    raw = be.query(LLM_SYSTEM, prompt)
    if raw.startswith("[LLM ERROR"):
        return None, {"provider": provider, "model": model, "error": raw}
    import re as _re
    _topen, _tclose = "\u003Cthink", "\u003C/think\u003E"
    stripped = _re.sub(_topen + r".*" + _tclose, "", raw, flags=_re.DOTALL).strip()
    obj = extract_json_object(stripped) or (extract_json_object(raw) if raw.strip() else None)
    if obj is None or not isinstance(obj, dict) or "tokens" not in obj:
        try:
            os.remove(be.cache_path_for(LLM_SYSTEM, prompt))   # purge poisoned cache entry
        except Exception:
            pass
        head = (stripped or raw)[:120].replace("\n", " ")
        return None, {"provider": provider, "model": model,
                      "error": f"no usable JSON in LLM response (head: {head!r})"}
    toks = obj.get("tokens", [])
    rows = []
    for i, (g, op) in enumerate(zip(glyphs, ops)):
        t = next((t for t in toks if t.get("i") == i), None)
        if t is None or not str(t.get("concrete", "")).strip():
            try:
                os.remove(be.cache_path_for(LLM_SYSTEM, prompt))
            except Exception:
                pass
            return None, {"provider": provider, "model": model,
                          "error": f"token index {i} missing from LLM response"}
        rows.append({"i": i, "glyph": g, "opcode": op,
                     "process": str(t.get("process", "")).strip() or op,
                     "concrete": str(t["concrete"]).strip(),
                     "rationale": str(t.get("rationale", "")).strip(),
                     "command": "—", "exact": False, "source": "llm"})
    meta = {"provider": provider, "model": model}
    if generic:
        meta["register"] = {"name": str(obj.get("register", {}).get("name", register_text)),
                            "dim": str(obj.get("register", {}).get("dim", "synthesized by LLM"))}
    return rows, meta

RUNTIMES = {
    "gmonados": {
        "name": "G-mOMonadOS (GPU-native mOMonadOS)",
        "lanes": {
            "Quantum":  "fibqc verify|compile|jones|knot|winding · braids · jones · qft · iuft · sic · d12 · d2048 · dqi · shor",
            "IMASM":    "cycle · weight · banked · insert · trans · arev",
            "Crystal":  "decode · store · find · name",
            "Grammar":  "ig · classify · frob · aleph · shor · rh · ym · fde",
            "ParaASM":  "test · frob · kernel · load",
            "Exec":     "boot <I-XXIX|dec> · run · tick · watch · timer",
            "Status":   "status · registers · memory · heatmap · graph · program",
            "Cr3echrz": "cr3 · p4ra",
            "Rebis":    "codon · translate · genetics · materials · bio · tx",
            "Dialect":  "ruleset · jump · seal · compound",
            "Tools":    "opi · braids · gpu batches · fuzzing · provenance",
        },
    },
    "vox":    {"name": "V⊙x (substrate witness)",
               "lanes": {"lift": "lift · run · circuit · word",
                          "judge": "verdict · pairs · classify · self"}},
    "imas":   {"name": "IMASM language CLI",
               "lanes": {"check": "check · classify · eval · eval16 · compose · chaos · path · learn"}},
    "native": {"name": "native numeral",
               "lanes": {"numeral": "encode · decode · factor · gcd · primetest · unbraid · compose · decompose"}},
    "para":   {"name": "ParaVM (Belnap FOUR)",
               "lanes": {"b4": "lattice · kernel · invariant · circuit · run · b4f_check · bridge · test"}},
}

# ── register model ─────────────────────────────────────────────────
@dataclass
class Register:
    rid: str
    name: str
    dim: str
    desc: str
    keywords: List[str]
    runtime: str                     # default runtime id
    ops: Dict[str, Tuple]             # opcode -> (process, concrete, rationale, command, exact)
# ── the register catalog ───────────────────────────────────────────

ANYONIC = Register(
    rid="anyon", name="anyonic ququart computation",
    dim="d=4 ququart · ττ fusion space of the Fibonacci anyon (1+τ)",
    desc="A 4-level system encoding the fusion channels of a ττ Fibonacci-anyon "
         "pair. Braids are 2/5-turn phases on the winding lattice; the degenerate "
         "fusion space is the both. Lane: G-mOMonadOS Quantum / fibqc.",
    keywords=["anyon", "anyonic", "fibonacci", "fib", "ququart", "braiding",
              "braid", "topological", "nonabelian", "non-abelian", "σ"],
    runtime="gmonados",
    ops={
        "VINIT": ("vacuum preparation",
                  "reset the isolated ququart to the vacuum sector |1⟩₀ (4 levels cleared, anyons in ground state)",
                  "VINIT is the 0→1 source, the only mark that creates; preparation creates the system",
                  "quantum fibqc verify", True),
        "FSPLIT": ("fusion-channel split (δ)",
                   "open the ττ pair: the two channel alternatives |1⟩,|τ⟩ of τ×τ=1+τ branch — the degenerate space entered as a block",
                   "δ is the only brancher; the fusion rule is exactly the two-channel split",
                   "quantum fibqc compile <braidword>", False),
        "FFUSE": ("fusion (μ)",
                  "fuse the ττ pair back; the charge sector (1 or τ) is the readout",
                  "μ is the only merger; fusion is the inverse of the split",
                  "quantum fibqc compile <braidword>", False),
        "ENGAGR": ("Belnap diagonal hold",
                   "hold BOTH channel outcomes: the degenerate fusion space is kept coherent, nothing collapses (genuine B)",
                   "ENGAGR holds the paradox; the degenerate fusion space is the both",
                   "quantum braids", False),
        "IMSCRIB": ("self-modeling ancilla",
                    "swap the register's sector onto a mirror qudit — the system reads its own state",
                    "⊙ is self-reference; the mirror ancilla is the isomorphic self-model",
                    "quantum fibqc jones <braidword>", False),
        "AFWD": ("forward braid σ",
                 "apply the σ exchange to the τ pair (2/5-turn phase on the winding lattice)",
                 "AFWD is the forward morphism; σ is the forward morphism of the anyonic representation",
                 "quantum fibqc compile σ", True),
        "AREV": ("clearing reverse σ⁻¹",
                 "apply σ⁻¹; the braid unwinds — a phase held in the open is lost, a banked phase survives",
                 "AREV is the self-inverse clearing reverse; σ⁻¹ is the exact inverse braid",
                 "quantum fibqc compile σ⁻¹", True),
        "CLINK": ("braid-word composition",
                  "concatenate the braids into one braid program (σ·σ⁻¹ → a single word)",
                  "⋈ composes; braid-word concatenation is the isomorphic composition",
                  "quantum fibqc compile <composed>", True),
        "EVALT": ("T-channel projection",
                  "measure and project onto the fusion channel |1⟩ (the T outcome)",
                  "EVALT deposits T; the 1-channel projection is the isomorphic deposit",
                  "quantum dqi (measure phase)", False),
        "EVALF": ("F-channel projection",
                  "measure and project onto the fusion channel |τ⟩ (the F outcome)",
                  "EVALF deposits F; the τ-channel projection is the isomorphic deposit",
                  "quantum dqi (measure phase)", False),
        "IFIX": ("topological commit",
                 "destructive readout: the final sector is fixed irreversibly (topologically protected)",
                 "IFIX is the irreversible commit; topological measurement is irreversible",
                 "quantum fibqc jones <braidword>", True),
        "TANCH": ("release / terminal",
                  "hand the final sector to the readout bus; the out-port may remain open (living end)",
                  "TANCH anchors the terminal; release, the port may stay open",
                  "run (Exec lane)", False),
    })

BELNAP = Register(
    rid="belnap", name="Belnap FOUR register",
    dim="B4 = {T, F, t, f} with the B and N diagonals",
    desc="Paraconsistent 4-valued register; the contradiction is held, not "
         "resolved. Lane: ParaVM.",
    keywords=["belnap", "four", "dialethe", "paraconsistent", "contradiction",
              "b4", "multilattice"],
    runtime="para",
    ops={
        "VINIT": ("register init", "set the B4 register to N (nothing believed yet)",
                  "0→1 source: creates the register", "para lattice init N", True),
        "FSPLIT": ("δ-cut", "cut {T,t} | {F,f} — the truth cut inside the constructive block",
                   "δ is the only brancher; the cut is the partition", "para circuit T,t,F,f", False),
        "FFUSE": ("μ-merge", "recombine the arms into one B4 value (μ∘δ=id at either arity)",
                  "μ is the only merger", "para lattice meet/join", False),
        "ENGAGR": ("hold B (Both)", "set the register to B — the contradiction is carried, not resolved",
                   "ENGAGR is the Belnap diagonal", "para lattice set B", True),
        "IMSCRIB": ("self-belief readout", "read the register's own current value",
                    "⊙ is self-reference", "para b4f_check <query>", False),
        "AFWD": ("monotone advance", "advance the belief (N→F→B→T or N→t→B→T)",
                 "AFWD advances the morphism", "para kernel 1", False),
        "AREV": ("complement", "swap T↔F, t↔f — the dual perspective",
                 "AREV is the involution", "para circuit complement", False),
        "CLINK": ("gate composition", "chain the B4 gates into one circuit",
                  "⋈ composes", "para circuit <gates>", True),
        "EVALT": ("deposit T", "set T on the register", "EVALT deposits T",
                  "para lattice set T", True),
        "EVALF": ("deposit F", "set f on the register", "EVALF deposits F",
                  "para lattice set f", True),
        "IFIX": ("commit belief", "freeze the current B4 value — irreversible",
                 "IFIX commits", "para invariant", False),
        "TANCH": ("lattice dump", "release the register; the out-port may stay open",
                  "TANCH anchors", "para lattice dump", False),
    })
QUQUART = Register(
    rid="ququart", name="ququart (d=4 unitary)",
    dim="a 4-level unitary system",
    desc="Generic 4-level computation without anyonic statistics. "
         "Lane: G-mOMonadOS Quantum / qft.",
    keywords=["ququart", "qudit", "d=4", "quaternary", "4-level", "unitary"],
    runtime="gmonados",
    ops={
        "VINIT": ("reset", "reset the qudit to |0⟩",
                  "VINIT is the 0→1 source", "quantum qft init", False),
        "FSPLIT": ("H4 superposition", "Hadamard over the 4 levels — all alternatives branch",
                   "δ is the only brancher", "quantum qft H4", False),
        "FFUSE": ("recombine", "recombine the branches (inverse H4)",
                  "μ is the only merger", "quantum qft H4⁻¹", False),
        "ENGAGR": ("phase hold", "hold the 4-valued phase without collapse (the both)",
                   "ENGAGR holds the paradox", "quantum qft phase-hold", False),
        "IMSCRIB": ("mirror SWAP", "SWAP with an ancilla qudit — self-model",
                    "⊙ is self-reference", "quantum qft SWAP", False),
        "AFWD": ("T4 gate", "the π/4 phase gate T4 (1/4 winding)",
                 "AFWD advances the morphism", "quantum qft T4", True),
        "AREV": ("T4⁻¹", "the inverse phase gate (clearing reverse)",
                 "AREV is the involution", "quantum qft T4⁻¹", True),
        "CLINK": ("gate composition", "compose the gates into one circuit",
                  "⋈ composes", "quantum qft <circuit>", True),
        "EVALT": ("project |0⟩", "measure onto |0⟩ (the T outcome)",
                  "EVALT deposits T", "quantum dqi measure", False),
        "EVALF": ("project |1⟩", "measure onto |1⟩ (the F outcome)",
                  "EVALF deposits F", "quantum dqi measure", False),
        "IFIX": ("final measurement", "irreversible final readout",
                 "IFIX commits", "quantum dqi measure --commit", False),
        "TANCH": ("release", "release the qudit to the environment",
                  "TANCH anchors", "run (Exec lane)", False),
    })

SIC = Register(
    rid="sic", name="SIC-POVM frame register",
    dim="SIC-POVM in the frame's dimension",
    desc="Measurement-frame computation: fiducial rays, dual frames, "
         "DST walks. Lane: G-mOMonadOS Quantum / sic · d12 · d2048 · dqi.",
    keywords=["sic", "povm", "fiducial", "frame", "measurement"],
    runtime="gmonados",
    ops={
        "VINIT": ("prepare fiducial", "prepare the fiducial ray of the SIC",
                  "VINIT is the 0→1 source", "quantum sic fiducial", False),
        "FSPLIT": ("POVM split", "decompose the frame into its POVM branches",
                   "δ is the only brancher", "quantum sic split", False),
        "FFUSE": ("outcome fusion", "fuse the outcomes back to the frame",
                  "μ is the only merger", "quantum sic fuse", False),
        "ENGAGR": ("degeneracy hold", "hold the dual-pair degeneracy without collapse (the both)",
                   "ENGAGR holds the paradox", "quantum sic hold", False),
        "IMSCRIB": ("dual self-projection", "project the frame onto its own dual",
                    "⊙ is self-reference", "quantum dqi", False),
        "AFWD": ("DST advance", "advance one step on the design-system-tree walk",
                 "AFWD advances", "quantum sic walk +1", False),
        "AREV": ("DST reverse", "walk back one step",
                 "AREV is the involution", "quantum sic walk −1", False),
        "CLINK": ("frame composition", "compose the frames",
                  "⋈ composes", "quantum sic compose", False),
        "EVALT": ("outcome +", "take the + outcome of the POVM",
                  "EVALT deposits T", "quantum dqi outcome +", False),
        "EVALF": ("outcome −", "take the − outcome of the POVM",
                  "EVALF deposits F", "quantum dqi outcome −", False),
        "IFIX": ("collapse", "collapse the outcome — irreversible",
                 "IFIX commits", "quantum dqi collapse", False),
        "TANCH": ("frame release", "release the frame to the readout bus",
                  "TANCH anchors", "run (Exec lane)", False),
    })

NUMERAL = Register(
    rid="numeral", name="native numeral register",
    dim="the number as its own word ⊢(≻⋈∈bit∋)*⊙⊡⊣",
    desc="Arithmetic on the word's own bits — no decimal string kept alongside. "
         "Lane: native numeral.",
    keywords=["numeral", "number", "arithmetic", "integer", "factor", "prime"],
    runtime="native",
    ops={
        "VINIT": ("open the word", "emit ⊢ — the numeral word begins",
                  "VINIT is the 0→1 source", "native_numeral encode <n>", False),
        "FSPLIT": ("bit-cell split", "open a bit cell ≻⋈∈ (LSB-first)",
                   "δ is the only brancher", "native_numeral encode (cell open)", False),
        "FFUSE": ("bit-cell fuse", "close the bit cell ∋",
                  "μ is the only merger", "native_numeral encode (cell close)", False),
        "ENGAGR": ("parity hold", "hold the parity ambiguity (the B of the B4 gcd trace)",
                   "ENGAGR holds the paradox", "native_numeral gcd (Belnap trace)", False),
        "IMSCRIB": ("the word's own marks", "read the word's own glyph marks",
                    "⊙ is self-reference", "native_numeral word", True),
        "AFWD": ("advance one bit", "advance LSB→MSB through the bit cells",
                 "AFWD advances", "native_numeral encode (bits)", False),
        "AREV": ("reverse bit order", "reverse the bit order (MSB→LSB)",
                 "AREV is the involution", "native_numeral decode (reversed)", False),
        "CLINK": ("cell concatenation", "concatenate the bit cells into the full word",
                  "⋈ composes", "native_numeral encode <n>", True),
        "EVALT": ("deposit bit 0", "deposit ⊤ (bit 0, even)",
                  "EVALT deposits T", "native_numeral encode (bit 0)", False),
        "EVALF": ("deposit bit 1", "deposit ⊥ (bit 1, odd)",
                  "EVALF deposits F", "native_numeral encode (bit 1)", False),
        "IFIX": ("fix the limb", "commit the digit — irreversible",
                 "IFIX commits", "native_numeral decode (round-trip)", False),
        "TANCH": ("close ⊙⊡⊣", "close the word with ⊙⊡⊣",
                  "TANCH anchors", "native_numeral decode <word>", True),
    })
SUBSTRATE = Register(
    rid="substrate", name="real substrate (binary / EVM / WASM / .pyc)",
    dim="compiled code as a word",
    desc="The control-flow shape of real code, lifted by Vox. "
         "Lane: Vox.",
    keywords=["binary", "substrate", "evm", "wasm", "pyc", "x86", "lift",
              "code", "machine", "function"],
    runtime="vox",
    ops={
        "VINIT": ("prologue / entry", "the function entry — the walk begins",
                  "VINIT is the 0→1 source", "vox lift <file>", True),
        "FSPLIT": ("branch", "an if/switch — control flow forks",
                   "δ is the only brancher", "vox pairs <word>", False),
        "FFUSE": ("join", "the branch merge — the fork is undone",
                  "μ is the only merger", "vox pairs <word>", False),
        "ENGAGR": ("reentrancy hold", "hold a fork open across a terminal "
                   "(early return / reentrancy) — B",
                   "ENGAGR holds the paradox", "vox verdict <word>", False),
        "IMSCRIB": ("self-lift", "Vox reads its own image — every function in phase, F zero",
                    "⊙ is self-reference", "vox self", True),
        "AFWD": ("instruction advance", "PC++ — the next instruction",
                 "AFWD advances", "vox run <sym>", False),
        "AREV": ("backward jump", "a jump back — the clearing reverse",
                 "AREV is the involution", "vox run <sym> (backedge)", False),
        "CLINK": ("call/return link", "the call composed with its return",
                  "⋈ composes", "vox run <sym> --args", False),
        "EVALF": ("flag F", "CF=1 — the F flag is set",
                  "EVALF deposits F", "vox tables <file> <sym>", False),
        "EVALT": ("flag T", "CF=0 / ZF=1 — the T flag is set",
                  "EVALT deposits T", "vox tables <file> <sym>", False),
        "IFIX": ("commit (write / syscall)", "an irreversible side effect",
                 "IFIX commits", "vox run <sym> (commit)", False),
        "TANCH": ("ret / epilogue", "the function returns; the out-port may stay open",
                  "TANCH anchors", "vox verdict <word>", True),
    })

IMAS = Register(
    rid="imas", name="the IMASM register (self-host)",
    dim="the word runs on its own kernel",
    desc="The word is executed by the language that judges it — the strange "
         "loop as register. Lane: IMASM language CLI.",
    keywords=["imas", "kernel", "word", "language", "selfhost", "self-host"],
    runtime="imas",
    ops={
        "VINIT": ("open the word", "the word begins on the kernel register",
                  "VINIT is the 0→1 source", "imas check <word>", True),
        "FSPLIT": ("δ fork", "the register is cut into a partition {T,t}|{F,f}",
                   "δ is the only brancher", "imas eval16 <word> seed=A", False),
        "FFUSE": ("μ fuse", "the partition recombines — μ∘δ=id",
                  "μ is the only merger", "imas eval16 <word> seed=A", False),
        "ENGAGR": ("Belnap diagonal", "the kernel holds B — both arms live",
                   "ENGAGR holds the paradox", "imas eval <word> seed=B", False),
        "IMSCRIB": ("identity morphism", "the register sees itself",
                    "⊙ is self-reference", "imas classify <word>", False),
        "AFWD": ("forward morphism", "the register advances through the structure",
                 "AFWD advances", "imas eval <word>", False),
        "AREV": ("clearing reverse", "T↔F, t↔f on the register",
                 "AREV is the involution", "gmonados: imasm arev", False),
        "CLINK": ("compose", "the morphisms are chained",
                  "⋈ composes", "imas compose", False),
        "EVALT": ("deposit T", "T is set on the register",
                  "EVALT deposits T", "imas eval <word> seed=T", False),
        "EVALF": ("deposit F", "F is set on the register",
                  "EVALF deposits F", "imas eval <word> seed=F", False),
        "IFIX": ("commit", "the register value is fixed",
                 "IFIX commits", "imas check <word>", False),
        "TANCH": ("anchor", "the word ends; the out-port may stay open",
                  "TANCH anchors", "imas check <word>", True),
    })

REGISTERS = [ANYONIC, QUQUART, BELNAP, SIC, NUMERAL, SUBSTRATE, IMAS]

def match_register(text: str) -> Tuple[Optional[Register], int]:
    """Fuzzy-match the register string against the catalog by keyword score."""
    t = text.lower()
    best, score = None, 0
    for reg in REGISTERS:
        s = sum(2 for k in reg.keywords if k in t)
        if s > score:
            best, score = reg, s
    return best, score
# ── translation engine ─────────────────────────────────────────────

def assemble_braid(ops: List[str]) -> str:
    """Braid word from the braid tokens: AFWD → σ, AREV → σ⁻¹; CLINK composes
    the parts into one word. ∅ when no braid tokens are present."""
    parts, composed = [], False
    for op in ops:
        if op == "AFWD":
            parts.append("σ")
        elif op == "AREV":
            parts.append("σ⁻¹")
        elif op == "CLINK":
            composed = True
    if not parts:
        return "∅"
    return "·".join(parts) if composed else "".join(parts)

def translate(word: str, register_text: str, runtime_arg: str = "auto",
              llm_arg: Optional[str] = None, model_arg: Optional[str] = None,
              dry_run: bool = False) -> dict:
    """Full translation: parse → judge (real judge) → match register →
    per-token isomorphic processes → runtime plan. With --llm, the local
    llama.cpp model (or another provider) produces the per-token processes
    instead of / over the built-in tables."""
    ops = parse_word(word)
    glyphs = [GLYPHS[op] for op in ops]
    reg, score = match_register(register_text)
    generic = reg is None
    if generic:
        reg = QUQUART                       # template fallback (canonical table)
    runtime = reg.runtime if runtime_arg == "auto" else runtime_arg
    v, raw = judge(word)                    # the real judge, never re-implemented
    pr = pair_report(word)                  # pairing read from Vox, not stack-derived
    braidword = assemble_braid(ops)
    rows = []
    for i, (glyph, op) in enumerate(zip(glyphs, ops)):
        p = reg.ops.get(op)
        if p is None:
            rows.append({"i": i, "glyph": glyph, "opcode": op, "process": "?",
                         "concrete": f"no process for {op} in {reg.rid}",
                         "rationale": "", "command": "—", "exact": False, "source": "table"})
            continue
        process, concrete, rationale, cmd, exact = p
        cmd = cmd.replace("<braidword>", braidword).replace("<composed>", braidword)
        rows.append({"i": i, "glyph": glyph, "opcode": op, "process": process,
                     "concrete": concrete, "rationale": rationale, "command": cmd,
                     "exact": exact, "source": "table"})
    result = {"word": word, "ops": ops, "glyphs": glyphs, "reg": reg, "generic": generic,
              "register_text": register_text, "runtime": runtime, "verdict": v,
              "judge_raw": raw, "pairs": pr, "braidword": braidword, "rows": rows,
              "llm_meta": None, "llm_register": None}
    if llm_arg is not None or os.environ.get("IG_LLM", "").strip() == "1":
        prov = None if llm_arg in (None, "auto") else llm_arg
        try:
            provider, model, api_key = resolve_provider_model(prov, model_arg, None)
        except ValueError as e:
            result["llm_meta"] = {"provider": None, "model": None, "error": str(e)}
            return result
        if dry_run:
            _rows, meta = llm_translate(ops, glyphs, word, v, register_text, reg,
                                        generic, braidword, provider, model, dry_run=True)
            result["llm_meta"] = meta
        else:
            _rows, meta = llm_translate(ops, glyphs, word, v, register_text, reg,
                                        generic, braidword, provider, model)
            result["llm_meta"] = meta
            if _rows is not None:
                result["rows"] = _rows
                if meta.get("register"):
                    result["llm_register"] = meta["register"]
    return result

# ── rendering ──────────────────────────────────────────────────────

VERDICT_LABEL = {"T": "T (closes)", "B": "B (open / paradox held)",
                 "N": "N (identity / no fork)", "F": "F (ill-typed)"}

def render(r: dict, emit: bool = False) -> str:
    reg, rt = r["reg"], RUNTIMES[r["runtime"]]
    L = []
    W = "═" * 78
    L.append(W)
    L.append("EXCRIBE-VOX — word → register realization")
    L.append(W)
    L.append(f"Word:      {r['word']}   ({len(r['ops'])} tokens, canonical)")
    lr = r.get("llm_register")
    if lr:
        L.append(f"Register:  synthesized — {lr['name']}")
        L.append(f"            {lr['dim']}")
    else:
        L.append(f"Register:  {reg.rid} — {reg.name}")
        L.append(f"            {reg.dim}")
    L.append(f"Runtime:   {rt['name']}")
    lm = r.get("llm_meta")
    if lm:
        if lm.get("dry_run"):
            L.append(f"Translator: DRY-RUN — {lm.get('provider')}/{lm.get('model')} (prompt shown, nothing called)")
        elif lm.get("error"):
            L.append(f"Translator: LLM unavailable ({lm['error']}) — canonical table used")
        else:
            L.append(f"Translator: LLM {lm.get('provider')}/{lm.get('model')}   [local model when provider=local]")
    v = r["verdict"]
    L.append(f"Judge:     vox verdict = {VERDICT_LABEL.get(v, 'UNJUDGED')}   [real judge]")
    if r["generic"]:
        if r.get("llm_register"):
            L.append(f"NOTE:      no built-in match for {r['register_text']!r} — register synthesized by the LLM")
        else:
            L.append(f"NOTE:      no registered match for {r['register_text']!r} — "
                     f"using the {reg.rid} template; the register text is carried as-is")
    if r["braidword"] != "∅":
        L.append(f"Braid:     {r['braidword']}   (assembled from AFWD / AREV / CLINK)")
    if r["pairs"]:
        L.append("Pairs:     " + " / ".join(r["pairs"].splitlines()[:6]))
    L.append("─" * 78)
    L.append(f"{'idx':>3}  {'mark':<4} {'opcode':<8} {'isomorphic process':<26} concrete operation")
    for row in r["rows"]:
        srcmark = " ◆llm" if row.get("source") == "llm" else ""
        L.append(f"{row['i']:>3}  {row['glyph']:<4} {row['opcode']:<8} "
                 f"{row['process']:<26} {row['concrete']}{srcmark}")
    L.append("─" * 78)
    L.append("ISOMORPHISM RATIONALE (token → register)")
    for row in r["rows"]:
        if row["rationale"]:
            L.append(f"  {row['i']:>2}  {row['glyph']} {row['opcode']:<7} {row['rationale']}")
    L.append("─" * 78)
    L.append("REALIZATION PLAN (ordered operations)")
    short = rt["name"].split(" (")[0]
    for n, row in enumerate(r["rows"], 1):
        mark = "✓ exact" if row["exact"] else "lane"
        L.append(f"  {n:2}. [{row['glyph']} {row['opcode']:<7}] {short}: {row['command']}   ({mark})")
    if emit:
        L.append("─" * 78)
        L.append(f"EMIT — runtime script ({r['runtime']})")
        seen = []
        for row in r["rows"]:
            if row["command"] != "—" and row["command"] not in seen:
                seen.append(row["command"])
        for c in seen:
            L.append(f"  {short}> {c}")
    if r.get("llm_meta", {}).get("dry_run"):
        L.append("─" * 78)
        L.append("LLM PROMPT (dry-run — nothing was called)")
        L.append(f"  system:")
        for ln in r["llm_meta"]["system"].splitlines() or [r["llm_meta"]["system"]]:
            L.append(f"    {ln}")
        L.append(f"  prompt:")
        for ln in r["llm_meta"]["prompt"].splitlines():
            L.append(f"    {ln}")
    L.append(W)
    L.append(f"Register lanes [{r['runtime']}] (real command surface):")
    for lane, cmds in rt["lanes"].items():
        L.append(f"  {lane:<10} {cmds}")
    return "\n".join(L)

# ── CLI ────────────────────────────────────────────────────────────

def main():
    ap = argparse.ArgumentParser(
        description="EXCRIBE-VOX — IMASM word → exact isomorphic processes in a target register")
    ap.add_argument("word", nargs="?", help="IMASM word (canonical twelve marks or opcode names)")
    ap.add_argument("register", nargs="?", help="target register, e.g. 'anyonic ququart computation'")
    ap.add_argument("--runtime", default="auto",
                    choices=["auto", "gmonados", "vox", "imas", "native", "para"])
    ap.add_argument("--emit", action="store_true", help="emit the runtime command script")
    ap.add_argument("--json", action="store_true", help="JSON output")
    ap.add_argument("--list-registers", action="store_true", help="list the register catalog")
    ap.add_argument("--llm", nargs="?", const="auto", default=None, metavar="PROVIDER",
                    help="translate tokens via the LLM. Provider chain (excriber_v3 style): "
                         "local (llama.cpp server @ 127.0.0.1:8000, the model you are) → "
                         "openrouter → deepseek. Pass a provider name to force one. "
                         "Also on when IG_LLM=1.")
    ap.add_argument("--model", help="model slug override (or IG_MODEL env)")
    ap.add_argument("--api-key", help="API key override (the local server needs none)")
    ap.add_argument("--dry-run", action="store_true",
                    help="print the exact LLM system+prompt without calling the model")
    args = ap.parse_args()

    if args.list_registers:
        for reg in REGISTERS:
            print(f"  {reg.rid:<10} {reg.name:<42} runtime={reg.runtime}")
            print(f"             {reg.dim}")
            print(f"             kw: {', '.join(reg.keywords)}\n")
        return

    if not args.word or not args.register:
        ap.error("word and register are required (or --list-registers)")

    try:
        r = translate(args.word, args.register, args.runtime,
                            args.llm, args.model, args.dry_run)
    except ValueError as e:
        print(f"PARSE ERROR: {e}", file=sys.stderr)
        sys.exit(2)

    if args.json:
        out = {k: v for k, v in r.items() if k != "reg"}
        out["register"] = {"rid": r["reg"].rid, "name": r["reg"].name, "dim": r["reg"].dim}
        out["llm_meta"] = r["llm_meta"]
        if r.get("llm_register"):
            out["llm_register"] = r["llm_register"]
        print(json.dumps(out, indent=2, ensure_ascii=False))
    else:
        print(render(r, emit=args.emit))

if __name__ == "__main__":
    main()
