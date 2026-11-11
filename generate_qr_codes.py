"""
Printed-material QR code generator — reads qr-codes.json and, for every
active entry, writes:
  - {folder}/{id}.html      short redirect page (QR target: timemachinetours.fr/{folder}/{id})
  - {folder}/qr/{ID}.png    QR code for that page (raster, ~1500px)
  - {folder}/qr/{ID}.svg    same QR code as vector (best for print / Canva)

Supported types (folder = first letter of the id):
  type     folder  utm_source  utm_medium   example
  poster   h/      hostel      poster       H01 → /h/h01  (hostel posters)
  flyer    f/      handout     flyer        F01 → /f/f01
  card     c/      handout     card         C01 → /c/c01  (business cards)

Each redirect page:
  - pushes a 'qr_scan' event to GTM's dataLayer (qr_id, qr_type, label)
  - stores the id in sessionStorage (poster_id = id, tour_source = type)
  - redirects to `destination` with utm_source, utm_medium,
    utm_campaign={id} and ref={id} appended

index.html then forwards ref + utm_* to every JustGuide booking link.

Change `destination` to retarget a printed code (e.g. "/book/paris-time-machine")
and re-run this script: the QR code itself never changes.

Usage:
    pip install qrcode pillow
    python generate_qr_codes.py
"""

import json
import re
from pathlib import Path
from urllib.parse import urlencode

CONFIG_FILE = Path('qr-codes.json')
SITE        = 'https://timemachinetours.fr'

TYPES = {
    'poster': {'folder': 'h', 'utm_source': 'hostel',  'utm_medium': 'poster'},
    'flyer':  {'folder': 'f', 'utm_source': 'handout', 'utm_medium': 'flyer'},
    'card':   {'folder': 'c', 'utm_source': 'handout', 'utm_medium': 'card'},
}

TEMPLATE = """\
<!DOCTYPE html>
<html lang="en">
<head>
  <!-- Google Tag Manager -->
  <script>(function(w,d,s,l,i){{w[l]=w[l]||[];w[l].push({{'gtm.start':
    new Date().getTime(),event:'gtm.js'}});var f=d.getElementsByTagName(s)[0],
    j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;j.src=
    'https://www.googletagmanager.com/gtm.js?id='+i+dl;f.parentNode.insertBefore(j,f);
    }})(window,document,'script','dataLayer','GTM-5B56HBZC');</script>
  <!-- End Google Tag Manager -->

  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <meta name="robots" content="noindex, nofollow">
  <meta http-equiv="refresh" content="0;url={url}">
  <title>Time Machine Tours</title>
  <script>
    try {{
      sessionStorage.setItem('tour_source', '{type}');
      sessionStorage.setItem('poster_id', '{id}');
    }} catch (e) {{}}
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({{
      event:   'qr_scan',
      qr_id:   '{id}',
      qr_type: '{type}',
      label:   {label_js},
    }});
    window.location.replace('{url}');
  </script>
</head>
<body>
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5B56HBZC"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>
  <p style="font-family:sans-serif;padding:2rem;text-align:center;">
    <a href="{url}">Time Machine Tours →</a>
  </p>
</body>
</html>
"""


def make_qr(data, out_png):
    import qrcode
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=40, border=4)  # ~1500px: sharp at A4 size
    qr.add_data(data)
    qr.make(fit=True)
    qr.make_image(fill_color='black', back_color='white').save(out_png)

    # Vector version: one horizontal stroke per run of dark modules.
    m = qr.get_matrix()
    n = len(m)
    d = []
    for y, row in enumerate(m):
        x = 0
        while x < n:
            if row[x]:
                s = x
                while x < n and row[x]:
                    x += 1
                d.append(f'M{s} {y}h{x - s}')
            else:
                x += 1
    svg = (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {n} {n}" '
           f'width="1000" height="1000" shape-rendering="crispEdges">'
           f'<rect width="{n}" height="{n}" fill="#fff"/>'
           f'<path stroke="#000" transform="translate(0 .5)" d="{"".join(d)}"/></svg>\n')
    out_png.with_suffix('.svg').write_text(svg, encoding='utf-8')


def main():
    entries = json.loads(CONFIG_FILE.read_text(encoding='utf-8'))

    for e in entries:
        cid = e['id'].lower()
        if not e.get('active', True):
            print(f'  [skip] {cid} (inactive)')
            continue
        t = TYPES[e['type']]
        if not re.fullmatch(t['folder'] + r'\d{2,}', cid):
            raise SystemExit(f"{cid}: id must start with '{t['folder']}' for type {e['type']}")

        folder = Path(t['folder'])
        (folder / 'qr').mkdir(parents=True, exist_ok=True)

        dest = e.get('destination', '/')
        sep = '&' if '?' in dest else '?'
        url = dest + sep + urlencode({
            'utm_source': t['utm_source'], 'utm_medium': t['utm_medium'],
            'utm_campaign': cid, 'ref': cid,
        })
        html = TEMPLATE.format(id=cid, type=e['type'], url=url,
                               label_js=json.dumps(e.get('label', '')))
        (folder / f'{cid}.html').write_text(html, encoding='utf-8')
        make_qr(f'{SITE}/{t["folder"]}/{cid}', folder / 'qr' / f'{cid.upper()}.png')
        print(f'  [ok] {folder}/{cid}.html  ->  {url}')

    print('Done.')


if __name__ == '__main__':
    main()
