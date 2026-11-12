"""
Descarga las fotos de demo (Unsplash, licencia libre: https://unsplash.com/license) a demo_assets/images/.
Solo hace falta ejecutarlo si querés regenerar las imágenes; ya están incluidas en el repositorio.

    python demo_assets/fetch_assets.py
"""
import json
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parent
OUT = ROOT / 'images'
OUT.mkdir(exist_ok=True)

catalog = json.loads((ROOT / 'catalog.json').read_text(encoding='utf-8'))
wanted = {}
for p in catalog['products']:
    for img in p['images']:
        wanted[img] = (1000, 750)
for s in catalog['shops']:
    wanted[s['banner']] = (1600, 440)

for name, (w, h) in sorted(wanted.items()):
    dest = OUT / name
    if dest.exists():
        continue
    photo_id = name.rsplit('.', 1)[0]
    url = f'https://images.unsplash.com/photo-{photo_id}?w={w}&h={h}&fit=crop&crop=entropy&q=78&fm=jpg'
    req = urllib.request.Request(url, headers={'User-Agent': 'MultiMarketDemo/1.0'})
    dest.write_bytes(urllib.request.urlopen(req, timeout=30).read())
    print('ok', name)
