#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


def parse_test_input(path: Path) -> tuple[int, list[tuple[int, int, int]]]:
    tokens = [int(x) for x in path.read_text(encoding="utf-8").split()]
    if len(tokens) < 2:
        raise ValueError(f"{path}: expected n m")

    n = tokens[0]
    m = tokens[1]
    idx = 2
    edges: list[tuple[int, int, int]] = []

    for _ in range(m):
        if idx + 2 >= len(tokens):
            raise ValueError(f"{path}: not enough edge tokens")
        u = tokens[idx]
        v = tokens[idx + 1]
        w = tokens[idx + 2]
        edges.append((u, v, w))
        idx += 3

    return n, edges


def parse_test_output(path: Path) -> tuple[int | None, int | None, int | None, list[tuple[int, int, int]]]:
    text = path.read_text(encoding="utf-8")
    sum_edges = None
    extra = None
    total = None
    pairs: list[tuple[int, int, int]] = []

    m = re.search(r"Сумма длин всех ребер:\s*(\d+)", text)
    if m:
        sum_edges = int(m.group(1))
    m = re.search(r"Добавочная длина:\s*(\d+)", text)
    if m:
        extra = int(m.group(1))
    m = re.search(r"Минимальная длина маршрута почтальона:\s*(\d+)", text)
    if m:
        total = int(m.group(1))

    pair_re = re.compile(r"^\s*(\d+)\s*-\s*(\d+)\s*\(кратчайший путь\s*=\s*(\d+)\)\s*$")
    for line in text.splitlines():
        mm = pair_re.match(line)
        if mm:
            pairs.append((int(mm.group(1)), int(mm.group(2)), int(mm.group(3))))

    return sum_edges, extra, total, pairs


def compute_odd_vertices(n: int, edges: list[tuple[int, int, int]]) -> set[int]:
    deg = [0] * (n + 1)
    for u, v, _ in edges:
        deg[u] += 1
        deg[v] += 1
    return {v for v in range(1, n + 1) if deg[v] % 2 == 1}


def build_dot(
    test_name: str,
    n: int,
    edges: list[tuple[int, int, int]],
    odd: set[int],
    sum_edges: int | None,
    extra: int | None,
    total: int | None,
    pairs: list[tuple[int, int, int]],
) -> str:
    lines: list[str] = []
    lines.append("graph G {")

    label_parts = [f"Chinese Postman: {test_name}"]
    if sum_edges is not None and extra is not None and total is not None:
        label_parts.append(f"sum={sum_edges}, extra={extra}, total={total}")
    if odd:
        label_parts.append("odd vertices: " + ", ".join(str(v) for v in sorted(odd)))

    lines.append(
        '  graph [labeljust="l", labelloc="t", fontsize=18, fontname="Arial", '
        f'label="{"; ".join(label_parts)}"];'
    )
    lines.append('  node [shape=circle, style=filled, fontname="Arial", fontsize=12, penwidth=1.5];')
    lines.append('  edge [fontname="Arial", fontsize=11, color="#4b5563"];')
    lines.append("")

    for v in range(1, n + 1):
        if v in odd:
            lines.append(f'  {v} [fillcolor="#fee2e2", color="#dc2626", label="{v}\\nodd"];')
        else:
            lines.append(f'  {v} [fillcolor="#dbeafe", color="#1d4ed8", label="{v}"];')

    lines.append("")
    for i, (u, v, w) in enumerate(edges, start=1):
        lines.append(f'  {u} -- {v} [label="{w}", xlabel="e{i}"];')

    if pairs:
        lines.append("")
        lines.append("  // Added shortest-path pairings for odd-degree vertices")
        for u, v, d in pairs:
            lines.append(
                f'  {u} -- {v} [color="#dc2626", penwidth=2.4, style=dashed, '
                f'label="+{d}", constraint=false];'
            )

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DOT/PNG visualizations for Chinese Postman tests.")
    parser.add_argument(
        "--tests-dir",
        default=str((Path(__file__).resolve().parent / "../Code/tests").resolve()),
        help="Path to tests directory containing test*.in and test*.out",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent),
        help="Output directory for generated files",
    )
    parser.add_argument(
        "--require-dot",
        action="store_true",
        help="Fail if Graphviz 'dot' is unavailable",
    )
    args = parser.parse_args()

    tests_dir = Path(args.tests_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dot_bin = shutil.which("dot")
    if args.require_dot and not dot_bin:
        raise FileNotFoundError("Graphviz 'dot' was not found in PATH.")

    test_inputs = sorted(tests_dir.glob("test*.in"))
    if not test_inputs:
        raise FileNotFoundError(f"No test*.in found in {tests_dir}")

    for in_path in test_inputs:
        name = in_path.stem
        out_path = tests_dir / f"{name}.out"
        if not out_path.exists():
            raise FileNotFoundError(f"Missing {out_path.name} for {in_path.name}")

        n, edges = parse_test_input(in_path)
        sum_edges, extra, total, pairs = parse_test_output(out_path)
        odd = compute_odd_vertices(n, edges)
        dot_text = build_dot(name, n, edges, odd, sum_edges, extra, total, pairs)

        dot_path = output_dir / f"{name}.dot"
        dot_path.write_text(dot_text, encoding="utf-8")

        if dot_bin:
            png_path = output_dir / f"{name}.png"
            subprocess.run([dot_bin, "-Tpng", str(dot_path), "-o", str(png_path)], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
