# Format Profiles

포맷 프로필은 episode가 어떤 구성 규칙을 따르는지 고정하는 레이어다.

- `legacy-v1`: 기존 `daehan-pilot-codex-001`과 같은 흐름
- `wipe-cta-v2`: 오프닝/엔딩 경계를 `wipe`로 바꾸고, 컨텐츠를 문장 소개 + 따라하기 + 퀴즈 CTA로 단순화한 새 흐름
- `keyframe-review-v1`: 2D 키프레임 승인 후 6초 무음 클립을 만들고 나중에 더빙/타이포를 얹는 실험 흐름
- `education-dub-after-picture-v1`: 교육 콘텐츠용 표준 흐름. 오프닝/엔딩 대사는 재사용하고, 예문 길이를 TTS로 먼저 재서 picture lock 이후 더빙과 칠판 타이포를 합성

음성 운영 원칙:

- `voice id`는 전역 하나가 아니라 캐릭터별로 관리한다.
- 기본 음성 설정은 `characters/<slug>/voice.json`에서 읽는다.
- 회차별 `voice-slots.json`은 필요할 때만 `ttsVoiceEnv`로 override 한다.

운영 원칙:

1. 기존 episode는 원래 결과를 유지한 채 자신이 사용한 프로필만 명시한다.
2. 새 episode는 profile을 참조해서 시드한다.
3. 렌더러 공용화가 되더라도 episode의 `formatProfile`은 바꾸지 않는다.

권장 필드:

- `formatProfile`
- `formatProfilePath`
- `transitionPolicy`
- `ttsProvider`
- `ctaPolicy`
