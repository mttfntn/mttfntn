"""Writes the "Most used languages" block in README.md from the code in my public repositories.

    GITHUB_TOKEN=... python3 stats/languages.py

Adds up GitHub's per-language byte counts over every public, non-fork repository of USER
(except those in EXCLUDE), and replaces the text between the two LANGUAGES markers in
README.md. The languages workflow runs it once a day; without a token it still works, within
GitHub's limit for anonymous requests.
"""
import json
import os
import re
import urllib.request
from pathlib import Path

USER = "mttfntn"
TOP = 6
BAR = 20
README = Path(__file__).resolve().parent.parent / "README.md"
# Repositories built on someone else's code, left out so the chart counts only my own code.
# tissue-blender-5 is a fork of Alessandro Zomparelli's Tissue (not marked as a fork on GitHub).
EXCLUDE = {"tissue-blender-5"}
START, END = "<!--LANGUAGES:START-->", "<!--LANGUAGES:END-->"


def get(url):
    req = urllib.request.Request(url, headers={"Accept": "application/vnd.github+json", "User-Agent": "profile-stats"})
    token = os.environ.get("GITHUB_TOKEN")
    if token:
        req.add_header("Authorization", f"Bearer {token}")
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.load(r)


def totals():
    repos = get(f"https://api.github.com/users/{USER}/repos?type=owner&per_page=100")
    sums = {}
    for repo in repos:
        if repo["fork"] or repo["private"] or repo["name"] in EXCLUDE:
            continue
        for lang, size in get(repo["languages_url"]).items():
            sums[lang] = sums.get(lang, 0) + size
    return sums


def block(sums):
    total = sum(sums.values()) or 1
    rows = sorted(sums.items(), key=lambda kv: -kv[1])[:TOP]
    lines = []
    for lang, size in rows:
        share = size / total
        filled = round(share * BAR)
        # Kept narrow (about 40 characters) so it fits a phone screen without scrolling.
        lines.append(f"{lang:<11} {'█' * filled}{'░' * (BAR - filled)}  {share * 100:5.1f} %")
    return "```text\n" + "\n".join(lines) + "\n```"


def main():
    text = README.read_text(encoding="utf-8")
    new = re.sub(re.escape(START) + ".*?" + re.escape(END), f"{START}\n{block(totals())}\n{END}", text, flags=re.S)
    if new != text:
        README.write_text(new, encoding="utf-8")
        print("README.md updated")
    else:
        print("no change")


if __name__ == "__main__":
    main()
