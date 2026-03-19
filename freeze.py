"""
freeze.py — Generates a static build of the Flask app using Flask's test client.

Pages generated:
  /          → build/index.html
  /menu      → build/menu.html
  /cart      → build/cart.html
  /booking   → build/booking.html

Static assets are copied from static/ → build/static/
"""

import os
import re
import shutil
from app import app

BUILD_DIR = 'build'

# Routes to render and their output filenames
PAGES = [
    ('/', 'index.html'),
    ('/menu', 'menu.html'),
    ('/cart', 'cart.html'),
    ('/booking', 'booking.html'),
]

# Internal link rewrites: Flask path → static .html filename
LINK_MAP = {
    'href="/"': 'href="index.html"',
    "href='/'": "href='index.html'",
    'href="/menu"': 'href="menu.html"',
    'href="/cart"': 'href="cart.html"',
    'href="/booking"': 'href="booking.html"',
}

def fix_links(html):
    for old, new in LINK_MAP.items():
        html = html.replace(old, new)
    # Fix static file paths: /static/... → static/...
    html = re.sub(r'(href|src)="/static/', r'\1="static/', html)
    return html


def generate():
    os.makedirs(BUILD_DIR, exist_ok=True)

    # Render each page
    with app.test_client() as client:
        for route, filename in PAGES:
            response = client.get(route)
            html = response.data.decode('utf-8')
            html = fix_links(html)
            output_path = os.path.join(BUILD_DIR, filename)
            with open(output_path, 'w', encoding='utf-8') as f:
                f.write(html)
            print(f"  Generated: {output_path}")

    # Copy static assets
    static_src = 'static'
    static_dst = os.path.join(BUILD_DIR, 'static')
    if os.path.exists(static_dst):
        shutil.rmtree(static_dst)
    shutil.copytree(static_src, static_dst)
    print(f"  Copied:    {static_dst}/")

    print("\nStatic build complete -> build/")


if __name__ == '__main__':
    generate()
