#!/usr/bin/env python3
from __future__ import annotations

import argparse
import re
import shutil
import subprocess
from pathlib import Path


PALETTE = [
    "#93c5fd",
    "#86efac",
    "#fca5a5",
    "#fcd34d",
    "#c4b5fd",
    "#67e8f9",
    "#f9a8d4",
    "#bef264",
]


def parse_test_input(path: Path) -> tuple[int, list[tuple[int, int, int]]]:
    tokens = [int(x) for x in path.read_text(encoding="utf-8").split()]
    if len(tokens) < 2:
        raise ValueError(f"{path}: expected at least n and m")

    n = tokens[0]
    m = tokens[1]
    idx = 2
    edges: list[tuple[int, int, int]] = []

    for _ in range(m):
        if idx + 2 >= len(tokens):
            raise ValueError(f"{path}: not enough tokens for edges")
        u = tokens[idx]
        v = tokens[idx + 1]
        w = tokens[idx + 2]
        edges.append((u, v, w))
        idx += 3

    return n, edges


def parse_test_output(path: Path) -> dict[int, int]:
    owner: dict[int, int] = {}
    pattern = re.compile(r"^Государство\s+(\d+):\s*(.*)$")

    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line:
            continue
        match = pattern.match(line)
        if not match:
            continue
        state = int(match.group(1))
        tail = match.group(2).strip()
        if not tail:
            continue
        for city_str in tail.split():
            owner[int(city_str)] = state
    return owner


def color_for_state(state: int) -> str:
    if state <= 0:
        return "#e5e7eb"
    return PALETTE[(state - 1) % len(PALETTE)]


def build_dot(test_name: str, n: int, edges: list[tuple[int, int, int]], owner: dict[int, int]) -> str:
    lines: list[str] = []
    lines.append("graph G {")
    lines.append('  graph [labeljust="l", labelloc="t", fontsize=20, fontname="Arial", '
                 f'label="Cities: {test_name}"];')
    lines.append('  node [shape=circle, style=filled, fontname="Arial", fontsize=12, penwidth=1.3];')
    lines.append('  edge [fontname="Arial", fontsize=11, color="#4b5563"];')
    lines.append("")

    for v in range(1, n + 1):
        state = owner.get(v, 0)
        fill = color_for_state(state)
        label = f"{v}\\nS{state}" if state > 0 else str(v)
        lines.append(f'  {v} [label="{label}", fillcolor="{fill}"];')

    lines.append("")
    for i, (u, v, w) in enumerate(edges, start=1):
        lines.append(f'  {u} -- {v} [label="{w}", xlabel="e{i}"];')

    # Legend
    if owner:
        states = sorted(set(owner.values()))
        lines.append("")
        lines.append("  subgraph cluster_legend {")
        lines.append('    label="Legend"; fontsize=14; fontname="Arial"; color="#d1d5db";')
        for s in states:
            color = color_for_state(s)
            lines.append(f'    legend_{s} [shape=box, style=filled, fillcolor="{color}", '
                         f'label="S{s}", width=0.7, height=0.35, fixedsize=true];')
        for a, b in zip(states, states[1:]):
            lines.append(f"    legend_{a} -- legend_{b} [style=invis];")
        lines.append("  }")

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DOT/PNG visualizations for Cities tests.")
    parser.add_argument(
        "--tests-dir",
        default=str((Path(__file__).resolve().parent / "../Code/tests").resolve()),
        help="Path to tests directory containing test*.in and test*.out",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent),
        help="Where to place generated .dot/.png files",
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
        test_name = in_path.stem
        out_path = tests_dir / f"{test_name}.out"
        if not out_path.exists():
            raise FileNotFoundError(f"Missing expected output for {in_path.name}: {out_path.name}")

        n, edges = parse_test_input(in_path)
        owner = parse_test_output(out_path)
        dot_text = build_dot(test_name, n, edges, owner)

        dot_path = output_dir / f"{test_name}.dot"
        dot_path.write_text(dot_text, encoding="utf-8")

        if dot_bin:
            png_path = output_dir / f"{test_name}.png"
            subprocess.run([dot_bin, "-Tpng", str(dot_path), "-o", str(png_path)], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
