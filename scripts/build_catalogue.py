#!/usr/bin/env python3
"""
Rebuild ../basket-photo-library.html (the image grid + filter) from
scripts/manifest.json and scripts/images/*.jpg.

Usage:
    python3 scripts/build_catalogue.py
"""
import json
import base64
import html
import os
import re

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
MANIFEST_PATH = os.path.join(HERE, "manifest.json")
IMAGES_DIR = os.path.join(HERE, "images")
CATALOGUE_PATH = os.path.join(REPO_ROOT, "basket-photo-library.html")


def esc(s):
    return html.escape(s.strip())


def build_cards():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)
    manifest.sort(key=lambda m: m["simple_name"].lower())

    cards = []
    for m in manifest:
        with open(os.path.join(IMAGES_DIR, m["file"]), "rb") as f:
            b64 = base64.b64encode(f.read()).decode("ascii")
        cards.append(
            '<figure class="card">'
            '<div class="thumb"><img src="data:image/jpeg;base64,' + b64 + '" alt="' + esc(m["full_name"]) + '" loading="lazy" /></div>'
            '<figcaption><code class="filename">' + esc(m["file"]) + '</code><span class="fullname">' + esc(m["full_name"]) + '</span></figcaption>'
            '</figure>'
        )
    return "\n".join(cards), len(manifest)


if __name__ == "__main__":
    cards_html, count = build_cards()

    with open(CATALOGUE_PATH, encoding="utf-8") as f:
        page = f.read()

    page = re.sub(
        r'(<div class="grid" id="grid">\n).*?(\n</div>)',
        lambda m: m.group(1) + cards_html + m.group(2),
        page, flags=re.S,
    )
    page = re.sub(r'(<span class="count">)\d+(</span>)', r"\g<1>" + str(count) + r"\g<2>", page)

    with open(CATALOGUE_PATH, "w", encoding="utf-8") as f:
        f.write(page)

    print("Rebuilt basket-photo-library.html with %d photos." % count)
