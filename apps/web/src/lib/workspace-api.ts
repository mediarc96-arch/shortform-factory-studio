import { queueEpisodes, type QueueEpisode } from "@/features/console-data";
import { getSfsApiBaseUrl } from "@/lib/sfs-api";

export type WorkspaceEpisode = {
  slug: string;
  character_slug: string | null;
  status: "ready" | "review" | "blocked";
  final_output_path: string | null;
  thumbnail_path: string | null;
  review_report_path: string | null;
  publish_packet_path: string | null;
};

export type WorkspaceCharacter = {
  slug: string;
  display_name: string;
  root_path: string;
  has_bible: boolean;
  has_prompts: boolean;
  has_rights: boolean;
  has_voice: boolean;
  rights_status: "present" | "missing";
};

export type WorkspaceFormat = {
  slug: string;
  profile_path: string;
};

export type WorkspaceSnapshot = {
  character_count: number;
  episode_count: number;
  format_count: number;
  ready_episode_count: number;
  blocked_episode_count: number;
  characters?: WorkspaceCharacter[];
  episodes: WorkspaceEpisode[];
  formats?: WorkspaceFormat[];
};

export type CharacterRegistryItem = {
  slug: string;
  displayName: string;
  rightsStatus: "present" | "missing";
  hasBible: boolean;
  hasPrompts: boolean;
  hasVoice: boolean;
};

export type FormatRegistryItem = {
  slug: string;
  profilePath: string;
};

export type WorkspaceViewModel = {
  source: "api" | "sample";
  queue: QueueEpisode[];
  characters: CharacterRegistryItem[];
  formats: FormatRegistryItem[];
  characterCount: number;
  episodeCount: number;
  formatCount: number;
  readyEpisodeCount: number;
  blockedEpisodeCount: number;
};

export async function loadWorkspaceViewModel(): Promise<WorkspaceViewModel> {
  const snapshot = await fetchWorkspaceSnapshot();

  if (!snapshot) {
    return {
      source: "sample",
      queue: queueEpisodes,
      characters: [
        {
          slug: "jjiroo",
          displayName: "Jjiroo",
          rightsStatus: "missing",
          hasBible: true,
          hasPrompts: true,
          hasVoice: false
        }
      ],
      formats: [{ slug: "pet-toon-image-only-v1", profilePath: "formats/pet-toon-image-only-v1/profile.json" }],
      characterCount: 1,
      episodeCount: queueEpisodes.length,
      formatCount: 1,
      readyEpisodeCount: queueEpisodes.filter((episode) => episode.status === "ready").length,
      blockedEpisodeCount: queueEpisodes.filter((episode) => episode.status === "blocked").length
    };
  }

  const queue = snapshot.episodes.slice(0, 8).map((episode) => ({
    slug: episode.slug,
    character: episode.character_slug ?? "unknown",
    status: episode.status,
    nextGate: nextGateForEpisode(episode)
  }));
  const characters = snapshot.characters ?? [];
  const formats = snapshot.formats ?? [];

  return {
    source: "api",
    queue,
    characters: characters.map((character) => ({
      slug: character.slug,
      displayName: character.display_name,
      rightsStatus: character.rights_status,
      hasBible: character.has_bible,
      hasPrompts: character.has_prompts,
      hasVoice: character.has_voice
    })),
    formats: formats.map((format) => ({
      slug: format.slug,
      profilePath: format.profile_path
    })),
    characterCount: snapshot.character_count,
    episodeCount: snapshot.episode_count,
    formatCount: snapshot.format_count,
    readyEpisodeCount: snapshot.ready_episode_count,
    blockedEpisodeCount: snapshot.blocked_episode_count
  };
}

async function fetchWorkspaceSnapshot(): Promise<WorkspaceSnapshot | null> {
  const baseUrl = getSfsApiBaseUrl();

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
