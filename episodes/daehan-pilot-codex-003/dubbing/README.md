# Dubbing Package

## 구성
- `audio-overrides/`: 사람이 녹음한 wav/mp3를 넣는 위치
- `guide-audio/`: 현재 guide dub 기준선
- `reference-video/`: 씬별 reference clip
- `dubbing-cues.csv`: 타이밍 표
- `recording-script.md`: 읽기용 스크립트

## 사용
1. `recording-script.md`와 `reference-video/*.mp4`를 보고 녹음한다.
2. 대응 파일명을 유지한 채 `audio-overrides/`에 wav/mp3를 넣는다.
3. 같은 명령으로 다시 렌더한다.

```bash
.venv-video-tools/bin/python scripts/pilot/render_daehan_pilot_keyframe_review_v1.py --episode-dir episodes/daehan-pilot-codex-003 --env-file .env
```
