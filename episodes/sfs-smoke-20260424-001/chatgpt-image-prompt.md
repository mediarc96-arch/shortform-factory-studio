# ChatGPT Image Prompt — SFS 콘솔 스모크 테스트

이 파일은 사람이 ChatGPT에 직접 붙여넣어 Pet Toon 이미지를 받기 위한 handoff prompt다.
이 이슈의 완료 산출물은 자동 생성된 이미지가 아니라 이 프롬프트 파일이다.

## 사용 방법

1. ChatGPT 새 대화를 연다.
2. 아래 reference images 세 장을 먼저 업로드한다.
3. `전체 웹툰 strip 생성 프롬프트`를 붙여넣어 4컷 세로 웹툰 이미지를 요청한다.
4. 이어서 `컷별 개별 이미지 프롬프트`를 하나씩 붙여넣어 cut별 이미지를 따로 요청한다.
5. 받은 파일은 사람이 아래 경로명으로 저장한다.

## Reference Images To Upload

- `characters/jjiroo/jjiroo.png`
- `characters/jjiroo/jjiroo_sit.png`
- `characters/jjiroo/jjiroo_laydown.png`

## 저장 파일명

- 전체 웹툰 strip: `images/episode-strip.png`
- cut-01 개별 이미지: `images/cuts/cut-01.png`
- cut-02 개별 이미지: `images/cuts/cut-02.png`
- cut-03 개별 이미지: `images/cuts/cut-03.png`
- cut-04 개별 이미지: `images/cuts/cut-04.png`

## 전체 웹툰 strip 생성 프롬프트

```text
You are creating a Pet Toon webtoon image for an internal prompt handoff smoke test.

Use the uploaded reference images as the strict visual source for the recurring character Jjiroo.
The most important requirement is character consistency: preserve the exact same simple 2D hand-drawn pastel style, cream-colored fur, small black dot eyes, short muzzle, drooping ears, rounded small body, rough black outline, low-saturation fill texture, and curious nose-first posture from the uploaded references.

Episode title: SFS 콘솔 스모크 테스트
Protagonist: 찌루 (`jjiroo`)
Episode premise: SFS console 새 에피소드 요청이 정상 저장되는지 확인하는 내부 smoke test 상황. 찌루가 따뜻한 실내 작업 공간에서 빈 요청 카드, 작은 카메라, 간식 접시 주변을 호기심 있게 살피고, 마지막에는 준비 완료처럼 얌전히 앉아 사람을 바라보는 4컷 pet-toon 이미지-only 프롬프트 핸드오프.

Create one vertical webtoon strip made of 4 stacked panels.
Each panel should be a clean 2D hand-drawn webtoon panel with the same Jjiroo design in every panel.
Do not add captions, subtitles, speech bubbles, logos, watermarks, readable signs, UI screens, written labels, or decorative text.

Panel plan:
cut-01: New request scent. Jjiroo discovers a blank request card and a small camera prop on the floor near a warm indoor desk area, leading with his nose. Emotion: curious, alert, gentle pet-comedy setup.
cut-02: Sniff test around props. Jjiroo sniffs between the blank card, camera, and treat plate. The props are simple and completely text-free. Emotion: focused, investigative, food-motivated curiosity.
cut-03: Treat lock moment. Jjiroo pauses in front of the treat plate with intense little dot eyes. The blank request card remains beside him. Emotion: expectant, intensely focused, cute restraint.
cut-04: Prompt ready pose. Jjiroo sits calmly beside the treat and looks up toward the human viewpoint, as if the prompt handoff is ready. No text appears anywhere. Emotion: satisfied, ready, innocent payoff.

Cast cardinality:
- Draw exactly one Jjiroo in each panel.
- Do not create a second version of the same dog.
- Do not add extra animals or background pets.
- Do not show a visible person unless only implied by Jjiroo's eyeline.

Output:
- One vertical webtoon strip.
- Clear panel separation.
- No text inside the image.
- Soft everyday pet-comedy tone.

Avoid:
duplicate pet, second version of same character, extra animal, extra animals, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitles, subtitle, speech bubble, watermark, logo, cluttered background, readable signs
```

## 컷별 개별 이미지 프롬프트

아래 프롬프트를 하나씩 붙여넣어 각 컷 이미지를 따로 생성한다. ChatGPT가 이전 이미지를 참조할 수 있으면 직전 결과와 업로드한 reference images를 계속 참조하라고 말한다.

### cut-01 개별 이미지 프롬프트

```text
Create one clean vertical 2:3 webtoon panel, no text.

Use the uploaded reference images as the strict source for Jjiroo. Preserve the simple 2D hand-drawn pastel style, cream-colored fur, rough black outline, small black dot eyes, short muzzle, drooping ears, rounded small body, and curious nose-first posture.

Cut 01/04: Jjiroo discovers a blank request card and a small camera prop on the floor near a warm indoor desk area, leading with his nose.
Emotion: curious, alert, gentle pet-comedy setup.
Setting continuity: warm indoor desk-side workspace, no readable UI, no text on props.
Shot goal: show the arrival of a new request using props and Jjiroo's sniffing behavior, without any letters or labels.

Cast cardinality:
- exactly one Jjiroo (`jjiroo`)
- zero duplicate dogs
- zero extra animals
- no visible person unless only implied by Jjiroo's eyeline

Avoid:
duplicate pet, second version of same character, extra animal, extra animals, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitles, subtitle, speech bubble, watermark, logo, cluttered background, readable signs
```

### cut-02 개별 이미지 프롬프트

```text
Create one clean vertical 2:3 webtoon panel, no text.

Use the uploaded reference images as the strict source for Jjiroo. Preserve the simple 2D hand-drawn pastel style, cream-colored fur, rough black outline, small black dot eyes, short muzzle, drooping ears, rounded small body, and curious nose-first posture.

Cut 02/04: Jjiroo sniffs between the blank request card, small camera prop, and treat plate. The props are simple and completely text-free.
Emotion: focused, investigative, food-motivated curiosity.
Setting continuity: same indoor workspace, props remain in the same relative positions.
Shot goal: make the smoke test feel like Jjiroo is checking the request, without showing software UI.

Cast cardinality:
- exactly one Jjiroo (`jjiroo`)
- zero duplicate dogs
- zero extra animals
- no visible person unless only implied by Jjiroo's eyeline

Avoid:
duplicate pet, second version of same character, extra animal, extra animals, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitles, subtitle, speech bubble, watermark, logo, cluttered background, readable signs
```

### cut-03 개별 이미지 프롬프트

```text
Create one clean vertical 2:3 webtoon panel, no text.

Use the uploaded reference images as the strict source for Jjiroo. Preserve the simple 2D hand-drawn pastel style, cream-colored fur, rough black outline, small black dot eyes, short muzzle, drooping ears, rounded small body, and curious nose-first posture.

Cut 03/04: Jjiroo pauses in front of the treat plate with intense little dot eyes. The blank request card remains beside him.
Emotion: expectant, intensely focused, cute restraint.
Setting continuity: same workspace, treat plate foreground, blank card side prop.
Shot goal: use Jjiroo's food focus as the middle retention beat.

Cast cardinality:
- exactly one Jjiroo (`jjiroo`)
- zero duplicate dogs
- zero extra animals
- no visible person unless only implied by Jjiroo's eyeline

Avoid:
duplicate pet, second version of same character, extra animal, extra animals, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitles, subtitle, speech bubble, watermark, logo, cluttered background, readable signs
```

### cut-04 개별 이미지 프롬프트

```text
Create one clean vertical 2:3 webtoon panel, no text.

Use the uploaded reference images as the strict source for Jjiroo. Preserve the simple 2D hand-drawn pastel style, cream-colored fur, rough black outline, small black dot eyes, short muzzle, drooping ears, rounded small body, and curious nose-first posture.

Cut 04/04: Jjiroo sits calmly beside the treat and looks up toward the human viewpoint, as if the prompt handoff is ready. No text appears anywhere.
Emotion: satisfied, ready, innocent payoff.
Setting continuity: same indoor workspace, clean final arrangement, no UI screens or written labels.
Shot goal: close the internal smoke test by showing a ready pose through action, not text.

Cast cardinality:
- exactly one Jjiroo (`jjiroo`)
- zero duplicate dogs
- zero extra animals
- no visible person unless only implied by Jjiroo's eyeline

Avoid:
duplicate pet, second version of same character, extra animal, extra animals, extra limbs, wings, merged face, wrong fur color, wrong ear shape, changed eye style, photorealism, realistic fur, glossy 3D render, unrelated manga style, unrelated anime style, text, subtitles, subtitle, speech bubble, watermark, logo, cluttered background, readable signs
```
