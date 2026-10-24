"""Dependency-free checks for the static website before publication."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, unquote
import json
import re
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://drchangtingwei.com'
errors = []

class Page(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.ids, self.refs, self.ld, self.canonicals = [], [], [], []
        self.h1 = 0
        self.in_ld = False
        self.buffer = ''
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if 'id' in a:
            self.ids.append(a['id'])
        if tag == 'h1': self.h1 += 1
        if tag == 'link' and a.get('rel') == 'canonical':
            self.canonicals.append(a.get('href'))
        if tag == 'script' and a.get('type') == 'application/ld+json':
            self.in_ld, self.buffer = True, ''
        for key in ('href', 'src'):
            if a.get(key): self.refs.append(a[key])
        if tag == 'img' and 'alt' not in a:
            errors.append('Image missing alt attribute')
        if tag == 'a' and a.get('target') == '_blank' and 'noopener' not in a.get('rel', ''):
            errors.append('External new-tab link missing noopener: ' + a.get('href', ''))

    def handle_data(self, data):
        if self.in_ld: self.buffer += data

    def handle_endtag(self, tag):
        if tag == 'script' and self.in_ld:
            self.ld.append(self.buffer)
            self.in_ld = False

def local_file(url, source):
    parts = urlsplit(url)
    if parts.netloc and parts.netloc != 'drchangtingwei.com': return None
    if parts.scheme not in ('', 'http', 'https'): return None
    raw = unquote(parts.path)
    dest = (ROOT / raw.lstrip('/')) if raw.startswith('/') else (source.parent / raw if raw else source)
    if dest.is_dir(): dest /= 'index.html'
    return dest.resolve(), unquote(parts.fragment)

files = sorted(p for p in ROOT.rglob('*.html') if '.tmp' not in p.parts and '.git' not in p.parts)
pages = {}
for file in files:
    if file.name.startswith('google'): continue
    page = Page(file.read_text())
    pages[file.resolve()] = page
    if page.h1 != 1: errors.append(f'{file.relative_to(ROOT)}: {page.h1} h1 elements')
    if len(page.ids) != len(set(page.ids)): errors.append(f'{file.relative_to(ROOT)}: duplicate IDs')
    if file.name != '404.html' and len(page.canonicals) != 1: errors.append(f'{file.relative_to(ROOT)}: canonical count')
    for ld in page.ld:
        try: json.loads(ld)
        except ValueError as e: errors.append(f'{file.relative_to(ROOT)}: invalid JSON-LD {e}')

checked = 0
for file, page in pages.items():
    for ref in page.refs:
        target = local_file(ref, file)
        if not target: continue
        checked += 1
        dest, fragment = target
        if not dest.exists(): errors.append(f'{file.relative_to(ROOT)}: missing {ref}')
        elif fragment and dest in pages and fragment not in pages[dest].ids:
            errors.append(f'{file.relative_to(ROOT)}: missing anchor {ref}')

xml = ET.parse(ROOT / 'sitemap.xml')
urls = [e.text for e in xml.findall('.//{*}loc')]
text_urls = (ROOT / 'sitemap.txt').read_text().splitlines()
if set(urls) != set(text_urls) or len(urls) != len(set(urls)):
    errors.append('Sitemap XML/text mismatch or duplicate URLs')
for url in urls:
    dest, _ = local_file(url, ROOT / 'index.html')
    if not dest.exists(): errors.append('Sitemap missing page: ' + url)
    elif dest in pages and pages[dest].canonicals != [url]: errors.append('Canonical mismatch: ' + url)
workflow = (ROOT / '.github/workflows/indexnow.yml').read_text()
for url in urls:
    if '"' + url + '"' not in workflow: errors.append('IndexNow missing ' + url)

if errors:
    print('\n'.join(errors))
    sys.exit(1)
print(f'PASS: {len(pages)} HTML pages, {checked} local links/assets/anchors, {len(urls)} sitemap URLs, JSON-LD, canonical tags, image alt text.')
