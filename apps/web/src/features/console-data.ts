import type { ScreenId } from "@/i18n/locales";

export type QueueEpisode = {
  slug: string;
  character: string;
  status: "review" | "blocked" | "ready";
  nextGate: string;
};

export type Gate = {
  index: number;
  title: string;
  detail: string;
  state: "done" | "next" | "risk";
};

export const queueEpisodes: QueueEpisode[] = [
  {
    slug: "jjiroo-pilot-001",
    character: "Jjiroo",
    status: "review",
    nextGate: "rights note"
  },
  {
    slug: "pet-toon-jjonga-rainy-walk-001",
    character: "Jjonga",
    status: "blocked",
    nextGate: "image jobs missing"
  },
  {
    slug: "malmoelab-quiz-episode-041",
    character: "Daehan",
    status: "ready",
    nextGate: "delivery link"
  }
];

export const productionGates: Gate[] = [
  {
    index: 1,
    title: "소스 패킷 인덱싱 완료",
    detail: "source-packet.json, storyboard plan, render candidates",
    state: "done"
  },
  {
    index: 2,
    title: "세로형 최종 후보 발견",
    detail: "renders/final/review-candidate.mp4",
    state: "done"
  },
  {
    index: 3,
    title: "권리 노트 미완료",
    detail: "rights.md 확인 전까지 공개 발행 차단",
    state: "next"
  },
  {
    index: 4,
    title: "클라이언트 패키지 미발급",
    detail: "활성 토큰과 외부 열람 감사 기록 없음",
    state: "risk"
  }
];

export const shots = [
  ["01 오프닝", "00:00-00:06"],
  ["02 훅", "00:06-00:12"],
  ["03 전환", "00:12-00:19"],
  ["04 리액션", "00:19-00:27"],
  ["05 해결", "00:27-00:35"],
  ["06 엔드 카드", "00:35-00:42"]
] as const;

export const reviewFrames = [
  ["0012", "ok"],
  ["0248", "ok"],
  ["0516", "note"],
  ["0781", "ok"],
  ["1182", "fix"],
  ["1430", "ok"],
  ["1688", "ok"],
  ["1904", "ok"]
] as const;

export const referenceFiles = [
  "front-neutral.png",
  "side-profile.png",
  "happy-expression.png",
  "rain-scene.png",
  "thumbnail-safe.png",
  "walking-pose.png",
  "close-up.png",
  "unsafe-archive.png",
  "turnaround.png",
  "style-lock.png"
] as const;

export const navOrder: ScreenId[] = [
  "production",
  "review",
  "request",
  "characters",
  "delivery",
  "ops"
];
