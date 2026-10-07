"""Register-bound numeral tape operators using the existing Vox arithmetic."""
import fcntl
import hashlib
import json
import os
from pathlib import Path
import shutil
import uuid

from factor_workflow import ROOT, logged

VOX = ROOT / "Vox"
KINDS = {"⊢": "open", "∈": "split", "⊤": "bit", "⊥": "bit", "≺": "clear",
         "∋": "rejoin", "≻": "advance", "⋈": "compose", "⊙": "retain",
         "⊡": "factor_latch", "⊣": "release"}


def compile_numeral(plan, ops, symbols):
    if set(plan) != {"backend", "source", "steps", "prepare_seconds", "execute_seconds"}:
        raise ValueError("numeral-factor needs source, per-symbol steps and preparation/extraction bounds")
    source = plan["source"]
    if not isinstance(source, str) or not source.isascii() or not source.isdecimal() or int(source).bit_length() < 128:
        raise ValueError("numeral factor source must be a decimal natural of at least 128 bits")
    for key in ("prepare_seconds", "execute_seconds"):
        if type(plan[key]) is not int or not 1 <= plan[key] <= 86400:
            raise ValueError("numeral factor budgets must lie between one second and one day")
    steps = plan["steps"]
    if steps == "register-bound":
        steps, frame_ids = [], []
        for i, op in enumerate(ops):
            symbol = symbols.get(op)
            if symbol not in KINDS:
                raise ValueError(f"missing numeral-factor primitive for {symbol} at position {i}; register-bound cannot invent it")
            kind = KINDS[symbol]
            action = {"kind": kind}
            if kind == "split":
                action["id"] = f"cell_{i}"
                frame_ids.append(action["id"])
            elif kind == "rejoin":
                if not frame_ids:
                    raise ValueError("numeral rejoin has no retained frame")
                action["id"] = frame_ids.pop()
            elif kind == "bit":
                action["value"] = 0 if symbol == "⊤" else 1
            steps.append({"i": i, "symbol": symbol, "actions": [action]})
        plan["steps"] = steps
    if (not ops or ops[0] != "VINIT" or ops[-1] != "TANCH" or
            not isinstance(steps, list) or len(steps) != len(ops)):
        raise ValueError("numeral morphisms require boundaries and exact position coverage")
    frames, seen, bits, fixed = [], set(), 0, False
    boundaries = []
    for i, (step, op) in enumerate(zip(steps, ops)):
        symbol = symbols.get(op)
        if (symbol not in KINDS or not isinstance(step, dict) or set(step) != {"i", "symbol", "actions"} or
                type(step["i"]) is not int or step["i"] != i or step["symbol"] != symbol or
                not isinstance(step["actions"], list) or len(step["actions"]) != 1):
            raise ValueError(f"position {i} needs its register-bound numeral operator")
        action = step["actions"][0]
        kind = KINDS[symbol]
        keys = {"kind", "value"} if kind == "bit" else {"kind", "id"} if kind in {"split", "rejoin"} else {"kind"}
        if not isinstance(action, dict) or set(action) != keys or action.get("kind") != kind:
            raise ValueError(f"{symbol} requires the numeral carrier's {kind} morphism")
        before = {"carrier": "native_numeral_tape", "cells": bits, "frames": list(frames), "fixed": fixed}
        if fixed and kind != "release":
            raise ValueError("fixed numeral admits only release")
        if kind == "open" and i != 0:
            raise ValueError("numeral source opens only once")
        if kind == "bit":
            value = 0 if symbol == "⊤" else 1
            if not frames or type(action["value"]) is not int or action["value"] != value:
                raise ValueError("numeral bit morphism needs its open cell frame and bound zero/one value")
            bits += 1
        elif kind in {"split", "rejoin"}:
            if not isinstance(action["id"], str) or not action["id"].strip():
                raise ValueError("numeral cell frame needs an identifier")
            if kind == "split":
                if action["id"] in seen:
                    raise ValueError("numeral cell frame identifiers must be unique")
                seen.add(action["id"])
                frames.append(action["id"])
            elif not frames or frames.pop() != action["id"]:
                raise ValueError("numeral rejoin consumes the retained inner cell frame")
        elif kind == "clear" and not frames:
            raise ValueError("numeral clearing needs a retained frame with banked cells")
        elif kind == "factor_latch":
            if frames or not bits:
                raise ValueError("factor latch needs a rejoined numeral tape")
            fixed = True
        elif kind == "release" and (not fixed or i != len(steps) - 1):
            raise ValueError("numeral release requires a fixed tape at the terminal boundary")
        after = {"carrier": "native_numeral_tape", "cells": bits, "frames": list(frames), "fixed": fixed}
        boundaries.append({"i": i, "symbol": symbol, "domain": before, "codomain": after})
    return {"status": "ready", "plan": plan, "word_ops": list(ops), "boundaries": boundaries,
            "symbol_word": "".join(symbols[op] for op in ops), "transport": "source-baked-numeral"}


def execute_numeral(compiled):
    plan = compiled["plan"]
    destination = Path(__file__).resolve().parent / "measurements/factors" / uuid.uuid4().hex
    destination.mkdir(parents=True)
    (destination / "request.json").write_text(json.dumps(compiled, ensure_ascii=False, indent=2) + "\n")
    report = {"backend": "numeral-factor", "status": "preparing", "artifacts": str(destination),
              "source": plan["source"], "events": [], "instruments": []}

    def record():
        (destination / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        return report

    def call(argv, name, seconds, env=None):
        result = logged(argv, destination, name, seconds, cwd=VOX, env=env)
        report["instruments"].append(result)
        return result

    def events(path):
        observed = []
        for line in Path(path).read_text().splitlines():
            parts = line.split("\t")
            if len(parts) == 3 and parts[0] == "started":
                i = int(parts[1])
                if i != len(observed) or parts[2] != plan["steps"][i]["symbol"]:
                    raise ValueError("native numeral execution order differs from the bound word")
                observed.append({"i": i, "symbol": parts[2], "kind": plan["steps"][i]["actions"][0]["kind"],
                                 "status": "unclosed"})
            elif len(parts) == 7 and parts[0] == "event":
                i = int(parts[1])
                step, boundary = plan["steps"][i], compiled["boundaries"][i]
                if i != len(observed) - 1 or parts[2] != step["symbol"]:
                    raise ValueError("native numeral event differs from bound symbol")
                observed[-1].update(status="completed", domain=boundary["domain"], codomain=boundary["codomain"],
                                    before=parts[3], after=parts[4],
                                    native_before_state=parts[5], native_after_state=parts[6],
                                    state_fields=["cells", "frames", "cursor", "linked_words", "fixed", "candidate_factors"])
        return observed

    record()
    try:
        env = dict(os.environ, CARGO_NET_OFFLINE="true", EXCRIBE_NUMERAL_WORD=compiled["symbol_word"],
                   EXCRIBE_NUMERAL_SOURCE=plan["source"])
        (VOX / "target").mkdir(exist_ok=True)
        with (VOX / "target/excribe-numeral-bake.lock").open("a") as lock:
            fcntl.flock(lock, fcntl.LOCK_EX)
            build = call(["cargo", "build", "--release", "--offline", "--bin", "excribe_numeral"],
                         "build", plan["prepare_seconds"], env)
            if build["returncode"]:
                report.update(status="preparation_failed", error="native numeral morphism executable did not build")
                return record()
            binary = destination / "membrane"
            shutil.copy2(VOX / "target/release/excribe_numeral", binary)
        report["executable_sha256"] = hashlib.sha256(binary.read_bytes()).hexdigest()
        inspection = call([str(binary), "--inspect", compiled["symbol_word"], plan["source"]], "source_binding", 60)
        report["preparation_events"] = events(inspection["stdout"])
        if inspection["returncode"]:
            report.update(status="source_binding_failed", error=Path(inspection["stderr"]).read_text().strip())
            return record()
        report["status"] = "extracting"
        record()
        execution = call([str(binary)], "execution", plan["execute_seconds"])
        report["events"] = events(execution["stdout"])
        if execution["returncode"]:
            report.update(status="unclosed", error="no completed native numeral factor extraction within the bound")
            return record()
        factors = [line.split("\t")[1:] for line in Path(execution["stdout"]).read_text().splitlines()
                   if line.startswith("factor\t")]
        if len(factors) < 2 or any(len(factor) != 2 for factor in factors):
            raise ValueError("native readout did not supply a nontrivial factor multiset")
        verification = call([str(binary), "--verify", *(factor[1] for factor in factors)], "verification", 120)
        if verification["returncode"]:
            report.update(status="verification_failed", error="independent native tape product/primality screening failed")
            return record()
        report.update(status="verified", product_verified=True, factors=[f[0] for f in factors],
                      factor_words=[f[1] for f in factors], primality="native_miller_rabin_screening",
                      producer="vox_native_tape_smart_factor")
        return record()
    except (OSError, ValueError, KeyError, IndexError) as exc:
        report.update(status="execution_failed", error=str(exc))
        return record()
