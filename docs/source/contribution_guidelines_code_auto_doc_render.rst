.. _contribution_guidelines.code.auto_doc.render:

=======================
Render Your Docstring
=======================

.. include:: logo_include.rst

Preview your documentation locally before submitting.

____

Quick Start
--------------

**Two Options:**

1. **Simple Testing** - Test single file (recommended for quick checks)
2. **Full Setup** - Complete Sphinx environment (see `Sphinx Quickstart <https://www.sphinx-doc.org/en/master/usage/quickstart.html>`__)

____

Simple Testing Setup
-----------------------

**Step 1: Download Test Package**

Download and unzip the test package in your working directory.

**Step 2: Install Requirements**

.. code-block:: bash

    cd docs
    pip install -r requirements.txt

.. tip:: 

   Create a virtual environment first:
   
   .. code-block:: bash
   
       python -m venv venv
       source venv/bin/activate  # On Windows: venv\Scripts\activate
       pip install -r requirements.txt

**Step 3: Install Make**

.. code-block:: bash

    # Linux/macOS
    sudo apt install make
    
    # macOS (alternative)
    brew install make

.. note:: ``sudo`` is optional if you have admin rights.

**Step 4: Add Your File**

Place your Python file inside ``docs/`` and rename it ``test_file.py``.

.. note:: 

   There's an example ``test_file.py`` already present. Delete it and replace with yours.

**Step 5: Build Documentation**

.. code-block:: bash

    make html

**Step 6: View Results**

Open ``build/html/index.html`` in your browser.

.. code-block:: bash

    # Linux
    xdg-open build/html/index.html
    
    # macOS
    open build/html/index.html
    
    # Windows
    start build/html/index.html

____

Iterating on Changes
------------------------

**Make Changes → Clean → Rebuild**

.. code-block:: bash

    # 1. Edit test_file.py
    
    # 2. Clean old build
    make clean
    
    # 3. Rebuild
    make html
    
    # 4. Refresh browser

**Quick Rebuild Script:**

.. code-block:: bash

    # Create rebuild.sh
    echo "make clean && make html" > rebuild.sh
    chmod +x rebuild.sh
    
    # Use it
    ./rebuild.sh

____

What to Check
----------------

**Visual Checks:**

- |check| Function signature displays correctly
- |check| Parameters formatted properly
- |check| Code examples render with syntax highlighting
- |check| Plots/images appear correctly
- |check| Links work (internal and external)
- |check| Admonitions (notes, warnings) styled properly
- |check| Table formatting looks clean

**Common Issues:**

- |cross| **Missing imports** - Add to ``rst_prolog`` in ``conf.py``

- |cross| **Plot not showing** - Check file path and ``@savefig`` directive

- |cross| **Broken links** - Verify reference targets exist

- |cross| **Code not executing** - Check ``ipython`` directive syntax

____

Example test_file.py
------------------------

.. code-block:: python

    """
    Test module for documentation rendering.
    """

    def example_function(x: int, y: int = 0) -> int:
        """
        Example function with complete docstring.
        
        Parameters
        ----------
        x : int
            First parameter
        y : int, optional
            Second parameter. Default is 0.
        
        Returns
        -------
        int
            Sum of x and y
        
        Examples
        --------
        .. code-block:: python
        
           result = example_function(5, 3)
           print(result)
           >>> 8
        
        .. ipython:: python
        
           example_function(10, 5)
        
        See Also
        --------
        other_function : Related function
        """
        return x + y

____

Troubleshooting
-------------------

**Build Errors:**

.. code-block:: bash

    # Clear cache completely
    make clean
    rm -rf build/
    
    # Rebuild
    make html

**Import Errors:**

Edit ``conf.py`` and add to ``rst_prolog``:

.. code-block:: python

    rst_prolog = """
    .. ipython:: python
       :suppress:
       
       import vastorbit as vo
       import sys
       sys.path.insert(0, '/path/to/your/module')
    """

**Warnings:**

Check ``build/html/output.txt`` for detailed warnings and fix accordingly.

____

.. tip::

   **Pro Workflow:**
   
   1. Write docstring in your editor
   2. Copy to ``test_file.py``
   3. Run ``make clean && make html``
   4. Check browser
   5. Iterate until perfect
   6. Copy back to actual file

.. seealso::

   - :ref:`contribution_guidelines.code.auto_doc` - Complete documentation guide
   - :ref:`contribution_guidelines.code.auto_doc.example` - Docstring examples
   - `Sphinx Documentation <https://www.sphinx-doc.org/>`__ - Official Sphinx docs