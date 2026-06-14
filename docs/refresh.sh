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
# =============================================================================
set -euo pipefail

MODE="${1:-full}"

# ── Headless build: never open chart windows or browser tabs ────────────────
# Executed ipython cells call plt.show() / fig.show(); outside a notebook
# those spawn GUI windows (matplotlib) or browser tabs (plotly/highcharts)
# and can block the build until closed by hand.
export MPLBACKEND=Agg          # matplotlib: render in memory, no window
export PLOTLY_RENDERER=json    # plotly: fig.show() becomes a no-op print
export BROWSER=true            # webbrowser.open() runs /bin/true -> nothing

# Resolve site-packages dynamically (the old hardcoded
# /usr/local/lib/python3.10/... breaks on every Python upgrade)
SITE_PKGS="$(python3 -c 'import sysconfig; print(sysconfig.get_paths()["purelib"])')"

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
    exit 0
fi

# ── FULL gear only: reinstall the package ───────────────────────────────────
if [ "$MODE" = "full" ]; then
    echo ">>> Reinstalling vastorbit"
    echo y | pip3 uninstall vastorbit
    pip3 install ../.

    # In case the data files are not copied
    mkdir -p "$SITE_PKGS/vastorbit/datasets/data/laliga/"
    cp ../vastorbit/datasets/data/laliga/*.json "$SITE_PKGS/vastorbit/datasets/data/laliga/" 2>/dev/null || true
fi

# ── Pre-processing ───────────────────────────────────────────────────────────
python3 replace_sphinx_dir.py

# ── Build ────────────────────────────────────────────────────────────────────
JOBS="${JOBS:-1}"

if [ "$MODE" = "fast" ]; then
    echo ">>> FAST build: incremental, no code execution (jobs=$JOBS)"
    FAST_DOCS=1 make html SPHINXOPTS="-j $JOBS"
else
    echo ">>> FULL build: clean + execute everything (jobs=$JOBS)"
    make clean
    make html SPHINXOPTS="-j $JOBS"
fi

# ── Post-processing (the built HTML is regenerated, so always run) ──────────
python3 remove_pattern.py
python3 fix_links.py
python3 create_toc_tree.py
# python3 notebook_correction.py

# ── Reverse pre-processing ───────────────────────────────────────────────────
python3 reverse_replace_sphinx_dir.py

# Run Black
# black ../.

echo ">>> Done ($MODE mode)."