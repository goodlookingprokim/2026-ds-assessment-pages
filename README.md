# 2026 데이터과학 수행평가 안내

학생용 정적 웹사이트입니다. `docs/`가 GitHub Pages 게시 대상입니다.

- `docs/index.html`: 1·2차 선택
- `docs/orange.html`, `docs/python.html`: 같은 디자인과 정보 순서의 공지
- `docs/orange-guide/`, `docs/python-guide/`: 학생 실습 안내, 예시, 영상
- `docs/files/orange-csv-30.zip`: 30개 가상 CSV 묶음
- `orange-data/`: 기존 8열을 보존하고 3열을 추가한 11열 CSV v2의 생성기와 원본
- `orange-media/`: 질문 선택·캡처 설명 그림과 한국어 음성·자막이 있는 짧은 보충 영상

두 Google 설문은 학생의 답변과 첨부를 받는 별도 제출 경로입니다. 이 정적 사이트는 학생의 이름, 답변 또는 성적을 저장하지 않습니다. 2차 마감은 원 공지에서 아직 확정되지 않아 날짜를 만들지 않았습니다.

수정 후에는 `python3 orange-data/build.py`로 합성 CSV를 검증하고, `python3 build.py`로 공개용 사본을 생성한 뒤 `python3 verify_site.py`로 네비게이션, 링크, 질문 14개, 30개 CSV의 행·열, 코드 예시, 영상, 제출 설문 및 금지 문구를 검사합니다. `build.py`는 상위 폴더 `outputs/`의 기존 자료와 이 저장소의 `orange-data/`, `orange-media/`를 입력으로 사용합니다. 기존 8열 CSV와 촬영 자료는 상위 `outputs/`에 그대로 남습니다. 기존 긴 Orange 영상과 화면 사진은 8열 자료로 만든 조작 예시로 표시하고, 새 보충 자료에서 질문·축 선택과 캡처 방법을 안내합니다.

보충 영상을 다시 만들 때는 Pillow가 설치된 macOS Python에서 `orange-media/build_diversity_media.py`를 실행합니다. 영상 음성은 `orange-media/narration/`의 한국어 시스템 음성 원본을 사용하며, 교사 본인 음성으로 표시하지 않습니다.

교사용 채점 도구, 원본 응답, 학생 식별 정보와 점수 기록은 이 공개 저장소에 넣지 않습니다. 공개 CSV는 가상 연습 자료입니다.
