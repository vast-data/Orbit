.. _index:

.. raw:: html

   <div class="vob-hero">
     <div class="vob-hero__bg" style="background-image:url('_static/website/about_us/cover/the_vision.png')"></div>
     <div class="vob-hero__inner">

.. include:: logo_include.rst

.. raw:: html

       <p class="vob-hero__tagline">The Python library for data science and AI that runs where your data lives.</p>

.. container:: vob-hero-cta

   .. button-ref:: getting_started
       :ref-type: ref
       :color: primary

       Get started

   .. button-ref:: connection
       :ref-type: ref
       :color: secondary

       Connect to VAST

   .. button-ref:: api
       :ref-type: ref
       :color: secondary

       Browse the API

.. raw:: html

     </div>
   </div>

==============================
In-database data science & AI
==============================

VAST Orbit lets data scientists, analysts, and ML engineers run a complete
workflow — preparing, exploring, analyzing, and modeling data — directly inside
the VAST Data Platform, using the pandas- and scikit-learn-style API they already
know. Instead of copying data out to a notebook, VAST Orbit pushes the work down to
where the data sits and brings only the answers back, so the same code runs on a
kilobyte or a petabyte, against a table or a Parquet file, without a rewrite.

.. raw:: html

   <div class="vob-video">
     <video controls preload="none"
            poster="_static/website/video/vastorbit_intro_poster.png">
       <source src="_static/website/video/vastorbit_trailer_med.mp4"  type="video/mp4">
     </video>
   </div>

What VAST Orbit brings to your business
---------------------------------------

Most data science works backwards: the data is huge and stays put, while the tools
are small and insist everything be copied to them. VAST Orbit removes the copy —
preparation, analytics, and scoring all run inside VAST — and that single change pays
off differently for everyone who touches the data.

.. tab-set::

    .. tab-item:: For data scientists

        .. image:: _static/website/about_us/cover/data_scientist_dashboard.png
            :class: about-cover
            :alt: Familiar Python, at any scale

        .. raw:: html

            <span class="tab-lead">Your tools and your syntax, at any scale.</span>

        Keep the pandas and scikit-learn habits you already have. ``VastFrame`` behaves
        like a DataFrame and the models follow the scikit-learn API, so the notebook you
        write against a sample becomes production code against the full table — no
        rewrite, no new language, and no waiting on an export before you can think.

        Because the work runs in VAST, the size of the data stops being your problem:
        the same few lines hold whether you are working through a megabyte or a petabyte.

    .. tab-item:: For platform & data teams

        .. image:: _static/website/about_us/cover/platform.png
            :class: about-cover
            :alt: One governed surface

        .. raw:: html

            <span class="tab-lead">One governed surface instead of pipeline sprawl.</span>

        Since the work executes where the data lives, there are no extracts to copy and
        no side pipelines to babysit. Sensitive data stays inside VAST under one set of
        controls, lineage stays intact, and the platform you already run becomes the
        single place analysts, models, and agents all work.

        That means far less to secure, move, and reconcile — and far fewer moving parts
        between a question and its answer.

    .. tab-item:: For the business

        .. image:: _static/website/about_us/cover/data_scientist_business.png
            :class: about-cover
            :alt: Answers sooner, for less

        .. raw:: html

            <span class="tab-lead">Answers sooner, on more of your data, for less.</span>

        Every copy is time lost, compute and storage paid for twice, and another place
        data can leak. Removing it means questions are answered sooner, against more of
        the estate at once, at a fraction of the infrastructure cost.

        A central data strategy stops being an architecture diagram and becomes
        something teams use day to day — on a single table or every asset across the
        business.

Key features
------------

.. grid:: 1 2 3 3
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item-card:: |i-indb| No data movement
        :text-align: center

        Preparation, analytics, and scoring execute inside VAST. Your data never
        leaves the platform, so work stays fast, governed, and secure.

    .. grid-item-card:: |i-frame| Python you already know
        :text-align: center

        ``VastFrame`` behaves like a pandas DataFrame and the models follow the
        scikit-learn API, so notebook code becomes production code unchanged.

    .. grid-item-card:: |i-multisource| One query, every source
        :text-align: center

        One federated query joins VAST tables, data-lake files, and external
        databases — with no ETL pipeline to build first.

    .. grid-item-card:: |i-scale| Scale without rewrites
        :text-align: center

        VAST's flash-native, disaggregated architecture keeps queries interactive
        from gigabytes to exabytes, so workflows grow with your data.

    .. grid-item-card:: |i-inml| Machine learning in place
        :text-align: center

        Train on intelligently sampled data, then deploy the model for in-database
        inference that scores billions of rows where they live.

    .. grid-item-card:: |i-magic| Ready for AI agents
        :text-align: center

        A built-in MCP server and the ``%%ai`` and ``%%sql`` notebook magics let
        assistants and LLMs query and reason over your VAST data directly.

What you can do with it
-----------------------

.. tab-set::

    .. tab-item:: Prepare & explore

        .. image:: _static/website/about_us/cover/indb_dashboard.png
            :class: about-cover
            :alt: Prepare and explore data in VAST

        .. raw:: html

            <span class="tab-lead">Clean, shape, and understand data at any scale.</span>

        Cleaning and shaping data is usually the slowest part of a project, and it
        only gets slower as the data grows. With VAST Orbit you handle missing values,
        remove duplicates, normalize, encode, and engineer features using familiar
        calls that execute inside VAST — so a petabyte table feels like a megabyte one
        and nothing is pulled into Python first.

        When it is time to look before you leap, charts and statistical summaries are
        generated from intelligent samples, letting you profile distributions,
        correlations, and outliers across billions of rows in seconds rather than
        waiting on an export.

    .. tab-item:: Analyze across sources

        .. image:: _static/website/about_us/cover/different_sources.png
            :class: about-cover
            :alt: Analyze across every source

        .. raw:: html

            <span class="tab-lead">Join everything, in one query, close to the data.</span>

        Real questions rarely live in a single table. Because VAST Orbit reaches your
        data through one federated query engine, one piece of Python can join a VAST
        table with Parquet files in the data lake and a customer record in PostgreSQL — all
        in the same query and all executed next to the data.

        That turns the idea of a central data layer from an architecture diagram into
        something an analyst can use day to day: ad-hoc analysis across the whole
        estate, with no ETL job to schedule and no warehouse to load first.

    .. tab-item:: Machine learning

        .. image:: _static/website/about_us/cover/healthcare.png
            :class: about-cover
            :alt: Machine learning in the database

        .. raw:: html

            <span class="tab-lead">Train flexibly, then score billions of rows in place.</span>

        VAST Orbit supports a hybrid workflow that matches how teams really work:
        train quickly with the embedded algorithms or bring a scikit-learn model you
        trained locally, then deploy it for inference that runs as SQL inside VAST.

        Scoring happens where the data is, so you can refresh predictions on live data
        continuously — fraud scores, churn risk, demand forecasts — instead of
        shuttling features and results between systems and serving infrastructure.

    .. tab-item:: AI platform

        .. image:: _static/website/about_us/cover/ai_development_platform.png
            :class: about-cover
            :alt: An AI development platform on VAST

        .. raw:: html

            <span class="tab-lead">Make your data a first-class tool for AI.</span>

        Modern AI is only as good as its access to context. VAST Orbit exposes your
        data and its own analytics as tools an LLM can call through an MCP server, and
        the ``%%ai`` magic lets you ask a question in plain language and get back a
        working, schema-aware query.

        The result is a single governed platform where analysts, models, and agents
        all operate on the same data, with no copies in between — the foundation for
        AI applications you can actually trust in production.

Use cases
---------

The same library powers very different problems, because they all come down to
running analytics and models close to large, fast-moving data.

.. grid:: 1 2 3 3
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item-card:: |i-fraud| Fraud detection
        :text-align: center

        Score every transaction against historical patterns in place and catch fraud
        in real time — without exporting sensitive financial data.

    .. grid-item-card:: |i-churn| Customer 360 & churn
        :text-align: center

        Combine CRM, billing, and clickstream into one view and predict churn where
        the data already sits, then refresh scores continuously.

    .. grid-item-card:: |i-telecom| Telecom & networks
        :text-align: center

        Optimize coverage and capacity over billions of call-detail records, joining
        live traffic with historical patterns in a single query.

    .. grid-item-card:: |i-energy| IoT & asset health
        :text-align: center

        Monitor sensor streams and forecast failures across live and historical
        readings together, scoring devices where their data lands.

    .. grid-item-card:: |i-insurance| Risk & insurance
        :text-align: center

        Price risk and flag anomalies across policy, claims, and external data sets at
        once, with full lineage and no data leaving the platform.

    .. grid-item-card:: |i-bio| Life sciences
        :text-align: center

        Explore genomic and clinical data at petabyte scale with familiar Python,
        keeping regulated data governed inside VAST throughout.

A quick look
------------

Connect once, then prepare, join, visualize, and model — every step executing in
VAST:

.. code-block:: python

    import vastorbit as vo

    # Connect to VAST
    vo.new_connection({
        "host": "vast-cluster.example.com",
        "port": 8080,
        "catalog": "vast_catalog",
        "schema": "analytics",
    })

    # A VastFrame is a handle to data in VAST — nothing is pulled into Python
    customers = vo.VastFrame("vast_catalog.crm.customers")

    # Prepare the data, in place
    customers = customers.fillna({"income": 0, "age": customers["age"].avg()})
    customers["income_norm"] = customers.normalize("income")

    # Explore with intelligent sampling
    customers["age"].hist(nbins=20)

    # Join a VAST table with data-lake files — one query, executed in VAST
    transactions = vo.VastFrame("hive.default.transactions")
    enriched = customers.join(transactions, on="customer_id", how="inner")

    # Train a model, then score billions of rows in the database
    from vastorbit.machine_learning.vast import RandomForestClassifier

    model = RandomForestClassifier(n_estimators = 4)
    model.fit(enriched, ["age", "tenure"], "churn")
    predictions = model.predict(enriched)   # runs inside VAST

Built on the VAST Data Platform
-------------------------------

VAST Orbit is only as capable as the foundation beneath it. The VAST Data Platform
unifies storage, database, and compute into one consistent system, so every asset —
transactional tables, data-lake files, streaming events, and vector embeddings —
lives in one place and speaks one language. When the infrastructure is that
consistent, everything becomes possible: there is no copy step to slow you down, no
second system to reconcile, and no scale ceiling to design around.

VAST Orbit turns that consistency into a single queryable surface for Python, where
one ``VastFrame`` reaches a table or a file, a gigabyte or an exabyte, all the same
way. It works with **VAST 4.5 and later**. Learn more about the foundation it builds
on at the `VAST Data Platform <https://www.vastdata.com/platform/database>`__.

Today that single query runs on Trino; VAST's own query engine is on the way and will
become the default. Because you work through one ``VastFrame`` API, your code stays
exactly the same when the engine underneath it changes.

Installation
------------

Install the beta with pip:

.. code-block:: bash

    pip install vastorbit

VAST Orbit needs **Python 3.12+**, network access to your VAST cluster, and
**VAST 4.5 or later**. Version 0.1.x is a beta; a production-ready 1.0.0 is on the
way. See :ref:`getting_started` for full setup and :ref:`connection` for connection
and authentication options.

.. note::

    Placeholders such as ``vast-cluster.example.com`` and ``vast_catalog`` stand in
    for your own cluster host and catalog names throughout the docs.

Explore the documentation
--------------------------

.. grid:: 2 2 2 2
    :gutter: 3
    :class-container: feature-tiles

    .. grid-item-card:: |i-start| Getting Started
        :link: getting_started
        :link-type: ref
        :text-align: center

        Install VAST Orbit and run your first in-database query in minutes.

    .. grid-item-card:: |i-connect| Connection Guide
        :link: connection
        :link-type: ref
        :text-align: center

        Connect to VAST, authenticate, and reach every catalog.

    .. grid-item-card:: |i-guide| User Guide
        :link: user_guide
        :link-type: ref
        :text-align: center

        Master ``VastFrame`` and the in-database operations behind it.

    .. grid-item-card:: |i-ml| Machine Learning
        :link: api.machine_learning
        :link-type: ref
        :text-align: center

        Train models and deploy them for inference at production scale.

    .. grid-item-card:: |i-charts| Chart Gallery
        :link: chart_gallery
        :link-type: ref
        :text-align: center

        See the visualizations VAST Orbit can build from sampled data.

    .. grid-item-card:: |i-stats| Statistics
        :link: statistics
        :link-type: ref
        :text-align: center

        The library by the numbers — measured live from the source.

    .. grid-item-card:: |i-examples| Examples
        :link: examples
        :link-type: ref
        :text-align: center

        Follow end-to-end tutorials across analytics and ML workflows.

    .. grid-item-card:: |i-about| About Us
        :link: about_us
        :link-type: ref
        :text-align: center

        Meet the people behind VAST Orbit and the story that shaped it.

.. note::

    VAST Orbit brings Python data science to the VAST Data Platform — query
    anywhere, analyze everything, and build AI at any scale, all with in-database
    execution and zero data movement.

.. toctree::
    :hidden:
    :maxdepth: 1
    :titlesonly:

    getting_started
    connection
    whats_new
    contribution_guidelines
    examples
    api
    chart_gallery
    user_guide
    statistics
    about_us