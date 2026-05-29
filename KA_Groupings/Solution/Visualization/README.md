# Visualization for KA Groupings Tests

This directory creates visualizations for tests from:

`../Code/tests`

## Output

For each test and each tick from `testN.out`:

- `testN_tick_A_B.dot` - Graphviz source
- `testN_tick_A_B.png` - rendered image (if Graphviz `dot` is available)

Notation:

- node color = group id on this tick
- solid dark edge = active interaction on this tick
- dashed gray edge = inactive interaction on this tick
- edge label = `len [t_start,t_finish]`

## Build

```bash
make
```

## Force PNG rendering

```bash
make png
```

## Cleanup

```bash
make clean
```
