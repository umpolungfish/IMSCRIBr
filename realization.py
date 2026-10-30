"""Closed, local realization adapters. Model output is data, never shell/code."""
import copy
from descent_workflow import compile_descent, execute_descent
import subprocess
from pathlib import Path
from factor_workflow import compile_factor, execute_factor
from numeral_workflow import compile_numeral, execute_numeral

SYMBOLS = dict(zip(("VINIT", "TANCH", "AFWD", "AREV", "CLINK", "IMSCRIB", "FSPLIT", "FFUSE", "EVALT", "EVALF", "ENGAGR", "IFIX"), "⊢⊣≻≺⋈⊙∈∋⊤⊥⊞⊡"))

CATALOG = """Synthesize a bound executable composition. Recognized motifs guide
lowering; a word is never required to stay bare because a whole-word adapter
is absent. Bind its positions to compositions of available carrier operations.
Keep phase, leakage, source snapshots, and attributed evidence distinct.
Every symbol is an operator morphism. Its executable lowering must preserve
that operator's role and have a bound domain and codomain that compose with
its neighbors. A motif abbreviates such a composition; it never replaces
per-symbol operations or licenses identity at a working symbol.
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
3. ququart-factor: {backend:"ququart-factor",source:decimal_string,base:decimal_string,
   radix:decimal_power_of_two_string,seed:decimal_string,
   preparation:{mode:"fresh"}|{mode:"compiled",path:existing_compiler_report_path}|
               {mode:"retained",path:existing_case_directory},
   prepare_seconds:positive_integer,execute_seconds:positive_integer,
   steps:[{i:position,symbol:canonical_symbol,actions:[operation,...]}]}.
   Use this for actual factor extraction, not an exchange/evidence approximation.
   Exactly one bound step per symbol. This carrier consists of source-bound
   preparation artifacts, retained cursors/frames and attributed terminal evidence.
   No mandatory first or last glyph: without ⊢ the composition consumes the
   independently source-bound carrier; without ⊣ its output remains retained.
   Neither omission manufactures preparation, extraction, evidence or release.
   Its operations are actual workflow morphisms, not coherent Artin gates:
   ⊢ {kind:"bind"} initializes the source/base/radix/seed carrier.
   ≻ {kind:"prepare"} consumes bound source and produces a validated baked case;
      or {kind:"extract"} consumes prepared case and produces actual native readout.
      Multiple ordered actions can share one ≻: [prepare,extract] is valid and
      supplies a readout before the next evidence glyph. Later extraction can
      reuse the validated prepared case while retaining each forward cursor.
   ⊙ {kind:"retain"} is identity on the entire carrier.
   ∈ {kind:"split",id:string} retains a source/active/evidence frame.
   ∋ {kind:"rejoin",id:string} consumes the retained inner frame, checks source
      binding and carries the transformed active state and attributed evidence.
   ⋈ {kind:"link"} binds the baked Fourier/modular-work composition certificate.
   ⊤ {kind:"evidence",axis:"support",proposition:string,witness:string} evaluates
      the independent terminal producer/product verifier on the actual readout.
   ⊥ same evidence schema with axis:"refutation" evaluates failed verification.
   ≺ {kind:"return"} restores the retained forward preparation cursor, preserving
      terminal evidence. This is a workflow cursor return, NOT coherent inversion.
      A requested coherent inverse needs anyon-composition instead.
   ⊞ {kind:"engage",proposition:string} holds both already evaluated coordinates.
   ⊡ {kind:"latch",id:string} copies fixed carrier/evidence after all frames rejoin.
      The copied latch stays immutable; it does not freeze the separate active
      cursor. Returns and links may continue on that cursor before release.
   ⊣ {kind:"release"} releases the latch and verified factors at the terminal end.
      ⊙ may retain the released carrier as identity after release.
   Each operation is restricted to its indicated symbol. Typed carrier phases
   compose as unit -> bound -> prepared -> readout; return restores the last
   forward domain; fixation -> latched and terminal release -> released.
   Bind actual frame ids, evidence proposition and witness ids. No stage labels
   or narrative-only position coverage can substitute for these morphisms.
   Evidence here measures only the producer/product verifier. Renaming its
   proposition cannot turn it into a purity, braid residual or distribution-law
   measurement. Engage needs both evaluated axes for the same proposition;
   evaluation of both axes does not imply both were accepted or that evidence is B.
   The native preparation script emits canonical numeral words and bakes the
   source, radix-scaled modular base, physical Fourier operator and shared-work
   schedule into a new executable. The extraction binary has NO runtime source
   arguments. The independent verifier checks the actual producing arm, measured
   evidence, source binding and Gödel factor product. Current source has removed
   the classical native producer, so fresh preparations disable that arm and
   execute the ququart phase/SIC route. Never restore it or invent a period.
   No factor values or known order may enter this schema or preparation.
   Bind base=2,radix=4,seed=1729 unless the request chooses otherwise. Use fresh
   preparation if no actual compatible retained artifact was supplied. Bind
   stage budgets explicitly (e.g. prepare_seconds=1800,execute_seconds=120).
   An execution without a verified terminal pair is unclosed, never success.
4. numeral-factor: {backend:"numeral-factor",source:decimal_string,
   prepare_seconds:positive_integer,execute_seconds:positive_integer,
   steps:"register-bound"|[{i:position,symbol:canonical_symbol,actions:[operation]}]}.
   Use only for an explicitly requested numeral-codec target in the native numeral register.
   The IMASM operation word is the program; the source numeral is separately bound data.
   A factor request or Gödel-encoding relationship alone does not select this adapter
   or authorize interpreting program glyphs as source numeral bits.
   Supported operators act on a least-significant-cell-first native numeral tape:
   ⊢ {kind:"open"}; ∈ {kind:"split",id:string};
   ⊤ {kind:"bit",value:0}; ⊥ {kind:"bit",value:1};
   ≺ {kind:"clear"} clears the transient cursor while retaining deposited
      cells banked inside their open frame. It needs no Artin exchange batch.
   ∋ {kind:"rejoin",id:string}; ≻ {kind:"advance"};
   ⋈ {kind:"compose"}; ⊙ {kind:"retain"};
   ⊡ {kind:"factor_latch"} seals the reconstructed source and invokes existing
      Vox native tape factor extraction; ⊣ {kind:"release"} checks the tape
      product and native primality screening before releasing the factor multiset.
   steps:"register-bound" asks the compiler to supply these indexed morphisms
   deterministically, including paired frame identifiers. It does not skip them.
   This adapter currently has no ⊞ primitive. A word containing ⊞ needs an
   unresolved adapter binding, not an invented engagement action or a declaration
   that the Grammar glyph is forbidden. register-bound cannot bypass that gap.
   The input word is the operator composition to execute, not a list of claimed
   support/refutation observations. The source is independently bound from the
   request. Native preparation must reconstruct exactly that source from the
   deposited cells, then bake word and source into the executable. A mismatch is
   source_binding_failed, never repaired by altering the word or named source.
   ⊤/⊥ here deposit zero/one cells; they do not choose SIC outcomes or evidence
   thresholds. No prepare/extract ≻ symbols need to be inserted into a numeral.
   Use the existing Vox folded tape arithmetic and factor relation; source-baked
   runtime takes no input. Release only after a separate native tape verification.
   Native Miller-Rabin screening is identified as screening, not a primality proof.
   Never replace this request with anyon-composition or unrelated measurements.
5. semiprime-descent: {backend:"semiprime-descent",source:decimal_string,
   seed:decimal_string,constant:decimal_string,attempts:positive_integer,
   steps_per_attempt:positive_integer,total_steps:positive_integer,
   search_mode?:"bounded"|"until-closed",
   steps:"register-bound"|[{i:position,symbol:canonical_symbol,actions:[operation]}]}.
   This arithmetic register extracts inside ∈⊤⊥⊞∋. ∈ cyclic_split retains two
   slow/fast x²+c orbit states with a measured collision GCD; a repeated-image
   predecessor safeguard retains completeness. ⊤ square_congruence lifts a
   strict observed divisor into X,Y and checks their squares modulo the source.
   Odd N uses X=(g+N/g)/2,Y=|g-N/g|/2. Even N uses X=N/2+1,Y=N/2-1.
   ⊥ gcd_severing recomputes gcd(|X-Y|,N) on this verified square witness.
   ⊞ knowledge_join retains FOUR evidence across retries. ∋ verify_and_fuse
   divides N by the selected GCD and checks its exact Gödel/support-polynomial
   product. Both factors must be strictly between one and N.
   Source, seed and constant are native numeral tapes; no factors or unknown
   prime are supplied to cycle detection. A hidden factor collision is observed
   at the GCD stage. Failed attempts F and later success T remain joined as B;
   budget exhaustion without a completed observation deposits N.
   Optional surrounding operations: ⊢ bind_source, ⊙ retain_source before descent;
   ≻ advance_verified_pair, ⋈ link_product_witness, ≺ return_source,
   ⊡ latch_pair, ⊣ release_pair afterwards. These perform no extraction.
   Use steps:"register-bound" for exact lowering. Bounds are iteration budgets.
   Seed=2 and constant=1 give the default reproducible walk when unspecified.
   until-closed ignores attempt/total budgets, requires steps_per_attempt >= 2,
   enumerates all seed/constant residues and streams retained attempt traces.
   It has no total runtime/attempt cap. Semiprime closure is eventual; practical
   RSA runtime is not guaranteed. Bounded mode remains an explicit experiment.
   This register does not give these glyph meanings to numeral cells or SIC
   evidence. An unfinished descent reports budget_exhausted and no factor pair.
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
    if compiled["plan"]["backend"] == "semiprime-descent":
        step = compiled["plan"]["steps"][i]
        return {"process": step["symbol"], "concrete": "Native descent morphism: " + json_text(step["actions"]),
                "input": "retained source and cyclic/evidence carrier",
                "output": "carrier after this measured descent operation",
                "check": "Execution pending: orbit collision, measured GCD, lifted square congruence, FOUR joins and source product."}
    if compiled["plan"]["backend"] == "numeral-factor":
        step, boundary = compiled["plan"]["steps"][i], compiled["boundaries"][i]
        return {"process": step["symbol"], "concrete": "Native numeral morphism: " + json_text(step["actions"]),
                "input": json_text(boundary["domain"]), "output": json_text(boundary["codomain"]),
                "check": "Execution pending: native tape reconstruction, sealed-source equality and verified factor-product release. No SIC policy is implied."}
    if compiled["plan"]["backend"] == "ququart-factor":
        step = compiled["plan"]["steps"][i]
        boundary = compiled["boundaries"][i]
        return {"process": step["symbol"], "concrete": "Bound factor-carrier morphism: " + json_text(step["actions"]),
                "input": boundary["domain"], "output": boundary["codomain"],
                "check": "Execution pending: retain actual before/after carrier, source frames and attributed instrument evidence at this symbol."}
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
    if backend == "semiprime-descent":
        return compile_descent(plan, ops, SYMBOLS)
    if backend == "ququart-factor":
        return compile_factor(copy.deepcopy(plan), list(ops), SYMBOLS)
    if backend == "numeral-factor":
        return compile_numeral(copy.deepcopy(plan), list(ops), SYMBOLS)
    keys = {"backend", "steps", "frame", "seed"} if backend == "evidence" else {"backend", "steps", "source"}
    if backend not in {"evidence", "anyon-ququart"} or set(plan) != keys:
        raise ValueError("unknown adapter or unexpected realization fields")
    steps = plan["steps"]
    if not isinstance(ops, list) or not ops or not isinstance(steps, list) or len(steps) != len(ops):
        raise ValueError("realization requires exact token coverage")
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
    if not isinstance(ops, list) or not ops or not isinstance(plan["steps"], list) or len(plan["steps"]) != len(ops):
        raise ValueError("composition needs exact token coverage")
    schema = {"retain": set(), "sic": set(), "inverse": set(), "exchange": {"generators"},
              "split": {"id"}, "rejoin": {"id"}, "latch": {"id"}, "engage": {"proposition"},
              "evidence": {"proposition", "axis", "outcome", "numerator", "denominator", "witness"}}
    splits, returns, latches, evidence = [], 0, set(), set()
    roles = {"⊢": "retain", "⊣": "sic", "⊙": "retain", "≻": "exchange",
             "≺": "inverse", "⋈": "exchange", "∈": "split", "∋": "rejoin",
             "⊤": "evidence", "⊥": "evidence", "⊞": "engage", "⊡": "latch"}
    for i, (step, op) in enumerate(zip(plan["steps"], ops)):
        if (SYMBOLS.get(op) is None or not isinstance(step, dict) or set(step) != {"i", "symbol", "actions"} or
                type(step["i"]) is not int or step["i"] != i or step["symbol"] != SYMBOLS.get(op) or
                not isinstance(step["actions"], list) or not step["actions"]):
            raise ValueError(f"composition position {i} needs its symbol and ordered operations")
        kinds = [a.get("kind") if isinstance(a, dict) else None for a in step["actions"]]
        if step["symbol"] == "≺" and "exchange" in kinds:
            raise ValueError("return must consume a previously retained exchange, not manufacture a forward exchange at the return symbol")
        if roles[step["symbol"]] not in kinds or (step["symbol"] == "⊙" and set(kinds) != {"retain"}):
            raise ValueError(f"{step['symbol']} requires its operator morphism with a valid primitive, not a placeholder composition")
        if step["symbol"] in {"⊤", "⊥"} and not any(
                isinstance(a, dict) and a.get("kind") == "evidence" and
                a.get("axis") == ("support" if step["symbol"] == "⊤" else "refutation")
                for a in step["actions"]):
            raise ValueError("evaluation morphism must bind the symbol's evidence axis")
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
    if checked["plan"]["backend"] == "semiprime-descent":
        return execute_descent(checked)
    if checked["plan"]["backend"] == "numeral-factor":
        return execute_numeral(checked)
    if checked["plan"]["backend"] == "ququart-factor":
        return execute_factor(checked)
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
