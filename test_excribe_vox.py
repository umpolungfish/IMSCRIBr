"""Exercise excription boundaries against the real Vox word reader."""
import json
import subprocess
import sys
import unittest
from unittest.mock import patch

import excribe_vox as exv


class ExcriptionTests(unittest.TestCase):
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
