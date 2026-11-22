"""Generates the terminal-style project cards in cards/dark/ and cards/light/ (one SVG each).

    GITHUB_TOKEN=... python3 cards/make_cards.py

Each card is a thin terminal-style frame with the project name cut into its top edge, then the
description and a details line with the platform, the latest release and the stars (shown once
there are any), read from GitHub. The languages workflow runs this daily,
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
     "a 1930s color dictionary, now in your shader editor.", "blender · python", "#E87D0D"),
    ("shrinkpatch", "shrinkpatch-blender", "shrinkpatch",
     "stick details onto any surface. no seams, no fuss.", "blender · python", "#E87D0D"),
    ("driver-controller", "driver-controller-blender", "driver-controller",
     "all your drivers, one panel.", "blender · python", "#E87D0D"),
    ("checklist-tool", "checklist-tool-blender", "checklist-tool",
     "a to-do list that lives inside the .blend.", "blender · python", "#E87D0D"),
    ("resource-safeguard", "resource-safeguard-blender", "resource-safeguard",
     "your gpu takes a break when you do.", "blender · python", "#E87D0D"),
    ("tissue-blender-5", "tissue-blender-5", "tissue-blender-5",
     "alessandro zomparelli's tissue, kept running on 5.3.", "blender · python", "#E87D0D"),
    ("onefingerrotation", "OneFingerRotation", "onefingerrotation",
     "spin swiftui views with one finger.", "swift · swiftui", "#F05138"),
    ("phone-trackpad", "phone-trackpad", "phone-trackpad",
     "your phone, but it's a trackpad now.", "python · windows · macos", "#3776AB"),
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


def wrap(text, width):
    lines, line = [], ""
    for word in text.split():
        if line and len(line) + 1 + len(word) > width:
            lines.append(line)
            line = word
        else:
            line = f"{line} {word}".strip()
    return lines + [line]


def card(name, desc, details, release, stars, accent, t):
    """One card as SVG: a thin terminal-style frame with the name cut into its top edge, two
    lines for the description (always reserved, so every card has the same height) and a
    details line. All text is monospace."""
    inner = COLS - 4
    width = COLS * CHAR_W + 2 * PAD
    left, right = PAD + CHAR_W / 2, PAD + (COLS - 0.5) * CHAR_W
    top, line0 = PAD + 8, PAD + 8 + LINE_H + 4
    desc_lines = (wrap(desc, inner) + ["", ""])[:2]
    bottom = line0 + 3 * LINE_H + 2
    height = bottom + PAD
    head, _, rest = details.partition(" · ")
    meta_tail = (" · " + rest if rest else "") + (f" · {release}" if release else "") + (f" · ★ {stars}" if stars else "")
    x_text = PAD + 2 * CHAR_W
    title_w = (len(name) + 2) * CHAR_W
    e = escape
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{width:.0f}" height="{height:.0f}" viewBox="0 0 {width:.0f} {height:.0f}">
<style>text {{ font: 14px {FONT}; }}</style>
<rect width="100%" height="100%" fill="{t['bg']}"/>
<rect x="{left:.1f}" y="{top:.1f}" width="{right - left:.1f}" height="{bottom - top:.1f}" fill="none" stroke="{t['border']}" stroke-width="1.2"/>
<rect x="{x_text - CHAR_W:.1f}" y="{top - 3:.1f}" width="{title_w:.1f}" height="6" fill="{t['bg']}"/>
<rect x="{right - 2.6 * CHAR_W:.1f}" y="{top - 3:.1f}" width="{2.2 * CHAR_W:.1f}" height="6" fill="{t['bg']}"/>
<text x="{x_text:.1f}" y="{top + 5:.1f}" fill="{t['name']}">{e(name)}</text>
<text x="{right - 2.1 * CHAR_W:.1f}" y="{top + 5:.1f}" fill="{accent}">↗</text>
<text x="{x_text:.1f}" y="{line0:.1f}" fill="{t['text']}">{e(desc_lines[0])}</text>
<text x="{x_text:.1f}" y="{line0 + LINE_H:.1f}" fill="{t['text']}">{e(desc_lines[1])}</text>
<text x="{x_text:.1f}" y="{line0 + 2 * LINE_H + 8:.1f}" xml:space="preserve"><tspan fill="{accent}">{e(head)}</tspan><tspan fill="{t['dim']}">{e(meta_tail)}</tspan></text>
</svg>
"""


def main():
    for slug, repo, name, desc, details, accent in PROJECTS:
        info = api(f"repos/{USER}/{repo}") or {}
        release = (api(f"repos/{USER}/{repo}/releases/latest") or {}).get("tag_name")
        for theme, colors in THEMES.items():
            out = HERE / theme
            out.mkdir(exist_ok=True)
            svg = card(name, desc, details, release, info.get("stargazers_count", 0), accent, colors)
            (out / f"{slug}.svg").write_text(svg, encoding="utf-8")
    print(f"wrote {len(PROJECTS) * len(THEMES)} cards")


if __name__ == "__main__":
    main()
