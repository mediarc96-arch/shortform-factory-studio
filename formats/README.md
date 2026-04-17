# Format Profiles

포맷 프로필은 episode가 어떤 구성 규칙을 따르는지 고정하는 레이어다.

- `legacy-v1`: 기존 `daehan-pilot-codex-001`과 같은 흐름
- `wipe-cta-v2`: 오프닝/엔딩 경계를 `wipe`로 바꾸고, 컨텐츠를 문장 소개 + 따라하기 + 퀴즈 CTA로 단순화한 새 흐름

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
