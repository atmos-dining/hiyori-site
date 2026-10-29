#!/usr/bin/env python3
"""Create the Pages artifact from an explicit list of public website assets."""
import os, re, shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
OUT = ROOT / '_site'
if OUT.exists():
    shutil.rmtree(OUT)
OUT.mkdir()
for name in ('index.html', 'menu.html', 'drink.html', 'space.html', 'access.html', 'privacy.html',
             'style.css', 'common.js', 'site-paths.js', 'favicon.svg', 'robots.txt', '.nojekyll'):
    shutil.copy2(ROOT / name, OUT / name)
for name in ('sitemap.xml', 'CNAME'):
    if (ROOT / name).is_file():
        shutil.copy2(ROOT / name, OUT / name)
for name in ('blog', 'images', 'videos', 'vendor'):
    shutil.copytree(ROOT / name, OUT / name, ignore=shutil.ignore_patterns('._*', '.DS_Store', '__pycache__'))
(OUT / 'admin').mkdir()
for name in ('index.html', 'config.yml'):
    shutil.copy2(ROOT / 'admin' / name, OUT / 'admin' / name)
# The CMS reads repository-relative image paths; keep /images stable across domains.
site_url = os.environ.get('SITE_URL', '').rstrip('/')
if site_url:
    from urllib.parse import urlsplit
    base_path = urlsplit(site_url).path.rstrip('/')
    p = OUT / 'admin/index.html'
    p.write_text(p.read_text().replace('name="site-base-path" content=""', f'name="site-base-path" content="{base_path}"'))
    p = OUT / 'admin/config.yml'
    p.write_text(re.sub(r'^(site_url|display_url):.*$', lambda m: f'{m.group(1)}: {site_url}', p.read_text(), flags=re.M))
print('Packaged public assets in _site (source, instructions and local settings excluded)')
