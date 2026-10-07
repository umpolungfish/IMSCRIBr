"""Bind and execute the native five-stage semiprime descent register."""
import copy
import json
from pathlib import Path
import subprocess
import tempfile

ROOT = Path(__file__).resolve().parent.parent
BINARY = ROOT / "Vox/target/release/semiprime_descent"
DESCENT = "∈⊤⊥⊞∋"
KINDS = {"⊢": "bind_source", "⊙": "retain_source", "∈": "cyclic_split",
         "⊤": "square_congruence", "⊥": "gcd_severing", "⊞": "knowledge_join",
         "∋": "verify_and_fuse", "≻": "advance_verified_pair", "⋈": "link_product_witness",
         "≺": "return_source", "⊡": "latch_pair", "⊣": "release_pair"}


def compile_descent(plan, ops, symbols):
    required = {"backend", "source", "seed", "constant", "attempts", "steps_per_attempt", "total_steps", "steps"}
    if not isinstance(plan, dict) or set(plan) not in (required, required | {"search_mode"}):
        raise ValueError("descent needs source, cyclic parameters, iteration budgets and indexed stages")
    mode = plan.get("search_mode", "bounded")
    if mode not in {"bounded", "until-closed"}:
        raise ValueError("descent search_mode must be bounded or until-closed")
    for key in ("source", "seed", "constant"):
        value = plan[key]
        if not isinstance(value, str) or not value.isascii() or not value.isdecimal():
            raise ValueError(f"descent {key} must be a decimal natural")
    if (plan["source"].lstrip("0") or "0") in {"0", "1"}:
        raise ValueError("descent source must be at least two")
    for key in ("attempts", "steps_per_attempt", "total_steps"):
        if type(plan[key]) is not int or not 1 <= plan[key] < 2**64:
            raise ValueError(f"descent {key} must be a positive native iteration budget")
    if mode == "until-closed" and plan["steps_per_attempt"] < 2:
        raise ValueError("until-closed requires at least two steps per attempt")
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
            "--constant", plan["constant"], "--steps", str(plan["steps_per_attempt"])]
    if mode == "until-closed":
        argv.append("--until-closed")
    else:
        argv.extend(["--attempts", str(plan["attempts"]), "--total-steps", str(plan["total_steps"])])
    return {"status": "ready", "plan": checked, "word_ops": list(ops),
            "symbol_word": word, "argv": argv, "transport": "native-descent"}


def execute_descent(compiled):
    if compiled["plan"].get("search_mode") == "until-closed":
        return execute_until_closed(compiled)
    proc = subprocess.run(compiled["argv"], capture_output=True, text=True, timeout=120)
    if proc.returncode not in {0, 1}:
        raise ValueError(f"native descent failed ({proc.returncode}): {proc.stderr.strip()}")
    try:
        report = json.loads(proc.stdout)
    except ValueError as exc:
        raise ValueError("native descent omitted its JSON trace") from exc
    if (report.get("backend") != "semiprime-descent" or report.get("word") != compiled["symbol_word"] or
            report.get("source") != (compiled["plan"]["source"].lstrip("0") or "0") or not report.get("events") or
            (proc.returncode == 0) != (report.get("status") == "verified")):
        raise ValueError("native descent omitted source binding, stages or execution status")
    report["returncode"] = proc.returncode
    return report


def execute_until_closed(compiled):
    """Stream attempt history to disk; no whole-search timeout or memory buffer."""
    directory = Path(__file__).resolve().parent / "measurements" / "descent"
    directory.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryFile(mode="w+t", dir=directory) as errors, tempfile.NamedTemporaryFile(
            mode="w", prefix="attempts_", suffix=".jsonl", dir=directory, delete=False) as trace:
        proc = subprocess.Popen(compiled["argv"], stdout=subprocess.PIPE, stderr=errors, text=True)
        final = None
        try:
            for line in proc.stdout:
                trace.write(line)
                trace.flush()
                envelope = json.loads(line)
                report = envelope["attempt"]
                if (envelope.get("mode") != "until-closed" or
                        report.get("backend") != "semiprime-descent" or
                        report.get("word") != compiled["symbol_word"] or
                        report.get("source") != (compiled["plan"]["source"].lstrip("0") or "0")):
                    raise ValueError("complete descent stream lost source/stage binding")
                if envelope.get("status") == "verified":
                    if report.get("status") != "verified" or not report.get("factors"):
                        raise ValueError("complete descent omitted verified factors")
                    final = report | {"search_mode": "until-closed", "search_attempts": envelope["search_attempts"],
                                      "search_steps": envelope["search_steps"], "trace": trace.name}
            code = proc.wait()
            if code or final is None:
                errors.seek(0)
                raise ValueError(f"complete descent stopped without closure ({code}): {errors.read().strip()}")
            return final | {"returncode": code}
        finally:
            if proc.poll() is None:
                proc.terminate()
                proc.wait()
            proc.stdout.close()
