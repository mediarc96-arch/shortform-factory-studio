# jjiroo-tancheon-duck-chase-001 Post-Production Plan

## 필수 후반작업 항목

- [ ] 이미지 일관성 보정
  - 찌루의 크림아이보리 털색, 세모 귀, 민트색 Y형 하네스와 쫑아의 카라멜브라운 털색, 처진 귀, 복숭아색 하네스를 전 scene에서 동일하게 맞춘다. 물에 젖은 이후에도 개체 식별성이 흔들리면 안 된다.
- [ ] 얼굴 보정
  - scene-10의 `왜 거기 있어요?` 표정은 위협감 없이 순진한 의문으로 읽혀야 한다. 어머니 얼굴은 정보량을 줄이고 상황 리액션만 남겨 주인공 초점을 뺏지 않게 정리한다.
- [ ] 간단한 파츠 애니메이션
  - 귀 perk, 꼬리 flick, 고개 tilt, 젖은 털 shake anticipation, 물방울 drip 정도만 추가한다. 과장된 squash/stretch보다 관찰형 현실감을 우선한다.
- [ ] 배경 분리
  - 강물, 강변 잔디, 산책로, 인물 레이어를 분리해 splash, ripples, speed ramp, caption safe-zone 확보가 가능하게 만든다. duck zone과 climb-out bank는 지형 기준점으로 남긴다.
- [ ] 상황별 효과
  - `scene-05`에는 harness snap + duck flutter accent, `scene-06`에는 splash impact, `scene-07~08`에는 물살과 chase urgency, `scene-10`에는 작은 drip hold만 남긴다. 공포성 water FX는 금지한다.
- [ ] 속도 보정 / speed ramp
  - `scene-05~06` 전환만 짧게 가속하고 나머지는 readability를 우선한다. `scene-08`은 수영 속도보다 거리 차이를 보여 주는 방향으로 리듬을 잡고, `scene-10`은 reaction hold를 충분히 남긴다.
- [ ] 전환 효과
  - whip이나 hard cut은 추격 축이 이어질 때만 제한적으로 사용한다. 기본은 straight cut + action match이며, `scene-09 -> scene-10`은 동일 상태 hold 연장처럼 붙인다.
- [ ] 자막 작업
  - `typography-slots.json`만 사용해 post에서 합성한다. lower-third는 chalkboard 계열이 아니라 soft-webtoon subtitle 톤을 유지하고, `scene-06` splash frame과 `scene-08` swim frame은 caption-free 가독성을 우선한다.
- [ ] 효과음 작업
  - paw steps, leash sway, sniffing, harness snap, duck flutter, splash, 물살, 젖은 발소리, drip tail을 분리해서 배치한다. narration overlap을 가리지 않도록 transient 위주로 얹는다.
- [ ] 배경음악
  - 밝고 가벼운 코미디 리듬의 low-stakes BGM을 유지하되 `scene-03` duck 발견에서 살짝 tension을 올리고 `scene-10`에서는 리듬을 비워 reaction punchline이 먼저 들리게 한다.
- [ ] 컬러 정리
  - sunny daytime 산책 톤을 유지하고, 물 진입 이후에도 전체를 차갑게 밀지 않는다. 강물은 깨끗한 낮 톤, 강변은 밝은 녹색 계열로 유지해 사건이 위험 서사처럼 보이지 않게 한다.
- [ ] QA 리스크 체크
  - 오리가 다치거나 사냥당하는 인상, 익수 공포, 찌루의 공격성, 쫑아 identity drift, 어머니의 과도한 주연화, baked text, scene boundary jump를 우선 검수한다.

## QA 주의사항

- 오리가 너무 위협적으로 보이지 않는지
- 찌루나 쫑아가 난폭하거나 잔인하게 보이지 않는지
- 코믹한 사건으로 읽히는지
- 감정선이 storyboard와 어긋나지 않는지
- `scene-05` 이후 chase axis와 `scene-09` climb-out bank가 같은 장소로 읽히는지
- narration, SFX, typography 타이밍이 같은 beat map을 공유하는지
