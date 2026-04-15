# Shortform Factory Studio

Working directory for `Shortform Factory` production assets.

Use this workspace for:

- recurring character bibles and reference images
- episode packets and shot plans
- generated frames, clips, audio, and final renders
- shared style guides, overlays, and reusable production assets

Do not store large production assets inside Paperclip runtime directories.

## Structure

```text
characters/   캐릭터 이미지 및 아이덴티티
  _template/
episodes/     완료된 작업 영상 
  _template/
docs/         문서
inbound/
  references/
shared/
  backgrounds/  영상제작시 배경으로 사용할 리소스
    images/
    videos/
  styles/
  overlays/
  music/
  sfx/
```

## Canonical Docs

- [docs/REFERENCE_SHORTFORM_WORKFLOW.md](./docs/REFERENCE_SHORTFORM_WORKFLOW.md)
- [docs/PAPERCLIP_ISSUE_OPERATIONS.md](./docs/PAPERCLIP_ISSUE_OPERATIONS.md)
- [docs/CHARACTER_BIBLE_TEMPLATE.md](./docs/CHARACTER_BIBLE_TEMPLATE.md)
- [docs/EPISODE_PACKET_TEMPLATE.md](./docs/EPISODE_PACKET_TEMPLATE.md)
- [docs/MALMOELAB_HANGUL_QUIZ_OPERATING_MODEL.md](./docs/MALMOELAB_HANGUL_QUIZ_OPERATING_MODEL.md)
- [docs/YOUTUBE_CHANNEL_SETUP.md](./docs/YOUTUBE_CHANNEL_SETUP.md)

## Quiz Pipeline

- source fetch: `scripts/fetch_malmoelab_source.py`
- AI panel assets: `scripts/generate_gemini_quiz_assets.py`
- render: `scripts/render_malmoelab_quiz.py`
- used sentence ledger: `data/used_sentences.jsonl`
- first sample episode: `episodes/malmoelab-ko-quiz-001/`

### Gemini image assets

`malmoelab` classroom quiz shorts can optionally generate per-phase panel artwork with Gemini image generation before the final render pass.

기본 운영 모드는 **template-only** 입니다.

- `teacherImage` + 칠판 텍스트 오버레이 + 음악 + CTA만으로 렌더
- 별도 API key 없음
- `Video Editor`는 이 모드를 기본값으로 사용

즉, `GEMINI_IMAGE_API_KEY`를 넣지 않아도 퀴즈 쇼츠 제작은 계속 가능합니다.

Recommended env on `Video Editor`:

- `GEMINI_IMAGE_API_KEY`

Fallback env names that also work:

- `GEMINI_API_KEY`
- `GOOGLE_API_KEY`

Typical sequence:

```bash
python scripts/generate_gemini_quiz_assets.py \
  --source-packet episodes/malmoelab-ko-quiz-001/source-packet.json

python scripts/render_malmoelab_quiz.py \
  --source-packet episodes/malmoelab-ko-quiz-001/source-packet.json
```

The asset-generation step writes:

- `episodes/<slug>/renders/generated-assets/title-panel.png`
- `episodes/<slug>/renders/generated-assets/question-panel.png`
- `episodes/<slug>/renders/generated-assets/answer-panel.png`
- `episodes/<slug>/renders/generated-assets/asset-manifest.json`

If those files exist, the renderer uses them automatically. Otherwise it falls back to `teacherImage`.
