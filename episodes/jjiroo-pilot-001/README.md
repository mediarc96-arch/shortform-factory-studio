# Jjiroo Duck Episode — Video AI Prompt Package

This package is designed for image-to-video or text-to-video tools such as Grok, Sora-style systems, Runway, Pika, and similar generators.

## Recommended workflow
1. Start with `docs/scene-plan.md` to understand the dramatic flow.
2. Load `docs/asset-manifest.json` to keep character and style consistency.
3. Use `docs/shot-prompts.json` shot by shot instead of prompting the entire story at once.
4. Use `docs/source-packet.json` as the machine-readable project manifest.
5. Attach the reference images in `references/` and the generated stills in `generated_scenes/` when the video tool supports image conditioning.

## Important prompting rules
- Use one shot at a time.
- Do not use "comic strip", "panel", "grid", or "layout".
- Repeatedly state:
  - single scene illustration
  - one moment only
  - no panels, no borders, no layout, no grid
  - preserve the exact hand-drawn pastel 2D style
- Keep Jjiroo cream-colored with droopy ears.
- Keep Jjonga brown with a more alert, tense expression.

## Folder layout
- `docs/scene-plan.md`: human-readable directing plan
- `docs/shot-prompts.json`: per-shot prompts for video generation
- `docs/asset-manifest.json`: character and style lock file
- `docs/source-packet.json`: project manifest with asset references
- `references/`: canonical reference art and character sheets
- `generated_scenes/`: still images generated for each story moment

## Notes
- Cut 6 and Cut 7 were generated in separate steps, but one tool output reused the same filename. In this package, the available saved image is labeled honestly based on the surviving file state.
