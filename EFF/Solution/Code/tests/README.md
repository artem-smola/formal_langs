# Тестовые данные

## Файлы

- `test1.in` / `test1.out` — пример с `epsilon`-ветвью, которая отфильтровывается из `EFF`.
- `test2.in` / `test2.out` — пример с `alpha`, содержащей терминал и нетерминал.
- `test3.in` / `test3.out` — пример с конечной `epsilon`-цепочкой и пустым словом.

Тесты используют legacy-формат ввода (`k`, `p`, продукции, `alpha`).
Программа также поддерживает extended-формат с директивами
`start/nonterminals/terminals`.

## Быстрая проверка

```bash
./eff < tests/test1.in
./eff < tests/test2.in
./eff < tests/test3.in
```
