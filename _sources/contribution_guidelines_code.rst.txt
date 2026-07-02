.. _contribution_guidelines.code:

=====================
Code Contribution
=====================

.. include:: logo_include.rst

Complete guide for contributing code to VAST Orbit.

____

Developer Guide
------------------

Follow these guides in order for your first contribution:

.. grid:: 1 2 2 2
    :gutter: 3

    .. grid-item::
    
      .. card:: |i-setup| 1. Setting Up
        :link: contribution_guidelines.code.setting_up
        :link-type: ref
        :text-align: center
        :class-card: custom-card
        
        Fork, clone, and configure your development environment.
        
        +++
        
        Start Here →

    .. grid-item::
    
      .. card:: |i-tests| 2. Unit Tests
        :link: contribution_guidelines.code.unit_tests
        :link-type: ref
        :text-align: center
        :class-card: custom-card
        
        Write and run tests with pytest. Required for all PRs.
        
        +++
        
        Learn Testing →

    .. grid-item::
    
      .. card:: |i-functions| 3. Useful Functions
        :link: contribution_guidelines.code.useful_functions
        :link-type: ref
        :text-align: center
        :class-card: custom-card
        
        Helper utilities and common patterns in the codebase.
        
        +++
        
        View Utilities →

    .. grid-item::
    
      .. card:: |i-practices| 4. Best Practices
        :link: contribution_guidelines.code.misc
        :link-type: ref
        :text-align: center
        :class-card: custom-card
        
        Coding standards, style guide, and conventions.
        
        +++
        
        Read Guidelines →

    .. grid-item::
    
      .. card:: |i-docs| 5. Documentation
        :link: contribution_guidelines.code.auto_doc
        :link-type: ref
        :text-align: center
        :class-card: custom-card
        
        Auto-generate API docs with Sphinx and docstrings.
        
        +++
        
        Document Code →

    .. grid-item::
    
      .. card:: |i-examples| 6. Examples
        :link: contribution_guidelines.code.example
        :link-type: ref
        :text-align: center
        :class-card: custom-card
        
        Real contribution examples and step-by-step walkthroughs.
        
        +++
        
        See Examples →

____

Quick Start
--------------

**Ready to contribute? Follow these steps:**

.. code-block:: bash

  # 1. Fork and clone
  git clone https://github.com/vast-data/VAST-Orbit.git
  cd vastorbit

  # 2. Create branch
  git checkout -b feature/your-feature-name

  # 3. Install dev dependencies
  pip install -e ".[dev]"

  # 4. Make changes and test
  pytest tests/

  # 5. Format and lint
  black .
  pylint vastorbit

  # 6. Commit and push
  git commit -m "Add: Your feature description"
  git push origin feature/your-feature-name

  # 7. Open Pull Request on GitHub

____

Checklist Before PR
-----------------------

Before submitting your pull request:

- [ ] Code follows style guidelines (Black formatting)
- [ ] All tests pass locally (`pytest`)
- [ ] New tests added for new features
- [ ] Code coverage maintained (>80%)
- [ ] Docstrings added/updated
- [ ] Documentation updated (if needed)
- [ ] No pylint warnings
- [ ] Commit messages are clear
- [ ] PR description references issue

____

Detailed Guides
------------------

.. toctree::
   :maxdepth: 1
   
   contribution_guidelines_code_setting_up
   contribution_guidelines_code_unit_tests
   contribution_guidelines_code_useful_functions
   contribution_guidelines_code_misc
   contribution_guidelines_code_auto_doc
   contribution_guidelines_code_example

____

.. tip::

   **First time contributor?** Start with issues labeled `good-first-issue` on GitHub. Join us on Slack (`vastsupport.slack.com <https://vastsupport.slack.com>`__) if you need help!

.. seealso::

   - :ref:`cicd` - Automated quality checks
   - :ref:`contribution_guidelines` - General contribution guidelines