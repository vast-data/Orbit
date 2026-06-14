# Configuration file for the Sphinx documentation builder.
#
# For the full list of built-in configuration values, see the documentation:
# https://www.sphinx-doc.org/en/master/usage/configuration.html

# -- Project information -----------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#project-information

# Created by: Badr Ouali

# Loading vastorbit by default
# # All RST files will have the following at the top:
rst_prolog = """
.. ipython:: python
    :suppress:

    import vastorbit
    vastorbit.set_option("plotting_lib","matplotlib") 

.. raw:: html

    <div class="loader-container" id="loaderContainer">
    <img src="_static/loader.gif" alt="Loading..." class="gif-loader">
    </div>
    <div id="content" style="display:none;">
    <!-- Your page content goes here -->
    </div>

    <script>
    window.addEventListener("load", function() {
        var loader = document.getElementById("loaderContainer");
        var content = document.getElementById("content");

        // Hide the loader and show the content after the page has loaded
        loader.style.display = "none";
        content.style.display = "block";
    });
    </script>

    <script>
    var previousOption = document.getElementById("filter-select").value;

    function switchVersion(selectedVersion) {
        var currentURL = window.location.href;
        
        var newURL = currentURL.replace(previousOption, selectedVersion);
        
        window.location.href = newURL;
        
        // Update the previousOption with the new selected version
        previousOption = selectedVersion;
    }
    </script>
    <div id="main">
    </div>
    <script src="https://code.jquery.com/jquery-3.6.0.min.js"></script>

    <script>
    function openNav() {
    document.getElementById("mySidebar").style.width = "250px";
    document.getElementById("main").style.marginLeft = "250px";
    }

    function closeNav() {
    document.getElementById("mySidebar").style.width = "0";
    document.getElementById("main").style.marginLeft= "0";
    }
    </script>

    <script type='text/javascript'>
        (function ($) {
            // Enable/disable submit button
            $('#choice_50_1_0, #choice_50_1_1').on('change', function () {
                $('#feedback-form .gform_button').prop('disabled', !$(this).val());
            });

            // Show/hide additional comments
            $('#choice_50_2_0, #choice_50_2_1').on('change', function () {
                if ($(this).val() === 'yes') {
                    $('#field_50_3').slideDown('fast');
                } else {
                    $('#field_50_3').slideUp('fast');
                }
            });

            $('#gform_50').on('submit', function(e) {
                e.preventDefault();
                var $form = $(this);

                $form.css({
                    'opacity': .5,
                    'cursor': 'progress',
                });

                $.ajax({
                    type: "post",
                    dataType: "json",
                    url: 'https://www.VAST.com/wp-admin/admin-ajax.php',
                    data: {
                        action: 'python_feedback',
                        formData: $(this).serializeArray(),
                    },
                    success: function (response) {
                        if (response.is_valid) {
                            $form.html(response.confirmation_message);
                        } else {
                            console.log('something went wrong');
                        }

                        console.log( response );
                        $form.css({
                            'opacity': 1,
                            'cursor': 'default',
                        });
                    }
                });
            });
        })(jQuery);
    </script>
    
    
"""


# --- VAST icon substitutions (CSS-mask icons, _static/icons/) ---------------
# Usage in any .rst:  |check| **In-Database Execution**
rst_prolog += """

.. |check| raw:: html

   <span class="vi vi-check vi-cyan" role="img" aria-label="yes"></span>

.. |cross| raw:: html

   <span class="vi vi-cross vi-red" role="img" aria-label="bad"></span>

.. |zap| raw:: html

   <span class="vi vi-zap vi-cyan" role="img" aria-label="fast"></span>

.. |database| raw:: html

   <span class="vi vi-database vi-cyan" role="img" aria-label="database"></span>

.. |globe| raw:: html

   <span class="vi vi-globe vi-cyan" role="img" aria-label="federated"></span>

.. |export| raw:: html

   <span class="vi vi-export vi-cyan" role="img" aria-label="export"></span>

.. |chart| raw:: html

   <span class="vi vi-chart vi-cyan" role="img" aria-label="chart"></span>

.. |arrow| raw:: html

   <span class="vi vi-arrow vi-cyan" role="img" aria-label="arrow"></span>

.. |info| raw:: html

   <span class="vi vi-info vi-cyan" role="img" aria-label="info"></span>

.. |warn| raw:: html

   <span class="vi vi-warning vi-amber" role="img" aria-label="warning"></span>

.. |orbit| raw:: html

   <span class="vi vi-orbit vi-cyan" role="img" aria-label="VastOrbit"></span>
"""


# --- Official VAST icon-font substitutions (used in index.rst & cards) ------
rst_prolog += """

.. |i-start| raw:: html

   <i class="vast vast-vastronaut" role="img" aria-label="getting started"></i>

.. |i-connect| raw:: html

   <i class="vast vast-networking" role="img" aria-label="connection"></i>

.. |i-guide| raw:: html

   <i class="vast vast-configuration-guide" role="img" aria-label="user guide"></i>

.. |i-ml| raw:: html

   <i class="vast vast-machine-learning" role="img" aria-label="machine learning"></i>

.. |i-inml| raw:: html

   <i class="vast vast-brain" role="img" aria-label="in-database ML"></i>

.. |i-charts| raw:: html

   <i class="vast vast-data-analytics" role="img" aria-label="chart gallery"></i>

.. |i-explore| raw:: html

   <i class="vast vast-graph" role="img" aria-label="exploration"></i>

.. |i-api| raw:: html

   <i class="vast vast-laptop" role="img" aria-label="API reference"></i>

.. |i-examples| raw:: html

   <i class="vast vast-solution-brief" role="img" aria-label="examples"></i>

.. |i-prep| raw:: html

   <i class="vast vast-wrench" role="img" aria-label="data preparation"></i>

.. |i-indb| raw:: html

   <i class="vast vast-table-database" role="img" aria-label="in-database processing"></i>

.. |i-multisource| raw:: html

   <i class="vast vast-no-silos" role="img" aria-label="multi-source access"></i>

.. |i-files| raw:: html

   <i class="vast vast-folder" role="img" aria-label="file queries"></i>

.. |i-docs| raw:: html

   <i class="vast vast-ebook" role="img" aria-label="documentation"></i>

.. |i-chat| raw:: html

   <i class="vast vast-chat-bubble" role="img" aria-label="community"></i>

.. |i-email| raw:: html

   <i class="vast vast-email" role="img" aria-label="support"></i>

.. |i-about| raw:: html

   <i class="vast vast-3-users" role="img" aria-label="about us"></i>

.. |i-setup| raw:: html

   <i class="vast vast-gear" role="img" aria-label="setting up"></i>

.. |i-tests| raw:: html

   <i class="vast vast-easy" role="img" aria-label="unit tests"></i>

.. |i-functions| raw:: html

   <i class="vast vast-wrench-full" role="img" aria-label="useful functions"></i>

.. |i-practices| raw:: html

   <i class="vast vast-white-paper" role="img" aria-label="best practices"></i>

.. |i-frame| raw:: html

   <i class="vast vast-data-sheet" role="img" aria-label="vastframe"></i>

.. |i-stats| raw:: html

   <i class="vast vast-chart-up" role="img" aria-label="statistics"></i>

.. |i-notebook| raw:: html

   <i class="vast vast-monitor" role="img" aria-label="jupyter"></i>

.. |i-datasets| raw:: html

   <i class="vast vast-data-vault" role="img" aria-label="datasets"></i>

.. |i-sample| raw:: html

   <i class="vast vast-data-reduction" role="img" aria-label="sampling"></i>

.. |i-select| raw:: html

   <i class="vast vast-3-diverging-arrows" role="img" aria-label="model selection"></i>

.. |i-memory| raw:: html

   <i class="vast vast-storage-class-memory" role="img" aria-label="memory models"></i>

.. |i-automl| raw:: html

   <i class="vast vast-lightning-bolt" role="img" aria-label="automl"></i>

.. |i-funcs| raw:: html

   <i class="vast vast-wrench" role="img" aria-label="functions"></i>

.. |i-geo| raw:: html

   <i class="vast vast-globe" role="img" aria-label="geospatial"></i>

.. |i-joins| raw:: html

   <i class="vast vast-merging-arrows" role="img" aria-label="joins"></i>

.. |i-dupes| raw:: html

   <i class="vast vast-copy-to-clipboard" role="img" aria-label="duplicates"></i>

.. |i-missing| raw:: html

   <i class="vast vast-question-mark" role="img" aria-label="missing values"></i>

.. |i-encode| raw:: html

   <i class="vast vast-packaging" role="img" aria-label="encoding"></i>

.. |i-scale| raw:: html

   <i class="vast vast-scaling" role="img" aria-label="scaling"></i>

.. |i-decomp| raw:: html

   <i class="vast vast-objects" role="img" aria-label="decomposition"></i>

.. |i-feateng| raw:: html

   <i class="vast vast-gear" role="img" aria-label="feature engineering"></i>

.. |i-magic| raw:: html

   <i class="vast vast-constellation" role="img" aria-label="magic methods"></i>

.. |i-classify| raw:: html

   <i class="vast vast-shared-silos" role="img" aria-label="classification"></i>

.. |i-cluster| raw:: html

   <i class="vast vast-clouds" role="img" aria-label="clustering"></i>

.. |i-time| raw:: html

   <i class="vast vast-restore" role="img" aria-label="time"></i>

.. |i-understand| raw:: html

   <i class="vast vast-brain" role="img" aria-label="understand concepts"></i>

.. |i-business| raw:: html

   <i class="vast vast-dollar-sign" role="img" aria-label="business solutions"></i>

.. |i-market| raw:: html

   <i class="vast vast-chart-up" role="img" aria-label="market data"></i>

.. |i-bio| raw:: html

   <i class="vast vast-life-sciences" role="img" aria-label="life sciences"></i>

.. |i-game| raw:: html

   <i class="vast vast-play" role="img" aria-label="games"></i>

.. |i-ship| raw:: html

   <i class="vast vast-shipping" role="img" aria-label="titanic"></i>

.. |i-quality| raw:: html

   <i class="vast vast-easy" role="img" aria-label="quality"></i>

.. |i-telecom| raw:: html

   <i class="vast vast-phone" role="img" aria-label="telecom"></i>

.. |i-health| raw:: html

   <i class="vast vast-shield" role="img" aria-label="asset health"></i>

.. |i-travel| raw:: html

   <i class="vast vast-globe" role="img" aria-label="travel"></i>

.. |i-churn| raw:: html

   <i class="vast vast-chart-down" role="img" aria-label="customer churn"></i>

.. |i-fraud| raw:: html

   <i class="vast vast-lock" role="img" aria-label="fraud detection"></i>

.. |i-sports| raw:: html

   <i class="vast vast-speedometer" role="img" aria-label="sports performance"></i>

.. |i-insurance| raw:: html

   <i class="vast vast-data-protection" role="img" aria-label="insurance"></i>

.. |i-media| raw:: html

   <i class="vast vast-media-and-broadcast" role="img" aria-label="media"></i>

.. |i-energy| raw:: html

   <i class="vast vast-lightning-bolt" role="img" aria-label="energy"></i>

.. |i-spam| raw:: html

   <i class="vast vast-virus" role="img" aria-label="spam detection"></i>

.. |i-music| raw:: html

   <i class="vast vast-sound-on" role="img" aria-label="music"></i>

.. |i-virus| raw:: html

   <i class="vast vast-virus" role="img" aria-label="virus"></i>

.. |i-text| raw:: html

   <i class="vast vast-white-paper" role="img" aria-label="text analytics"></i>

.. |i-pipeline| raw:: html

   <i class="vast vast-merging-arrows" role="img" aria-label="pipeline"></i>

.. |i-ensemble| raw:: html

   <i class="vast vast-multiple-racks" role="img" aria-label="ensemble"></i>

.. |i-tree| raw:: html

   <i class="vast vast-3-diverging-arrows" role="img" aria-label="decision trees"></i>
"""

import os
import sys

# ─── FAST DOCS MODE ──────────────────────────────────────────────────────────
# Skip ALL code execution (ipython directives + notebooks) for fast styling /
# content iteration. Code blocks render as static highlighted Python instead
# of executing against Trino. Charts and outputs will NOT appear.
#
#   FAST_DOCS=1 make html          # fast structural/style build
#   make html                      # normal full build (executes everything)
FAST_DOCS = os.environ.get("FAST_DOCS", "").lower() in ("1", "true", "yes")
if FAST_DOCS:
    print("\033[93m*** FAST_DOCS: code execution disabled (ipython + notebooks) ***\033[0m")

sys.path.insert(0, os.path.abspath(".."))


project = "vastorbit"
copyright = "2026 VAST. All rights reserved."
author = "VAST"
release = "0.1.x"
# -- General configuration ---------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#general-configuration

keep_going = True

extensions = [
    "sphinx.ext.autodoc",
    "sphinx.ext.autosummary",
    "IPython.sphinxext.ipython_directive",
    "IPython.sphinxext.ipython_console_highlighting",
    "nbsphinx",
    "sphinx_inline_tabs",
    "sphinx_design",
    "sphinx_copybutton",
    "sphinx.ext.graphviz",
]

ipython_warning_is_error = False

# Notebooks: execute on normal builds, never in FAST_DOCS mode
nbsphinx_execute = "never" if FAST_DOCS else "auto"

templates_path = ["_templates"]

exclude_patterns = [
    '_build', 
    'Thumbs.db', 
    '.DS_Store',
]

import vastorbit  # isort:skip

# version = '%s r%s' % (pandas.__version__, svn_version())
version = str(vastorbit.__version__)

autosummary_generate = True


# -- Options for HTML output -------------------------------------------------
# https://www.sphinx-doc.org/en/master/usage/configuration.html#options-for-html-output


html_theme = "furo"

# Syntax highlighting: light-canvas tokens in light mode,
# bright dark-canvas tokens (Furo-specific option) in dark mode.
pygments_style = "tango"
pygments_dark_style = "native"  #'pydata_sphinx_theme'

html_static_path = ["_static"]

html_logo = "_static/vast_logo.png"


# Theme Options for Furo theme

html_theme_options = {
    # NOTE: footer_icons is no longer rendered — _templates/page.html
    # overrides Furo's footer with the full VAST footer (same links included).
    "footer_icons": [
        {
            "name": "Privacy Policy",
            "url": "https://www.vastdata.com/legal/privacy-policy",
            "html": "Privacy Policy",
            "class": "bottom_buttons",
        },
        {
            "name": "Cookies Policy",
            "url": "https://www.vastdata.com/legal/cookie-policy",
            "html": "Cookies Policy",
            "class": "bottom_buttons",
        },
        {
            "name": "GitHub",
            "url": "https://github.com/vastdata-dev/vastorbit",
            "html": """
                <svg stroke="currentColor" fill="currentColor" stroke-width="0" viewBox="0 0 16 16">
                    <path fill-rule="evenodd" d="M8 0C3.58 0 0 3.58 0 8c0 3.54 2.29 6.53 5.47 7.59.4.07.55-.17.55-.38 0-.19-.01-.82-.01-1.49-2.01.37-2.53-.49-2.69-.94-.09-.23-.48-.94-.82-1.13-.28-.15-.68-.52-.01-.53.63-.01 1.08.58 1.23.82.72 1.21 1.87.87 2.33.66.07-.52.28-.87.51-1.07-1.78-.2-3.64-.89-3.64-3.95 0-.87.31-1.59.82-2.15-.08-.2-.36-1.02.08-2.12 0 0 .67-.21 2.2.82.64-.18 1.32-.27 2-.27.68 0 1.36.09 2 .27 1.53-1.04 2.2-.82 2.2-.82.44 1.1.16 1.92.08 2.12.51.56.82 1.27.82 2.15 0 3.07-1.87 3.75-3.65 3.95.29.25.54.73.54 1.48 0 1.07-.01 1.93-.01 2.2 0 .21.15.46.55.38A8.013 8.013 0 0016 8c0-4.42-3.58-8-8-8z"></path>
                </svg>
            """,
            "class": "",
        },
    ],
    "announcement": f"""<div class='centered-content'>
                            
                        </div>



                    <div class="main-header-container">

                        <div class="very-top-container">

                            <a href="index.html">
                                <svg height="30px" width="150px" viewBox="50 130 1100 280" version="1.1" xmlns="http://www.w3.org/2000/svg">
                                    <!-- Main logo text - will change color based on theme -->
                                    <path class="logo-text" opacity="1" d="M68.64 154.01c-.31-9.01 6.54-17.88 15.44-19.5 25.31-.11 50.63-.01 75.94-.04 6.26-.22 11.99 5.26 12.26 11.48.2 5.03.14 10.07.05 15.1.04 5.98-5.18 11.74-11.31 11.5-13.18.13-26.38-.24-39.57.17 1.88 4.21 4.46 8.02 6.91 11.91 15.65 26.01 31.25 52.07 46.94 78.06 2.38 3.41 3.3 7.75 2.16 11.79-1.49 4.86-6.54 6.97-10.4 9.59-4.07 2.39-7.93 6.24-13.03 5.64-4.4.14-7.9-3.16-9.93-6.76-23.52-38.52-46.77-77.2-70.43-115.63-2.57-4.01-5.05-8.4-5.03-13.31m376.29 52.89c3.34-1.77 6.72-3.49 10.26-4.82 3.96-1.48 8.59.44 10.84 3.9 3.38 5.22 5.63 11.07 8.35 16.65 10.67 22.3 20.8 44.87 31.7 67.05 4.15-7.29 7.28-15.11 10.96-22.65 8.56-18.11 16.98-36.3 25.6-54.39 2.06-3.98 3.85-9 8.55-10.51 3.66-1.55 7.39.47 10.69 1.97 3.03 1.51 6.43 2.67 8.67 5.34 2.4 2.68 2.89 6.72 1.7 10.04-16.58 35.03-32.95 70.18-49.55 105.21-2.41 5.16-4.66 11.28-10.41 13.54-6.98 3.64-16.16-.07-19.56-6.92-17.66-37.32-35.14-74.73-52.79-112.05-1.95-4.58.65-10.21 4.99-12.36m255.29-3.69c7.24-3.98 17.15-.4 20.45 7.11 17.56 37.05 34.72 74.31 52.5 111.26 1.72 4.71-.37 10.36-4.88 12.64-4.29 2.07-8.5 4.9-13.3 5.47-5.85-.12-9.03-5.76-11.15-10.45-12.26-26.11-24.69-52.14-36.84-78.31-12.35 26.29-24.7 52.57-37.17 78.81-1.85 3.82-4 8.19-8.39 9.53-3.65 1.34-7.19-.86-10.41-2.32-3-1.54-6.36-2.74-8.57-5.4-2.37-2.69-2.69-6.68-1.64-9.98 16.63-34.73 32.88-69.66 49.24-104.53 2.52-5.11 4.51-11.33 10.16-13.83m175.28-.5c5.71-1.53 11.65-1.08 17.5-1.12 17.01 0 34.01 0 51.02-.01 3.56-.19 7.36.85 9.66 3.74 3.84 4.28 2.52 10.5 2.27 15.71-.05 4.29-2.86 8.62-7.16 9.62-4.52 1.04-9.2.53-13.79.63-16.69 0-33.37-.01-50.05 0-4.02-.17-8.55 1.47-10.35 5.3-1.2 3.82-.29 8.35 2.75 11.08 3.13 3.31 7.77 4.21 12.02 5.21 9.16 2.25 18.35 4.36 27.55 6.49 10.69 2.43 20.83 8.6 26.81 17.95 6.27 9.57 7.4 21.91 4.56 32.84-4.42 16.92-22 28.83-39.3 27.59-19.35-.06-38.7.03-58.05-.05-5.74.5-10.77-5.06-10.42-10.65.04-3.91-.2-7.9.74-11.73 1.14-4.18 5.35-7.27 9.72-6.93 18.67-.02 37.34-.04 56.02.02 3.24-.01 6.83.16 9.59-1.86 4.09-2.91 4.36-9.08 2.03-13.18-1.94-3.35-5.84-4.7-9.42-5.42-10.08-2.09-20.01-4.79-30.05-7.03-11.68-2.75-22.57-9.75-29.04-19.97-6.18-9.91-7.5-22.64-3.89-33.68 4.23-12.87 16.5-21.51 29.28-24.55m148.18 7.25c.57-4.9 5.41-8.63 10.28-8.37 34.02.01 68.05-.03 102.08.02 5.18-.13 9.74 4.26 10.14 9.37.31 5.72 1.12 12.51-3.19 17.04-2.47 2.84-6.45 3.34-9.98 3.29-11.04-.06-22.09.02-33.13-.07-.62 32.25-.04 64.54-.28 96.8.05 4.22-3.31 7.86-7.07 9.31-4.48.7-9.05.34-13.56.31-3.54.15-6.57-2.42-8.11-5.41-1.49-3.9-1.03-8.17-1.1-12.25.02-29.58.04-59.15 0-88.73-10.59.02-21.18-.02-31.76.05-2.81-.01-5.71.02-8.34-1.07-3.46-1.68-6.11-5.28-6.08-9.20-.11-3.7-.19-7.4.1-11.09m-746.54 46.21c2.45-4.08 4.79-9.18 9.89-10.35 5.41-1.61 10.15 2.03 14.55 4.61 3.98 2.47 8.84 4.57 10.7 9.22 1.45 5.1.21 10.62-2.56 15.05-22.43 37.26-44.77 74.59-67.2 111.85-2.97 4.8-5.45 10.51-10.77 13.18-7.78 4.2-18.01.31-22.64-6.8-12.42-20.91-24.81-41.86-37.28-62.75-1.98-3.09-2.1-7.09-1.03-10.51 1.5-3.68 5.17-5.65 8.47-7.45 3.7-1.98 7.23-4.28 11.08-5.97 4.9-2.16 11.01.1 13.74 4.61 6.76 10.93 12.98 22.2 19.96 33.01 1.52-2.12 3-4.26 4.3-6.52 16.12-27.14 32.53-54.12 48.79-81.18"/>
                                    
                                    <!-- Blue accent triangle - stays the same in both modes -->
                                    <path class="logo-accent" opacity="1" d="M203.53 145.2c1.34-6.93 9.06-10.09 15.46-9.87 47.65-.07 95.3-.09 142.95-.08 12.9-.32 21.83 16.09 15.39 26.98-12.07 19.99-24.18 39.94-36.12 60-1.82 3.44-4.49 6.78-8.52 7.58-3.84 1.42-7.66-.82-10.91-2.68-3.56-2.13-7.26-4.03-10.77-6.24-4.54-2.9-6.7-9.3-4.17-14.19 6.28-11.58 13.94-22.4 20.07-34.06-37.65-.12-75.3-.01-112.94-.09-5.95.11-11.02-5.62-10.68-11.47.09-5.29-.33-10.62.24-15.88"/>
                                </svg>
                            </a>

                            <div class="top-dropdown">
                                <button class="dropdown-btn">&#9776;</button>
                                <div class="dropdown-content">
                                    <a class="top-button" href="./getting_started.html" id="sitenav-solutions">Getting Started</a>
                                    <a class="top-button" href="./about_us.html" id="sitenav-solutions">About Us</a>
                                    <a class="top-button" href="./api.html" id="sitenav-solutions">API Reference</a>
                                    <a class="top-button" href="https://github.com/vastdata-dev/vastorbit" id="sitenav-solutions">GitHub</a>
                                </div>
                            </div>
                            <div class="search-top-dropdown">
                                <button class="search-dropdown-btn">
                                    <svg width="30" height="30" viewBox="0 0 100 100" xmlns="http://www.w3.org/2000/svg" fill="none" stroke="#000000" stroke-width="10">
                                    <!-- Handle -->
                                    <line x1="60" y1="60" x2="85" y2="85"></line>
                                    <!-- Glass -->
                                    <circle cx="35" cy="35" r="30"></circle>
                                    </svg>
                                </button>
                                <div class="search-dropdown-content">
                                    <form class="sidebar-search-container_top-2" method="get" action="search.html" role="search">
                                    <input class="sidebar-search" placeholder="Search" name="q" aria-label="Search">
                                    <input type="hidden" name="check_keywords" value="yes">
                                    <input type="hidden" name="area" value="default">
                                    </form>
                                </div>
                            </div>
                            <div class="right-top-container">
                                <div class="top-button-container">
                                    <a class="top-button" href="./index.html" id="sitenav-solutions">Home</a>
                                    <a class="top-button" href="./about_us.html" id="sitenav-solutions">About Us</a>
                                    <a class="top-button" href="./api.html" id="sitenav-solutions">API Reference</a>
                                    <a class="top-button" href="" id="sitenav-solutions">GitHub</a>
                                </div>
                                <div class='top_search'>
                                    <form class='sidebar-search-container sidebar-search-container_top' method='get' action='search.html' role='search'>
                                        <input class='sidebar-search' placeholder='Search Content...' name='q' aria-label='Search'>
                                        <input type='hidden' name='check_keywords' value='yes'>
                                        <input type='hidden' name='area' value='default'>
                                    </form>
                                </div>
                                <div class="form-group">
                                    <select class="form-control" id="filter-select" name="filter-select" onchange="switchVersion(this.value)">
                                        <option value="0.1.x" selected>0.1.x</option>
                                    </select>
                                </div>
                                <div class="color-theme-container">
                                    <button class="theme-toggle">
                                        <div class="visually-hidden">Toggle Light / Dark / Auto color theme</div>
                                        <svg class="theme-icon-when-auto-dark"><use href="#svg-moon-with-sun"></use></svg>
                                        <svg class="theme-icon-when-auto-light"><use href="#svg-sun-with-moon"></use></svg>
                                        <svg class="theme-icon-when-dark"><use href="#svg-moon"></use></svg>
                                        <svg class="theme-icon-when-light"><use href="#svg-sun"></use></svg>
                                    </button>
                                </div>
                            </div>
                            
                        </div>
                </div>""",
    "light_css_variables": {
        "color-announcement-background": "white",
        "color-announcement-text": "#03142C",   # VAST Navy
        "color-sidebar-background": "#F4F4F5",
        "color-sidebar-background-border": "#E4E4E7",
        "color-brand-primary": "#03142C",       # VAST Navy
        "color-brand-content": "#0E86B8",       # readable cyan-blue for links on white
    },
    "dark_css_variables": {
        # VAST navy ramp — layered navy, never pure black (matches vastdata.com)
        "color-background-primary": "#04101F",
        "color-background-secondary": "#03142C",   # VAST Navy
        "color-background-hover": "#0A2240",
        "color-background-border": "#1B3A5C",
        "color-foreground-primary": "#E8EFF7",
        "color-foreground-secondary": "#9FB3C8",
        "color-code-background": "#0A2240",
        "color-code-foreground": "#E8EFF7",
        "color-inline-code-background": "rgba(31, 217, 254, 0.10)",
        "color-sidebar-background": "#0F2042",
        "color-sidebar-item-background--hover": "#0A2240",
        "color-admonition-background": "#0A2240",
        "color-announcement-background": "#03142C",
        "color-announcement-text": "#E8EFF7",
        "color-brand-primary": "#1FD9FE",          # VAST Cyan
        "color-brand-content": "#1FD9FE",
    },
}

html_favicon = "_static/vlogo.png"
# Customization
html_css_files = [
    "css/vast_brand.css",  # VAST brand tokens — must load before the other stylesheets
    "css/custom_styling.css",
    "css/ai_assistant.css",
    "css/vast_icons.css",  # official VAST icon font (122 glyphs, _static/fonts/)
    "css/vi_icons.css",  # vi mask glyphs (|check|, |cross|, ... — _static/icons/)
    # Inter is the web fallback when licensed Moderat woff2 files are absent
    "https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700;800&display=swap",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/fontawesome.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/solid.min.css",
    "https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/brands.min.css",
]

html_js_files = [
    "js/ai_assistant.js",
    "js/theme_dark_default.js",
]

def _register_noexec_ipython(app):
    """FAST_DOCS: replace the executing ipython directive with a static
    code-block renderer. Same content, zero execution, instant builds."""
    from docutils import nodes
    from docutils.parsers.rst import Directive, directives

    class NoExecIPython(Directive):
        has_content = True
        required_arguments = 0
        optional_arguments = 1
        final_argument_whitespace = True
        option_spec = {
            "verbatim": directives.flag,
            "suppress": directives.flag,
            "okexcept": directives.flag,
            "okwarning": directives.flag,
            "doctest": directives.flag,
            "python": directives.unchanged,
        }

        def run(self):
            if "suppress" in self.options:
                return []  # hidden in real builds, hidden here too
            lines = [l for l in self.content if not l.lstrip().startswith("@savefig")]
            code = "\n".join(lines)
            node = nodes.literal_block(code, code)
            node["language"] = "python"
            return [node]

    app.add_directive("ipython", NoExecIPython, override=True)


def setup(app):
    """Patch IPython directive to skip remaining cells in failed RST files."""
    if FAST_DOCS:
        _register_noexec_ipython(app)
        return  # skip the retry monkeypatch; nothing executes anyway
    try:
        from IPython.sphinxext import ipython_directive
        import time
        import os
        
        # Track failed files
        failed_files = set()
        current_file = [None]  # Use list for mutability in closure
        
        # Monkey-patch the process_input method
        original_process_input = ipython_directive.EmbeddedSphinxShell.process_input
        
        def safe_process_input_with_retry(self, data, input_prompt, lineno):
            # Get current source file from Sphinx state
            try:
                source_file = self.state.document.current_source
                
                # Check if we moved to a new file
                if source_file != current_file[0]:
                    current_file[0] = source_file
                    # Reset failure state for new file
                    if source_file in failed_files:
                        print(f"\n📄 Processing new file: {os.path.basename(source_file)}")
                        print(f"   (Previous failures in this file will be ignored)\n")
                
                # Skip if this file already failed
                if source_file in failed_files:
                    print(f"⏭️  Skipping cell (file already failed): {os.path.basename(source_file)}")
                    return
                    
            except AttributeError:
                source_file = "unknown"
            
            max_retries = 30
            retry_delay = 10
            max_delay = 120
            
            for attempt in range(max_retries):
                try:
                    return original_process_input(self, data, input_prompt, lineno)
                except Exception as e:
                    error_msg = str(e)
                    
                    # Check if it's a Trino connection error
                    if any(keyword in error_msg.lower() for keyword in [
                        'failed connection to trino',
                        'trino.client',
                        'connection refused',
                        'cannot connect',
                        'failed after'
                    ]):
                        if attempt < max_retries - 1:
                            wait_time = min(retry_delay * (2 ** attempt), max_delay)
                            print(f"\n⏳ Trino connection failed. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                            print(f"   Error: {error_msg}")
                            print(f"   💡 Please start Trino and the build will continue automatically.\n")
                            time.sleep(wait_time)
                        else:
                            # Max retries reached - mark file as failed and skip
                            print(f"\n❌ Trino connection failed after {max_retries} attempts in {os.path.basename(source_file)}")
                            print(f"   ⏭️  Skipping remaining cells in this file and moving to next RST...\n")
                            failed_files.add(source_file)
                            return
                    else:
                        # Non-Trino error - mark file as failed and skip
                        print(f"\n⚠️  IPython execution failed in {os.path.basename(source_file)}: {e}")
                        print(f"   ⏭️  Skipping remaining cells in this file and moving to next RST...\n")
                        failed_files.add(source_file)
                        return
            
            return
        
        ipython_directive.EmbeddedSphinxShell.process_input = safe_process_input_with_retry
        
        # Patch process_block similarly
        original_process_block = ipython_directive.EmbeddedSphinxShell.process_block
        
        def safe_process_block_with_retry(self, block):
            # Get current source file
            try:
                source_file = self.state.document.current_source
                
                # Check if we moved to a new file
                if source_file != current_file[0]:
                    current_file[0] = source_file
                    if source_file in failed_files:
                        print(f"\n📄 Processing new file: {os.path.basename(source_file)}")
                
                # Skip if this file already failed
                if source_file in failed_files:
                    print(f"⏭️  Skipping block (file already failed): {os.path.basename(source_file)}")
                    return [], None
                    
            except AttributeError:
                source_file = "unknown"
            
            max_retries = 30
            retry_delay = 10
            max_delay = 120
            
            for attempt in range(max_retries):
                try:
                    return original_process_block(self, block)
                except Exception as e:
                    error_msg = str(e)
                    
                    if any(keyword in error_msg.lower() for keyword in [
                        'failed connection to trino',
                        'trino.client',
                        'connection refused',
                        'cannot connect',
                        'failed after'
                    ]):
                        if attempt < max_retries - 1:
                            wait_time = min(retry_delay * (2 ** attempt), max_delay)
                            print(f"\n⏳ Trino connection failed. Waiting {wait_time}s before retry {attempt + 1}/{max_retries}...")
                            print(f"   💡 Please start Trino and the build will continue automatically.\n")
                            time.sleep(wait_time)
                        else:
                            print(f"\n❌ Trino connection failed after {max_retries} attempts in {os.path.basename(source_file)}")
                            print(f"   ⏭️  Skipping remaining cells in this file and moving to next RST...\n")
                            failed_files.add(source_file)
                            return [], None
                    else:
                        print(f"\n⚠️  IPython block failed in {os.path.basename(source_file)}: {e}")
                        print(f"   ⏭️  Skipping remaining cells in this file and moving to next RST...\n")
                        failed_files.add(source_file)
                        return [], None
            
            return [], None
        
        ipython_directive.EmbeddedSphinxShell.process_block = safe_process_block_with_retry
        
    except ImportError:
        pass