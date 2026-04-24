# Pet Toon Style Lock

## Reference Mode

`reference-only`

## Character Identity Rules

- Use canonical files from `characters/<slug>/` whenever they exist.
- Preserve the approved character drawing style almost exactly.
- Do not improve, polish, modernize, photorealize, 3D-render, or convert the character into a different comic/anime style.
- Keep fur color, face marks, eye shape, nose, ear silhouette, outline roughness, proportions, and posture personality stable.

## New Character Rule

If a person or character appears without a canonical definition:

1. assign a stable slug,
2. record its first appearance in `storyboard/character-continuity.json`,
3. save the first generated image path as that character's lock image,
4. reuse that lock description and image for every later cut.

## Negative Prompt Core

duplicate pet, second version of same character, extra animal, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitle, watermark, logo, cluttered background
