"""Regression checks for visible physician identity and patient booking routes."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit, parse_qs
import json
import re

ROOT = Path(__file__).resolve().parent.parent
ORIGIN = 'https://drchangtingwei.com'
PHYSICIAN = ORIGIN + '/#physician'
BOOKING_ROUTES = {
    'kmuh-weight': ('www.kmuh.org.tw', '/Web/WebRegistration/QuickPass/QuickPassReserve', {'FormType': ['Weight']}),
    'kmuh-thoracic': ('www.kmuh.org.tw', '/Web/WebRegistration/Registration/RegSchedule', {'virtualCode': ['HD25'], 'JsonLoc': ['["0230"]'], 'lang': ['tw']}),
    'kmugh-thoracic': ('www.kmugh.org.tw', '/Web/WebRegistration/Registration/RegSchedule', {'virtualCode': ['GD11'], 'JsonLoc': ['["0230"]'], 'lang': ['tw']}),
}


class VisiblePage(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.links, self.text, self.hidden = [], [], 0
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        if tag in ('head', 'script', 'style'): self.hidden += 1
        if tag == 'a': self.links.append(dict(attrs))

    def handle_endtag(self, tag):
        if tag in ('head', 'script', 'style'): self.hidden -= 1

    def handle_data(self, data):
        if not self.hidden: self.text.append(data)


for path in ('index.html', 'about/index.html', 'en/index.html'):
    source = (ROOT / path).read_text()
    graph = json.loads(re.search(r'<script type="application/ld\+json">(.*?)</script>', source, re.S).group(1))['@graph']
    person = next(node for node in graph if node.get('@type') == 'Person')
    assert person['@id'] == PHYSICIAN, path
    assert person['identifier']['value'] == '1080224', path
    assert person['worksFor']['@id'] == ORIGIN + '/#kmuh', path
    assert person['affiliation']['@id'] == ORIGIN + '/#kmgh', path
    for host in ('www.kmuh.org.tw', 'www.kmugh.org.tw'):
        assert any(urlsplit(url).hostname == host and parse_qs(urlsplit(url).query).get('doctorID') == ['1080224'] for url in person['sameAs']), path
    assert all(item.get('@type') != 'ScholarlyArticle' for item in person.get('subjectOf', [])), path
    if path != 'index.html':
        visible = ''.join(VisiblePage(source).text)
        assert all(term in visible for term in ('張庭瑋', 'Ting-Wei Chang')), path

for path in ('thoracic/index.html', 'bariatric/index.html', 'esophageal/index.html', 'en/index.html'):
    source = (ROOT / path).read_text()
    page = VisiblePage(source)
    bookings = [a for a in page.links if a.get('data-booking')]
    expected_hosts = ['www.kmuh.org.tw'] if path.startswith('bariatric/') else ['www.kmuh.org.tw', 'www.kmugh.org.tw']
    for host in expected_hosts:
        assert any(urlsplit(a['href']).hostname == host for a in bookings), path
    for a in bookings:
        parsed = urlsplit(a['href'])
        assert parsed.scheme == 'https' and parsed.hostname in expected_hosts, path
        assert '/RegStep' not in parsed.path, path
    if not path.startswith('en/'):
        assert 'id="consultation-guide"' in source, path
    assert any('/appointment/' in a.get('href', '') for a in page.links), path

for slug in ('pulmonary-nodules-follow-up', 'low-dose-ct-lung-screening', 'bariatric-weight-regain', 'reflux-hiatal-hernia'):
    path = 'articles/' + slug + '.html'
    source = (ROOT / path).read_text()
    card = re.search(r'<section class="clinician-context".*?</section>', source, re.S).group(0)
    visible = ''.join(VisiblePage(card).text)
    assert all(term in visible for term in ('張庭瑋', 'Ting-Wei Chang', '高醫本院', '高醫岡山')), path
    graph = json.loads(re.search(r'<script type="application/ld\+json" data-clinician-identity>(.*?)</script>', source, re.S).group(1))
    assert graph['@id'] == PHYSICIAN and graph['name'] == '張庭瑋', path
    assert graph['identifier']['value'] == '1080224', path
    for host in ('www.kmuh.org.tw', 'www.kmugh.org.tw'):
        assert any(urlsplit(a.get('href', '')).hostname == host and parse_qs(urlsplit(a['href']).query).get('doctorID') == ['1080224'] for a in VisiblePage(card).links), path
    assert len(re.findall(r'id="clinician-context"', source)) == 1, path

# Internal validation notes belong in private working records, not patient copy.
# The physician ID must remain in JSON-LD and official URLs above, not in prose.
internal_copy = (
    '1080224', '身分來源核對', '此日期不代表臨床內容重新審閱',
    '降低中英文實體混淆', '交叉核對', '未提供未核實', '不引用未核對',
    '本頁不由題名推算', '未轉載原文全文', '清楚標示紀錄的性質',
    '本文不提供未經確認',
    'Cross-check', 'cross-checked', 'Identity sources checked',
    'These public sources help distinguish',
)
checked = 0
for file in ROOT.rglob('*.html'):
    if any(part.startswith('.') for part in file.relative_to(ROOT).parts) or file.name.startswith('google'):
        continue
    page = VisiblePage(file.read_text())
    visible = ''.join(page.text)
    assert not any(term in visible for term in internal_copy), str(file.relative_to(ROOT))
    source = file.read_text()
    if 'class="mobile-cta"' in source and file.relative_to(ROOT).as_posix() != 'en/index.html':
        assert re.search(r'<a class="mobile-cta"[^>]*>\s*門診時間與掛號\s*</a>', source), str(file.relative_to(ROOT))
    assert '食道癌還有救嗎' not in source, str(file.relative_to(ROOT))
    for link in page.links:
        parsed = urlsplit(link.get('href', ''))
        assert '/Registration/RegStep' not in parsed.path, f'Dated booking URL: {file}'
        key = link.get('data-booking')
        if key:
            assert key in BOOKING_ROUTES, f'Unknown booking route: {key} in {file}'
            host, route, query = BOOKING_ROUTES[key]
            assert parsed.scheme == 'https' and parsed.hostname == host, str(file)
            assert parsed.path == route and parse_qs(parsed.query) == query, str(file)
            assert not parsed.fragment, str(file)
    checked += 1

appointment = (ROOT / 'appointment/index.html').read_text()
for section in ('thoracic', 'bariatric', 'gangshan'):
    assert f'href="#{section}"' in appointment and f'id="{section}"' in appointment, section
for path in ('publications/index.html', 'media/index.html'):
    source = (ROOT / path).read_text()
    assert '<section class="final-cta"' in source and 'href="../appointment/"' in source, path

regain = (ROOT / 'articles/bariatric-weight-regain.html').read_text()
faq_html = re.search(r'<section id="questions".*?</section>', regain, re.S).group(0)
faq = json.loads(re.search(r'<script type="application/ld\+json" data-patient-faq>(.*?)</script>', regain, re.S).group(1))
pairs = re.findall(r'<details><summary>(.*?)</summary><p>(.*?)</p></details>', faq_html, re.S)
assert len(pairs) == len(faq['mainEntity']) == 4
for (question, answer), entity in zip(pairs, faq['mainEntity']):
    assert entity['name'] == question and entity['acceptedAnswer']['text'] == answer
assert all(f'id="{part}"' in regain for part in ('when', 'options', 'revision', 'prepare', 'questions'))
assert '外科減重' in appointment and 'QuickPassReserve?FormType=Weight' in appointment

print(f'PASS: 3 physician identity graphs, 4 care/booking pages, 4 article identity/source cards, official hospital destinations, {checked} pages free of internal editorial notes.')
print('PASS: consistent mobile booking labels, appointment shortcuts, and publication/media booking prompts.')
print('PASS: all booking buttons use verified evergreen routes; no dated RegStep links; 4 visible answers match FAQ structured data.')
