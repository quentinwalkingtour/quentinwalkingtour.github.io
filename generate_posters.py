"""
Hostel poster redirect generator — reads h/posters.json and writes:
  - h/{id}.html      short redirect page (QR target: timemachinetours.fr/h/{id})
  - h/qr/{ID}.png    print-ready QR code for that page

Each redirect page:
  - pushes a 'poster_scan' event to GTM's dataLayer (poster_id, hostel)
  - stores the poster id in sessionStorage (tour_source='poster', poster_id)
  - redirects to `destination` with utm_source=hostel, utm_medium=poster,
    utm_campaign={id} and ref={id} appended

The mapping id -> hostel lives in the "Affiches auberges" Google Sheet; the
`hostel` field here is optional. Change `destination` to retarget a poster
after printing (e.g. "/book/paris-time-machine"), then re-run this script.

Usage:
    pip install qrcode pillow
    python generate_posters.py
"""

import json
from pathlib import Path
from urllib.parse import urlencode

POSTERS_FILE = Path('h/posters.json')
OUTPUT_DIR   = Path('h')
QR_DIR       = OUTPUT_DIR / 'qr'
SITE         = 'https://timemachinetours.fr'

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
      sessionStorage.setItem('tour_source', 'poster');
      sessionStorage.setItem('poster_id', '{id}');
    }} catch (e) {{}}
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({{
      event:     'poster_scan',
      poster_id: '{id}',
      hostel:    {hostel_js},
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


def make_qr(data, out):
    import qrcode
    qr = qrcode.QRCode(error_correction=qrcode.constants.ERROR_CORRECT_M,
                       box_size=40, border=4)  # ~1500px: sharp at A4 size
    qr.add_data(data)
    qr.make(fit=True)
    qr.make_image(fill_color='black', back_color='white').save(out)


def main():
    QR_DIR.mkdir(parents=True, exist_ok=True)
    posters = json.loads(POSTERS_FILE.read_text(encoding='utf-8'))

    for p in posters:
        pid = p['id'].lower()
        if not p.get('active', True):
            print(f'  [skip] {pid} (inactive)')
            continue
        dest = p.get('destination', '/')
        sep = '&' if '?' in dest else '?'
        url = dest + sep + urlencode({
            'utm_source': 'hostel', 'utm_medium': 'poster',
            'utm_campaign': pid, 'ref': pid,
        })
        html = TEMPLATE.format(id=pid, url=url,
                               hostel_js=json.dumps(p.get('hostel', '')))
        (OUTPUT_DIR / f'{pid}.html').write_text(html, encoding='utf-8')
        make_qr(f'{SITE}/h/{pid}', QR_DIR / f'{pid.upper()}.png')
        print(f'  [ok] h/{pid}.html  ->  {url}')

    print('Done.')


if __name__ == '__main__':
    main()
