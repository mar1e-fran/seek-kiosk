"""Build the 3D kiosk: kiosk-3d/src/*.template.html -> kiosk-3d/index.html + kiosk-3d/screen.html

Self-contained: the screen is a single file (assets, QR generator and logo inlined),
and the 3D page mounts it on the kiosk via <iframe src="screen.html?bare">.
Shares assets/, src/vendor/ and tools/furniture-*.html with the interface build.
"""
import base64, re
from pathlib import Path

here = Path(__file__).resolve().parent
root = here.parent

screen = (here / 'src/screen.template.html').read_text()
logo = (root / 'assets/logo.svg').read_text()
screen = screen.replace('{{LOGO_SVG}}', logo[logo.index('<svg'):].replace('<svg ', '<svg class="still-mark" aria-hidden="true" ', 1))
for key in ('F1', 'F2', 'F3'):
    screen = screen.replace('{{%s}}' % key, ' '.join((root / f'tools/furniture-{key.lower()}.html').read_text().split()))
screen = screen.replace('/*__QR__*/', (root / 'src/vendor/qrcode.min.js').read_text())
uri = lambda p: 'data:image/svg+xml;base64,' + base64.b64encode((root / p).read_bytes()).decode()
screen = re.sub(r'(assets/[\w-]+\.svg)', lambda m: uri(m[1]), screen)
(here / 'screen.html').write_text(screen)

kiosk = (here / 'src/kiosk.template.html').read_text()
kiosk = kiosk.replace('{{SCREEN_SRC}}', 'screen.html?bare')
(here / 'index.html').write_text(kiosk)
print('kiosk-3d/index.html + kiosk-3d/screen.html')
