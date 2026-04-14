# Render Notes: nabi-korea-trip-001

## Scope

- Source issue: [SHO-8](/SHO/issues/SHO-8)
- Integrity pass issue: [SHO-9](/SHO/issues/SHO-9)
- Production mode: `reference-only`
- Status: prototype only, not publish-ready

## Actual Inputs Used By Final Render

- Character source:
  - `/home/kindsr/projects/shortform-factory-studio/characters/nabi/나비_IMG_1286.png`
- Render script:
  - `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/render_prototype.py`
- Frame output folder:
  - `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/renders/frames`

## Background Provenance

- `render_prototype.py` looks for scene backgrounds under:
  - `assets/backgrounds/images`
  - `shared/backgrounds/images`
  - `inbound/references/backgrounds/images`
- At the episode-local path `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/assets/backgrounds/images`, the folder currently contains only `.gitkeep`.
- No episode-local `seoul.*`, `busan.*`, or `jeju.*` image was available during this integrity audit.
- The current prototype should therefore be treated as using scripted fallback backgrounds generated inside `render_prototype.py`, not supplied travel photography or linked external plates.

## Fallback Scene Mapping

- `seoul`
  - dark city blocks plus tower silhouette drawn in code
- `busan`
  - ocean bands plus bridge arcs drawn in code
- `jeju`
  - mountain forms plus dol hareubang-inspired shape drawn in code

## Final Outputs

- Video:
  - `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/final/nabi-korea-trip-001-v1.mp4`
  - size: `426K`
  - sha256: `adeb519689cc37e8b31eb59a5c7ff5c7bb08e0c5d954ba017fd442fbbba22bf8`
- Thumbnail:
  - `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/final/nabi-korea-trip-001-thumb.png`
  - size: `142K`
  - sha256: `5b21e62f28cc1fc4885548d3a7513f54d28d4b243704a2aa209859cf435299fb`

## Disclosure Placement

- Visual disclosure:
  - `AI로 만들어진 영상입니다.`
  - rendered at lower-right in all scenes by `draw_disclosure()`
- Publish packet disclosure:
  - duplicated in `/home/kindsr/projects/shortform-factory-studio/episodes/nabi-korea-trip-001/publish-packet.json`

## QA Notes

- Verify the fallback-background description matches what appears in the final MP4.
- Verify disclosure readability against the encoded file, not just the frame script.
- Do not describe this prototype as location-shot or background-plate-backed unless new assets are added and the episode is re-rendered.
