# Excribe Vox usage

`excribe_vox.py` turns an IMASM word and a register description into a carrier-bound morphism plan. Vox reads the normalized word and supplies its verdict and paired regions. Model translation can add validated executable bindings for the supported adapters.

Run the examples below from the directory containing `excribe_vox.py` and this guide.

Model examples use your exported `IG_PROVIDER` and `IG_MODEL` settings. Keep your existing values if they are already configured. Otherwise set them before running model commands, replacing the model placeholder with your provider's model identifier:

```bash
export IG_PROVIDER=local
export IG_MODEL='YOUR_SERVED_MODEL_ID'
```

Bare `--llm` requests translation using those settings. Offline inspection and saved-plan replay need neither setting.

## Start with a local example

Execute the supplied evidence plan without contacting a model:

```bash
python3 excribe_vox.py --run-plan evidence_return.plan.json
```

The example prepares propositions p and q, separates their evidence axes, swaps their coordinates, returns through the retained inverse, deposits support and refutation for p, rejoins the axes, and latches the result. The final state has both evidence coordinates for p and refutation for q. Its fuse witness reports successful coordinate reconstruction and a changed source state.

Inspect a word using the local register definitions:

```bash
python3 excribe_vox.py \
  '⊢∈≻∋⊣' belnap --offline --emit
```

Use the canonical symbols for the word. Quote the word and register description so the shell passes each as one argument. Empty words and foreign marks are rejected.

## Ask the model for an executable plan

Give the register description concrete source values, an operation, and any evidence source identifiers:

```bash
word='⊢∈≻≺⊞∋⊣'
register='FOUR evidence carrier with propositions p and q, seed p supported and q refuted; swap p and q then reverse that swap, deposit support from sensor-A and refutation from sensor-B for p'

python3 excribe_vox.py "$word" "$register" \
  --llm --save-plan my_evidence.plan.json --execute
```

`--llm` requests model translation using `IG_PROVIDER` and `IG_MODEL`. `--save-plan` creates a new plan file and refuses to overwrite an existing file. `--execute` runs the validated realization and includes its witnesses in the report. Omit `--execute` to inspect and save the plan before running it.

Replay the saved plan without another model call:

```bash
python3 excribe_vox.py --run-plan my_evidence.plan.json
```

Replay revalidates the source bindings and ordered operations. It regenerates native arguments and evidence witnesses. The standalone replay command accepts no word or register arguments.

## Supported execution

### FOUR evidence carrier

The `evidence` adapter binds a proposition frame and an explicit support/refutation seed. Each proposition has two Boolean coordinates. A forward action applies a bound coordinate permutation; a return action uses the most recently retained inverse. Split and fuse separate and reconstruct the support/refutation axes while retaining the source snapshot.

Supporting and refuting evaluations deposit attributed evidence. Engagement deposits both coordinates. Identity preserves the state, linking retains ordered composition, fixation copies a latch, and the terminal boundary releases the result and witnesses. Supplied source identifiers record attribution; execution does not independently measure the named sensors.

`coordinate_return` checks reconstruction of the current evidence coordinates. `source_return` checks equality with the retained source. Depositing new evidence can change source equality while preserving coordinate reconstruction.

### Native anyonic ququart

The `anyon-composition` path synthesizes an ordered composition on one resident native carrier. Bind a decimal source of at least 128 bits, a source basis, signed Artin generators, and any evidence policies:

```bash
python3 excribe_vox.py '⊢≻≺⊣' \
  'An anyonic ququart with source 340282366920938463463374607431768211507; start in T, apply signed Artin generators 1, 2, -3 in order, then their retained inverse' \
  --llm --execute
```

The whole composition runs in one native `sic-tool anyon-program` invocation, retaining all five channels. Return actions reverse retained exchange batches and measure their actual source-return residuals. The report gives the maximum absolute real or imaginary component difference as an integer numerator over the native fixed-point scale. Terminal analysis retains sixteen SIC masses and outside-carrier mass without collapsing the carrier.

Each symbol can bind an ordered composition of native primitives. Split retains a named source frame, phase, and leakage. Rejoin checks native SIC dual reconstruction of current computational populations and compares all five amplitudes with the retained source. Coherent phase is retained separately throughout; probabilities alone do not reconstruct it. Evaluations apply explicitly bound rational thresholds to current native SIC masses and retain accepted or rejected observations with their sources. Engagement retains both previously evaluated evidence coordinates. Fixation copies the state and evidence. Linking can apply an ordered exchange composition.

Motifs guide synthesis without limiting it to registered whole words. An unresolved result must identify a genuinely missing primitive or material binding. Missing whole-word templates do not require a bare sequence. Old saved `anyon-ququart` plans remain replayable through their narrower legacy exchange interface, whose terminal measurement is destructive.

## Read the report

The report carries the original input, normalized word, Vox reading, pairing regions, carrier frame, and per-morphism boundaries. Executable rows take their descriptions and input/output boundaries from the validated adapter. The original model explanation is retained separately in JSON as `model_explanation`.

Use `--json` for a machine-readable translation report. Saved-plan replay always prints a JSON execution witness. `--emit` prints shell-quoted Vox inspection commands and, when available, the native realization command. Offline table descriptions alone do not create an executable plan.

Vox's verdict answers its control-flow question. A carrier's reconstruction witness answers its own return question. Successful execution retains both readings where available.

## Model and source controls

Provider and model selection use `IG_PROVIDER` and `IG_MODEL` in these examples. The local server defaults to `http://127.0.0.1:8000`; set `IG_LOCAL_URL` to change its base address when using the local provider. CLI provider and model overrides take precedence over environment settings.

Known register descriptions use local definitions unless model translation is requested. Unknown descriptions can trigger model translation automatically. `--offline` prevents provider discovery and calls. It cannot be combined with `--llm`, `--stream`, or `--dry-run`.

Inspect the complete model prompt without contacting a server:

```bash
python3 excribe_vox.py '⊢≻≺⊣' anyon \
  --llm --dry-run
```

The prompt includes addressed local source excerpts and the executable adapter catalog. Add `--context PATH` for another local source file; the option is repeatable. `--stream` writes generated model output to stderr. `--think off` disables local-model thinking; other supported effort values appear in `--help`. `--no-spinner` disables progress animation.

Model bindings must cover every symbol in order. Invalid executable bindings receive one correction attempt. Persistently invalid bindings produce an error. Model-supplied shell commands and code are rejected by the closed adapter schema.

## Command combinations

Run this setup once in your shell from the tool's directory. The following examples reuse these variables:

```bash
EXV=excribe_vox.py
WORD='⊢∈≻≺⊞∋⊣'
REGISTER='FOUR evidence carrier with propositions p and q, seed p supported and q refuted; swap p and q then reverse that swap, deposit support from sensor-A and refutation from sensor-B for p'
ANYON_WORD='⊢≻≺⊣'
ANYON_REGISTER='An anyonic ququart with source 340282366920938463463374607431768211507; start in T, apply signed Artin generators 1, 2, -3 in order, then their retained inverse'
```

### Offline inspection

These commands contact no model provider. `--runtime` selects report context; the executable adapter is determined by validated realization bindings.

```bash
# Basic local report
python3 "$EXV" "$WORD" belnap --offline

# A word with a fixation boundary before the terminal boundary
python3 "$EXV" '⊢∈≻≺⊞∋⊡⊣' belnap --offline

# JSON report
python3 "$EXV" "$WORD" belnap --offline --json

# Include shell-quoted Vox inspection commands
python3 "$EXV" "$WORD" belnap --offline --emit

# Inspection-command data in JSON
python3 "$EXV" "$WORD" belnap --offline --emit --json

# Explicit report runtime
python3 "$EXV" "$WORD" belnap --offline --runtime para --emit

# SIC carrier definition
python3 "$EXV" '⊢∈⊙∋⊣' sic --offline --json

# Anyonic carrier definition with runtime context
python3 "$EXV" "$ANYON_WORD" anyon --offline --runtime gmonados --emit

# Structural boundaries for a target without a local definition
python3 "$EXV" "$WORD" 'a chemical reaction vessel' --offline --json
```

### Prompt inspection

Dry-run constructs the prompt without provider discovery or a model call. Source paths are resolved from the current working directory.

```bash
# Exact system instructions and prompt
python3 "$EXV" "$WORD" "$REGISTER" --llm --dry-run

# Prompt in JSON with thinking disabled
python3 "$EXV" "$WORD" "$REGISTER" \
  --llm --dry-run --think off --json

# One additional source
python3 "$EXV" "$ANYON_WORD" "$ANYON_REGISTER" \
  --llm --dry-run --context ../HORN_TORUS_GEOMETRY_CONTEXT.md

# Multiple additional sources
python3 "$EXV" "$ANYON_WORD" "$ANYON_REGISTER" \
  --llm --dry-run \
  --context ../SNS_PRIME.md \
  --context ../ig-docs/ANYONIC_QUQUART_MEMBRANES.md --json
```

### Model translation

These commands require the provider configured through `IG_PROVIDER`, using `IG_MODEL`. Streaming writes model output to stderr, leaving stdout available for the final report.

```bash
# Generate a bound realization for inspection
python3 "$EXV" "$WORD" "$REGISTER" --llm

# JSON without progress animation
python3 "$EXV" "$WORD" "$REGISTER" --llm --json --no-spinner

# Stream with thinking disabled
python3 "$EXV" "$WORD" "$REGISTER" --llm --stream --think off

# Stream while keeping the final report as JSON
python3 "$EXV" "$WORD" "$REGISTER" \
  --llm --stream --json --no-spinner

# Higher reasoning effort and emitted commands
python3 "$EXV" "$WORD" "$REGISTER" --llm --think high --emit

# Source-grounded anyonic translation
python3 "$EXV" "$ANYON_WORD" "$ANYON_REGISTER" \
  --llm --context ../ig-docs/THE_CODEX_FIBONACCI.md --emit

# A different local server address
IG_PROVIDER=local IG_LOCAL_URL=http://127.0.0.1:8080 \
  python3 "$EXV" "$WORD" "$REGISTER" --llm --json
```

Replace `YOUR_SERVED_MODEL_ID` with an identifier accepted by your server. The authentication example assumes its key is already stored in `IG_LOCAL_API_KEY`.

```bash
# Explicit model selection
IG_MODEL='YOUR_SERVED_MODEL_ID' \
  python3 "$EXV" "$WORD" "$REGISTER" --llm --think low

# Authenticated local server
IG_PROVIDER=local python3 "$EXV" "$WORD" "$REGISTER" \
  --llm --api-key "$IG_LOCAL_API_KEY" --json
```

`IG_PROVIDER` is tried first; if it is unavailable, the current resolver can fall through to its configured provider chain. `IG_MODEL` is retained for the selected provider, so choose a model identifier compatible with it. For strict provider selection without fallback, explicitly pass `--llm "$IG_PROVIDER"`; the model still comes from `IG_MODEL`. An explicit unavailable provider fails. Remote providers require their configured credentials.

### Execution and saving

Each save command requires a fresh destination filename. Newly synthesized anyonic compositions retain coherent state and report non-destructive terminal SIC analysis.

```bash
# Generate and execute evidence operations
python3 "$EXV" "$WORD" "$REGISTER" --llm --execute

# Execute with structured witnesses and thinking disabled
python3 "$EXV" "$WORD" "$REGISTER" \
  --llm --execute --json --think off --no-spinner

# Save a plan for review without executing
python3 "$EXV" "$WORD" "$REGISTER" \
  --llm --save-plan evidence_review.plan.json --emit

# Save and execute together
python3 "$EXV" "$WORD" "$REGISTER" \
  --llm --save-plan evidence_run.plan.json --execute --json

# Execute native exchanges and show their command
python3 "$EXV" "$ANYON_WORD" "$ANYON_REGISTER" \
  --llm --execute --emit --runtime gmonados

# Save native exchanges for later execution
python3 "$EXV" "$ANYON_WORD" "$ANYON_REGISTER" \
  --llm --save-plan anyon_review.plan.json --json --think off
```

### Standalone replay

Replay always prints a JSON execution witness and contacts no model. The saved-plan examples require the corresponding save commands above to have completed successfully.

```bash
# Supplied example
python3 "$EXV" --run-plan evidence_return.plan.json

# Previously reviewed evidence operations
python3 "$EXV" --run-plan evidence_review.plan.json

# Previously reviewed native exchanges
python3 "$EXV" --run-plan anyon_review.plan.json
```

Keep `--offline` separate from `--llm`, `--stream`, and `--dry-run`. Use `--run-plan` as a standalone replay command, without a word, register, `--llm`, `--execute`, or `--save-plan`. Offline table reports provide descriptive plans; `--save-plan` and `--execute` require a validated executable realization from model translation.

## Complex words with concrete bindings

These examples use the existing `IG_PROVIDER` and `IG_MODEL` settings. Each word supplies a different operation sequence. The descriptions bind the seed, each permutation, each evidence deposit, and its source. The evidence results below are checked against the local executable adapter using those exact bindings. Model translation must supply the same bindings to produce those results; inspect the returned `binding` fields when reviewing a saved plan.

### Every symbol on one evidence carrier

```bash
python3 excribe_vox.py '⊢⊙∈≻⊤⋈≺∈⊥⊞⊙∋∋⊡⊣' \
  'FOUR evidence carrier with frame ordered p, q, r; seed p neither, q supported, r refuted. Retain identity, open the outer evidence split, and apply the forward relabeling p to q, q to r, r to p. Deposit support for q from sensor-A. Link the actions and apply the retained inverse relabeling. Open an inner evidence split; deposit refutation for q from sensor-B, and support from sensor-C plus refutation from sensor-D for r. Retain identity, rejoin the inner split, rejoin the outer split, latch, and release.' \
  --llm --execute --json --think off --no-spinner
```

The returned evidence is p supported, q both supported and refuted, and r both supported and refuted. Both rejoin events reconstruct their current coordinates. Neither returns its original split source, because evidence was added. Vox reads this supplied word as T.

### Nested splits with two retained returns

```bash
python3 excribe_vox.py '⊢∈≻∈≻∈⊤⊥∋≺∋≺∋⊡⊣' \
  'FOUR evidence carrier with frame ordered p, q, r; seed p neither, q supported, r refuted. Open the outer split and swap p with q, retaining r. Open the middle split and swap q with r, retaining p. Open the inner split; deposit support for r from inner-support and refutation for p from inner-refutation. Rejoin the inner split. Undo the most recent swap, rejoin the middle split, undo the first swap, rejoin the outer split, latch, and release.' \
  --llm --save-plan nested_evidence.plan.json --execute --emit

python3 excribe_vox.py --run-plan nested_evidence.plan.json
```

The final evidence is p supported, q both supported and refuted, and r refuted. Each return undoes the last unreversed coordinate swap. The deposited evidence travels with those coordinates. All rejoin events reconstruct the current coordinates; source equality changes at each split. Vox reads T.

### Separate rounds of support and refutation

```bash
python3 excribe_vox.py '⊢∈⊤∋⋈∈⊥⊞∋⊡⊣' \
  'FOUR evidence carrier with propositions alarm and backup, both seeded neither supported nor refuted. In the first split deposit support for alarm from detector-A and rejoin. Link into a second split; deposit refutation for alarm from detector-B, then deposit support from backup-A and refutation from backup-B for backup. Rejoin, latch the completed state, and release.' \
  --llm --stream --execute --json --no-spinner
```

Both alarm and backup finish with support and refutation. The first split's source snapshot precedes the support deposit; the second snapshot already contains it. Both source-return witnesses are false. Vox reads T.

### Two forward operations returned in reverse order

```bash
python3 excribe_vox.py '⊢∈≻≻⊙≺≺∋⊡⊣' \
  'FOUR evidence carrier with frame ordered p, q, r; seed p supported, q refuted, r neither. Split the evidence axes. First relabel p to q, q to r, r to p. Then swap p with q while retaining r. Retain identity. Undo the second relabeling, then undo the first relabeling. Rejoin, latch, and release without depositing evidence.' \
  --llm --execute --json --think high
```

The final seed is recovered exactly: p supported, q refuted, r neither. The rejoin witness reports `coordinate_return: true` and `source_return: true`. Overall source equality is also true. Vox reads T.

### Intermediate latches preserve distinct states

```bash
python3 excribe_vox.py '⊢∈⊞⊡⊤⊥⊡∋⊡⊣' \
  'FOUR evidence carrier with p and q both seeded neither. Split, then deposit support from p-support and refutation from p-refutation for p. Latch that intermediate state. Deposit support for q from q-support, then refutation for q from q-refutation. Latch again, rejoin, latch the terminal state, and release. Preserve every copied latch in the execution events.' \
  --llm --save-plan latched_evidence.plan.json --execute --json
```

The first latch contains both evidence coordinates for p and neither for q. The second and final latches contain both coordinates for both propositions. The earlier latch remains unchanged. Vox reads T.

### Repeated deposits retain their separate witnesses

```bash
python3 excribe_vox.py '⊢∈⊤⊤⋈⊥⊥⊙∋⊡⊣' \
  'FOUR evidence carrier with proposition p seeded neither. Split. Deposit support for p from support-A, then support for p from support-B. Link the ordered operations. Deposit refutation for p from refutation-A, then refutation for p from refutation-B. Retain identity, rejoin, latch, and release. Keep each deposit source in its own event.' \
  --llm --execute --json --emit
```

The final coordinates for p are both true. Repeated deposits leave an already-set coordinate true, while their operation events retain distinct source identifiers. Vox reads T.

### Nested native exchange returns

```bash
python3 excribe_vox.py '⊢⊙≻≻⊙≺≺⊙⊣' \
  'An anyonic ququart with decimal source 340282366920938463463374607431768211507, initialized in T. Retain identity. The first forward operation applies signed Artin generators 1, 2, -3 in order. The second applies 4, -5, 2 in order. Retain identity. Return by undoing the second forward operation, then undoing the first forward operation. Retain identity and perform terminal native SIC measurement with outside-carrier mass retained.' \
  --llm --save-plan nested_anyonic.plan.json --execute --emit

python3 excribe_vox.py --run-plan nested_anyonic.plan.json
```

The native exchange order is `1, 2, -3, 4, -5, 2, -2, 5, -4, 3, -2, -1`. All exchanges act in one resident carrier. Identity symbols add no exchanges. Vox reads N because this word contains no split/rejoin region. Native composition still runs and produces its SIC/leakage witness and measured return residuals.

### Two independent native exchange-and-return rounds

```bash
python3 excribe_vox.py '⊢≻⊙≺≻⊙≺⊣' \
  'An anyonic ququart with decimal source 340282366920938463463374607431768211507, initialized in T. Apply signed Artin generators 2, 3, 2 as the first forward operation; retain identity and undo that operation. Apply 5, -4, 1, -2 as the second forward operation; retain identity and undo that operation. End with native SIC measurement and retain the outside-carrier mass.' \
  --llm --execute --json --think off
```

The native order is `2, 3, 2, -2, -3, -2, 5, -4, 1, -2, 2, -1, 4, -5`. The rounds share the same resident carrier. Vox reads N; the native terminal witness is reported separately.

### Inspect the same complex word in other registers

These commands inspect descriptive carrier plans without requesting execution. Use model synthesis to bind a native composition; offline definitions alone supply no executable bindings.

```bash
python3 excribe_vox.py '⊢⊙∈≻⊤⋈≺∈⊥⊞⊙∋∋⊡⊣' \
  anyon --offline --runtime gmonados --emit

python3 excribe_vox.py '⊢∈≻∈⊙≻≺∋⋈≺∋⊡⊣' \
  sic --offline --json

python3 excribe_vox.py '⊢∈≻⊤∋⋈∈≺⊥∋⊡⊣' \
  'a membrane reactor retaining source composition and reaction witnesses' \
  --offline --emit

python3 excribe_vox.py '⊢∈≻∈⊙≻≺∋⋈≺∋⊡⊣' \
  'a SIC carrier with a retained analysis frame and source operator' \
  --llm --dry-run --context ../ig-docs/ququart_membranes.tex --json
```

### A full native synthesis with measured evidence

```bash
python3 excribe_vox.py '⊢⊙∈≻⊤⋈≺∈⊥⊞⊙∋∋⊡⊣' \
  'An anyonic ququart with decimal source 340282366920938463463374607431768211507, initialized in T. Retain identity and split into a named outer retained SIC frame. Apply exchange batch 1, 2. For proposition p evaluate support from policy-A by testing SIC outcome 0 mass divided by total mass against threshold 1/32. Link by applying exchange batch 3, -4. At the return symbol undo both retained batches, most recent first. Split into an inner retained frame. Evaluate refutation for p from policy-B using outcome 1 mass divided by total mass against threshold 1/32. Engage the two measured evidence coordinates without manufacturing acceptance. Retain identity; rejoin inner then outer, checking native population synthesis and source return. Latch final coherent state and evidence. Release non-destructive SIC analysis. Use native composition throughout and supply measured residuals only after execution.' \
  --llm --save-plan synthetic_anyonic.plan.json --execute --json --no-spinner

python3 excribe_vox.py --run-plan synthetic_anyonic.plan.json
```

The local native control for these bindings executes both returns, verifies both population reconstructions, retains both attributed policy observations, and copies a final latch. It measures the all-five-channel source residual in the current run. A residual quoted in a source manuscript belongs to that manuscript's preparation and is never substituted for this execution witness.

Before execution, row checks describe pending procedures. After `--execute`, rows are marked completed and their `execution_events` refer to the actual native events. Return rows display measured ratios, rejoin rows carry population certificates, and evaluation rows carry the accepted or rejected observation. `source_equal: false` means the integer amplitudes differ exactly; inspect the measured ratio to determine the size of that difference.

## Large semiprime factor extraction

For a numeral word, use the native numeral carrier. The same symbols bind zero/one cell operations rather than SIC evidence policies. This saved request retains the supplied word and independently named source:

```bash
python3 excribe_vox.py --run-plan numeral_semiprime.plan.json
```

The source is `271690685666312585018220346622515128917`. The saved plan uses `backend: "numeral-factor"` and `steps: "register-bound"`. The compiler expands that shorthand into an indexed native morphism at every symbol. Split retains the cell frame, ⊤ deposits zero, ⊥ deposits one, return clears transient cursor state while preserving banked cells, and rejoin carries the deposited tape. Fixation compares the reconstructed tape to the independently named source before invoking Vox's existing tape factor extraction. Terminal release verifies the factor product and screens each factor with native Miller-Rabin.

The preparation-only native binding check reports `source_binding_failed` if the word reconstructs a different number. It prints the reconstructed value in the diagnostic. No extraction runs in that case, and neither source nor word is silently changed. Successful source binding bakes both into the executable; extraction takes no arguments. A separate native verifier then replays the source operators and checks the released factor multiset. Primality screening is reported separately from a primality proof.

To synthesize bindings for your own numeral word with `IG_PROVIDER` and `IG_MODEL`, pass its actual symbols as the first argument and a description such as `native numeral source 271690685666312585018220346622515128917 to prime factors through internal Gödel relations`, with `--llm --save-plan your_numeral.plan.json`. Add `--execute` to perform extraction. A factor request cannot fall back to anyonic threshold observations.

Request a source-baked RSA-100 extraction using the configured `IG_PROVIDER` and `IG_MODEL`:

```bash
python3 excribe_vox.py '⊢∈≻⋈∈≻⊤⊥∋≺⊞∋⊡⊣' \
  'Extract a nontrivial factor pair of decimal semiprime 1522605027922533360535618378132637429718068114961380688657908494580122963258952897654000350692006139. Use the ququart-factor preparation/readout/evidence carrier, base 2, radix 4, seed 1729, fresh preparation bounded at 1800 seconds and extraction bounded at 120 seconds. Bind the source; split outer; prepare the source-baked case at the first forward symbol; link its Fourier operator and modular work; split inner; execute the resident phase/SIC membrane at the second forward symbol. Evaluate support and refutation for factor_pair with witness terminal-product-verifier using the independent terminal producer/product check. Rejoin inner; return the retained preparation cursor while preserving terminal evidence; engage both evaluated coordinates; rejoin outer; latch factor_latch; release verified factors. Bind every symbol to its executable morphism. Supply neither known factors nor a period. Report an unfinished extraction as unclosed.' \
  --llm --save-plan rsa100_generated.plan.json --execute --json --think off

# Replay the supplied fixed bindings without a model call.
python3 excribe_vox.py --run-plan rsa100_factor.plan.json
```

Every symbol executes a bound morphism on the preparation/readout/evidence carrier. The plan contains indexed `steps`, each with its symbol and ordered `actions`. Compilation checks adjacent carrier phases, retained frame pairing, evidence axes and fixation before release. Execution records actual `before` and `after` carriers at each operation. Working symbols cannot be replaced with identity or stage labels.

Preparation compiles the source and work into a case executable; its extraction invocation receives no arguments. No factors or period are provided to preparation. The return here restores the retained preparation cursor while preserving attributed terminal evidence. Its witness concerns that workflow carrier. For a coherent five-channel inverse, use native anyonic composition and its measured amplitude residual instead.

Every execution retains its request, instrument logs, case and result under `measurements/factors/`. `verified` means the independent terminal verifier accepted the factors and source product. Failed or unclosed execution exits with status 1 and releases no verified factor pair. Support records acceptance of the terminal producer/product check; refutation records its rejection. Rejection concerns that readout and does not establish that the source has no factors. The supplied RSA-100 request is an extraction experiment, not a claim of successful factorization or a runtime guarantee.

New saved plans retain the translation's `sources` array, and replay emits it alongside the execution witness. Older plans without that array emit an empty array; replay does not invent provenance.

Saved factor bindings also support `preparation: {"mode": "compiled", "path": "..."}` for a source-matching compiler report, or `{"mode": "retained", "path": "..."}` for an existing case. Paths must remain inside the constellation. Retained cases must match the requested source, base, radix and seed, pass artifact checks, and pass native preparation validation.

## Requirements and errors

Model requests include the complete local Fibonacci Codex, with its digest and full line coverage in saved provenance. Other sources use selected passages. The grounding contract distinguishes coherent state, attributed FOUR evidence, classical measurement, numerical return residuals, and exact factor-product checks. It resolves the Codex's transposed operator names against the live glyph mapping. Missing measurement policies remain unresolved; example thresholds are not defaults. A return cannot manufacture a forward exchange at its own symbol merely to undo it. Supplying the text and these constraints does not guarantee model comprehension or establish an execution result.

Use Python 3 with the existing constellation layout. Vox is expected at `Vox/target/release/vox`; `EXCRIBE_VOX_BIN` overrides that path. Model calls use `httpx`. Native anyonic execution requires `G-mOMonadOS/target/release/sic-tool`. Offline definitions and evidence-plan replay need no model server.

A parse or argument error exits with status 2. Instrument failures, provider failures, malformed model responses, and realization failures exit with status 1. An unsupported adapter can be described successfully, but requesting execution or saving that realization fails. A provider error requires checking the selected server and model; an adapter error requires changing the bindings or choosing a supported operation sequence.

See the built-in descriptions and full CLI options:

```bash
python3 excribe_vox.py --list-registers
python3 excribe_vox.py --help
```

## Five-stage semiprime descent

Replay the native `∈⊤⊥⊞∋` pipeline with the supplied 8051 source:

```bash
python3 excribe_vox.py --run-plan semiprime_descent.plan.json
../Vox/target/release/semiprime_descent 8051 --seed 0 --constant 0
```

The measured pair is 83 and 97. The fixed first cycle fails; subsequent success retains both evidence coordinates at B. Each attempt records its orbit collision states, collision GCD, lifted square witness, residues and knowledge join. `∋` checks exact division, native multiplication, canonical word multiplication and support-polynomial carry reconstruction.

The cyclic stage advances slow and fast quadratic orbit channels and detects a hidden-factor collision by GCD. The next stage constructs a square witness from that measured divisor and checks both residues directly. Consecutive repeated-image predecessors preserve complete parameter traversal. Each attempt keeps a fixed number of native tapes. Bounded collision search has explicit iteration budgets. An exhausted budget releases no factors and exits with status 1. Optional initialization and sealing carry the source and verified result without extracting factors. The standalone word `∈⊤⊥⊞∋` is supported.

Use `semiprime descent` in a model request to select this register. Its plan contains source, seed, constant, attempt and step budgets, and indexed operations. Neither factors nor an unknown prime are supplied to the search. See the native command's `--help` for parameter controls.

For complete cyclic parameter traversal, select `search_mode: "until-closed"` or use the native flag:

```bash
python3 excribe_vox.py --run-plan semiprime_until_closed.plan.json
../Vox/target/release/semiprime_descent 271690685666312585018220346622515128917 --until-closed --steps 100000
```

This mode has no attempt, total-step or frontend time limit. Each finite attempt has at least two steps, advances the constant, and advances the seed on constant wrap. It eventually visits every residue pair. FOUR coordinates persist across attempts; complete frontend replay streams attempt traces into `measurements/descent/` instead of retaining the whole search in memory. Counters use native arbitrary-length tapes. A semiprime has a successful parameter pair in this traversal, giving eventual closure when uninterrupted with sufficient resources. This is not a practical runtime guarantee for large RSA inputs. The supplied fixture still uses 8051; no successful closure of the large source has been observed.

Run the regression controls:

```bash
python3 -m unittest -v test_excribe_vox.py
```
