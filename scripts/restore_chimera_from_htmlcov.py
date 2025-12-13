#!/usr/bin/env python3
"""Utility to restore chimera_autarch.py from the htmlcov coverage HTML file.
Use this if the Python source was accidentally overwritten.
"""
import html
import re
from pathlib import Path


def restore(htmlcov_path: Path, out_path: Path):
    text = htmlcov_path.read_text(encoding='utf-8')
    # Extract content within <main id="source"> ... </main>
    m = re.search(r'<main id="source">(.*?)</main>', text, flags=re.S)
    if not m:
        raise RuntimeError("Could not find <main id=\"source\"> in htmlcov file")

    source_html = m.group(1)
    # Remove line number spans and extract code spans
    # Replace HTML entities and strip tags
    # Replace closing tag patterns for lines with newline
    # The code in coverage uses <p class="..."><span class="n">...line number...</span><span class="t">...code...</span></p>
    lines = []
    for match in re.finditer(r'<p[^>]*>(.*?)</p>', source_html, flags=re.S):
        p_content = match.group(1)
        # Strip leading line number
        # Remove any <span class="n">...</span>
        p_content = re.sub(r'<span class="n">.*?</span>', '', p_content, flags=re.S)
        # Remove <span class="t"> and nested spans and get their inner text
        # Replace each span tag with its text content by removing tags
        text_line = re.sub(r'<[^>]+>', '', p_content)
        # Unescape HTML entities
        text_line = html.unescape(text_line)
        # Strip trailing whitespace added by coverage formatting
        lines.append(text_line.rstrip())

    # Write back to out_path
    out_path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f"Restored {out_path} from {htmlcov_path}, {len(lines)} lines")


if __name__ == '__main__':
    import sys
    base = Path(__file__).resolve().parents[1]
    htmlcov = base / 'htmlcov' / 'chimera_autarch_py.html'
    out = base / 'chimera_autarch.py'
    if not htmlcov.exists():
        print('htmlcov file not found:', htmlcov)
        sys.exit(2)
    restore(htmlcov, out)

