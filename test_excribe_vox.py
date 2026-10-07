"""Exercise excription boundaries against the real Vox word reader."""
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import excribe_vox as exv


class ExcriptionTests(unittest.TestCase):
    def test_complete_descent_ignores_total_caps_and_retains_stream(self):
        saved = json.loads((exv.Path(exv.HERE) / "semiprime_descent.plan.json").read_text())
        plan = saved["plan"] | {"search_mode": "until-closed", "attempts": 1,
                                "total_steps": 1, "steps_per_attempt": 128}
        compiled = exv.compile_plan(plan, exv.parse_word(saved["word"]))
        self.assertIn("--until-closed", compiled["argv"])
        self.assertNotIn("--total-steps", compiled["argv"])
        report = exv.execute_plan(compiled)
        self.assertEqual(report["status"], "verified")
        self.assertEqual(report["evidence"], "B")
        self.assertEqual(report["search_attempts"], "2")
        self.assertEqual(report["search_steps"], "5")
        events = [json.loads(line) for line in exv.Path(report["trace"]).read_text().splitlines()]
        self.assertEqual([event["status"] for event in events], ["searching", "verified"])

    def test_complete_descent_accepts_source_beyond_python_decimal_limit(self):
        saved = json.loads((exv.Path(exv.HERE) / "semiprime_descent.plan.json").read_text())
        plan = saved["plan"] | {"source": "1" + "0" * 5000, "search_mode": "until-closed"}
        compiled = exv.compile_plan(plan, exv.parse_word(saved["word"]))
        self.assertEqual(compiled["plan"]["source"], plan["source"])

    def test_collision_lift_executes_on_noncongruent_raw_squares(self):
        saved = json.loads((exv.Path(exv.HERE) / "semiprime_descent.plan.json").read_text())
        plan = saved["plan"] | {"source": "15", "seed": "1", "constant": "6",
                                "attempts": 1, "steps_per_attempt": 1, "total_steps": 1}
        report = exv.execute_plan(exv.compile_plan(plan, exv.parse_word("∈⊤⊥⊞∋")))
        self.assertEqual(sorted(map(int, report["factors"])), [3,5])
        split, square, sever, _, fuse = report["events"]
        raw_x, raw_y = int(split["computational_channel"]), int(split["leakage_channel"])
        self.assertNotEqual(raw_x*raw_x % 15, raw_y*raw_y % 15)
        self.assertTrue(split["distinct_mod_source"])
        self.assertEqual(split["collision_gcd"], "3")
        self.assertEqual((square["X"], square["Y"]), ("4", "1"))
        self.assertTrue(square["lifted_from_collision"])
        self.assertTrue(square["square_congruence"])
        self.assertEqual(sever["gcd"], "3")
        self.assertTrue(fuse["mu_delta_source_return"])

    def test_descent_register_selection_retains_arithmetic_stage_meanings(self):
        reg, score = exv.match_register("semiprime descent factor extraction with FOUR evidence")
        self.assertEqual(reg.rid, "descent")
        self.assertEqual(score, 100)
        self.assertIn("squares", reg.ops["EVALT"][1])
        self.assertIn("GCD", reg.ops["EVALF"][1])
        self.assertEqual(exv.match_register("native numeral factor extraction")[0].rid, "numeral")

    def test_descent_model_binding_compiles_with_its_matched_register(self):
        saved = json.loads((exv.Path(exv.HERE) / "semiprime_descent.plan.json").read_text())
        word = saved["word"]
        ops = exv.parse_word(word)
        reg = exv.match_register("semiprime descent factor extraction")[0]
        response = {"register": {"name": "descent", "dim": "native source tape",
                                 "frame": "retained attempts", "return_check": "exact source product"},
                    "tokens": [{"i": i, "process": "native descent", "concrete": reg.ops[op][1],
                                "rationale": "bound register morphism", "input": "retained source",
                                "output": "retained source and witnesses", "check": "execute native stage"}
                               for i, op in enumerate(ops)], "realization": saved["plan"]}
        with patch.object(exv.LlmBackend, "query", return_value=json.dumps(response)):
            rows, meta = exv.llm_translate(ops, list(word), word, "T", "semiprime descent factor extraction",
                                           reg, False, "e", 0, "local", "test")
        self.assertIsNotNone(rows, meta)
        self.assertEqual(meta["realization"]["plan"]["backend"], "semiprime-descent")

    def test_descent_replay_measures_all_five_stages(self):
        saved = json.loads((exv.Path(exv.HERE) / "semiprime_descent.plan.json").read_text())
        compiled = exv.compile_plan(saved["plan"], exv.parse_word(saved["word"]))
        report = exv.execute_plan(compiled)
        self.assertEqual(report["status"], "verified")
        self.assertEqual(sorted(map(int, report["factors"])), [83, 97])
        self.assertEqual(report["evidence"], "B")
        self.assertEqual({e["kind"] for e in report["events"] if e["symbol"] in "∈⊤⊥⊞∋"},
                         {"cyclic_split", "square_congruence", "gcd_severing", "knowledge_join", "verify_and_fuse"})
        fuse = next(e for e in report["events"] if e["kind"] == "verify_and_fuse")
        self.assertTrue(fuse["mu_delta_source_return"])
        self.assertTrue(fuse["support_polynomial_product_verified"])

    def test_descent_has_no_universal_word_endpoint_rule(self):
        saved = json.loads((exv.Path(exv.HERE) / "semiprime_descent.plan.json").read_text())
        compiled = exv.compile_plan(saved["plan"], exv.parse_word("∈⊤⊥⊞∋"))
        report = exv.execute_plan(compiled)
        self.assertEqual(report["status"], "verified")
        self.assertEqual(report["word"], "∈⊤⊥⊞∋")
        ops = exv.parse_word("⊙")
        plan = {"backend": "evidence", "frame": ["p"], "seed": {"p": [False, False]},
                "steps": [{"i": 0, "op": ops[0]}]}
        self.assertEqual(exv.compile_plan(plan, ops)["status"], "ready")

    def test_descent_budget_exhaustion_and_wrong_stage_order(self):
        saved = json.loads((exv.Path(exv.HERE) / "semiprime_descent.plan.json").read_text())
        plan = saved["plan"] | {"attempts": 1, "steps_per_attempt": 1, "total_steps": 1}
        report = exv.execute_plan(exv.compile_plan(plan, exv.parse_word(saved["word"])))
        self.assertEqual(report["status"], "budget_exhausted")
        self.assertIsNone(report["factors"])
        self.assertEqual(report["returncode"], 1)
        with self.assertRaisesRegex(ValueError, "ordered"):
            exv.compile_plan(plan, exv.parse_word("∈⊥⊤⊞∋"))

    def test_complete_codex_grounding(self):
        context = exv.source_context("factor extraction")
        codex = next(item for item in context if exv.Path(item["path"]).name == "THE_CODEX_FIBONACCI.md")
        original = exv.Path(codex["path"]).read_text(encoding="utf-8")
        self.assertEqual(codex["text"], original)
        self.assertEqual(codex["scope"], "complete")
        self.assertEqual(codex["end_line"], len(original.splitlines()))
        self.assertIn("some Codex passages transpose", exv.LLM_SYSTEM)
        self.assertIn("Rejected support does not automatically", exv.LLM_SYSTEM)
        self.assertIn("Illustrative Codex thresholds are not defaults", exv.LLM_SYSTEM)

    def test_return_cannot_manufacture_its_forward_domain(self):
        word, plan = self.native_composition()
        step = next(step for step in plan["steps"] if step["symbol"] == "≺")
        step["actions"].insert(0, {"kind": "exchange", "generators": [1]})
        with self.assertRaisesRegex(ValueError, "previously retained exchange"):
            exv.compile_plan(plan, exv.parse_word(word))

    def test_numeral_factor_binds_cells_without_quantum_evidence(self):
        saved = json.loads((exv.Path(exv.HERE) / "numeral_semiprime.plan.json").read_text())
        compiled = exv.compile_plan(saved["plan"], exv.parse_word(saved["word"]))
        steps = compiled["plan"]["steps"]
        self.assertEqual(steps[2]["actions"], [{"kind": "bit", "value": 1}])
        self.assertEqual(steps[3]["actions"], [{"kind": "clear"}])
        self.assertEqual(steps[-2]["actions"], [{"kind": "factor_latch"}])
        self.assertEqual(steps[-1]["actions"], [{"kind": "release"}])
        for left, right in zip(compiled["boundaries"], compiled["boundaries"][1:]):
            self.assertEqual(left["codomain"], right["domain"])
        self.assertNotIn("evidence", json.dumps(steps))
        self.assertNotIn("exchange", json.dumps(steps))
        self.assertEqual(compiled["symbol_word"], saved["word"])

    def test_numeral_factor_rejects_invented_evidence_and_cell_values(self):
        import copy
        saved = json.loads((exv.Path(exv.HERE) / "numeral_semiprime.plan.json").read_text())
        ops = exv.parse_word(saved["word"])
        plan = exv.compile_plan(saved["plan"], ops)["plan"]
        bad = copy.deepcopy(plan)
        bad["steps"][2]["actions"] = [{"kind": "evidence", "axis": "refutation"}]
        with self.assertRaisesRegex(ValueError, "numeral carrier"):
            exv.compile_plan(bad, ops)
        bad = copy.deepcopy(plan)
        bad["steps"][2]["actions"][0]["value"] = 0
        with self.assertRaisesRegex(ValueError, "zero/one"):
            exv.compile_plan(bad, ops)

    def test_factor_workflow_binds_large_source_without_known_factors(self):
        saved = json.loads((exv.Path(exv.HERE) / "rsa100_factor.plan.json").read_text())
        compiled = exv.compile_plan(saved["plan"], saved["word_ops"])
        self.assertEqual(compiled["symbol_word"], "⊢∈≻⋈∈≻⊤⊥∋≺⊞∋⊡⊣")
        self.assertEqual(compiled["transport"], "source-baked-workflow")
        self.assertEqual(len(compiled["boundaries"]), len(saved["word_ops"]))
        self.assertEqual(compiled["boundaries"][0]["domain"], "unit")
        self.assertEqual(compiled["boundaries"][-1]["codomain"], "released")
        for left, right in zip(compiled["boundaries"], compiled["boundaries"][1:]):
            self.assertEqual(left["codomain"], right["domain"])
        plan = compiled["plan"]
        self.assertNotIn("factors", plan)
        self.assertNotIn("order", plan)
        self.assertEqual(plan["preparation"], {"mode": "fresh"})
        import factor_workflow as fw
        values = fw.native_numerals([plan["source"], plan["base"]])
        proc = subprocess.run([str(fw.OPERATOR), "--read-numeral", values[plan["source"]]], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(proc.stdout.strip(), plan["source"])

    def test_factor_workflow_rejects_missing_coverage_and_injected_factors(self):
        saved = json.loads((exv.Path(exv.HERE) / "rsa100_factor.plan.json").read_text())
        plan, ops = saved["plan"], saved["word_ops"]
        with self.assertRaisesRegex(ValueError, "workflow needs"):
            exv.compile_plan(plan | {"p": "known-factor"}, ops)
        for invalid in ("0", "1", plan["source"]):
            with self.assertRaises(ValueError):
                exv.compile_plan(plan | {"base": invalid}, ops)
        with self.assertRaisesRegex(ValueError, "power of two"):
            exv.compile_plan(plan | {"radix": "3"}, ops)
        with self.assertRaisesRegex(ValueError, "cover every position"):
            exv.compile_plan(plan | {"steps": plan["steps"][:-1]}, ops)
        with self.assertRaisesRegex(ValueError, "local constellation"):
            exv.compile_plan(plan | {"preparation": {"mode": "retained", "path": "/etc"}}, ops)

    def test_factor_morphisms_reject_stage_only_and_wrong_operator_bindings(self):
        import copy
        saved = json.loads((exv.Path(exv.HERE) / "rsa100_factor.plan.json").read_text())
        for position in range(len(saved["word_ops"])):
            plan = copy.deepcopy(saved["plan"])
            plan["steps"][position]["actions"] = [{"kind": "retain"}]
            with self.assertRaises(ValueError):
                exv.compile_plan(plan, saved["word_ops"])
        plan = copy.deepcopy(saved["plan"])
        plan["steps"][8]["actions"][0]["id"] = "outer"
        with self.assertRaisesRegex(ValueError, "inner frame"):
            exv.compile_plan(plan, saved["word_ops"])
        plan = copy.deepcopy(saved["plan"])
        plan["steps"][6]["actions"][0]["axis"] = "refutation"
        with self.assertRaisesRegex(ValueError, "evidence axis"):
            exv.compile_plan(plan, saved["word_ops"])

    def test_missing_execution_event_is_not_marked_completed(self):
        report = {"rows": [{"i": 0}]}
        exv.attach_execution(report, {"events": []})
        self.assertEqual(report["rows"][0]["execution_status"], "not_run")

    def test_native_work_symbol_cannot_lower_to_identity(self):
        word, plan = self.native_composition()
        plan["steps"][3]["actions"] = [{"kind": "retain"}]
        with self.assertRaisesRegex(ValueError, "operator morphism"):
            exv.compile_plan(plan, exv.parse_word(word))

    def test_factor_execution_failure_is_not_promoted_to_completed(self):
        report = {"rows": [{"i": 0}, {"i": 1}, {"i": 2}]}
        witness = {"backend": "ququart-factor", "status": "unclosed", "events": [
            {"i": 0, "stage": "prepare", "status": "completed"},
            {"i": 1, "stage": "extract", "status": "unclosed"},
            {"i": 2, "stage": "verify", "status": "not_run"}]}
        exv.attach_execution(report, witness)
        self.assertEqual([r["execution_status"] for r in report["rows"]], ["completed", "unclosed", "not_run"])
        self.assertIn("unclosed", report["rows"][1]["check"])

    def native_composition(self):
        word = "⊢⊙∈≻⊤⋈≺∈⊥⊞⊙∋∋⊡⊣"
        actions = [
            [{"kind": "retain"}], [{"kind": "retain"}], [{"kind": "split", "id": "outer"}],
            [{"kind": "exchange", "generators": [1, 2]}],
            [{"kind": "evidence", "proposition": "p", "axis": "support", "outcome": 0,
              "numerator": "1", "denominator": "32", "witness": "policy-A"}],
            [{"kind": "exchange", "generators": [3, -4]}],
            [{"kind": "inverse"}, {"kind": "inverse"}],
            [{"kind": "split", "id": "inner"}],
            [{"kind": "evidence", "proposition": "p", "axis": "refutation", "outcome": 1,
              "numerator": "1", "denominator": "32", "witness": "policy-B"}],
            [{"kind": "engage", "proposition": "p"}], [{"kind": "retain"}],
            [{"kind": "rejoin", "id": "inner"}], [{"kind": "rejoin", "id": "outer"}],
            [{"kind": "latch", "id": "final"}], [{"kind": "sic"}],
        ]
        plan = {"backend": "anyon-composition", "source": str(2**128 + 51), "digit": 0,
                "steps": [{"i": i, "symbol": symbol, "actions": actions[i]} for i, symbol in enumerate(word)]}
        return word, plan

    def test_synthetic_native_composition_realizes_every_symbol(self):
        word, plan = self.native_composition()
        compiled = exv.compile_plan(plan, exv.parse_word(word))
        result = exv.execute_plan(compiled)
        self.assertEqual(exv.judge(word)[0], "T")
        self.assertEqual(len(result["final_state"]), 5)
        self.assertEqual(len(result["sic_masses"]), 17)
        inverses = [e for e in result["events"] if e["kind"] == "inverse"]
        self.assertEqual([e["generators"] for e in inverses], [[4, -3], [-2, -1]])
        for event in inverses:
            numerator = int(event["return"]["numerator"])
            denominator = int(event["return"]["denominator"])
            self.assertLess(numerator * 2**100, denominator)
        rejoins = [e for e in result["events"] if e["kind"] == "rejoin"]
        self.assertTrue(all(e["population_dual_verified"] for e in rejoins))
        observations = [e for e in result["events"] if e["kind"] == "evidence"]
        self.assertEqual([e["observation"]["witness"] for e in observations], ["policy-A", "policy-B"])
        self.assertEqual(result["latches"]["final"]["state"], result["final_state"])
        # The current run supplies its own fixed-point return, never a source-paper number.
        self.assertNotIn("3.79160691e-77", json.dumps(result))

    def test_emitted_native_composition_includes_bound_stdin(self):
        word, plan = self.native_composition()
        report = exv.translate(word, "anyon", offline=True)
        report["realization"] = exv.compile_plan(plan, exv.parse_word(word))
        command = next(line.strip() for line in exv.render(report, emit=True).splitlines()
                       if line.strip().startswith("printf '%s'"))
        proc = subprocess.run(["bash", "-c", command], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["backend"], "anyon-composition")

    def test_native_composition_controls_reject_invalid_bindings(self):
        word, plan = self.native_composition()
        plan["steps"][11]["actions"][0]["id"] = "outer"
        with self.assertRaisesRegex(ValueError, "inner frame"):
            exv.compile_plan(plan, exv.parse_word(word))
        word, plan = self.native_composition()
        plan["steps"][4]["actions"][0]["denominator"] = "0"
        with self.assertRaisesRegex(ValueError, "threshold"):
            exv.compile_plan(plan, exv.parse_word(word))
        word, plan = self.native_composition()
        plan["steps"][0]["actions"] = [{"kind": "shell", "command": "invented"}]
        with self.assertRaisesRegex(ValueError, "primitive"):
            exv.compile_plan(plan, exv.parse_word(word))

    def test_native_evidence_rejection_does_not_manufacture_acceptance(self):
        word, plan = self.native_composition()
        for i in (4, 8):
            plan["steps"][i]["actions"][0]["numerator"] = "32"
        result = exv.execute_plan(exv.compile_plan(plan, exv.parse_word(word)))
        policies = [e for e in result["events"] if e["kind"] == "evidence"]
        self.assertTrue(all(not e["observation"]["accepted"] for e in policies))
        engagement = next(e for e in result["events"] if e["kind"] == "engage")
        self.assertFalse(engagement["evidence"]["support"][0]["accepted"])
        self.assertFalse(engagement["evidence"]["refutation"][0]["accepted"])

    def test_model_synthesizes_native_composition_for_complex_word(self):
        word, plan = self.native_composition()
        ops = exv.parse_word(word)
        response = {"register": {k: "native five-channel carrier" for k in ("name", "dim", "frame", "return_check")},
                    "tokens": [{"i": i, **{k: "proposed procedure" for k in
                                ("process", "concrete", "rationale", "input", "output", "check")}} for i in range(len(word))],
                    "realization": plan}
        with patch.object(exv.LlmBackend, "query", return_value=json.dumps(response)):
            rows, meta = exv.llm_translate(ops, list(word), word, "T", "anyon", exv.match_register("anyon")[0],
                                          False, "∅", None, "local", "test")
        self.assertNotIn("error", meta)
        self.assertEqual(len(rows), len(word))
        self.assertIn("Execution pending", rows[6]["check"])
        self.assertEqual(rows[6]["binding"]["actions"], [{"kind": "inverse"}, {"kind": "inverse"}])
        result = {"rows": rows}
        exv.attach_execution(result, exv.execute_plan(meta["realization"]))
        self.assertTrue(all(r["execution_status"] == "completed" for r in rows))
        self.assertNotIn("Execution pending", rows[6]["check"])
        self.assertEqual(len(rows[6]["execution_events"]), 2)
        self.assertIn('"numerator"', rows[6]["check"])

    def test_names_and_glyphs_have_identical_instrument_input(self):
        glyphs = exv.translate("⊢∈≻∋⊣", "belnap", offline=True)
        names = exv.translate("VINIT FSPLIT AFWD FFUSE TANCH", "belnap", offline=True)
        self.assertEqual(names["judge_raw"], glyphs["judge_raw"])
        self.assertEqual(names["pairing"], glyphs["pairing"])
        self.assertEqual(names["verdict"], "T")
        self.assertEqual(names["pairing"]["regions"][0]["indices"], [2])

    def test_real_controls_discriminate_identity_open_and_unpaired_fuse(self):
        for word, verdict in (("⊢∈⊙∋⊣", "N"), ("⊢∈≻⊣", "B"),
                              ("⊢≻∋⊣", "F"), ("⊢∈≻⊞∋⊣", "T")):
            with self.subTest(word=word):
                report = exv.translate(word, "belnap", offline=True)
                self.assertEqual(report["verdict"], verdict)
        self.assertEqual(exv.translate("⊢∈≻⊣", "belnap", offline=True)
                         ["pairing"]["unpaired_splits"], [1])

    def test_offline_unknown_register_is_structural_and_serializable(self):
        with patch.object(exv, "resolve_provider_model", side_effect=AssertionError("network")):
            report = exv.translate("⊢∈≻∋⊣", "a chemical reaction vessel", offline=True)
        self.assertIsNone(report["reg"])
        self.assertEqual(len(report["rows"]), 5)
        self.assertTrue(all(row["source"] == "structure" for row in report["rows"]))

    def test_cli_unknown_register_json(self):
        proc = subprocess.run([sys.executable, exv.__file__, "⊢∈≻∋⊣",
                               "a chemical reaction vessel", "--offline", "--json"],
                              capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertIsNone(json.loads(proc.stdout)["register"])

    def test_dry_run_is_network_free_for_known_and_unknown_registers(self):
        with patch.object(exv, "resolve_provider_model", side_effect=AssertionError("network")):
            for description in ("sic", "a chemical reaction vessel"):
                report = exv.translate("⊢∈≻∋⊣", description, dry_run=True, llm_arg="local")
                self.assertTrue(report["llm_meta"]["dry_run"])
                self.assertIn("Local source excerpts", report["llm_meta"]["prompt"])

    def test_provider_override_does_not_fall_through(self):
        with patch.object(exv, "local_server_up", return_value=False):
            with self.assertRaisesRegex(ValueError, "local provider is unavailable"):
                exv.resolve_provider_model("local")

    def test_failed_instrument_does_not_borrow_verdict(self):
        with patch.object(exv.subprocess, "run", return_value=subprocess.CompletedProcess(
                [], 1, "verdict T", "failed")):
            verdict, raw = exv.judge("⊢∈≻∋⊣")
        self.assertIsNone(verdict)
        self.assertIn("exit 1", raw)

    def test_emit_commands_execute_the_normalized_input(self):
        report = exv.translate("VINIT FSPLIT AFWD FFUSE TANCH", "anyon", offline=True)
        for check in report["checks"]:
            proc = subprocess.run(check["argv"], capture_output=True, text=True)
            self.assertEqual(proc.returncode, 0, proc.stderr)
            self.assertIn("verdict", proc.stdout)
        self.assertNotIn("quantum fibqc compile σ", exv.render(report, emit=True))

    def test_braid_projection_preserves_intervening_operators(self):
        self.assertEqual(exv.assemble_braid(["AFWD", "AREV"]), "e")
        self.assertEqual(exv.assemble_braid(["AFWD", "EVALT", "AREV"]), "σ·[⊤]·σ⁻¹")

    def test_parser_rejects_empty_and_foreign_marks(self):
        for word in ("", "   ", "⊢>∋⊣", "⊢[∈≻∋]⊣"):
            with self.subTest(word=word), self.assertRaises(ValueError):
                exv.parse_word(word)

    def test_llm_requires_complete_ordered_boundary_rows(self):
        good = {"register": {"name": "reaction carrier", "dim": "stated species",
                             "frame": "species coordinates", "return_check": "reconstruct source species"},
                "tokens": [{"i": i, "process": "carry", "concrete": "retain species",
                            "rationale": "identity on the carrier", "input": "species",
                            "output": "species", "check": "compare retained species"}
                           for i in range(2)],
                "realization": {"backend": "unsupported", "reason": "No chemical carrier adapter is installed."}}
        args = (["VINIT", "TANCH"], ["⊢", "⊣"], "⊢⊣", "N", "reaction vessel",
                None, True, "∅", None, "local", "test")
        with patch.object(exv.LlmBackend, "query", return_value=json.dumps(good)):
            rows, meta = exv.llm_translate(*args)
            self.assertEqual(len(rows), 2)
            self.assertEqual(rows[0]["check"], "compare retained species")
        malformed = [json.dumps(good)[:-2], '{"register":null,"tokens":[]}',
                     json.dumps({**good, "tokens": [good["tokens"][0]] * 2})]
        for raw in malformed:
            with self.subTest(raw=raw), patch.object(exv.LlmBackend, "query", return_value=raw):
                rows, meta = exv.llm_translate(*args)
                self.assertIsNone(rows)
                self.assertIn("error", meta)

    def test_known_carriers_keep_their_frame(self):
        anyon = exv.translate("⊢∈≻∋⊣", "anyon", offline=True)
        sic = exv.translate("⊢∈≻∋⊣", "sic", offline=True)
        self.assertIn("fifth", anyon["carrier"]["frame"])
        self.assertIn("Σ_i tr(X E_i) D_i", sic["carrier"]["return_check"])
        self.assertTrue(sic["rows"][1]["check"])
        self.assertNotEqual(sic["rows"][1]["input"], sic["rows"][1]["output"])

    def test_executable_evidence_forward_inverse_and_fuse(self):
        ops = exv.parse_word("⊢∈≻≺∋⊣")
        steps = [{"i": i, "op": op} for i, op in enumerate(ops)]
        steps[2]["permutation"] = ["q", "p"]
        plan = {"backend": "evidence", "frame": ["p", "q"],
                "seed": {"p": [True, False], "q": [False, True]}, "steps": steps}
        compiled = exv.compile_plan(plan, ops)
        witness = exv.execute_plan(compiled)
        self.assertTrue(witness["source_return"])
        self.assertTrue(witness["events"][4]["coordinate_return"])
        self.assertEqual(witness["events"][2]["after"]["q"], [True, False])
        # Same-sized non-bijections and invented shell fields must be rejected.
        for permutation in (["p", "p"], ["p", "missing"]):
            steps[2]["permutation"] = permutation
            with self.assertRaises(ValueError):
                exv.compile_plan(plan, ops)
        steps[2]["permutation"] = ["q", "p"]
        plan["shell"] = "anything"
        with self.assertRaises(ValueError):
            exv.compile_plan(plan, ops)

    def test_evidence_changes_keep_source_attribution_and_honest_return(self):
        ops = exv.parse_word("⊢∈⊞∋⊡⊣")
        steps = [{"i": i, "op": op} for i, op in enumerate(ops)]
        steps[2].update(proposition="p", support="sensor-A", refutation="sensor-B")
        compiled = exv.compile_plan({"backend": "evidence", "frame": ["p"],
                                    "seed": {"p": [False, False]}, "steps": steps}, ops)
        witness = exv.execute_plan(compiled)
        self.assertEqual(witness["final"], {"p": [True, True]})
        self.assertFalse(witness["source_return"])
        self.assertTrue(witness["events"][3]["coordinate_return"])
        self.assertEqual(witness["events"][2]["bindings"]["support"], "sensor-A")
        # Saved derived witnesses/commands cannot override adapter execution.
        compiled["argv"] = ["invented"]
        compiled["final"] = {"p": [False, False]}
        self.assertEqual(exv.execute_plan(compiled)["final"], {"p": [True, True]})

    def test_native_anyonic_sequence_uses_one_resident_carrier(self):
        ops = exv.parse_word("⊢≻≺⊣")
        steps = [{"i": i, "op": op} for i, op in enumerate(ops)]
        steps[1]["generators"] = [1, 2, -3]
        compiled = exv.compile_plan({"backend": "anyon-ququart",
                                    "source": str(2**128 + 51), "steps": steps}, ops)
        self.assertEqual(compiled["argv"][-6:], ["1", "2", "-3", "3", "-2", "-1"])
        witness = exv.execute_plan(compiled)
        self.assertEqual(witness["returncode"], 0)
        self.assertIn("outside-carrier mass", witness["stdout"])
        self.assertFalse(witness["inverse_residual_verified"])
        steps[1]["generators"] = [0]
        with self.assertRaises(ValueError):
            exv.compile_plan(compiled["plan"] | {"steps": steps}, ops)

    def test_missing_and_fabricated_model_realization_rejected(self):
        good = {"register": {k: "evidence" for k in ("name", "dim", "frame", "return_check")},
                "tokens": [{"i": i, **{k: "bound" for k in ("process", "concrete", "rationale", "input", "output", "check")}}
                           for i in range(2)]}
        args = (["VINIT", "TANCH"], ["⊢", "⊣"], "⊢⊣", "N", "evidence",
                None, True, "∅", None, "local", "test")
        for plan in (None, {"backend": "shell", "command": "invented"}):
            with patch.object(exv.LlmBackend, "query", return_value=json.dumps(good | {"realization": plan})):
                rows, meta = exv.llm_translate(*args)
                self.assertIsNone(rows)
                self.assertIn("unrealizable", meta["error"])

    def test_model_binding_repair_and_adapter_bound_explanation(self):
        ops = exv.parse_word("⊢∈⊙∋⊣")
        obj = {"register": {k: "FOUR" for k in ("name", "dim", "frame", "return_check")},
               "tokens": [{"i": i, **{k: "incorrect model explanation" for k in
                           ("process", "concrete", "rationale", "input", "output", "check")}} for i in range(len(ops))],
               "realization": {"backend": "evidence", "frame": ["p"], "seed": {"p": [True, False]},
                               "steps": [{"i": i, "op": op} for i, op in enumerate(ops)]}}
        args = (ops, list("⊢∈⊙∋⊣"), "⊢∈⊙∋⊣", "N", "FOUR evidence",
                None, True, "∅", None, "local", "test")
        broken = obj | {"realization": {"backend": "invented"}}
        with patch.object(exv.LlmBackend, "query", side_effect=[json.dumps(broken), json.dumps(obj)]) as query:
            rows, meta = exv.llm_translate(*args)
        self.assertEqual(query.call_count, 2)
        self.assertTrue(meta["binding_repair_attempted"])
        self.assertIn("support and refutation axes", rows[1]["concrete"])
        self.assertEqual(rows[1]["model_explanation"]["concrete"], "incorrect model explanation")
        self.assertTrue(exv.execute_plan(meta["realization"])["source_return"])

    def test_saved_example_replays_through_cli(self):
        proc = subprocess.run([sys.executable, exv.__file__, "--run-plan",
                               str(exv.Path(exv.HERE) / "evidence_return.plan.json")], capture_output=True, text=True)
        self.assertEqual(proc.returncode, 0, proc.stderr)
        self.assertEqual(json.loads(proc.stdout)["final"], {"p": [True, True], "q": [False, True]})

    def test_documented_complex_evidence_words(self):
        seed = {"p": [False, False], "q": [True, False], "r": [False, True]}
        cases = [
            ("⊢⊙∈≻⊤⋈≺∈⊥⊞⊙∋∋⊡⊣", seed,
             {3: {"permutation": ["q", "r", "p"]},
              4: {"proposition": "q", "witness": "sensor-A"},
              8: {"proposition": "q", "witness": "sensor-B"},
              9: {"proposition": "r", "support": "sensor-C", "refutation": "sensor-D"}},
             {"p": [True, False], "q": [True, True], "r": [True, True]}),
            ("⊢∈≻∈≻∈⊤⊥∋≺∋≺∋⊡⊣", seed,
             {2: {"permutation": ["q", "p", "r"]},
              4: {"permutation": ["p", "r", "q"]},
              6: {"proposition": "r", "witness": "inner-support"},
              7: {"proposition": "p", "witness": "inner-refutation"}},
             {"p": [True, False], "q": [True, True], "r": [False, True]}),
            ("⊢∈⊤∋⋈∈⊥⊞∋⊡⊣", {"alarm": [False, False], "backup": [False, False]},
             {2: {"proposition": "alarm", "witness": "detector-A"},
              6: {"proposition": "alarm", "witness": "detector-B"},
              7: {"proposition": "backup", "support": "backup-A", "refutation": "backup-B"}},
             {"alarm": [True, True], "backup": [True, True]}),
            ("⊢∈≻≻⊙≺≺∋⊡⊣", {"p": [True, False], "q": [False, True], "r": [False, False]},
             {2: {"permutation": ["q", "r", "p"]}, 3: {"permutation": ["q", "p", "r"]}},
             {"p": [True, False], "q": [False, True], "r": [False, False]}),
            ("⊢∈⊞⊡⊤⊥⊡∋⊡⊣", {"p": [False, False], "q": [False, False]},
             {2: {"proposition": "p", "support": "p-support", "refutation": "p-refutation"},
              4: {"proposition": "q", "witness": "q-support"},
              5: {"proposition": "q", "witness": "q-refutation"}},
             {"p": [True, True], "q": [True, True]}),
            ("⊢∈⊤⊤⋈⊥⊥⊙∋⊡⊣", {"p": [False, False]},
             {2: {"proposition": "p", "witness": "support-A"},
              3: {"proposition": "p", "witness": "support-B"},
              5: {"proposition": "p", "witness": "refutation-A"},
              6: {"proposition": "p", "witness": "refutation-B"}}, {"p": [True, True]}),
        ]
        for word, initial, bindings, expected in cases:
            with self.subTest(word=word):
                ops = exv.parse_word(word)
                steps = [{"i": i, "op": op, **bindings.get(i, {})} for i, op in enumerate(ops)]
                compiled = exv.compile_plan({"backend": "evidence", "frame": list(initial),
                                            "seed": initial, "steps": steps}, ops)
                actual = exv.execute_plan(compiled)
                self.assertEqual(actual["final"], expected)
                self.assertEqual(actual["source_return"], initial == expected)
                fuses = [e for e in actual["events"] if e["op"] == "FFUSE"]
                self.assertTrue(all(e["coordinate_return"] for e in fuses))
                self.assertTrue(all(e["source_return"] == (initial == expected) for e in fuses))
                self.assertEqual(exv.judge(word)[0], "T")
                if word == "⊢∈⊞⊡⊤⊥⊡∋⊡⊣":
                    self.assertEqual(actual["events"][3]["latched"], {"p": [True, True], "q": [False, False]})
                    self.assertEqual(actual["events"][6]["latched"], expected)

    def test_documented_complex_native_sequences(self):
        cases = [
            ("⊢⊙≻≻⊙≺≺⊙⊣", {2: [1, 2, -3], 3: [4, -5, 2]},
             [1, 2, -3, 4, -5, 2, -2, 5, -4, 3, -2, -1]),
            ("⊢≻⊙≺≻⊙≺⊣", {1: [2, 3, 2], 4: [5, -4, 1, -2]},
             [2, 3, 2, -2, -3, -2, 5, -4, 1, -2, 2, -1, 4, -5]),
        ]
        for word, bindings, expected in cases:
            with self.subTest(word=word):
                ops = exv.parse_word(word)
                steps = [{"i": i, "op": op, **({"generators": bindings[i]} if i in bindings else {})}
                         for i, op in enumerate(ops)]
                compiled = exv.compile_plan({"backend": "anyon-ququart", "source": str(2**128 + 51),
                                            "steps": steps}, ops)
                self.assertEqual(compiled["argv"][3:], list(map(str, expected)))
                self.assertEqual(exv.execute_plan(compiled)["returncode"], 0)
                self.assertEqual(exv.judge(word)[0], "N")

    def test_usage_document_has_no_token_names(self):
        doc = (exv.Path(exv.HERE) / "USAGE.md").read_text()
        for name in exv._GL.values():
            self.assertNotIn(name, doc)


if __name__ == "__main__":
    unittest.main()
