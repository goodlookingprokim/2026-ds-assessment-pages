# 1차 Orange 영상 자료

- `diversity_addendum.mp4`: 질문·축 선택, 화면 저장, 현재 11열 CSV를 안내하는 짧은 영상입니다.
- `diversity_addendum.vtt`: 동영상의 한국어 설명 자막. 웹페이지 `<video>`의 `<track kind="captions">`로 연결합니다.
- `file-two-branches.png`: 사용자가 제공한 File → Data Table / Scatter Plot 분기 배치 그림입니다.
- `manual-student.mp4`: 개정 전 8열 CSV를 사용한 보관용 원본입니다. 배포하지 않습니다.
- `manual-branch-layout.mp4`: 잘못된 가로 위젯 배치를 그림으로 가린 이전 보관본입니다. 배포하지 않습니다.
- `recapture/`: 현재 11열 CSV를 Orange 안정화 앱에서 직접 열어 File → Data Table → Scatter Plot을 순서대로 연결한 실제 화면 세 단계와 표·산점도 캡처, 완료된 `GoodlookingproKim` 음성의 근거입니다.
- `manual-recaptured.mp4`, `subtitles-recaptured.vtt`: 실제 연결 전·첫 연결·두 연결 완료 화면을 발화 순서에 맞춘 배포용 영상과 음성 원문 자막입니다. `python3 orange-media/recapture/build_video.py`로 다시 생성합니다.
- `01_question_choices.png`: 세 가지 서로 다른 출발 질문과 해당 축·색.
- `02_axes_workflow.png`: 질문 선택부터 해석까지의 단계.
- `03_real_orange_capture.png`: 2026-10-21 촬영한 11번 로봇 Orange 산점도 실제 화면을 명시적으로 예시로 배치.
- `04_capture_checklist.png`: 제출용 연결·결과 화면의 구분.

기존 두 영상은 보관만 합니다. 배포용 기본 조작 영상의 연결 장면은 실제 Orange 앱에서 만든 세 연결 상태를 사용하며 별도 배치 그림을 덧씌우지 않습니다.

재생성: `python3 orange-media/recapture/build_video.py` (ffmpeg 필요). 질문 선택 영상은 `uv run --with pillow python orange-media/build_diversity_media.py`로 만듭니다.
