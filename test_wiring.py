"""Port conservation and nesting regressions for the standard wiring builder."""
import itertools
import re
import unittest

from tokens import Token
from wiring import Wire, WiredGraph, imscr_wiring


def graph(names):
    return imscr_wiring(tuple(Token[name] for name in names.split()))


class WiringTest(unittest.TestCase):
    def test_cycle_is_explicit_and_can_still_be_rendered(self):
        from native_wiring import inspect_wiring
        from symbolic_diagram import render_wiring_svg_v3
        g = WiredGraph((Token.AFWD, Token.CLINK), [Wire(0, "o", 1, "i"), Wire(1, "o", 0, "i")])
        self.assertEqual(g.validate(), [])
        with self.assertRaisesRegex(ValueError, "directed cycle"):
            g.topological_layers()
        self.assertIsNotNone(render_wiring_svg_v3(g, graph_report=inspect_wiring(g)))
        bad = WiredGraph((Token.AFWD,), [Wire(-1, "o", 0, "i")])
        for method in (bad.cross_branch_wires, bad.topological_layers):
            with self.assertRaisesRegex(ValueError, "out of range"):
                method()

    def test_svg_binds_native_carriers_without_inventing_a_return_edge(self):
        import json
        import xml.etree.ElementTree as ET
        from native_wiring import inspect_wiring
        from symbolic_diagram import render_wiring_svg_v3
        g = graph("VINIT FSPLIT AREV FFUSE TANCH")
        report = inspect_wiring(g)
        for pen in (False, True):
            svg = render_wiring_svg_v3(g, ourobor="O₃", pen_mode=pen, graph_report=report)
            xml = ET.fromstring("\n".join(svg.parts))
            ns = {"s": "http://www.w3.org/2000/svg"}
            bound = json.loads(xml.find("s:metadata", ns).text)
            self.assertEqual(bound, report)
            texts = [e.text for e in xml.findall("s:text", ns)]
            self.assertIn("Ff", texts)
            self.assertIn("Tt", texts)
            self.assertTrue(any("ancestry CLOSED" in (t or "") for t in texts))
            plain = render_wiring_svg_v3(g, pen_mode=pen, graph_report=report)
            # A tuple tier is not an extra wire from the terminal to the source.
            base = ET.fromstring("\n".join(plain.parts))
            self.assertEqual(len(xml.findall("s:path", ns)), len(base.findall("s:path", ns)))
            g.wires.reverse()
            with self.assertRaisesRegex(ValueError, "different wiring"):
                render_wiring_svg_v3(g, pen_mode=pen, graph_report=report)
            g.wires.reverse()

    def test_cross_overrides_cannot_be_silently_dropped_or_overwritten(self):
        from wiring import cross_wiring
        tokens = graph("VINIT FSPLIT EVALT FFUSE TANCH").tokens
        for overrides in ([(1, "missing", 3, "F")], [(1, "F", -1, "i")],
                          [(1, "F", 0, "i")], [(1, "F", 3, "F")] * 2):
            with self.subTest(overrides=overrides), self.assertRaises(ValueError):
                cross_wiring(tokens, overrides)
    def test_native_flow_preserves_named_ports_and_wire_permutations(self):
        from native_wiring import inspect_wiring
        g = graph("VINIT FSPLIT EVALF EVALT FFUSE TANCH")
        for seed in range(16):
            report = inspect_wiring(g, seed)
            reversed_graph = WiredGraph(g.tokens, list(reversed(g.wires)))
            other = inspect_wiring(reversed_graph, seed)
            self.assertEqual(report["node_inputs"], other["node_inputs"])
            self.assertEqual(report["node_inputs"][2:4], [seed & 10, seed & 5])
            self.assertEqual(report["node_inputs"][-1], seed)
            self.assertEqual(report["pairs"], [[1, 4]])
            self.assertEqual(report["pair_recovers_input"], [True])
            self.assertEqual(report["edge_values"], list(reversed(other["edge_values"])))

    def test_native_reports_actual_ancestry_and_loss_separately(self):
        from native_wiring import inspect_wiring
        g = graph("VINIT FSPLIT AREV FFUSE TANCH")
        report = inspect_wiring(g)
        self.assertTrue(report["closure_verified"])
        self.assertEqual(report["pair_recovers_input"], [False])
        # Change only the wires: the fuse no longer has two ancestral inputs.
        g.wires = [w for w in g.wires if (w.src_node, w.src_port) != (1, "T")]
        other = inspect_wiring(g)
        self.assertEqual(other["closure"], "open")
        self.assertEqual(other["pairs"], [])

    def test_native_open_f_slot_is_not_reinterpreted_as_t(self):
        from native_wiring import inspect_wiring
        g = WiredGraph((Token.VINIT, Token.FSPLIT, Token.TANCH),
                       [Wire(0, "o", 1, "i"), Wire(1, "F", 2, "i")])
        report = inspect_wiring(g)
        self.assertEqual(report["node_inputs"][-1], 10)
        self.assertEqual(report["closure"], "open")
        g.wires.append(Wire(1, "F", 2, "i"))
        with self.assertRaises(ValueError):
            inspect_wiring(g)

    def test_ascii_uses_bound_edge_flow_and_never_counts_pairs_as_closure(self):
        from native_wiring import inspect_wiring
        from symbolic_diagram import render_wiring_ascii
        g = graph("VINIT FSPLIT AREV FFUSE TANCH")
        report = inspect_wiring(g)
        text = render_wiring_ascii(g, graph_report=report)
        self.assertIn("Native ancestry: CLOSED", text)
        self.assertIn("[T→T]  Tt", text)
        self.assertIn("[F→i]  Ff", text)
        fallback = render_wiring_ascii(g)
        self.assertNotIn("CLOSED", fallback)
        self.assertIn("unchecked", fallback)
        self.assertIn("unchecked", render_wiring_ascii(WiredGraph((), [])))
        g.wires.reverse()
        with self.assertRaisesRegex(ValueError, "different wiring"):
            render_wiring_ascii(g, graph_report=report)

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
