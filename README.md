# 2026 데이터과학 수행평가 안내

학생용 정적 웹사이트입니다. `docs/`가 GitHub Pages 게시 대상입니다.

- `docs/index.html`: 1·2차 선택
- `docs/orange.html`, `docs/python.html`: 같은 디자인과 정보 순서의 공지
- `docs/orange-guide/`, `docs/python-guide/`: 학생 실습 안내, 예시, 영상
- `docs/files/orange-csv-30.zip`: 30개 가상 CSV 묶음

두 Google 설문은 학생의 답변과 첨부를 받는 별도 제출 경로입니다. 이 정적 사이트는 학생의 이름, 답변 또는 성적을 저장하지 않습니다. 2차 마감은 원 공지에서 아직 확정되지 않아 날짜를 만들지 않았습니다.

수정 후에는 프로젝트 루트의 원본 자료를 유지한 채 `python3 build.py`로 공개용 사본을 생성하고 `python3 verify_site.py`로 모든 로컬 링크, 30개 CSV, 제출 설문 및 금지 문구를 검사합니다. `build.py`는 이 저장소의 상위 폴더 `outputs/`에 있는 검토된 자료를 입력으로 사용합니다.

교사용 채점 도구, 원본 응답, 학생 식별 정보, 교사 시험 데이터와 점수 기록은 이 공개 저장소에 넣지 않습니다.
