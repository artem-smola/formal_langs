# Test Data

- `test1` - baseline case with three 10-minute ticks.
- `test2` - input without explicit `T` (`T` inferred from intervals).
- `test3` - mixed interval boundaries and truncated final tick `[20, 25)`.

All intervals are interpreted as half-open: `[start, finish)`.

Quick check:

```bash
./ka_groups < tests/test1.in
./ka_groups < tests/test2.in
./ka_groups < tests/test3.in
./ka_groups --machine < tests/test1.in
```
