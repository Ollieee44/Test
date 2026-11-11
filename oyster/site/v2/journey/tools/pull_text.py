"""Pull the words saved in a live page (its Edit text panel) into the repo, so the build's version of record carries them.
Reads a saved copy of the published page (the Artifact tool's read writes one), takes its #c2text data block, checks its
shape, and writes it as JSON; the build applies it in place of its default words for that page.
Usage: python pull_text.py <saved page.html> <journey/text/clickN.json>"""
import json, re, sys
src, dst = sys.argv[1:3]
html = open(src, encoding='utf8').read()
m = re.search(r'<script type="application/json" id="c2text">(.*?)</script>', html, re.S)
if not m: sys.exit('no text block (#c2text) in ' + src)
T = json.loads(m.group(1))
assert isinstance(T.get('sections'), list) and all(set(s) == {'title', 'label', 'heading', 'body'} and all(isinstance(v, str) for v in s.values()) for s in T['sections'])
assert isinstance(T.get('tagline'), list) and len(T['tagline']) == 2 and all(isinstance(v, str) for v in T['tagline'])
json.dump(T, open(dst, 'w', encoding='utf8'), ensure_ascii=False, indent=1)
print(dst, len(T['sections']), 'sections')
