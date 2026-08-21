# 치요 우주 표류 내부 모션 테스트 프롬프트

## 사용 조건

- 이 프롬프트는 내부 프리비스 검토용 초안이다.
- 현재 단계에서 외부 렌더를 실행하지 않는다.
- 실행이 필요하면 Head of Content 승인 후 별도 render job 파일을 작성하고 `Video Generation Worker`에 넘긴다.
- `characters/chiyo/rights.md`의 TBD 항목이 남아 있으므로 외부 공개, 반복 시리즈화, character training, LoRA 제작에 사용하지 않는다.

## Reference

Use `characters/chiyo/치요_IMG_1285.jpg` as the only character reference image. Treat it as the canonical turnaround/reference sheet for Chiyo.

## Style Lock

Chiyo is a cute SD/chibi anime-style humanoid character with a large head and small body, bright white or pale light-gray long hair, vivid mint hair highlights, a long ponytail, very large black ear-shaped headpiece with red outer trim and red triangular inner points, large lime-mint eyes, thick black eyelashes and eyeliner, a small gentle smile, X-shaped earrings, dark gray hooded jacket, white top, light gray long lower garment, white sneakers, and black socks. Keep the clean 2D animation turnaround style, simple clear linework, and soft coloring from the reference image.

## Motion Test Prompt

Create a 12-second vertical 9:16 internal motion previs shot chain of Chiyo slowly drifting through quiet space. Keep exactly one Chiyo in frame. Preserve Chiyo's white hair, mint highlights, black and red headpiece, lime-mint eyes, X-shaped earrings, chibi proportions, dark gray jacket, white top, light gray lower garment, white sneakers, and black socks exactly as shown in the reference.

The background is deep navy space with soft nebula layers, small star particles, and distant planet silhouettes. The tone is calm, lonely, and gentle, not horror and not cold realism. Use slow layered parallax and subtle camera drift only. Avoid large body movement. Chiyo floats almost still, with only a tiny eye-direction change toward a small mint light in the distance.

Shot timing:

1. 0.0-2.5s: front-facing Chiyo floats near the upper center of frame. Star particles drift slowly downward. Chiyo's face, headpiece, white hair, mint highlights, and lime-mint eyes must be readable in the first frame.
2. 2.5-5.5s: the camera drifts slightly to suggest a 3/4 side view. A small distant planet silhouette passes in the background through parallax. Chiyo's proportions and headpiece do not change.
3. 5.5-8.5s: Chiyo shifts to the left side of frame while a small mint light appears far on the right. Chiyo's eyes quietly orient toward the light. The expression stays gentle and restrained.
4. 8.5-12.0s: Chiyo returns toward a half-front view and holds almost still while looking at the mint light. The final half-second aligns star-particle movement with the first shot for a soft loop.

No text, no subtitles, no captions, no logo, no watermark, no AI disclosure inside the frame. Keep safe empty space only if later editorial overlays are approved.

## Negative Prompt

photorealistic, realistic adult body proportions, 3D render, plastic doll material, mature seductive pose, long realistic legs, missing black and red headpiece, small headpiece, changed hair color, missing mint hair streaks, changed eye color, missing X earrings, extra ears, animal tail, wings, extra limbs, extra fingers, duplicate Chiyo, extra characters, extra animals, merged face, distorted face, horror mood, gritty realism, messy lineart, blurry face, fast spin, falling tumble, running, jumping, big arm movement, outfit change, text, subtitles, logo, watermark

## Acceptance Notes

- Pass only if Chiyo remains visually consistent with the reference image across all cuts.
- Pass only if there is exactly one Chiyo and no extra characters or animals.
- Pass only if motion remains low-risk: slow parallax, tiny camera drift, and small eye-direction change.
- Fail if the render changes the drawing style, creates a 3D/realistic character, duplicates the character, or loses the headpiece, mint hair streaks, eye color, or chibi proportions.
