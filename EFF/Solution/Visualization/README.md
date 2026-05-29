# Visualization for EFF Tests

This directory contains visualizations for test cases from:

`../Code/tests`

## What is generated

For each `testN.in` + `testN.out` pair:

- `testN.dot` - rightmost-derivation graph in Graphviz DOT format
- `testN.png` - rendered image (only if Graphviz `dot` is installed)

Terminal leaves are colorized:
- green = prefix belongs to `EFF`
- gray = terminal leaf exists, but filtered out from `EFF`

## Build

```bash
make
```

## Render PNG explicitly

```bash
make png
```

This target requires Graphviz `dot` in `PATH`.

## Cleanup

```bash
make clean
```
