# Pet Toon Template

`[Pet Toon]`은 Pet Contents의 영상 제작 버전과 분리된 image-only 포맷이다.

결과물은 episode folder 안에 다음 파일로만 남긴다.

- `images/cuts/cut-XX.png`
- `images/episode-strip.png`
- `pet-toon-manifest.json`

기본 실행:

```sh
python3 scripts/pilot/generate_pet_toon_episode.py \
  --episode-dir episodes/pet-toon-jjonga-rainy-walk-001 \
  --protagonist-slug jjonga \
  --protagonist-name 쫑아 \
  --episode-title "비 오는 날 산책" \
  --episode-text "비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기." \
  --cut-count 4 \
  --generate
```

Paperclip agent 런타임에서는 `PAPERCLIP_API_URL`, `PAPERCLIP_API_KEY`, `PAPERCLIP_COMPANY_ID`, `PAPERCLIP_PROJECT_WORKSPACE_ID`로 중앙 이미지 생성 API를 호출한다. 이 경우 OpenAI API 키는 Paperclip 서버/회사 secret에만 있으면 되고 agent가 직접 알 필요가 없다.

중앙 API 환경과 직접 fallback용 `OPENAI_API_KEY`가 모두 없으면 이미지 호출은 하지 않고 source packet, style lock, storyboard plan, OpenAI image jobs를 준비한 뒤 blocker manifest를 남긴다.
