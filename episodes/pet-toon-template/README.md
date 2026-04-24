# Pet Toon Template

`[Pet Toon]`은 Pet Contents의 영상 제작 버전과 분리된 manual prompt handoff 포맷이다.

에이전트 결과물은 episode folder 안에 다음 파일로 남긴다.

- `chatgpt-image-prompt.md`
- `storyboard/style-lock.md`
- `storyboard/storyboard-plan.json`
- `storyboard/character-continuity.json`
- `pet-toon-manifest.json`

사람은 `chatgpt-image-prompt.md`를 ChatGPT에 붙여넣고 받은 이미지를 아래 경로로 저장한다.

- `images/cuts/cut-XX.png`
- `images/episode-strip.png`

기본 실행:

```sh
python3 scripts/pilot/generate_pet_toon_episode.py \
  --episode-dir episodes/pet-toon-jjonga-rainy-walk-001 \
  --protagonist-slug jjonga \
  --protagonist-name 쫑아 \
  --episode-title "비 오는 날 산책" \
  --episode-text "비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기." \
  --cut-count 4
```

`--generate`는 더 이상 사용하지 않는다. Pet Toon 이슈는 사람이 ChatGPT에 입력할 프롬프트 md가 생성되면 완료다.
