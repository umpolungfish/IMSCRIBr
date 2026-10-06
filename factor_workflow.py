"""Prepare, run and independently verify an existing source-baked membrane."""
import copy
import hashlib
import json
import os
from pathlib import Path
import signal
import subprocess
import sys
import time

ROOT = Path(__file__).resolve().parent.parent
KERNEL = ROOT / "G-mOMonadOS"
OPERATOR = KERNEL / "target/release/ququart_prepare_operator"


def local_path(raw):
    path = Path(raw).expanduser().resolve()
    if not path.is_relative_to(ROOT):
        raise ValueError("factor artifacts must remain inside the local constellation")
    return path


def compile_factor(plan, ops, symbols):
    required = {"backend", "source", "base", "radix", "seed", "preparation", "steps", "prepare_seconds", "execute_seconds"}
    if set(plan) != required:
        raise ValueError("factor workflow needs source, base, radix, seed, preparation, per-symbol steps and budgets")
    for key in ("source", "base", "radix", "seed"):
        if not isinstance(plan[key], str) or not plan[key].isascii() or not plan[key].isdecimal():
            raise ValueError(f"factor {key} must be a decimal natural for preparation")
    if int(plan["source"]).bit_length() < 128 or not 1 < int(plan["base"]) < int(plan["source"]):
        raise ValueError("factor source needs at least 128 bits and a nontrivial modular base")
    radix = int(plan["radix"])
    if radix < 2 or radix & (radix - 1):
        raise ValueError("factor work radix must be a power of two")
    if int(plan["seed"]) >= 2**64:
        raise ValueError("factor entropy seed must fit the native preparation register")
    for key in ("prepare_seconds", "execute_seconds"):
        if type(plan[key]) is not int or not 1 <= plan[key] <= 86400:
            raise ValueError(f"{key} must be a positive bound up to one day")
    preparation = plan["preparation"]
    if not isinstance(preparation, dict) or preparation.get("mode") not in {"fresh", "compiled", "retained"}:
        raise ValueError("factor preparation must be fresh, compiled or retained")
    keys = {"mode"} if preparation["mode"] == "fresh" else {"mode", "path"}
    if set(preparation) != keys:
        raise ValueError("factor preparation has missing or unexpected bindings")
    if "path" in preparation:
        if not isinstance(preparation["path"], str) or not preparation["path"].strip():
            raise ValueError("factor preparation requires a concrete artifact path")
        artifact = local_path(preparation["path"])
        if not (artifact.is_file() if preparation["mode"] == "compiled" else artifact.is_dir()):
            raise ValueError("requested retained factor artifact does not exist")
    if not isinstance(ops, list) or not ops or ops[0] != "VINIT" or ops[-1] != "TANCH":
        raise ValueError("factor workflow needs source and terminal boundaries")
    steps = plan["steps"]
    if not isinstance(steps, list) or len(steps) != len(ops):
        raise ValueError("factor morphisms must cover every position once")
    schema = {"bind": set(), "retain": set(), "prepare": set(), "extract": set(),
              "link": set(), "return": set(), "release": set(), "split": {"id"},
              "rejoin": {"id"}, "latch": {"id"}, "engage": {"proposition"},
              "evidence": {"proposition", "axis", "witness"}}
    principal = {"⊢": {"bind"}, "⊙": {"retain"}, "∈": {"split"}, "∋": {"rejoin"},
                 "≻": {"prepare", "extract"}, "≺": {"return"}, "⋈": {"link"},
                 "⊤": {"evidence"}, "⊥": {"evidence"}, "⊞": {"engage"},
                 "⊡": {"latch"}, "⊣": {"release"}}
    frames, inverses, evidence, latches = [], [], set(), set()
    phase = "unit"
    boundaries = []
    for i, (step, op) in enumerate(zip(steps, ops)):
        symbol = symbols.get(op)
        if (symbol not in principal or not isinstance(step, dict) or set(step) != {"i", "symbol", "actions"} or
                type(step["i"]) is not int or step["i"] != i or step["symbol"] != symbol or
                not isinstance(step["actions"], list) or not step["actions"]):
            raise ValueError(f"factor position {i} requires its symbol and executable morphism")
        before = phase
        for action in step["actions"]:
            if not isinstance(action, dict) or not isinstance(action.get("kind"), str):
                raise ValueError("factor morphism must name a bound operation")
            kind = action["kind"]
            if kind not in schema or set(action) != {"kind"} | schema[kind] or kind not in principal[symbol]:
                raise ValueError(f"{symbol} does not realize the proposed {kind} morphism")
            for key in schema[kind]:
                if not isinstance(action[key], str) or not action[key].strip():
                    raise ValueError(f"{kind} requires a concrete {key}")
            if phase in {"latched", "released"} and kind != "release":
                raise ValueError("a fixed factor carrier admits only terminal release")
            if kind == "bind":
                if i != 0 or phase != "unit":
                    raise ValueError("source binding must initialize the carrier once")
                phase = "bound"
            elif kind == "prepare":
                if phase != "bound":
                    raise ValueError("preparation consumes a source-bound carrier")
                inverses.append(phase)
                phase = "prepared"
            elif kind == "extract":
                if phase != "prepared":
                    raise ValueError("extraction consumes a validated prepared carrier")
                inverses.append(phase)
                phase = "readout"
            elif kind == "return":
                if not inverses:
                    raise ValueError("return needs a retained forward carrier")
                phase = inverses.pop()
            elif kind == "split":
                if action["id"] in frames:
                    raise ValueError("duplicate open factor frame")
                frames.append(action["id"])
            elif kind == "rejoin":
                if not frames or frames.pop() != action["id"]:
                    raise ValueError("factor rejoin must consume the retained inner frame")
            elif kind == "link" and phase not in {"prepared", "readout"}:
                raise ValueError("link needs a prepared operator and its modular work")
            elif kind == "evidence":
                axis = "support" if symbol == "⊤" else "refutation"
                if action["axis"] != axis or not any(s["symbol"] == "≻" and any(a["kind"] == "extract" for a in s["actions"]) for s in steps[:i]):
                    raise ValueError("factor evidence requires an extracted readout and the symbol's evidence axis")
                evidence.add((action["proposition"], axis))
            elif kind == "engage":
                if any((action["proposition"], axis) not in evidence for axis in ("support", "refutation")):
                    raise ValueError("factor engagement needs both evaluated evidence coordinates")
            elif kind == "latch":
                if frames or not evidence or action["id"] in latches:
                    raise ValueError("factor fixation needs rejoined frames and evaluated evidence")
                latches.add(action["id"])
                phase = "latched"
            elif kind == "release":
                if frames or phase != "latched" or i != len(steps) - 1:
                    raise ValueError("factor release needs a fixed, rejoined carrier at the terminal boundary")
                phase = "released"
        boundaries.append({"i": i, "symbol": symbol, "domain": before, "codomain": phase})
    if phase != "released":
        raise ValueError("factor composition lacks a terminal release")
    return {"status": "ready", "plan": plan, "word_ops": ops,
            "symbol_word": "".join(symbols[op] for op in ops), "boundaries": boundaries,
            "carrier_kind": "source-bound preparation/readout/evidence carrier",
            "transport": "source-baked-workflow"}


def logged(argv, destination, name, seconds):
    """Capture real instrument output; terminate the owned group on timeout."""
    stdout = destination / f"{name}.stdout"
    stderr = destination / f"{name}.stderr"
    started = time.monotonic()
    with stdout.open("x") as out, stderr.open("x") as err:
        proc = subprocess.Popen(argv, cwd=KERNEL, stdout=out, stderr=err,
                                env=dict(os.environ, CARGO_NET_OFFLINE="true"), start_new_session=True)
        try:
            returncode = proc.wait(timeout=seconds)
            timed_out = False
        except subprocess.TimeoutExpired:
            try:
                os.killpg(proc.pid, signal.SIGTERM)
            except ProcessLookupError:
                pass
            try:
                proc.wait(timeout=5)
            except subprocess.TimeoutExpired:
                try:
                    os.killpg(proc.pid, signal.SIGKILL)
                except ProcessLookupError:
                    pass
                proc.wait()
            returncode, timed_out = proc.returncode, True
    return {"argv": list(map(str, argv)), "returncode": returncode, "timed_out": timed_out,
            "elapsed_seconds": time.monotonic() - started, "stdout": str(stdout), "stderr": str(stderr)}


def native_numerals(values):
    proc = subprocess.run([str(OPERATOR), "--numerals", *values], capture_output=True, text=True, check=True, timeout=30)
    return json.loads(proc.stdout)


def attest_case(case, source_word, base_word, radix_word, seed_word):
    manifest = json.loads((case / "manifest.json").read_text())
    prepared = json.loads((case / "prepared.json").read_text())
    if manifest.get("component") != "ququart_factor" or prepared.get("component") != "ququart_factor":
        raise ValueError("retained case is not a factor membrane")
    for filename, key in (("membrane", "sha256"), ("verify_readout", "verifier_sha256"), ("prepared.json", "prepared_sha256")):
        if hashlib.sha256((case / filename).read_bytes()).hexdigest() != manifest.get(key):
            raise ValueError(f"factor case {filename} differs from its manifest")
    if (prepared.get("source_word") != source_word or manifest.get("source_word") != source_word or
            prepared.get("binary_base_word") != base_word or manifest.get("binary_base_word") != base_word):
        raise ValueError("factor case source or binary modular base differs from requested preparation")
    if any(prepared.get(key) != word or manifest.get(key) != word
           for key, word in (("radix_word", radix_word), ("seed_word", seed_word))):
        raise ValueError("factor case radix or seed differs from requested preparation")
    if manifest.get("runtime_inputs") != []:
        raise ValueError("factor membrane must have no runtime source inputs")
    if (case / "prepared.json").read_bytes() not in (case / "membrane").read_bytes():
        raise ValueError("factor preparation is not embedded in its executable")
    return manifest, prepared


def execute_factor(compiled):
    try:
        return _execute_factor(compiled)
    except (OSError, subprocess.SubprocessError, ValueError, KeyError) as exc:
        raise ValueError(f"factor workflow failed; retained artifacts remain under measurements/factors: {exc}") from exc


def _execute_factor(compiled):
    plan = compiled["plan"]
    archive = Path(__file__).resolve().parent / "measurements/factors"
    archive.mkdir(parents=True, exist_ok=True)
    import uuid
    destination = archive / uuid.uuid4().hex
    destination.mkdir()
    (destination / "request.json").write_text(json.dumps(compiled, ensure_ascii=False, indent=2) + "\n")
    report = {"backend": "ququart-factor", "status": "preparing", "artifacts": str(destination), "events": [], "instruments": []}

    def record():
        (destination / "result.json").write_text(json.dumps(report, ensure_ascii=False, indent=2) + "\n")
        return report

    record()
    carrier = {"phase": "unit", "source": plan["source"], "active": {}, "evidence": {},
               "frames": [], "returns": [], "latches": {}, "links": []}
    execution, verification, fields = None, None, None
    invocations = {}

    def instrument(argv, name, seconds):
        invocations[name] = invocations.get(name, 0) + 1
        if invocations[name] > 1:
            name = f"{name}_{invocations[name]}"
        observation = logged(argv, destination, name, seconds)
        report["instruments"].append(observation)
        return observation

    def prepare():
        build = instrument(["cargo", "build", "--release", "--offline", "--bin", "ququart_prepare_operator",
                            "--bin", "ququart_verify_readout"], "tools", plan["prepare_seconds"])
        if build["returncode"]:
            raise ValueError("native preparation tools did not build")
        values = native_numerals([plan[k] for k in ("source", "base", "radix", "seed")] + ["0"])
        preparation = plan["preparation"]
        if preparation["mode"] == "retained":
            case = local_path(preparation["path"])
        else:
            count = invocations.get("preparation", 0)
            case = destination / ("case" if count == 0 else f"case_{count + 1}")
            argv = [sys.executable, str(KERNEL / "prepare_ququart.py"), values[plan["source"]], str(case),
                    "--base", values[plan["base"]], "--radix", values[plan["radix"]],
                    "--seed", values[plan["seed"]], "--native-arm", values["0"], "--dynamic-work"]
            if preparation["mode"] == "compiled":
                argv.extend(["--compiled-report", str(local_path(preparation["path"]))])
            if instrument(argv, "preparation", plan["prepare_seconds"])["returncode"]:
                raise ValueError("source-bound membrane preparation did not complete")
        attest_case(case, values[plan["source"]], values[plan["base"]], values[plan["radix"]], values[plan["seed"]])
        if instrument([str(case / "verify_readout"), "--validate-prepared", str(case / "prepared.json")],
                      "prepared_validation", 120)["returncode"]:
            raise ValueError("native preparation validation failed")
        report.update(case=str(case), manifest_sha256=hashlib.sha256((case / "manifest.json").read_bytes()).hexdigest(),
                      source_word=values[plan["source"]])
        return {"case": str(case), "manifest_sha256": report["manifest_sha256"], "source_word": values[plan["source"]]}

    def evaluate():
        nonlocal verification, fields
        if verification is None:
            case = Path(report["case"])
            verification = instrument([str(case / "verify_readout"), str(case / "prepared.json"), execution["stdout"]],
                                      "verification", 120)
            if verification["returncode"] == 0:
                lines = Path(execution["stdout"]).read_text().splitlines()
                fields = dict(line.split("=", 1) for line in lines[1:])
        return verification["returncode"] == 0

    def snapshot():
        return copy.deepcopy(carrier)

    for step, boundary in zip(plan["steps"], compiled["boundaries"]):
        for action_index, action in enumerate(step["actions"]):
            kind = action["kind"]
            before = snapshot()
            event = {"i": step["i"], "symbol": step["symbol"], "action_index": action_index,
                     "kind": kind, "domain": before["phase"], "status": "completed", "before": before}
            report["active_morphism"] = {"i": step["i"], "symbol": step["symbol"], "kind": kind}
            record()
            try:
                if kind == "bind":
                    vox = os.environ.get("EXCRIBE_VOX_BIN", str(ROOT / "Vox/target/release/vox"))
                    if instrument([vox, "verdict", compiled["symbol_word"]], "word_reading", 30)["returncode"]:
                        raise ValueError("Vox word reading failed")
                    carrier["phase"] = "bound"
                    carrier["active"] = {k: plan[k] for k in ("source", "base", "radix", "seed")}
                elif kind == "retain":
                    pass
                elif kind == "split":
                    carrier["frames"].append({"id": action["id"], "source": carrier["source"],
                                              "active": copy.deepcopy(carrier["active"]),
                                              "evidence": copy.deepcopy(carrier["evidence"])})
                elif kind in {"prepare", "extract"}:
                    carrier["returns"].append({"phase": carrier["phase"], "active": copy.deepcopy(carrier["active"])})
                    if kind == "prepare":
                        carrier["active"] = prepare()
                        carrier["phase"] = "prepared"
                    else:
                        verification, fields = None, None
                        report["status"] = "extracting"
                        execution = instrument([str(Path(report["case"]) / "membrane")], "execution", plan["execute_seconds"])
                        carrier["active"] = {**carrier["active"], "readout": execution["stdout"],
                                               "readout_sha256": hashlib.sha256(Path(execution["stdout"]).read_bytes()).hexdigest(),
                                               "returncode": execution["returncode"], "timed_out": execution["timed_out"]}
                        carrier["phase"] = "readout"
                        if execution["returncode"] or execution["timed_out"]:
                            event["status"] = "unclosed"
                elif kind == "link":
                    case = Path(report["case"])
                    prepared = json.loads((case / "prepared.json").read_text())
                    carrier["links"].append({"source_word": prepared["source_word"],
                                              "binary_base_word": prepared["binary_base_word"],
                                              "prepared_sha256": hashlib.sha256((case / "prepared.json").read_bytes()).hexdigest()})
                elif kind == "evidence":
                    accepted = evaluate()
                    observation = {"accepted": accepted if action["axis"] == "support" else not accepted,
                                   "predicate": "terminal_producer_and_product_verified" if action["axis"] == "support"
                                   else "terminal_producer_or_product_unverified",
                                   "witness": action["witness"], "instrument": verification}
                    carrier["evidence"].setdefault(action["proposition"], {}).setdefault(action["axis"], []).append(observation)
                    event["observation"] = observation
                elif kind == "rejoin":
                    frame = carrier["frames"].pop()
                    if frame["id"] != action["id"] or frame["source"] != carrier["source"]:
                        raise ValueError("factor frame source binding changed")
                    event["source_return"] = {"source_binding_equal": True, "frame": frame["id"],
                                              "metric": "preparation_source_binding", "coherent_amplitude_return": "not_measured_here"}
                    # Evidence is carried monotonically and remains attributed to its readout.
                elif kind == "return":
                    retained = carrier["returns"].pop()
                    carrier["active"] = retained["active"]
                    carrier["phase"] = retained["phase"]
                    event["coordinate_return"] = {"active_carrier_equal": carrier["active"] == retained["active"],
                                                  "metric": "retained_preparation_cursor", "coherent_inverse": "not_this_operation"}
                elif kind == "engage":
                    event["evidence"] = copy.deepcopy(carrier["evidence"][action["proposition"]])
                elif kind == "latch":
                    carrier["latches"][action["id"]] = {"source": carrier["source"], "active": copy.deepcopy(carrier["active"]),
                                                        "evidence": copy.deepcopy(carrier["evidence"])}
                    carrier["phase"] = "latched"
                elif kind == "release":
                    carrier["phase"] = "released"
                    if fields is not None:
                        def read_word(raw):
                            return subprocess.run([str(OPERATOR), "--read-numeral", raw], capture_output=True,
                                                  text=True, check=True, timeout=30).stdout.strip()
                        producer = read_word(fields["producing_arm_word"])
                        report.update(status="verified", product_verified=True, factor_words=[fields["p_word"], fields["q_word"]],
                                      factors=[read_word(fields["p_word"]), read_word(fields["q_word"])],
                                      producer="ququart_phase_with_sic_frame" if producer == "1" else "native_factor_arm",
                                      phase_samples=json.loads(fields["phase_samples"]), closure_word=fields["closure_word"])
                    else:
                        report.update(status="unclosed", product_verified=False, error="terminal verifier did not accept a factor pair")
                event.update(after=snapshot(), codomain=carrier["phase"])
                if carrier["phase"] != boundary["codomain"] and action_index == len(step["actions"]) - 1:
                    raise ValueError("factor morphism codomain differs from its compiled boundary")
            except (OSError, subprocess.SubprocessError, ValueError, KeyError) as exc:
                event.update(status="failed", error=str(exc), after=snapshot())
                report.update(status="preparation_failed" if kind in {"bind", "prepare"} else "execution_failed", error=str(exc))
                report["events"].append(event)
                report["carrier"] = snapshot()
                return record()
            report["events"].append(event)
            report["carrier"] = snapshot()
            record()
    report.pop("active_morphism", None)
    return record()
