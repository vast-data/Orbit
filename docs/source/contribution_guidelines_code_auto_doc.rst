.. _contribution_guidelines.code.auto_doc:

========================
Automatic Documentation
========================

.. include:: logo_include.rst

Complete guide to generating professional API documentation with Sphinx and reStructuredText.

____

📚 Getting Started
------------------

VastOrbit uses **Sphinx** for documentation generation and **reStructuredText (RST)** as the markup language. RST provides clear, readable documentation writing, and Sphinx generates HTML and other formats from RST files.

**Learning Path:**

1. ✅ Read the reStructuredText (RST) syntax basics below
2. ✅ Explore Sphinx documentation and configuration
3. ✅ Practice with :ref:`contribution_guidelines.code.auto_doc.example`
4. ✅ Use :ref:`contribution_guidelines.code.auto_doc.render` to preview changes

.. tip::

   The best way to learn is by doing. Create a test project, write RST files, and build documentation with Sphinx.

.. toctree::
   :hidden:

   contribution_guidelines_code_auto_doc_render
   contribution_guidelines_code_auto_doc_example

____

🔧 Environment Setup
--------------------

Complete Sphinx Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section covers setting up Sphinx to automate documentation. **(Future: This will be integrated into CI/CD pipeline.)**

**Step-by-Step Setup:**

**1. Clone the Repository**

.. code-block:: bash

    git clone https://github.com/vastdata-dev/vastorbit.git
    cd vastorbit

**2. Create docs Folder**

.. code-block:: bash

    mkdir -p docs

**3. Setup Sphinx Environment**

Download and unzip the essential Sphinx files (make file and source folder) and place them in the docs folder.

**4. Configure conf.py**

Edit ``docs/source/conf.py`` with special attention to:

- **copyright year** - Update to current year
- **release version** - Match VastOrbit version
- **rst_prolog** - Content added to top of every RST file (imports, settings)

Example rst_prolog:

.. code-block:: python

    rst_prolog = """
    .. |vo| replace:: VastOrbit
    
    .. ipython:: python
       :suppress:
       
       import vastorbit as vo
       import pandas as pd
       vo.set_option("mode", "full")
    """

**5. Install Requirements**

.. code-block:: bash

    pip install -r docs/requirements.txt

**6. Install VastOrbit**

.. code-block:: bash

    # Uninstall existing version if present
    pip uninstall vastorbit
    
    # Install from source
    pip install .

**7. Update Directory Paths**

Navigate to docs folder and run:

.. code-block:: bash

    cd docs
    python3 replace_sphinx_dir.py

This updates all directory paths inside VastOrbit code for Sphinx.

**8. Build HTML Documentation**

.. code-block:: bash

    make html

.. note::

   You may need to install make:
   
   .. code-block:: bash
   
       apt install make

**9. Clean Up Function Names**

Remove "vastorbit." prefix from function names:

.. code-block:: bash

    python3 remove_pattern.py

This converts ``vastorbit.VastFrame.bar`` → ``VastFrame.bar``

**10. View Documentation**

HTML files are now in ``docs/build`` directory.

Quick Rebuild Script
~~~~~~~~~~~~~~~~~~~~

For convenience, use the ``refresh.sh`` script after making code/docstring changes:

.. code-block:: bash

    ./refresh.sh

.. note::

   You may need to make it executable:
   
   .. code-block:: bash
   
       chmod +x refresh.sh

____

📖 RST Syntax Guide
-------------------

Headers and Subheaders
~~~~~~~~~~~~~~~~~~~~~~

**Normal Headers:**

Use ``--------`` underneath text to mark as header:

.. code-block:: rst

    Function Name
    -------------

**Sections and Subsections:**

Use ``=======`` for main sections and ``-------`` for subsections:

.. code-block:: rst

    Parameters
    ==========
    method: str, optional
        Description here.
    
    Subsection
    ----------
    Some text here.
    
    Returns
    =======
    float
        Return value description.

**Centered Headers:**

.. code-block:: rst

    .. centered:: Some Centered Information!

**Output:**

.. centered:: Some Centered Information!

Indentation and Line Spacing
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Line spacing and indentation must be carefully managed. Without line breaks, all text is treated as a single line. Use ``|`` to go to next line without adding extra space.

**Example 1: Using | for compact spacing**

.. code-block:: rst

    Parameters
    ----------
    method: str, optional
        Method used to compute the optimal h.
            | auto : Combination of Freedman Diaconis and Sturges.
            | freedman_diaconis : Freedman Diaconis 
            | sturges : Sturges

**Output:**

    method: str, optional
        Method used to compute the optimal h.
            | auto : Combination of Freedman Diaconis and Sturges.
            | freedman_diaconis : Freedman Diaconis 
            | sturges : Sturges

**Example 2: Using blank lines for spacing**

.. code-block:: rst

    Parameters
    ----------
    method: str, optional
        Method used to compute the optimal h.
            auto : Combination of Freedman Diaconis and Sturges.

            freedman_diaconis : Freedman Diaconis 

            sturges : Sturges

**Output:**

    method: str, optional
        Method used to compute the optimal h.
            auto : Combination of Freedman Diaconis and Sturges.

            freedman_diaconis : Freedman Diaconis 

            sturges : Sturges

**Example 3: Aligned formatting**

.. code-block:: rst

    Parameters
    ----------
    method: str, optional
        Method used to compute the optimal h.
            auto              : Combination of Freedman Diaconis
                                and Sturges.
            freedman_diaconis : Freedman Diaconis
            sturges           : Sturges

**Output:**

    method: str, optional
        Method used to compute the optimal h.
            auto              : Combination of Freedman Diaconis
                                and Sturges.
            freedman_diaconis : Freedman Diaconis
            sturges           : Sturges

Code Blocks
~~~~~~~~~~~

**Static Code (Not Executed):**

.. code-block:: rst

    .. code-block:: python

       import vastorbit as vo
       vo.VastFrame({"a":[1,2,3]})

**Output:**

.. code-block:: python

   import vastorbit as vo
   vo.VastFrame({"a":[1,2,3]})

Code Execution
~~~~~~~~~~~~~~

Execute and display code using the ipython directive.

.. note::

   Requires extensions in conf.py:
   
   - ``IPython.sphinxext.ipython_directive``
   - ``IPython.sphinxext.ipython_console_highlighting``

**Basic Execution:**

.. code-block:: rst

    .. ipython:: python

        import vastorbit as vo
        vo.VastFrame({"a":[1,2,3]})

Suppressing Code/Output
~~~~~~~~~~~~~~~~~~~~~~~~

**Method 1: Suppress Entire Block**

Use ``:suppress:`` directive option to hide entire code block:

.. code-block:: rst

    .. ipython:: python
        :suppress: 
        
        import vastorbit as vo
        import pandas as pd
        import sys
        
    .. ipython:: python

        print(vo.VastFrame({"a":[1,2,3]}))

**Output:**

.. ipython:: python
    :suppress: 
    
    import vastorbit as vo
    import pandas as pd
    import sys
    
.. ipython:: python

    print(vo.VastFrame({"a":[1,2,3]}))

**Method 2: Suppress Single Line**

Use ``@suppress`` pseudo-directive:

.. code-block:: rst

    .. ipython:: python

        @suppress      
        import vastorbit as vo
        print(vo.VastFrame({"a":[1,2,3]}))

**When to Use:**

- **Block suppress**: For multiple import statements
- **@suppress**: For skipping single lines

Links and References
~~~~~~~~~~~~~~~~~~~~

**Internal References:**

.. code-block:: rst

    # Section reference
    :ref:`api.vastframe`
    
    # Function reference
    :py:func:`~vastorbit.VastFrame.bar`
    
    # Module reference
    :py:mod:`~vastorbit.VastFrame`

**External Links:**

.. code-block:: rst

    `Link Text <https://example.com>`_

Lists
~~~~~

.. code-block:: rst

    **Bullet List:**
    
    - Item 1
    - Item 2
      - Nested item
    
    **Numbered List:**
    
    1. First item
    2. Second item
    3. Third item

____

📊 Plotting and Visualizations
-------------------------------

Matplotlib Plots
~~~~~~~~~~~~~~~~

Use ``@savefig`` pseudo-directive to save matplotlib figures:

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import matplotlib.pyplot as plt
        x = [1, 2, 3, 4, 5]
        y = [2, 4, 6, 8, 10]
        plt.plot(x, y, marker='o', linestyle='-')
        plt.xlabel('X-axis')
        plt.ylabel('Y-axis')
        plt.title('Simple Linear Plot')
        @savefig simple_plot.png
        plt.show()

**Output:**

.. ipython:: python
    :suppress:

    import matplotlib.pyplot as plt
    x = [1, 2, 3, 4, 5]
    y = [2, 4, 6, 8, 10]
    plt.plot(x, y, marker='o', linestyle='-')
    plt.xlabel('X-axis')
    plt.ylabel('Y-axis')
    plt.title('Simple Linear Plot')
    @savefig simple_plot.png
    plt.show()

Image File Naming Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. important::

   **Naming Convention for Images:**
   
   Format: ``path_with_underscores_classname_functionname.png``
   
   **Example:** For boxplot function in ``core/VastFrame/_plotting.py`` inside vDFPlot class:
   
   ``core_VastFrame__plotting_vDFPlot_boxplot.png``
   
   **Multiple plots in one function:**
   
   - ``core_VastFrame__plotting_vDFPlot_boxplot_1.png``
   - ``core_VastFrame__plotting_vDFPlot_boxplot_2.png``

VastOrbit Plots
~~~~~~~~~~~~~~~

**Matplotlib Backend:**

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
        @savefig vastorbit_plot.png
        data.bar("counts")

**Output:**

.. ipython:: python
    :suppress:

    import vastorbit as vo
    data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
    @savefig vastorbit_plot.png
    data.bar("counts")

**Plotly Backend:**

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        vo.set_option("plotting_lib","plotly")
        data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
        fig = data.bar("counts")
        fig.write_html("figures/plotly_bar.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotly_bar.html

.. note::

   Matplotlib files can be saved as PNG images. Plotly and Highcharts must be saved as HTML files.

Advanced HTML Output
~~~~~~~~~~~~~~~~~~~~

For advanced graphics (VastFrame output, Plotly charts), use this methodology:

1. Create HTML representation
2. Save as HTML file
3. Load and display HTML file

**VastFrame Output:**

.. code-block:: rst

    .. ipython:: python
        :suppress:

        import vastorbit as vo
        html_file = open("figures/vastframe_output.html", "w")
        html_file.write(vo.VastFrame({"a":[1,2,3]})._repr_html_())
        html_file.close()

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/vastframe_output.html

**Plotly Correlation Table:**

.. code-block:: rst

    .. ipython:: python
        :suppress:

        from vastorbit.datasets import load_titanic
        titanic = load_titanic()
        fig = titanic.corr(method = "spearman")
        fig.write_html("figures/plotly_corr.html")

    .. raw:: html
        :file: SPHINX_DIRECTORY/figures/plotly_corr.html

HTML File Naming Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. important::

   **Naming Convention for HTML Files:**
   
   Same as images: ``path_with_underscores_classname_functionname.html``
   
   **Important:**
   
   - Add ``figures/`` prefix when saving: ``"figures/filename.html"``
   - Use ``SPHINX_DIRECTORY/figures/`` when loading in raw html directive

____

📋 Tables
---------

CSV Table Directive
~~~~~~~~~~~~~~~~~~~

Easiest method for creating tables:

.. code-block:: rst

    .. csv-table:: **Table Title**
        :header: Column Header, Another Column
        :widths: 30, 70

        Row 1 Value, Value in Row 1
        Row 2 Value, Value in Row 2
        Row 3 Value, Value in Row 3

**Output:**

.. csv-table:: **Table Title**
    :header: Column Header, Another Column
    :widths: 30, 70

    Row 1 Value, Value in Row 1
    Row 2 Value, Value in Row 2
    Row 3 Value, Value in Row 3

Manual Table Format
~~~~~~~~~~~~~~~~~~~

More control but more complex:

.. code-block:: rst

    +---------------+------------------+
    | Column Header | Another Column   |
    +===============+==================+
    | Row 1 Value   | Value in Row 1   |
    +---------------+------------------+
    | Row 2 Value   | Value in Row 2   |
    +---------------+------------------+
    | Row 3 Value   | Value in Row 3   |
    +---------------+------------------+

**Output:**

+---------------+------------------+
| Column Header | Another Column   |
+===============+==================+
| Row 1 Value   | Value in Row 1   |
+---------------+------------------+
| Row 2 Value   | Value in Row 2   |
+---------------+------------------+
| Row 3 Value   | Value in Row 3   |
+---------------+------------------+

____

📝 Admonitions and Directives
------------------------------

See Also
~~~~~~~~

.. code-block:: rst

    .. seealso:: :py:mod:`~vastorbit.VastFrame.bar`
        Documentation of the bar chart function.

**Output:**

.. seealso:: :py:mod:`~vastorbit.VastFrame.bar`
    Documentation of the bar chart function.

Deprecation Warning
~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

    .. deprecated:: 3.8

**Output:**

.. deprecated:: 3.8

Notes, Warnings, and More
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

    .. note:: This is a note.

    .. tip:: This is a helpful tip.

    .. hint:: This is a hint.

    .. important:: This is important information.

    .. warning:: This is a warning.

    .. danger:: This is a danger warning.

**Output:**

.. note:: This is a note.

.. tip:: This is a helpful tip.

.. hint:: This is a hint.

.. important:: This is important information.

.. warning:: This is a warning.

.. danger:: This is a danger warning.

____

✍️ Docstring Standards
-----------------------

NumPy Style Template
~~~~~~~~~~~~~~~~~~~~

VastOrbit follows NumPy docstring conventions:

.. code-block:: python

    def function_name(param1: str, param2: int = 0) -> dict:
        """
        Brief one-line description of the function.
        
        Longer description providing more details about the function's
        purpose, behavior, and any important notes.
        
        Parameters
        ----------
        param1 : str
            Description of the first parameter. Explain what it does
            and any constraints or requirements.
        param2 : int, optional
            Description of the second parameter. 
            Default value is 0.
        
        Returns
        -------
        dict
            Description of the return value. Explain the structure
            and contents of what's returned.
        
        Examples
        --------
        Basic usage:
        
        .. code-block:: python
        
           result = function_name("test", 5)
           print(result)
        
        Advanced usage:
        
        .. ipython:: python
        
           result = function_name("advanced", param2=10)
           result
        
        See Also
        --------
        related_function : Brief description of related function
        another_function : Another related function
        
        Notes
        -----
        Any additional notes, implementation details, or 
        important considerations for users.
        
        References
        ----------
        .. [1] Author Name, "Paper Title", Journal, Year.
        """

Best Practices
~~~~~~~~~~~~~~

**Key Points:**

- ✅ Use NumPy docstring style consistently
- ✅ Include complete type hints in function signature
- ✅ Provide at least one working example
- ✅ Cross-reference related functions
- ✅ Keep descriptions clear and concise
- ✅ Use proper RST formatting in docstrings
- ✅ Test examples actually work before committing

**Common Sections:**

- **Parameters** - All function arguments
- **Returns** - What the function returns
- **Raises** - Exceptions that may be raised
- **Examples** - Working code examples
- **See Also** - Related functions
- **Notes** - Additional information
- **References** - Citations if applicable

____

🔗 Useful Resources
-------------------

**reStructuredText (RST):**

- `RST Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`_ - Official RST basics from Sphinx
- `RST Directives <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`_ - Available directives and formatting options
- `RST Cheat Sheet <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`_ - Quick reference for common markup
- `RST Syntax Specification <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`_ - Complete syntax specification

**Sphinx:**

- `Sphinx Domains and Roles <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html>`_ - Specialized markup for Python code
- `Sphinx Configuration <https://www.sphinx-doc.org/en/master/usage/configuration.html>`_ - Configure Sphinx behavior
- `Common RST Substitutions <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#substitutions>`_ - Reusable content definitions

**Python Documentation:**

- `Docutils Documentation <https://docutils.sourceforge.io/docs/index.html>`_ - RST parsing library
- `NumPy Docstring Guide <https://numpydoc.readthedocs.io/en/latest/format.html>`_ - Standard docstring format

**VastOrbit Specific:**

- :ref:`contribution_guidelines.code.auto_doc.example` - Complete documentation examples
- :ref:`contribution_guidelines.code.auto_doc.render` - Preview documentation locally

____

.. tip::

   **Learning Strategy:**
   
   1. Start by copying well-documented functions as templates
   2. Check :py:func:`~vastorbit.VastFrame.bar` for a good reference
   3. Build documentation locally and preview changes
   4. Iterate until it looks professional

.. seealso::

   - :ref:`contribution_guidelines.code` - Code contribution guidelines
   - :ref:`cicd` - CI/CD pipeline and automated checks
   - :ref:`api` - Complete API reference