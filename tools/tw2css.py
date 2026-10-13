"""Convert Figma design-context JSX (Tailwind) subtrees into plain HTML with inline CSS."""
import re, sys

def px(v):
    v = v.replace('_', ' ')
    if v.startswith('calc('):
        v = re.sub(r'(?<=[\d%)])([+-])(?=[\d(])', r' \1 ', v)
    return v

def conv(cls):
    st = {}; tf = {'translate': [], 'rotate': None, 'scale': None, 'skew': None}
    for c in cls.split():
        m = re.match(r'^(-?)(h|w|left|top|right|bottom|size)-\[(.+)\]$', c)
        if m:
            k = {'h': 'height', 'w': 'width', 'size': 'size'}.get(m[2], m[2])
            v = px(m[3])
            if k == 'size': st['width'] = st['height'] = v
            else: st[k] = v
            continue
        if c == 'size-full': st['width'] = st['height'] = '100%'; continue
        if c in ('absolute', 'relative'): st['position'] = c; continue
        if c == 'flex': st['display'] = 'flex'; continue
        if c == 'contents': st['display'] = 'contents'; continue
        if c == 'block': st['display'] = 'block'; continue
        if c == 'items-center': st['align-items'] = 'center'; continue
        if c == 'justify-center': st['justify-content'] = 'center'; continue
        if c == 'flex-none': st['flex'] = 'none'; continue
        if c == 'inset-0': st['inset'] = '0'; continue
        m = re.match(r'^inset-\[(.+)\]$', c)
        if m: st['inset'] = px(m[1]); continue
        m = re.match(r'^rotate-\[(.+)\]$', c)
        if m: tf['rotate'] = m[1]; continue
        m = re.match(r'^(-?)scale-y-(\d+)$', c)
        if m: tf['scale'] = f"1,{'-' if m[1] else ''}{int(m[2])/100}"; continue
        m = re.match(r'^skew-x-\[(.+)\]$', c)
        if m: tf['skew'] = m[1]; continue
        m = re.match(r'^bg-\[(.+)\]$', c)
        if m: st['background'] = m[1]; continue
        if c == 'border': st['border-width'] = '1px'; continue
        if c == 'border-solid': st['border-style'] = 'solid'; continue
        if c == 'border-white': st['border-color'] = '#fff'; continue
        if c == 'border-black': st['border-color'] = '#000'; continue
        if c == 'max-w-none': st['max-width'] = 'none'; continue
        if c in ('content-stretch',): continue
        print('UNHANDLED', c, file=sys.stderr)
    parts = []
    if tf['rotate']: parts.append(f"rotate({tf['rotate']})")
    # Figma emits Tailwind v3 order: rotate → skew → scale
    if tf['skew']: parts.append(f"skewX({tf['skew']})")
    if tf['scale']: parts.append(f"scale({tf['scale']})")
    if parts: st['transform'] = ' '.join(parts)
    return ';'.join(f'{k}:{v}' for k, v in st.items())

def extract(text, node_id):
    i = text.index(f'data-node-id="{node_id}"')
    start = text.rindex('<', 0, i)
    depth = 0; pos = start
    for m in re.finditer(r'<(/?)(\w+)([^>]*?)(/?)>', text[start:]):
        closing, selfclose = m[1], m[4]
        if not closing and not selfclose: depth += 1
        elif closing: depth -= 1
        if depth == 0:
            return text[start:start + m.end()]
    raise ValueError(node_id)

def to_html(jsx, img_map):
    def tag(m):
        closing, name, attrs, selfclose = m[1], m[2], m[3], m[4]
        if closing: return f'</{ "div" if name in ("a","button") else name}>'
        name = 'div' if name in ('a', 'button') else name
        cls = re.search(r'className="([^"]*)"', attrs)
        src = re.search(r'src=\{(\w+)\}', attrs)
        out = f'<{name}'
        if cls and conv(cls[1]): out += f' style="{conv(cls[1])}"'
        if src: out += f' src="{img_map[src[1]]}" alt=""'
        if name == 'img': return out + '>'
        return out + ('></div>' if selfclose else '>')
    return re.sub(r'<(/?)(\w+)([^>]*?)(/?)>', tag, jsx)
