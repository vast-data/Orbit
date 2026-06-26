.. _statistics:

=====================
VAST Orbit Statistics
=====================

.. include:: logo_include.rst

Numbers say more than adjectives. Every figure on this page is generated directly
from the VAST Orbit source when the documentation is built — the library inspects
its own modules and counts what it actually ships. Nothing here is hand-written or
rounded up, so the page always reflects exactly the version you are reading.

Summary
-------

The chart below summarizes VAST Orbit by counting the public building blocks in each
area of the library: the loaders and generators that get data in, the visualization
layer, the DataFrame and column operations you use to prepare and explore data, the
SQL function layer, and machine learning. Read together, they show how much of a
complete, in-database data-science toolkit already ships in the box.

.. ipython:: python
    :suppress:

    import vastorbit as vo
    from vastorbit._utils._inspect_statistics import summarise_vastorbit_chart

    # kind="pie" is the default; the drill-down bar is intentionally not used here.
    vo.set_option("plotting_lib", "plotly")
    fig = summarise_vastorbit_chart()
    html_text = fig.to_html().replace(
        "container", "plotting_summarise_vastorbit_chart"
    )
    with open(
        "SPHINX_DIRECTORY/figures/plotting_summarise_vastorbit_chart.html", "w"
    ) as file:
        file.write(html_text)

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/plotting_summarise_vastorbit_chart.html

The same breakdown in exact numbers, grouped by category with a running total for
each, is below.

.. ipython:: python
    :suppress:

    from vastorbit._utils._inspect_statistics import gen_rst_summary_table

    with open("SPHINX_DIRECTORY/figures/vastorbit_stats_table.rst", "w") as file:
        file.write(gen_rst_summary_table())

.. include:: ../figures/vastorbit_stats_table.rst

Code coverage
-------------

Breadth is only half the story — the tests behind it are the other half. This pie
shows how much of the VAST Orbit codebase is exercised by the test suite, a quick
read on how much of the library is verified and where there is still room to grow.

.. ipython:: python
    :suppress:

    import vastorbit as vo
    from vastorbit._utils._inspect_statistics import codecov_vastorbit_chart

    vo.set_option("plotting_lib", "plotly")
    fig = codecov_vastorbit_chart()
    fig.write_html(
        "SPHINX_DIRECTORY/figures/plotting_codecov_vastorbit_chart.html"
    )

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/plotting_codecov_vastorbit_chart.html

How these numbers are produced
------------------------------

There is no manual tally. VAST Orbit ships a small inspection module,
:py:mod:`vastorbit._utils._inspect_statistics`, that imports the library, walks its
modules, and counts the public functions, classes, and methods in each area before
rendering the summary and coverage charts. You can reproduce everything on this page
yourself in a few lines:

.. code-block:: python

    import vastorbit as vo
    from vastorbit._utils._inspect_statistics import (
        summarise_vastorbit_chart,
        gen_rst_summary_table,
        codecov_vastorbit_chart,
    )

    vo.set_option("plotting_lib", "plotly")

    # The summary pie of public building blocks, by area
    summarise_vastorbit_chart()

    # The same breakdown as a table, with per-category totals
    print(gen_rst_summary_table())

    # The test code-coverage pie
    codecov_vastorbit_chart()

Because the counts come straight from the installed package, they stay honest: every
new function or model added to VAST Orbit shows up here on the next build,
automatically.

.. seealso::

    - :ref:`api` - the full, documented API behind these numbers
    - :ref:`api.machine_learning` - the models behind the model count
    - :ref:`getting_started` - install VAST Orbit and explore it yourself