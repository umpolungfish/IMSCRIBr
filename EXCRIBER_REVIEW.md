# EXCRIBER REVIEW — IMSCRIBr excriber python files
Reviewed: excriber.py (418 ln), excriber_v2.py (271), excriber_v3.py (688), batch_excribe_25.py (106).
Method: full read of every file + live parse/excribe runs + anchor verdict from Vox.
Anchor: `vox verdict '⊢≻∈⊤⊥∋⊡⊣'` → **T** (kernel ground truth for the canonical word).

## SHARED BUGS (all three excribers)

**S1. IFIX glyph is wrong — the excribers cannot read a real word.**
`GLYPH_TO_OPCODE` maps `"◻": "IFIX"` in all three files. `◻` is not one of the
twelve; the IFIX mark is `⊡`. Consequences, measured:
  - input `⊡` is not in the map → silently dropped: `parse_word('⊢≻∈⊤⊥∋⊡⊣')`
    returns 7 opcodes (VINIT AFWD FSPLIT3 EVALT EVALF FFUSE3 TANCH), the
    8-glyph canonical word loses its IFIX entirely;
  - `OPCODE_TO_GLYPH["IFIX"]` = `◻`, so any excription that re-emits glyphs
    rewrites the word into one the kernel will not parse.
  - Vox judges that word T. An elaborator that cannot even see the mark is
    elaborating a different word.

**S2. ∈/∋ map to `FSPLIT3`/`FFUSE3`, but the semantics tables key `FSPLIT`/`FFUSE`.**
`OPCODE_SEMANTICS` (v1) and `OP_SEM` (v2/v3) have no `FSPLIT3`/`FFUSE3` entries.
Measured: on any glyph word the ∈ and ∋ steps render with action `?` and empty
structural meaning. The fork/fuse — the load-bearing pair of the language — is
the one part of the word the excriber visibly cannot name.

**S3. `parse_word` swallows unknown marks.**
The final `else: i += 1` drops any character that is not a mapped glyph or a
prefix of an opcode name. Retired marks (=, ◇, >, +, <, ●, ×, ¬, ←, V/T/B
codes) vanish instead of erroring, so a corrupted or legacy word excribes
silently as a shorter, different word. There is no diagnostic, no F verdict.

**S4. Pairing is stack-rule over the linear string, not ancestry over edges.**
All three use "nearest unmatched FSPLIT" and treat every node strictly between
fork and fuse as one interleaved arm:
  - v1 `find_pairs`: `f_arm_indices` is always `[]`; all nodes go to `t_arm_indices`;
  - v2/v3: one `arm_nodes` list; `arm_type` = whichever of EVALT/EVALF appears
    FIRST in that list. A fork with work on both arms is mislabelled as a
    single T-arm or F-arm.
The docstrings claim "ancestry", but ancestry is a property of the edges (the
verb), and these files never build edges. Fine for a plain well-nested strand;
wrong for anything routed.

**S5. Verdict logic is a home-grown reimplementation that contradicts the kernel.**
The same 8-line block (ENGAGR→B / pairs+work→T / pairs no work→N / else N) is
copied 4 times (v1 once, v2 once, v3 twice — including in dead code). It:
  - can never say B (open) for a dangling ∈ or ∋ — `⊢∈⊤⊣` reads "N (no fork)"
    instead of B;
  - has no F verdict at all (ill-typed shapes read N);
  - says "B (paradox held)" for ANY word containing ⊞, even `⊢⊞⊣` with no dyad;
  - on the canonical word, v2 and v3 print **"N (no fork)" where Vox says T**
    (measured), purely because of bug S2 (FSPLIT3≠FSPLIT kills pair detection
    on glyph input).
The excriber is a *narrator*; it should call the judge, not re-implement it
incorrectly. The fix is one subprocess (or import) of the real check.

**S6. `OPCODE_TO_GLYPH` is built by dict inversion and inherits S1** — output
words are not parseable.

## excriber.py (v1) — additional bugs

**V1-1. Docstring example is unparseable.** Line 18 example
`"⊢⊙=◇>+<●◇×<●=⊞⊙¬⊣"` is built from RETIRED marks (=, ◇, >, +, <, ●, ×, ¬).
Under S3 it parses to a 2-opcode word (`VINIT IMSCRIB`), i.e. the advertised
usage demonstrates a word the excriber would misread.
**V1-2. Usage mismatch.** Module docstring says `--context-desc`; main() only
handles `--desc`.
**V1-3. `elaborate_step` is a fixed SIC-POVM monologue.** Every branch
hardcodes the d=12→d=2048 / 2-adic conductor / Zauner narrative. The context
name appears in at most one slot of most templates; excribing `collatz_conjecture`
produces SIC-POVM prose. The "domain context" is decorative.
**V1-4. Text-form parsing drops forks.** `parse_word("VINIT FSPLIT EVALT FFUSE TANCH")`
→ `[VINIT, EVALT, TANCH]` (measured): the name list only offers `FSPLIT3`/`FFUSE3`,
so the 6-char `FSPLIT` is eaten one char at a time by the swallow branch. Text
input gets zero pairs; only glyph input pairs (and even then via the S2 mismatch
in the semantics tables).
**V1-5. `get_context_info` is a dead catalog bridge.** Hardcoded absolute path,
10 s subprocess, bare `except: pass`, and it only fills `info["tier"]` —
`tuple` and `description` are never set, so `context_tuple` is always "" and the
catalog description is never read. The f-string also interpolates
`context_name` into child Python source (injection point).
**V1-6. `EVALI` in the name list** with no semantics entry → `?`; EVALI is the
trilattice-face reading of ⊞, not a classic opcode, and it is not in the glyph map.

## excriber_v2.py — additional bugs

**V2-1. The headline feature is disabled for glyph input.** `find_pairs_by_ancestry`
matches only `op == "FSPLIT"`/`"FFUSE"`; the glyph map emits `FSPLIT3`/`FFUSE3`,
so glyph words (the normal form) get **zero pairs** — measured: canonical word
→ verdict `N (no fork)` where Vox says T. Arm-aware elaboration only fires on
opcode-text input, which V1-4 shows v1 cannot even parse.
**V2-2. `idx > 10` special cases** for IMSCRIB/CLINK — position hacks bound to
one particular 14-opcode word; any other word length changes the narrative.
**V2-3. Same fixed SIC-POVM monologue** as v1 (slightly more arm-aware text).
**V2-4. No B/F verdicts; ENGAGR→B unconditionally** (S5).

## excriber_v3.py — additional bugs

**V3-1. `def excribe` appears twice** (measured: 2 definitions). The per-step LLM
version (~line 396) is shadowed by the batched one (~line 640); `LlmBackend.
elaborate_step` and the first excribe are dead code.
**V3-2. API errors become content.** `query()` returns `"[LLM ERROR: {e}]"`
on ANY failure (network, 4xx, null content); `excribe_batched` then stores that
string as the step elaboration. `_query_json_array` returns
`["[LLM ERROR: ...]"] * expected_len` — one failed request poisons every step.
**V3-3. Unbounded batch tokens.** `max_tokens = max(1024, expected_len * 150)`
— a 2048-glyph word requests a 307k-token completion with no cap or chunking.
**V3-4. Cache key has no version.** sha256[:16] of provider:model:system:prompt;
code changes never invalidate cached elaborations. (16 hex = 64 bits, collision
plausible over many runs.)
**V3-5. Misspelled OpenRouter referer** `github.com/umpolungfish/imscrbgrmr`.
**V3-6. Redundant strictness condition.** Inside `if not args.dry_run:` the
re-raise guard is `if not args.dry_run and os.environ.get("EXCRIBER_STRICT")`
— the first conjunct is always true there; the comment ("Re-raise to let the
user know") does not match the code (conditional exit).
**V3-7. Verdict block duplicated** in both excribe bodies (S5).

## batch_excribe_25.py — additional bugs

**B1. Unbound `exc` on the error path.** If `excribe_batched` raises, the
`except` sets `text`, but the following `print(f"  done ({len(exc.steps)}...")`
references `exc`, which was never assigned → NameError masks the original
error and aborts the whole batch.
**B2. 9 names imported, ~1 used.** `GLYPH_TO_OPCODE, OPCODE_TO_GLYPH,
parse_word, OP_SEM, find_pairs_by_ancestry, ExcribedStep, Excription,
ForkFusePair` are unused.
**B3. Docstring overclaim.** "Reads from WORDZ library (WORDZ.txt) or wordbook" —
WORDZ.txt is never opened; it only appears in the final "unchanged" print.
**B4. `resolve_provider_model()` unguarded** — no API key = unhandled
ValueError traceback before any entry is processed.
**B5. Fine points:** PICKS is genuinely 25 entries; wordbook
(`/home/mrnob0dy666/imsgct/MoDoT/ob3ects/imasm_catalog_words.json`, 3.8 MB)
and WORDZ.txt both exist.

## FIX LIST (in priority order)

1. **S1:** map `⊡`→IFIX (drop `◻`); regenerate `OPCODE_TO_GLYPH` from the
   corrected table. One-line fix per file; unblocks reading real words.
2. **S2:** make the glyph map emit `FSPLIT`/`FFUSE` (or add the `*3` keys to
   the semantics tables and pair-detection) so ∈/∋ are named and paired.
3. **S5:** delete the home-grown verdict; call the real judge
   (`vox verdict <word>` or the imasm CLI `check`) and report its T/N/B/F.
   The narrator should carry the verdict, not compute a wrong one.
4. **S3:** make the parser strict — unknown marks raise (or produce F), never
   vanish.
5. **S4:** if arm-level elaboration is to stay, build the actual edges (the
   verb supplies them) and pair by ancestry; until then label arms "unresolved"
   instead of inventing T/F from the first eval seen.
6. **V1-3/V2-3:** move the fixed SIC-POVM monologue out of the code; v3's
   LLM path already does this properly — v1/v2 should be deleted or reduced to
   thin wrappers over v3.
7. **V3-1..V3-6:** delete the shadowed excribe, raise instead of returning
   error strings, cap/chunk batch tokens, version the cache key, fix the
   referer, drop the redundant conjunct.
8. **B1:** guard the post-loop print with `if "exc" in locals()` / move it
   inside the try.
9. Retire v1 and v2 once v3 passes: three copies of one parser with three
   different bugs is the maintenance trap.

VERDICT: the files are a workable scaffolding (v3's LLM batching + caching is
sound design) but as written none of them can read a real IMASM word correctly:
the IFIX mark is invisible, fork/fuse are misnamed, pairing is positional, and
the self-computed verdict contradicts the kernel on the canonical word.
Anchor: `vox verdict '⊢≻∈⊤⊥∋⊡⊣'` = T; excriber v2/v3 say "N (no fork)".

## APPLIED — canonical-twelve update
All four files updated to use only ⊢ ⊣ ≻ ≺ ⋈ ⊙ ∈ ∋ ⊤ ⊥ ⊞ ⊡ (backups: *.pre_canonical.bak):
1. Glyph maps: `"◻": "IFIX"` → `"⊡": "IFIX"` in excriber.py, excriber_v2.py, excriber_v3.py (S1 fixed).
2. `∈`/`∋` now map to `FSPLIT`/`FFUSE` everywhere (S2 fixed); FSPLIT3/FFUSE3 strings removed from
   v1 name list, find_pairs, and verdict tuple; stray EVALI removed.
3. Parsers are STRICT: any non-canonical mark raises ValueError (S3 fixed). ◻ and ◇ both verified to raise.
4. v1 docstring example replaced with the canonical `⊢⊙⋈∈≻⊤≺⊞⊥∋⊡⊣`; `--context-desc` → `--desc`.
5. Prose labels `¬` for IFIX replaced with IFIX in v1/v2 (4 sites).
6. batch_excribe_25.py: `done` print moved inside the try (B1 fixed — no more unbound `exc` NameError).
Verified: all three excribers parse the canonical word to 8/8 opcodes, find 1 pair, no `?` actions,
and report verdict **T** — agreeing with `vox verdict '⊢≻∈⊤⊥∋⊡⊣'` = **T**. Wordbook
(imasc_catalog_words.json) scanned: zero non-canonical characters, so the batch runs clean under strict parsing.
Remaining (not glyph-related, unchanged by this pass): S4 positional pairing, S5 home-grown verdict
block (now at least fed correct opcodes), v1/v2 hardcoded SIC-POVM monologue, v3 duplicate excribe /
LLM error-as-content / unversioned cache.
