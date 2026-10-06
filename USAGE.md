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

The `anyon-ququart` adapter starts in the native T basis state. Bind a decimal source of at least 128 bits and signed Artin generator indices from 1 through 5:

```bash
python3 excribe_vox.py '⊢≻≺⊣' \
  'An anyonic ququart with source 340282366920938463463374607431768211507; start in T, apply signed Artin generators 1, 2, -3 in order, then their retained inverse' \
  --llm --execute
```

The whole exchange sequence runs in one native `sic-tool` invocation, retaining the five-channel carrier. Return actions reverse the forward generator list and negate each sign. The terminal action performs destructive SIC measurement and reports outside-carrier mass. This output does not certify an inverse amplitude residual.

This adapter supports source, terminal, identity, forward, and return operations. Native split/fuse and the other morphisms are currently unsupported. General SIC, arbitrary unitary, numeral, executable-substrate, and IMASM-register definitions remain descriptive unless a matching execution adapter is added. An unsupported realization includes its reason and cannot be saved or executed.

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

Each save command requires a fresh destination filename. The anyonic examples perform destructive terminal SIC measurement.

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

## Requirements and errors

Use Python 3 with the existing constellation layout. Vox is expected at `Vox/target/release/vox`; `EXCRIBE_VOX_BIN` overrides that path. Model calls use `httpx`. Native anyonic execution requires `G-mOMonadOS/target/release/sic-tool`. Offline definitions and evidence-plan replay need no model server.

A parse or argument error exits with status 2. Instrument failures, provider failures, malformed model responses, and realization failures exit with status 1. An unsupported adapter can be described successfully, but requesting execution or saving that realization fails. A provider error requires checking the selected server and model; an adapter error requires changing the bindings or choosing a supported operation sequence.

See the built-in descriptions and full CLI options:

```bash
python3 excribe_vox.py --list-registers
python3 excribe_vox.py --help
```

Run the regression controls:

```bash
python3 -m unittest -v test_excribe_vox.py
```
