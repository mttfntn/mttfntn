"""Generates the project cards in cards/dark/ and cards/light/ (one SVG per project).

    python3 cards/make_cards.py

Edit PROJECTS below and run it again; README.md links each card to its repository.
"""
from pathlib import Path
from xml.sax.saxutils import escape

HERE = Path(__file__).resolve().parent
W, H = 420, 116
PAD = 22
FONT = "-apple-system, BlinkMacSystemFont, 'Segoe UI', Helvetica, Arial, sans-serif"

# slug, name, description, tag (language or platform), tag color
PROJECTS = [
    ("sanzo-wada-colors", "sanzo wada colors", "a 1930s color dictionary, now in your shader editor.", "Blender · Python", "#E87D0D"),
    ("shrinkpatch", "shrinkpatch", "stick details onto any surface. no seams, no fuss.", "Blender · Python", "#E87D0D"),
    ("driver-controller", "driver controller", "all your drivers, one panel.", "Blender · Python", "#E87D0D"),
    ("checklist-tool", "checklist tool", "a to-do list that lives inside the .blend.", "Blender · Python", "#E87D0D"),
    ("resource-safeguard", "resource safeguard", "your gpu takes a break when you do.", "Blender · Python", "#E87D0D"),
    ("tissue-blender-5", "tissue for blender 5", "alessandro zomparelli's tissue, kept running on 5.3.", "Blender · Python", "#E87D0D"),
    ("onefingerrotation", "onefingerrotation", "spin swiftui views with one finger. 58 people liked that.", "SwiftUI", "#F05138"),
    ("phone-trackpad", "phone trackpad", "your phone, but it's a trackpad now.", "Python · Windows · macOS", "#3776AB"),
]

THEMES = {
    "dark": {"bg": "#161b22", "border": "#30363d", "title": "#e6edf3", "text": "#8d96a0", "arrow": "#6e7681"},
    "light": {"bg": "#ffffff", "border": "#d1d9e0", "title": "#1f2328", "text": "#59636e", "arrow": "#818b98"},
}


def wrap(text, max_chars=62):
    """Splits text into at most two lines of about max_chars characters."""
    words, lines, line = text.split(), [], ""
    for w in words:
        if line and len(line) + 1 + len(w) > max_chars:
            lines.append(line)
            line = w
        else:
            line = f"{line} {w}".strip()
    lines.append(line)
    return lines[:2]


def card(name, desc, tag, color, t):
    desc_lines = "".join(
        f'<text x="{PAD}" y="{68 + i * 20}" class="d">{escape(l)}</text>' for i, l in enumerate(wrap(desc)))
    return f"""<svg xmlns="http://www.w3.org/2000/svg" width="{W}" height="{H}" viewBox="0 0 {W} {H}">
<style>
.n {{ font: 600 17px {FONT}; fill: {t['title']}; }}
.d {{ font: 400 13.5px {FONT}; fill: {t['text']}; }}
.t {{ font: 500 12px {FONT}; fill: {t['text']}; }}
.a {{ font: 400 17px {FONT}; fill: {t['arrow']}; }}
</style>
<rect x="0.5" y="0.5" width="{W - 1}" height="{H - 1}" rx="12" fill="{t['bg']}" stroke="{t['border']}"/>
<text x="{PAD}" y="40" class="n">{escape(name)}</text>
<text x="{W - PAD}" y="40" class="a" text-anchor="end">↗</text>
{desc_lines}
<circle cx="{PAD + 5}" cy="{H - 21}" r="5" fill="{color}"/>
<text x="{PAD + 16}" y="{H - 17}" class="t">{escape(tag)}</text>
</svg>
"""


def main():
    for theme, colors in THEMES.items():
        out = HERE / theme
        out.mkdir(exist_ok=True)
        for slug, name, desc, tag, color in PROJECTS:
            (out / f"{slug}.svg").write_text(card(name, desc, tag, color, colors), encoding="utf-8")
    print(f"wrote {len(PROJECTS) * len(THEMES)} cards")


if __name__ == "__main__":
    main()
