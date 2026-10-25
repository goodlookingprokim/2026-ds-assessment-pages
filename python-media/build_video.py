#!/usr/bin/env python3
"""Replace the obsolete Notion/Colab opening with the current file workflow."""

from pathlib import Path
import re
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ROOT = HERE.parent
SOURCE = ROOT.parent / "outputs/2차_파이썬_쉬운가이드_20261022"
W, H = 1920, 1080
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
DURATIONS = (11.2, 12.5, 10.0)
OLD_CUT = 42.933


def run(*args):
    subprocess.run(args, check=True)


def write(draw, xy, value, size=48, color="#17352d", bold=False):
    font = ImageFont.truetype(FONT, size, index=6 if bold else 0)
    draw.text(xy, value, fill=color, font=font)


def background(number, title, description):
    frame = Image.new("RGB", (W, H), "#f7faf6")
    draw = ImageDraw.Draw(frame)
    draw.rounded_rectangle((55, 38, W - 55, 151), 25, fill="#145c4c")
    write(draw, (92, 68), "2026 데이터과학  |  2차 Python", 40, "white", True)
    write(draw, (75, 188), title, 69, bold=True)
    write(draw, (79, 285), description, 36, "#4d625b")
    write(draw, (1750, 1011), f"{number}/3", 31, "#4d625b")
    return frame, draw


def paste_capture(frame, source, box, target):
    shot = Image.open(source).convert("RGB").crop(box)
    shot.thumbnail((target[2] - target[0], target[3] - target[1]), Image.Resampling.LANCZOS)
    x = target[0] + ((target[2] - target[0]) - shot.width) // 2
    y = target[1] + ((target[3] - target[1]) - shot.height) // 2
    frame.paste(shot, (x, y))


frame, draw = background(1, "안내 페이지에서 예시 파일 받기", "축제 기본 예시 .ipynb 파일을 내려받습니다.")
draw.rounded_rectangle((70, 366, 1850, 949), 26, fill="white", outline="#cbdcd2", width=3)
paste_capture(frame, HERE / "current-guide.jpg", (0, 0, 1265, 330), (105, 391, 1815, 839))
write(draw, (135, 865), "1  안내 페이지 → 축제 기본 예시 파일 받기", 42, "#145c4c", True)
frame.save(HERE / "intro-01.png")

frame, draw = background(2, "Google Colab에 파일 업로드", "파일 → 노트 열기 → 업로드 → Browse")
draw.rounded_rectangle((70, 357, 1850, 970), 26, fill="white", outline="#cbdcd2", width=3)
paste_capture(frame, HERE / "colab-upload-current.jpg", (135, 75, 1145, 645), (95, 375, 1825, 949))
frame.save(HERE / "intro-02.png")

frame, draw = background(3, "내 Drive에 사본 저장", "업로드한 노트북이 열리면 내 작업 파일을 만듭니다.")
draw.rounded_rectangle((70, 365, 1850, 950), 26, fill="white", outline="#cbdcd2", width=3)
write(draw, (150, 470), "Colab 메뉴", 45, "#4d625b")
write(draw, (150, 554), "파일  →  Drive에 사본 저장", 75, "#145c4c", True)
write(draw, (150, 715), "새로 열린 사본에서 1. 내 자료 셀을 바꾸세요.", 49)
frame.save(HERE / "intro-03.png")

(HERE / "narration").mkdir(exist_ok=True)
for number, duration in enumerate(DURATIONS, 1):
    run("ffmpeg", "-y", "-v", "error", "-loop", "1", "-framerate", "15",
        "-i", str(HERE / f"intro-{number:02d}.png"), "-i", str(HERE / "narration" / f"{number:02d}.wav"),
        "-t", str(duration), "-vf", "format=yuv420p", "-af", "apad",
        "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
        "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "1",
        str(HERE / f"segment-{number:02d}.mp4"))

run("ffmpeg", "-y", "-v", "error", "-ss", str(OLD_CUT),
    "-i", str(SOURCE / "쉬운_동영상_매뉴얼.mp4"),
    "-vf", "fps=15,format=yuv420p", "-c:v", "libx264", "-preset", "veryfast", "-crf", "23",
    "-c:a", "aac", "-b:a", "128k", "-ar", "48000", "-ac", "1",
    str(HERE / "segment-04.mp4"))
playlist = "ffconcat version 1.0\n" + "".join(f"file 'segment-{n:02d}.mp4'\n" for n in range(1, 5))
(HERE / "segments.ffconcat").write_text(playlist)
run("ffmpeg", "-y", "-v", "error", "-safe", "0", "-f", "concat", "-i", str(HERE / "segments.ffconcat"),
    "-c", "copy", "-movflags", "+faststart", str(HERE / "쉬운_동영상_매뉴얼.mp4"))


def stamp(seconds):
    milliseconds = round(seconds * 1000)
    hours, milliseconds = divmod(milliseconds, 3600000)
    minutes, milliseconds = divmod(milliseconds, 60000)
    whole, milliseconds = divmod(milliseconds, 1000)
    return f"{hours:02d}:{minutes:02d}:{whole:02d}.{milliseconds:03d}"


def seconds(stamp_value):
    match = re.fullmatch(r"(\d\d):(\d\d):(\d\d)\.(\d\d\d)", stamp_value)
    assert match
    hours, minutes, whole, milliseconds = map(int, match.groups())
    return hours * 3600 + minutes * 60 + whole + milliseconds / 1000


# 자막.vtt는 실제 나레이션을 발화별로 확인한 파일입니다.
# 화면 설명을 자막으로 복사하거나 이전 영상의 VTT를 이어 붙이지 않습니다.
offset = sum(DURATIONS) - OLD_CUT

script = """00:00:00.000 안내 페이지에서 예시 파일 받기
안녕하세요. 잘생김프로쌤입니다. 2차 수행평가는 예시 노트북을 내 자료로 바꾸고, 결과를 확인한 뒤 제출합니다.

00:00:11.200 Google Colab에 업로드하기
먼저 안내 페이지에서 축제 기본 예시 파일을 받으세요. 구글 코랩을 열어 파일, 노트 열기, 업로드에서 방금 받은 아이파이엔비 파일을 선택합니다.

00:00:23.700 내 Drive에 사본 저장하기
노트북이 열리면 파일, 드라이브에 사본 저장을 누르세요. 새로 열린 내 사본에서 자료 셀을 바꾸며 실습합니다.

"""
for block in (SOURCE / "대본.txt").read_text().split("\n\n"):
    if block.startswith("00:00:42.933") or block.startswith("00:01:") or block.startswith("00:02:"):
        old_stamp, rest = block.split(" ", 1)
        script += stamp(seconds(old_stamp) + offset) + " " + rest + "\n\n"
(HERE / "대본.txt").write_text(script.rstrip() + "\n")
print(HERE / "쉬운_동영상_매뉴얼.mp4")
