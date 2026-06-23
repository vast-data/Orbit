.. _contribution_guidelines.code.auto_doc.example:

========================
Complete Example
========================

.. include:: logo_include.rst

Comprehensive docstring templates and examples for VAST Orbit documentation.

____

Docstring Structure
-----------------------

Every VAST Orbit function docstring should follow this structure:

1. **Version Information** (optional)
2. **Description** (required)
3. **Parameters** (required)
4. **Returns** (required)
5. **Examples** (required)
6. **Notes/Warnings** (optional)
7. **See Also** (optional)

____

Version Information
-----------------------

**New Feature:**

.. code-block:: rst
    
    .. versionadded:: 1.0

**This renders as:**

.. versionadded:: 1.0

*(Notice: A green "New in version 1.0" badge appears)*

----

**Deprecated Feature:**

.. code-block:: rst

    .. deprecated:: 2.0

**This renders as:**

.. deprecated:: 2.0

*(Notice: A red "Deprecated since version 2.0" warning appears)*

----

**Changed Feature:**

.. code-block:: rst

    .. versionchanged:: 1.5.0

**This renders as:**

.. versionchanged:: 1.5.0

*(Notice: An orange "Changed in version 1.5.0" badge appears)*

----

.. note:: 
   
   Version directives are not applicable to functions already in VAST Orbit since inception. Only use them for new features, deprecations, or significant changes.

.. hint:: 
   
   For complete list of admonitions: https://sphinx-themes.org/sample-sites/furo/kitchen-sink/admonitions/

____

Description
--------------

**Best Practices:**

- |check| Write one summary line at the top (concise, action-oriented)
- |check| Add detailed explanation below with multiple paragraphs if needed
- |check| Use inline code blocks with backticks for code elements: ``VastFrame``
- |check| Reference VAST Orbit objects using Sphinx roles: ``:py:class:`~VastColumn```
- |check| Explain what the function does, not how it does it (implementation details go in Notes)

**Example:**

.. code-block:: python

    def one_hot_encode(
        self,
        prefix: Optional[str] = None,
        prefix_sep: str = "_",
        drop_first: bool = True,
        use_numbers_as_suffix: bool = False,
    ) -> "VastFrame":
        """     
        Encodes the :py:class:`~VastColumn` with the One-Hot Encoding algorithm.

        One hot encoding will be done on the selected column. The result will be 
        outputted in new columns thus resulting in additional columns added to the 
        table. The first category/dummy will be dropped by default unless stated 
        otherwise by the parameter ``drop_first``.
        """

**This renders as:**

Encodes the :py:class:`~VastColumn` with the One-Hot Encoding algorithm.

One hot encoding will be done on the selected column. The result will be 
outputted in new columns thus resulting in additional columns added to the 
table. The first category/dummy will be dropped by default unless stated 
otherwise by the parameter ``drop_first``.

*(Notice: "VastColumn" becomes a clickable link, "drop_first" is formatted as code)*

____

Parameters
-------------

Format: Add parameter type and description. Create heading with ``----------`` underline.

**Example:**

.. code-block:: python

    """
    Parameters
    ----------
    x: int
        x is the input value
    y: str, optional
        Optional string parameter. Default is None.
    z: list[str], optional
        List of strings for processing.
        
        - Item 1: First processing option
        - Item 2: Second processing option
    """

**This renders as:**

.. rubric:: Parameters

x: int
    x is the input value
y: str, optional
    Optional string parameter. Default is None.
z: list[str], optional
    List of strings for processing.
    
    - Item 1: First processing option
    - Item 2: Second processing option

*(Notice: "optional" is automatically detected, parameters are bolded, descriptions are indented)*

____

Returns
----------

Format: Specify return type and description. Use the same heading format.

**Example:**

.. code-block:: python

    """
    Returns
    -------
    PlottingObject
        Plotting object containing the generated chart.
        Can be displayed, saved, or further customized.
    """

**This renders as:**

.. rubric:: Returns

PlottingObject
    Plotting object containing the generated chart.
    Can be displayed, saved, or further customized.

*(Notice: Return type is bolded, description explains what the object contains)*

____

Examples
-----------

Static Code Block
~~~~~~~~~~~~~~~~~

Display code without execution - useful for showing expected output or simple examples:

.. code-block:: rst

    .. code-block:: python

        >>> x = [1, 2, 3]
        >>> max(x)
        3

**This renders as:**

.. code-block:: python

    >>> x = [1, 2, 3]
    >>> max(x)
    3

*(Notice: Code is syntax-highlighted but not executed - the "3" is just text)*

----

Executed Code
~~~~~~~~~~~~~

Display and execute code - the actual output will be shown:

.. code-block:: rst

    .. ipython:: python

        x = 2
        y = 3
        x + y

**This renders as:**

.. ipython:: python

    x = 2
    y = 3
    x + y

*(Notice: Code is executed and the result "5" is displayed as actual output)*

----

**When to use which:**

- **Static** (``.. code-block::``): For pseudo-code, expected output examples, or when you want to show specific formatting
- **Executed** (``.. ipython::``): For real examples that should work when users copy-paste them

____

Figures & Equations
----------------------

Equations
~~~~~~~~~

Use LaTeX math notation for mathematical formulas:

.. code-block:: rst

    .. math::

        (a + b)^2 = a^2 + 2ab + b^2

**This renders as:**

.. math::

    (a + b)^2 = a^2 + 2ab + b^2

*(Notice: Beautiful mathematical typesetting using LaTeX)*

----

**More complex example:**

.. code-block:: rst

    .. math::

        \bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i

**This renders as:**

.. math::

    \bar{x} = \frac{1}{n}\sum_{i=1}^{n} x_i

----

Matplotlib Plots
~~~~~~~~~~~~~~~~

Use ``@savefig`` pseudo-directive to save and display matplotlib figures:

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import matplotlib.pyplot as plt
        import numpy as np
        
        x = np.linspace(0, 10, 100)
        y = np.sin(x)
        
        plt.figure(figsize=(8, 4))
        plt.plot(x, y, 'b-', linewidth=2)
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Sine Wave')
        plt.grid(True, alpha=0.3)
        
        @savefig example_sine_wave.png
        plt.show()

**This renders as:**

.. ipython:: python
    :suppress:

    import matplotlib.pyplot as plt
    import numpy as np
    
    x = np.linspace(0, 10, 100)
    y = np.sin(x)
    
    plt.figure(figsize=(8, 4))
    plt.plot(x, y, 'b-', linewidth=2)
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Sine Wave')
    plt.grid(True, alpha=0.3)
    
    @savefig example_sine_wave.png
    plt.show()

*(Notice: The sine wave plot is displayed inline, and the image is saved to _images/example_sine_wave.png)*

----

**VAST Orbit Bar Chart Example:**

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
        @savefig core_VastFrame_plotting_bar_example.png
        data.bar("counts")

**This renders as:**

.. ipython:: python
    :suppress:

    import vastorbit as vo
    data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
    @savefig core_VastFrame_plotting_bar_example.png
    data.bar("counts")

*(Notice: VAST Orbit's matplotlib bar chart is displayed and saved)*

----

.. important:: 

   **File naming convention:** Use descriptive names following the pattern:
   ``path_with_underscores_classname_functionname.png``
   
   Example: ``core_VastFrame_plotting_bar_1.png``

.. note:: 

   VAST Orbit is imported by default in the documentation environment - no need to show import statements unless demonstrating specific import patterns.

----

Plotly Plots
~~~~~~~~~~~~~~~~~~~~~~~~

Interactive plots must be saved as HTML files and then included:

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        vo.set_option("plotting_lib", "plotly")
        data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
        fig = data.bar("counts")
        fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPlot_bar_example.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPlot_bar_example.html

**This renders as:**

.. ipython:: python
    :suppress:

    import vastorbit as vo
    vo.set_option("plotting_lib", "plotly")
    data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
    fig = data.bar("counts")
    fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPlot_bar_example.html")

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPlot_bar_plotly.html

*(Notice: An interactive Plotly chart is embedded - you can hover, zoom, pan)*

----

.. important::

   **File paths for HTML:**
   
   - **When saving** (in Python): write to ``"SPHINX_DIRECTORY/figures/filename.html"`` — the ``SPHINX_DIRECTORY`` token is replaced with the absolute ``docs/`` path at build time.
   - **When loading** (in RST): reference the same file with ``:file: SPHINX_DIRECTORY/figures/filename.html``. The build substitutes the token before Sphinx reads the page and reverses it afterwards, so nothing machine-specific is committed.

----

VastFrame Table Output
~~~~~~~~~~~~~~~~~~~~~~~

Display VastFrame tables as interactive HTML:

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        data = vo.VastFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
        html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_table_example.html", "w")
        html_file.write(data._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/core_VastFrame_table_example.html

**This renders as:**

.. ipython:: python
    :suppress:

    import vastorbit as vo
    data = vo.VastFrame({"a": [1, 2, 3], "b": [4, 5, 6], "c": [7, 8, 9]})
    html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_table_example.html", "w")
    html_file.write(data._repr_html_())
    html_file.close()

.. raw:: html
    :file: SPHINX_DIRECTORY/figures/core_VastFrame_table_example.html

*(Notice: An interactive VastFrame table with sortable columns)*

____

Notes & Admonitions
----------------------

Use admonitions to highlight important information:

.. code-block:: rst
    
    .. note:: 
       This is an informational note to provide context.

    .. tip:: 
       This is a helpful tip for best practices.

    .. hint:: 
       This is a hint to guide users toward the solution.

    .. important:: 
       This is important information that affects behavior.

    .. warning:: 
       This is a warning about potential issues or pitfalls.

    .. danger:: 
       This is a danger warning for critical situations that could cause data loss.

**This renders as:**

.. note:: 
   This is an informational note to provide context.

.. tip:: 
   This is a helpful tip for best practices.

.. hint:: 
   This is a hint to guide users toward the solution.

.. important:: 
   This is important information that affects behavior.

.. warning:: 
   This is a warning about potential issues or pitfalls.

.. danger:: 
   This is a danger warning for critical situations that could cause data loss.

*(Notice: Each admonition has a distinct color and icon based on its severity)*

----

**When to use each:**

- **note**: General information, context, or clarifications
- **tip**: Best practices, recommendations, or shortcuts
- **hint**: Gentle guidance toward the right approach
- **important**: Critical information that affects functionality
- **warning**: Potential issues, edge cases, or common mistakes
- **danger**: Severe issues that could cause data loss or system problems

____

See Also
-----------

**Reference Related Functions:**

.. code-block:: rst

    .. seealso:: 

        | :py:func:`~vastorbit.VastFrame.barh` : Horizontal bar charts
        | :py:func:`~vastorbit.VastFrame.hist` : Histogram plots

**This renders as:**

.. seealso:: 

   | :py:func:`~vastorbit.VastFrame.barh` : Horizontal bar charts
   | :py:func:`~vastorbit.VastFrame.hist` : Histogram plots

*(Notice: Clickable links to related functions with brief descriptions)*

----

**Reference Modules:**

.. code-block:: rst

    .. seealso:: 

        :py:mod:`~vastorbit.machine_learning.vast.linear_model`
           Linear modeling functions for regression and classification.

**This renders as:**

.. seealso:: 

   :py:mod:`~vastorbit.machine_learning.vast.linear_model`
      Linear modeling functions for regression and classification.

----

**Best Practices:**

- |check| Use ``|`` (pipe) to create compact lists of related functions
- |check| Add brief descriptions explaining how functions relate
- |check| Link to both similar functions and complementary ones
- |check| Order from most to least related

____

Complete Examples
--------------------

Example 1: Basic Aggregation Function (max)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Complete function with docstring:**

.. code-block:: python

    def max(
        self,
        columns: Optional[SQLColumns] = None,
        **agg_kwargs,
    ) -> TableSample:
        """
        .. versionadded:: 1.0

        Aggregates the VastFrame using 'max' (Maximum).

        Computes the maximum value for each specified column. This is useful
        for finding the largest values in your dataset. The operation is 
        performed directly in the database for optimal performance.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all numerical 
            VastColumns are used.
        **agg_kwargs
            Any optional parameter to pass to the Aggregate function.
            
            - by: List of columns to group by
            - having: Filtering condition for groups

        Returns
        -------
        TableSample
            Table containing the maximum value for each column.

        Examples
        --------
        Basic usage with a single column:

        .. ipython:: python

            import vastorbit as vo
            data = vo.VastFrame({"price": [5.2, 10.16, 7.8, 3.4]})
            data["price"].max()

        Multiple columns:

        .. ipython:: python

            data = vo.VastFrame({
                "price": [5.2, 10.16, 7.8],
                "quantity": [100, 200, 150]
            })
            data.max(columns=["price", "quantity"])

        .. note:: 
           The max operation ignores NULL values. If all values are NULL,
           the result will be NULL.

        .. seealso:: 
        
           | :py:func:`~vastorbit.VastFrame.min` : Find minimum values
           | :py:func:`~vastorbit.VastFrame.mean` : Calculate averages
           | :py:func:`~vastorbit.VastFrame.agg` : General aggregation function

        """
        return None

**This docstring renders as:**

.. ipython:: python
    :suppress:

    import vastorbit as vo

----

.. versionadded:: 1.0

**Aggregates the VastFrame using 'max' (Maximum).**

Computes the maximum value for each specified column. This is useful
for finding the largest values in your dataset. The operation is 
performed directly in the database for optimal performance.

.. rubric:: Parameters

columns: SQLColumns, optional
    List of the VastColumns names. If empty, all numerical 
    VastColumns are used.
\*\*agg_kwargs
    Any optional parameter to pass to the Aggregate function.
    
    - by: List of columns to group by
    - having: Filtering condition for groups

.. rubric:: Returns

TableSample
    Table containing the maximum value for each column.

**Examples**

Basic usage with a single column:

.. ipython:: python

    import vastorbit as vo
    data = vo.VastFrame({"price": [5.2, 10.16, 7.8, 3.4]})
    data["price"].max()

Multiple columns:

.. ipython:: python

    data = vo.VastFrame({
        "price": [5.2, 10.16, 7.8],
        "quantity": [100, 200, 150]
    })
    data.max(columns=["price", "quantity"])

.. note:: 
   The max operation ignores NULL values. If all values are NULL,
   the result will be NULL.

.. seealso:: 

   | :py:func:`~vastorbit.VastFrame.min` : Find minimum values
   | :py:func:`~vastorbit.VastFrame.mean` : Calculate averages
   | :py:func:`~vastorbit.VastFrame.agg` : General aggregation function

____

Example 2: Plotting Function (bar)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Complete function with docstring:**

.. code-block:: python

    def bar(
        self,
        columns: SQLColumns,
        method: PlottingMethod = "density",
        of: Optional[str] = None,
        max_cardinality: tuple[int, int] = (6, 6),
        h: tuple[PythonNumber, PythonNumber] = (None, None),
        kind: Literal["auto", "drilldown", "stacked"] = "auto",
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        .. versionadded:: 1.0

        Draws the bar chart of the input :py:class:`~VastColumn` based
        on an aggregation.

        Creates a bar chart visualizing the distribution or aggregation of 
        data. Supports both single-column and multi-column bar charts with
        various aggregation methods and styles.

        Parameters
        ----------
        columns: SQLColumns
            List of the VastColumns names. The list must
            have one or two elements.
        method: str, optional
            The method used to aggregate the data.
            
            - count: Number of elements
            - density: Percentage of the distribution
            - mean: Average of the VastColumn 'of'
            - min: Minimum of the VastColumn 'of'
            - max: Maximum of the VastColumn 'of'
            - sum: Sum of the VastColumn 'of'
            - q%: q Quantile of the VastColumn 'of' (ex: 50% for median)
            
            It can also be a customized aggregation, for example:
            ``AVG(column1) + 5``
        of: str, optional
            The :py:class:`~VastColumn` used to compute the aggregation.
        max_cardinality: tuple, optional
            Maximum number of distinct elements for VastColumns
            1 and 2 to be used as categorical (default: (6, 6)).
            For these elements, no h is picked or computed.
        h: tuple, optional
            Interval width of the VastColumn 1 and 2 bars.
            Only valid if the VastColumns are numerical.
            Optimized h will be computed if the parameter is
            empty or invalid.
        kind: str, optional
            The BarChart Type.
            
            - auto: Regular BarChart based on 1 or 2 VastColumns
            - drilldown: Drill Down BarChart based on 2 VastColumns
            - stacked: Stacked BarChart based on 2 VastColumns
        chart: PlottingObject, optional
            The chart object to plot on.
        **style_kwargs
            Any optional parameter to pass to the plotting
            functions.
            
            - width: Chart width in pixels
            - height: Chart height in pixels
            - color: Bar color

        Returns
        -------
        PlottingObject
            Plotting object containing the chart. Can be displayed
            inline, saved to file, or further customized.

        Examples
        --------
        **Basic bar chart (matplotlib):**

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            data = vo.VastFrame({"category": ["A", "B", "C", "A", "B"], 
                                  "value": [10, 15, 7, 12, 20]})
            @savefig core_VastFrame_vDFPlot_bar_basic.png
            data.bar("category")

        .. code-block:: python
        
            data = vo.VastFrame({"category": ["A", "B", "C", "A", "B"], 
                                  "value": [10, 15, 7, 12, 20]})
            data.bar("category")

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            data = vo.VastFrame({"category": ["A", "B", "C", "A", "B"], 
                                  "value": [10, 15, 7, 12, 20]})
            @savefig core_VastFrame_vDFPlot_bar_basic.png
            data.bar("category")

        ----

        **Interactive Plotly chart:**

        .. ipython:: python
            :suppress:

            import vastorbit as vo
            vo.set_option("plotting_lib", "plotly")
            data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
            fig = data.bar("counts")
            fig.write_html("SPHINX_DIRECTORY/figures/core_VastFrame_vDFPlot_bar_plotly_example2.html")

        .. code-block:: python
        
            vo.set_option("plotting_lib", "plotly")
            data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
            data.bar("counts")

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_vDFPlot_bar_plotly_example2.html

        ----

        **Aggregated bar chart:**

        .. ipython:: python
            :suppress:

            data = vo.VastFrame({
                "category": ["A", "B", "C", "A", "B"],
                "value": [10, 15, 7, 12, 20]
            })
            @savefig core_VastFrame_vDFPlot_bar_aggregated.png
            data.bar("category", method="sum", of="value")

        .. code-block:: python

            data = vo.VastFrame({
                "category": ["A", "B", "C", "A", "B"],
                "value": [10, 15, 7, 12, 20]
            })
            data.bar("category", method="sum", of="value")

        .. ipython:: python
            :suppress:

            data = vo.VastFrame({
                "category": ["A", "B", "C", "A", "B"],
                "value": [10, 15, 7, 12, 20]
            })
            @savefig core_VastFrame_vDFPlot_bar_aggregated.png
            data.bar("category", method="sum", of="value")

        .. note:: 
           You can use matplotlib or plotly as the backend.
           Set with ``vo.set_option("plotting_lib", "plotly")``

        .. tip::
           For large datasets with high cardinality, consider using the
           ``max_cardinality`` parameter to limit the number of bars.

        .. seealso:: 
        
           | :py:func:`~vastorbit.VastFrame.barh` : Horizontal bar charts
           | :py:func:`~vastorbit.VastFrame.hist` : Histogram plots
           | :py:func:`~vastorbit.VastFrame.pie` : Pie charts

        """
        return None

**This docstring renders as:**

----

.. versionadded:: 1.0

**Draws the bar chart of the input VastColumn based on an aggregation.**

Creates a bar chart visualizing the distribution or aggregation of 
data. Supports both single-column and multi-column bar charts with
various aggregation methods and styles.

.. rubric:: Parameters

columns: SQLColumns
    List of the VastColumns names. The list must have one or two elements.
method: str, optional
    The method used to aggregate the data.
    
    - count: Number of elements
    - density: Percentage of the distribution
    - mean: Average of the VastColumn 'of'
    - min: Minimum of the VastColumn 'of'
    - max: Maximum of the VastColumn 'of'
    - sum: Sum of the VastColumn 'of'
    - q%: q Quantile of the VastColumn 'of' (ex: 50% for median)
    
    It can also be a customized aggregation, for example: ``AVG(column1) + 5``

of: str, optional
    The VastColumn used to compute the aggregation.
max_cardinality: tuple, optional
    Maximum number of distinct elements for VastColumns 1 and 2 to be used as categorical (default: (6, 6)).
h: tuple, optional
    Interval width of the VastColumn 1 and 2 bars. Only valid if the VastColumns are numerical.
kind: str, optional
    The BarChart Type (auto, drilldown, or stacked).
chart: PlottingObject, optional
    The chart object to plot on.
\*\*style_kwargs
    Optional plotting parameters (width, height, color, etc.).

.. rubric:: Returns

PlottingObject
    Plotting object containing the chart.

**Examples**

Basic bar chart (matplotlib):

.. ipython:: python
    :suppress:

    import vastorbit as vo
    data = vo.VastFrame({"category": ["A", "B", "C", "A", "B"], 
                          "value": [10, 15, 7, 12, 20]})
    @savefig core_VastFrame_vDFPlot_bar_basic.png
    data.bar("category")

Interactive Plotly chart: *(rendered as interactive HTML)*

Aggregated bar chart:

.. ipython:: python
    :suppress:

    data = vo.VastFrame({
        "category": ["A", "B", "C", "A", "B"],
        "value": [10, 15, 7, 12, 20]
    })
    @savefig core_VastFrame_vDFPlot_bar_aggregated.png
    data.bar("category", method="sum", of="value")

.. note:: 
   You can use matplotlib or plotly as the backend.
   Set with ``vo.set_option("plotting_lib", "plotly")``

.. tip::
   For large datasets with high cardinality, consider using the
   ``max_cardinality`` parameter to limit the number of bars.

.. seealso:: 

   | :py:func:`~vastorbit.VastFrame.barh` : Horizontal bar charts
   | :py:func:`~vastorbit.VastFrame.hist` : Histogram plots
   | :py:func:`~vastorbit.VastFrame.pie` : Pie charts

____

Example 3: Statistical Function (corr)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Complete function with docstring:**

.. code-block:: python

    def corr(
        self,
        columns: Optional[SQLColumns] = None,
        method: Literal[
            "pearson", "kendall", "spearman", "spearmand", "biserial", "cramer"
        ] = "pearson",
        mround: int = 3,
        focus: Optional[str] = None,
        show: bool = True,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:
        """
        Computes the Correlation Matrix of the VastFrame.

        Calculates pairwise correlations between columns using various
        correlation methods. Supports both linear and non-linear correlation
        measures for different data types.

        Parameters
        ----------
        columns: SQLColumns, optional
            List of the VastColumns names. If empty, all
            numerical VastColumns are used.
        method: str, optional
            Method to use to compute the correlation.
            
            **pearson**
                Pearson's correlation coefficient (linear).
                Measures linear relationships between variables.
                
                .. math::
                
                    r = \\frac{\\sum(x_i - \\bar{x})(y_i - \\bar{y})}{\\sqrt{\\sum(x_i - \\bar{x})^2 \\sum(y_i - \\bar{y})^2}}

            **spearman**
                Spearman's correlation coefficient (monotonic - rank based).
                Measures monotonic relationships using ranks.

            **spearmanD**
                Spearman's correlation coefficient using the DENSE RANK 
                function instead of the RANK function.

            **kendall**
                Kendall's correlation coefficient (similar trends).
                Computes the Tau-B coefficient.
                
                .. warning::
                   This method uses a CROSS JOIN during computation and 
                   is therefore computationally expensive at O(n²), 
                   where n is the total count of the VastFrame.
            
            **cramer**
                Cramer's V (correlation between categories).
                Measures association between categorical variables.
                
            **biserial**
                Biserial Point (correlation between binaries and numericals).
                Measures correlation between binary and continuous variables.

        mround: int, optional
            Rounds the coefficient using the input number of
            digits. This is only used to display the correlation
            matrix (default: 3).
        focus: str, optional
            Focus the computation on one VastColumn.
        show: bool, optional
            If set to True, the Plotting object is
            returned (default: True).
        chart: PlottingObject, optional
            The chart object used to plot.
        **style_kwargs
            Any optional parameter to pass to the plotting
            functions.

        Returns
        -------
        PlottingObject
            Plotting object containing the correlation heatmap.

        Examples
        --------
        **Basic correlation matrix:**

        .. ipython:: python
            
            from vastorbit.datasets import load_titanic
            titanic = load_titanic()
            @savefig core_VastFrame_agg_corr_basic.png
            titanic.corr(method = "pearson")

        **Spearman correlation (rank-based):**

        .. ipython:: python
            
            @savefig core_VastFrame_agg_corr_spearman.png
            titanic.corr(method = "spearman")

        **Focus on specific column:**

        .. ipython:: python
            
            @savefig core_VastFrame_agg_corr_focus.png
            titanic.corr(method = "pearson", focus = "age")

        .. note::
           Pearson correlation assumes linear relationships. For non-linear
           relationships, use Spearman or Kendall methods.

        .. warning::
           Kendall's method is computationally expensive for large datasets.
           Consider using Spearman instead for better performance.

        .. seealso::
        
           | :py:func:`~vastorbit.VastFrame.cov` : Covariance matrix
           | :py:func:`~vastorbit.VastFrame.aggregate` : Custom aggregations
           | :py:mod:`~vastorbit.machine_learning.metrics` : Statistical metrics

        """
        return None

**This docstring renders as:**

----

**Computes the Correlation Matrix of the VastFrame.**

Calculates pairwise correlations between columns using various
correlation methods. Supports both linear and non-linear correlation
measures for different data types.

.. rubric:: Parameters

columns: SQLColumns, optional
    List of the VastColumns names. If empty, all numerical VastColumns are used.
method: str, optional
    Method to use to compute correlation:
    
    - **pearson**: Linear correlation
    - **spearman**: Rank-based monotonic correlation
    - **kendall**: Tau-B coefficient (computationally expensive)
    - **cramer**: Categorical association
    - **biserial**: Binary-continuous correlation

mround: int, optional
    Decimal places for rounding (default: 3)
focus: str, optional
    Focus computation on one column
show: bool, optional
    Return plotting object (default: True)
chart: PlottingObject, optional
    Chart object to plot on
\*\*style_kwargs
    Additional plotting parameters

.. rubric:: Returns

PlottingObject
    Correlation heatmap

**Examples**

Basic correlation matrix:

.. ipython:: python
    
    from vastorbit.datasets import load_titanic
    titanic = load_titanic()
    @savefig core_VastFrame_agg_corr_basic.png
    titanic.corr(method = "pearson")

Spearman correlation:

.. ipython:: python
    
    @savefig core_VastFrame_agg_corr_spearman.png
    titanic.corr(method = "spearman")

Focus on specific column:

.. ipython:: python
    
    @savefig core_VastFrame_agg_corr_focus.png
    titanic.corr(method = "pearson", focus = "age")

.. note::
   Pearson correlation assumes linear relationships. For non-linear
   relationships, use Spearman or Kendall methods.

.. warning::
   Kendall's method is computationally expensive for large datasets.
   Consider using Spearman instead for better performance.

.. seealso::

   | :py:func:`~vastorbit.VastFrame.cov` : Covariance matrix
   | :py:func:`~vastorbit.VastFrame.aggregate` : Custom aggregations

____

Example 4: Data Transformation (pivot)
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Complete function with docstring:**

.. code-block:: python

    def pivot(
        self,
        index: str,
        columns: str,
        values: str,
        aggr: str = "sum",
        prefix: Optional[str] = None,
    ) -> "VastFrame":
        """
        Returns the Pivot of the VastFrame using the input aggregation.

        Reshapes data from long to wide format by pivoting column values
        into new columns. This is useful for creating summary tables and
        cross-tabulations.

        Parameters
        ----------
        index: str
            VastColumn used to group the elements. These values
            become the rows in the pivot table.
        columns: str
            The VastColumn used to compute the different categories,
            which then act as the columns in the pivot table.
        values: str
            The VastColumn whose values populate the new VastFrame.
        aggr: str, optional
            Aggregation to use on 'values' (default: "sum").
            To use complex aggregations, you must use braces: {}.
            
            Examples:
            
            - Simple: ``"MAX"``
            - Complex: ``"MAX({}) - MIN({})"``
            - With constants: ``"AVG({}) * 100"``
        prefix: str, optional
            The prefix for the pivot table's column names.
            Useful for avoiding name conflicts.

        Returns
        -------
        VastFrame
            The pivoted table with reshaped data.

        Examples
        --------
        **Load sample data:**
        
        .. ipython:: python
            :suppress:

            from vastorbit.datasets import load_smart_meters
            sm = load_smart_meters()
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_aggregate_pivot_input.html", "w")
            html_file.write(sm.head(10)._repr_html_())
            html_file.close()

        .. code-block:: python

            from vastorbit.datasets import load_smart_meters
            sm = load_smart_meters()
            sm.head(10)

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_aggregate_pivot_input.html

        **Basic pivot table:**

        .. ipython:: python
            :suppress:

            pivoted = sm.pivot(
                index="time",
                columns="val",
                values="electricity",
                aggr="sum"
            )
            html_file = open("SPHINX_DIRECTORY/figures/core_VastFrame_aggregate_pivot_output.html", "w")
            html_file.write(pivoted.head(5)._repr_html_())
            html_file.close()

        .. code-block:: python

            pivoted = sm.pivot(
                index="time",
                columns="val",
                values="electricity",
                aggr="sum"
            )
            pivoted.head(5)

        .. raw:: html
            :file: SPHINX_DIRECTORY/figures/core_VastFrame_aggregate_pivot_output.html

        **Advanced aggregation:**

        .. code-block:: python

            # Calculate range (max - min)
            pivoted = sm.pivot(
                index="time",
                columns="val",
                values="electricity",
                aggr="MAX({}) - MIN({})"
            )

        .. tip::
           Use the ``prefix`` parameter to avoid column name conflicts
           when pivoting multiple times.

        .. note::
           NULL values in the pivot table indicate no data exists for
           that combination of index and column values.

        .. seealso::
        
           | :py:func:`~vastorbit.VastFrame.groupby` : Group and aggregate
           | :py:func:`~vastorbit.VastFrame.melt` : Reverse operation (wide to long)

        """
        return None

**This docstring renders as:**

----

**Returns the Pivot of the VastFrame using the input aggregation.**

Reshapes data from long to wide format by pivoting column values
into new columns. This is useful for creating summary tables and
cross-tabulations.

.. rubric:: Parameters

index: str
    VastColumn for rows in the pivot table
columns: str
    VastColumn for columns in the pivot table
values: str
    VastColumn to populate the table
aggr: str, optional
    Aggregation function (default: "sum")
prefix: str, optional
    Column name prefix

.. rubric:: Returns

VastFrame
    The pivoted table

**Examples**

Load sample data: *(interactive table shown)*

Basic pivot table: *(shows before/after tables)*

Advanced aggregation with range calculation: *(code example)*

.. tip::
   Use the ``prefix`` parameter to avoid column name conflicts
   when pivoting multiple times.

.. note::
   NULL values in the pivot table indicate no data exists for
   that combination of index and column values.

.. seealso::

   | :py:func:`~vastorbit.VastFrame.groupby` : Group and aggregate
   | :py:func:`~vastorbit.VastFrame.melt` : Reverse operation (wide to long)

____

Key Takeaways
----------------

**Documentation Structure:**

- |check| Headers created with ``----------`` underneath title
- |check| Parameters automatically bolded in NumPy format
- |check| Inline code blocks use double backticks: ````code````
- |check| Cross-references use Sphinx roles: ``:py:func:`~function```

**Code Display Options:**

1. **Static** (``.. code-block:: python``): Show code without execution
2. **Executed** (``.. ipython:: python``): Run code and show output
3. **Hidden** (``.. ipython:: python`` with ``:suppress:``): Run but hide code

**Visualization Methods:**

- |check| **Matplotlib**: Use ``@savefig filename.png`` before ``plt.show()``
- |check| **Plotly**: Save as HTML with ``fig.write_html()`` then include with ``.. raw:: html``
- |check| **VastFrame tables**: Export HTML with ``._repr_html_()`` then include with ``.. raw:: html``

**Admonitions:**

- |check| ``.. note::``: General information
- |check| ``.. tip::``: Best practices
- |check| ``.. hint::``: Gentle guidance
- |check| ``.. important::``: Critical information
- |check| ``.. warning::``: Potential issues
- |check| ``.. danger::``: Severe problems

**File Naming Conventions:**

- Images: ``path_with_underscores_classname_functionname.png``
- HTML: ``path_with_underscores_classname_functionname.html``
- Multiple files: Add ``_1``, ``_2``, etc. suffix

.. note:: 

   Display of admonitions, graphics, and text is affected by the selected theme. 
   Examples compiled using "furo" and "pydata_sphinx_theme".

.. tip::

   Copy these complete examples as templates for your docstrings. They demonstrate
   all the major features and best practices for VAST Orbit documentation.

.. important::

   Always test your examples before committing! Use ``make html`` to build
   the documentation locally and verify all plots, tables, and code examples
   render correctly.

.. seealso::

   - :ref:`contribution_guidelines.code.auto_doc` - Full documentation guide
   - :ref:`contribution_guidelines.code.auto_doc.render` - Preview locally
   - `NumPy Docstring Guide <https://numpydoc.readthedocs.io/en/latest/format.html>`__ - Official style guide