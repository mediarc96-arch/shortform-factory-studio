import { queueEpisodes, type QueueEpisode } from "@/features/console-data";

export type WorkspaceEpisode = {
  slug: string;
  character_slug: string | null;
  status: "ready" | "review" | "blocked";
  final_output_path: string | null;
  thumbnail_path: string | null;
  review_report_path: string | null;
  publish_packet_path: string | null;
};

export type WorkspaceSnapshot = {
  character_count: number;
  episode_count: number;
  format_count: number;
  ready_episode_count: number;
  blocked_episode_count: number;
  episodes: WorkspaceEpisode[];
};

export type WorkspaceViewModel = {
  source: "api" | "sample";
  queue: QueueEpisode[];
  episodeCount: number;
  readyEpisodeCount: number;
  blockedEpisodeCount: number;
};

const DEFAULT_API_BASE_URL = "http://127.0.0.1:8000";

export async function loadWorkspaceViewModel(): Promise<WorkspaceViewModel> {
  const snapshot = await fetchWorkspaceSnapshot();

  if (!snapshot) {
    return {
      source: "sample",
      queue: queueEpisodes,
      episodeCount: 40,
      readyEpisodeCount: 1,
      blockedEpisodeCount: 1
    };
  }

  const queue = snapshot.episodes.slice(0, 8).map((episode) => ({
    slug: episode.slug,
    character: episode.character_slug ?? "unknown",
    status: episode.status,
    nextGate: nextGateForEpisode(episode)
  }));

  return {
    source: "api",
    queue,
    episodeCount: snapshot.episode_count,
    readyEpisodeCount: snapshot.ready_episode_count,
    blockedEpisodeCount: snapshot.blocked_episode_count
  };
}

async function fetchWorkspaceSnapshot(): Promise<WorkspaceSnapshot | null> {
  const baseUrl = process.env.SFS_API_BASE_URL ?? DEFAULT_API_BASE_URL;

  try {
    const response = await fetch(`${baseUrl}/workspace`, {
      cache: "no-store",
      next: { revalidate: 0 }
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as WorkspaceSnapshot;
  } catch {
    return null;
  }
}

function nextGateForEpisode(episode: WorkspaceEpisode): string {
  if (!episode.final_output_path) {
    return "final output";
  }
  if (!episode.thumbnail_path) {
    return "thumbnail";
  }
  if (!episode.review_report_path) {
    return "review report";
  }
  if (!episode.publish_packet_path) {
    return "publish packet";
  }
  return "delivery link";
}
