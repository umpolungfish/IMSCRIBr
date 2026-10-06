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
                           for i in range(2)]}
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


if __name__ == "__main__":
    unittest.main()
