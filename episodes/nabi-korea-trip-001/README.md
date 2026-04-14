# nabi-korea-trip-001

15초 길이의 첫 `나비` 쇼츠 프로토타입.

주제:

- 나비가 한국의 대표적인 여행 장면을 짧게 훑으며 시청자에게 다음 여행을 상상하게 만든다.

산출물:

- 최종 영상: `./final/nabi-korea-trip-001-v1.mp4`
- 썸네일: `./final/nabi-korea-trip-001-thumb.png`
- 게시 패킷: `./publish-packet.json`
- 렌더 스크립트: `./render_prototype.py`
- 렌더 무결성 노트: `./render-notes.md`

주의:

- 이 버전은 `reference-only` 방식의 간단한 프로토타입이다.
- 캐릭터 일관성이 깨지기 전까지는 LoRA 학습 없이 진행한다.
- 소스 이슈는 [SHO-8](/SHO/issues/SHO-8)이다.
- 현재 `./assets/backgrounds/images`에는 장면 배경 이미지가 없고 `.gitkeep`만 있다.
- 최종 MP4와 썸네일의 장소 배경은 `render_prototype.py`의 scripted fallback scene generation으로 생성되었다.
- 외부 배경 이미지 또는 영상 플레이트를 사용할 경우 패킷과 `render-notes.md`를 함께 갱신한 뒤 다시 렌더해야 한다.
