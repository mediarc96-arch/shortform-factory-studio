# SFS 콘솔 스모크 테스트

## Work Type

new_pet_toon_episode

## Output Policy

manual-chatgpt-prompt-handoff

## Source

- parent issue: [SHO-77](/SHO/issues/SHO-77)
- handoff issue: [SHO-86](/SHO/issues/SHO-86)
- episode slug: `sfs-smoke-20260424-001`
- format profile: `pet-toon-image-only-v1`
- protagonist: 찌루 (`jjiroo`)
- production mode: `reference-only`

## Episode Truth

SFS console 새 에피소드 요청이 정상 저장되는지 확인하는 내부 smoke test 상황입니다. 찌루가 따뜻한 실내 작업 공간에서 빈 요청 카드, 작은 카메라, 간식 접시 주변을 호기심 있게 살피고, 마지막에는 준비 완료처럼 얌전히 앉아 사람을 바라보는 4컷 pet-toon 이미지-only 프롬프트 핸드오프입니다.

이미지 안에는 글자, 로고, 화면 UI, 자막, 말풍선, 워터마크를 넣지 않습니다.

## Reference Status

- requested canonical pack missing: `characters/jjiroo/refs/canonical-pack`
- rights note missing: `characters/jjiroo/rights.md`
- board approved internal smoke preparation without those files in [SHO-77 comment](/SHO/issues/SHO-77#comment-c612c7fb-7824-4ee4-bab6-b362a9ff233d)
- no external publish until `characters/jjiroo/rights.md` exists or the board signs a publish-specific rights waiver

## Human Reference Uploads

- `characters/jjiroo/jjiroo.png`
- `characters/jjiroo/jjiroo_sit.png`
- `characters/jjiroo/jjiroo_laydown.png`

## Required Agent Output

- `source-packet.json`
- `packet.md`
- `chatgpt-image-prompt.md`
- `storyboard/style-lock.md`
- `storyboard/storyboard-plan.json`
- `storyboard/character-continuity.json`
- `pet-toon-manifest.json`

## Human Output Paths After ChatGPT Generation

- `images/cuts/cut-01.png`
- `images/cuts/cut-02.png`
- `images/cuts/cut-03.png`
- `images/cuts/cut-04.png`
- `images/episode-strip.png`

## Boundary

This packet does not create the final MP4, QA report, thumbnail, or publish metadata. Those gates open only after the human saves the ChatGPT-returned images under the paths above.
