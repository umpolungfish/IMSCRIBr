"""Port conservation and nesting regressions for the standard wiring builder."""
import itertools
import re
import unittest

from tokens import Token
from wiring import Wire, WiredGraph, imscr_wiring


def graph(names):
    return imscr_wiring(tuple(Token[name] for name in names.split()))


class WiringTest(unittest.TestCase):
    def test_nested_block_stays_between_its_enclosing_arm_operations(self):
        g = graph("VINIT FSPLIT EVALT FSPLIT EVALT EVALF FFUSE CLINK EVALF FFUSE TANCH")
        self.assertEqual(g.validate(), [])
        for w in (Wire(1, "T", 2, "i"), Wire(2, "o", 3, "i"),
                  Wire(6, "o", 7, "i"), Wire(7, "o", 9, "T")):
            self.assertIn(w, g.wires)

    def test_nested_block_can_occur_on_either_arm(self):
        for names in (
            "VINIT FSPLIT EVALT EVALF FSPLIT EVALT EVALF FFUSE AREV FFUSE TANCH",
            "VINIT FSPLIT FSPLIT EVALT EVALF FFUSE FFUSE TANCH",
            "VINIT FSPLIT EVALT FSPLIT EVALT FFUSE FSPLIT EVALF FFUSE EVALF FFUSE TANCH",
        ):
            with self.subTest(names=names):
                self.assertEqual(graph(names).validate(), [])

    def test_combinations_preserve_every_nested_segment_and_port(self):
        blocks = ("IMSCRIB", "FSPLIT EVALT EVALF FFUSE",
                  "FSPLIT FSPLIT EVALT FFUSE EVALF FFUSE")
        for left, right in itertools.product(blocks, repeat=2):
            g = graph(f"VINIT FSPLIT EVALT {left} CLINK EVALF {right} AREV FFUSE TANCH")
            with self.subTest(left=left, right=right):
                self.assertEqual(g.validate(), [])
                self.assertEqual(sum(map(len, g.topological_layers())), g.n())

    def test_negative_indices_are_invalid_instead_of_python_indexing(self):
        g = WiredGraph((Token.AFWD, Token.TANCH), [Wire(-1, "o", 0, "i")])
        self.assertTrue(any("out of range" in e for e in g.validate()))

    def test_open_fork_keeps_declared_ports(self):
        g = graph("VINIT FSPLIT EVALT TANCH")
        self.assertIn(Wire(1, "T", 2, "i"), g.wires)
        self.assertFalse(any("no out-port" in e for e in g.validate()))
        self.assertTrue(any("unconnected out-port (1,F)" in e for e in g.validate()))

    def test_scaffold_retains_every_operation_and_nested_product(self):
        from proof_scaffold import emit_scaffold
        names = "VINIT FSPLIT EVALT FSPLIT EVALT EVALF FFUSE CLINK EVALF FFUSE TANCH"
        tokens = tuple(Token[n] for n in names.split())
        text = emit_scaffold(tokens, name="nested_audit")
        body = text.split("-- ── Main IGProtocol term", 1)[1].split("-- ── Evaluation arm", 1)[0]
        self.assertEqual(sorted(map(int, re.findall(r"\.arrow nested_audit_l(\d+)\b", body))),
                         list(range(len(tokens))))
        self.assertEqual(body.count("(.prod "), 2)
        self.assertNotIn("Dual-Link self-pairing", body)
        self.assertTrue(text.rstrip().endswith("end Imscribing"))


if __name__ == "__main__":
    unittest.main()
