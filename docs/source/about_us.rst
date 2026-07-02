.. _about_us:

========
About Us
========

.. include:: logo_include.rst

VAST Orbit is built by a small team at VAST who believe data science should happen
where the data already lives — and that the right tools should make that feel
effortless.

The story behind VAST Orbit
---------------------------

.. tab-set::

    .. tab-item:: The vision

        .. image:: _static/website/about_us/cover/vision.png
            :class: about-cover
            :alt: The vision behind VAST Orbit

        .. raw:: html

            <span class="tab-lead">Data kept growing. The tools didn't keep up.</span>

        For years the tools of data science forced a trade-off. Python and pandas are
        fast and flexible but bound by memory; Spark scales but is heavy and slow to
        iterate on; SQL is powerful but never quite fits the way a data scientist
        thinks. Meanwhile the data spread across databases, lakes, and files, and
        reaching all of it meant building yet another pipeline.

        The VAST Data Platform removed the usual reason for all that movement by
        unifying transactional and analytical processing, all-flash performance at
        data-lake economics, and linear scale from gigabytes to exabytes. What was
        still missing was a way for data scientists to use that power with the Python
        they already knew. VAST Orbit exists to close exactly that gap.

    .. tab-item:: The philosophy

        .. image:: _static/website/about_us/cover/the_philosophy.png
            :class: about-cover
            :alt: The philosophy of in-database computing

        .. raw:: html

            <span class="tab-lead">Bring the tools to the data, not the data to the tools.</span>

        Everything in VAST Orbit follows from one principle: computation should happen
        where the data lives. Operations execute inside VAST, data stays put, and only
        results travel back to Python — so a petabyte dataset feels like a megabyte
        one, and nothing sensitive leaks out along the way.

        Just as important, the experience stays familiar. You work with patterns you
        already know from pandas and scikit-learn, the heavy lifting happens in the
        database, and the same code you wrote in a notebook is the code that runs in
        production. VAST Orbit doesn't move data to your tools; it brings your tools to
        the data.

    .. tab-item:: Technical foundation

        .. image:: _static/website/about_us/cover/technical_foundation.png
            :class: about-cover
            :alt: The technical foundation of VAST Orbit

        .. raw:: html

            <span class="tab-lead">Proven analytics, re-engineered for the VAST query engine.</span>

        Under the hood, VAST Orbit translates everyday Python into operations that run
        in the database: data preparation, statistical profiling, hundreds of analytic
        and SQL functions, multi-source joins across every catalog, and machine-learning
        inference — all executed in VAST rather than in Python.

        Rather than reinvent that analytics surface from scratch, VAST Orbit builds on years of proven, open-source engineering, re-engineered for the VAST DataBase. That heritage is why the library arrived broad and battle-tested, and why so much of it works the moment you connect.

The team
--------

.. grid:: 2 2 3 3

    .. grid-item::

        .. card:: Badr Ouali
          :img-top: _static/website/about_us/team/member1.jpg
          :link: https://www.linkedin.com/in/badr-ouali/
          :text-align: center
          :class-card: member-pics-card

          DB Solutions Engineer

    .. grid-item::

        .. card:: Fouad Teban
          :img-top: _static/website/about_us/team/member2.jpg
          :link: https://www.linkedin.com/in/fouadteban/
          :text-align: center
          :class-card: member-pics-card

          Field Engineering Lead

    .. grid-item::

        .. card:: Christian Neundorf
          :img-top: _static/website/about_us/team/member3.jpg
          :link: https://www.linkedin.com/in/christian-neundorf-552a6721/
          :text-align: center
          :class-card: member-pics-card

          Senior Systems Engineer

    .. grid-item::

        .. card:: Chris Snow
          :img-top: _static/website/about_us/team/member4.jpg
          :link: https://www.linkedin.com/in/csnowuk/
          :text-align: center
          :class-card: member-pics-card

          Product Manager

    .. grid-item::

        .. card:: Kiran Kumar
          :img-top: _static/website/about_us/team/member5.jpg
          :link: https://www.linkedin.com/in/kiranmavatoor/
          :text-align: center
          :class-card: member-pics-card

          Principal Systems Engineer

    .. grid-item::

        .. card:: Kuldeep Venati
          :img-top: _static/website/about_us/team/member6.jpg
          :link: https://www.linkedin.com/in/venati/
          :text-align: center
          :class-card: member-pics-card

          Principal Data Platform SE

Get involved
------------

VAST Orbit is young and moving quickly, which is the best time to help shape it.
Whether you want to ask a question, report something broken, or contribute code,
here is where to start.

Join the conversation
~~~~~~~~~~~~~~~~~~~~~~~

The fastest way to get help or share what you are building is the VAST Slack. If you
are stuck connecting to a cluster, unsure how to express an operation, or just
curious what others are doing with VAST Orbit, ask there — the team reads it. Join us
at `vastsupport.slack.com <https://vastsupport.slack.com>`__.

Report an issue
~~~~~~~~~~~~~~~

Found a bug or hit a query that should work but doesn't? Open an issue on GitHub with
a small reproduction and it helps us fix it quickly. File issues at
`github.com/vast-data/vastorbit/issues <https://github.com/vast-data/Orbit/issues>`__.

Improve the documentation
~~~~~~~~~~~~~~~~~~~~~~~~~~~

Contributions are not only about code. If something here was unclear, a missing
example would have saved you time, or you spotted a mistake, a documentation pull
request is one of the most valuable things you can send — it helps the next person
who arrives with the same question.

Open a pull request
~~~~~~~~~~~~~~~~~~~~~

Want to add a function, fix behavior, or extend a model? We welcome it. Have a look
at the :ref:`contribution_guidelines` to see how the project is organized and how to
get a change reviewed and merged.

Open source, maintained by VAST
-------------------------------

VAST Orbit is open source and is developed and maintained by VAST Data. It is not a
separately supported product and carries no enterprise SLA — but it is actively
maintained, and the quickest ways to get help are the community Slack and the issue
tracker above.

.. note::

    VAST Orbit brings Python data science to the VAST Data Platform: prepare,
    explore, analyze, and build AI — all with in-database execution at any scale.