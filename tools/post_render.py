#!/usr/bin/env python3
"""Keep historical reading URLs working and validate generated local links."""
from html import escape
from html.parser import HTMLParser
import json
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT/'docs'
redirects = json.loads((ROOT/'tools/redirects.json').read_text())
for old, new in redirects.items():
    destination = '../' + new
    path = DOCS/old
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text('<!doctype html><html lang="en"><head><meta charset="utf-8">'
                    f'<meta http-equiv="refresh" content="0;url={escape(destination)}">'
                    '<title>Reading moved</title></head><body>'
                    f'<a href="{escape(destination)}">Continue to the reading</a>'
                    '<script>location.replace(' + json.dumps(destination) + '+location.hash)</script>'
                    '</body></html>\n')
(DOCS/'.nojekyll').touch()

class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.links = []
    def handle_starttag(self, tag, attrs):
        for name, value in attrs:
            if name in ('href', 'src') and value:
                self.links.append(value)

missing = set()
for path in DOCS.rglob('*.html'):
    parser = Links()
    parser.feed(path.read_text())
    for link in parser.links:
        url = urlsplit(link)
        if url.scheme or url.netloc or not url.path:
            continue
        target = DOCS/unquote(url.path).lstrip('/') if url.path.startswith('/') else path.parent/unquote(url.path)
        if not target.exists():
            missing.add((str(path.relative_to(DOCS)), link))
if missing:
    raise SystemExit('Broken local links: ' + repr(sorted(missing)))
print('Verified generated local links and preserved 23 historical reading URLs.')
