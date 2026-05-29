# Visualization for Cities Tests

This directory contains visualizations for test cases from:

`../Code/tests`

## What is generated

For each `testN.in` + `testN.out` pair:

- `testN.dot` - graph in Graphviz DOT format
- `testN.png` - rendered image (only if Graphviz `dot` is installed)

Node color indicates the state assignment from `testN.out`.
Edge labels are road lengths.

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
