# Audio Loudness Review: malmoelab-ko-repeat-jeonyeok-004-grok-build
날짜: 2026-04-16

## 원인 요약
- 현재 파이프라인은 `edge_tts`로 생성한 세그먼트를 `trim_audio_edges()`로 앞뒤 무음만 제거하고 그대로 믹스한다.
- `ko-KR-InJoonNeural` 같은 동일 음성이라도 문장 길이와 발화 내용에 따라 원본 레벨이 달라진다.
- 004 세그먼트 샘플 측정 결과 `mean_volume`이 다음처럼 흔들렸다.
  - `segment-06.mp3` (`집`): `-21.2 dB`
  - `segment-08.mp3` (`회사`): `-17.6 dB`
  - 차이: 약 `3.6 dB`
- 그래서 반복 파트에서 어떤 단어는 갑자기 작고, 어떤 단어는 상대적으로 크게 들린다.

## 검토한 대안

### 대안 A — 세그먼트별 `mean_volume` 타깃 보정
- 방식: 각 TTS 세그먼트에 `volumedetect`를 걸어 `mean_volume`을 측정한 뒤, 목표값(`-19 dB`)까지 gain을 자동 보정한다.
- 장점: 단어처럼 짧은 클립에도 안정적이다.
- 장점: 적용 로직이 단순하고 재현 가능하다.
- 장점: peak ceiling(`-2 dB`)을 함께 두면 클리핑 위험도 막을 수 있다.
- 샘플 결과:
  - `segment-06.mp3`: `-21.2 dB -> -19.5 dB`
  - `segment-08.mp3`: `-17.6 dB -> -19.4 dB`
- 판단: **채택**

### 대안 B — 세그먼트별 `loudnorm`
- 방식: 각 세그먼트마다 `loudnorm=I=-19:LRA=7:TP=-2` 적용
- 장점: 방송형 loudness 정규화 개념과 맞는다.
- 단점: 짧은 단어 클립에서 결과가 오히려 흔들렸다.
- 샘플 결과:
  - `segment-06.mp3`: `-17.1 dB`
  - `segment-08.mp3`: `-20.0 dB`
- 판단: 짧은 클립에 불안정해서 비채택

### 대안 C — 최종 narration mix에만 `loudnorm`
- 방식: 세그먼트는 그대로 두고, 전부 합친 뒤 최종 narration track에만 정규화 적용
- 장점: 구현이 간단하다.
- 단점: 세그먼트 간 상대 볼륨 차이는 그대로 남는다.
- 판단: 근본 원인 해결이 아니어서 비채택

### 대안 D — job 파일에 단어별 수동 gain 테이블 작성
- 방식: `집`, `회사`, `화장실`마다 개별 gain 수치를 수동 입력
- 장점: 특정 에피소드만 미세 조정 가능하다.
- 단점: 에피소드마다 반복 수작업이 필요하고 확장성이 없다.
- 판단: 운영 비용이 커서 비채택

## 적용 결정
- 004 빌드에는 **대안 A**를 적용한다.
- 구현 위치:
  - `scripts/render_repeat_fill_blank_grok.py`
  - `generate_tts_segments()` 안에서 `trim_audio_edges()` 직후 세그먼트별 음량 정규화 수행
- 설정 위치:
  - `source-packet.json`
  - `narration.tracks.ko.normalizePerSegment = true`
  - `targetMeanDb = -19.0`
  - `peakCeilingDb = -2.0`

## 적용 후 검증
- 재빌드 후 세그먼트 측정값:
  - `segment-06.mp3` (`집`): `-19.5 dB`
  - `segment-08.mp3` (`회사`): `-19.4 dB`
  - `segment-10.mp3` (`화장실`): `-19.0 dB`
- 전체 세그먼트 분포는 대체로 `-19.5 ~ -19.0 dB`로 수렴했다.
- 결론: 003에서 들리던 단어 간 음량 차이는 004에서 실질적으로 정리됐다.
