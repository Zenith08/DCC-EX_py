import os
import re
from typing import Optional

# Directory where Sphinx generates the documentation
build_dir: str = os.path.join('docs', 'build')

# Regular expression to match links that include the incorrect path
link_regex: re.Pattern[str] = re.compile(r'\(_autosummary/(.*?)\.md(#.*?)?\)')
python_regex: re.Pattern[str] = re.compile(r'```default')


def replace_link(match: re.Match) -> str:
    # Extract path without '_autosummary/' and '.md'
    path: str = match.group(1)
    # Extract fragment if it exists
    print(f"Got path {path}")
    fragment: Optional[str] = match.group(2) if match.group(2) else ''
    return f'({path}{fragment})'


def fix_links_in_file(file_path) -> None:
    with open(file_path, 'r', encoding='utf8') as file:
        content: str = file.read()

    # Replace all occurrences of the incorrect path with the correct path
    updated_content: str = re.sub(link_regex, replace_link, content)
    updated_content = updated_content.replace("```default", "```python")
    updated_content = updated_content.replace(".. code-block:", "")

    with open(file_path, 'w', encoding='utf8') as file:
        file.write(updated_content)


def process_directory(dir_path) -> None:
    for root, _, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith('.md'):
                file_path: str = os.path.join(root, file_name)
                fix_links_in_file(file_path)


def list_files(startpath):
    for root, dirs, files in os.walk(startpath):
        level = root.replace(startpath, '').count(os.sep)
        indent = ' ' * 4 * (level)
        print('{}{}/'.format(indent, os.path.basename(root)))
        subindent = ' ' * 4 * (level + 1)
        for f in files:
            print('{}{}'.format(subindent, f))


if __name__ == '__main__':
    # Start processing the HTML files in the build directory
    list_files(".")
    process_directory(build_dir)
    print(f"Fixed links in directory: {build_dir}")
