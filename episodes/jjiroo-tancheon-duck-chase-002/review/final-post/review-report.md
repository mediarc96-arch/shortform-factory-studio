# Video Review: jjiroo-tancheon-duck-chase-002
날짜: 2026-04-28

## 전체 요약

- 총 씬 수: 10
- 이슈 있는 씬: 4
- PASS 씬: 6
- 심각도: 블로커
- 판정: QA 승인 불가. publish handoff 금지.

## 확인한 산출물

- Final review video: `episodes/jjiroo-tancheon-duck-chase-002/renders/final/jjiroo-tancheon-duck-chase-002-final-review.mp4`
- Review bundle: `episodes/jjiroo-tancheon-duck-chase-002/review/final-post`
- Manifest: `episodes/jjiroo-tancheon-duck-chase-002/review/final-post/final-post-manifest.json`
- Source packet: `episodes/jjiroo-tancheon-duck-chase-002/source-packet.json`
- Style lock: `episodes/jjiroo-tancheon-duck-chase-002/storyboard/style-lock.md`
- Camera plan: `episodes/jjiroo-tancheon-duck-chase-002/storyboard/camera-plan.md`
- Voice slots: `episodes/jjiroo-tancheon-duck-chase-002/voice-slots.json`
- Typography slots: `episodes/jjiroo-tancheon-duck-chase-002/typography-slots.json`

## 패킷 정합성

- Export integrity: 1080x1920, 9:16, 30.000s, 30fps, 900 frames, AAC mono audio 확인.
- `voice-slots.json`, `typography-slots.json`, `review/final-post/frame-map.csv`의 텍스트와 타이밍은 서로 일치함.
- POST typography는 지정된 5개 슬롯으로만 보이며, sampled frames 기준 텍스트 문구는 `오리 발견`, `전광석화 돌진`, `엄마도 입수`, `혼자 다시 올라옴`, `왜 거기 있어?`로 슬롯과 일치함.
- `packet.md`에는 reference asset path와 disclosure plan이 있음: `./storyboard/style-lock.md`를 episode-local provisional canon으로 사용, `metadata-only disclosure and attribution`.
- Publish packet은 아직 없음. `review/final-post/post-checklist.md`에도 `Publish packet`이 미완료로 남아 있으므로 이 상태는 publish-ready가 아님.

## 씬별 결과

### scene-01 PASS

- 산책 setup, 찌루/쫑아/어머니의 기본 관계와 하네스 색상 구분이 읽힘.

### scene-02 PASS

- sniffing beat와 두 반려견 identity가 유지됨.

### scene-03 PASS

- 오리 발견 beat와 POST caption `오리 발견`이 slot 의도와 일치함.

### scene-04 PASS

- 접근/긴장 beat가 호기심 기반으로 읽히며 wildlife harm 톤은 없음.

### scene-05 PASS with note

- `전광석화 돌진` caption은 slot과 일치함.
- 오리 회피와 찌루 돌진은 읽히지만, 후속 scene의 duplicate issue 때문에 이 acceleration 구간 이후 continuity를 재검토해야 함.

### scene-06 PASS

- 강 입수와 물 splash beat가 읽힘. 현 프레임만으로는 text-in-generation 문제는 보이지 않음.

### scene-07 BLOCKER

- scene-07 / frame 503 / planned cast는 `Jjiroo 1, mother 1`인데, 화면에는 mint harness를 단 cream Jjiroo-like 개체가 2마리로 보임. 어머니의 입수 beat가 같은 개체 중복처럼 치환되어 `엄마도 입수` 내러티브와 충돌함.
- scene-07 / frame 506 / POST caption `엄마도 입수`가 표시되는 순간에도 화면은 어머니가 아니라 duplicate Jjiroo-like dog 2마리로 읽힘. `[Pet Contents]` 기준 second version of same pet은 하드 블로커.

### scene-08 BLOCKER

- scene-08 / frame 594 / planned cast는 `Jjiroo 1, mother 1`인데 왼쪽에서 또 다른 cream dog head가 들어오고 중앙에도 Jjiroo가 있어 duplicate Jjiroo로 보임. 어머니가 뒤처지는 comic mismatch가 성립하지 않음.

### scene-09 BLOCKER

- scene-09 / frame 686 / `혼자 다시 올라옴` beat인데 물속 개체와 강가 개체가 둘 다 Jjiroo-like로 보임. 자력 climb-out이 아니라 같은 반려견 복제처럼 읽혀 story truth와 충돌함.
- scene-09 / frame 716 / POST caption `혼자 다시 올라옴`이 표시되는 프레임에서도 물속에 다른 Jjiroo-like 개체가 남아 있어 "혼자"라는 claim을 깨뜨림.

### scene-10 BLOCKER

- scene-10 / frame 816 / final payoff는 `Jjiroo 1, mother 1`이어야 하는데, foreground Jjiroo 외에 물속 Jjiroo-like 개체와 강가의 또 다른 cream dog가 함께 보임. 젖은 어머니를 보는 반전 표정이 아니라 중복 개체를 보는 장면으로 읽힘.
- scene-10 / frame 885 / 엔딩 직전까지 duplicate Jjiroo-like 개체가 유지됨. `왜 거기 있어?` caption의 대상이 어머니가 아니라 duplicate dog처럼 보이므로 payoff가 무너짐.

## 권고 사항

- 재렌더 필요 씬: `scene-07`, `scene-08`, `scene-09`, `scene-10`
- POST 편집으로 수정 가능: 없음. 동일 반려견 중복과 어머니 치환 문제는 picture/source frame 단계 문제라 crop, caption, timing 조정으로 해결 불가.
- 재작업 기준:
  - `scene-07`: `Jjiroo 1, mother 1, ducks 3`, 어머니는 같은 진입 지점에서 뒤늦게 입수하고 찌루는 한 박자 앞서 있어야 함.
  - `scene-08`: `Jjiroo 1, mother 1, ducks 2`, 찌루-어머니 거리 차를 보여야 하며 두 번째 찌루 금지.
  - `scene-09`: `Jjiroo 1, mother 1, ducks 0`, 찌루가 스스로 올라오는 단일 동작이어야 함.
  - `scene-10`: `Jjiroo 1, mother 1, ducks 0`, 찌루는 뭍 위 foreground, 어머니는 물속/물가 뒤편 supporting guardian으로 읽혀야 함.
- 재렌더 후 동일한 `review/final-post` 수준의 frame map/contact sheet를 다시 생성해 QA 재요청 필요.
