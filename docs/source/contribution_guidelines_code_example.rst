.. _contribution_guidelines.code.example:

====================
Code Example
====================

.. include:: logo_include.rst

Step-by-step guide to adding new functions to VastOrbit.

____

🏗️ VastOrbit Architecture
--------------------------

**Core Objects:**

- **VastFrame** - Main data structure (like pandas DataFrame)
- **VastColumn** - Individual columns within VastFrame

**Code Organization:**

.. code-block:: text

    vastorbit/core/
    ├── VastFrame/
    │   ├── _aggregate.py      # Aggregation methods (sum, mean, etc.)
    │   ├── _plotting.py        # Visualization methods
    │   ├── _transform.py       # Data transformation
    │   └── ...
    └── VastColumn/
        ├── _statistics.py      # Statistical methods
        ├── _encoding.py        # Encoding methods
        └── ...

.. tip::

   Similar methods are grouped together. Add your function to the appropriate file based on functionality.

____

✍️ Function Template
--------------------

Type Hints
~~~~~~~~~~

Always specify type hints for all parameters:

.. code-block:: python

    from typing import Union, Optional, Literal
    
    @save_vastorbit_logs
    def pie(
        self,
        columns: SQLColumns,
        max_cardinality: Union[None, int, tuple] = None,
        h: Union[None, int, tuple] = None,
        chart: Optional[PlottingObject] = None,
        **style_kwargs,
    ) -> PlottingObject:

**Type Hint Guide:**

- **Union** - Multiple types: ``Union[int, str]``
- **Optional** - Can be None: ``Optional[str]``
- **Literal** - Specific values: ``Literal["sum", "mean"]``

Docstring
~~~~~~~~~

Write comprehensive docstrings following NumPy style:

.. code-block:: python

    """
    Draws the nested density pie chart of the input VastColumns.

    Parameters
    ----------
    columns: SQLColumns
        List of the VastColumns names.
    max_cardinality: int | tuple, optional
        Maximum number of distinct elements for VastColumns 1 and 2 
        to be used as categorical. For these elements, no h is 
        picked or computed. If of type tuple, represents the 
        'max_cardinality' of each column.
    h: int | tuple, optional
        Interval width of the bar. If empty, an optimized h will 
        be computed. If of type tuple, it must represent each 
        column's 'h'.
    chart: PlottingObject, optional
        The chart object to plot on.
    **style_kwargs
        Any optional parameter to pass to the plotting functions.
    
    Returns
    -------
    PlottingObject
        Plotting object with the chart.
    
    Examples
    --------
    .. ipython:: python
    
       from vastorbit.datasets import load_titanic
       data = load_titanic()
       data.pie(['survived', 'pclass'])
    
    See Also
    --------
    bar : Bar chart visualization
    """

.. important:: 

   For complete docstring guidelines, see :ref:`contribution_guidelines.code.auto_doc`

____

🛠️ Essential Functions
-----------------------

Format Column Names
~~~~~~~~~~~~~~~~~~~

Use ``format_colnames()`` to properly format input column names:

.. ipython:: python

    from vastorbit.datasets import load_titanic
    titanic = load_titanic()
    titanic.get_columns()

Get Current Relation
~~~~~~~~~~~~~~~~~~~~

Use ``current_relation()`` to get the VastFrame's SQL relation:

.. ipython:: python
    
    titanic.current_relation()

Execute SQL
~~~~~~~~~~~

Use ``_executeSQL()`` to execute SQL queries:

.. ipython:: python

    from vastorbit._utils._sql._sys import _executeSQL
    _executeSQL(f"SELECT * FROM {titanic._genSQL()} LIMIT 2")

**Fetch Results:**

.. ipython:: python

    _executeSQL(
        f"SELECT * FROM {titanic._genSQL()} LIMIT 2",
        method="fetchall"
    )

**Available Methods:**

- ``fetchall`` - All rows as list
- ``fetchone`` - First row
- ``fetchfirstelem`` - First element of first row

____

📊 Complete Examples
--------------------

Example 1: VastFrame Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a correlation method to VastFrame:

.. code-block:: python

    from vastorbit._utils._sql._sys import _executeSQL
    from vastorbit._config.config import save_vastorbit_logs
    
    @save_vastorbit_logs
    def pearson(self, column1: str, column2: str) -> float:
        """
        Computes the Pearson Correlation Coefficient between two columns.

        Parameters
        ----------
        column1 : str
            First VastColumn name.
        column2 : str
            Second VastColumn name.

        Returns
        -------
        float
            Pearson Correlation Coefficient

        Examples
        --------
        .. ipython:: python
        
           from vastorbit.datasets import load_titanic
           titanic = load_titanic()
           titanic.pearson('age', 'fare')

        See Also
        --------
        corr : Computes the full correlation matrix
        """
        # Format column names
        column1, column2 = self.format_colnames([column1, column2])
        
        # Get current relation
        table = self._genSQL()
        
        # Build SQL query with label
        query = f"""
            SELECT /*+LABEL(VastFrame.pearson)*/ 
                   CORR({column1}, {column2}) 
            FROM {table}
        """
        
        # Execute and return result
        result = _executeSQL(
            query,
            title="Computing Pearson coefficient",
            method="fetchfirstelem"
        )
        
        return result

**Key Steps:**

1. ✅ Add ``@save_vastorbit_logs`` decorator
2. ✅ Include type hints
3. ✅ Write complete docstring
4. ✅ Format column names with ``format_colnames()``
5. ✅ Get relation with ``_genSQL()``
6. ✅ Label SQL queries: ``/*+LABEL(ClassName.method)*/``
7. ✅ Execute with ``_executeSQL()``
8. ✅ Return result

____

Example 2: VastColumn Method
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Add a correlation method to VastColumn:

.. code-block:: python

    from vastorbit._utils._sql._sys import _executeSQL
    from vastorbit._config.config import save_vastorbit_logs
    
    @save_vastorbit_logs
    def pearson(self, column: str) -> float:
        """
        Computes the Pearson Correlation Coefficient with another column.

        Parameters
        ----------
        column : str
            VastColumn name to correlate with.

        Returns
        -------
        float
            Pearson Correlation Coefficient

        Examples
        --------
        .. ipython:: python
        
           from vastorbit.datasets import load_titanic
           titanic = load_titanic()
           titanic['age'].pearson('fare')

        See Also
        --------
        VastFrame.corr : Computes the full correlation matrix
        """
        # Format input column name
        column1 = self.parent.format_colnames([column])[0]
        
        # Get current column name
        column2 = self.alias
        
        # Get parent VastFrame relation
        table = self.parent._genSQL()
        
        # Build SQL query with label
        query = f"""
            SELECT /*+LABEL(VastColumn.pearson)*/ 
                   CORR({column1}, {column2}) 
            FROM {table}
        """
        
        # Execute and return result
        result = _executeSQL(
            query,
            title="Computing Pearson coefficient",
            method="fetchfirstelem"
        )
        
        return result

**VastColumn Specifics:**

- ✅ Access parent VastFrame: ``self.parent``
- ✅ Get column name: ``self.alias``
- ✅ Format using parent: ``self.parent.format_colnames()``

____

🎯 Best Practices
-----------------

**Code Quality:**

- ✅ Always add type hints
- ✅ Use ``@save_vastorbit_logs`` decorator
- ✅ Label SQL queries for tracking
- ✅ Format column names properly
- ✅ Handle errors gracefully
- ✅ Write comprehensive docstrings
- ✅ Add usage examples
- ✅ Include "See Also" references

**SQL Queries:**

.. code-block:: python

    # Good - With label
    query = f"SELECT /*+LABEL(VastFrame.method)*/ column FROM {table}"
    
    # Bad - No label
    query = f"SELECT column FROM {table}"

**Error Handling:**

.. code-block:: python

    def safe_method(self, column: str) -> float:
        """Method with error handling."""
        try:
            column = self.format_colnames([column])[0]
            # ... execution code
            return result
        except Exception as e:
            raise ValueError(f"Error in method: {e}")

____

📝 Decorator Reference
----------------------

``@save_vastorbit_logs``
~~~~~~~~~~~~~~~~~~~~~~~~~

Saves method usage statistics to ``QUERY_PROFILES`` table in VAST DataBase.

**Tracks:**

- Method name and parameters
- Execution time
- User information
- Query patterns

**Usage:**

.. code-block:: python

    @save_vastorbit_logs
    def your_method(self, param: str) -> Any:
        """Your method description."""
        # Implementation
        pass

____

🧪 Testing Your Function
-------------------------

**Quick Test:**

.. code-block:: python

    # Create test file
    from vastorbit.datasets import load_titanic
    
    # Test VastFrame method
    titanic = load_titanic()
    result = titanic.pearson('age', 'fare')
    print(f"Correlation: {result}")
    
    # Test VastColumn method
    result = titanic['age'].pearson('fare')
    print(f"Correlation: {result}")

**Verify:**

1. ✅ Function executes without errors
2. ✅ Returns expected type
3. ✅ Handles edge cases
4. ✅ Documentation renders correctly
5. ✅ Examples run successfully

____

.. tip::

   **Development Workflow:**
   
   1. Choose appropriate module file
   2. Write function with type hints
   3. Add ``@save_vastorbit_logs`` decorator
   4. Write comprehensive docstring
   5. Test locally
   6. Render documentation (see :ref:`contribution_guidelines.code.auto_doc.render`)
   7. Submit PR

.. seealso::

   - :ref:`contribution_guidelines.code.auto_doc` - Documentation guide
   - :ref:`contribution_guidelines.code.unit_tests` - Testing guide
   - :ref:`api.vastframe` - VastFrame API reference
   - :ref:`api.vastcolumn` - VastColumn API reference (if exists)