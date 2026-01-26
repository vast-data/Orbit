#!/bin/bash

# Uninstall vastorbit
echo y | pip3 uninstall vastorbit

# Execute replace_sphinx_dir.py script
python3 replace_sphinx_dir.py

# Change the theme to sphinx inside vastorbit/_config/config.py

# Install the package
pip3 install ../.

# Clean the build directory
make clean

# In case the data files are not copied, then you can run the lines below
mkdir /usr/local/lib/python3.10/site-packages/vastorbit/datasets/data/laliga/
cp ../vastorbit/datasets/data/laliga/*.json /usr/local/lib/python3.10/site-packages/vastorbit/datasets/data/laliga/

# Build HTML documentation
make html

# Execute remove_pattern.py script
python3 remove_pattern.py

# Fix search directory for top nav bar + logo
python3 fix_links.py

# Create Manual TOC tree
python3 create_toc_tree.py

# Modify the header links of User Guide to work for Home/User_guide/Api/
# python3 notebook_correction.py

# Reverse replace_sphinx_dir.py script
python3 reverse_replace_sphinx_dir.py

# Run Blck
# black ../.