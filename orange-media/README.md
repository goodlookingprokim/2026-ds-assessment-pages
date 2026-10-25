# 1차 Orange 질문 선택 보충 영상

- `diversity_addendum.mp4`: 28초, 1600×900 H.264. 음성 없이 큰 글씨 화면과 한국어 자막으로 핵심을 안내합니다.
- `diversity_addendum.vtt`: 동영상의 한국어 설명 자막. 웹페이지 `<video>`의 `<track kind="captions">`로 연결합니다.
- `01_question_choices.png`: 세 가지 서로 다른 출발 질문과 해당 축·색.
- `02_axes_workflow.png`: 질문 선택부터 해석까지의 단계.
- `03_real_orange_capture.png`: 2026-10-21 촬영한 11번 로봇 Orange 산점도 실제 화면을 명시적으로 예시로 배치.
- `04_capture_checklist.png`: 제출용 연결·결과 화면의 구분.

기존 6분 시연 영상은 도구 조작의 실제 화면이며, 이 영상은 질문·축 선택과 캡처 기준의 보충 자료입니다. 새 CSV 열이나 새 설정으로 실행한 것처럼 조작 화면을 합성하지 않았습니다.

재생성: `/usr/bin/python3 orange-media/build_diversity_media.py` (macOS Pillow와 ffmpeg 필요).
