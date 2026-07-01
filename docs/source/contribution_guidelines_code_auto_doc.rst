.. _contribution_guidelines.code.auto_doc:

========================
Automatic Documentation
========================

.. include:: logo_include.rst

Complete guide to generating professional API documentation with Sphinx and reStructuredText.

____

Getting Started
------------------

VAST Orbit uses **Sphinx** for documentation generation and **reStructuredText (RST)** as the markup language. RST provides clear, readable documentation writing, and Sphinx generates HTML and other formats from RST files.

**Learning Path:**

1. Read the reStructuredText (RST) syntax basics below
2. Explore Sphinx documentation and configuration
3. Practice with :ref:`contribution_guidelines.code.auto_doc.example`
4. Use :ref:`contribution_guidelines.code.auto_doc.render` to preview changes

.. tip::

   The best way to learn is by doing. Create a test project, write RST files, and build documentation with Sphinx.

.. toctree::
   :hidden:

   contribution_guidelines_code_auto_doc_render
   contribution_guidelines_code_auto_doc_example

____

Environment Setup
--------------------

Complete Sphinx Environment Configuration
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

This section covers setting up Sphinx to automate documentation. **(Future: This will be integrated into CI/CD pipeline.)**

**Step-by-Step Setup:**

**1. Clone the Repository**

.. code-block:: bash

   git clone https://github.com/vast-data/VAST-Orbit.git
   cd vastorbit

**2. Create docs Folder**

.. code-block:: bash

   mkdir -p docs

**3. Setup Sphinx Environment**

Download and unzip the essential Sphinx files (make file and source folder) and place them in the docs folder.

**4. Configure conf.py**

Edit ``docs/source/conf.py`` with special attention to:

- **copyright year** - Update to current year
- **release version** - Match VAST Orbit version
- **rst_prolog** - Content added to top of every RST file (imports, settings)

Example rst_prolog:

.. code-block:: python

   rst_prolog = """
   .. |vo| replace:: VAST Orbit
   
   .. ipython:: python
      :suppress:
      
      import vastorbit as vo
      import pandas as pd
      vo.set_option("mode", "full")
   """

**5. Install Requirements**

.. code-block:: bash

   pip install -r docs/requirements.txt

**6. Install VAST Orbit**

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

This updates all directory paths inside VAST Orbit code for Sphinx.

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

RST Syntax Guide
-------------------

Headers and Subheaders
~~~~~~~~~~~~~~~~~~~~~~

**Normal Headers:**

Use ``--------`` underneath text to mark as header:

.. code-block:: rst

   Function Name
   -------------

**This renders as:**

.. rubric:: Function Name


----

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

**This renders as:**

.. rubric:: Parameters

method: str, optional
    Description here.

.. rubric:: Subsection

Some text here.

.. rubric:: Returns

float
    Return value description.

----

**Centered Headers:**

.. code-block:: rst

   .. centered:: Some Centered Information!

**This renders as:**

.. centered:: Some Centered Information!

----

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

**This renders as:**

.. rubric:: Parameters

method: str, optional
    Method used to compute the optimal h.
        | auto : Combination of Freedman Diaconis and Sturges.
        | freedman_diaconis : Freedman Diaconis 
        | sturges : Sturges

*(Notice: Each line starts with | and there's no extra spacing between options)*

----

**Example 2: Using blank lines for spacing**

.. code-block:: rst

   Parameters
   ----------
   method: str, optional
       Method used to compute the optimal h.
           auto : Combination of Freedman Diaconis and Sturges.

           freedman_diaconis : Freedman Diaconis 

           sturges : Sturges

**This renders as:**

.. rubric:: Parameters

method: str, optional
    Method used to compute the optimal h.
        auto : Combination of Freedman Diaconis and Sturges.

        freedman_diaconis : Freedman Diaconis 

        sturges : Sturges

*(Notice: Extra spacing between each option for better readability)*

----

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

**This renders as:**

.. rubric:: Parameters

method: str, optional
    Method used to compute the optimal h.

    ::

        auto              : Combination of Freedman Diaconis
                            and Sturges.
        freedman_diaconis : Freedman Diaconis
        sturges           : Sturges

*(Notice: Options are aligned for a clean, professional look)*

----

Code Blocks
~~~~~~~~~~~

**Static Code (Not Executed):**

Show code without executing it:

.. code-block:: rst

   .. code-block:: python

      import vastorbit as vo
      vo.VastFrame({"a":[1,2,3]})

**This renders as:**

.. code-block:: python

   import vastorbit as vo
   vo.VastFrame({"a":[1,2,3]})

*(Notice: Code is displayed but not executed - just syntax highlighting)*

----

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

**This renders as:**

.. ipython:: python

   import vastorbit as vo
   vo.VastFrame({"a":[1,2,3]})

*(Notice: Code is executed and output is shown, including the VastFrame table)*

----

Suppressing Code/Output
~~~~~~~~~~~~~~~~~~~~~~~~

**Method 1: Suppress Entire Block**

Use ``:suppress:`` directive option to hide entire code block while still executing it:

.. code-block:: rst

   .. ipython:: python
      :suppress: 
      
      import vastorbit as vo
      import pandas as pd
      import sys
      
   .. ipython:: python

      print(vo.VastFrame({"a":[1,2,3]}))

**This renders as:**

.. ipython:: python
   :suppress: 
   
   import vastorbit as vo
   import pandas as pd
   import sys
   
.. ipython:: python

   print(vo.VastFrame({"a":[1,2,3]}))

*(Notice: The import statements are completely hidden - neither code nor output is shown. Only the print statement and its output are visible.)*

----

**Method 2: Suppress Single Line**

Use ``@suppress`` pseudo-directive to hide one line:

.. code-block:: rst

   .. ipython:: python

      @suppress      
      import vastorbit as vo
      print(vo.VastFrame({"a":[1,2,3]}))

**This renders as:**

.. ipython:: python

   @suppress      
   import vastorbit as vo
   print(vo.VastFrame({"a":[1,2,3]}))

*(Notice: The import line with @suppress is hidden, but the print output is still shown)*

**When to Use:**

- **Block suppress** (``:suppress:``): For hiding multiple import statements or setup code
- **Line suppress** (``@suppress``): For hiding single lines within visible code blocks

----

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

**This renders as:**

Section reference: :ref:`api.vastframe`

Function reference: :py:func:`~vastorbit.VastFrame.bar`

Module reference: :py:mod:`~vastorbit.VastFrame`

*(Notice: These become clickable links in the HTML documentation)*

----

**External Links:**

.. code-block:: rst

   `Link Text <https://example.com>`__

**This renders as:**

`Link Text <https://example.com>`__

----

Lists
~~~~~

**Bullet List:**

.. code-block:: rst

   - Item 1
   - Item 2
     - Nested item
   - Item 3

**This renders as:**

- Item 1
- Item 2
  - Nested item
- Item 3

----

**Numbered List:**

.. code-block:: rst

   1. First item
   2. Second item
   3. Third item

**This renders as:**

1. First item
2. Second item
3. Third item

____

Plotting and Visualizations
-------------------------------

Matplotlib Plots
~~~~~~~~~~~~~~~~

The ``@savefig`` directive saves the matplotlib figure to a file and displays it in the documentation.

**How it works:**

1. Create your plot with matplotlib
2. Add ``@savefig filename.png`` on its own line, right before ``plt.show()``
3. The image is automatically saved to ``_images/`` directory and embedded in the documentation

**Example Code:**

.. code-block:: rst

   .. ipython:: python
      :suppress:

      import matplotlib.pyplot as plt
      
      # Create data
      x = [1, 2, 3, 4, 5]
      y = [2, 4, 6, 8, 10]
      
      # Create plot
      plt.plot(x, y, marker='o', linestyle='-')
      plt.xlabel('X-axis')
      plt.ylabel('Y-axis')
      plt.title('Simple Linear Plot')
      
      # Save and display the figure
      @savefig simple_plot.png
      plt.show()

**This renders as:**

.. ipython:: python
   :suppress:
   :okwarning:

   import matplotlib.pyplot as plt
   x = [1, 2, 3, 4, 5]
   y = [2, 4, 6, 8, 10]
   plt.plot(x, y, marker='o', linestyle='-')
   plt.xlabel('X-axis')
   plt.ylabel('Y-axis')
   plt.title('Simple Linear Plot')
   @savefig simple_plot.png
   plt.show()

*(Notice: The code is hidden by :suppress:, but the plot is displayed. The image is also saved as simple_plot.png)*

----

**Key Points about @savefig:**

- ``@savefig`` must be on its own line, immediately before ``plt.show()``
- The ``:suppress:`` option hides the code from output (shows only the plot)
- Images are saved to ``_images/`` directory automatically
- The saved image can be reused elsewhere with:

  .. code-block:: rst
  
     .. image:: _images/simple_plot.png

----

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
   - ``core_VastFrame__plotting_vDFPlot_boxplot_3.png``

----

VAST Orbit Plots
~~~~~~~~~~~~~~~~

**Matplotlib Backend:**

.. code-block:: rst

   .. ipython:: python
      :suppress:

      import vastorbit as vo
      data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
      @savefig vastorbit_plot.png
      data.bar("counts")

**This renders as:**

.. ipython:: python
   :suppress:

   import vastorbit as vo
   data = vo.VastFrame({"counts":[1,1,1,2,2,3]})
   @savefig vastorbit_plot.png
   data.bar("counts")

*(Notice: VAST Orbit plot saved as PNG and displayed inline)*

----

**Plotly Backend:**

For Plotly charts, you need to save as HTML and include it:

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

   **Important Differences:**
   
   - **Matplotlib**: Save as PNG with ``@savefig filename.png``
   - **Plotly**: Save as HTML with ``fig.write_html()`` and include with ``.. raw:: html``

----

Advanced HTML Output
~~~~~~~~~~~~~~~~~~~~

For advanced graphics (VastFrame output, Plotly charts, interactive tables), use this methodology:

1. Generate HTML representation with ``._repr_html_()`` or ``.write_html()``
2. Save as HTML file in ``figures/`` directory
3. Load and display HTML file with ``.. raw:: html`` directive

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

*(This embeds the interactive VastFrame table directly in the documentation)*

----

**Plotly Correlation Matrix:**

.. code-block:: rst

   .. ipython:: python
      :suppress:

      from vastorbit.datasets import load_titanic
      titanic = load_titanic()
      fig = titanic.corr(method = "spearman")
      fig.write_html("figures/plotly_corr.html")

   .. raw:: html
      :file: SPHINX_DIRECTORY/figures/plotly_corr.html

*(This embeds an interactive Plotly correlation heatmap)*

----

HTML File Naming Convention
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

.. important::

   **Naming Convention for HTML Files:**
   
   Same as images: ``path_with_underscores_classname_functionname.html``
   
   **File Paths - Two Different Conventions:**
   
   1. **When saving** (in Python code): Use relative path ``"figures/filename.html"``
   2. **When loading** (in raw html directive): Use absolute path ``SPHINX_DIRECTORY/figures/filename.html``
   
   **Example:**
   
   .. code-block:: python
   
      # Saving (relative path)
      fig.write_html("figures/core_VastFrame_corr.html")
   
   .. code-block:: rst
   
      # Loading (absolute path)
      .. raw:: html
         :file: SPHINX_DIRECTORY/figures/core_VastFrame_corr.html

____

Tables
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

**This renders as:**

.. csv-table:: **Table Title**
   :header: Column Header, Another Column
   :widths: 30, 70

   Row 1 Value, Value in Row 1
   Row 2 Value, Value in Row 2
   Row 3 Value, Value in Row 3

----

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

**This renders as:**

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

Admonitions and Directives
------------------------------

See Also
~~~~~~~~

.. code-block:: rst

   .. seealso:: 
   
      :py:mod:`~vastorbit.VastFrame.bar`
         Documentation of the bar chart function.

**This renders as:**

.. seealso:: 

   :py:mod:`~vastorbit.VastFrame.bar`
      Documentation of the bar chart function.

----

Deprecation Warning
~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

   .. deprecated:: 3.8
      This feature is deprecated and will be removed in version 4.0.

**This renders as:**

.. deprecated:: 3.8
   This feature is deprecated and will be removed in version 4.0.

----

Notes, Warnings, and More
~~~~~~~~~~~~~~~~~~~~~~~~~~

.. code-block:: rst

   .. note:: 
      This is a note with important information.

   .. tip:: 
      This is a helpful tip for users.

   .. hint:: 
      This is a hint to guide users.

   .. important:: 
      This is important information that users must know.

   .. warning:: 
      This is a warning about potential issues.

   .. danger:: 
      This is a danger warning for critical situations.

**This renders as:**

.. note:: 
   This is a note with important information.

.. tip:: 
   This is a helpful tip for users.

.. hint:: 
   This is a hint to guide users.

.. important:: 
   This is important information that users must know.

.. warning:: 
   This is a warning about potential issues.

.. danger:: 
   This is a danger warning for critical situations.

____

Docstring Standards
-----------------------

NumPy Style Template
~~~~~~~~~~~~~~~~~~~~

VAST Orbit follows NumPy docstring conventions. Here's a complete template:

.. code-block:: python

   def function_name(param1: str, param2: int = 0) -> dict:
       """
       Brief one-line description of the function.
       
       Longer description providing more details about the function's
       purpose, behavior, and any important notes. This can span
       multiple lines and include detailed explanations.
       
       Parameters
       ----------
       param1 : str
           Description of the first parameter. Explain what it does,
           any constraints or requirements, and expected format.
       param2 : int, optional
           Description of the second parameter. Explain its purpose
           and behavior. Default value is 0.
       
       Returns
       -------
       dict
           Description of the return value. Explain the structure
           and contents of what's returned, including key names
           and value types if returning a dictionary.
       
       Raises
       ------
       ValueError
           If param1 is empty or invalid.
       TypeError
           If param2 is not an integer.
       
       Examples
       --------
       Basic usage example:
       
       .. code-block:: python
       
          result = function_name("test", 5)
          print(result)
       
       Advanced usage with actual execution:
       
       .. ipython:: python
       
          result = function_name("advanced", param2=10)
          result
       
       See Also
       --------
       related_function : Brief description of how it relates
       another_function : Another related function
       :py:func:`~vastorbit.module.other_function` : Cross-reference
       
       Notes
       -----
       Any additional notes, implementation details, algorithm
       explanations, or important considerations for users.
       
       This section can include:
       
       - Performance characteristics
       - Edge cases to be aware of
       - Best practices
       
       References
       ----------
       .. [1] Author Name, "Paper Title", Journal, Year.
       .. [2] Book Author, "Book Title", Publisher, Year.
       """

----

Best Practices
~~~~~~~~~~~~~~

**Key Points:**

- |check| Use NumPy docstring style consistently across all functions
- |check| Include complete type hints in function signature (e.g., ``param: str``)
- |check| Provide at least one working example that users can copy-paste
- |check| Cross-reference related functions with ``:py:func:`` directive
- |check| Keep descriptions clear, concise, and user-focused
- |check| Use proper RST formatting in docstrings (code blocks, lists, etc.)
- |check| Test that all examples actually work before committing

**Common Sections (in order):**

1. **Short Summary** - One-line description
2. **Extended Summary** - Detailed explanation (optional but recommended)
3. **Parameters** - All function arguments with types and descriptions
4. **Returns** - What the function returns with type and description
5. **Raises** - Exceptions that may be raised (optional)
6. **Examples** - Working code examples (at least one required)
7. **See Also** - Related functions (optional)
8. **Notes** - Additional information (optional)
9. **References** - Citations if applicable (optional)

**Parameter Description Format:**

.. code-block:: rst

   parameter_name : type
       Description of the parameter. Can span multiple lines
       with proper indentation. Include constraints, default
       behavior, and any important notes.

**Example of good vs bad:**

|cross| **Bad:**

.. code-block:: python

   def process_data(x, y):
       """Process data."""
       return x + y

|check| **Good:**

.. code-block:: python

   def process_data(x: float, y: float) -> float:
       """
       Add two numbers together.
       
       Parameters
       ----------
       x : float
           First number to add.
       y : float
           Second number to add.
       
       Returns
       -------
       float
           Sum of x and y.
       
       Examples
       --------
       .. ipython:: python
       
          process_data(2.5, 3.5)
       """
       return x + y

____

Useful Resources
-------------------

**reStructuredText (RST):**

- `RST Primer <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html>`__ - Official RST basics from Sphinx
- `RST Directives <https://www.sphinx-doc.org/en/master/usage/restructuredtext/directives.html>`__ - Available directives and formatting options
- `RST Cheat Sheet <https://docutils.sourceforge.io/docs/user/rst/quickref.html>`__ - Quick reference for common markup
- `RST Syntax Specification <https://docutils.sourceforge.io/docs/ref/rst/restructuredtext.html>`__ - Complete syntax specification

**Sphinx:**

- `Sphinx Domains and Roles <https://www.sphinx-doc.org/en/master/usage/restructuredtext/domains.html>`__ - Specialized markup for Python code
- `Sphinx Configuration <https://www.sphinx-doc.org/en/master/usage/configuration.html>`__ - Configure Sphinx behavior
- `Common RST Substitutions <https://www.sphinx-doc.org/en/master/usage/restructuredtext/basics.html#substitutions>`__ - Reusable content definitions

**Python Documentation:**

- `Docutils Documentation <https://docutils.sourceforge.io/docs/index.html>`__ - RST parsing library
- `NumPy Docstring Guide <https://numpydoc.readthedocs.io/en/latest/format.html>`__ - Standard docstring format we follow
- `Sphinx Napoleon <https://www.sphinx-doc.org/en/master/usage/extensions/napoleon.html>`__ - Extension for parsing NumPy docstrings

**VAST Orbit Specific:**

- :ref:`contribution_guidelines.code.auto_doc.example` - Complete documentation examples
- :ref:`contribution_guidelines.code.auto_doc.render` - Preview documentation locally

____

.. tip::

   **Learning Strategy:**
   
   1. Start by copying well-documented functions as templates
   2. Check :py:func:`~vastorbit.VastFrame.bar` for a reference example
   3. Build documentation locally with ``make html`` and preview changes
   4. Compare your rendered output with existing documentation
   5. Iterate until it looks professional and matches the style guide

.. seealso::

   - :ref:`contribution_guidelines.code` - Code contribution guidelines
   - :ref:`cicd` - CI/CD pipeline and automated checks
   - :ref:`api` - Complete API reference