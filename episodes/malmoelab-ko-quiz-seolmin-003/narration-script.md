# Narration Script - malmoelab-ko-quiz-seolmin-003

## Core Rules

1. This follows the `daehan-pilot-codex-003` spoken structure exactly.
2. Opening line keeps the same sentence structure as `003` and only swaps the character name to `설민`.
3. Ending line keeps the same sentence structure as `003`.
4. English prompt, reveal copy, CTA, and romanization stay as typography overlays. They are not separate TTS lines by default.
5. Romanization is support text only. Do not read it out loud.
6. Spoken Korean should stay bright, clear, and learner-friendly.
7. Do not turn `scene-1` or `scene-2` into a blank-quiz challenge.
8. Keep `reference-only` production mode. No character training or LoRA escalation is approved here.

## Source Lock

- focus word: `여행`
- romanization helper: `yeohaeng`
- romanization status: render fallback only, not authoritative learning content
- full sentence: `여름에는 가족과 여행을 갑니다.`
- blank sentence: `여름에는 가족과 ___을 갑니다.`
- translation: `In summer I go on a trip with my family.`
- CTA overlay: `malmoelab.com에서 더 알아보아요.`

## Timeline

### [Scene 1] 0.0s - 6.0s - Opening Greeting

```text
KO: "안녕하세요. 여러분과 한글을 함께 공부할 설민입니다!"
```

Visual cue: Seolmin faces camera on the right side of the frame and gives a small bright wave. The chalkboard remains empty for later typography.

### [Scene 2] 6.0s - 12.0s - Lesson Intro

```text
KO: "오늘 배울 문장은 여름에는 가족과 여행을 갑니다, 입니다."
```

Visual cue: Seolmin gestures toward the left chalkboard. Post typography shows the full Korean sentence with small romanization support.

### [Scene 3] 12.0s - 18.0s - Repeat Cue + Sentence

```text
KO: "따라해 볼까요?"
[1.0초]
KO: "여름에는 가족과 여행을 갑니다."
```

Visual cue: Seolmin invites the viewer to repeat, then listens with an encouraging expression. Post typography repeats the full sentence.

### [Scene 4] 18.0s - 24.0s - Blank Quiz

```text
KO: "빈칸에 들어갈 말은 무엇일까요?"
```

Visual cue: Seolmin points toward the blank area on the board. Post typography shows `여름에는 가족과 ___을 갑니다.` with romanization support. Do not speak or reveal `여행` in the voice line.

### [Scene 5] 24.0s - 30.0s - Ending

```text
KO: "말모이랩닷컴에서 더 알아보아요. 안녕!"
```

Visual cue: Seolmin gives a small goodbye wave. Post typography shows the CTA as a lower-third.

## Handoff Notes

- Use `characters/seolmin/voice.json` for voice inheritance.
- `characters/seolmin/bible.md` and `characters/seolmin/voice.json` reference `characters/seolmin/1_Opening_Seolmin.mp4`, but the available folder currently contains `characters/seolmin/1_Opening.mp4`. Treat `characters/seolmin/1_Opening.mp4` as the available opening fallback if an opening clip is needed downstream.
- All Korean sentence text, romanization, CTA, subtitles, logos, and reveal text must be added only in post-picture typography. Do not bake text into generated keyframes or video.
