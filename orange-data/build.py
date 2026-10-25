#!/usr/bin/env python3
"""Build version 2 of the synthetic Orange practice CSV set.

The original eight columns are copied without changing a single value. The
three added columns are deterministic teaching data, not observations.
"""

from __future__ import annotations

import csv
import hashlib
import random
import zipfile
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
SOURCE = ROOT / "outputs/2026_DS_Orange_주제별_가상데이터/학생배포/CSV"
DEST = HERE / "CSV"
ZIP = HERE / "orange-csv-30-v2.zip"
BASE_FIELDS = [
    "사례번호", "집단", "활동유형", "활동시간_시간", "지원지수_점",
    "참여지수_점", "성과지수_점", "만족도_점",
]
ADDED_FIELDS = ["도움방식", "사전친숙도_점", "체감난이도_점"]
HELP_OPTIONS = ["혼자 탐색", "동료 도움", "자료 참고", "교사 설명"]


def clamp(value: float) -> str:
    return f"{max(0, min(100, value)):.1f}"


def synthesize(subject: str, row: dict[str, str]) -> dict[str, str]:
    # Independent row seeds make the output reproducible even if CSV order changes.
    key = f"{subject}|{row['사례번호']}".encode("utf-8")
    rng = random.Random(int.from_bytes(hashlib.sha256(key).digest()[:8], "big"))
    group_effect = ((int.from_bytes(hashlib.sha256(row["집단"].encode()).digest()[:2], "big") % 13) - 6)
    activity_effect = ((int.from_bytes(hashlib.sha256(row["활동유형"].encode()).digest()[:2], "big") % 15) - 7)
    familiarity = max(0, min(100, 51 + group_effect + activity_effect + rng.gauss(0, 17)))
    # A weak, noisy pattern gives students room to find both a tendency and exceptions.
    difficulty = 60 - 0.27 * familiarity + 0.45 * activity_effect + rng.gauss(0, 19)
    return {
        "도움방식": HELP_OPTIONS[rng.randrange(len(HELP_OPTIONS))],
        "사전친숙도_점": clamp(familiarity),
        "체감난이도_점": clamp(difficulty),
    }


def build() -> None:
    sources = sorted(SOURCE.glob("[0-9][0-9]_*.csv"))
    assert len(sources) == 30, f"Expected 30 source CSVs, found {len(sources)}"
    DEST.mkdir(parents=True, exist_ok=True)
    for source in sources:
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            assert reader.fieldnames == BASE_FIELDS, source
            originals = list(reader)
        assert len(originals) == 180, source
        output = DEST / source.name
        with output.open("w", encoding="utf-8-sig", newline="") as handle:
            writer = csv.DictWriter(handle, fieldnames=BASE_FIELDS + ADDED_FIELDS, lineterminator="\n")
            writer.writeheader()
            for original in originals:
                writer.writerow({**original, **synthesize(source.stem, original)})
    with zipfile.ZipFile(ZIP, "w", compression=zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for file in sorted(DEST.glob("*.csv")):
            archive.write(file, f"학생배포/CSV/{file.name}")
    verify(sources)


def verify(sources: list[Path]) -> None:
    outputs = sorted(DEST.glob("[0-9][0-9]_*.csv"))
    assert len(outputs) == len(sources) == 30
    for source, output in zip(sources, outputs, strict=True):
        assert source.name == output.name
        assert output.read_bytes().startswith(b"\xef\xbb\xbf"), output
        with source.open("r", encoding="utf-8-sig", newline="") as handle:
            old = list(csv.DictReader(handle))
        with output.open("r", encoding="utf-8-sig", newline="") as handle:
            reader = csv.DictReader(handle)
            assert reader.fieldnames == BASE_FIELDS + ADDED_FIELDS, output
            new = list(reader)
        assert len(old) == len(new) == 180, output
        assert all({key: row[key] for key in BASE_FIELDS} == original for row, original in zip(new, old, strict=True)), output
        help_counts = Counter(row["도움방식"] for row in new)
        assert set(help_counts) == set(HELP_OPTIONS) and min(help_counts.values()) >= 20, output
        for field in ADDED_FIELDS[1:]:
            values = [float(row[field]) for row in new]
            assert all(0 <= value <= 100 for value in values), output
            assert len(set(values)) >= 90 and max(values) - min(values) >= 50, output
    with zipfile.ZipFile(ZIP) as archive:
        names = archive.namelist()
        assert len(names) == 30
        for output in outputs:
            assert archive.read(f"학생배포/CSV/{output.name}") == output.read_bytes()
    print(f"PASS: {len(outputs)} UTF-8 BOM CSVs, 180 rows and 11 columns each; original eight columns preserved; ZIP contents match")


if __name__ == "__main__":
    build()
