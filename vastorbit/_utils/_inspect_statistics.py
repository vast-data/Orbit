"""
SPDX-License-Identifier: Apache-2.0
"""

import inspect
import importlib
from typing import Optional, TYPE_CHECKING
import numpy as np

import vastorbit as vo
from vastorbit._typing import PlottingObject, NoneType
from vastorbit._utils._object import create_new_vdf

if TYPE_CHECKING:
    from vastorbit.core.vastframe.base import VastFrame


def count_functions_classes_methods(
    module_name: str, class_: Optional[str] = None
) -> np.ndarray:
    """
    Counts the number of functions,
    classes and methods in a specific
    module.

    Parameters
    ----------
    module_name: str
        Name of the module
        to inspect.
    class_: str, optional
        Class to inspect.

    Returns
    -------
    np.ndarray
        ``functions,classes,methods``

    Examples
    --------
    The following code demonstrates the
    usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._inspect_statistics import count_functions_classes_methods

        # Example.
        count_functions_classes_methods("vastorbit.machine_learning.vast")

    .. note::

        These functions serve as utilities to
        generate some elements in the Sphinx
        documentation.
    """
    # Import the module dynamically
    module = importlib.import_module(module_name)

    # Get all members of the module
    members = inspect.getmembers(module)

    # Count functions, classes, and methods
    function_count = sum(1 for name, member in members if inspect.isfunction(member))
    class_count = sum(1 for name, member in members if inspect.isclass(member))

    attribute_count = 0
    for name, member in members:
        if inspect.isclass(member) and (
            isinstance(class_, NoneType) or class_ in str(member)
        ):
            class_members = inspect.getmembers(member)
            attribute_count += sum(
                [
                    int(not (str(l[0]).startswith("_")))
                    for l in inspect.getmembers(member)
                ]
            )

    return np.array([function_count, class_count, attribute_count])


def count_vastorbit_functions():
    """
    Counts the number of functions,
    classes and methods in many
    vastorbit modules.

    Returns
    -------
    dict
        ``dictionary`` with the
        section name and the
        number of elements:
        ``functions,classes,methods``

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._inspect_statistics import count_vastorbit_functions

        # Example.
        count_vastorbit_functions()

    .. note::

        These functions serve as utilities to
        generate some elements in the Sphinx
        documentation.
    """
    all_funs = [
        ("VastFrame", "vastorbit.core.vastframe", "VastFrame"),
        ("VastColumn", "vastorbit.core.vastframe", "VastColumn"),
        ("TableSample", "vastorbit.core.tablesample", "TableSample"),
        ("VASTModels", "vastorbit.machine_learning.vast", None),
        ("inMemoryModels", "vastorbit.machine_learning.memmodel", None),
        ("Metrics", "vastorbit.machine_learning.metrics", None),
        ("Model Selection", "vastorbit.machine_learning.model_selection", None),
        (
            "Statistical Tests",
            "vastorbit.machine_learning.model_selection.statistical_tests",
            None,
        ),
        ("Plotting Matplotlib", "vastorbit.plotting._matplotlib", None),
        ("Plotting Plotly", "vastorbit.plotting._plotly", None),
        ("SQL Functions", "vastorbit.sql.functions", None),
        ("SQL Statements", "vastorbit.sql", None),
        ("SQL Geo Extensions", "vastorbit.sql.geo", None),
        ("Loaders", "vastorbit.datasets.loaders", None),
        ("Generators", "vastorbit.datasets.generators", None),
    ]
    res = {}
    for fun, mod, class_ in all_funs:
        res[fun] = count_functions_classes_methods(mod, class_)
    return res


def summarise_vastorbit_functions():
    """
    Returns a summary of the
    entire vastorbit module.

    Returns
    -------
    list
        ``list`` with the
        section name and the
        number of elements:
        ``title,nb_functions``

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._inspect_statistics import summarise_vastorbit_functions

        # Example.
        summarise_vastorbit_functions()

    .. note::

        These functions serve as utilities to
        generate some elements in the Sphinx
        documentation.
    """
    f = count_vastorbit_functions()
    res = []
    res += [("VAST Utils", "QueryProfiler", f["QueryProfiler"][2])]
    res += [("Loaders & Generators", "Loaders", f["Loaders"][0])]
    res += [("Loaders & Generators", "Generators", f["Generators"][0])]
    res += [("Data Visualization Functions", "Matplotlib", f["Plotting Matplotlib"][1])]
    res += [("Data Visualization Functions", "Plotly", f["Plotting Plotly"][1])]
    res += [("Data Preparation/Exploration Functions", "VastFrame", f["VastFrame"][2])]
    res += [
        ("Data Preparation/Exploration Functions", "VastColumn", f["VastColumn"][2])
    ]
    res += [
        ("Data Preparation/Exploration Functions", "TableSample", f["TableSample"][2])
    ]
    res += [("SQL Functions & Extensions", "SQL Functions", f["SQL Functions"][0])]
    res += [("SQL Functions & Extensions", "SQL Statements", f["SQL Statements"][0])]
    res += [
        ("SQL Functions & Extensions", "SQL Geo Extensions", f["SQL Geo Extensions"][0])
    ]
    res += [("Machine Learning", "Statistical Tests", f["Statistical Tests"][0])]
    res += [("Machine Learning", "Algorithms/Functions", sum(f["VASTModels"][0:2]))]
    res += [("Machine Learning", "Extensions", f["inMemoryModels"][1])]
    res += [("Machine Learning", "Metrics", f["Metrics"][0])]
    res += [("Machine Learning", "Evaluation Functions", f["Model Selection"][0])]
    res += [("", "Total", sum([x[-1] for x in res]))]
    return res


def gen_rst_summary_table() -> str:
    """
    Returns a summary of the
    entire vastorbit module
    in the RST format.

    Returns
    -------
    str
        RST summary.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._inspect_statistics import gen_rst_summary_table

        # Example.
        print(gen_rst_summary_table())

    .. note::

        These functions serve as utilities to
        generate some elements in the Sphinx
        documentation.
    """
    # Header
    table = "+----------------------------------------+------------------------+---------------+\n"
    table += "| Category                               | Subcategory            | Functions     |\n"
    table += "+========================================+========================+===============+\n"

    # Data rows
    current_category = None
    total_functions = 0
    data = summarise_vastorbit_functions()

    for category, subcategory, functions in data:
        if category != current_category:
            # New category, print total functions for the previous one
            if current_category is not None:
                table += f"| {''.ljust(39)}|| {'Total'.ljust(22)}|| {str(total_functions).ljust(13)}|\n"
                table += "+----------------------------------------+------------------------+---------------+\n"

            # Start a new category
            current_category = category
            total_functions = 0

            # Print the current category for the first row
            table += f"| {category.ljust(39)}|| {subcategory.ljust(22)}|| {str(functions).ljust(13)}|\n"
        else:
            # Print subsequent rows for the same category without repeating category
            table += f"| {''.ljust(39)}|| {subcategory.ljust(22)}|| {str(functions).ljust(13)}|\n"

        # Accumulate total functions
        total_functions += functions

    # Print total functions for the last category
    if current_category is not None:
        if subcategory != "Total":
            table += f"| {''.ljust(39)}|| {'Total'.ljust(22)}|| {str(total_functions).ljust(13)}|\n"
        table += "+----------------------------------------+------------------------+---------------+\n"

    return table


def vastorbit_stats_vdf() -> "VastFrame":
    """
    Returns a summary of the
    entire vastorbit as a
    :py:class:`~VastFrame`.

    Returns
    -------
    VastFrame
        summary of the module.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. ipython:: python

        # Import the function.
        from vastorbit._utils._inspect_statistics import vastorbit_stats_vdf

        # Example.
        vastorbit_stats_vdf()

    .. note::

        These functions serve as utilities to
        generate some elements in the Sphinx
        documentation.
    """
    stats = summarise_vastorbit_functions()[:-1]
    res = {
        "category": [x[0] for x in stats],
        "subcategory": [x[1] for x in stats],
        "number": [x[2] for x in stats],
    }
    return create_new_vdf(res)


def summarise_vastorbit_chart(kind: str = "barh") -> PlottingObject:
    """
    Returns a summary of the
    entire vastorbit as a
    :py:class:`~VastFrame`.

    Returns
    -------
    obj
        Plotting Object.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. code-block:: python

        # Import the function.
        from vastorbit._utils._inspect_statistics import summarise_vastorbit_chart

        # Example.
        summarise_vastorbit_chart()

    .. ipython:: python
        :suppress:

        from vastorbit._utils._inspect_statistics import summarise_vastorbit_chart
        vo.set_option("plotting_lib", "plotly")
        fig = summarise_vastorbit_chart()
        html_text = fig.htmlcontent.replace("container", "plotting_summarise_vastorbit_chart")
        with open("SPHINX_DIRECTORY/figures/plotting_summarise_vastorbit_chart.html", "w") as file:
            file.write(html_text)

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotting_summarise_vastorbit_chart.html

    .. note::

        These functions serve as utilities to
        generate some elements in the Sphinx
        documentation.
    """
    vdf = vastorbit_stats_vdf()
    if kind == "barh":
        return vdf.barh(
            ["category", "subcategory"],
            method="sum",
            of="number",
            max_cardinality=1000,
            kind="drilldown",
            categoryorder="total desc",
        )
    elif kind == "pie":
        return vdf.pie(
            ["category", "subcategory"], method="sum", of="number", max_cardinality=1000
        )
    else:
        raise ValueError("Invalid option.")


def codecov_vastorbit_chart():
    """
    Returns the vastorbit
    codecov chart.

    Returns
    -------
    obj
        Plotting Object.

    Examples
    --------
    The following code demonstrates
    the usage of the function.

    .. code-block:: python

        # Import the function.
        from vastorbit._utils._inspect_statistics import codecov_vastorbit_chart

        # Example.
        codecov_vastorbit_chart()

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        from vastorbit._utils._inspect_statistics import codecov_vastorbit_chart
        vo.set_option("plotting_lib", "plotly")
        fig = codecov_vastorbit_chart()
        fig.write_html("SPHINX_DIRECTORY/figures/plotting_codecov_vastorbit_chart.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotting_codecov_vastorbit_chart.html

    .. note::

        These functions serve as utilities to
        generate some elements in the Sphinx
        documentation.
    """
    vdf = create_new_vdf(
        {
            "category": ["Covered", "Not Covered"],
            "number": [100 * vo.__codecov__, 100 * (1 - vo.__codecov__)],
        }
    )
    return vdf["category"].pie(method="avg", of="number")
