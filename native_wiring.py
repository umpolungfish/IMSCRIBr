"""Bind an explicit port graph to the canonical native checker and flow engine."""
import hashlib
import json
from pathlib import Path
import subprocess
import tempfile

from tokens import Token
from wiring import out_ports, in_ports

_ROOT = Path(__file__).resolve().parent
_CORE = _ROOT.parent / "MoDoT" / "imasm_core" / "src"


def _instrument():
    sources = sorted(_CORE.glob("*.rs")) + [_ROOT / "native" / "wiring_probe.rs"]
    digest = hashlib.sha256()
    for path in sources:
        digest.update(path.name.encode())
        digest.update(path.read_bytes())
    binding = digest.hexdigest()
    cache = _ROOT / "native" / "build"
    cache.mkdir(parents=True, exist_ok=True)
    target = cache / ("wiring_probe_" + binding)
    if not target.exists():
        # Separate build directories prevent concurrent callers sharing outputs.
        with tempfile.TemporaryDirectory(dir=cache) as folder:
            lib = Path(folder) / "libimasm_core.rlib"
            for args in (
                ["--crate-name", "imasm_core", "--crate-type", "rlib", str(_CORE / "lib.rs"), "-o", str(lib)],
                [str(sources[-1]), "--extern", f"imasm_core={lib}", "-o", str(Path(folder) / "probe")],
            ):
                subprocess.run(["rustc", "--edition=2021", *args], check=True,
                               capture_output=True, text=True, timeout=120)
            (Path(folder) / "probe").replace(target)
    return target, binding


def inspect_wiring(graph, seed=15):
    """Return native ancestry and flow for this graph, preserving named T/F ports.

    Open valences are observations. Invalid indices, port names or duplicate
    bindings are rejected before native execution. Native slot order is T,F;
    insert an unused sink edge for a missing fork slot so F cannot become T.
    """
    if type(seed) is not int or not 0 <= seed < 16:
        raise ValueError("seed must be a four-bit register")
    n = graph.n()
    used_src, used_dst = set(), set()
    for w in graph.wires:
        if not (0 <= w.src_node < n and 0 <= w.dst_node < n):
            raise ValueError(f"node index out of range: {w}")
        src, dst = (w.src_node, w.src_port), (w.dst_node, w.dst_port)
        if (w.src_port not in out_ports(graph.tokens[w.src_node]) or
                w.dst_port not in in_ports(graph.tokens[w.dst_node]) or
                src in used_src or dst in used_dst):
            raise ValueError(f"invalid or duplicate port binding: {w}")
        used_src.add(src)
        used_dst.add(dst)
    ordered = sorted(enumerate(graph.wires), key=lambda item:
                     (item[1].src_node, out_ports(graph.tokens[item[1].src_node]).index(item[1].src_port)))
    nodes = [t.name for t in graph.tokens]
    edges, original = [], []
    for i in range(n):
        by_port = {w.src_port: (index, w) for index, w in ordered if w.src_node == i}
        for port in out_ports(graph.tokens[i]):
            if port in by_port:
                index, w = by_port[port]
                edges.append((i, w.dst_node))
                original.append(index)
            elif graph.tokens[i] == Token.FSPLIT:
                edges.append((i, len(nodes)))
                nodes.append("TANCH")
                original.append(None)
    target, binding = _instrument()
    payload = f"{seed}\n{' '.join(nodes)}\n" + "".join(f"{a} {b}\n" for a,b in edges)
    result = subprocess.run([str(target)], input=payload, capture_output=True,
                            text=True, check=True, timeout=30)
    report = json.loads(result.stdout)
    values = [None] * len(graph.wires)
    for index, value in zip(original, report["edge_values"]):
        if index is not None:
            values[index] = value
    report["edge_values"] = values
    report["node_inputs"] = report["node_inputs"][:n]
    report.update(status="checked", instrument="imasm_core::check + imasm_core::flow",
                  source_sha256=binding, seed=seed, port_observations=graph.validate(),
                  nodes=[t.name for t in graph.tokens],
                  wires=[[w.src_node,w.src_port,w.dst_node,w.dst_port] for w in graph.wires])
    return report
