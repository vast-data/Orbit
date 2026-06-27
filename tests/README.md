# VastOrbit tests

Fast, broad **smoke coverage** of the VastOrbit public API. Each test runs an
operation on a small built-in dataset and checks that it *executes and returns a
sane shape/type* — not exact numbers. Heavy work is deliberately avoided: tiny
tree ensembles, short synthetic series, `cv=3` on flat relations.

> Run everything from the **repo root** (where `pytest.ini` lives), not from
> inside this folder — `tests/` is a package and shared constants import as
> `from tests.helpers import ...`.

```sh
pytest                       # whole suite
pytest tests/core            # one area
pytest tests/machine_learning/vast/test_linear_model.py   # one file
pytest -k "logistic"         # by keyword
```

---

## Layout

The tree mirrors the package, one file per topic:

| Folder | Covers |
|--------|--------|
| `connection/` | connection registration + round-trip |
| `datasets/` | every `load_*` loader |
| `core/` | VastFrame — build/IO, aggregate, filter, encode, corr, math, join/union/sort, fill, pivot, rolling, outliers, transforms, column ops, time-series ops, inspection, export, TableSample |
| `sql/` | `create_table`/`insert_into`/`drop`, math & string function builders, geo helpers |
| `machine_learning/vast/` | one file per model module (linear, tree, ensemble, svm, naive_bayes, neighbors, cluster, decomposition, preprocessing, pipeline, feature_extraction, tsa) + model evaluation |
| `machine_learning/metrics/` | classification + regression metrics |
| `machine_learning/model_selection/` | cross-validate, learning/validation curves, grid/randomized search, stepwise, elbow/best_k, statistical tests |
| `machine_learning/memmodel/` | `to_memmodel`, `to_python` |
| `plotting/` | matplotlib (Agg) + plotly backends |
| `test_modules.py` | import smoke for `ai` / `chart` / `jupyter` |

---

## Connection

Tests target a **local Trino** via the `memory` connector — no external database,
and it supports the `CREATE TABLE` / `INSERT` the loaders and temp tables need.
Everything is overridable with environment variables:

| Variable | Default | |
|----------|---------|---|
| `TRINO_HOST` | `localhost` | |
| `TRINO_PORT` | `8080` | |
| `TRINO_USER` | `admin` | |
| `TRINO_CATALOG` | `memory` | writable, in-memory |
| `TRINO_SCHEMA` | `default` | |

```sh
TRINO_HOST=my-host TRINO_CATALOG=vast pytest
```

---

## Fixtures (`conftest.py`)

| Fixture | Scope | What it gives you |
|---------|-------|-------------------|
| `trino_connection` | session, autouse | opens one Trino connection and registers it with `set_connection` |
| `plotting_lib` | session, autouse | forces the matplotlib `Agg` backend |
| `name_factory` | function | `name_factory("prefix")` → unique name; **drops every model/table/view it handed out at teardown** |
| `titanic` `iris` `winequality` `airline` | session | datasets loaded once and reused |

Use `name_factory` for anything you create, so reruns never collide and nothing
leaks between tests:

```python
def test_something(winequality, name_factory):
    model = LinearRegression(name=name_factory("reg"))
    model.fit(winequality, ["fixed_acidity"], "quality")
    ...   # the model is dropped automatically afterwards
```

---

## Helpers (`helpers.py`)

Shared, importable from any depth as `from tests.helpers import ...`:

- **Column constants** — `TITANIC_NUM_X`, `TITANIC_BINARY_Y`, `IRIS_X`,
  `IRIS_MULTI_Y`, `WINE_X`, `WINE_REG_Y`.
- `unique_name(prefix)` — collision-free object name.
- `cols_lower(vdf)` — lower-cased, unquoted column names (Trino lowercases
  unquoted identifiers, so always compare columns case-insensitively).
- `trend_series(n)` / `multivariate_series(n)` — tiny synthetic series for
  time-series and VAR tests, no external loader required.

---

## Conventions

- **Smoke, not numeric.** Assert `is not None`, a row count, a column exists, a
  score is in `[0, 1]` — not exact values.
- **Keep it light.** Tree ensembles: `n_estimators=5, max_depth=3`. Clustering:
  `max_iter=10`. Model selection: `cv=3` on freshly-loaded flat relations.
- **Case-insensitive columns.** `assert "pred" in cols_lower(vd)`.
- **NULL-free slices for classifiers.** `data = titanic.copy()[X + [y]].dropna()`.
- **Parametrize across a model family** to cover many estimators in one test:

```python
import pytest
from vastorbit.machine_learning.vast import Ridge, Lasso

MODELS = [("Ridge", lambda n: Ridge(name=n)),
          ("Lasso", lambda n: Lasso(name=n))]

@pytest.mark.parametrize("label, factory", MODELS, ids=[m[0] for m in MODELS])
def test_family(winequality, name_factory, label, factory):
    model = factory(name_factory(f"reg_{label}"))
    model.fit(winequality, WINE_X, WINE_REG_Y)
    assert model.score() is not None
```

---

## Adding a test

1. Put it in the folder that mirrors the package module under test (create the
   folder with an `__init__.py` if it's new).
2. Pull a dataset from a fixture and columns/targets from `tests.helpers`.
3. Name every created object with `name_factory`.
4. Keep the dataset small and the assertion shape-level.
5. Confirm discovery before running live:
   ```sh
   pytest --collect-only -q
   ```

Coverage of what actually executed:

```sh
make test-cov            # or: pytest --cov=vastorbit --cov-report=term-missing
```
