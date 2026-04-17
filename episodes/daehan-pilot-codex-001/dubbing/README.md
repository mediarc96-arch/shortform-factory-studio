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
3. 같은 명령으로 다시 렌더한다. 별도 JSON 수정은 필요 없다.

렌더러는 아래 우선순위로 오디오를 선택한다.

- `audio-overrides/<voiceSlotId>.wav|mp3|m4a`
- 이미 `voice-slots.json`에 선택된 `human-dub` / `actor-dub` / `voice-pack`
- 기본 `guide-audio/*`

```bash
.venv-video-tools/bin/python scripts/pilot/render_daehan_pilot_final.py --episode-dir episodes/daehan-pilot-codex-001 --env-file .env
```
