"""
One-time cleanup.

71 source files currently have the literal path
    SPHINX_DIRECTORY
frozen into their `.. raw:: html :file:` directives, because the old reverse
script never matched (it looked for "VAST Orbit-master" with a space). Since the
SPHINX_DIRECTORY placeholder no longer exists in those files, re-running
replace_sphinx_dir.py can't fix them.

Run this ONCE to turn the stale absolute path back into the placeholder. After
that, the normal replace / reverse cycle takes over and stays machine-independent.

    python3 normalize_baked_paths.py
"""

import os

# The exact stale string baked into the source tree. If you find other stale
# roots later, add them here.
STALE_PATHS = [
    "SPHINX_DIRECTORY",
    "/Users/badr.ouali/Documents/VAST Orbit-master/docs",  # the spaced variant, just in case
]
PLACEHOLDER = "SPHINX_DIRECTORY"

search_directory = ".."
SELF = {
    "replace_sphinx_dir.py",
    "reverse_replace_sphinx_dir.py",
    "normalize_baked_paths.py",
}

changed = 0
for root, dirs, files in os.walk(search_directory):
    for file in files:
        if not (file.endswith(".py") or file.endswith(".rst")) or file in SELF:
            continue
        path = os.path.join(root, file)
        with open(path, "r", encoding="utf-8") as f:
            content = f.read()
        new = content
        for stale in STALE_PATHS:
            new = new.replace(stale, PLACEHOLDER)
        if new != content:
            with open(path, "w", encoding="utf-8") as f:
                f.write(new)
            changed += 1
            print(f"Normalized: {path}")

print(f"Done. {changed} file(s) reset to the {PLACEHOLDER} placeholder.")
