"""Build the SEEK interface: src/index.template.html -> index.html + dist/seek-kiosk.html

The template is written in Figma design px (a 2100 × 3536 kiosk). The build renders the kiosk at
K × that size: px inside /*@kiosk*/ CSS blocks, inline style="" attributes and the furniture partials
are multiplied by K, and the script reads K for the few px it writes. A smaller real layout means
phones never allocate full-size layers when things animate (that is what crashed mobile Safari).
"""
import base64
import re
from pathlib import Path

K = 0.25
root = Path(__file__).resolve().parent.parent
PX = re.compile(r'(?<![\w.#-])(-?\d*\.?\d+)px')


def scale_px(text):
    return PX.sub(lambda m: f'{round(float(m[1]) * K, 4):g}px', text)


def scale_css(css):
    # leave @media conditions (viewport px) alone
    parts = re.split(r'(@media[^{]*\{)', css)
    return ''.join(p if p.startswith('@media') else scale_px(p) for p in parts)


html = (root / 'src/index.template.html').read_text()

# 1. kiosk CSS
html = re.sub(r'/\*@kiosk\*/(.*?)/\*@end-kiosk\*/', lambda m: scale_css(m[1]), html, flags=re.S)

# 2. inline styles in the markup (not inside scripts) + furniture partials
head, body = html.split('</style>', 1)
markup, scripts = body.split('<script>', 1)
markup = re.sub(r'style="([^"]*)"', lambda m: f'style="{scale_px(m[1])}"', markup)
for key in ('F1', 'F2', 'F3'):
    part = ' '.join((root / f'tools/furniture-{key.lower()}.html').read_text().split())
    markup = markup.replace('{{%s}}' % key, re.sub(r'style="([^"]*)"', lambda m: f'style="{scale_px(m[1])}"', part))
html = head + '</style>' + markup + '<script>' + scripts

# 3. script scale + QR generator (qrcode-generator 1.4.4, MIT), inlined so there are no runtime deps
html = html.replace('/*__K__*/1', str(K))
html = html.replace('/*__QR__*/', (root / 'src/vendor/qrcode.min.js').read_text())
(root / 'index.html').write_text(html)
print('index.html', len(html), 'bytes')

# Single-file embed: every assets/*.svg inlined as a data URI
single = re.sub(r'(assets/[\w-]+\.svg)',
                lambda m: 'data:image/svg+xml;base64,' + base64.b64encode((root / m[1]).read_bytes()).decode(), html)
(root / 'dist').mkdir(exist_ok=True)
(root / 'dist/seek-kiosk.html').write_text(single)
print('dist/seek-kiosk.html', len(single), 'bytes')
