# 치요 프롬프트 세트

## 기본 생성 프롬프트

치요, 귀여운 SD/치비 비율의 애니메이션풍 인간형 캐릭터, 큰 머리와 작은 몸, 밝은 흰색 또는 연회색 긴 머리와 선명한 민트색 하이라이트, 긴 포니테일, 큰 검정색 귀 모양 헤드피스와 붉은 외곽 라인, 붉은 삼각 포인트, 라임-민트 계열의 큰 눈, 두꺼운 검은 속눈썹과 아이라인, 작은 미소, X자 모양 귀걸이, 어두운 회색 후드 재킷, 흰색 상의, 밝은 회색 긴 하의, 흰색 운동화, 깔끔한 2D 애니메이션 턴어라운드 스타일, 단순하고 선명한 라인, 부드러운 채색

## 네거티브 프롬프트

photorealistic, realistic adult body proportions, 3D render, doll-like plastic material, hyper-detailed skin, mature seductive pose, long realistic legs, missing black and red headpiece, small headpiece, changed hair color, missing mint hair streaks, changed eye color, missing X earrings, extra ears, animal tail, wings, extra limbs, extra fingers, extra characters, horror mood, gritty realism, messy lineart, blurry face, text, subtitles, logo, watermark

## 쇼츠용 장면 프롬프트 기본형

치요가 고요한 우주 공간을 천천히 떠도는 장면, 캐릭터는 `./치요_IMG_1285.jpg`의 큰 검정/붉은 헤드피스와 흰 머리, 민트 헤어 스트릭, 라임-민트 눈, 어두운 회색 재킷을 그대로 유지, 배경은 딥 네이비 우주와 부드러운 성운, 작은 별 입자, 먼 행성 실루엣, 느린 부유감과 조용한 판타지 분위기, 세로형 9:16 쇼츠 프레이밍, 자막이 들어갈 여백 확보, 텍스트와 로고 없음

## 샷별 프롬프트 메모

- 콜드 오픈: 정면 기준 치요가 우주 한가운데 떠 있고, 큰 헤드피스와 민트 헤어 스트릭이 첫 프레임부터 읽힘
- 표류 확장: 3/4 또는 측면에 가까운 구도, 배경 별 입자와 행성 실루엣이 뒤로 흐르며 천천히 이동
- 빛 발견: 치요가 화면 한쪽에 있고 먼 곳의 작은 민트빛 광원을 바라봄, 표정은 과장하지 않고 조용한 집중
- 루프 엔딩: 반정면으로 돌아오며 거의 정지한 자세, 별먼지 흐름을 첫 컷과 비슷하게 맞춰 반복 재생감 확보

## 우주 표류 테스트 프롬프트

`./치요_IMG_1285.jpg`를 유일한 캐릭터 기준 이미지로 사용한다. 치요의 흰 머리, 민트 하이라이트, 검정/붉은 헤드피스, 라임-민트 눈, X자 귀걸이, 어두운 회색 재킷을 동일하게 유지한다. 치요가 딥 네이비 우주 배경 속에서 조용히 떠 있고, 작은 별 입자와 부드러운 성운이 천천히 지나간다. 고요하지만 차갑지 않은 애니메이션 판타지 톤, 깔끔한 2D 라인, 부드러운 채색, 9:16 vertical short framing. No text, no subtitles, no watermark, no logo.

## 운용 규칙

- 첫 에피소드에서는 `./치요_IMG_1285.jpg`를 핵심 참조 이미지로 사용한다.
- 현재 이미지는 정면/측면/후면이 들어 있는 master turnaround/reference-sheet asset으로 취급한다.
- `refs/` 폴더를 만든 뒤 현재 JPG를 복사하거나 명시적으로 등록하고, 이후 cutout, expression, pose reference를 추가하는 것이 다음 정리 작업이다.
- 생성 결과가 헤드피스, 머리색, 눈색, 치비 비율을 잃으면 재생성한다.
- 반복 캐릭터로 확장하기 전까지는 `reference-only`로만 운영한다.
