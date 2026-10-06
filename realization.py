"""Closed, local realization adapters. Model output is data, never shell/code."""
import copy
import subprocess
from pathlib import Path

CATALOG = """realization must be a complete object using one of these adapters:
1. evidence: {backend:"evidence", frame:[unique proposition names],
   seed:{every frame name:[support_boolean,refutation_boolean]},
   steps:[{i:token_index,op:opcode,...}]}. Exactly one step per token.
   VINIT/TANCH/IMSCRIB/FSPLIT/FFUSE/IFIX/CLINK take no extra fields.
   AFWD takes permutation:[frame names] (a bijective coordinate relabeling).
   AREV reverses the most recent retained AFWD permutation.
   EVALT/EVALF take proposition:frame_name,witness:nonempty_source_identifier.
   ENGAGR takes proposition:frame_name,support:source_identifier,refutation:source_identifier.
   FSPLIT retains separate support/refutation arms and source; FFUSE rejoins
   those axes exactly. Deposits are monotone, so return witnesses explicitly
   distinguish coordinate reconstruction from source-state equality.
   This is a concrete FOUR evidence adapter, not a coherent quantum carrier.
2. anyon-ququart: {backend:"anyon-ququart",source:decimal_integer_string,
   steps:[{i:token_index,op:opcode,...}]}. Source must be at least 128 bits.
   Only VINIT,TANCH,IMSCRIB,AFWD,AREV are supported. AFWD takes
   generators:[nonzero signed integers of absolute value <=5]. AREV reverses
   the last AFWD in reversed order with signs negated. Initial carrier is T.
   One native sic-tool invocation retains all five amplitudes; terminal SIC
   measurement is destructive. It reports leakage, not a certified inverse residual.
If this target/word cannot be implemented by these adapters, return
realization:{backend:"unsupported",reason:nonempty explanation}. Never substitute
an evidence carrier for a requested quantum/chemical/physical carrier. Never
invent commands, missing bindings, arbitrary code, or unsupported operations."""

EVIDENCE_ACTIONS = {
    "VINIT": "Prepare the explicitly bound support/refutation seed in its proposition frame.",
    "TANCH": "Release the terminal evidence state and operation witnesses.",
    "IMSCRIB": "Retain the evidence state unchanged.",
    "FSPLIT": "Separate support and refutation axes; retain the full source snapshot.",
    "FFUSE": "Reconstruct the two evidence axes; compare coordinates and retained source separately.",
    "AFWD": "Relabel the proposition coordinates by the bound bijection and retain its inverse.",
    "AREV": "Apply the retained inverse of the last forward coordinate relabeling.",
    "EVALT": "Deposit support for the bound proposition with its supplied source identifier.",
    "EVALF": "Deposit refutation for the bound proposition with its supplied source identifier.",
    "ENGAGR": "Deposit both evidence coordinates with their separately bound source identifiers.",
    "IFIX": "Latch a copied state with the preceding operation witnesses retained.",
    "CLINK": "Compose the preceding ordered actions on their shared evidence carrier.",
}


def bound_description(compiled, i):
    """Executable boundaries take precedence over model prose."""
    step = compiled["plan"]["steps"][i]
    op = step["op"]
    if compiled["plan"]["backend"] == "evidence":
        event = compiled["events"][i]
        checks = {k: event[k] for k in ("coordinate_return", "source_return") if k in event}
        return {"process": op, "concrete": EVIDENCE_ACTIONS[op],
                "input": json_text(event["before"]), "output": json_text(event["after"]),
                "check": json_text(checks) if checks else "Validated typed adapter bindings; retain operation event."}
    event = compiled["events"][i]
    descriptions = {"VINIT": "Prepare native T basis state with source-bound precision.",
                    "TANCH": "Perform native destructive SIC measurement and report outside-carrier mass.",
                    "IMSCRIB": "Retain the resident five-channel carrier unchanged.",
                    "AFWD": "Apply ordered native Artin exchanges: ", "AREV": "Apply retained inverse exchanges: "}
    return {"process": op, "concrete": descriptions[op] + (json_text(event["generators"]) if "generators" in event else ""),
            "input": "native T preparation" if op == "VINIT" else "resident five-channel carrier",
            "output": "SIC terminal measurement" if op == "TANCH" else "resident five-channel carrier",
            "check": "Native operation errors propagate; terminal SIC/leakage witness retained. Inverse residual is not certified."}


def json_text(value):
    import json
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def compile_plan(plan, ops):
    if not isinstance(plan, dict):
        raise ValueError("missing typed realization object")
    backend = plan.get("backend")
    if backend == "unsupported":
        if set(plan) != {"backend", "reason"} or not isinstance(plan["reason"], str) or not plan["reason"].strip():
            raise ValueError("unsupported realization needs a reason")
        return {"status": "unsupported", **plan}
    keys = {"backend", "steps", "frame", "seed"} if backend == "evidence" else {"backend", "steps", "source"}
    if backend not in {"evidence", "anyon-ququart"} or set(plan) != keys:
        raise ValueError("unknown adapter or unexpected realization fields")
    steps = plan["steps"]
    if not isinstance(ops, list) or not ops or not isinstance(steps, list) or len(steps) != len(ops) or ops[0] != "VINIT" or ops[-1] != "TANCH":
        raise ValueError("realization requires source/terminal boundaries and exact token coverage")
    state, frames, inverses, events, exchanges = {}, [], [], [], []
    if backend == "evidence":
        frame = plan["frame"]
        if (not isinstance(frame, list) or not frame or
                any(not isinstance(p, str) or not p.strip() for p in frame) or len(set(frame)) != len(frame)):
            raise ValueError("evidence frame needs unique nonempty proposition names")
        seed = plan["seed"]
        if not isinstance(seed, dict) or set(seed) != set(frame) or any(
                not isinstance(v, list) or len(v) != 2 or any(type(b) is not bool for b in v) for v in seed.values()):
            raise ValueError("seed must bind both Boolean evidence coordinates for every proposition")
        state = copy.deepcopy(seed)
    else:
        source = plan["source"]
        if not isinstance(source, str) or not source.isascii() or not source.isdecimal() or int(source).bit_length() < 128:
            raise ValueError("native source must be a decimal integer of at least 128 bits")
    for i, (step, op) in enumerate(zip(steps, ops)):
        if op not in {"VINIT", "TANCH", "IMSCRIB", "FSPLIT", "FFUSE", "AFWD", "AREV", "EVALT", "EVALF", "ENGAGR", "IFIX", "CLINK"}:
            raise ValueError("foreign opcode in realization")
        if not isinstance(step, dict) or type(step.get("i")) is not int or step["i"] != i or step.get("op") != op:
            raise ValueError(f"realization token {i} has wrong index/opcode")
        extra = ({"permutation"} if op == "AFWD" else {"proposition", "witness"} if op in {"EVALT", "EVALF"}
                 else {"proposition", "support", "refutation"} if op == "ENGAGR" else set()) if backend == "evidence" else ({"generators"} if op == "AFWD" else set())
        if set(step) != {"i", "op"} | extra:
            raise ValueError(f"token {i} has missing or unexpected operation bindings")
        if op in {"VINIT", "TANCH"} and i not in {0, len(ops)-1}:
            raise ValueError("nested source/terminal boundary is unsupported")
        before = copy.deepcopy(state)
        if backend == "anyon-ququart":
            event = {"i": i, "op": op}
            if op not in {"VINIT", "TANCH", "IMSCRIB", "AFWD", "AREV"}:
                raise ValueError(f"native anyon adapter does not implement {op}")
            if op == "AFWD":
                generators = step["generators"]
                if not isinstance(generators, list) or not generators or any(type(g) is not int or not 1 <= abs(g) <= 5 for g in generators):
                    raise ValueError("Artin generators must be signed strand indices 1 through 5")
                exchanges.extend(generators)
                inverses.append([-g for g in reversed(generators)])
                event["generators"] = generators.copy()
            elif op == "AREV":
                if not inverses:
                    raise ValueError("AREV has no retained forward operation")
                event["generators"] = inverses.pop()
                exchanges.extend(event["generators"])
            events.append(event)
        else:
            if op == "FSPLIT":
                frames.append(copy.deepcopy(state))
            elif op == "FFUSE":
                if not frames:
                    raise ValueError("FFUSE has no retained split frame")
                source_state = frames.pop()
            elif op == "AFWD":
                permutation = step["permutation"]
                if not isinstance(permutation, list) or any(not isinstance(p, str) for p in permutation) or len(permutation) != len(frame) or set(permutation) != set(frame):
                    raise ValueError("forward relabeling must be a bijection of the retained frame")
                mapping = dict(zip(frame, permutation))
                state = {mapping[p]: v for p, v in state.items()}
                inverses.append({v: k for k, v in mapping.items()})
            elif op == "AREV":
                if not inverses:
                    raise ValueError("AREV has no retained forward operation")
                mapping = inverses.pop()
                state = {mapping[p]: v for p, v in state.items()}
            elif op in {"EVALT", "EVALF", "ENGAGR"}:
                p = step["proposition"]
                if not isinstance(p, str) or p not in state:
                    raise ValueError("evidence deposit refers to an unbound proposition")
                witnesses = [step[k] for k in ("support", "refutation") if op == "ENGAGR"] if op == "ENGAGR" else [step["witness"]]
                if any(not isinstance(w, str) or not w.strip() for w in witnesses):
                    raise ValueError("each evidence deposit requires source attribution")
                for axis in ([0, 1] if op == "ENGAGR" else [0 if op == "EVALT" else 1]):
                    state[p][axis] = True
            event = {"i": i, "op": op, "before": before, "after": copy.deepcopy(state)}
            if op == "FSPLIT":
                event["arms"] = [{p: v[axis] for p, v in state.items()} for axis in (0, 1)]
            if op == "IFIX":
                event["latched"] = copy.deepcopy(state)
            if op == "FFUSE":
                arms = [{p: v[axis] for p, v in state.items()} for axis in (0, 1)]
                reconstructed = {p: [arms[0][p], arms[1][p]] for p in frame}
                event.update(coordinate_return=reconstructed == state, source_return=state == source_state)
            if op in {"EVALT", "EVALF", "ENGAGR"}:
                event["bindings"] = {k: step[k] for k in extra}
            events.append(event)
    if frames:
        raise ValueError("realization leaves an open evidence frame")
    result = {"status": "ready", "plan": copy.deepcopy(plan), "word_ops": list(ops), "events": events}
    if backend == "evidence":
        result.update(events=events, final=state, source_return=state == plan["seed"])
    else:
        binary = Path(__file__).resolve().parent.parent / "G-mOMonadOS/target/release/sic-tool"
        result["argv"] = [str(binary), "anyon-ququart", plan["source"], *map(str, exchanges)]
    return result


def execute_plan(compiled):
    # Recompile the source object: never trust stored/generated argv or witnesses.
    checked = compile_plan(compiled["plan"], compiled["word_ops"])
    if checked["plan"]["backend"] == "evidence":
        return {"backend": "evidence", "events": checked["events"], "final": checked["final"],
                "source_return": checked["source_return"]}
    proc = subprocess.run(checked["argv"], capture_output=True, text=True, timeout=120)
    if proc.returncode:
        raise ValueError(f"native realization failed ({proc.returncode}): {proc.stderr.strip()}")
    if "outside-carrier mass" not in proc.stdout or "SIC" not in proc.stdout:
        raise ValueError("native realization omitted its SIC/leakage witness")
    return {"backend": "anyon-ququart", "argv": checked["argv"], "stdout": proc.stdout,
            "stderr": proc.stderr, "returncode": proc.returncode,
            "inverse_residual_verified": False}
