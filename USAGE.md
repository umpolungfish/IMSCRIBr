# Excribe Vox usage

`excribe_vox.py` turns an IMASM word and a register description into a carrier-bound morphism plan. Vox reads the normalized word and supplies its verdict and paired regions. Model translation can add validated executable bindings for the supported adapters.

Run the examples below from `~/imsgct`.

## Start with a local example

Execute the supplied evidence plan without contacting a model:

```bash
python3 IMSCRIBr/excribe_vox.py --run-plan IMSCRIBr/evidence_return.plan.json
```

The example prepares propositions p and q, separates their evidence axes, swaps their coordinates, returns through the retained inverse, deposits support and refutation for p, rejoins the axes, and latches the result. The final state has both evidence coordinates for p and refutation for q. Its fuse witness reports successful coordinate reconstruction and a changed source state.

Inspect a word using the local register definitions:

```bash
python3 IMSCRIBr/excribe_vox.py \
  'VINIT FSPLIT AFWD FFUSE TANCH' belnap --offline --emit
```

Opcode names and canonical glyphs are accepted. Quote the word and register description so the shell passes each as one argument. Empty words and foreign marks are rejected.

## Ask the model for an executable plan

Give the register description concrete source values, an operation, and any evidence source identifiers:

```bash
word='VINIT FSPLIT AFWD AREV ENGAGR FFUSE TANCH'
register='FOUR evidence carrier with propositions p and q, seed p supported and q refuted; swap p and q then reverse that swap, deposit support from sensor-A and refutation from sensor-B for p'

python3 IMSCRIBr/excribe_vox.py "$word" "$register" \
  --llm local --save-plan IMSCRIBr/my_evidence.plan.json --execute
```

`--llm local` selects the local model server explicitly. `--save-plan` creates a new plan file and refuses to overwrite an existing file. `--execute` runs the validated realization and includes its witnesses in the report. Omit `--execute` to inspect and save the plan before running it.

Replay the saved plan without another model call:

```bash
python3 IMSCRIBr/excribe_vox.py --run-plan IMSCRIBr/my_evidence.plan.json
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
python3 IMSCRIBr/excribe_vox.py 'VINIT AFWD AREV TANCH' \
  'An anyonic ququart with source 340282366920938463463374607431768211507; start in T, apply signed Artin generators 1, 2, -3 in order, then their retained inverse' \
  --llm local --execute
```

The whole exchange sequence runs in one native `sic-tool` invocation, retaining the five-channel carrier. Return actions reverse the forward generator list and negate each sign. The terminal action performs destructive SIC measurement and reports outside-carrier mass. This output does not certify an inverse amplitude residual.

This adapter supports source, terminal, identity, forward, and return operations. Native split/fuse and the other morphisms are currently unsupported. General SIC, arbitrary unitary, numeral, executable-substrate, and IMASM-register definitions remain descriptive unless a matching execution adapter is added. An unsupported realization includes its reason and cannot be saved or executed.

## Read the report

The report carries the original input, normalized word, Vox reading, pairing regions, carrier frame, and per-morphism boundaries. Executable rows take their descriptions and input/output boundaries from the validated adapter. The original model explanation is retained separately in JSON as `model_explanation`.

Use `--json` for a machine-readable translation report. Saved-plan replay always prints a JSON execution witness. `--emit` prints shell-quoted Vox inspection commands and, when available, the native realization command. Offline table descriptions alone do not create an executable plan.

Vox's verdict answers its control-flow question. A carrier's reconstruction witness answers its own return question. Successful execution retains both readings where available.

## Model and source controls

The local server defaults to `http://127.0.0.1:8000`. Set `IG_LOCAL_URL` to change its base address, and use `--model` or `IG_MODEL` to select a model. An explicitly requested unavailable provider fails instead of falling through to another provider. To stay local, specify `--llm local`.

Known register descriptions use local definitions unless model translation is requested. Unknown descriptions can trigger model translation automatically. `--offline` prevents provider discovery and calls. It cannot be combined with `--llm`, `--stream`, or `--dry-run`.

Inspect the complete model prompt without contacting a server:

```bash
python3 IMSCRIBr/excribe_vox.py 'VINIT AFWD AREV TANCH' anyon \
  --llm local --dry-run
```

The prompt includes addressed local source excerpts and the executable adapter catalog. Add `--context PATH` for another local source file; the option is repeatable. `--stream` writes generated model output to stderr. `--think off` disables local-model thinking; other supported effort values appear in `--help`. `--no-spinner` disables progress animation.

Model bindings must cover every token in order. Invalid executable bindings receive one correction attempt. Persistently invalid bindings produce an error. Model-supplied shell commands and code are rejected by the closed adapter schema.

## Requirements and errors

Use Python 3 with the existing constellation layout. Vox is expected at `Vox/target/release/vox`; `EXCRIBE_VOX_BIN` overrides that path. Model calls use `httpx`. Native anyonic execution requires `G-mOMonadOS/target/release/sic-tool`. Offline definitions and evidence-plan replay need no model server.

A parse or argument error exits with status 2. Instrument failures, provider failures, malformed model responses, and realization failures exit with status 1. An unsupported adapter can be described successfully, but requesting execution or saving that realization fails. A provider error requires checking the selected server and model; an adapter error requires changing the bindings or choosing a supported operation sequence.

See the built-in descriptions and full CLI options:

```bash
python3 IMSCRIBr/excribe_vox.py --list-registers
python3 IMSCRIBr/excribe_vox.py --help
```

Run the regression controls:

```bash
cd IMSCRIBr
python3 -m unittest -v test_excribe_vox.py
```
