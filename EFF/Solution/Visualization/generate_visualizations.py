#!/usr/bin/env python3
from __future__ import annotations

import argparse
import shutil
import subprocess
from dataclasses import dataclass
from pathlib import Path


@dataclass
class Production:
    lhs: str
    rhs: str


def trim(s: str) -> str:
    return s.strip()


def is_eps_token(s: str) -> bool:
    t = trim(s)
    return t == "" or t.lower() in {"eps", "epsilon"}


def normalize_symbols(s: str) -> str:
    return "".join(ch for ch in s if not ch.isspace())


def split_by_bar(rhs: str) -> list[str]:
    parts: list[str] = []
    cur = []
    for ch in rhs:
        if ch == "|":
            parts.append("".join(cur).strip())
            cur.clear()
        else:
            cur.append(ch)
    parts.append("".join(cur).strip())
    return parts


def parse_production(line: str) -> list[Production]:
    if "->" not in line:
        raise ValueError(f"Bad production line: {line}")
    left, right = line.split("->", 1)
    lhs = trim(left)
    if len(lhs) != 1 or not lhs.isupper():
        raise ValueError(f"LHS must be one nonterminal A..Z: {line}")
    prods: list[Production] = []
    for alt in split_by_bar(right):
        rhs = "" if is_eps_token(alt) else normalize_symbols(alt)
        prods.append(Production(lhs=lhs, rhs=rhs))
    return prods


def parse_input(path: Path) -> tuple[int, list[Production], str]:
    lines = [trim(x) for x in path.read_text(encoding="utf-8").splitlines()]
    lines = [x for x in lines if x and not x.startswith("#")]
    if len(lines) < 4:
        raise ValueError(f"{path}: expected at least 4 meaningful lines")

    k = int(lines[0])
    p = int(lines[1])
    if p <= 0:
        raise ValueError(f"{path}: p must be positive")
    if len(lines) < 2 + p + 1:
        raise ValueError(f"{path}: not enough lines for {p} productions and alpha")

    productions: list[Production] = []
    for i in range(p):
        productions.extend(parse_production(lines[2 + i]))
    alpha_raw = lines[2 + p]
    alpha = "" if is_eps_token(alpha_raw) else normalize_symbols(alpha_raw)
    return k, productions, alpha


def parse_eff_set(path: Path) -> set[str]:
    lines = [x.strip() for x in path.read_text(encoding="utf-8").splitlines()]
    eff: set[str] = set()
    for i, line in enumerate(lines):
        if line == "EFF:" and i + 1 < len(lines):
            words = lines[i + 1].strip()
            if words == "∅" or words == "":
                return eff
            for token in words.split():
                eff.add("" if token == "ε" else token)
            return eff
    raise ValueError(f"{path}: cannot find EFF section")


def rightmost_nonterminal_pos(form: str) -> int:
    for i in range(len(form) - 1, -1, -1):
        if form[i].isupper():
            return i
    return -1


def all_terminals(form: str) -> bool:
    return all(not ch.isupper() for ch in form)


def pref_k(s: str, k: int) -> str:
    return s if len(s) <= k else s[:k]


def printable(s: str) -> str:
    return "ε" if s == "" else s


def escape_label(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def build_derivation_graph(
    k: int, productions: list[Production], alpha: str, eff_set: set[str]
) -> tuple[dict[str, int], list[tuple[str, str, str]], dict[str, str]]:
    by_lhs: dict[str, list[Production]] = {}
    for p in productions:
        by_lhs.setdefault(p.lhs, []).append(p)

    node_id: dict[str, int] = {alpha: 0}
    edges: list[tuple[str, str, str]] = []
    states = [alpha]
    expanded: set[str] = set()

    max_forms = 250
    max_form_len = max(64, 4 * k + 16)

    while states:
        cur = states.pop()
        if all_terminals(cur):
            continue
        if cur in expanded:
            continue
        expanded.add(cur)

        pos = rightmost_nonterminal_pos(cur)
        if pos < 0:
            continue
        nt = cur[pos]
        for p in by_lhs.get(nt, []):
            nxt = cur[:pos] + p.rhs + cur[pos + 1 :]
            if len(nxt) > max_form_len:
                continue
            if nxt not in node_id and len(node_id) < max_forms:
                node_id[nxt] = len(node_id)
                states.append(nxt)
            if nxt in node_id:
                rhs_print = printable(p.rhs)
                edges.append((cur, nxt, f"{nt}->{rhs_print}"))

    node_style: dict[str, str] = {}
    for form in node_id:
        if all_terminals(form):
            p = pref_k(form, k)
            if p in eff_set:
                node_style[form] = "#bbf7d0"
            else:
                node_style[form] = "#e5e7eb"
        else:
            node_style[form] = "#dbeafe"
    return node_id, edges, node_style


def build_dot(
    test_name: str,
    k: int,
    alpha: str,
    eff_set: set[str],
    node_id: dict[str, int],
    edges: list[tuple[str, str, str]],
    node_style: dict[str, str],
) -> str:
    lines: list[str] = []
    lines.append("digraph G {")
    lines.append(
        '  graph [labeljust="l", labelloc="t", fontsize=20, fontname="Arial", '
        f'label="EFF rightmost derivations: {test_name}"];'
    )
    lines.append('  rankdir=TB;')
    lines.append('  node [shape=box, style=filled, fontname="Arial", fontsize=11, color="#374151"];')
    lines.append('  edge [fontname="Arial", fontsize=10, color="#6b7280"];')
    lines.append("")

    for form, idx in sorted(node_id.items(), key=lambda x: x[1]):
        label = escape_label(printable(form))
        fill = node_style[form]
        penwidth = "2.0" if form == alpha else "1.2"
        lines.append(
            f'  n{idx} [label="{label}", fillcolor="{fill}", penwidth={penwidth}];'
        )

    lines.append("")
    for src, dst, lab in edges:
        lines.append(f'  n{node_id[src]} -> n{node_id[dst]} [label="{escape_label(lab)}"];')

    eff_words = " ".join(printable(x) for x in sorted(eff_set))
    if not eff_words:
        eff_words = "∅"

    lines.append("")
    lines.append("  subgraph cluster_legend {")
    lines.append('    label="Legend"; fontsize=13; fontname="Arial"; color="#d1d5db";')
    lines.append('    key_nonterm [shape=box, style=filled, fillcolor="#dbeafe", label="sentential form"];')
    lines.append('    key_eff [shape=box, style=filled, fillcolor="#bbf7d0", label="terminal leaf, prefix in EFF"];')
    lines.append('    key_filtered [shape=box, style=filled, fillcolor="#e5e7eb", label="terminal leaf, filtered"];')
    lines.append('    key_nonterm -> key_eff [style=invis];')
    lines.append('    key_eff -> key_filtered [style=invis];')
    lines.append("  }")

    lines.append("")
    lines.append("  subgraph cluster_info {")
    lines.append('    label="Test info"; fontsize=13; fontname="Arial"; color="#d1d5db";')
    lines.append(f'    info_k [shape=note, label="k = {k}"];')
    lines.append(f'    info_alpha [shape=note, label="alpha = {escape_label(printable(alpha))}"];')
    lines.append(f'    info_eff [shape=note, label="EFF = {escape_label(eff_words)}"];')
    lines.append('    info_k -> info_alpha [style=invis];')
    lines.append('    info_alpha -> info_eff [style=invis];')
    lines.append("  }")

    lines.append("}")
    return "\n".join(lines) + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description="Generate DOT/PNG visualizations for EFF tests.")
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

        k, productions, alpha = parse_input(in_path)
        eff_set = parse_eff_set(out_path)
        node_id, edges, node_style = build_derivation_graph(k, productions, alpha, eff_set)
        dot_text = build_dot(test_name, k, alpha, eff_set, node_id, edges, node_style)

        dot_path = output_dir / f"{test_name}.dot"
        dot_path.write_text(dot_text, encoding="utf-8")

        if dot_bin:
            png_path = output_dir / f"{test_name}.png"
            subprocess.run([dot_bin, "-Tpng", str(dot_path), "-o", str(png_path)], check=True)

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
