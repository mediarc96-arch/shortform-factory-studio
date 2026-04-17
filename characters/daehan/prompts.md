# 대한 프롬프트 세트

## 기본 생성 프롬프트

A handsome Korean male teacher named Daehan in his early 30s, long silver-white hair flowing past his shoulders, bright violet eyes, small confident smile, wearing a traditional Korean black durumagi hanbok with a white inner collar, black leather gloves on both hands, a traditional Korean gat (black wide-brimmed hat) with a golden decorative band and red silk tassels hanging on both sides, small golden earring, 3D CG anime style with clean soft shading, light-novel / game CG aesthetic, cheerful and lively expression, standing in front of a green classroom chalkboard, wooden chalk tray with colored chalks visible, warm classroom lighting

## 네거티브 프롬프트

photorealistic, realistic human skin texture, western fantasy robe, modern suit, business attire, short hair, black hair, brown eyes, no hat, no gloves, gat removed, hanbok replaced, extra fingers, deformed hands, dark horror tone, aggressive expression, sexualized pose, messy lineart, noisy background, low quality, blurry, watermark, text artifacts, multiple characters, distorted face

## 쇼츠용 장면 프롬프트 기본형

대한 선생님이 녹색 칠판 오른쪽에 서서 칠판을 향해 분필로 글씨를 쓰는 동작을 취하는 장면, 왼손 또는 오른손에 흰 분필을 들고 있음, 칠판은 비어 있거나 후반 타이포그래피가 들어갈 자리를 확보하도록 단순하게 유지, 캐릭터는 화면 오른쪽 1/3 지점에 배치되어 왼쪽 칠판 영역이 넓게 비워지도록 구성, 밝고 활기찬 표정, 세로형(9:16) 또는 가로형(16:9) 쇼츠 프레이밍, 자막이 들어갈 하단 여백 확보, 부드러운 자연광, 교실 분위기

## 샷별 프롬프트 메모

- **오프닝 훅 (인사)**: 정면 미디엄샷, 카메라를 바라보며 환하게 웃고 한 손을 들어 인사하는 컷. 대사: "안녕하세요. 대한이에요!"
- **칠판 쓰기 컷**: 3/4 측면 샷, 분필을 들고 칠판에 한글을 쓰는 동작, 시청자에게 등을 보이지 않도록 살짝 몸을 돌린 자세
- **설명 컷**: 칠판 오른쪽에 서서 방금 쓴 글씨를 손가락 또는 지시봉으로 가리키며 설명하는 컷, 표정은 자신감 있고 친근함
- **발음 시범 컷**: 정면 클로즈업, 입 모양이 또렷하게 보이는 각도, 학습자가 입 모양을 따라할 수 있도록 구성
- **리액션 컷**: 학습자의 정답을 칭찬하듯 엄지를 들거나 박수 치는 경쾌한 동작
- **CTA 마무리**: 정면 미디엄샷, 손을 가볍게 흔들며 친근하게 인사. 대사: "안녕~!"

## 칠판 구성 규칙

- 칠판은 화면 왼쪽 2/3을 차지, 캐릭터는 오른쪽 1/3에 배치
- **칠판의 한글 콘텐츠는 후반 타이포그래피로 오버레이하는 것이 기본** — AI 생성 단계에서는 칠판을 비워두거나 자리잡이(placeholder) 상태로 유지
- 생성 단계에서는 캐릭터의 "쓰는 동작"(분필·손·팔의 움직임)만 연기시키고, 실제 글씨는 편집 단계에서 스트로크 리빌·페이드인 등으로 합성
- 칠판 영역이 후반 타이포그래피로 덮일 수 있도록 카메라·조명 반사·손 그림자 간섭을 최소화
- 칠판 하단에는 나무 분필 받침과 흰·노란·분홍 분필, 지우개 배치

## 운용 규칙

- 첫 에피소드에서는 `./daehan.jpg`를 핵심 참조 이미지로 사용
- 새로운 참조 이미지가 생기면 `refs/` 디렉토리에 넣고 이 문서에 사용 우선순위를 추가
- 생성 결과에서 갓·장갑·은발·보라 눈동자 중 하나라도 드리프트하면 재생성하고 억지 보정하지 않음
- 칠판 한글 콘텐츠와 하단 자막은 모두 후반 작업에서 타이포그래피로 얹는 것이 기본. AI 생성 단계에서는 "동작"과 "구도"만 잡고 텍스트는 비워둠
- 오프닝·클로징 대사는 고정: "안녕하세요. 대한이에요!" / "안녕~!"
