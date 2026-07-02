.. _cicd:

===================
CI/CD Pipeline
===================

.. include:: logo_include.rst

Automated quality assurance and deployment for VAST Orbit.

____

Overview
--------

VAST Orbit uses a comprehensive CI/CD pipeline to ensure code quality, consistency, and reliability. Every code change goes through automated checks before merging.

.. image:: /_static/cicd_pipeline.svg
   :width: 100%
   :align: center
   :alt: VAST Orbit CI/CD pipeline: formatting, quality analysis, unit testing, coverage, documentation

____

Pipeline Stages
---------------

**1. Code Formatting**
~~~~~~~~~~~~~~~~~~~~~~~~~~

**Tool:** Black

Enforces consistent code style across the entire codebase.

.. grid:: 2

   .. grid-item::
      
      **What it does:**
      
      - Automatically formats Python code
      - Ensures consistent style
      - Removes style debates from code reviews

   .. grid-item::
      
      **Why it matters:**
      
      - Improves readability
      - Reduces cognitive load
      - Maintains professional appearance

:ref:`Learn more → <cicd.black>`

____

**2. Code Quality Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Tool:** Pylint

Static code analysis to identify potential issues and enforce standards.

.. grid:: 2

   .. grid-item::
      
      **What it checks:**
      
      - Code complexity
      - Naming conventions
      - Potential bugs
      - Best practices

   .. grid-item::
      
      **Benefits:**
      
      - Catches issues early
      - Enforces standards
      - Improves maintainability

:ref:`Learn more → <cicd.pylint>`

____

**3. Unit Testing**
~~~~~~~~~~~~~~~~~~~~~~~

**Tool:** Pytest

Comprehensive test suite across multiple Python environments.

.. grid:: 2

   .. grid-item::
      
      **Test coverage:**
      
      - Python 3.12+
      - Linux and macOS
      - Multiple database configurations
      - Edge cases and regression tests

   .. grid-item::
      
      **Ensures:**
      
      - No regressions
      - Feature stability
      - Cross-platform compatibility

:ref:`Learn more → <cicd.unittest>`

____

**4. Coverage Analysis**
~~~~~~~~~~~~~~~~~~~~~~~~~~~~

**Tool:** Codecov

Tracks test coverage to ensure comprehensive testing.

.. grid:: 2

   .. grid-item::
      
      **Metrics tracked:**
      
      - Line coverage
      - Branch coverage
      - Function coverage
      - File-by-file breakdown

   .. grid-item::
      
      **Target:**
      
      - Minimum 80% coverage
      - 100% on critical paths
      - No coverage regressions

:ref:`Learn more → <cicd.codecov>`

____

**5. Documentation**
~~~~~~~~~~~~~~~~~~~~~~~~

**Tool:** Sphinx

Automatically builds and deploys documentation on every merge.

.. grid:: 2

   .. grid-item::
      
      **Auto-generated:**
      
      - API documentation
      - Code examples
      - Release notes
      - Version history

   .. grid-item::
      
      **Always current:**
      
      - Synced with code
      - Updated on every merge
      - Published automatically

:ref:`Learn more → <cicd.sphinx>`

____

Benefits
--------

|check| **Fast Feedback**
   Issues caught in minutes, not days

|check| **Consistent Quality**
   Every PR meets the same standards

|check| **Reduced Errors**
   Automated checks catch common mistakes

|check| **Better Collaboration**
   Clear expectations for all contributors

|check| **Confidence**
   Every merge maintains stability

____

For Contributors
----------------

**Before Submitting a PR:**

1. Run formatters locally: ``black .``
2. Check code quality: ``pylint vastorbit``
3. Run tests: ``pytest``
4. Verify coverage: ``pytest --cov``

**What to Expect:**

- All checks must pass before merge
- Failed checks include detailed error messages
- Documentation updates automatically
- Feedback typically within 10 minutes

.. tip::

   Set up pre-commit hooks to run checks automatically before each commit. See our `contributing guide <https://github.com/vast-data/Orbit/blob/main/CONTRIBUTING.md>`__ for setup instructions.

____

Pipeline Status
---------------

.. image:: https://github.com/vast-data/Orbit/workflows/CI/badge.svg
   :target: https://github.com/vast-data/Orbit/actions
   :alt: CI Status

.. image:: https://codecov.io/gh/vast-data/vastorbit/branch/main/graph/badge.svg
   :target: https://codecov.io/gh/vast-data/vastorbit
   :alt: Code Coverage

____

Detailed Documentation
----------------------

.. toctree::
   :maxdepth: 1
   
   cicd_black
   cicd_pylint
   cicd_unittest
   cicd_codecov
   cicd_sphinx