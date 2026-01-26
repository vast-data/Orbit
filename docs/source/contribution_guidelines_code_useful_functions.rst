.. _contribution_guidelines.code.useful_functions:

=================
Useful Functions
=================

.. include:: logo_include.rst

This section is an overview of some useful functions. You can use these to implement new features.

____

Get Columns
===========

To check if a list of columns belongs to the VastFrame:

.. code-block:: python

    # import
    from vastorbit import VastFrame
    
    # Function
    VastFrame.get_columns():
        """
        Returns the TableSample columns.
        
        Returns
        -------
        list
            columns.
        """

**Example:** If VastFrame 'vdf' has two columns named respectively 'A' and 'B', ``VastFrame.get_columns()`` will return a list: ``["A","B"]``.

____

Format Column Names
===================

To format a list using the columns of the VastFrame:

.. code-block:: python
        
    # import
    from vastorbit import VastFrame
    
    # Function
    VastFrame.format_colnames(self, columns: Union[str, list]):
        """
        ---------------------------------------------------------------------------
        Method used to format a list of columns with the column names of the 
        VastFrame.
        
        Parameters
        ----------
        columns: list/str
            List of column names to format.
        
        Returns
        -------
        list
            Formatted column names.
        """

**Example:** If VastFrame 'vdf' has two columns named respectively 'CoLuMn A' and 'CoLumnB', ``VastFrame.format_colnames(['column a', 'columnb']) == ['CoLuMn A', 'CoLumnB']``.

____

Quote Identifiers
=================

Identifiers in a SQL query must be formatted a certain way. You can use the following function to get a properly formatted identifier:

.. code-block:: python
        
    # import 
    from vastorbit import quote_ident
    
    # Function
    def quote_ident(column: str):
        """
        ---------------------------------------------------------------------------
        Returns the specified string argument in the required format to use it as 
        an identifier in a SQL query.
        
        Parameters
        ----------
        column: str
            Column name.
        
        Returns
        -------
        str
            Formatted column name.
        """

**Example:** ``quote_ident('my column name') == '"my column name"'``

____

Logo Functions
==============

The two following functions will generate the vastorbit logo as a string or as an HTML object.

.. code-block:: python
        
    # import
    from vastorbit._utils._logo import vastorbit_logo_html 
    from vastorbit._utils._logo import vastorbit_logo_str
    
    # Functions
    def vastorbit_logo_html()  # vastorbit HTML Logo
    def vastorbit_logo_str()   # vastorbit Python STR Logo