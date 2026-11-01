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
SUBMISSION_STYLE_VERSION = sha256((ROOT / "submission-practice.css").read_bytes()).hexdigest()[:10]


def media_stamp(path: Path) -> str:
    return sha256(path.read_bytes()).hexdigest()[:10]

ORANGE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSel8D22f8y8r0tWJYpux0EIqAKeGsD56wiYdUVHdgLPBNUaJA/viewform"
PYTHON_FORM = "https://docs.google.com/forms/d/e/1FAIpQLSdb_FYb6h-rQgikGn8_F4y0rpf1DCMkWUvg1huvRV6fmeYClA/viewform"
PRACTICE_FORM = "https://docs.google.com/forms/d/e/1FAIpQLScZOqpPs9S-6z6NNaMuyRPG4v95KnQXw4QXtG5yP9WdSp2YLQ/viewform"


def copy(source: Path, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, dest)


def link(url: str, label: str, css: str = "") -> str:
    external = url.startswith("https://")
    attrs = ' target="_blank" rel="noopener noreferrer"' if external else (' download' if Path(url.split('#')[0]).suffix.lower() in {'.csv', '.zip', '.ipynb', '.pdf', '.mp4', '.ows', '.txt'} else '')
    return f'<a class="{css}" href="{escape(url, quote=True)}"{attrs}>{escape(label)}</a>'


def global_nav(active: str, prefix: str = "") -> str:
    items = [("home", "메인", "index.html"), ("practice", "연습 제출", "practice.html"), ("orange", "1차 안내", "orange.html"), ("orange-guide", "1차 실습", "orange-guide/index.html"), ("python", "2차 안내", "python.html"), ("python-guide", "2차 실습", "python-guide/index.html")]
    links = ""
    for key, label, path in items:
        current = ' aria-current="page"' if key == active else ""
        links += f'<a href="{prefix}{path}"{current}>{label}</a>'
    return f'<nav class="global-nav" aria-label="전체 페이지 빠른 이동">{links}</nav>'


def login_notice(prefix: str = "") -> str:
    return ('<aside class="login-notice" aria-label="제출 전 필수 안내"><div class="login-notice-inner">'
        '<p class="submission-notice-title"><span class="login-required">필수</span> 설문 작성·파일 제출 전에 꼭 확인하세요</p>'
        '<div class="submission-rules"><div class="submission-rule"><strong>① 개인 Google 계정 로그인 → 설문 작성</strong>'
        '<p>먼저 <b>반드시 본인의 개인 Google 계정으로 로그인하세요.</b> 로그인한 뒤 설문지를 작성합니다. 설문 위쪽 이메일이 내 계정인지 확인하세요.</p></div>'
        '<div class="submission-rule"><strong>② 모든 제출 파일명에 학번_이름 필수</strong>'
        '<p>파일 이름 맨 앞에 <b>본인의 학번과 이름</b>을 적으세요. 여러 파일은 뒤에 내용을 덧붙이고, <b>확장자는 그대로</b> 유지합니다.</p>'
        '<p class="submission-name-example">예: <code>20601_홍길동.ows</code> · <code>20601_홍길동_연결화면.png</code> · <code>20601_홍길동.ipynb</code></p>'
        '</div></div><p class="submission-scope">1차·2차 수행평가와 연습 제출 모두 적용합니다. 예시의 학번·이름은 본인의 것으로 바꾸세요.</p>'
        '<div class="login-notice-links">' + link(prefix + "practice.html", "처음이라면 파일 제출 연습부터 →") + ' · ' +
        link(PRACTICE_FORM, "연습용 Google 설문 열기") + '</div></div></aside>')


def shell(title: str, active: str, body: str) -> str:
    caption_assets = f'<link rel="stylesheet" href="caption-panel.css"><script src="caption-panel.js?v={CAPTION_SCRIPT_VERSION}" defer></script>' if '<video' in body else ''
    return f'''<!doctype html>
<html lang="ko"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="description" content="2026 데이터과학 수행평가 학생 안내와 실습 자료">
<title>{escape(title)} · 2026 데이터과학</title><link rel="stylesheet" href="styles.css"><link rel="stylesheet" href="submission-practice.css?v={SUBMISSION_STYLE_VERSION}">{caption_assets}</head>
<body><a class="skip" href="#content">본문으로 바로 가기</a>
{login_notice()}
<header class="site-header"><div class="wrap header-inner"><a class="brand" href="index.html">2026 데이터과학 <span>수행평가 안내</span></a>
{global_nav(active)}</div></header>
<main class="wrap" id="content">{body}</main><footer class="wrap footer">{global_nav(active)}<p>고2 6·7·8·9반 · 자료와 제출 방법은 이 페이지에서 확인하세요. 제출은 Google 로그인이 필요합니다.</p></footer>
</body></html>'''


def add_guide_nav(page: str, active: str, previous: str, next_page: str) -> str:
    page = page.replace('학교에서 안내한 Google 계정으로', '반드시 본인의 개인 Google 계정으로 먼저 로그인한 뒤')
    page = page.replace('파일을 추가할 때 Google 로그인이 필요합니다.', '설문을 작성하기 전에 본인의 개인 Google 계정으로 로그인해야 합니다. 모든 첨부 파일 이름에 학번_이름이 들어 있는지 확인하세요.')
    page = page.replace('이 이름은 파일을 찾기 위한 권장 예시입니다.', '제출 파일 이름에는 본인의 학번과 이름을 반드시 넣습니다. 뒤의 주제명은 바꿔도 됩니다.')
    page = page.replace('방금 다운로드한 .ipynb 파일 1개를 골라 업로드하고,', '방금 다운로드한 .ipynb 파일 이름에 본인의 학번_이름을 적은 뒤 파일 1개를 골라 업로드하고,')
    page = page.replace('과제 제목·학번·이름을 적습니다.', '먼저 본인의 개인 Google 계정으로 로그인하고 표시된 이메일을 확인한 뒤 과제 제목·학번·이름을 적습니다.')
    page = page.replace('파일 이름과 출처를 적고 실제 사용한 원본 CSV·Excel을 모두 올립니다.', '실제로 제출할 개인 원본 CSV·Excel의 파일 이름에도 본인의 학번_이름을 넣습니다. 이름을 바꿨다면 Orange의 File에서 다시 연결하고 .ows를 저장해 확인하세요. 파일 이름과 출처를 적고 실제 사용한 원본을 모두 올립니다.')
    nav = '<div class="assessment-nav"><div class="assessment-nav-inner">' + global_nav(active, "../") + f'<div class="assessment-neighbors"><a href="../{previous}">← 이전 페이지</a><a href="../{next_page}">다음 페이지 →</a></div></div></div>'
    page = page.replace('<body>', '<body>' + login_notice("../") + nav, 1)
    css = '<style>.assessment-nav{position:sticky;top:0;z-index:100;background:#fff;border-bottom:2px solid #145c4c;box-shadow:0 3px 10px #0001}.assessment-nav-inner{max-width:1050px;margin:auto;padding:8px 16px;display:flex;flex-wrap:wrap;align-items:center;justify-content:space-between;gap:8px}.assessment-nav .global-nav{display:flex;flex-wrap:wrap;gap:4px}.assessment-nav a{display:inline-block;padding:7px 10px;border-radius:6px;color:#173d33;text-decoration:none;font-size:14px;font-weight:700}.assessment-nav a:hover,.assessment-nav a[aria-current=page]{background:#c5e8da}.assessment-neighbors{display:flex;gap:4px}.question-choices{padding:18px;background:#eaf3ef;border:1px solid #cbd8d1;border-radius:12px;margin:20px 0}.question-choices ol{list-style:none;display:grid;grid-template-columns:repeat(2,minmax(0,1fr));gap:8px;padding:0}.question-choices li{background:#fff;padding:11px;border-radius:7px;border:1px solid #cbd8d1}.question-choices li strong,.question-choices li span{display:block}.question-choices li span{font-size:13px}.question-choices code{white-space:nowrap}.diversity-visual{max-width:100%}@media(max-width:600px){.assessment-nav-inner{padding:4px 8px}.assessment-nav a{font-size:12px;padding:6px}.assessment-neighbors{width:100%;justify-content:space-between}.question-choices ol{grid-template-columns:1fr}}</style>'
    if active == "orange-guide":
        css = css.replace("</style>", ".branch-layout{width:min(100%,572px);margin-inline:auto}.branch-layout img{width:100%}</style>", 1)
    assets = f'<link rel="stylesheet" href="../submission-practice.css?v={SUBMISSION_STYLE_VERSION}"><link rel="stylesheet" href="../caption-panel.css"><script src="../caption-panel.js?v={CAPTION_SCRIPT_VERSION}" defer></script>'
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
    page = page.replace('CSV를 불러오고 두 도구를 연결하는 기존 실제 화면 시연입니다.', '새 작업 화면에서 위젯 세 개를 배치하고 현재 11열 CSV를 불러온 다음, File의 두 갈래 연결, Data Table의 표, Scatter Plot의 축과 색을 보여 줍니다. 참여·성과는 조작 예시 한 가지이며 자신의 질문에 맞춰 축과 색을 바꾸세요.')
    page = page.replace('<p class="small">완성 예시를 보는 목적은 연결과 결과를 이해하는 것입니다.', '<p class="small">다른 컴퓨터에서 완성 예시 OWS를 열면 File 위젯에서 내려받은 같은 번호 CSV를 다시 선택하세요. 자신의 질문으로 분석한 작업 파일은 따로 저장하세요.</p><p class="small">완성 예시를 보는 목적은 연결과 결과를 이해하는 것입니다.')
    page = page.replace('경계 사례는 AI가 임의로 0점 처리하지 않고 교사 확인 전까지 보류한다.', '경계 사례는 근거를 다시 확인하여 교사가 판단한다.')
    page = page.replace('기술 복원 기한 뒤에도 OWS', '교사의 확인을 거친 뒤에도 OWS')
    new_video = '<p><strong>먼저 질문 선택 영상을 보세요.</strong> 여러 분석 질문과 현재 11열 CSV를 소개합니다. 이어서 실제 Orange 화면 영상에서 새 화면 열기, 위젯 배치, CSV 불러오기, 두 갈래 연결과 표·그래프를 순서대로 따라 하세요.</p><video controls preload="metadata" poster="assets/01_question_choices.png"><source src="diversity_addendum.mp4" type="video/mp4"><track kind="captions" src="diversity_addendum.vtt" srclang="ko" label="한국어" default></video><p><a href="diversity_addendum.mp4" download>질문과 현재 자료 확인 영상 내려받기</a></p>'
    page = page.replace('<video id="reference-video"', new_video + '<video id="reference-video"', 1)
    page = page.replace('CSV 조작 참고 영상(10월 21일 촬영)', '현재 11열 CSV를 연 Orange 실제 화면(10월 26일 시작 단계 보완)')
    page = page.replace('poster="assets/file-two-branches.png" aria-label="실제 화면으로 보는 CSV Orange 실습"', 'poster="assets/csv_video_start.png" aria-label="새 화면부터 시작하는 CSV Orange 실습"')
    page = page.replace('<div class="actions"><button class="secondary" type="button" data-seek="30">00:30 자료 열기로 이동</button><button class="secondary" type="button" data-seek="65">01:05 도구 연결로 이동</button><button class="secondary" type="button" data-seek="99">01:39 그래프 보기로 이동</button><button class="secondary" type="button" data-seek="135">02:15 저장하기로 이동</button></div>', '<div class="actions"><button class="secondary" type="button" data-seek="0">00:00 새 화면·위젯 배치</button><button class="secondary" type="button" data-seek="14">00:14 CSV 선택</button><button class="secondary" type="button" data-seek="26">00:26 두 갈래 연결</button><button class="secondary" type="button" data-seek="53">00:53 표 확인</button><button class="secondary" type="button" data-seek="72">01:12 산점도 확인</button></div>')
    media = ROOT / "orange-media"
    for filename in ("manual.mp4", "subtitles.vtt", "diversity_addendum.mp4", "diversity_addendum.vtt"):
        source = media / {"manual.mp4": "manual-recaptured.mp4", "subtitles.vtt": "subtitles-recaptured.vtt"}.get(filename, filename)
        page = re.sub(rf'src="{re.escape(filename)}(?:\?v=[^\"]*)?"',
                      f'src="{filename}?v={media_stamp(source)}"', page)
    recapture = media / "recapture"
    for source, dest in (("00f-three-widgets-unconnected.png", "csv_video_start.png"),
                         ("00-file-top.png", "csv_video_import.png"),
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
        ("00f-three-widgets-unconnected.png", "csv_video_start.png"),
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
<div class="date"><strong>평가: 11월 2~6일</strong><strong>제출 마감: 2026년 11월 6일까지</strong></div>
</div>
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
<li><strong>개인 Google 계정 로그인 후 설문으로 제출</strong><p>로그인한 계정을 확인한 뒤 학번·이름·과제 제목과 일곱 답변을 작성합니다. 모든 제출 파일 이름에 학번_이름을 적어 첨부하고 접수 완료 화면을 확인합니다.</p></li></ol>''', "steps")
    body += section("제출 전 확인", '''<div class="callout"><strong>제출물</strong><p>.ows 파일 1개 + 전체 연결 화면 1장 + 결과 화면 1장 + 설문 답변 7개</p><p>교사 제공 CSV는 주제 번호만 적습니다. 직접 준비한 자료라면 실제 사용한 CSV·Excel 원본과 출처를 함께 제출하고, Excel의 시트 이름도 적습니다.</p></div>
<div class="filename-check"><strong>파일명 확인: 학번_이름을 반드시 적으세요</strong><ul><li>작업 파일: <code>20601_홍길동.ows</code></li><li>전체 연결 화면: <code>20601_홍길동_연결화면.png</code></li><li>분석 결과 화면: <code>20601_홍길동_분석결과.png</code></li><li>개인 자료를 제출하는 경우: <code>20601_홍길동_자료.csv</code> 또는 <code>20601_홍길동_자료.xlsx</code></li></ul><p>본인의 학번·이름으로 바꾸고 실제 파일의 확장자는 유지하세요. 개인 자료 파일 이름을 바꿨다면 Orange의 File에서 다시 연결하고 .ows를 저장한 뒤 표·그래프가 열리는지 확인하세요.</p></div>
<p>30점 = 답변 21점 + 자료 읽기·연결 4점 + 분석 결과 5점. 답변은 문항에 맞는 완결 문장 3개 이상 3점, 2개 2점, 1개 1점, 없으면 0점입니다. 같은 뜻의 반복은 한 번만 셉니다.</p>
<p>파일 문제가 생기면 준비된 답변과 파일을 마감일까지 제출하고 교사에게 알리세요.</p>''')
    body += section("실습 영상", '<p>먼저 질문 선택 영상에서 다양한 축을 살펴보세요. 다음 영상은 새 작업 화면에서 위젯을 배치하고 현재 11열 CSV를 불러온 뒤 File의 두 갈래 연결, 표, 그래프를 순서대로 보여 줍니다. 참여·성과는 조작 예시 한 가지이므로 자신의 질문에 맞춰 축과 색을 바꾸세요.</p><video controls preload="metadata" width="100%"><source src="orange-guide/question-choices.mp4" type="video/mp4"><track kind="captions" src="orange-guide/question-choices.vtt" srclang="ko" label="한국어" default></video><p>' + link("orange-guide/question-choices.mp4", "질문 선택 영상 받기") + '</p><video controls preload="metadata" width="100%" poster="orange-guide/assets/csv_video_start.png"><source src="orange-guide/manual.mp4" type="video/mp4"><track kind="captions" src="orange-guide/subtitles.vtt" srclang="ko" label="한국어" default></video><p>' + link("orange-guide/manual.mp4", "기본 조작 영상 받기") + '</p>')
    body += section("주제별 CSV", '<p>하나만 골라도 됩니다. 내려받은 CSV의 내용은 바꾸지 말고 자신의 Orange 작업 파일을 만드세요.</p><ul class="topic-list">' + ''.join(rows) + '</ul>', "topics")
    body += '<div class="submit"><div><h2>이제 제출하세요</h2><p><strong>개인 Google 계정 로그인 후 작성 · 모든 파일명에 학번_이름 필수</strong></p><p>답변과 첨부파일을 확인하고 제출 완료 화면까지 보세요.</p></div>' + link(ORANGE_FORM, "1차 제출 설문 열기", "button") + '</div>'
    for filename, source in (("manual.mp4", media / "manual-recaptured.mp4"),
                             ("subtitles.vtt", media / "subtitles-recaptured.vtt"),
                             ("question-choices.mp4", media / "diversity_addendum.mp4"),
                             ("question-choices.vtt", media / "diversity_addendum.vtt"),
                             ("assets/csv_video_start.png", recapture / "00f-three-widgets-unconnected.png")):
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
<div class="date"><strong>평가: 11월 9~13일</strong><strong>제출 마감: 2026년 11월 13일까지</strong></div></div>
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
<li><strong>개인 Google 계정 로그인 후 설문으로 제출</strong><p>로그인한 계정을 확인한 뒤 학번·이름·과제 제목과 일곱 답변을 작성합니다. .ipynb 파일 이름에 학번_이름을 적어 첨부하고 접수 완료 화면을 확인합니다.</p></li></ol>''', "steps")
    body += section("제출 전 확인", '''<div class="callout"><strong>제출물</strong><p>실행 결과가 저장된 .ipynb 파일 1개(10MB 이하) + 설문 답변 7개</p><p>필요한 숫자는 노트북 안에 넣습니다. 별도 CSV·Excel·화면 캡처·수정 일지는 필수가 아닙니다.</p></div>
<div class="filename-check"><strong>파일명 확인: 학번_이름을 반드시 적으세요</strong><p>예: <code>20601_홍길동.ipynb</code> 또는 <code>20601_홍길동_운동시간.ipynb</code></p><p>본인의 학번·이름으로 바꾸고 <b>.ipynb 확장자는 그대로</b> 유지하세요. 설문지에 첨부된 파일 이름도 확인합니다.</p></div>
<p>답변 7개에는 자료·결과 소개, 어려움, 바꾼 부분과 달라진 결과, 코드 한 부분의 역할, 활용하고 싶은 곳, 배운 점, 다음 보완점을 적습니다.</p>
<p>30점 = 답변 21점 + NumPy·pandas·Matplotlib 활용과 실행 9점. 답변은 문항에 맞는 완결 문장 3개 이상 3점, 2개 2점, 1개 1점, 없으면 0점입니다. 기본정보는 무배점입니다.</p>
<p>실행이 막히면 이름과 숫자의 개수, 쉼표·따옴표·대괄호를 확인하고 다시 모두 실행하세요. 제출 마감은 2026년 11월 13일까지입니다.</p>''')
    body += section("실습 영상", '<video controls preload="metadata" width="100%"><source src="python-guide/쉬운_동영상_매뉴얼.mp4" type="video/mp4"><track kind="captions" src="python-guide/자막.vtt" srclang="ko" label="한국어" default></video><p>' + link("python-guide/쉬운_동영상_매뉴얼.mp4", "영상 파일 받기") + '</p>')
    body += '<div class="submit"><div><h2>이제 제출하세요</h2><p><strong>개인 Google 계정 로그인 후 작성 · 파일명에 학번_이름 필수</strong></p><p>실행 결과가 들어 있는 .ipynb 파일을 첨부하고 일곱 답변을 작성하세요.</p></div>' + link(PYTHON_FORM, "2차 제출 설문 열기", "button") + '</div>'
    (PUBLIC / "python.html").write_text(shell("2차 Python 수행평가", "python", body))


def build_index() -> None:
    body = '''<div class="hero index-hero"><h1>2026 데이터과학<br>수행평가 안내</h1><p class="lead">1차와 2차 안내, 실습 자료, 제출 순서를 한곳에서 확인하세요.</p></div>
<section class="section"><h2>처음 제출한다면 먼저 연습하세요</h2><p>개인 Google 계정 로그인부터 파일 첨부, 제출 완료 화면 확인까지 연습합니다. 연습은 성적에 반영되지 않으며, 실제 수행평가는 아래 1차·2차 설문에 따로 제출합니다.</p><a class="button" href="practice.html">파일 제출 연습과 사용 방법 →</a></section>
<div class="choice-grid"><a class="choice" href="orange.html"><span>1차 · Orange</span><h2>자료 하나로 그래프 하나 만들기</h2><p>평가: 11월 2~6일 · 제출 마감: 2026년 11월 6일까지</p><strong>안내와 자료 보기 →</strong></a>
<a class="choice" href="python.html"><span>2차 · Python</span><h2>내 자료로 계산·표·그래프 만들기</h2><p>평가: 11월 9~13일 · 제출 마감: 2026년 11월 13일까지</p><strong>안내와 자료 보기 →</strong></a></div>
<section class="section"><h2>제출 순서</h2><p>각 페이지에서 필요한 파일을 받고 실습 방법을 익힌 뒤, 해당 Google 설문에 일곱 답변과 파일을 차례대로 넣습니다. 마지막 접수 완료 화면까지 확인하세요.</p></section>'''
    (PUBLIC / "index.html").write_text(shell("수행평가 안내", "", body))


def build_practice() -> None:
    if not PRACTICE_FORM.startswith("https://docs.google.com/forms/"):
        raise ValueError("Publish the practice form and set its verified responder URL before building")
    copy(ROOT / "practice-files" / "upload-practice.txt", PUBLIC / "files" / "upload-practice.txt")
    body = '''<div class="hero"><p class="number">1차·2차 공통 준비</p><h1>파일 제출을<br>먼저 연습해요</h1><p class="lead">내 Google 계정으로 로그인하고, 작은 파일 하나를 첨부해 제출 완료 화면까지 확인합니다.</p></div>
<div class="route">연습 파일 받기 <span>→</span> 개인 계정 로그인 <span>→</span> 파일 첨부 <span>→</span> 제출 완료 확인</div>
<div class="callout"><strong>이 설문은 연습용입니다.</strong><p>성적에 반영되지 않으며 여러 번 연습할 수 있습니다. 연습을 마쳐도 1차·2차 수행평가 제출이 완료되는 것은 아닙니다. 실제 과제는 각 안내 페이지의 제출 설문으로 내세요.</p></div>'''
    body += section("준비물은 두 가지예요", '<ul><li>본인이 사용할 수 있는 <strong>개인 Google 계정</strong></li><li>아래에서 내려받는 작은 연습 파일 1개</li></ul><p>연습 파일 내용은 고칠 필요가 없습니다. <strong>파일 이름은 반드시 본인의 학번_이름_연습.txt로 바꾸세요.</strong></p><p>파일을 업로드하고 제출하면 Google 계정의 이름·이메일·프로필 사진이 자동으로 기록됩니다.</p><div class="practice-actions">' + link("files/upload-practice.txt", "① 연습 파일 받기 (.txt)", "button") + link(PRACTICE_FORM, "② 연습 설문 열기 ↗", "button") + '</div><p class="practice-small">설문은 새 탭에서 열립니다. 이 안내를 옆에 두고 차례대로 따라 하세요.</p>')
    body += section("처음부터 차례대로 따라 하세요", '''<ol class="steps practice-steps">
<li><strong>연습 파일을 내려받아요</strong><p>위의 <b>① 연습 파일 받기</b>를 누릅니다. 보통 컴퓨터의 <b>다운로드</b> 폴더에 <code>upload-practice.txt</code>가 저장됩니다. 저장 위치를 확인한 뒤 파일을 선택하고 <b>이름 바꾸기</b>로 <b>본인의 학번_이름_연습.txt</b>로 바꿉니다. 예: <code>20601_홍길동_연습.txt</code>. <b>.txt 확장자는 지우거나 바꾸지 마세요.</b></p></li>
<li><strong>내 개인 Google 계정으로 로그인해요</strong><p><b>② 연습 설문 열기</b>를 누릅니다. 로그인 화면이 나오면 내 개인 Google 계정으로 로그인합니다. 친구·교사·공용 계정을 사용하지 마세요. 비밀번호는 설문 문항에 적지 않습니다.</p></li>
<li><strong>설문에 표시된 계정을 확인해요</strong><p>설문 위쪽 이메일이 내 계정인지 확인합니다. 다른 사람의 계정이면 <b>계정 전환</b>을 눌러 내 계정으로 바꾸세요. <b>연습 별명</b>은 선택 문항이며, 쓰고 싶으면 <b>연습01</b>처럼 적으면 됩니다.</p></li>
<li><strong>파일을 선택하고 업로드해요</strong><p>파일 첨부 문항에서 <b>파일 추가</b>를 누릅니다. <b>업로드 → 찾아보기(Browse)</b> 또는 파일 선택 버튼을 눌러 다운로드 폴더에서 <b>본인의 학번과 이름으로 바꾼 연습 파일</b>을 선택하세요. 예: <code>20601_홍길동_연습.txt</code>. 파일을 고르면 업로드가 시작됩니다. 별도로 <b>업로드</b> 버튼이 보이면 누르세요. 업로드가 끝나고 설문지에 파일명이 나타날 때까지 기다립니다.</p></li>
<li><strong>첨부한 파일 이름을 확인해요</strong><p>설문 문항 안의 첨부 파일 이름에 <b>본인의 학번과 이름</b>이 표시되는지 확인합니다. 예: <code>20601_홍길동_연습.txt</code>. 잘못 고른 파일이면 옆의 삭제 버튼으로 지운 뒤 다시 첨부하세요. 파일 이름이 보이면 <b>제출 전 확인</b> 문항에서 <b>내 개인 Google 계정으로 로그인했고, 올린 파일명을 확인했습니다.</b>에 체크합니다.</p></li>
<li><strong>제출 버튼을 누르고 완료 화면을 확인해요</strong><p>맨 아래 <b>제출</b>을 누릅니다. <b>파일 제출 연습이 완료되었습니다.</b>라는 안내가 나타나면 성공입니다. 파일 첨부만 하고 창을 닫으면 제출되지 않습니다.</p></li>
</ol>''', "how-to")
    body += section("막히면 여기부터 확인하세요", '''<dl class="practice-help">
<dt>다른 사람의 이메일이 표시돼요.</dt><dd>설문 위쪽의 <b>계정 전환</b>을 누르세요. 여러 계정이 있으면 본인의 개인 계정을 선택한 뒤 표시된 이메일을 다시 확인합니다.</dd>
<dt>계정이 없거나 로그인할 수 없어요.</dt><dd>제출 마감 전에 교사에게 알려 도움을 받으세요. 다른 사람의 계정을 빌려서 제출하지 않습니다.</dd>
<dt>파일이 어디 있는지 모르겠어요.</dt><dd>다운로드 폴더에서 본인의 <code>학번_이름_연습.txt</code>를 찾으세요. 아직 이름을 바꾸지 않았다면 <code>upload-practice.txt</code>를 찾아 이름을 바꿉니다. 파일이 없으면 이 페이지에서 다시 받습니다.</dd>
<dt>업로드가 안 되거나 파일이 너무 크다고 해요.</dt><dd>연습 설문에는 <b>파일 1개, 10MB 이하</b>를 첨부합니다. 여기서 제공한 작은 .txt 파일을 고르고 업로드가 끝날 때까지 기다리세요. 인터넷 연결과 내 계정 로그인 상태도 확인합니다.</dd>
<dt>권한이 없다는 화면이 나와요.</dt><dd>개인 Google 계정으로 로그인했는지 확인합니다. 계속 막히면 오류 문구를 교사에게 보여 주세요.</dd>
<dt>제출 버튼을 눌러도 다음 화면으로 넘어가지 않아요.</dt><dd>빨간색으로 표시된 필수 문항을 확인하세요. 파일 첨부와 확인 체크를 마친 뒤 다시 제출합니다.</dd>
</dl>''')
    body += section("연습을 마쳤다면", '''<ul><li>내 계정으로 로그인했다.</li><li>첨부한 파일 이름에 본인의 학번과 이름이 들어 있는지 확인했다.</li><li>제출 버튼을 누르고 접수 완료 화면을 확인했다.</li></ul><p>공용 컴퓨터에서는 사용을 마친 뒤 <strong>Google 계정에서 로그아웃</strong>하세요. 창을 닫는 것만으로 로그아웃되는 것은 아닙니다.</p><p>이제 실제 과제의 안내에 따라 제출물을 준비하세요. 1차는 .ows와 화면 캡처, 2차는 실행 결과가 저장된 .ipynb를 제출합니다.</p><div class="practice-actions"><a class="button" href="orange.html">1차 안내로 이동</a><a class="button" href="python.html">2차 안내로 이동</a></div>''')
    (PUBLIC / "practice.html").write_text(shell("Google 로그인·파일 제출 연습", "practice", body), encoding="utf-8")


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
    if not PRACTICE_FORM.startswith("https://docs.google.com/forms/"):
        raise ValueError("Set the verified practice form URL before building the public pages")
    PUBLIC.mkdir(exist_ok=True)
    (PUBLIC / ".nojekyll").touch()
    copy(ROOT / "caption-panel.css", PUBLIC / "caption-panel.css")
    copy(ROOT / "caption-panel.js", PUBLIC / "caption-panel.js")
    copy(ROOT / "submission-practice.css", PUBLIC / "submission-practice.css")
    build_orange()
    build_python()
    build_index()
    build_practice()
    version_caption_tracks()


if __name__ == "__main__":
    main()
