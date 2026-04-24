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

## SFS Console

`sfs.devscent.com` serves the Next.js/FastAPI console in this repo.

```bash
docker compose up -d --build
```

The API scans this workspace, stores request/delivery metadata in the shared
Postgres database `shortform_factory`, and only writes files for explicit
character creation actions. The default workspace mount is read-only, with
`characters/` overlaid as the writable template scope.

Implemented console actions:

- production request preview and persisted draft creation
- audit log writes for production request, character, and delivery actions
- character template creation under `characters/<slug>`
- delivery token issue/revoke with token hashes stored at rest
- optional Paperclip issue handoff when `SFS_PAPERCLIP_COMPANY_ID` and a valid
  `SFS_PAPERCLIP_API_TOKEN` are configured

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

## Docker Ownership Safety

이 repo에서 `git add .` 할 때 아래 에러가 나면 거의 항상 Docker가 bind-mounted repo에 `root` 소유 파일이나 `.git/objects`를 만든 경우입니다.

```text
error: insufficient permission for adding an object to repository database .git/objects
```

원칙:

- repo를 건드리는 `docker run`은 항상 현재 사용자 UID/GID로 실행
- 이미 떠 있는 컨테이너에서 repo에 쓰는 `docker exec`도 현재 사용자 UID/GID로 실행
- root 컨테이너 안에서 `git add`, `git commit`, `git push` 하지 않기

Helper scripts:

```bash
scripts/docker-run-as-user.sh <image> [command...]
scripts/docker-exec-as-user.sh <container> <command...>
scripts/fix-repo-permissions.sh
```

Examples:

```bash
scripts/docker-run-as-user.sh python:3.12 bash -lc 'python --version'
scripts/docker-exec-as-user.sh my-container bash
scripts/fix-repo-permissions.sh
```

직접 `docker` 명령을 써야 하면 최소한 아래 옵션은 유지하세요.

```bash
docker run --user "$(id -u):$(id -g)" ...
docker exec -u "$(id -u):$(id -g)" ...
```
