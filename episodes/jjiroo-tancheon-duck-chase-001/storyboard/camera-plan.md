# jjiroo-tancheon-duck-chase-001 Camera Plan

## 카메라 워킹 원칙

- 각 cut은 웹툰식 가독성이 먼저다. 액션이 있더라도 지형과 캐릭터 위치가 헷갈리면 안 된다.
- 오리 발견 전까지는 안정적인 관찰형 구도, 추격부터는 방향성이 분명한 역동 구도, 마지막은 hold에 가까운 코믹 반응 구도로 정리한다.
- river entry point와 climb-out bank는 같은 장소로 읽히도록 반복적으로 노출한다.
- 어머니는 구조 맥락을 주는 보조축이고, 화면의 감정 중심은 끝까지 찌루의 시점과 표정에 둔다.

## 연속성 / seed handoff 규칙

- `scene-01`은 `keyframes/kf-01.jpg`에서 시작한다.
- `scene-02`부터 `scene-10`까지는 직전 scene의 `handoffLastFramePath`를 다음 scene의 opening seed로 사용한다.
- `scene-n` 마지막 프레임과 `scene-(n+1)` 첫 프레임은 같은 pose, 같은 카메라 baseline, 같은 강변 지형, 같은 하네스 상태에서 시작해야 한다.
- `cut-05 -> cut-06`은 같은 추격 방향을 유지한 채 물 진입으로 연결하고, `cut-06 -> cut-07`은 같은 강 진입 지점을 유지한 채 어머니만 뒤늦게 프레임 안으로 들어오게 한다.
- `cut-08 -> cut-09`는 찌루가 오리 추격을 포기하고 climb-out bank로 방향을 바꾸는 한 번의 동선 변화로 처리한다.
- `cut-09 -> cut-10`은 찌루가 이미 뭍에 올라온 상태를 유지한 채 미세한 표정 반응만 추가한다.

## Cut-by-Cut Plan

| cut | scene | beat | camera move | shot goal | intensity | duration intent | transition note | continuity note |
|-----|-------|------|-------------|-----------|-----------|-----------------|-----------------|-----------------|
| cut-01 | scene-01 | sunny riverside walk setup | gentle opening pan | 장소, 보호자, 두 강아지의 산책 관계를 한 화면에서 잠근다 | low | 2.5s | calm daylight atmosphere에서 바로 시작 | 탄천 산책로, 강, 하네스 상태를 첫 기준 프레임으로 고정 |
| cut-02 | scene-02 | dogs sniff and enjoy the walk | subtle handheld drift near dog height | 생활감과 평온함을 쌓아 이후 급변 대비를 만든다 | low | 2.5s | cut-01보다 한 단계 가까이 붙는다 | 같은 진행 방향과 위치 관계를 유지한 채 찌루만 sniffing 자세로 낮춘다 |
| cut-03 | scene-03 | Jjiroo spots the ducks | tiny push-in on Jjiroo reaction | 오리 발견 순간과 시선 방향을 한눈에 꽂는다 | low | 2.5s | sniffing eye-line에서 duck sightline으로 연결 | 오리 resting zone이 이후 chase axis의 종착점으로 계속 읽혀야 한다 |
| cut-04 | scene-04 | stalking tension before breakaway | slow lateral creep | 돌진 직전 긴장과 하네스 tension을 축적한다 | medium-low | 2.8s | ducks를 같은 geography 안에 붙든 채 횡이동 | 찌루의 crouch 방향은 cut-05 sprint 방향과 동일해야 한다 |
| cut-05 | scene-05 | breakaway sprint and duck scatter | aggressive diagonal chase frame | 첫 acceleration peak와 코믹 과장을 만든다 | high | 3.0s | hold를 한 번 끊고 대각선 방향으로 풀어준다 | 어머니는 뒤에 남고, 쫑아는 shore에 남으며, 찌루만 물가로 가속 |
| cut-06 | scene-06 | river jump splash | fast drop into splash impact | 강 진입 지점을 관객이 정확히 기억하게 만든다 | high | 3.0s | same directional momentum을 water entry로 연결 | cut-05의 bank edge와 같은 좌표에서만 입수해야 한다 |
| cut-07 | scene-07 | mother jumps in after Jjiroo | forward chase framing with layered depth | 구조자와 주인공의 거리 차이를 웃음 포인트로 만든다 | medium-high | 3.4s | cut-06 splash 뒤에 어머니 action을 바로 얹는다 | 어머니는 같은 진입 지점에서 들어오고 찌루는 이미 한 박자 앞서 있어야 한다 |
| cut-08 | scene-08 | Jjiroo swims ahead through current | vertical tracking follow | 찌루의 수영 자신감과 어머니의 난처함을 동시에 보인다 | medium-high | 3.4s | scene-07의 강 중앙 action line을 그대로 잇는다 | 오리는 더 멀어지고 찌루-어머니 간 거리 차가 커져야 하지만 공포 톤은 금지 |
| cut-09 | scene-09 | Jjiroo self-rescues and climbs out | easing pullback toward the bank exit | 찌루가 스스로 무사히 나온다는 사실을 명확히 잠근다 | medium | 3.0s | chase axis를 resolution axis로 꺾는다 | climb-out bank는 earlier river geography와 같은 장소로 읽혀야 한다 |
| cut-10 | scene-10 | puzzled look at soaked mother | mostly locked comedy hold | 반전 표정과 허탈한 상황을 punchline으로 남긴다 | low | 3.9s | cut-09 final pose에서 움직임만 최소화 | 찌루는 이미 안전한 뭍 위, 어머니는 물속 뒤편, 카메라 baseline은 크게 바꾸지 않는다 |
