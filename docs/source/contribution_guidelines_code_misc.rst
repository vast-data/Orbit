.. _contribution_guidelines.code.misc:

===============
Miscellaneous
===============

.. include:: logo_include.rst

Code formatting and licensing requirements.

____

Code Formatting (PEP 8)
------------------------

Once you are satisfied with your code, please run `black <https://black.readthedocs.io/en/stable/>`_ for your code. Black will automatically format all your code to make it professional and consistent with PEP 8.

Next please run `pylint <https://pypi.org/project/pylint/>`_ and ensure that your score is above the minimum threshold of 5. Pylint will automatically provide you with the improvement opportunities that you can adjust to increase your score.

As per the updated CI/CD, no code will be accepted that requires formatting using black or has a lower pylint score than the threshold stated above.

____

License Headers
---------------

Every file in this project must use the following Apache 2.0 header:

.. code-block:: python

    """
    SPDX-License-Identifier: Apache-2.0
    """
