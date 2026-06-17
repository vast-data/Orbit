import os

DOCS_DIR = os.path.dirname(os.path.abspath(__file__))

search_directory = ".."
search_word = DOCS_DIR  # whatever the forward script wrote
replacement_word = "SPHINX_DIRECTORY"

SELF = {"replace_sphinx_dir.py", "reverse_replace_sphinx_dir.py"}


def search_replace_in_file(file_path):
    with open(file_path, "r", encoding="utf-8") as file:
        content = file.read()
    if search_word not in content:
        return False
    with open(file_path, "w", encoding="utf-8") as file:
        file.write(content.replace(search_word, replacement_word))
    return True


print(f"Reverting '{search_word}' -> '{replacement_word}'")
for root, dirs, files in os.walk(search_directory):
    for file in files:
        if (file.endswith(".py") or file.endswith(".rst")) and file not in SELF:
            path = os.path.join(root, file)
            if search_replace_in_file(path):
                print(f"Updated: {path}")

print("Search and replace complete.")
