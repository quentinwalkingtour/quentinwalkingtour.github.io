"""
Redirect generator — reads go/redirects.json and writes go/{slug}.html
for every active entry.

Each generated page:
  - Instantly redirects via <meta http-equiv="refresh">
  - Falls back to window.location.replace() via JS
  - Has a visible <noscript> link
  - Pushes a GTM dataLayer event for click tracking

Usage:
    python generate_redirects.py
"""

import json
from pathlib import Path

REDIRECTS_FILE = Path('go/redirects.json')
OUTPUT_DIR     = Path('go')

REDIRECT_TEMPLATE = """\
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
  <title>Redirecting… | Paris Time Machine</title>
  <script>
    window.dataLayer = window.dataLayer || [];
    window.dataLayer.push({{
      event:         'affiliate_redirect',
      redirect_slug: '{slug}',
      platform:      '{platform}',
    }});
    window.location.replace('{url}');
  </script>
</head>
<body>
  <!-- Google Tag Manager (noscript) -->
  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=GTM-5B56HBZC"
    height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>

  <p style="font-family:sans-serif;padding:2rem;text-align:center;">
    Redirecting… <a href="{url}">Click here if nothing happens</a>.
  </p>
</body>
</html>
"""


def main():
    OUTPUT_DIR.mkdir(exist_ok=True)

    redirects = json.loads(REDIRECTS_FILE.read_text(encoding='utf-8'))

    generated = 0
    for r in redirects:
        if not r.get('active', True):
            print(f'  [skip] {r["slug"]} (inactive)')
            continue

        html = REDIRECT_TEMPLATE.format(
            slug     = r['slug'],
            platform = r.get('platform', 'unknown'),
            url      = r['url'],
            title    = r.get('title', r['slug']),
        )

        out = OUTPUT_DIR / f"{r['slug']}.html"
        out.write_text(html, encoding='utf-8')
        print(f'  [ok] {out}')
        generated += 1

    print(f'Done — {generated} redirect(s) generated.')


if __name__ == '__main__':
    main()
