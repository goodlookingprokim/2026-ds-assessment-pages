#!/usr/bin/env python3
"""Build a short, captioned Orange question-choice addendum from honest visuals."""

from pathlib import Path
import subprocess

from PIL import Image, ImageDraw, ImageFont

HERE = Path(__file__).resolve().parent
ORIGINAL = HERE.parents[1] / "outputs/1차_Orange_실습매뉴얼/assets/csv_video_result.png"
FONT = "/System/Library/Fonts/AppleSDGothicNeo.ttc"
W, H = 1600, 900
INK = "#17352d"
MUTED = "#4d625b"
PAPER = "#f7faf6"
GREEN = "#145c4c"
MINT = "#dff4e9"
LINE = "#cbdcd2"
WHITE = "#ffffff"


def font(size, bold=False):
    return ImageFont.truetype(FONT, size, index=6 if bold else 0)


def text(draw, xy, message, size, color=INK, bold=False):
    draw.text(xy, message, font=font(size, bold), fill=color)


def base(number, title, subtitle):
    image = Image.new("RGB", (W, H), PAPER)
    draw = ImageDraw.Draw(image)
    draw.rounded_rectangle((44, 36, 1556, 135), 25, fill=GREEN)
    text(draw, (78, 65), "2026 데이터과학  |  1차 Orange", 35, WHITE, True)
    text(draw, (48, 178), title, 65, INK, True)
    text(draw, (51, 269), subtitle, 31, MUTED)
    draw.line((48, 836, 1550, 836), fill=LINE, width=3)
    text(draw, (50, 850), "질문 선택 → 축·색 설정 → 결과 읽기 → 화면 저장", 26, MUTED)
    text(draw, (1480, 850), f"{number}/4", 26, MUTED)
    return image, draw


def card(draw, y, label, question, axes, color=None):
    draw.rounded_rectangle((49, y, 1551, y + 145), 21, fill=WHITE, outline=LINE, width=3)
    draw.rounded_rectangle((74, y + 27, 153, y + 105), 17, fill=MINT)
    text(draw, (98, y + 42), label, 35, GREEN, True)
    text(draw, (181, y + 23), question, 38, INK, True)
    suffix = "  ·  색: " + color if color else ""
    text(draw, (183, y + 83), axes + suffix, 28, MUTED)


image, draw = base(1, "같은 자료에서도 질문은 달라질 수 있어요", "아래는 출발 예시입니다. 한 가지를 골라 자신의 말로 읽으세요.")
card(draw, 345, "A", "활동 시간이 길수록 만족도는 높아 보일까?", "가로축 활동시간_시간 / 세로축 만족도_점", "활동유형")
card(draw, 511, "B", "지원 정도와 참여 정도는 어떻게 나타날까?", "가로축 지원지수_점 / 세로축 참여지수_점", "집단")
card(draw, 677, "C", "같은 참여 정도에서도 성과의 차이가 있을까?", "가로축 참여지수_점 / 세로축 성과지수_점", "활동유형")
image.save(HERE / "01_question_choices.png")

image, draw = base(2, "질문에 맞춰 축과 색을 고르세요", "File → Data Table, File → Scatter Plot 연결은 그대로 유지합니다.")
draw.rounded_rectangle((49, 343, 1551, 767), 24, fill=WHITE, outline=LINE, width=3)
for y, label, detail in [
    (381, "① 질문 한 개", "표의 숫자 열 2개와 범주 열 1개를 고릅니다."),
    (482, "② Scatter Plot", "Axis x와 Axis y는 숫자 열, Color는 집단 또는 활동유형."),
    (583, "③ 결과 읽기", "점의 모임·차이·예외를 근거와 함께 씁니다."),
    (684, "④ 과장 금지", "가상 자료의 관계를 실제 원인·결과로 단정하지 않습니다."),
]:
    text(draw, (89, y), label, 38, GREEN, True)
    text(draw, (421, y + 2), detail, 31, INK)
image.save(HERE / "02_axes_workflow.png")

image, draw = base(3, "실제 Orange 화면에서 확인할 곳", "2026.10.21 촬영한 11번 로봇 자료 시연 화면 · 한 가지 설정 예시")
shot = Image.open(ORIGINAL).convert("RGB")
shot.thumbnail((1050, 625), Image.Resampling.LANCZOS)
draw.rounded_rectangle((42, 343, 1135, 790), 18, fill=WHITE, outline=LINE, width=3)
# Keep the source screenshot's proportions and show all axis and color labels.
shot.thumbnail((1050, 444), Image.Resampling.LANCZOS)
image.paste(shot, (63, 348 + (432 - shot.height) // 2))
draw.rounded_rectangle((1164, 344, 1551, 789), 18, fill=MINT)
text(draw, (1192, 383), "이 화면은", 37, GREEN, True)
text(draw, (1192, 432), "참여 ↔ 성과", 37, INK, True)
text(draw, (1192, 490), "다른 질문이면", 31, INK)
text(draw, (1192, 537), "축도 바꿉니다.", 36, GREEN, True)
text(draw, (1192, 630), "결과 캡처에", 29, INK)
text(draw, (1192, 676), "축·색·점이", 34, INK, True)
text(draw, (1192, 721), "보이게 저장", 34, INK, True)
image.save(HERE / "03_real_orange_capture.png")

image, draw = base(4, "제출용 캡처는 두 장", "자신이 실제로 선택한 질문과 설정이 결과에 드러나야 합니다.")
card(draw, 369, "1", "연결 화면", "File에서 Data Table과 Scatter Plot으로 가는 두 선")
card(draw, 546, "2", "결과 화면", "그래프·가로축·세로축·색상 설정이 함께 보이는 화면")
text(draw, (66, 741), "저장한 .ows를 다시 열어 확인한 뒤, 설문에 파일과 화면을 각각 첨부하세요.", 30, GREEN, True)
image.save(HERE / "04_capture_checklist.png")

vtt = """WEBVTT

00:00:00.000 --> 00:00:07.000
같은 자료에서도 질문은 달라질 수 있습니다. 활동 시간과 만족도, 지원과 참여, 참여와 성과 중 하나처럼 자신만의 질문을 고르세요.

00:00:07.000 --> 00:00:14.000
File을 Data Table과 Scatter Plot에 각각 연결하고, 질문에 맞춰 숫자 열 두 개를 축으로, 집단이나 활동유형을 색으로 고르세요.

00:00:14.000 --> 00:00:21.000
이 화면은 기존 11번 로봇 자료의 실제 시연입니다. 참여와 성과는 한 가지 예시입니다. 다른 질문을 골랐다면 축도 바꾸세요.

00:00:21.000 --> 00:00:28.000
연결선이 보이는 화면 한 장, 그래프와 축과 색상 설정이 보이는 결과 화면 한 장을 저장하세요. 저장한 작업 파일도 다시 열어 확인합니다.
"""
(HERE / "diversity_addendum.vtt").write_text(vtt, encoding="utf-8")

concat = "".join(f"file '{(HERE / name).as_posix()}'\nduration {duration}\n" for name, duration in [
    ("01_question_choices.png", 7),
    ("02_axes_workflow.png", 7),
    ("03_real_orange_capture.png", 7),
    ("04_capture_checklist.png", 7),
])
(HERE / "slides.ffconcat").write_text(concat, encoding="utf-8")
subprocess.run([
    "ffmpeg", "-y", "-v", "error", "-safe", "0", "-f", "concat", "-i", str(HERE / "slides.ffconcat"),
    "-vf", "fps=24,format=yuv420p", "-c:v", "libx264", "-crf", "22", "-preset", "fast", "-movflags", "+faststart",
    str(HERE / "diversity_addendum.mp4"),
], check=True)
print(HERE / "diversity_addendum.mp4")
