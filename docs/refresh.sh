#!/bin/bash
# =============================================================================
# VastOrbit docs refresh — three gears:
#
#   ./refresh.sh            FULL  : reinstall package, clean, execute all code,
#                                   post-process. The release-quality build.
#   ./refresh.sh fast       FAST  : no reinstall, no clean, FAST_DOCS=1
#                                   (no code execution). Structure/content
#                                   iteration in a fraction of the time.
#   ./refresh.sh css        CSS   : no build at all — just sync _static
#                                   (css/js/icons/fonts/thumbs) into the built
#                                   HTML. Styling iteration in ~1 second.
#
# Every build (full/fast) now writes logs to docs/_logs/ and bundles them into
# docs/_logs/docs_logs.zip so they can be shared for diagnosis:
#     build.log            full stdout+stderr of the build
#     sphinx_warnings.log  Sphinx's own warnings (missing :file: includes, etc.)
#     figure_errors.log    the exact example cells that failed to execute
# For clean, readable logs run single-threaded:  JOBS=1 ./refresh.sh
# =============================================================================
set -euo pipefail

MODE="${1:-full}"

# ── Headless build: never open chart windows or browser tabs ────────────────
export MPLBACKEND=Agg          # matplotlib: render in memory, no window
export PLOTLY_RENDERER=json    # plotly: fig.show() becomes a no-op print
export BROWSER=true            # webbrowser.open() runs /bin/true -> nothing

SITE_PKGS="$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"

# ── Log setup ────────────────────────────────────────────────────────────────
LOG_DIR="$PWD/_logs"
mkdir -p "$LOG_DIR"
BUILD_LOG="$LOG_DIR/build.log"
SPHINX_WARN_LOG="$LOG_DIR/sphinx_warnings.log"
export FIGURE_ERROR_LOG="$LOG_DIR/figure_errors.log"
# Start each build with fresh logs (conf.py only ever appends to FIGURE_ERROR_LOG)
rm -f "$BUILD_LOG" "$SPHINX_WARN_LOG" "$FIGURE_ERROR_LOG"
: > "$FIGURE_ERROR_LOG"   # ensure it exists even if zero failures

# ── Stray example outputs ────────────────────────────────────────────────────
# Files written by doc examples via relative paths (to_csv/to_json/to_pickle/
# SQL export). They land in docs/ and are NOT inputs — anything read during the
# build (titanic_subset.csv, titanic_more_data.csv, iris.json) is written earlier
# in the same build, so removing them afterwards is safe.
STRAY_OUTPUTS=(
    vdf_data.p
    query.sql
    titanic_subset.csv
    titanic_more_data.csv
    titanic_age_clean.csv
    titanic_age_clean.json
    iris.json
)

clean_stray_outputs() {
    local removed=0
    for f in "${STRAY_OUTPUTS[@]}"; do
        if [ -e "$f" ]; then
            rm -f "$f" && removed=$((removed + 1))
        fi
    done
    [ "$removed" -gt 0 ] && echo ">>> Cleaned $removed stray example output file(s) from $PWD"
    return 0
}

bundle_logs() {
    ( cd "$LOG_DIR" && zip -q -FS docs_logs.zip \
        build.log sphinx_warnings.log figure_errors.log 2>/dev/null || true )
    echo ""
    echo ">>> Logs written to: $LOG_DIR"
    echo "      build.log            ($(wc -l < "$BUILD_LOG" 2>/dev/null || echo 0) lines)"
    echo "      sphinx_warnings.log  ($(wc -l < "$SPHINX_WARN_LOG" 2>/dev/null || echo 0) lines)"
    echo "      figure_errors.log    ($(wc -l < "$FIGURE_ERROR_LOG" 2>/dev/null || echo 0) failed cells)"
    echo ">>> Share this single file: $LOG_DIR/docs_logs.zip"
}
# Always bundle logs AND sweep stray outputs on exit, even if the build aborts.
on_exit() {
    clean_stray_outputs
    bundle_logs
}
trap on_exit EXIT

# ── CSS gear: instant styling feedback, no Sphinx at all ────────────────────
if [ "$MODE" = "css" ]; then
    echo ">>> CSS sync only (no rebuild)"
    for d in css js icons fonts thumbs; do
        if [ -d "_static/$d" ]; then
            mkdir -p "_build/html/_static/$d"
            cp -r "_static/$d/." "_build/html/_static/$d/"
            echo "    synced _static/$d"
        fi
    done
    echo ">>> Done. Hard-refresh the browser (Ctrl+Shift+R)."
    trap - EXIT   # no build logs to bundle in css mode
    exit 0
fi

# ── FULL gear only: reinstall the package ───────────────────────────────────
if [ "$MODE" = "full" ]; then
    echo ">>> Reinstalling vastorbit"
    echo y | pip3 uninstall vastorbit
    # Regular (non-editable) install: this runs the real build step, so your
    # dynamic version (setuptools_scm / _version.py) and package metadata are
    # generated correctly. Editable installs skip that build step, which is why
    # `vastorbit.__version__` went missing.
    pip3 install ../.

    mkdir -p "$SITE_PKGS/vastorbit/datasets/data/laliga/"
    cp ../vastorbit/datasets/data/laliga/*.json "$SITE_PKGS/vastorbit/datasets/data/laliga/" 2>/dev/null || true
fi

# ── Pre-processing ───────────────────────────────────────────────────────────
# The docstring/RST examples write figures here via absolute paths
# (SPHINX_DIRECTORY -> this docs dir). open()/write_html won't create the
# directory, so make sure it exists before the build.
mkdir -p figures

# Replace SPHINX_DIRECTORY in the repo source + docs/source .rst files.
python3 replace_sphinx_dir.py 2>&1 | tee -a "$BUILD_LOG"

# CRITICAL for autodoc figures: autodoc imports vastorbit from site-packages, so
# the docstrings Sphinx actually reads live there, NOT in ../vastorbit. Patch the
# installed copy's placeholders too, otherwise every docstring
# `fig.write_html("SPHINX_DIRECTORY/figures/..")` / `.. raw:: html :file:
# SPHINX_DIRECTORY/figures/..` fails to write/resolve and the figure is never
# inserted. No reverse needed: the full build reinstalls the package next time,
# overwriting these files.
if [ "$MODE" = "full" ] && [ -d "$SITE_PKGS/vastorbit" ]; then
    echo ">>> Resolving SPHINX_DIRECTORY in installed package docstrings"
    DOCS_DIR="$PWD" python3 - "$SITE_PKGS/vastorbit" <<'PY' 2>&1 | tee -a "$BUILD_LOG"
import os, sys
pkg = sys.argv[1]
docs = os.environ["DOCS_DIR"]
n = 0
for root, _, files in os.walk(pkg):
    for f in files:
        if f.endswith(".py"):
            p = os.path.join(root, f)
            try:
                s = open(p, encoding="utf-8").read()
            except (UnicodeDecodeError, OSError):
                continue
            if "SPHINX_DIRECTORY" in s:
                open(p, "w", encoding="utf-8").write(s.replace("SPHINX_DIRECTORY", docs))
                n += 1
print(f"Patched {n} installed module file(s).")
PY
fi

# ── Build ────────────────────────────────────────────────────────────────────
# JOBS=1 by default for readable, correctly-ordered logs while diagnosing.
JOBS="${JOBS:-1}"
# -w writes Sphinx's own warnings to a dedicated file; 2>&1 | tee captures the
# full build (including conf.py's per-cell failure prints) into build.log.
SPHINX_W="-w $SPHINX_WARN_LOG"

if [ "$MODE" = "fast" ]; then
    echo ">>> FAST build: incremental, no code execution (jobs=$JOBS)"
    FAST_DOCS=1 make html SPHINXOPTS="-j $JOBS $SPHINX_W" 2>&1 | tee -a "$BUILD_LOG"
else
    echo ">>> FULL build: clean + execute everything (jobs=$JOBS)"
    make clean 2>&1 | tee -a "$BUILD_LOG"
    make html SPHINXOPTS="-j $JOBS $SPHINX_W" 2>&1 | tee -a "$BUILD_LOG"
fi

# ── Post-processing (the built HTML is regenerated, so always run) ──────────
python3 remove_pattern.py     2>&1 | tee -a "$BUILD_LOG"
python3 fix_links.py          2>&1 | tee -a "$BUILD_LOG"
python3 create_toc_tree.py    2>&1 | tee -a "$BUILD_LOG"
# python3 notebook_correction.py

# ── Reverse pre-processing ───────────────────────────────────────────────────
python3 reverse_replace_sphinx_dir.py 2>&1 | tee -a "$BUILD_LOG"

# Run Black
# black ../.

echo ">>> Done ($MODE mode)."