#!/usr/bin/env python3
"""Build the public, student-only assessment Pages site from reviewed sources."""
from html import escape
from hashlib import sha256
from pathlib import Path
import json
import re
import shutil

ROOT = Path(__file__).resolve().parent
SOURCE = ROOT.parent / "outputs"
PUBLIC = ROOT / "docs"
CAPTION_SCRIPT_VERSION = sha256((ROOT / "caption-panel.js").read_bytes()).hexdigest()[:10]


def media_stamp(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()[:10]

ORANGE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSel8D22f8y8r0tWJYpux0EIqAKeGsD56wiYdUVHdgLPBNUaJA/viewform"
PYTHON_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdb_FYb6h-rQgikGn8_F4y0rpf1DCMkWUvg1huvRV6fmeYClA/viewform"


def copy(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)


def link(url: str, label: str, css: str = "") -> str:
    external = url.startswith("https://")
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else (' download' if Path(url.split('#')[0]).suffix.lower() in {'.csv', '.zip', '.ipynb', '.pdf', '.mp4', '.ows'} else '')
    return f'<a class="{css}" href="{escape(url, quote=True)}"{attrs}>{escape(label)}</a>'


def global_nav(active: str, prefix: str = "") -> str:
    items = [("home", "메인", "index.html"), ("orange", "1차 안내", "orange.html"), ("orange-guide", "1차 실습", "orange-guide/index.html"), ("python", "2차 안내", "python.html"), ("python-guide", "2차 실습", "python-guide/index.html")]
    links = ""
    for key, label, path in items:
        current = ' aria-current="page"' if key == active else ""
        links += f'<a href="{prefix}{path}"{current}>{label}</a>'
    return f'<nav class="global-nav" aria-label="전체 페이지 빠른 이동">{links}</nav>'


def shell(title: str, active: str, body: str) -> str:
    caption_assets = f'<link rel="stylesheet" href="caption-panel.css"><script src="caption-panel.js?v={CAPTION_SCRIPT_VERSION}" defer></script>' if '<video' in body else ''
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="2026 데이터과학 수행평가 학생 안내와 실습 자료">
<title>{escape(title)} · 2026 데이터과학</title><link rel="stylesheet" href="styles.css">{caption_assets}</head>
<body><a class="skip" href="#content">본문으로 바로 가기</a>
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html">2026 데이터과학 <span>수행평가 안내</span></a>
{global_nav(active)}</div></header>
<main class="wrap" id="content">{body}</main><footer class="wrap footer">{global_nav(active)}<p>고2 6·7·8·9반 · 자료와 제출 방법은 이 페이지에서 확인하세요. 제출은 Google 로그인이 필요합니다.</p></footer>
</body></html>'''


def add_guide_nav(page: str, active: str, previous: str, next_page: str) -> str:
    nav = '<div class="assessment-nav"><div class="assessment-nav-inner">' + global_nav(active, "../") + f'<div class="assessment-neighbors"><a href="../{previous}">← 이전 페이지</a><a href="../{next_page}">다음 페이지 →</a></div></div></div>'
    page = page.replace('<body>', '<body>' + nav, 1)
    css = '<style>.assessment-nav{position:sticky;top:0;z-index:100;background:#fff;border-bottom:2px solid #145c4c;box-shadow:0 3px 10px #0001}.assessment-nav-inner{max-width:1050px;margin:auto;padding:8px 16px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px}.assessment-nav .global-nav{display:flex;flex-wrap:wrap;gap:4px}.assessment-nav a{display:inline-block;padding:7px 10px;border-radius:6px;color:#173d33;text-decoration:none;font-size:14px;font-weight:700}.assessment-nav a:hover,.assessment-nav a[aria-current=page]{background:#c5e8da}.assessment-neighbors{display:flex;gap:4px}.question-choices{padding:18px;background:#eaf3ef;border:1px solid #cbd8d1;border-radius:12px;margin:20px 0}.question-choices ol{list-style:none;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;padding:0}.question-choices li{background:#fff;padding:11px;border-radius:7px;border:1px solid #cbd8d1}.question-choices li strong,.question-choices li span{display:block}.question-choices li span{font-size:13px}.question-choices code{white-space:nowrap}.diversity-visual{max-width:100%}@media(max-width:600px){.assessment-nav-inner{padding:4px 8px}.assessment-nav a{font-size:12px;padding:6px}.assessment-neighbors{width:100%;justify-content:space-between}.question-choices ol{grid-template-columns:1fr}}</style>'
    if active == "orange-guide":
        css = css.replace("</style>", ".branch-layout{width:min(100%,572px);margin-inline:auto}.branch-layout img{width:100%}</style>", 1)
    assets = f'<link rel="stylesheet" href="../caption-panel.css"><script src="../caption-panel.js?v={CAPTION_SCRIPT_VERSION}" defer></script>'
    return page.replace('</head>', css + assets + '</head>', 1)


def file_item(url: str, title: str, detail: str) -> str:
    return f'<li>{link(url, title)}<span>{escape(detail)}</span></li>'


def section(heading: str, contents: str, ident: str = "") -> str:
    return f'<section class="section"{f" id={chr(34)}{ident}{chr(34)}" if ident else ""}><h2>{escape(heading)}</h2>{contents}</section>'


ORANGE_QUESTIONS = [
    ("활동 시간이 긴 사례는 만족도가 어떻게 다를까?", "활동시간_시간", "만족도_점", "활동유형"),
    ("활동 시간과 체감 난이도는 함께 달라질까?", "활동시간_시간", "체감난이도_점", "집단"),
    ("처음부터 익숙했던 사례는 활동을 덜 어렵게 느낄까?", "사전친숙도_점", "체감난이도_점", "도움방식"),
    ("사전 친숙도에 따라 성과의 분포가 달라질까?", "사전친숙도_점", "성과지수_점", "활동유형"),
    ("지원 정도와 만족도는 어떤 모양으로 나타날까?", "지원지수_점", "만족도_점", "도움방식"),
    ("참여 정도가 비슷한 사례들의 만족도는 같을까?", "참여지수_점", "만족도_점", "집단"),
    ("어렵게 느낀 사례에도 성과가 높은 경우가 있을까?", "체감난이도_점", "성과지수_점", "도움방식"),
    ("지원 정도와 참여 정도의 관계는 활동별로 같을까?", "지원지수_점", "참여지수_점", "활동유형"),
    ("같은 활동 시간에서도 참여 정도가 다른 사례는?", "활동시간_시간", "참여지수_점", "도움방식"),
    ("처음 익숙한 정도와 참여 정도를 비교하면?", "사전친숙도_점", "참여지수_점", "집단"),
    ("만족도가 높은 사례는 성과도 항상 높을까?", "만족도_점", "성과지수_점", "활동유형"),
    ("같은 시간 활동해도 성과가 다른 사례는?", "활동시간_시간", "성과지수_점", "집단"),
    ("참여 정도가 높은 사례는 성과도 높게 보일까?", "참여지수_점", "성과지수_점", "활동유형"),
    ("지원 정도가 높아도 활동이 어렵게 느껴질까?", "지원지수_점", "체감난이도_점", "도움방식"),
]


def question_cards() -> str:
    cards = "".join(f'<li><strong>{i}. {escape(question)}</strong><span>가로축 <code>{escape(x)}</code> · 세로축 <code>{escape(y)}</code> · 색 <code>{escape(color)}</code></span></li>' for i, (question, x, y, color) in enumerate(ORANGE_QUESTIONS, 1))
    return '<section class="question-choices" id="question-choices"><h2>내 분석 질문 고르기 · 14가지 시작 예시</h2><p>CSV 한 개와 질문 한 개를 골라 시작하세요. 아래 축·색은 예시이며, 자료에 맞게 바꿔도 됩니다. 관계가 보이지 않거나 예외가 보여도 중요한 결과입니다. 가상 사례에서 보이는 모습만 설명하고 원인이나 실제 사람 전체의 사실로 단정하지 않습니다.</p><ol>' + cards + '</ol><p>결과 화면을 캡처할 때는 내가 선택한 가로축·세로축·색 설정과 점들이 함께 보이게 하세요. 답변에는 선택한 질문, 화면에서 본 근거, 예외 또는 한계를 씁니다.</p></section>'


def revise_orange_guide(page: str) -> str:
    page = page.replace('자료는 모두 180개 가상 사례 × 같은 8개 열입니다.', '새 CSV는 모두 180개 가상 사례 × 11개 열입니다.')
    page = page.replace('처음에는 “참여 정도가 높은 사례는 성과도 높게 보일까?”라는 질문 하나로 시작하세요.', '아래 14가지 예시 중 마음에 드는 질문 하나를 골라 시작하세요.')
    page = page.replace('자료의 뜻 알아보기 · 8개 열과 분석 질문', '자료의 뜻 알아보기 · 11개 열')
    page = page.replace('30개 모두 같은 8개 열, 180개 가상 사례입니다.', '30개 모두 같은 11개 열, 180개 가상 사례입니다.')
    extra_rows = '<tr><th>도움방식</th><td>혼자 탐색·동료 도움·자료 참고·교사 설명 중 하나인 가상 범주입니다.</td></tr><tr><th>사전친숙도_점</th><td>활동을 시작하기 전 주제에 익숙했던 정도를 나타내는 가상 점수입니다.</td></tr><tr><th>체감난이도_점</th><td>활동 뒤 어렵다고 느낀 정도를 나타내는 가상 점수입니다. 높을수록 어렵게 느낀 것입니다.</td></tr>'
    page = page.replace('<tr><th>만족도_점</th><td>활동에 만족한 정도를 나타내는 가상 점수입니다.</td></tr>', '<tr><th>만족도_점</th><td>활동에 만족한 정도를 나타내는 가상 점수입니다.</td></tr>' + extra_rows)
    page = page.replace('네 가지 점수는 모두', '여섯 가지 점수는 모두')
    start = page.index('<h3>처음에는 이 질문 하나로 시작하세요</h3>')
    end = page.index('<p class="note"><strong>빈칸은 0점이 아닙니다.', start)
    page = page[:start] + '<p>질문은 한 가지만 골라도 됩니다. 선택한 질문에 맞춰 산점도의 숫자 열 두 개와 범주 색을 고르세요. <a href="#question-choices">14가지 질문 예시 보기</a></p>' + page[end:]
    page = page.replace('11번 예시에는 180행·8열이 있습니다. <code>참여지수_점</code>과 <code>성과지수_점</code> 열을 찾아보세요.', '현재 11번 CSV는 180행·11열입니다. <code>참여지수_점</code>, <code>성과지수_점</code>뿐 아니라 새 열인 <code>도움방식</code>, <code>사전친숙도_점</code>, <code>체감난이도_점</code>도 찾아보세요.')
    page = page.replace('왼쪽 <strong>Visualize</strong>에서 <strong>Scatter Plot</strong>을 끌어 놓습니다.', '왼쪽 <strong>Visualize</strong>에서 <strong>Scatter Plot</strong>을 끌어 놓습니다. <strong>File은 왼쪽 가운데, Data Table은 오른쪽 위, Scatter Plot은 오른쪽 아래</strong>로 벌려 놓으세요. 두 연결선을 따로 볼 수 있습니다.')
    connection_why = ('<p><strong>왜 두 곳에 연결할까요?</strong> File은 CSV를 읽어 같은 자료를 두 도구로 보냅니다. '
        '<strong>Data Table</strong>에서는 행 수·열 이름·값과 빈칸을 확인해 자료를 제대로 읽었는지 살핍니다. '
        '<strong>Scatter Plot</strong>에서는 고른 숫자 열 두 개를 가로축·세로축에 놓아 점의 분포와 예외를 봅니다. '
        '따라서 <strong>File → Data Table</strong>과 <strong>File → Scatter Plot</strong>을 각각 연결하세요. '
        'Data Table을 거쳐 Scatter Plot으로 잇는 순서가 아니라, 같은 원자료가 두 갈래로 갑니다.</p>'
        '<p>File을 왼쪽 가운데에 두고 Data Table을 오른쪽 위, Scatter Plot을 오른쪽 아래에 두면 두 선의 출발점과 도착점이 겹치지 않아 확인하기 쉽습니다. '
        '두 선에 <code>Data</code>가 표시되는지 살펴보세요. 위치 자체가 점수 기준은 아니며, 이 배치는 연결을 쉽게 확인하기 위한 예시입니다.</p>')
    page = page.replace('<h3>③ File에서 두 곳으로 연결하기</h3>', '<h3>③ File에서 두 곳으로 연결하기</h3>' + connection_why, 1)
    page = page.replace('File에서 나가는 선이 두 개인지 확인합니다.', 'File에서 출발하는 선 두 개가 각각 Data Table과 Scatter Plot에 도착하는지 확인합니다. 두 위젯 사이에 연결선이 있어야 하는 것은 아닙니다.')
    page = page.replace('assets/csv_video_connections.png', 'assets/file-two-branches.png')
    page = page.replace('실제 연결 화면. File의 자료를 표와 그래프로 각각 보냅니다.', '현재 11열 CSV를 연 실제 Orange 화면. File에서 위쪽 Data Table과 아래쪽 Scatter Plot으로 두 선이 각각 이어집니다.')
    page = page.replace('<figure><a href="assets/file-two-branches.png"', '<figure class="branch-layout"><a href="assets/file-two-branches.png"', 1)
    page = page.replace('<h3>⑤ 그래프 만들고 읽기</h3>', '<h3>⑤ 내가 고른 질문으로 그래프 만들고 읽기</h3><p><a href="#question-choices">14가지 질문 예시</a>에서 하나를 고릅니다. 아래 사진의 참여·성과 축은 조작 시연용입니다. 자신의 질문에 맞는 숫자 열 두 개로 바꾸세요.</p>')
    page = page.replace('Axis x</strong>(가로축)는 <code>참여지수_점</code>으로 고릅니다.', 'Axis x</strong>(가로축)는 내가 고른 질문의 첫 번째 숫자 열로 고릅니다.')
    page = page.replace('Axis y</strong>(세로축)는 <code>성과지수_점</code>으로 고릅니다.', 'Axis y</strong>(세로축)는 내가 고른 질문의 두 번째 숫자 열로 고릅니다.')
    page = page.replace('Color</strong>(색상)는 <code>활동유형</code>으로 고릅니다.', 'Color</strong>(색상)는 질문에 맞게 <code>집단</code>, <code>활동유형</code>, <code>도움방식</code> 중에서 고릅니다.')
    page = page.replace('점들이 보이면, 눈에 띄는 모양 하나를 찾아봅니다. 어느 쪽에 높은 점들이 많은가요?', '점들이 보이면 모인 곳과 벗어난 점을 찾습니다. 관계가 뚜렷하지 않아도 그대로 적습니다.')
    page = page.replace('실제 결과 화면. 가로축은 참여지수, 세로축은 성과지수, 색은 활동유형입니다.', '현재 11열 CSV의 실제 결과 화면. 가로축은 참여지수, 세로축은 성과지수, 색은 집단입니다. 질문을 바꾸면 축과 색도 바꾸세요.')
    alternate_graph = '<figure><a href="assets/alternative-scatter.png" target="_blank" rel="noopener"><img loading="lazy" src="assets/alternative-scatter.png" alt="같은 11열 CSV에서 가로축 활동시간, 세로축 만족도, 색 활동유형을 고른 실제 Orange 산점도"></a><figcaption>다른 질문의 실제 결과: 활동시간과 만족도를 비교하고 활동유형으로 색을 구분한 화면 · 누르면 크게 볼 수 있습니다.</figcaption></figure>'
    page = page.replace('<p class="note"><strong>여기까지 보이면 실습 성공!', alternate_graph + '<p class="note"><strong>여기까지 보이면 실습 성공!', 1)
    page = page.replace('11번 CSV를 읽은 실제 화면. 180개 사례를 확인합니다.', '현재 11열 CSV를 읽은 실제 화면. 180개 사례와 10 features, 1 meta attribute를 확인합니다.')
    page = page.replace('실제 표 화면. 가로 스크롤을 움직이며 열 이름을 확인합니다.', '현재 11열 CSV의 실제 표 화면. 행·열 이름·빈칸을 확인합니다.')
    page = page.replace('CSV로 만든 OWS를 다시 연 실제 작업 화면.', '현재 11열 CSV로 만든 OWS의 실제 분기 연결 화면.')
    page = page.replace('11번 자료에는 빈칸이 있습니다. 선택한 두 축 중 값이 없는 6개 사례는 그래프에 나오지 않아, 180행 중 174개 점이 그려집니다.', '11번 자료의 참여·성과 열에는 빈칸이 있어 두 축을 고르면 180행 중 174개 점이 그려집니다. 다른 축을 고르면 표시되는 점 수가 달라질 수 있습니다.')
    page = page.replace('File의 7 features와 1 meta attribute는 합해 여덟 열입니다.', 'File의 10 features와 1 meta attribute는 합해 열한 열입니다.')
    current_capture = ('<div class="note"><strong>현재 배포 CSV의 실제 Orange 화면</strong><p>아래 두 사진은 11번 새 CSV를 File에서 다시 열어 확인한 화면입니다. 180 instances, 10 features, 1 meta attribute가 합쳐서 11열입니다.</p></div>'
        '<figure><a href="assets/current-11-file-top.jpg" target="_blank" rel="noopener"><img loading="lazy" src="assets/current-11-file-top.jpg" alt="현재 11열 CSV를 연 Orange File 창. 180 instances, 10 features, 1 meta attribute가 표시됨"></a><figcaption>현재 자료의 행 수와 열 구성 · 누르면 크게 볼 수 있습니다.</figcaption></figure>'
        '<figure><a href="assets/current-11-file-bottom.jpg" target="_blank" rel="noopener"><img loading="lazy" src="assets/current-11-file-bottom.jpg" alt="현재 11열 CSV의 아래쪽 열: 도움방식, 사전친숙도_점, 체감난이도_점, 사례번호"></a><figcaption>아래로 내리면 추가된 세 열과 사례번호가 보입니다. · 누르면 크게 볼 수 있습니다.</figcaption></figure>')
    page = page.replace('<h3>⑤ 내가 고른 질문으로 그래프 만들고 읽기</h3>', current_capture + '<h3>⑤ 내가 고른 질문으로 그래프 만들고 읽기</h3>', 1)
    page = page.replace('전체 자료를 한꺼번에 받거나 기존 Excel을 쓰려면', '전체 CSV를 받거나 기존 8열 Excel을 참고하려면')
    page = page.replace('기존 Excel 원본 ZIP 받기', '기존 8열 Excel 원본 ZIP 받기 · 이번 CSV와 열 수 다름')
    visuals = '<figure><img class="diversity-visual" src="assets/01_question_choices.png" alt="서로 다른 세 분석 질문과 그에 맞는 가로축·세로축·색 설정을 보여 주는 설명 그림"><figcaption>질문에 따라 축과 색을 다르게 고르는 방법</figcaption></figure>'
    page = page.replace('<details id="practice">', question_cards() + visuals + '<details id="practice">', 1)
    page = page.replace('<h3>⑤ 내가 고른 질문으로 그래프 만들고 읽기</h3>', '<h3>⑤ 내가 고른 질문으로 그래프 만들고 읽기</h3><figure><img class="diversity-visual" src="assets/02_axes_workflow.png" alt="질문을 고르고 Orange 산점도에서 가로축·세로축·색을 설정하는 순서"><figcaption>질문에서 그래프 설정으로 이어지는 순서</figcaption></figure>')
    page = page.replace('<h3>Windows · 기본', '<figure><img class="diversity-visual" src="assets/04_capture_checklist.png" alt="결과 화면 캡처에 그래프, 가로축, 세로축, 색 설정이 모두 보여야 한다는 확인표"><figcaption>결과 화면을 저장하기 전 확인</figcaption></figure><h3>Windows · 기본', 1)
    page = page.replace('CSV를 불러오고 두 도구를 연결하는 기존 실제 화면 시연입니다.', '현재 11열 CSV를 연 실제 Orange 화면에서 File의 두 갈래 연결, Data Table의 표, Scatter Plot의 축과 색을 보여 줍니다. 참여·성과는 조작 예시 한 가지이며 자신의 질문에 맞춰 축과 색을 바꾸세요.')
    page = page.replace('<p class="small">완성 예시를 보는 목적은 연결과 결과를 이해하는 것입니다.', '<p class="small">다른 컴퓨터에서 완성 예시 OWS를 열면 File 위젯에서 내려받은 같은 번호 CSV를 다시 선택하세요. 자신의 질문으로 분석한 작업 파일은 따로 저장하세요.</p><p class="small">완성 예시를 보는 목적은 연결과 결과를 이해하는 것입니다.')
    page = page.replace('경계 사례는 AI가 임의로 0점 처리하지 않고 교사 확인 전까지 보류한다.', '경계 사례는 근거를 다시 확인하여 교사가 판단한다.')
    new_video = '<p><strong>먼저 질문 선택 영상을 보세요.</strong> 여러 분석 질문과 현재 11열 CSV를 소개합니다. 이어서 실제 Orange 화면 영상에서 두 갈래 연결과 표·그래프를 확인하세요.</p><video controls preload="metadata" poster="assets/01_question_choices.png"><source src="diversity_addendum.mp4" type="video/mp4"><track kind="captions" src="diversity_addendum.vtt" srclang="ko" label="한국어" default></video><p><a href="diversity_addendum.mp4" download>질문과 현재 자료 확인 영상 내려받기</a></p>'
    page = page.replace('<video id="reference-video"', new_video + '<video id="reference-video"', 1)
    page = page.replace('CSV 조작 참고 영상(10월 21일 촬영)', '현재 11열 CSV를 연 Orange 실제 화면(10월 25일 다시 캡처)')
    page = page.replace('<div class="actions"><button class="secondary" type="button" data-seek="30">00:30 자료 열기로 이동</button><button class="secondary" type="button" data-seek="65">01:05 도구 연결로 이동</button><button class="secondary" type="button" data-seek="99">01:39 그래프 보기로 이동</button><button class="secondary" type="button" data-seek="135">02:15 저장하기로 이동</button></div>', '<div class="actions"><button class="secondary" type="button" data-seek="0">00:00 두 갈래 연결</button><button class="secondary" type="button" data-seek="27">00:27 표 확인</button><button class="secondary" type="button" data-seek="46">00:46 산점도 확인</button></div>')
    media = ROOT / "orange-media"
    for filename in ("manual.mp4", "subtitles.vtt", "diversity_addendum.mp4", "diversity_addendum.vtt"):
        source = media / {"manual.mp4": "manual-recaptured.mp4", "subtitles.vtt": "subtitles-recaptured.vtt"}.get(filename, filename)
        page = re.sub(rf'src="{re.escape(filename)}(?:\?v=[^\"]*)?"',
                      f'src="{filename}?v={media_stamp(source)}"', page)
    recapture = media / "recapture"
    for source, dest in (("00-file-top.png", "csv_video_import.png"),
                         ("03-table.png", "csv_video_table.png"),
                         ("04-scatter-participation-performance.png", "csv_video_result.png"),
                         ("02-canvas-branch.png", "csv_video_reopened.png"),
                         ("02-canvas-branch.png", "file-two-branches.png"),
                         ("05-scatter-activity-satisfaction.png", "alternative-scatter.png")):
        page = page.replace(f'assets/{dest}"', f'assets/{dest}?v={media_stamp(recapture / source)}"')
    return add_guide_nav(page, 'orange-guide', 'orange.html', 'python.html')


def exercise_example_block(source: Path) -> str:
    notebook = json.loads(source.read_text(encoding='utf-8'))
    labels = {3: '1. 내 자료', 5: '2. NumPy 계산', 7: '3. pandas 표', 9: '4. Matplotlib 그래프'}
    blocks = ''.join(f'<h4>{title}</h4><pre class="notebook-code"><code>{escape("".join(notebook["cells"][index]["source"]))}</code></pre>' for index, title in labels.items())
    return '<details id="exercise-code"><summary>운동 시간으로 바꾼 예시 보기 · 코드 펼치기</summary><div class="detail-body"><p>아래는 내려받는 예시 노트북의 주요 코드입니다. 내 자료 셀만 바꾸어 실행하세요.</p>' + blocks + '</div></details>'


def build_orange() -> None:
    manual = SOURCE / "1차_Orange_실습매뉴얼"
    dataset = SOURCE / "2026_DS_Orange_주제별_가상데이터"
    new_data = ROOT / "orange-data"
    guide = PUBLIC / "orange-guide"
    guide.mkdir(parents=True, exist_ok=True)
    (guide / "index.html").write_text(revise_orange_guide((manual / "index_student.html").read_text()))
    for name in ["학생용_한장안내.pdf", "설문응답_작성가이드.pdf", "학생용_한장안내.md", "설문응답_작성가이드.md"]:
        copy(manual / name, guide / name)
    copy(manual / "assets" / "00_new.png", guide / "assets" / "00_new.png")
    recapture = ROOT / "orange-media" / "recapture"
    for source, dest in [
        ("00-file-top.png", "csv_video_import.png"),
        ("03-table.png", "csv_video_table.png"),
        ("04-scatter-participation-performance.png", "csv_video_result.png"),
        ("02-canvas-branch.png", "csv_video_reopened.png"),
        ("02-canvas-branch.png", "file-two-branches.png"),
        ("05-scatter-activity-satisfaction.png", "alternative-scatter.png"),
    ]:
        copy(recapture / source, guide / "assets" / dest)
    media = ROOT / "orange-media"
    copy(media / "manual-recaptured.mp4", guide / "manual.mp4")
    copy(media / "subtitles-recaptured.vtt", guide / "subtitles.vtt")
    for name in ["01_question_choices.png", "02_axes_workflow.png", "03_real_orange_capture.png", "04_capture_checklist.png"]:
        copy(media / name, guide / "assets" / name)
    for name in ["current-11-file-top.jpg", "current-11-file-bottom.jpg"]:
        copy(media / name, guide / "assets" / name)
    copy(media / "diversity_addendum.mp4", guide / "diversity_addendum.mp4")
    copy(media / "diversity_addendum.vtt", guide / "diversity_addendum.vtt")
    copy(media / "diversity_addendum.mp4", guide / "question-choices.mp4")
    copy(media / "diversity_addendum.vtt", guide / "question-choices.vtt")
    copy(new_data / "orange-csv-30-v2.zip", guide / "downloads" / "학생배포_CSV_30주제.zip")
    copy(dataset / "학생배포_Excel_원본보관.zip", guide / "downloads" / "학생배포_Excel_원본보관.zip")
    copy(new_data / "orange-csv-30-v2.zip", PUBLIC / "files" / "orange-csv-30.zip")
    example_ows = guide / "downloads" / "제출예시" / "CSV_시연_11_로봇.ows"
    copy(manual / "downloads" / "제출예시" / "CSV_시연_11_로봇.ows", example_ows)
    workflow = example_ows.read_text(encoding="utf-8")
    for node_id, position in (("0", "(120, 210)"), ("1", "(360, 80)"), ("2", "(360, 340)")):
        pattern = rf'(<node id="{node_id}"[^>]*position=")[^"]+(" />)'
        workflow, count = re.subn(pattern, lambda match: match.group(1) + position + match.group(2), workflow, count=1)
        assert count == 1, f"Orange example is missing widget {node_id}"
    example_ows.write_text(workflow, encoding="utf-8")
    csv_root = new_data / "CSV"
    rows = []
    for csv in sorted(csv_root.glob("[0-9][0-9]_*.csv")):
        copy(csv, guide / "downloads" / "학생배포" / "CSV" / csv.name)
        rows.append(file_item(f"orange-guide/downloads/학생배포/CSV/{csv.name}", csv.stem, "CSV 한 개"))
    assert len(rows) == 30, f"Expected 30 CSV files, found {len(rows)}"
    body = '''<div class="hero"><p class="number">1차 수행평가 · Orange</p><h1>자료 하나로<br>그래프 하나 만들기</h1>
<p class="lead">관심 있는 자료를 골라 표와 그래프를 만들고, 발견한 내용을 내 말로 설명합니다.</p>
<div class="date"><strong>평가 11월 2~6일</strong><strong>제출 마감 11월 6일 23:59</strong></div></div>
<div class="route">자료 선택 <span>→</span> 표·그래프 <span>→</span> 파일·화면 저장 <span>→</span> 답변 7개 <span>→</span> 설문 제출</div>'''
    body += section("먼저 받을 자료", '<p>30개 주제 중 마음에 드는 <strong>CSV 한 개</strong>를 고르세요. 파일마다 가상 사례 180개와 공통 열 11개가 있어 표와 그래프를 연습할 수 있습니다. 실제 사람의 기록이 아니며, 다른 주제나 직접 준비한 자료를 써도 됩니다.</p><ul class="resource-list">' +
        file_item("files/orange-csv-30.zip", "CSV 30종 한 번에 받기", "여러 주제를 둘러볼 때") +
        file_item("#topics", "CSV 한 개씩 고르기", "필요한 주제만 받기") +
        file_item("orange-guide/index.html", "화면을 따라 하는 실습 가이드", "불러오기·연결·캡처·설문 제출") +
        file_item("orange-guide/학생용_한장안내.pdf", "한 장 안내 PDF", "빠르게 순서 확인") +
        file_item("orange-guide/설문응답_작성가이드.pdf", "답변 작성 가이드 PDF", "일곱 문항과 작성 예시") +
        '</ul>')
    body += section("분석 질문을 먼저 고르세요", question_cards(), "questions")
    body += section("순서대로 해 보세요", '''<ol class="steps"><li><strong>CSV를 Orange에 불러오기</strong><p>File로 CSV를 읽습니다. Data Table을 오른쪽 위에 두고 File에서 연결하면 행·열·빈칸을 표로 확인할 수 있습니다.</p></li>
<li><strong>질문에 맞는 그래프 만들기</strong><p>Scatter Plot을 오른쪽 아래에 두고 File에서 직접 연결합니다. 같은 자료가 표와 산점도로 각각 전달됩니다. 선택한 질문에 맞춰 가로축·세로축·색을 고릅니다. <a href="orange-guide/index.html#practice">두 연결의 이유와 실제 배치 화면 보기</a></p></li>
<li><strong>파일과 화면 저장</strong><p>Orange 작업 파일(.ows), 전체 연결 화면 1장, 주요 결과 화면 1장을 준비합니다. 저장한 .ows를 다시 열어 확인하세요.</p></li>
<li><strong>일곱 답변 작성</strong><p>결과물, 자료 구성, 연결 이유, 발견한 점과 근거, 진로·학업 도움, 느낀 점, 아쉬움·보완점을 각각 적습니다.</p></li>
<li><strong>Google 설문으로 제출</strong><p>학번·이름·과제 제목, 일곱 답변과 파일을 차례대로 넣고 접수 완료 화면을 확인합니다.</p></li></ol>''', "steps")
    body += section("제출 전 확인", '''<div class="callout"><strong>제출물</strong><p>.ows 파일 1개 + 전체 연결 화면 1장 + 결과 화면 1장 + 설문 답변 7개</p><p>교사 제공 CSV는 주제 번호만 적습니다. 직접 준비한 자료라면 실제 사용한 CSV·Excel 원본과 출처를 함께 제출하고, Excel의 시트 이름도 적습니다.</p></div>
<p>30점 = 답변 21점 + 자료 읽기·연결 4점 + 분석 결과 5점. 답변은 문항에 맞는 완결 문장 3개 이상 3점, 2개 2점, 1개 1점, 없으면 0점입니다. 같은 뜻의 반복은 한 번만 셉니다.</p>
<p>파일 문제로 막히면 준비된 답변과 파일부터 11월 6일 23:59까지 제출하고 교사에게 알리세요. 원래 작업의 누락·손상·경로 문제는 11월 9일 23:59까지 보완할 수 있습니다. 그 기간에 답변 수정이나 새 분석을 추가할 수는 없습니다.</p>''')
    body += section("실습 영상", '<p>먼저 질문 선택 영상에서 다양한 축을 살펴보세요. 다음 영상은 현재 11열 CSV를 연 실제 Orange 화면에서 File의 두 갈래 연결, 표, 그래프를 보여 줍니다. 참여·성과는 조작 예시 한 가지이므로 자신의 질문에 맞춰 축과 색을 바꾸세요.</p><video controls preload="metadata" width="100%"><source src="orange-guide/question-choices.mp4" type="video/mp4"><track kind="captions" src="orange-guide/question-choices.vtt" srclang="ko" label="한국어" default></video><p>' + link("orange-guide/question-choices.mp4", "질문 선택 영상 받기") + '</p><video controls preload="metadata" width="100%" poster="orange-guide/assets/file-two-branches.png"><source src="orange-guide/manual.mp4" type="video/mp4"><track kind="captions" src="orange-guide/subtitles.vtt" srclang="ko" label="한국어" default></video><p>' + link("orange-guide/manual.mp4", "기본 조작 영상 받기") + '</p>')
    body += section("주제별 CSV", '<p>하나만 골라도 됩니다. 내려받은 CSV의 내용은 바꾸지 말고 자신의 Orange 작업 파일을 만드세요.</p><ul class="topic-list">' + ''.join(rows) + '</ul>', "topics")
    body += '<div class="submit"><div><h2>이제 제출하세요</h2><p>Google 계정으로 설문을 열고 답변과 파일을 확인한 뒤, 제출 완료 화면까지 보세요.</p></div>' + link(ORANGE_FORM, "1차 제출 설문 열기", "button") + '</div>'
    for filename, source in (("manual.mp4", media / "manual-recaptured.mp4"),
                             ("subtitles.vtt", media / "subtitles-recaptured.vtt"),
                             ("question-choices.mp4", media / "diversity_addendum.mp4"),
                             ("question-choices.vtt", media / "diversity_addendum.vtt"),
                             ("assets/file-two-branches.png", recapture / "02-canvas-branch.png")):
        body = body.replace(f'"orange-guide/{filename}"',
                            f'"orange-guide/{filename}?v={media_stamp(source)}"')
    (PUBLIC / "orange.html").write_text(shell("1차 Orange 수행평가", "orange", body))


def build_python() -> None:
    source = SOURCE / "2차_파이썬_쉬운가이드_20261022"
    guide = PUBLIC / "python-guide"
    page = (source / "index.html").read_text()
    page = page.replace("AI는 채점 초안과 근거를 돕고 선생님이 최종 확인합니다.", "선생님이 제출 내용과 실행 결과를 확인하여 최종 평가합니다.")
    page = page.replace("https://colab.research.google.com/drive/1_jHFBKldDwVPT8eoHbUKqPVfGCnUO34Q", "기본예시_축제.ipynb")
    page = page.replace("https://colab.research.google.com/drive/1REZUbCgR0sa2hXKjVj6ElN86NMrQp7Lw", "제출예시_운동시간.ipynb")
    old_starter = '<a class="button" href="기본예시_축제.ipynb" target="_blank" rel="noopener">축제 예시 Colab에서 열기</a>'
    assert old_starter in page
    page = page.replace(old_starter, '<a class="button" href="기본예시_축제.ipynb" download>축제 기본 예시 파일 받기</a><a class="button secondary" href="https://colab.research.google.com/" target="_blank" rel="noopener">Google Colab 열기</a>')
    page = page.replace('<a class="button secondary" href="기본예시_축제.ipynb" download>기본 예시 파일 받기</a>', '')
    page = page.replace('교사가 제공한 축제 예시에서 시작합니다. 원본을 열자마자 <strong>내 Drive에 사본</strong>을 만드세요.', '축제 기본 예시 파일을 먼저 받으세요. Google Colab을 열어 받은 <code>.ipynb</code> 파일을 업로드한 뒤 <strong>내 Drive에 사본</strong>을 만드세요.')
    page = page.replace('Colab 화면 위쪽의 파일 → Drive에 사본 저장을 누릅니다.', 'Colab에서 파일 → 노트 열기 → 업로드 → Browse로 받은 예시 노트북을 엽니다. 열린 노트북에서 파일 → Drive에 사본 저장을 누릅니다.')
    page = page.replace('교사가 시험한 Colab 기본 예시 화면. 자신의 사본에서 작업합니다.', '운동 시간으로 바꾼 Colab 시연 화면. 처음 받은 축제 예시와 값이 다르므로 자신의 사본에서 작업합니다.')
    upload_figure = '<figure><a href="images/colab-upload-current.jpg" target="_blank" rel="noopener"><img loading="lazy" src="images/colab-upload-current.jpg" alt="현재 Google Colab의 Open notebook 창에서 Upload 탭과 Browse 버튼을 선택하는 화면"></a><figcaption>현재 Colab의 업로드 창. 안내 페이지에서 받은 .ipynb 파일을 Browse로 선택합니다. · 누르면 크게 볼 수 있습니다.</figcaption></figure>'
    page = page.replace('<figure><a href="images/02-colab.png"', upload_figure + '<figure><a href="images/02-colab.png"', 1)
    old_button = '<a class="button secondary" href="제출예시_운동시간.ipynb" target="_blank" rel="noopener">운동 시간으로 바꾼 예시 보기</a>'
    assert old_button in page, "Python example button changed in source"
    page = page.replace(old_button, '')
    anchor = '<a class="button secondary" href="제출예시_운동시간.ipynb" download>바꾼 예시 파일 받기</a></div>'
    assert anchor in page
    page = page.replace(anchor, anchor + exercise_example_block(source / "제출예시_운동시간.ipynb"))
    page = page.replace('</head>', '<style>.notebook-code{overflow-x:auto;white-space:pre;max-height:440px;overflow-y:auto;padding:16px;background:#162321;color:#effaf1;border-radius:8px;line-height:1.5}.notebook-code code{background:transparent;color:inherit;padding:0}.detail-body h4{margin:20px 0 6px}</style></head>', 1)
    page = add_guide_nav(page, 'python-guide', 'python.html', 'index.html')
    (guide / "index.html").parent.mkdir(parents=True, exist_ok=True)
    (guide / "index.html").write_text(page)
    for name in ["기본예시_축제.ipynb", "제출예시_운동시간.ipynb"]:
        copy(source / name, guide / name)
    python_media = ROOT / "python-media"
    for name in ["쉬운_동영상_매뉴얼.mp4", "자막.vtt", "대본.txt"]:
        copy(python_media / name, guide / name)
    copy(python_media / "colab-upload-current.jpg", guide / "images" / "colab-upload-current.jpg")
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


def version_caption_tracks() -> None:
    """Force browsers to fetch revised VTT files after each Pages deployment."""
    for page in PUBLIC.rglob("*.html"):
        html = page.read_text(encoding="utf-8")

        def add_version(match):
            caption = page.parent / match.group(2)
            if not caption.is_file():
                return match.group(0)
            version = sha256(caption.read_bytes()).hexdigest()[:10]
            return f"{match.group(1)}{match.group(2)}?v={version}{match.group(3)}"

        updated = re.sub(r'(<track[^>]*\bsrc=")([^"]+\.vtt)(")', add_version, html)
        if updated != html:
            page.write_text(updated, encoding="utf-8")


def main() -> None:
    PUBLIC.mkdir(exist_ok=True)
    (PUBLIC / ".nojekyll").touch()
    copy(ROOT / "caption-panel.css", PUBLIC / "caption-panel.css")
    copy(ROOT / "caption-panel.js", PUBLIC / "caption-panel.js")
    build_orange()
    build_python()
    build_index()
    version_caption_tracks()


if __name__ == "__main__":
    main()
