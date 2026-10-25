#!/usr/bin/env python3
"""Check public site links, assets, and student-facing copy before publishing."""
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit
import ast
import csv
import re
import zipfile
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent / "docs"


def caption_cues(path: Path):
    blocks = path.read_text(encoding="utf-8").strip().split("\n\n")
    if blocks[0] != "WEBVTT":
        raise ValueError(f"Invalid VTT header: {path}")
    cues = []
    for block in blocks[1:]:
        lines = block.splitlines()
        if " --> " not in lines[0]:
            lines.pop(0)  # Optional cue number.
        start, end = lines[0].split(" --> ")
        def milliseconds(stamp):
            hours, minutes, seconds = stamp.split(":")
            return int(hours) * 3600000 + int(minutes) * 60000 + round(float(seconds) * 1000)
        cues.append((milliseconds(start), milliseconds(end), " ".join(lines[1:])))
    return cues


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
        nav = re.search(r'<nav class="global-nav".*?</nav>', text, re.S)
        if not nav or any(target not in nav.group(0) for target in ('index.html', 'orange.html', 'orange-guide/index.html', 'python.html', 'python-guide/index.html')):
            failures.append(f"Incomplete global navigation: {page.relative_to(ROOT)}")
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
    expected_columns = {"도움방식", "사전친숙도_점", "체감난이도_점"}
    for path in csvs:
        with path.open(encoding="utf-8-sig", newline="") as stream:
            reader = csv.DictReader(stream)
            if len(reader.fieldnames or []) != 11 or not expected_columns.issubset(reader.fieldnames or []) or len(list(reader)) != 180:
                failures.append(f"Orange CSV schema/rows mismatch: {path.name}")
    with zipfile.ZipFile(ROOT / "files/orange-csv-30.zip") as archive:
        if len([name for name in archive.namelist() if re.search(r"CSV/[0-9][0-9]_.*\.csv$", name)]) != 30:
            failures.append("The Orange ZIP does not contain 30 CSV files")
    for page in ("orange.html", "python.html"):
        if "docs.google.com/forms/d/e/" not in (ROOT / page).read_text():
            failures.append(f"Missing submission form: {page}")
    for page in ("orange.html", "orange-guide/index.html"):
        text = (ROOT / page).read_text()
        if len(re.findall(r'<li><strong>\d+\. .*?</strong><span>가로축', text)) < 14:
            failures.append(f"Orange question choices missing: {page}")
        if "question-choices.mp4" not in text and "diversity_addendum.mp4" not in text:
            failures.append(f"Orange diversity video missing: {page}")
    orange_guide = (ROOT / "orange-guide/index.html").read_text()
    for phrase in ("왜 두 곳에 연결할까요?", "행 수·열 이름·값과 빈칸", "위쪽 Data Table과 아래쪽 Scatter Plot", "assets/file-two-branches.png"):
        if phrase not in orange_guide:
            failures.append(f"Orange branch explanation missing: {phrase}")
    example = ET.parse(ROOT / "orange-guide/downloads/제출예시/CSV_시연_11_로봇.ows").getroot()
    nodes = {node.get("id"): node for node in example.find("nodes")}
    links = {(link.get("source_node_id"), link.get("sink_node_id")) for link in example.find("links")}
    if links != {("0", "1"), ("0", "2")}:
        failures.append("Orange example must branch directly from File to both widgets")
    if not (ast.literal_eval(nodes["1"].get("position"))[1] < ast.literal_eval(nodes["0"].get("position"))[1] < ast.literal_eval(nodes["2"].get("position"))[1]):
        failures.append("Orange example must place Data Table above File and Scatter Plot below")
    guide = (ROOT / "python-guide/index.html").read_text()
    if '<details id="exercise-code">' not in guide or guide.count('class="notebook-code"') != 4:
        failures.append("Python exercise example is not visible as four inline code blocks")
    if re.search(r'<a[^>]*>운동 시간으로 바꾼 예시 보기</a>', guide):
        failures.append("Python exercise example still opens a separate page")
    for relative, minimum in (("orange-guide/diversity_addendum.vtt", 6),
                              ("orange-guide/subtitles.vtt", 60),
                              ("python-guide/자막.vtt", 30)):
        try:
            cues = caption_cues(ROOT / relative)
            if len(cues) < minimum or any(start >= end or
                (index > 0 and start < cues[index - 1][1])
                for index, (start, end, _) in enumerate(cues)):
                failures.append(f"Invalid or overlapping captions: {relative}")
        except (ValueError, IndexError) as error:
            failures.append(f"Invalid captions: {relative} ({error})")
    narration = (ROOT / "python-guide/대본.txt").read_text(encoding="utf-8")
    spoken = " ".join(block.split("\n", 1)[1] for block in narration.strip().split("\n\n"))
    captions = " ".join(text for _, _, text in caption_cues(ROOT / "python-guide/자막.vtt"))
    spoken_words = re.findall(r"[가-힣A-Za-z0-9]+", spoken.lower())
    caption_words = re.findall(r"[가-힣A-Za-z0-9]+", captions.lower())
    if caption_words != spoken_words:
        failures.append("Python captions must reproduce the spoken narration, not the slide summaries")
    if failures:
        raise SystemExit("\n".join(failures))
    print(f"PASS: {len(list(ROOT.rglob('*.html')))} HTML pages, {count} local references, 30 individual CSV files, 2 submission forms")


if __name__ == "__main__":
    main()
