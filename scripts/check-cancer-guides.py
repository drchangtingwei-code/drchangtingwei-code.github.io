"""Ensure cancer guides remain readable, source-linked and easy to book from."""
from html import unescape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json
import re

ROOT = Path(__file__).resolve().parent.parent
SLUGS = ('lung-cancer-treatment', 'esophageal-cancer', 'mediastinal-tumor')

def plain(text):
    return unescape(re.sub('<[^>]+>', '', text)).strip()

class Links(HTMLParser):
    def __init__(self, text):
        super().__init__(convert_charrefs=True)
        self.links = []
        self.feed(text)
    def handle_starttag(self, tag, attrs):
        if tag == 'a': self.links.append(dict(attrs))

for slug in SLUGS:
    page = (ROOT / 'articles' / (slug + '.html')).read_text()
    visible_faq = re.search(r'<section class="content-block cancer-faq".*?</section>', page, re.S).group()
    pairs = re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', visible_faq, re.S)
    data = json.loads(re.search(r'<script type="application/ld\+json" data-cancer-faq>(.*?)</script>', page, re.S).group(1))
    assert len(pairs) == len(data['mainEntity']) == 4, slug
    for (q, a), entity in zip(pairs, data['mainEntity']):
        assert plain(q) == entity['name'] and plain(a) == entity['acceptedAnswer']['text'], slug
    intro = re.search(r'<section class="clinician-context".*?</section>', page, re.S).group()
    assert all(x in plain(intro) for x in ('張庭瑋', 'Ting-Wei Chang', '高醫本院', '高醫岡山')), slug
    for host in ('www.kmuh.org.tw', 'www.kmugh.org.tw'):
        assert any(urlsplit(a.get('href', '')).hostname == host and parse_qs(urlsplit(a['href']).query).get('doctorID') == ['1080224'] for a in Links(intro).links), slug
    for route in ('kmuh-thoracic', 'kmugh-thoracic'):
        assert any(a.get('data-booking') == route for a in Links(page).links), slug
    assert 'class="mobile-cta" href="../appointment/#thoracic"' in page, slug
    assert 'reviewedBy' not in page and 'lastReviewed' not in page and '撰寫並審閱' not in page, slug
    assert '<ol class="cancer-path"' in page, slug
    assert len(re.findall(r'<h1\b', page)) == 1, slug
    for index in ('index.html', 'thoracic/index.html', 'articles/index.html'):
        assert slug + '.html' in (ROOT / index).read_text(), (slug, index)
print('PASS: 3 cancer guides, 12 visible/schema-matched FAQs, official physician identity and booking routes, diagrams, and discoverable internal links.')
