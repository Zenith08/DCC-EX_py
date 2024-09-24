import os
import re
from typing import Optional

# Directory where Sphinx generates the documentation
build_dir: str = os.path.join(os.path.abspath('.'), 'docs', 'build', 'markdown')

# The correct path you want to use (e.g., root or other folder GitHub Wiki expects)
correct_path = ''

# Regular expression to match links that include the incorrect path
link_regex: re.Pattern[str] = re.compile(r'\(_autosummary/(.*?)\.md(#.*?)?\)')

def replace_link(match: re.Match) -> str:
    path: str = match.group(1)  # Extract path without '_autosummary/' and '.md'
    fragment: Optional[str] = match.group(2) if match.group(2) else ''  # Extract fragment if it exists
    return f'({path}{fragment})'

def fix_links_in_file(file_path) -> None:
    with open(file_path, 'r', encoding='utf8') as file:
        content: str = file.read()

    # Replace all occurrences of the incorrect path with the correct path
    # updated_content = re.sub(link_regex, lambda match: match.group(1).replace(incorrect_path, correct_path), content)
    updated_content: str = re.sub(link_regex, replace_link, content)

    with open(file_path, 'w', encoding='utf8') as file:
        file.write(updated_content)

def process_directory(dir_path) -> None:
    for root, _, files in os.walk(dir_path):
        for file_name in files:
            if file_name.endswith('.md'):
                file_path: str = os.path.join(root, file_name)
                fix_links_in_file(file_path)

if __name__ == '__main__':
    # Start processing the HTML files in the build directory
    process_directory(build_dir)
    print(f"Fixed links in directory: {build_dir}")