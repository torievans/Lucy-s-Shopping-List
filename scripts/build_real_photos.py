#!/usr/bin/env python3
"""
Rebuild the REAL_PHOTOS block for picture-quest.html from scripts/manifest.json
and scripts/images/*.jpg, then splice it into ../picture-quest.html in place.

Usage:
    python3 scripts/build_real_photos.py

After editing scripts/manifest.json (e.g. adding/removing/renaming items) and
scripts/images/*.jpg to match, re-run this to regenerate the app.
"""
import re
import json
import base64
import os

HERE = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(HERE)
MANIFEST_PATH = os.path.join(HERE, "manifest.json")
IMAGES_DIR = os.path.join(HERE, "images")
APP_PATH = os.path.join(REPO_ROOT, "picture-quest.html")

IRREGULAR_SINGULAR = {
    "leaves": "leaf", "loaves": "loaf", "knives": "knife", "batteries": "battery",
    "cherries": "cherry", "strawberries": "strawberry", "blueberries": "blueberry",
    "raspberries": "raspberry", "potatoes": "potato", "tomatoes": "tomato",
    "boxes": "box", "dresses": "dress", "brushes": "brush", "watches": "watch",
    "footprints": "footprint", "glasses": "glass", "people": "person", "children": "child",
}


def singularize(w):
    if w in IRREGULAR_SINGULAR:
        return IRREGULAR_SINGULAR[w]
    if re.search(r"[a-z]ies$", w):
        return w[:-3] + "y"
    if re.search(r"(sh|ch|ss|x|s)es$", w):
        return w[:-2]
    if re.search(r"[a-z]s$", w) and not w.endswith("ss"):
        return w[:-1]
    return w


def js_str(s):
    return json.dumps(s)


def build_real_photos_block():
    with open(MANIFEST_PATH, encoding="utf-8") as f:
        manifest = json.load(f)

    entries = []
    for m in manifest:
        phrase = m["simple_name"].strip().lower()
        words = phrase.split()
        tokens = set(words)
        for w in words:
            tokens.add(singularize(w))
        tokens.add(phrase)
        with open(os.path.join(IMAGES_DIR, m["file"]), "rb") as imgf:
            b64 = base64.b64encode(imgf.read()).decode("ascii")
        entries.append({
            "name": m["full_name"],
            "phrase": phrase,
            "tokens": sorted(tokens),
            "dataUri": "data:image/jpeg;base64," + b64,
        })

    parts = []
    for e in entries:
        tokens_js = "[" + ",".join(js_str(t) for t in e["tokens"]) + "]"
        parts.append("{name:%s,phrase:%s,tokens:%s,img:%s}" % (
            js_str(e["name"]), js_str(e["phrase"]), tokens_js, js_str(e["dataUri"])
        ))

    block = "var REAL_PHOTOS = [\n" + ",\n".join(parts) + "\n];\n"
    block += """
var REAL_PHOTOS_BY_PHRASE = {};
var REAL_PHOTOS_BY_TOKEN = {};
REAL_PHOTOS.forEach(function(p){
  if (!(p.phrase in REAL_PHOTOS_BY_PHRASE)) REAL_PHOTOS_BY_PHRASE[p.phrase] = p;
  p.tokens.forEach(function(t){
    if (t.indexOf(" ") > -1) return;
    (REAL_PHOTOS_BY_TOKEN[t] = REAL_PHOTOS_BY_TOKEN[t] || []).push(p);
  });
});
"""
    return block, len(entries)


def splice_into_app(block):
    with open(APP_PATH, encoding="utf-8") as f:
        html = f.read()

    start_marker = "/* ---- Real product photos (from Tori's Morrisons basket) ---- */\n  "
    end_marker = "var STOP_PREFIXES"

    start_idx = html.index(start_marker) + len(start_marker)
    end_idx = html.index(end_marker, start_idx)

    html = html[:start_idx] + block + "\n\n  " + html[end_idx:]

    with open(APP_PATH, "w", encoding="utf-8") as f:
        f.write(html)


if __name__ == "__main__":
    block, count = build_real_photos_block()
    splice_into_app(block)
    print("Rebuilt picture-quest.html with %d real product photos." % count)
