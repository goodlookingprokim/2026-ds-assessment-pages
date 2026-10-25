#!/usr/bin/env python3
"""Build the public, student-only assessment Pages site from reviewed sources."""
from html import escape
from pathlib import Path
import re
import shutil

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "outputs"
PUBLIC = ROOT / "docs"

ORANGE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSel8D22f8y8r0tWJYpux0EIqAKeGsD56wiYdUVHdgLPBNUaJA/viewform"
PYTHON_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdb_FYb6h-rQgikGn8_F4y0rpf1DCMkWUvg1huvRV6fmeYClA/viewform"


def copy(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)


def link(url: str, label: str, css: str = "") -> str:
    external = url.startswith("https://")
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else ""
    return f'<a class="{css}" href="{escape(url, quote=True)}"{attrs}>{escape(label)}</a>'


def shell(title: str, active: str, body: str) -> str:
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="2026 데이터과학 수행평가 학생 안내와 실습 자료">
<title>{escape(title)} · 2026 데이터과학</title><link rel="stylesheet" href="styles.css"></head>
<body><a class="skip" href="#content">본문으로 바로 가기</a>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html">2026 데이터과학 <span>수행평가 안내</span></a>
<nav aria-label="수행평가"><a {'aria-current="page"' if active == 'orange' else ''} href="orange.html">1차 · Orange</a><a {'aria-current="page"' if active == 'python' else ''} href="python.html">2차 · Python</a></nav></div></header>
<main class="wrap" id="content">{body}</main><footer class="wrap footer">고2 6·7·8·9반 · 자료와 제출 방법은 이 페이지에서 확인하세요. 제출은 Google 로그인이 필요합니다.</footer>
</body></html>'''


def file_item(url: str, title: str, detail: str) -> str:
    return f'<li>{link(url, title)}<span>{escape(detail)}</span></li>'


def section(heading: str, contents: str, ident: str = "") -> str:
    return f'<section class="section"{f" id={chr(34)}{ident}{chr(34)}" if ident else ""}><h2>{escape(heading)}</h2>{contents}</section>'


def build_orange() -> None:
    manual = SOURCE / "1차_Orange_실습매뉴얼"
    dataset = SOURCE / "2026_DS_Orange_주제별_가상데이터"
    guide = PUBLIC / "orange-guide"
    copy(manual / "index_student.html", guide / "index.html")
    for name in ["manual.mp4", "subtitles.vtt", "학생용_한장안내.pdf", "설문응답_작성가이드.pdf", "학생용_한장안내.md", "설문응답_작성가이드.md"]:
        copy(manual / name, guide / name)
    for name in ["00_new.png", "csv_video_import.png", "csv_video_connections.png", "csv_video_table.png", "csv_video_result.png", "csv_video_reopened.png"]:
        copy(manual / "assets" / name, guide / "assets" / name)
    copy(dataset / "학생배포_CSV_30주제.zip", guide / "downloads" / "학생배포_CSV_30주제.zip")
    copy(dataset / "학생배포_Excel_원본보관.zip", guide / "downloads" / "학생배포_Excel_원본보관.zip")
    copy(dataset / "학생배포_CSV_30주제.zip", PUBLIC / "files" / "orange-csv-30.zip")
    copy(manual / "downloads" / "제출예시" / "CSV_시연_11_로봇.ows", guide / "downloads" / "제출예시" / "CSV_시연_11_로봇.ows")
    csv_root = dataset / "학생배포" / "CSV"
    rows = []
    for csv in sorted(csv_root.glob("[0-9][0-9]_*.csv")):
        copy(csv, guide / "downloads" / "학생배포" / "CSV" / csv.name)
        rows.append(file_item(f"orange-guide/downloads/학생배포/CSV/{csv.name}", csv.stem, "CSV 한 개"))
    assert len(rows) == 30, f"Expected 30 CSV files, found {len(rows)}"
    body = '''<div class="hero"><p class="number">1차 수행평가 · Orange</p><h1>자료 하나로<br>그래프 하나 만들기</h1>
<p class="lead">관심 있는 자료를 골라 표와 그래프를 만들고, 발견한 내용을 내 말로 설명합니다.</p>
<div class="date"><strong>평가 11월 2~6일</strong><strong>제출 마감 11월 6일 23:59</strong></div></div>
<div class="route">자료 선택 <span>→</span> 표·그래프 <span>→</span> 파일·화면 저장 <span>→</span> 답변 7개 <span>→</span> 설문 제출</div>'''
    body += section("먼저 받을 자료", '<p>30개 주제 중 마음에 드는 <strong>CSV 한 개</strong>를 고르세요. 파일마다 가상 사례 180개와 공통 열 8개가 있어 표와 그래프를 연습할 수 있습니다. 실제 사람의 기록이 아니며, 다른 주제나 직접 준비한 자료를 써도 됩니다.</p><ul class="resource-list">' +
        file_item("files/orange-csv-30.zip", "CSV 30종 한 번에 받기", "여러 주제를 둘러볼 때") +
        file_item("#topics", "CSV 한 개씩 고르기", "필요한 주제만 받기") +
        file_item("orange-guide/index.html", "화면을 따라 하는 실습 가이드", "불러오기·연결·캡처·설문 제출") +
        file_item("orange-guide/학생용_한장안내.pdf", "한 장 안내 PDF", "빠르게 순서 확인") +
        file_item("orange-guide/설문응답_작성가이드.pdf", "답변 작성 가이드 PDF", "일곱 문항과 작성 예시") +
        '</ul>')
    body += section("순서대로 해 보세요", '''<ol class="steps"><li><strong>CSV를 Orange에 불러오기</strong><p>File로 CSV를 열고 Data Table에 연결해 표를 확인합니다.</p></li>
<li><strong>그래프 만들기</strong><p>File에서 Scatter Plot에도 직접 연결합니다. 참여지수_점과 성과지수_점, 활동유형으로 시작해도 됩니다.</p></li>
<li><strong>파일과 화면 저장</strong><p>Orange 작업 파일(.ows), 전체 연결 화면 1장, 주요 결과 화면 1장을 준비합니다. 저장한 .ows를 다시 열어 확인하세요.</p></li>
<li><strong>일곱 답변 작성</strong><p>결과물, 자료 구성, 연결 이유, 발견한 점과 근거, 진로·학업 도움, 느낀 점, 아쉬움·보완점을 각각 적습니다.</p></li>
<li><strong>Google 설문으로 제출</strong><p>학번·이름·과제 제목, 일곱 답변과 파일을 차례대로 넣고 접수 완료 화면을 확인합니다.</p></li></ol>''', "steps")
    body += section("제출 전 확인", '''<div class="callout"><strong>제출물</strong><p>.ows 파일 1개 + 전체 연결 화면 1장 + 결과 화면 1장 + 설문 답변 7개</p><p>교사 제공 CSV는 주제 번호만 적습니다. 직접 준비한 자료라면 실제 사용한 CSV·Excel 원본과 출처를 함께 제출하고, Excel의 시트 이름도 적습니다.</p></div>
<p>30점 = 답변 21점 + 자료 읽기·연결 4점 + 분석 결과 5점. 답변은 문항에 맞는 완결 문장 3개 이상 3점, 2개 2점, 1개 1점, 없으면 0점입니다. 같은 뜻의 반복은 한 번만 셉니다.</p>
<p>파일 문제로 막히면 준비된 답변과 파일부터 11월 6일 23:59까지 제출하고 교사에게 알리세요. 원래 작업의 누락·손상·경로 문제는 11월 9일 23:59까지 보완할 수 있습니다. 그 기간에 답변 수정이나 새 분석을 추가할 수는 없습니다.</p>''')
    body += section("실습 영상", '<video controls preload="metadata" width="100%"><source src="orange-guide/manual.mp4" type="video/mp4"><track kind="captions" src="orange-guide/subtitles.vtt" srclang="ko" label="한국어" default></video><p>' + link("orange-guide/manual.mp4", "영상 파일 받기") + '</p>')
    body += section("주제별 CSV", '<p>하나만 골라도 됩니다. 내려받은 CSV의 내용은 바꾸지 말고 자신의 Orange 작업 파일을 만드세요.</p><ul class="topic-list">' + ''.join(rows) + '</ul>', "topics")
    body += '<div class="submit"><div><h2>이제 제출하세요</h2><p>Google 계정으로 설문을 열고 답변과 파일을 확인한 뒤, 제출 완료 화면까지 보세요.</p></div>' + link(ORANGE_FORM, "1차 제출 설문 열기", "button") + '</div>'
    (PUBLIC / "orange.html").write_text(shell("1차 Orange 수행평가", "orange", body))


def build_python() -> None:
    source = SOURCE / "2차_파이썬_쉬운가이드_20261022"
    guide = PUBLIC / "python-guide"
    page = (source / "index.html").read_text()
    page = page.replace("AI는 채점 초안과 근거를 돕고 선생님이 최종 확인합니다.", "선생님이 제출 내용과 실행 결과를 확인하여 최종 평가합니다.")
    page = page.replace("https://colab.research.google.com/drive/1_jHFBKldDwVPT8eoHbUKqPVfGCnUO34Q", "기본예시_축제.ipynb")
    page = page.replace("https://colab.research.google.com/drive/1REZUbCgR0sa2hXKjVj6ElN86NMrQp7Lw", "제출예시_운동시간.ipynb")
    (guide / "index.html").parent.mkdir(parents=True, exist_ok=True)
    (guide / "index.html").write_text(page)
    for name in ["기본예시_축제.ipynb", "제출예시_운동시간.ipynb", "쉬운_동영상_매뉴얼.mp4", "자막.vtt", "대본.txt"]:
        copy(source / name, guide / name)
    for png in (source / "images").glob("*.png"):
        copy(png, guide / "images" / png.name)
    body = '''<div class="hero"><p class="number">2차 수행평가 · Python</p><h1>내 자료로<br>계산·표·그래프 만들기</h1>
<p class="lead">예시 노트북을 내 주제와 자료에 맞게 바꾸고, 실행 결과를 저장해 설명합니다.</p>
<div class="date"><strong>평가 11월 9~13일</strong><strong>제출 마감 미정 · 확정 후 안내</strong></div></div>
<div class="route">예시 받기 <span>→</span> 내 자료로 바꾸기 <span>→</span> 모두 실행 <span>→</span> .ipynb 저장 <span>→</span> 답변·파일 제출</div>'''
    body += section("먼저 받을 자료", '<p>아래 파일은 이 페이지에서 바로 받을 수 있습니다. 예시 노트북의 <strong>★ 1. 내 자료</strong> 셀부터 바꾸세요. 예시 코드는 그대로 사용해도 됩니다.</p><ul class="resource-list">' +
        file_item("python-guide/기본예시_축제.ipynb", "축제 기본 예시 노트북", "Google Colab에서 업로드해 사본 저장") +
        file_item("python-guide/제출예시_운동시간.ipynb", "운동 시간으로 바꾼 예시", "자료를 바꾸는 방법 참고") +
        file_item("python-guide/index.html", "화면을 따라 하는 실습 가이드", "Colab·저장·다운로드·설문 제출") +
        file_item("python-guide/쉬운_동영상_매뉴얼.mp4", "실습 영상 파일", "필요할 때 내려받기") + '</ul>')
    body += section("순서대로 해 보세요", '''<ol class="steps"><li><strong>예시를 Colab에 열기</strong><p>노트북 파일을 받은 뒤 Colab에 업로드하고 파일 → Drive에 사본 저장을 선택합니다.</p></li>
<li><strong>내 자료로 바꾸기</strong><p>★ 1. 내 자료 셀의 제목, 항목 이름, 이름, 숫자, 단위, 자료 설명을 내 주제에 맞게 바꿉니다. 이름과 숫자의 개수는 같게 맞춥니다.</p></li>
<li><strong>처음부터 모두 실행</strong><p>런타임 → 세션 다시 시작 및 모두 실행으로 계산, 표, 그래프에 오류가 없는지 확인합니다.</p></li>
<li><strong>.ipynb 내려받기</strong><p>결과를 저장한 뒤 파일 → 다운로드 → .ipynb 다운로드를 선택합니다. Colab 링크나 .py 파일로 대신 내지 않습니다.</p></li>
<li><strong>Google 설문으로 제출</strong><p>학번·이름·과제 제목, 일곱 답변과 .ipynb 파일을 넣고 접수 완료 화면을 확인합니다.</p></li></ol>''', "steps")
    body += section("제출 전 확인", '''<div class="callout"><strong>제출물</strong><p>실행 결과가 저장된 .ipynb 파일 1개(10MB 이하) + 설문 답변 7개</p><p>필요한 숫자는 노트북 안에 넣습니다. 별도 CSV·Excel·화면 캡처·수정 일지는 필수가 아닙니다.</p></div>
<p>답변 7개에는 자료·결과 소개, 어려움, 바꾼 부분과 달라진 결과, 코드 한 부분의 역할, 활용하고 싶은 곳, 배운 점, 다음 보완점을 적습니다.</p>
<p>30점 = 답변 21점 + NumPy·pandas·Matplotlib 활용과 실행 9점. 답변은 문항에 맞는 완결 문장 3개 이상 3점, 2개 2점, 1개 1점, 없으면 0점입니다. 기본정보는 무배점입니다.</p>
<p>실행이 막히면 이름과 숫자의 개수, 쉼표·따옴표·대괄호를 확인하고 다시 모두 실행하세요. 제출 마감은 확정 후 이 페이지와 설문에 안내됩니다.</p>''')
    body += section("실습 영상", '<video controls preload="metadata" width="100%"><source src="python-guide/쉬운_동영상_매뉴얼.mp4" type="video/mp4"><track kind="captions" src="python-guide/자막.vtt" srclang="ko" label="한국어" default></video><p>' + link("python-guide/쉬운_동영상_매뉴얼.mp4", "영상 파일 받기") + '</p>')
    body += '<div class="submit"><div><h2>이제 제출하세요</h2><p>실행 결과가 들어 있는 .ipynb 파일을 첨부하고 일곱 답변을 작성하세요.</p></div>' + link(PYTHON_FORM, "2차 제출 설문 열기", "button") + '</div>'
    (PUBLIC / "python.html").write_text(shell("2차 Python 수행평가", "python", body))


def build_index() -> None:
    body = '''<div class="hero index-hero"><h1>2026 데이터과학<br>수행평가 안내</h1><p class="lead">1차와 2차 안내, 실습 자료, 제출 순서를 한곳에서 확인하세요.</p></div>
<div class="choice-grid"><a class="choice" href="orange.html"><span>1차 · Orange</span><h2>자료 하나로 그래프 하나 만들기</h2><p>11월 2~6일 · 11월 6일 23:59 제출</p><strong>안내와 자료 보기 →</strong></a>
<a class="choice" href="python.html"><span>2차 · Python</span><h2>내 자료로 계산·표·그래프 만들기</h2><p>11월 9~13일 · 제출 마감 확정 후 안내</p><strong>안내와 자료 보기 →</strong></a></div>
<section class="section"><h2>제출 순서</h2><p>각 페이지에서 필요한 파일을 받고 실습 방법을 익힌 뒤, 해당 Google 설문에 일곱 답변과 파일을 차례대로 넣습니다. 마지막 접수 완료 화면까지 확인하세요.</p></section>'''
    (PUBLIC / "index.html").write_text(shell("수행평가 안내", "", body))


def main() -> None:
    PUBLIC.mkdir(exist_ok=True)
    (PUBLIC / ".nojekyll").touch()
    build_orange()
    build_python()
    build_index()


if __name__ == "__main__":
    main()
