"""Bind and execute the native five-stage semiprime descent register."""
import copy
import json
from pathlib import Path
import subprocess

ROOT = Path(__file__).resolve().parent.parent
BINARY = ROOT / "Vox/target/release/semiprime_descent"
DESCENT = "∈⊤⊥⊞∋"
KINDS = {"⊢": "bind_source", "⊙": "retain_source", "∈": "cyclic_split",
         "⊤": "square_congruence", "⊥": "gcd_severing", "⊞": "knowledge_join",
         "∋": "verify_and_fuse", "≻": "advance_verified_pair", "⋈": "link_product_witness",
         "≺": "return_source", "⊡": "latch_pair", "⊣": "release_pair"}


def compile_descent(plan, ops, symbols):
    required = {"backend", "source", "seed", "constant", "attempts", "steps_per_attempt", "total_steps", "steps"}
    if not isinstance(plan, dict) or set(plan) != required:
        raise ValueError("descent needs source, cyclic parameters, iteration budgets and indexed stages")
    for key in ("source", "seed", "constant"):
        value = plan[key]
        if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
            raise ValueError(f"descent {key} must be a decimal natural")
    if int(plan["source"]) < 2:
        raise ValueError("descent source must be at least two")
    for key in ("attempts", "steps_per_attempt", "total_steps"):
        if type(plan[key]) is not int or not 1 <= plan[key] < 2**64:
            raise ValueError(f"descent {key} must be a positive native iteration budget")
    if not isinstance(ops, list) or not ops or any(op not in symbols for op in ops):
        raise ValueError("descent needs canonical operator positions")
    word = "".join(symbols[op] for op in ops)
    if word.count(DESCENT) != 1:
        raise ValueError("descent needs one ordered ∈⊤⊥⊞∋ region")
    start = word.index(DESCENT)
    if any(g not in "⊢⊙" for g in word[:start]) or any(g not in "≻⋈≺⊡⊣" for g in word[start + 5:]):
        raise ValueError("this register binds initialization before descent and sealing after it")
    steps = [{"i": i, "symbol": g, "actions": [{"kind": KINDS[g]}]} for i, g in enumerate(word)]
    if plan["steps"] != "register-bound" and plan["steps"] != steps:
        raise ValueError("descent stages must exactly bind each symbol's native operation")
    checked = copy.deepcopy(plan)
    checked["steps"] = steps
    argv = [str(BINARY), plan["source"], "--word", word, "--seed", plan["seed"],
            "--constant", plan["constant"], "--attempts", str(plan["attempts"]),
            "--steps", str(plan["steps_per_attempt"]), "--total-steps", str(plan["total_steps"])]
    return {"status": "ready", "plan": checked, "word_ops": list(ops),
            "symbol_word": word, "argv": argv, "transport": "native-descent"}


def execute_descent(compiled):
    proc = subprocess.run(compiled["argv"], capture_output=True, text=True, timeout=120)
    if proc.returncode not in {0, 1}:
        raise ValueError(f"native descent failed ({proc.returncode}): {proc.stderr.strip()}")
    try:
        report = json.loads(proc.stdout)
    except ValueError as exc:
        raise ValueError("native descent omitted its JSON trace") from exc
    if (report.get("backend") != "semiprime-descent" or report.get("word") != compiled["symbol_word"] or
            report.get("source") != str(int(compiled["plan"]["source"])) or not report.get("events") or
            (proc.returncode == 0) != (report.get("status") == "verified")):
        raise ValueError("native descent omitted source binding, stages or execution status")
    report["returncode"] = proc.returncode
    return report
