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


def intersects(a1: int, b1: int, a2: int, b2: int) -> bool:
    return max(a1, a2) < min(b1, b2)


def parse_test_input(path: Path) -> tuple[int, list[dict[str, int]], int]:
    lines = [line.strip() for line in path.read_text(encoding="utf-8").splitlines() if line.strip()]
    head = [int(x) for x in lines[0].split()]
    if len(head) not in (2, 3):
        raise ValueError(f"{path}: header must be 'n m' or 'n m T'")

    n = head[0]
    m = head[1]
    global_t = head[2] if len(head) == 3 else -1

    edges: list[dict[str, int]] = []
    max_finish = 0
    for i in range(1, 1 + m):
        values = [int(x) for x in lines[i].split()]
        if len(values) not in (4, 5):
            raise ValueError(f"{path}: edge line {i} must contain 4 or 5 integers")

        if len(values) == 4:
            u, v, t1, t2 = values
            edge_len = t2 - t1
        else:
            u, v, edge_len, t1, t2 = values

        edges.append(
            {
                "u": u,
                "v": v,
                "len": edge_len,
                "start": t1,
                "finish": t2,
            }
        )
        max_finish = max(max_finish, t2)

    if global_t < 0:
        global_t = max_finish

    return n, edges, global_t


def parse_test_output(path: Path) -> list[dict[str, object]]:
    ticks: list[dict[str, object]] = []
    current = None
    tick_re = re.compile(r"^Такт\s+\[(\d+),\s*(\d+)\):$")
    group_re = re.compile(r"^\s*Группировка\s+(\d+):\s*(.*)$")

    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.rstrip()
        if not line:
            continue

        tm = tick_re.match(line)
        if tm:
            if current is not None:
                ticks.append(current)
            current = {"start": int(tm.group(1)), "finish": int(tm.group(2)), "groups": {}}
            continue

        gm = group_re.match(line)
        if gm and current is not None:
            gid = int(gm.group(1))
            cities = [int(x) for x in gm.group(2).split()] if gm.group(2).strip() else []
            current["groups"][gid] = cities

    if current is not None:
        ticks.append(current)

    return ticks


def color_for_group(group_id: int) -> str:
    if group_id <= 0:
        return "#e5e7eb"
    return PALETTE[(group_id - 1) % len(PALETTE)]


def build_owner_map(groups: dict[int, list[int]]) -> dict[int, int]:
    owner: dict[int, int] = {}
    for gid, members in groups.items():
        for node in members:
            owner[node] = gid
    return owner


def build_dot(
    test_name: str,
    tick_start: int,
    tick_finish: int,
    n: int,
    edges: list[dict[str, int]],
    groups: dict[int, list[int]],
) -> str:
    owner = build_owner_map(groups)
    lines: list[str] = []
    lines.append("graph G {")
    lines.append(
        '  graph [labeljust="l", labelloc="t", fontsize=18, fontname="Arial", '
        f'label="KA Groupings: {test_name}; tick [{tick_start}, {tick_finish})"];'
    )
    lines.append('  node [shape=circle, style=filled, fontname="Arial", fontsize=11, penwidth=1.3];')
    lines.append('  edge [fontname="Arial", fontsize=10];')
    lines.append("")

    for v in range(1, n + 1):
        gid = owner.get(v, 0)
        fill = color_for_group(gid)
        label = f"{v}\\nG{gid}" if gid > 0 else str(v)
        lines.append(f'  {v} [label="{label}", fillcolor="{fill}", color="#1f2937"];')

    lines.append("")
    for i, e in enumerate(edges, start=1):
        u = e["u"]
        v = e["v"]
        edge_label = f'{e["len"]} [{e["start"]},{e["finish"]}]'
        active = intersects(e["start"], e["finish"], tick_start, tick_finish)
        if active:
            lines.append(
                f'  {u} -- {v} [label="{edge_label}", xlabel="e{i}", color="#0f172a", penwidth=2.0];'
            )
        else:
            lines.append(
                f'  {u} -- {v} [label="{edge_label}", xlabel="e{i}", color="#9ca3af", style=dashed];'
            )

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DOT/PNG visualizations for KA_Groupings tests.")
    parser.add_argument(
        "--tests-dir",
        default=str((Path(__file__).resolve().parent / "../Code/tests").resolve()),
        help="Path to test*.in/test*.out files",
    )
    parser.add_argument(
        "--output-dir",
        default=str(Path(__file__).resolve().parent),
        help="Output directory",
    )
    parser.add_argument(
        "--require-dot",
        action="store_true",
        help="Fail if Graphviz 'dot' is not available",
    )
    args = parser.parse_args()

    tests_dir = Path(args.tests_dir)
    output_dir = Path(args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    dot_bin = shutil.which("dot")
    if args.require_dot and not dot_bin:
        raise FileNotFoundError("Graphviz 'dot' was not found in PATH.")

    input_files = sorted(tests_dir.glob("test*.in"))
    if not input_files:
        raise FileNotFoundError(f"No test inputs in {tests_dir}")

    for in_path in input_files:
        test_name = in_path.stem
        out_path = tests_dir / f"{test_name}.out"
        if not out_path.exists():
            raise FileNotFoundError(f"Missing {out_path.name} for {in_path.name}")

        n, edges, _ = parse_test_input(in_path)
        ticks = parse_test_output(out_path)
        for tick in ticks:
            t1 = int(tick["start"])
            t2 = int(tick["finish"])
            groups = tick["groups"]
            dot_text = build_dot(test_name, t1, t2, n, edges, groups)
            stem = f"{test_name}_tick_{t1}_{t2}"

            dot_path = output_dir / f"{stem}.dot"
            dot_path.write_text(dot_text, encoding="utf-8")

            if dot_bin:
                png_path = output_dir / f"{stem}.png"
                subprocess.run([dot_bin, "-Tpng", str(dot_path), "-o", str(png_path)], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
