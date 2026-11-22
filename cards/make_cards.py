"""Generates the terminal-style project cards in cards/dark/ and cards/light/ (one SVG each).

    GITHUB_TOKEN=... python3 cards/make_cards.py

Each card is a thin terminal-style frame with the project name cut into its top edge, then the
description and a details line with the platform, the latest release, the size of its download
and the stars (shown once there are any), read from GitHub. The languages workflow runs this daily,
so releases and stars stay current. README.md links each card to its repository.
"""
import json
import os
import urllib.error
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
USER = "mttfntn"
COLS = 46           # characters per line, borders included
CHAR_W = 8.4        # width of one character in SVG units (each line is stretched to fit exactly)
LINE_H = 21
PAD = 14
FONT = "ui-monospace, SFMono-Regular, Menlo, Consolas, 'DejaVu Sans Mono', 'Liberation Mono', monospace"

# card file, repository, name, description, details, accent color
PROJECTS = [
    ("sanzo-wada-colors", "sanzo-wada-colors-blender", "sanzo-wada-colors",
     "a 1930s color dictionary, now in your shader editor.", "blender", "#E87D0D"),
    ("shrinkpatch", "shrinkpatch-blender", "shrinkpatch",
     "stick details onto any surface. no seams, no fuss.", "blender", "#E87D0D"),
    ("driver-controller", "driver-controller-blender", "driver-controller",
     "all your drivers, one panel.", "blender", "#E87D0D"),
    ("checklist-tool", "checklist-tool-blender", "checklist-tool",
     "a to-do list that lives inside the .blend.", "blender", "#E87D0D"),
    ("resource-safeguard", "resource-safeguard-blender", "resource-safeguard",
     "your gpu takes a break when you do.", "blender", "#E87D0D"),
    ("tissue-blender-5", "tissue-blender-5", "tissue-blender-5",
     "alessandro zomparelli's tissue, kept running on 5.3.", "blender", "#E87D0D"),
    ("composition-guides", "composition-guides-blender", "composition-guides",
     "thirds, golden ratio and friends, fitted to your camera.", "blender", "#E87D0D"),
    ("ior-material-list", "ior-material-list-blender", "ior-material-list",
     "every ior value you keep googling, one click away.", "blender", "#E87D0D"),
    ("lut-manager", "lut-manager-blender", "lut-manager",
     "browse your .cube luts, preview them live in the viewport.", "blender", "#E87D0D"),
    ("mesh-analyzer", "mesh-analyzer-blender", "mesh-analyzer",
     "live topology overlay. ngons have nowhere to hide.", "blender", "#E87D0D"),
    ("octane-fast-start", "octane-fast-startup-blender", "octane-fast-start",
     "blender opens fast, even when octane's server is off.", "blender · octane", "#E87D0D"),
    ("solid-snapshot", "snapshot-blender", "solid-snapshot",
     "viewport shots in standard colors, whatever your view transform.", "blender", "#E87D0D"),
    ("transforms-checker", "transforms-checker-blender", "transforms-checker",
     "finds the objects you forgot to apply.", "blender", "#E87D0D"),
    ("unused-data-blocks", "unused-data-blocks-detector-blender", "unused-data-blocks",
     "tells you when your .blend carries dead weight.", "blender", "#E87D0D"),
    ("onefingerrotation", "OneFingerRotation", "onefingerrotation",
     "spin swiftui views with one finger.", "swift · swiftui", "#F05138"),
    ("phone-trackpad", "phone-trackpad", "phone-trackpad",
     "your phone, but it's a trackpad now.", "python · win/mac", "#3776AB"),
]

THEMES = {
    "dark": {"bg": "#0d1117", "border": "#3d444d", "name": "#e6edf3", "text": "#9198a1", "dim": "#656c76"},
    "light": {"bg": "#ffffff", "border": "#c8d1da", "name": "#1f2328", "text": "#59636e", "dim": "#818b98"},
}


def api(path):
    """GET from the GitHub API; None when the thing doesn't exist (e.g. no release yet)."""
    req = urllib.request.Request(f"https://api.github.com/{path}",
                                 headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-cards"})
    if os.environ.get("GITHUB_TOKEN"):
        req.add_header("Authorization", f"Bearer {os.environ['GITHUB_TOKEN']}")
    try:
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:
            return None
        raise


def human_size(n):
    return f"{n / 1024:.1f} KB" if n < 1024 ** 2 else f"{n / 1024 ** 2:.1f} MB"


def wrap(text, width):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def card(name, desc, details, release, size, stars, accent, t, cols=COLS, desc_rows=2, split_meta=False):
    """One card as SVG: a thin terminal-style frame with the name cut into its top edge, the
    description (desc_rows lines, always reserved, so every card of a layout has the same height)
    and the details. All text is monospace. The compact layout (narrow screens) uses fewer
    columns, so its text stays large when the card is shown small, and puts the release on a
    second details line."""
    inner = cols - 6  # text width, with at least one character of margin before the frame
    width = cols * CHAR_W + 2 * PAD
    left, right = PAD + CHAR_W / 2, PAD + (cols - 0.5) * CHAR_W
    top, line0 = PAD + 8, PAD + 8 + LINE_H + 4
    desc_lines = wrap(desc, inner)
    if len(desc_lines) > desc_rows or len(name) > cols - 7:
        raise ValueError(f"{name!r} does not fit a {cols}-column card")
    desc_lines = (desc_lines + [""] * desc_rows)[:desc_rows]
    head, _, rest = details.partition(" · ")
    extra = " · ".join(x for x in (release, size, f"★ {stars}" if stars else None) if x)
    # If the details don't fit, the secondary platform words (e.g. "python") go first.
    stars_text = f"★ {stars}" if stars else None
    for platform in ([" · " + rest] if rest else []) + [""]:
        if split_meta:  # compact: platform / release and size / stars, each on its own line
            meta = [(head, platform), ("", " · ".join(x for x in (release, size) if x)), ("", stars_text or "")]
        else:
            extra = " · ".join(x for x in (release, size, stars_text) if x)
            meta = [(head, platform + (" · " + extra if extra else ""))]
        if all(len(h + tail) <= inner for h, tail in meta):
            break
    else:
        raise ValueError(f"details too long for the card: {head!r} {release!r} {size!r} {stars_text!r}")
    bottom = line0 + (desc_rows + len(meta)) * LINE_H + 2
    height = bottom + PAD
    x_text = PAD + 2 * CHAR_W
    title_w = (len(name) + 2) * CHAR_W
    e = escape
    rows = [f'<text x="{x_text:.1f}" y="{line0 + i * LINE_H:.1f}" fill="{t["text"]}">{e(l)}</text>'
            for i, l in enumerate(desc_lines)]
    y = line0 + desc_rows * LINE_H + 8
    for h, tail in meta:
        rows.append(f'<text x="{x_text:.1f}" y="{y:.1f}" xml:space="preserve"><tspan fill="{accent}">{e(h)}</tspan>'
                    f'<tspan fill="{t["dim"]}">{e(tail)}</tspan></text>')
        y += LINE_H
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">
<style>text {{ font: 14px {FONT}; }}</style>
<rect width="100%" height="100%" fill="{t['bg']}"/>
<rect x="{left:.1f}" y="{top:.1f}" width="{right - left:.1f}" height="{bottom - top:.1f}" fill="none" stroke="{t['border']}" stroke-width="1.2"/>
<rect x="{x_text - CHAR_W:.1f}" y="{top - 3:.1f}" width="{title_w:.1f}" height="6" fill="{t['bg']}"/>
<rect x="{right - 2.6 * CHAR_W:.1f}" y="{top - 3:.1f}" width="{2.2 * CHAR_W:.1f}" height="6" fill="{t['bg']}"/>
<text x="{x_text:.1f}" y="{top + 5:.1f}" fill="{t['name']}">{e(name)}</text>
<text x="{right - 2.1 * CHAR_W:.1f}" y="{top + 5:.1f}" fill="{accent}">↗</text>
""" + "\n".join(rows) + "\n</svg>\n"


# Layouts: folder suffix -> card() options. Only the standard one is used now: the cards have no
# fixed width in README.md, so they sit two per row on wide screens and wrap to one per row,
# shrunk to the screen width, on phones. The compact layout stays available for other uses.
LAYOUTS = {"": {}}


def main():
    for slug, repo, name, desc, details, accent in PROJECTS:
        info = api(f"repos/{USER}/{repo}") or {}
        latest = api(f"repos/{USER}/{repo}/releases/latest") or {}
        release = latest.get("tag_name")
        zips = [a["size"] for a in latest.get("assets", []) if a["name"].endswith(".zip")]
        size = human_size(zips[0]) if zips else None  # the download attached to the release
        for theme, colors in THEMES.items():
            for suffix, options in LAYOUTS.items():
                out = HERE / f"{theme}{suffix}"
                out.mkdir(exist_ok=True)
                svg = card(name, desc, details, release, size, info.get("stargazers_count", 0), accent, colors,
                           **options)
                (out / f"{slug}.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {len(PROJECTS) * len(THEMES) * len(LAYOUTS)} cards")


if __name__ == "__main__":
    main()
