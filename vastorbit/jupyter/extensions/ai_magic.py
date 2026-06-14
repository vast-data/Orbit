"""
VAST Orbit AI Magic — Jupyter Extension
=======================================

Load with::

    %load_ext vastorbit.ai

Configure::

    %ai_config --key sk-ant-api03-... --model claude-sonnet-4-20250514

Use::

    %%ai
    Show me the top 10 regions by average revenue, with a bar chart

The extension auto-detects the API key in this order:
    1. %ai_config --key passed explicitly
    2. ANTHROPIC_API_KEY environment variable
    3. ~/.vastorbit/config.json  →  {"anthropic_api_key": "sk-ant-..."}
"""

from __future__ import annotations

import json
import os
import time
import textwrap
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any

from IPython.core.magic import (
    Magics,
    magics_class,
    cell_magic,
    line_magic,
)
from IPython.core.magic_arguments import (
    argument,
    magic_arguments,
    parse_argstring,
)


# ═══════════════════════════════════════════════════════════════
# Schema Cache
# ═══════════════════════════════════════════════════════════════

@dataclass
class SchemaCache:
    """Cache table schemas to avoid re-introspecting on every %%ai call."""

    ttl: int = 300
    _store: dict = field(default_factory=dict)
    _ts: dict = field(default_factory=dict)

    def _key(self, catalog: str, schema: str) -> str:
        return f"{catalog}.{schema}"

    def get(self, catalog: str, schema: str) -> str | None:
        k = self._key(catalog, schema)
        if k in self._ts and (time.time() - self._ts[k]) < self.ttl:
            return self._store.get(k)
        return None

    def put(self, catalog: str, schema: str, desc: str) -> None:
        k = self._key(catalog, schema)
        self._store[k] = desc
        self._ts[k] = time.time()

    def invalidate(self) -> None:
        self._store.clear()
        self._ts.clear()


def introspect_schema(conn_info: dict) -> str:
    """
    Query information_schema for table/column metadata.
    Returns compact format: table_name(col1 TYPE, col2 TYPE, ...)
    """
    import vastorbit as vo

    catalog = conn_info.get("catalog", "")
    schema = conn_info.get("schema", "")

    tables_result = vo.sql(f"""
        SELECT table_name
        FROM {catalog}.information_schema.tables
        WHERE table_schema = '{schema}'
        ORDER BY table_name
    """)

    lines = []
    for row in tables_result:
        tname = row[0] if isinstance(row, (list, tuple)) else row
        cols = vo.sql(f"""
            SELECT column_name, data_type
            FROM {catalog}.information_schema.columns
            WHERE table_schema = '{schema}'
              AND table_name = '{tname}'
            ORDER BY ordinal_position
        """)
        col_defs = ", ".join(f"{c[0]} {c[1]}" for c in cols)
        lines.append(f"{tname}({col_defs})")

    return "\n".join(lines) if lines else "(no tables found)"


# ═══════════════════════════════════════════════════════════════
# Compressed System Prompt
# ═══════════════════════════════════════════════════════════════

SYSTEM_PROMPT = textwrap.dedent("""\
    You are a VAST Orbit code generator. Output ONLY executable Python code.
    No markdown, no backticks, no explanations.

    ## VAST Orbit API Reference (from source code)

    ```
    import vastorbit as vo

    # ── Connection (already established — NEVER generate connection code) ──
    vo.current_connection()         # returns conn object
    vo.current_cursor()             # returns cursor

    # ── VastFrame — core object (pandas-like, in-database via Trino) ──
    vdf = vo.VastFrame("table_name")
    vdf = vo.VastFrame("SELECT * FROM t WHERE ...")

    # Reading
    vdf.head(limit=5)               # returns TableSample
    vdf.tail(limit=5)
    vdf.iloc(limit=5, offset=0)
    vdf.shape()                     # (nrows, ncols)
    vdf.get_columns()               # list of column names
    vdf.select(columns)             # returns new VastFrame with subset

    # VastColumn access
    vdf["col"]                      # returns VastColumn
    vdf["col"].head(limit=5)
    vdf["col"].nlargest(n=10)
    vdf["col"].nsmallest(n=10)

    # ── Aggregation ──
    vdf.describe(method="auto", columns=None, unique=False)
    # method: "auto"|"numerical"|"categorical"|"all"
    vdf.aggregate(func, columns=None)
    # func: list of SQL agg strings, e.g. ["AVG(col)", "MAX(col)"]
    vdf.groupby(columns, expr=None, having=None)
    # columns: str or list    expr: list of SQL agg expressions
    # Example: vdf.groupby("region", ["AVG(revenue) AS avg_rev", "COUNT(*) AS cnt"])
    # Example: vdf.groupby(["city", "year"], ["SUM(sales) AS total"])
    vdf.avg(columns=None) / .sum() / .min() / .max()
    vdf.std() / .var() / .median() / .count()
    vdf.nunique(columns=None, approx=True)
    vdf.duplicated(columns=None, count=False)
    vdf.count_percent(columns=None, sort_result=True, desc=True)
    # VastColumn aggregation
    vdf["col"].avg() / .sum() / .min() / .max() / .std() / .median()
    vdf["col"].value_counts(k=30)
    vdf["col"].topk(k=6)
    vdf["col"].mode() / .distinct() / .nunique()

    # ── Filtering ──
    vdf.filter("age > 30 AND city = 'Dubai'")  # SQL WHERE condition
    vdf.search(conditions, usecols=None)
    vdf.isin(val)                   # val: dict {"col": [v1, v2]}
    vdf.between(column, start, end)
    vdf.at_time(ts, time)
    vdf.between_time(ts, start_time, end_time)
    vdf.first(ts, offset) / .last(ts, offset)
    vdf.drop(columns) / .drop_duplicates() / .dropna()
    vdf.sample(n=None, x=None, method="random")
    vdf.balance(column, method="under")
    # VastColumn filtering
    vdf["col"].drop() / .dropna() / .drop_outliers(threshold=4.0)
    vdf["col"].isin(val)

    # ── Sorting & Joins ──
    vdf.sort(columns)               # str, list, or {"col": "desc"}
    vdf.join(input_relation, on=None, how="inner")
    # on: dict {"left_col": "right_col"} or list of conditions
    # how: "left"|"right"|"inner"|"full"|"cross"
    vdf.append(input_relation)      # UNION ALL

    # ── Transforms ──
    vdf.eval("new_col", "col1 * col2 + 100")   # add computed column
    vdf.fillna(val=None, method=None)           # val: dict or scalar
    vdf.clip(lower, upper)
    vdf.interpolate(ts, rule, method=None)
    vdf.narrow(index, columns=None, col_name="column", val_name="value")  # unpivot/melt
    vdf.pivot(index, columns, values, aggr="sum")

    # ── Encoding & Scaling (on VastFrame) ──
    vdf["col"].label_encode() / .one_hot_encode()
    vdf.normalize(columns=None, method="zscore") / .scale(columns, method)

    # ── Correlation & Stats (IMPORTANT: these return plots directly!) ──
    vdf.corr(columns=None, method="pearson", show=True)
    # Returns a plotly/matplotlib Figure directly. It IS a heatmap.
    # DO NOT chain .heatmap() on the result — corr() already displays the matrix.
    # methods: "pearson"|"spearman"|"spearmand"|"kendall"|"cramer"|"biserial"
    vdf.cov(columns=None, show=True)         # covariance matrix plot
    vdf.regr(columns=None, method="r2", show=True)  # regression matrix
    vdf.corr_pvalue(column1, column2, method="pearson")  # returns float
    vdf.acf(column, ts, p=12)                # autocorrelation plot
    vdf.pacf(column, ts, p=5)                # partial autocorrelation
    vdf.iv_woe(y, columns=None, nbins=10)    # IV / WOE analysis

    # ── Plotting (all return PlottingObject — interactive Plotly/HC/MPL) ──
    # VastFrame plots (pass list of column names):
    vdf.bar(columns, method="density", of=None)
    vdf.barh(columns, method="density", of=None)
    vdf.scatter(columns, by=None, size=None, max_nb_points=20000)
    vdf.scatter_matrix(columns=None, max_nb_points=1000)
    vdf.heatmap(columns, method="count", of=None)
    # columns: list of exactly 2 column names, e.g. ["col1", "col2"]
    vdf.hexbin(columns, method="count", of=None)
    vdf.contour(columns, func, nbins=100)
    vdf.boxplot(columns=None, max_nb_fliers=30)
    vdf.hist(columns, method="density", of=None)
    vdf.pie(columns, method="count", of=None)
    vdf.density(columns=None, nbins=100)
    vdf.pivot_table(columns, method="count", of=None, with_numbers=True)
    vdf.plot(ts, columns=None, kind="line")         # time-series line/area
    vdf.range_plot(columns, ts)
    vdf.outliers_plot(columns, threshold=3.0)
    # VastColumn plots:
    vdf["col"].bar(method="density") / .barh() / .pie()
    vdf["col"].hist(by=None, method="density")
    vdf["col"].boxplot(by=None) / .density() / .spider()
    vdf["col"].plot(ts, kind="line")
    vdf["col"].candlestick(ts)
    vdf["col"].range_plot(ts)
    vdf["col"].geo_plot()
    # Animated (VastFrame):
    vdf.animated_bar(ts, columns, by=None)
    vdf.animated_pie(ts, columns, by=None)
    vdf.animated_plot(ts, columns=None, by=None)
    vdf.animated_scatter(ts, columns, by=None)

    # ── IO ──
    vdf.to_pandas()                 # materialize to pandas DataFrame
    vdf.to_csv(path) / .to_json(path)
    vdf.to_db(name, ...) / .to_list() / .to_numpy()
    vdf.copy()                      # deep copy VastFrame
    vdf.train_test_split(test_size=0.33)  # returns (train_vdf, test_vdf)
    # Parsers
    vo.read_csv(path, ...) / vo.read_json(path, ...) / vo.read_pandas(df, table_name=...)

    # ── Machine Learning ──
    from vastorbit.machine_learning.vast import (
        # Classification
        RandomForestClassifier, XGBClassifier,
        LogisticRegression, NaiveBayes,
        NearestCentroid, KNeighborsClassifier,
        LinearSVC,
        # Regression
        RandomForestRegressor, XGBRegressor,
        LinearRegression, Ridge, Lasso, ElasticNet,
        PLSRegression, PoissonRegressor,
        KNeighborsRegressor, LinearSVR,
        # Clustering
        KMeans, KPrototypes, BisectingKMeans, DBSCAN,
        # Decomposition
        PCA, SVD, MCA,
        # Preprocessing
        StandardScaler, RobustScaler, MinMaxScaler, OneHotEncoder,
        # Anomaly Detection
        IsolationForest, LocalOutlierFactor,
    )

    # Supervised (classification / regression):
    model = RandomForestClassifier(n_estimators=10, max_depth=5, ...)
    model.fit(input_relation, X=["f1","f2"], y="target", test_relation="")
    model.predict(vdf, X=None, name="prediction", cutoff=0.5)
    model.predict_proba(vdf, X=None, name="prob", pos_label=None)
    model.score(metric="accuracy", cutoff=0.5)    # classif
    model.score(metric="r2")                       # regression
    model.classification_report(cutoff=0.5)
    model.regression_report()
    model.confusion_matrix(cutoff=0.5)
    model.roc_curve(nbins=30)           # binary/multiclass
    model.prc_curve(nbins=30)           # precision-recall
    model.lift_chart(nbins=1000)
    model.cutoff_curve(nbins=30)
    model.features_importance()
    model.plot(max_nb_points=100)       # decision boundary
    model.contour(nbins=100)
    # Tree models:
    model.get_tree(tree_id=0) / .plot_tree(tree_id=0)
    model.to_graphviz(tree_id=0)

    # Unsupervised:
    model = KMeans(n_cluster=8, ...)
    model.fit(input_relation, X=["f1","f2"])
    model.predict(vdf, name="cluster")
    model.plot() / .contour()

    # Model management:
    model.summarize() / .get_params() / .get_attributes()
    model.to_python() / .to_sql() / .to_binary(path)
    model.drop()                        # drop from DB

    # Model selection:
    from vastorbit.machine_learning.model_selection import elbow, cross_validate
    ```

    ## Rules
    1. Connection is ALREADY established. NEVER generate connection code.
    2. Output ONLY valid Python. No explanations, no markdown fences.
    3. Use `vdf` as default variable name for new VastFrames.
    4. Always display results: end with .head(), a plot call, or print().
    5. Prefer in-database ops. Only .to_pandas() if user explicitly asks.
    6. For ML: always show evaluation after fit (score, report, or plot).
    7. Use the schema below for correct table/column names.
    8. If user references existing notebook variables, use them as-is.
    9. CRITICAL: vdf.corr() already returns a heatmap plot. NEVER chain .heatmap() on corr().
    10. vdf.heatmap(columns) takes exactly 2 columns — it's for 2D density, NOT correlation.
    11. ALWAYS end with a bare expression (not assigned to a variable) so the
        result auto-displays. Example:
        GOOD:  vdf = vo.VastFrame("t"); vdf.corr()        ← last line is bare expr
        BAD:   vdf = vo.VastFrame("t"); result = vdf.corr() ← nothing displays
        If multiple results needed, use display(): from IPython.display import display
""")


# ═══════════════════════════════════════════════════════════════
# Claude API (zero-dependency — uses urllib)
# ═══════════════════════════════════════════════════════════════

def call_claude(
    api_key: str,
    system: str,
    user_message: str,
    model: str = "claude-sonnet-4-20250514",
    max_tokens: int = 2048,
) -> tuple[str, int, int]:
    """
    Call Claude and return (code, input_tokens, output_tokens).
    Uses urllib — no anthropic SDK needed.
    """
    import ssl
    import urllib.request

    # Build SSL context with fallback for environments where
    # Python can't find the system certificate bundle (conda,
    # corporate proxies, macOS after brew install, etc.)
    ssl_ctx = ssl.create_default_context()
    try:
        ssl_ctx.load_default_certs()
    except Exception:
        pass

    # If default certs failed, try certifi (pip install certifi)
    if ssl_ctx.cert_store_stats()["x509_ca"] == 0:
        try:
            import certifi
            ssl_ctx.load_verify_locations(certifi.where())
        except ImportError:
            # Last resort: warn and disable verification
            import warnings
            warnings.warn(
                "SSL certificate verification failed. "
                "Install certifi (`pip install certifi`) to fix this. "
                "Falling back to unverified HTTPS.",
                stacklevel=2,
            )
            ssl_ctx = ssl.create_default_context()
            ssl_ctx.check_hostname = False
            ssl_ctx.verify_mode = ssl.CERT_NONE

    body = json.dumps({
        "model": model,
        "max_tokens": max_tokens,
        "temperature": 0.0,
        "system": system,
        "messages": [{"role": "user", "content": user_message}],
    })

    req = urllib.request.Request(
        "https://api.anthropic.com/v1/messages",
        data=body.encode(),
        headers={
            "Content-Type": "application/json",
            "x-api-key": api_key,
            "anthropic-version": "2023-06-01",
        },
        method="POST",
    )

    with urllib.request.urlopen(req, context=ssl_ctx, timeout=60) as resp:
        data = json.loads(resp.read())

    code = "\n".join(
        b["text"] for b in data.get("content", []) if b.get("type") == "text"
    ).strip()

    # Strip markdown fences if model slips them in
    if code.startswith("```"):
        lines = code.split("\n")
        lines = [l for l in lines if not l.startswith("```")]
        code = "\n".join(lines).strip()

    usage = data.get("usage", {})
    return code, usage.get("input_tokens", 0), usage.get("output_tokens", 0)


# ═══════════════════════════════════════════════════════════════
# API Key Resolution
# ═══════════════════════════════════════════════════════════════

def _resolve_api_key(explicit: str | None = None) -> str | None:
    """
    Resolve API key with fallback chain:
        1. Explicit value (from %ai_config --key)
        2. ANTHROPIC_API_KEY env var
        3. ~/.vastorbit/config.json → anthropic_api_key
    """
    if explicit:
        return explicit

    env_key = os.environ.get("ANTHROPIC_API_KEY")
    if env_key:
        return env_key

    config_path = Path.home() / ".vastorbit" / "config.json"
    if config_path.exists():
        try:
            cfg = json.loads(config_path.read_text())
            return cfg.get("anthropic_api_key")
        except (json.JSONDecodeError, OSError):
            pass

    return None


# ═══════════════════════════════════════════════════════════════
# Jupyter Magics Class
# ═══════════════════════════════════════════════════════════════

@magics_class
class VAST OrbitAIMagics(Magics):
    """
    Jupyter magics for VAST Orbit AI code generation.

    Registered via %load_ext vastorbit.ai
    """

    def __init__(self, shell):
        super().__init__(shell)
        self.api_key: str | None = None
        self.model: str = "claude-sonnet-4-20250514"
        self.cache = SchemaCache(ttl=300)
        self.show_code: bool = True
        self.auto_execute: bool = True
        self.last_code: str = ""
        self.total_input_tokens: int = 0
        self.total_output_tokens: int = 0
        self.call_count: int = 0

        # Try to auto-resolve key on load
        self.api_key = _resolve_api_key()

    # ── Configuration ─────────────────────────────────────────

    @line_magic
    @magic_arguments()
    @argument("--key", "-k", type=str, default=None,
              help="Anthropic API key (sk-ant-...)")
    @argument("--model", "-m", type=str, default=None,
              help="Claude model (default: claude-sonnet-4-20250514)")
    @argument("--cache-ttl", type=int, default=None,
              help="Schema cache TTL in seconds (default: 300)")
    @argument("--show-code", type=str, default=None,
              choices=["true", "false"],
              help="Show generated code (default: true)")
    @argument("--auto-execute", type=str, default=None,
              choices=["true", "false"],
              help="Auto-execute generated code (default: true)")
    def ai_config(self, line):
        """
        Configure AI Magic settings.

        Usage::

            %ai_config --key sk-ant-api03-... --model claude-sonnet-4-20250514
            %ai_config --show-code false
            %ai_config --cache-ttl 600

        With no arguments, shows current configuration.
        """
        args = parse_argstring(self.ai_config, line)

        if args.key:
            self.api_key = args.key
        if args.model:
            self.model = args.model
        if args.cache_ttl is not None:
            self.cache.ttl = args.cache_ttl
        if args.show_code is not None:
            self.show_code = args.show_code == "true"
        if args.auto_execute is not None:
            self.auto_execute = args.auto_execute == "true"

        # Print current config
        key_display = (
            f"{self.api_key[:12]}...{self.api_key[-4:]}"
            if self.api_key else "NOT SET ⚠"
        )
        print(f"  api_key:      {key_display}")
        print(f"  model:        {self.model}")
        print(f"  cache_ttl:    {self.cache.ttl}s")
        print(f"  show_code:    {self.show_code}")
        print(f"  auto_execute: {self.auto_execute}")

    # ── Main Magic ────────────────────────────────────────────

    @cell_magic
    def ai(self, line, cell):
        """
        Generate and execute VAST Orbit code from natural language.

        Usage::

            %%ai
            Show me top 10 regions by revenue as a bar chart

            %%ai --no-exec
            Train a RandomForest on the churn table
        """
        from IPython.display import display, Code

        # Parse cell-level flags
        no_exec = "--no-exec" in line
        prompt = cell.strip()

        if not prompt:
            print("⚠ Empty prompt. Write what you want after %%ai")
            return

        # Resolve API key
        key = _resolve_api_key(self.api_key)
        if not key:
            print("⚠ No API key configured. Set it with:")
            print("  %ai_config --key sk-ant-api03-...")
            print("  or set ANTHROPIC_API_KEY environment variable")
            print("  or add to ~/.vastorbit/config.json")
            return

        # Get schema context
        schema_ctx = self._get_schema_context()

        # Build system prompt
        system = SYSTEM_PROMPT + (
            f"\n\n## Available Tables\n```\n{schema_ctx}\n```"
        )

        # Call Claude
        try:
            code, in_tok, out_tok = call_claude(
                api_key=key,
                system=system,
                user_message=prompt,
                model=self.model,
            )
        except Exception as e:
            print(f"✗ Claude API error: {e}")
            return

        self.last_code = code
        self.total_input_tokens += in_tok
        self.total_output_tokens += out_tok
        self.call_count += 1

        # Display code
        if self.show_code:
            print("─" * 56)
            print(f"🛰️  VAST Orbit AI  ({in_tok}+{out_tok} tokens)")
            print("─" * 56)
            display(Code(code, language="python"))
            print("─" * 56)

        # Execute: run all lines, then eval the last expression
        # so it auto-displays and stores in _ (like a normal cell)
        if self.auto_execute and not no_exec:
            try:
                ns = self.shell.user_ns
                # Split code into "body" (statements) and "last" (expression)
                import ast as _ast
                try:
                    tree = _ast.parse(code)
                except SyntaxError as e:
                    print(f"✗ Syntax error in generated code: {e}")
                    return

                if tree.body and isinstance(tree.body[-1], _ast.Expr):
                    # Last node is a bare expression — exec body, eval last
                    last_expr = _ast.Expression(body=tree.body[-1].value)
                    _ast.fix_missing_locations(last_expr)
                    body = _ast.Module(body=tree.body[:-1], type_ignores=[])
                    _ast.fix_missing_locations(body)
                    exec(compile(body, "<ai>", "exec"), ns)
                    result = eval(compile(last_expr, "<ai>", "eval"), ns)
                    # Store in _ and Out[n] like IPython does
                    ns["_"] = result
                    ns["_ai_result"] = result
                    # Display the result
                    if result is not None:
                        from IPython.display import display
                        display(result)
                else:
                    # All statements (assignments, etc.) — just exec
                    exec(code, ns)
            except Exception as e:
                print(f"✗ Execution error: {e}")
                print("  Use %ai_code to inspect and fix manually.")

    # ── Helper Magics ─────────────────────────────────────────

    @line_magic
    def ai_schema(self, line):
        """
        Show or refresh the cached schema.

        Usage::

            %ai_schema            # show cached schema
            %ai_schema refresh    # force re-introspection
        """
        if line.strip() == "refresh":
            self.cache.invalidate()
            print("✓ Schema cache cleared. Next %%ai call will re-introspect.")
        else:
            schema = self._get_schema_context()
            print(schema)

    @line_magic
    def ai_code(self, line):
        """Show the last AI-generated code."""
        if self.last_code:
            from IPython.display import display, Code
            display(Code(self.last_code, language="python"))
        else:
            print("No code generated yet.")

    @line_magic
    def ai_stats(self, line):
        """Show cumulative token usage for the session."""
        print(f"  calls:         {self.call_count}")
        print(f"  input tokens:  {self.total_input_tokens:,}")
        print(f"  output tokens: {self.total_output_tokens:,}")
        total = self.total_input_tokens + self.total_output_tokens
        print(f"  total tokens:  {total:,}")

    # ── Internal ──────────────────────────────────────────────

    def _get_schema_context(self) -> str:
        """Get schema from cache or introspect."""
        try:
            import vastorbit as vo
            conn = vo.current_connection()
            catalog = getattr(conn, "catalog", "default")
            schema = getattr(conn, "schema", "default")

            cached = self.cache.get(catalog, schema)
            if cached is not None:
                return cached

            desc = introspect_schema({
                "catalog": catalog,
                "schema": schema,
            })
            self.cache.put(catalog, schema, desc)
            return desc
        except Exception as e:
            return f"(schema unavailable: {e})"


# ═══════════════════════════════════════════════════════════════
# Extension Entry Point — this is what %load_ext calls
# ═══════════════════════════════════════════════════════════════

def load_ipython_extension(ipython):
    """
    Called by ``%load_ext vastorbit.ai``

    Registers all magics and auto-detects the API key from
    env vars or config file.
    """
    magics = VAST OrbitAIMagics(ipython)
    ipython.register_magics(magics)

    key_status = "✓ key detected" if magics.api_key else "⚠ no key — run %ai_config --key YOUR_KEY"
    print(f"🛰️  VAST Orbit AI Magic loaded ({key_status})")
    print(f"   Use:  %%ai  |  %ai_config  |  %ai_schema  |  %ai_code  |  %ai_stats")


def unload_ipython_extension(ipython):
    """Called by ``%unload_ext vastorbit.ai``"""
    pass
