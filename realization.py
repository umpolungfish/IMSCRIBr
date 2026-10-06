"""Closed, local realization adapters. Model output is data, never shell/code."""
import copy
import subprocess
from pathlib import Path

SYMBOLS = dict(zip(("VINIT", "TANCH", "AFWD", "AREV", "CLINK", "IMSCRIB", "FSPLIT", "FFUSE", "EVALT", "EVALF", "ENGAGR", "IFIX"), "⊢⊣≻≺⋈⊙∈∋⊤⊥⊞⊡"))

CATALOG = """Synthesize a bound executable composition. Recognized motifs guide
lowering; a word is never required to stay bare because a whole-word adapter
is absent. Bind its positions to compositions of available carrier operations.
Keep phase, leakage, source snapshots, and attributed evidence distinct.
realization must use one of these schemas:
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
2. anyon-composition: {backend:"anyon-composition",source:decimal_integer_string,
   digit:0|1|2|3,steps:[{i:position,symbol:canonical_symbol,actions:[operation,...]}]}.
   Source must be at least 128 bits; digit binds native basis T,F,t,f respectively.
   Every position has a nonempty ordered composition of native operations.
   No whole-word or glyph allowlist restricts synthesis. Available operations:
   {kind:"retain"}: retain the resident coherent five-channel carrier.
   {kind:"exchange",generators:[signed nonzero strand indices 1..5]}:
     apply ordered physical Artin exchanges, retaining this batch and its source.
   {kind:"inverse"}: reverse/sign-negate the last retained exchange batch and
     measure its source-return residual in fixed-point units on all five channels.
   {kind:"split",id:string}: retain a named source snapshot, phase, leakage,
     and native sixteen SIC masses plus outside-carrier mass.
   {kind:"rejoin",id:string}: close the retained inner frame; evaluate native SIC
     dual reconstruction of current computational populations, retain coherent
     amplitudes separately, and measure all-five-channel source return.
     This is population synthesis with phase retained, not phase recovery from
     probabilities or destructive measurement followed by quantum inversion.
   {kind:"sic"}: non-destructive native analysis on the current carrier.
   {kind:"evidence",proposition:string,axis:"support"|"refutation",
     outcome:0..16,numerator:decimal_string,denominator:positive_decimal_string,
     witness:string}: evaluate an explicitly bound rational SIC-mass threshold
     and retain actual accepted/rejected observation and source attribution.
     Outcome 16 is outside carrier. Threshold lies between zero and one.
   {kind:"engage",proposition:string}: retain both previously evaluated evidence
     coordinates for that proposition; do not manufacture positive observations.
   {kind:"latch",id:string}: copy the coherent state and evidence under a unique id.
   Multiple operations may be composed at one symbol. Linking can bind an
   ordered exchange composition; nested split/return/rejoin motifs preserve
   one resident carrier. Bind evaluation policies from the user's description;
   missing material policies are unresolved bindings, not unsupported words.
   Terminal readout returns actual native witnesses without stochastic collapse.
Use anyon-composition for synthesized anyonic words, including split/rejoin,
evaluation, linking, engagement, and fixation. Do not infer that its symbols
are forbidden because a whole-word template has not been registered.
If a REQUIRED native primitive or material binding is genuinely absent, return
realization:{backend:"unsupported",reason:nonempty explanation naming that
primitive/binding and attempted composition}. Never substitute
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
    if compiled["plan"]["backend"] == "anyon-composition":
        return {"process": step["symbol"], "concrete": "Native ordered composition: " + json_text(step["actions"]),
                "input": "resident five-channel carrier with retained frames and attributed evidence",
                "output": "carrier and witnesses after the bound native composition",
                "check": "Execution pending: native source-return, SIC population synthesis, and evidence witnesses are measured during execution."}
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
    if backend == "anyon-composition":
        return compile_composition(plan, ops)
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


def compile_composition(plan, ops):
    if set(plan) != {"backend", "source", "digit", "steps"}:
        raise ValueError("composition needs source, basis digit, and ordered steps")
    source = plan["source"]
    if not isinstance(source, str) or not source.isascii() or not source.isdecimal() or int(source).bit_length() < 128:
        raise ValueError("native source must be a decimal integer of at least 128 bits")
    if type(plan["digit"]) is not int or not 0 <= plan["digit"] <= 3:
        raise ValueError("source basis digit must be 0 through 3")
    if (not isinstance(ops, list) or not ops or ops[0] != "VINIT" or ops[-1] != "TANCH" or
            not isinstance(plan["steps"], list) or len(plan["steps"]) != len(ops)):
        raise ValueError("composition needs source/terminal boundaries and exact coverage")
    schema = {"retain": set(), "sic": set(), "inverse": set(), "exchange": {"generators"},
              "split": {"id"}, "rejoin": {"id"}, "latch": {"id"}, "engage": {"proposition"},
              "evidence": {"proposition", "axis", "outcome", "numerator", "denominator", "witness"}}
    splits, returns, latches, evidence = [], 0, set(), set()
    for i, (step, op) in enumerate(zip(plan["steps"], ops)):
        if (not isinstance(step, dict) or set(step) != {"i", "symbol", "actions"} or
                type(step["i"]) is not int or step["i"] != i or step["symbol"] != SYMBOLS.get(op) or
                not isinstance(step["actions"], list) or not step["actions"]):
            raise ValueError(f"composition position {i} needs its symbol and ordered operations")
        for action in step["actions"]:
            if not isinstance(action, dict) or not isinstance(action.get("kind"), str):
                raise ValueError("native composition operation must name a primitive")
            kind = action["kind"]
            if kind not in schema or set(action) != {"kind"} | schema[kind]:
                raise ValueError(f"unknown primitive or incomplete bindings: {kind}")
            for key in schema[kind] - {"generators", "outcome"}:
                if not isinstance(action[key], str) or not action[key].strip():
                    raise ValueError(f"{kind} requires a concrete {key}")
            if kind == "exchange":
                gs = action["generators"]
                if not isinstance(gs, list) or not gs or any(type(g) is not int or not 1 <= abs(g) <= 5 for g in gs):
                    raise ValueError("exchange requires signed generators 1 through 5")
                returns += 1
            elif kind == "inverse":
                if not returns:
                    raise ValueError("inverse needs a retained exchange composition")
                returns -= 1
            elif kind == "split":
                if action["id"] in splits:
                    raise ValueError("duplicate open frame identifier")
                splits.append(action["id"])
            elif kind == "rejoin":
                if not splits or splits.pop() != action["id"]:
                    raise ValueError("rejoin must name the retained inner frame")
            elif kind == "latch":
                if action["id"] in latches:
                    raise ValueError("duplicate latch identifier")
                latches.add(action["id"])
            elif kind == "evidence":
                if action["axis"] not in {"support", "refutation"} or type(action["outcome"]) is not int or not 0 <= action["outcome"] <= 16:
                    raise ValueError("bind evidence axis and a native SIC outcome")
                for key in ("numerator", "denominator"):
                    if not action[key].isascii() or not action[key].isdecimal():
                        raise ValueError("evidence threshold must use decimal naturals")
                if not 0 <= int(action["numerator"]) <= int(action["denominator"]) or int(action["denominator"]) == 0:
                    raise ValueError("evidence threshold must lie between zero and one")
                evidence.add((action["proposition"], action["axis"]))
            elif kind == "engage":
                if any((action["proposition"], axis) not in evidence for axis in ("support", "refutation")):
                    raise ValueError("engagement requires both evaluated evidence coordinates")
    if splits:
        raise ValueError("composition leaves an unrejoined frame")
    binary = Path(__file__).resolve().parent.parent / "G-mOMonadOS/target/release/sic-tool"
    return {"status": "ready", "plan": copy.deepcopy(plan), "word_ops": list(ops),
            "argv": [str(binary), "anyon-program"], "transport": "stdin-json"}


def execute_plan(compiled):
    # Recompile the source object: never trust stored/generated argv or witnesses.
    checked = compile_plan(compiled["plan"], compiled["word_ops"])
    if checked["plan"]["backend"] == "anyon-composition":
        proc = subprocess.run(checked["argv"], input=json_text(checked["plan"]), capture_output=True, text=True, timeout=120)
        if proc.returncode:
            raise ValueError(f"native composition failed ({proc.returncode}): {proc.stderr.strip()}")
        import json
        report = json.loads(proc.stdout)
        if report.get("backend") != "anyon-composition" or not report.get("events") or "source_return" not in report:
            raise ValueError("native composition omitted execution witnesses")
        return report
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
