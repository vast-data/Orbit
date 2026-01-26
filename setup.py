"""
SPDX-License-Identifier: Apache-2.0
"""
#!/usr/bin/env python
import setuptools

with open("README.md", "r", encoding="utf-8") as fh:
    long_description = fh.read()

setuptools.setup(
    name="vastorbit",
    version="0.1.0",
    author="Badr Ouali",
    author_email="badr.ouali@outlook.fr",
    url="https://github.com/vastdata-dev/vastorbit",
    project_urls={
        "Bug Tracker": "https://github.com/vastdata-dev/vastorbit/issues",
        "Documentation": "",
        "Source Code": "https://github.com/vastdata-dev/vastorbit",
    },
    license="Apache-2.0",
    keywords=[
        "VAST",
        "python",
        "ml",
        "data science",
        "machine learning",
        "statistics",
        "database",
        "trino",
        "analytics",
        "big data",
    ],
    description=(
        "vastorbit simplifies data exploration, data cleaning, and machine "
        "learning in VAST databases using in-database analytics."
    ),
    long_description=long_description,
    long_description_content_type="text/markdown",
    packages=setuptools.find_packages(exclude=["tests", "tests.*", "docs", "examples"]),
    python_requires=">=3.12",
    install_requires=[
        "graphviz>=0.20.0",
        "matplotlib>=3.7.0",
        "numpy>=1.24.0",
        "pandas>=2.0.0",
        "plotly>=5.18.0",
        "scipy>=1.10.0",
        "scikit-learn>=1.3.0",
        "tqdm>=4.65.0",
        "vertica-highcharts>=0.1.4",
        "trino>=0.328.0",
        "pyyaml>=6.0.1",
        "requests>=2.32.2",
        "urllib3>=2.2.1",
    ],
    extras_require={
        "geo": [
            "descartes>=1.1.0",
            "geopandas>=0.14.0",
            "shapely>=2.0.0",
        ],
        "parquet": [
            "pyarrow>=15.0.0",
        ],
        "dev": [
            "pytest>=7.4.0",
            "pytest-cov>=4.1.0",
            "pytest-mock>=3.12.0",
            "black>=23.12.0",
            "ruff>=0.1.0",
            "isort>=5.13.0",
            "mypy>=1.8.0",
            "sphinx>=7.2.0",
            "sphinx-rtd-theme>=2.0.0",
        ],
        "all": [
            "descartes>=1.1.0",
            "geopandas>=0.14.0",
            "shapely>=2.0.0",
            "pyarrow>=15.0.0",
        ],
    },
    package_data={
        "vastorbit": [
            "*.csv",
            "*.json",
            "*.css",
            "*.html",
            "datasets/data/*.csv",
            "datasets/data/*.json",
        ]
    },
    include_package_data=True,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Intended Audience :: Science/Research",
        "Intended Audience :: Developers",
        "Intended Audience :: Financial and Insurance Industry",
        "Programming Language :: Python :: 3",
        "Programming Language :: Python :: 3.12",
        "Programming Language :: Python :: 3.13",
        "Programming Language :: Python :: 3.14",
        "Programming Language :: Python :: 3 :: Only",
        "Topic :: Database",
        "Topic :: Scientific/Engineering",
        "Topic :: Scientific/Engineering :: Artificial Intelligence",
        "Topic :: Scientific/Engineering :: Information Analysis",
        "License :: OSI Approved :: Apache Software License",
        "Operating System :: OS Independent",
        "Natural Language :: English",
    ],
    zip_safe=False,
)