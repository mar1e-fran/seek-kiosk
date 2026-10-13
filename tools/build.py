"""Inline the converted furniture partials into the page: src/index.template.html -> index.html"""
from pathlib import Path
root = Path(__file__).resolve().parent.parent
html = (root / 'src/index.template.html').read_text()
for key in ('F1', 'F2', 'F3'):
    part = (root / f'tools/furniture-{key.lower()}.html').read_text()
    html = html.replace('{{%s}}' % key, ' '.join(part.split()))
# QR generator (qrcode-generator 1.4.4, MIT) inlined so the embed has no runtime dependencies
html = html.replace('/*__QR__*/', (root / 'src/vendor/qrcode.min.js').read_text())
(root / 'index.html').write_text(html)
print('index.html', len(html), 'bytes')

# Single-file embed: every assets/*.svg inlined as a data URI
import base64, re
def inline(m):
    data = (root / m[1]).read_bytes()
    return 'data:image/svg+xml;base64,' + base64.b64encode(data).decode()
single = re.sub(r'(assets/[\w-]+\.svg)', inline, html)
(root / 'dist').mkdir(exist_ok=True)
(root / 'dist/seek-kiosk.html').write_text(single)
print('dist/seek-kiosk.html', len(single), 'bytes')
