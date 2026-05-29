# Visualization for Chinese Postman Tests

This directory builds visualizations for test cases from:

`../Code/tests`

## What is generated

For every `testN.in` + `testN.out` pair:

- `testN.dot` - Graphviz source
- `testN.png` - rendered image (if Graphviz `dot` is installed)

Visualization details:

- blue nodes: even-degree vertices
- red nodes: odd-degree vertices
- dashed red edges: odd-vertex pairings selected by the algorithm (`+distance`)

## Build

```bash
make
```

## Render PNG explicitly

```bash
make png
```

## Cleanup

```bash
make clean
```
