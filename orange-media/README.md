# 1차 Orange 영상 자료

- `diversity_addendum.mp4`: 질문·축 선택, 화면 저장, 현재 11열 CSV를 안내하는 짧은 영상입니다.
- `diversity_addendum.vtt`: 동영상의 한국어 설명 자막. 웹페이지 `<video>`의 `<track kind="captions">`로 연결합니다.
- `file-two-branches.png`: 사용자가 제공한 File → Data Table / Scatter Plot 분기 배치 그림입니다.
- `manual-student.mp4`: 개정 전 8열 CSV를 사용한 보관용 원본입니다. 배포하지 않습니다.
- `manual-branch-layout.mp4`: 잘못된 가로 위젯 배치를 그림으로 가린 이전 보관본입니다. 배포하지 않습니다.
- `recapture/`: Orange 안정화 앱의 새 작업 화면에서 File을 왼쪽, Data Table을 위쪽, Scatter Plot을 아래쪽에 놓고 현재 11열 CSV를 선택한 실제 화면을 담았습니다. 두 갈래 연결과 표·산점도 캡처도 포함합니다.
- `recapture/voice_01.wav`: 기존 `GoodlookingproKim` 완료 음성에서 위젯 배치·CSV 불러오기·180개 사례 확인만 남긴 25.6초 구간입니다. 뒤따르던 옛 8열 설명은 제외했습니다. 새 음성 생성은 Voicebox의 `default metallib` 로딩 오류로 실패했습니다.
- `manual-recaptured.mp4`, `subtitles-recaptured.vtt`: 새 화면·위젯 배치·CSV 불러오기·두 갈래 연결·표·산점도를 발화 순서에 맞춘 배포용 영상과 음성 원문 자막입니다. `python3 orange-media/recapture/build_video.py`로 다시 생성합니다.
- `01_question_choices.png`: 세 가지 서로 다른 출발 질문과 해당 축·색.
- `02_axes_workflow.png`: 질문 선택부터 해석까지의 단계.
- `03_real_orange_capture.png`: 2026-10-21 촬영한 11번 로봇 Orange 산점도 실제 화면을 명시적으로 예시로 배치.
- `04_capture_checklist.png`: 제출용 연결·결과 화면의 구분.

기존 두 영상은 보관만 합니다. 배포용 기본 조작 영상은 실제 Orange 앱의 단계별 화면 캡처를 사용하며 별도 배치 그림을 덧씌우지 않습니다.

재생성: `python3 orange-media/recapture/build_video.py` (ffmpeg 필요). 질문 선택 영상은 `uv run --with pillow python orange-media/build_diversity_media.py`로 만듭니다.
