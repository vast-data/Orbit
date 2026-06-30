# Building the VAST Orbit documentation

The VAST Orbit docs are built with **Sphinx** + **nbsphinx**. They are not just
API reference: most pages contain live code examples (and Jupyter notebooks)
that are **executed against a running database during the build**, so the charts,
tables, and outputs in the rendered docs are real. That is why the build is
heavier than a typical Sphinx site — and why this folder ships a helper script,
`refresh.sh`, that wraps the whole pipeline.

This guide covers the one-time setup, the everyday build commands, where output
and logs land, and how to diagnose a failed build.

---

## Contents

- [One-time setup](#one-time-setup)
- [Quick start](#quick-start)
- [Build modes (the four gears)](#build-modes-the-four-gears)
- [Environment knobs](#environment-knobs)
- [Output](#output)
- [Logs and diagnosing failures](#logs-and-diagnosing-failures)
- [What the post-processing scripts do](#what-the-post-processing-scripts-do)
- [Running the steps manually](#running-the-steps-manually)
- [Troubleshooting](#troubleshooting)

---

## One-time setup

Do these once per machine (or after a fresh clone).

**1. Clone the full repository.** The build imports the installed `vastorbit`
package *and* reads the `.rst`/notebook sources under `docs/`, so you need the
whole repo, not just this folder.

**2. Switch the plotting theme to `sphinx`.** Open `vastorbit/_config/config.py`
and set the default theme to `sphinx`:

```python
register_option(
    Option(
        "theme",
        "sphinx",
        "",
        in_validator(["light", "dark", "sphinx"]),
    )
)
```

*Why:* the `sphinx` theme renders charts with a **transparent background** so
they sit correctly on both the light and dark versions of the documentation
site. With `light`/`dark` the plots carry a solid background and look wrong on
the opposite theme.

**3. Install the docs requirements.** From the `docs/` folder:

```shell
pip install -r requirements.txt
```

**4. Install pandoc.** nbsphinx shells out to pandoc to convert notebooks to
reStructuredText; without it, every `.ipynb` page fails.

```shell
apt install pandoc
```

**5. Install `make`** (if you don't already have it):

```shell
apt install make
```

**6. Point the build at your docs directory.** Open `replace_sphinx_dir.py` and
set `replacement_word` to the **absolute path of this `docs/` folder** on your
machine:

```python
replacement_word = "/absolute/path/to/vastorbit/docs"
```

*Why:* example code in the docstrings and `.rst` files writes its generated
figures using a placeholder path, `SPHINX_DIRECTORY/figures/...`. The build swaps
that placeholder for a real, absolute path so the figures are written and then
embedded. `refresh.sh` runs this substitution for you (and reverses it
afterwards) — you only set the target path once.

---

## Quick start

Once set up, a full release-quality build is a single command from `docs/`:

```shell
./refresh.sh
```

That reinstalls the package, cleans previous output, executes every example, and
runs all the post-processing. It takes a while (everything is executed live). For
day-to-day iteration you'll usually want one of the faster gears below.

---

## Build modes (the four gears)

`refresh.sh` has four modes, trading completeness for speed:

| Mode | Command | What it does | Reach for it when |
|------|---------|--------------|-------------------|
| **full** | `./refresh.sh` | Reinstall the package, `make clean`, execute **all** example code, post-process. Release-quality. | Publishing, or after changing code/docstrings that examples depend on. |
| **fast** | `./refresh.sh fast` | Incremental build, no reinstall, no clean, `FAST_DOCS=1` so **example code is not executed**. | Iterating on prose/structure where you don't need fresh outputs. |
| **file** | `./refresh.sh file source/<page>.rst` | Rebuild **one page**, reusing the cached doctree; executes only that page's code and keeps every other built page intact. | Working on a single page. Prefix `FAST_DOCS=1` to skip even that page's code. |
| **css** | `./refresh.sh css` | No Sphinx build at all — just sync `_static` (css/js/icons/fonts/thumbs) into the already-built HTML. ~1 second. | Pure styling tweaks. |

A few notes:

- **`fast`** is the everyday driver for content work. Because it skips execution,
  any figure/table produced by a code cell won't refresh — but headings, text,
  cross-references, and layout all rebuild.
- **`file`** is surgical. It calls `sphinx-build` directly (rather than `make`,
  whose make-mode ignores a positional filename) and reuses the existing doctree
  cache, so no other page is re-read or re-executed. It **assumes a `full` (or
  `fast`) build has already run at least once** so that cache exists — and it does
  **not** reinstall/re-patch the package, so if you changed a docstring, run a
  `full` build first. Prose-only example:

  ```shell
  FAST_DOCS=1 ./refresh.sh file source/getting_started.rst
  ```

- **`css`** never touches Sphinx; after it runs, hard-refresh the browser
  (Ctrl+Shift+R) to bust the cache.

---

## Environment knobs

| Variable | Default | Effect |
|----------|---------|--------|
| `JOBS` | `1` | Sphinx parallelism. `JOBS=1` keeps log lines correctly ordered for diagnosis; bump it (e.g. `JOBS=4`) for faster builds once things are healthy. |
| `FAST_DOCS` | `0` | `FAST_DOCS=1` skips execution of example code (used by `fast`, and can be prefixed onto `file`). |

The script also forces a **headless** environment automatically
(`MPLBACKEND=Agg`, `PLOTLY_RENDERER=json`, `BROWSER=true`) so chart code never
tries to open a window or browser tab mid-build.

```shell
JOBS=4 ./refresh.sh fast          # faster fast-build
JOBS=1 ./refresh.sh               # clean, readable logs for a full build
```

---

## Output

The rendered site is written to:

```
build/html/
```

Open `build/html/index.html` in a browser. (`build` is the Makefile's `BUILDDIR`;
`source` is the `SOURCEDIR`.)

---

## Logs and diagnosing failures

Every build (`full`/`fast`/`file`) writes logs to `docs/_logs/` and bundles them
into a single shareable archive:

| File | Contents |
|------|----------|
| `build.log` | Full stdout + stderr of the build, including each per-cell failure printed by `conf.py`. |
| `sphinx_warnings.log` | Sphinx's own warnings (missing includes, broken references, malformed markup). |
| `figure_errors.log` | The exact example cells that failed to execute. |
| `docs_logs.zip` | All three of the above, zipped — **share this one file** when asking for help. |

For the cleanest logs, build single-threaded so output isn't interleaved:

```shell
JOBS=1 ./refresh.sh
```

The logs are reset at the start of each build, and the script also sweeps stray
example outputs (`titanic_subset.csv`, `iris.json`, etc.) that example code
writes into `docs/` — these are build by-products, not inputs, so removing them
afterwards is safe.

---

## What the post-processing scripts do

After Sphinx produces the HTML, `refresh.sh` runs several small fix-up passes:

| Script | Purpose |
|--------|---------|
| `replace_sphinx_dir.py` | Substitute the `SPHINX_DIRECTORY` placeholder with the real docs path **in the repo sources and in the installed package**, so docstring/RST figure paths resolve and write correctly. Runs before the build. |
| `reverse_replace_sphinx_dir.py` | Undo the substitution in the repo sources afterwards, leaving your working tree clean. |
| `remove_pattern.py` | Strip noisy path patterns so generated links read cleanly. |
| `fix_links.py` | Repair links to notebooks and other nested files. |
| `create_toc_tree.py` | Build a per-page table-of-contents tree. |
| `notebook_correction.py` | Legacy notebook-link fixer — normally unnecessary once `fix_links.py` runs (kept commented out). |

**On the installed-package patch:** autodoc imports `vastorbit` from
`site-packages`, so the docstrings Sphinx actually reads live there — not in
`../vastorbit`. A `full` build therefore also rewrites `SPHINX_DIRECTORY` inside
the *installed* copy; otherwise every docstring figure (`fig.write_html(...)` /
`.. raw:: html :file: ...`) fails to resolve and the chart never appears. No
reverse is needed for the installed copy because the next `full` build reinstalls
the package and overwrites it. This is also why `file` mode requires a prior
`full` build — it relies on that patch already being in place.

---

## Running the steps manually

If `refresh.sh` fails partway and you want to drive the pipeline by hand, the
`full` flow is:

```shell
# 1. Remove any existing install (the docs use a clean, non-editable install)
echo y | pip uninstall vastorbit

# 2. Resolve the docs directory inside the source
python3 replace_sphinx_dir.py

# 3. Install the package (non-editable — see Troubleshooting)
pip install ../.

# 4. Clean and build (the build executes examples, so it can take a while)
make clean
make html

# 5. Post-process the HTML
python3 remove_pattern.py
python3 fix_links.py
python3 create_toc_tree.py
# python3 notebook_correction.py   # only if fix_links didn't catch a link

# 6. Restore the source tree
python3 reverse_replace_sphinx_dir.py
black ../.
```

The finished site is in `build/html/`.

---

## Troubleshooting

**`vastorbit.__version__` is missing / metadata looks wrong.** Don't use an
editable install (`pip install -e`) for the docs. Editable installs skip the real
build step that generates the dynamic version (`setuptools_scm` / `_version.py`).
`refresh.sh` deliberately does a regular `pip install ../.`.

**Autodoc figures don't appear.** The docstrings Sphinx reads come from the
installed package, whose `SPHINX_DIRECTORY` placeholders must be patched. Run a
`full` build (it patches the installed copy); `fast`/`file` rely on a previous
`full` build having done so.

**`file` mode warns about a missing doctree cache.** Run a `full` (or `fast`)
build once first so `build/doctrees` exists; otherwise the single-file build
falls back to re-reading everything.

**Notebook pages fail to render.** Make sure `pandoc` is installed — nbsphinx
needs it to convert `.ipynb` files.

**Charts try to open windows or hang.** Build through `refresh.sh`, which sets the
headless environment variables; if you call `make html` directly, export
`MPLBACKEND=Agg`, `PLOTLY_RENDERER=json`, and `BROWSER=true` yourself.

**Interleaved or hard-to-read logs.** Build with `JOBS=1`.