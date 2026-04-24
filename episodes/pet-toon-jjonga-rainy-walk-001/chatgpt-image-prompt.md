# ChatGPT Image Prompt — 비 오는 날 산책

이 파일은 사람이 ChatGPT에 직접 붙여넣어 Pet Toon 이미지를 받기 위한 handoff prompt다.
이 이슈의 완료 산출물은 자동 생성된 이미지가 아니라 이 프롬프트 파일이다.

## 사용 방법

1. ChatGPT 새 대화를 연다.
2. 아래 reference images를 먼저 업로드한다.
3. `전체 웹툰 strip 생성 프롬프트`를 붙여넣어 4컷 세로 웹툰 이미지를 요청한다.
4. 이어서 `컷별 개별 이미지 프롬프트`를 하나씩 붙여넣어 cut별 이미지를 따로 요청한다.
5. 받은 파일은 사람이 아래 경로명으로 저장한다.

## Reference Images To Upload

- `characters/jjonga/jjonga.png`
- `characters/jjonga/jjonga_stand.png`
- `characters/jjonga/jjonga_laydown.png`
- `docs/example/찌루_쫑아_웹툰_파일럿.png`

## 저장 파일명

- 전체 웹툰 strip: `images/episode-strip.png`
- cut-01 개별 이미지: `images/cuts/cut-01.png`
- cut-02 개별 이미지: `images/cuts/cut-02.png`
- cut-03 개별 이미지: `images/cuts/cut-03.png`
- cut-04 개별 이미지: `images/cuts/cut-04.png`

## 전체 웹툰 strip 생성 프롬프트

```text
You are creating a Pet Toon webtoon image.

Use the uploaded reference images as the strict visual source for the recurring character.
The most important requirement is character consistency: preserve the exact same drawing style, face structure, fur color, eye style, nose, ear silhouette, outline roughness, pastel fill texture, and personality posture from the uploaded references.

Episode title: 비 오는 날 산책
Protagonist: 쫑아 (`jjonga`)
Episode premise: 비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기.

Create one vertical webtoon strip made of 4 stacked panels.
Each panel should be a clean 2D hand-drawn webtoon panel with the same character design in every panel.
Do not add captions, subtitles, speech bubbles, logos, watermarks, readable signs, or decorative text.

Panel plan:
cut-01: rainy reluctance - 쫑아 hesitates at the doorway on a rainy day, wearing a simple raincoat and looking suspicious about going outside. Emotion: watchful, reluctant, slightly annoyed
cut-02: first step outside - 쫑아 carefully steps onto the wet sidewalk, keeping the same tense posture and sharp little dot eyes. Emotion: cautious curiosity
cut-03: puddle discovery - 쫑아 notices a small puddle and leans forward with a clever, alert expression, still exactly the same brown dog character. Emotion: focused discovery
cut-04: splash payoff - 쫑아 happily splashes in the small puddle with wet paws, proud and playful while preserving the canonical hand-drawn style. Emotion: playful payoff

Character lock:
- Draw exactly one 쫑아 in each panel unless the panel plan explicitly says otherwise.
- Do not create a second version of the same dog.
- Do not change the dog into a realistic animal, a 3D render, a different manga/anime style, or a polished unrelated mascot.
- Keep the character close to the uploaded artist-like reference style.

Output:
- One vertical webtoon strip.
- No text inside the image.
- Clear panel separation.
- Soft everyday pet-comedy tone.

Avoid:
duplicate pet, second version of same character, extra animal, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitle, speech bubble, watermark, logo, cluttered background
```

## 컷별 개별 이미지 프롬프트

아래 프롬프트를 하나씩 붙여넣어 각 컷 이미지를 따로 생성한다. ChatGPT가 이전 이미지를 참조할 수 있으면 직전 결과와 업로드한 reference images를 계속 참조하라고 말한다.

### cut-01 개별 이미지 프롬프트

```text
Create one clean vertical webtoon panel, no text.

Episode premise: 비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기.
Cut 01/04: 쫑아 hesitates at the doorway on a rainy day, wearing a simple raincoat and looking suspicious about going outside.
Emotion: watchful, reluctant, slightly annoyed

Character lock:
- Draw exactly one 쫑아 (`jjonga`).
- Preserve the same canonical brown small dog from the uploaded reference images.
- Preserve the rough black outline, simple 2D hand-drawn pastel style, small black dot eyes, small nose, asymmetric rounded/floppy ears, and alert smart expression.
- Do not redesign the character, do not switch art style, do not make a realistic dog, and do not create a second copy of the dog.

Composition:
- 2:3 vertical webtoon panel, soft everyday background, simple readable staging.
- Keep the panel text-free: no captions, no speech bubbles, no signs, no logos, no watermark.

Avoid:
duplicate pet, second version of same character, extra animal, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitle, speech bubble, watermark, logo, cluttered background
```

### cut-02 개별 이미지 프롬프트

```text
Create one clean vertical webtoon panel, no text.

Episode premise: 비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기.
Cut 02/04: 쫑아 carefully steps onto the wet sidewalk, keeping the same tense posture and sharp little dot eyes.
Emotion: cautious curiosity

Character lock:
- Draw exactly one 쫑아 (`jjonga`).
- Preserve the same canonical brown small dog from the uploaded reference images.
- Preserve the rough black outline, simple 2D hand-drawn pastel style, small black dot eyes, small nose, asymmetric rounded/floppy ears, and alert smart expression.
- Do not redesign the character, do not switch art style, do not make a realistic dog, and do not create a second copy of the dog.

Composition:
- 2:3 vertical webtoon panel, soft everyday background, simple readable staging.
- Keep the panel text-free: no captions, no speech bubbles, no signs, no logos, no watermark.

Avoid:
duplicate pet, second version of same character, extra animal, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitle, speech bubble, watermark, logo, cluttered background
```

### cut-03 개별 이미지 프롬프트

```text
Create one clean vertical webtoon panel, no text.

Episode premise: 비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기.
Cut 03/04: 쫑아 notices a small puddle and leans forward with a clever, alert expression, still exactly the same brown dog character.
Emotion: focused discovery

Character lock:
- Draw exactly one 쫑아 (`jjonga`).
- Preserve the same canonical brown small dog from the uploaded reference images.
- Preserve the rough black outline, simple 2D hand-drawn pastel style, small black dot eyes, small nose, asymmetric rounded/floppy ears, and alert smart expression.
- Do not redesign the character, do not switch art style, do not make a realistic dog, and do not create a second copy of the dog.

Composition:
- 2:3 vertical webtoon panel, soft everyday background, simple readable staging.
- Keep the panel text-free: no captions, no speech bubbles, no signs, no logos, no watermark.

Avoid:
duplicate pet, second version of same character, extra animal, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitle, speech bubble, watermark, logo, cluttered background
```

### cut-04 개별 이미지 프롬프트

```text
Create one clean vertical webtoon panel, no text.

Episode premise: 비 오는 날 산책을 싫어하던 쫑아가 우비를 입고 나가서 작은 물웅덩이를 발견하고 신나게 노는 이야기.
Cut 04/04: 쫑아 happily splashes in the small puddle with wet paws, proud and playful while preserving the canonical hand-drawn style.
Emotion: playful payoff

Character lock:
- Draw exactly one 쫑아 (`jjonga`).
- Preserve the same canonical brown small dog from the uploaded reference images.
- Preserve the rough black outline, simple 2D hand-drawn pastel style, small black dot eyes, small nose, asymmetric rounded/floppy ears, and alert smart expression.
- Do not redesign the character, do not switch art style, do not make a realistic dog, and do not create a second copy of the dog.

Composition:
- 2:3 vertical webtoon panel, soft everyday background, simple readable staging.
- Keep the panel text-free: no captions, no speech bubbles, no signs, no logos, no watermark.

Avoid:
duplicate pet, second version of same character, extra animal, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitle, speech bubble, watermark, logo, cluttered background
```
