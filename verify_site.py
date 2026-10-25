#!/usr/bin/env python3
"""Check public site links, assets, and student-facing copy before publishing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import re
import zipfile

ROOT = Path(__file__).resolve().parent / "docs"


class References(HTMLParser):
    def __init__(self):
        super().__init__()
        self.refs = []

    def handle_starttag(self, tag, attrs):
        values = dict(attrs)
        for key in ("href", "src"):
            if values.get(key):
                self.refs.append(values[key])


def main() -> None:
    failures = []
    count = 0
    for page in ROOT.rglob("*.html"):
        text = page.read_text(encoding="utf-8")
        visible = re.sub(r"<style.*?</style>|<script.*?</script>", " ", text, flags=re.I | re.S)
        visible = re.sub(r"<[^>]+>", " ", visible)
        for phrase in (r"인공지능.{0,24}(?:평가|채점)", r"(?<![A-Za-z])AI(?![A-Za-z]).{0,24}(?:평가|채점)", r"(?:평가|채점).{0,24}(?<![A-Za-z])AI(?![A-Za-z])"):
            if re.search(phrase, visible, re.I | re.S):
                failures.append(f"Forbidden public phrase or file link: {page.relative_to(ROOT)} ({phrase})")
        for phrase in (r"drive\.google\.com/file/", r"colab\.research\.google\.com/drive/"):
            if re.search(phrase, text, re.I):
                failures.append(f"External Drive link: {page.relative_to(ROOT)} ({phrase})")
        refs = References()
        refs.feed(text)
        for ref in refs.refs:
            parsed = urlsplit(ref)
            if parsed.scheme or ref.startswith("//"):
                continue
            target = (page.parent / unquote(parsed.path)).resolve() if parsed.path else page.resolve()
            if not target.is_relative_to(ROOT.resolve()) or not target.exists():
                failures.append(f"Broken local link: {page.relative_to(ROOT)} -> {ref}")
            count += 1
    csvs = list((ROOT / "orange-guide/downloads/학생배포/CSV").glob("[0-9][0-9]_*.csv"))
    if len(csvs) != 30:
        failures.append(f"Expected 30 individual CSV files; found {len(csvs)}")
    with zipfile.ZipFile(ROOT / "files/orange-csv-30.zip") as archive:
        if len([name for name in archive.namelist() if re.search(r"CSV/[0-9][0-9]_.*\.csv$", name)]) != 30:
            failures.append("The Orange ZIP does not contain 30 CSV files")
    for page in ("orange.html", "python.html"):
        if "docs.google.com/forms/d/e/" not in (ROOT / page).read_text():
            failures.append(f"Missing submission form: {page}")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {len(list(ROOT.rglob('*.html')))} HTML pages, {count} local references, 30 individual CSV files, 2 submission forms")


if __name__ == "__main__":
    main()
