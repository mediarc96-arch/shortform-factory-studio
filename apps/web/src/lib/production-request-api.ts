import { getSfsApiBaseUrl } from "@/lib/sfs-api";
import type { WorkspaceViewModel } from "@/lib/workspace-api";

export type ProductionRequestType = "new_episode" | "revise_episode" | "publish_only" | "metadata_update";

export type ProductionRequestDraft = {
  requestType: ProductionRequestType;
  episodeSlug: string;
  characterSlug: string;
  formatProfileSlug: string;
  outputTarget: string;
  referencePath: string;
  completionCriteria: string;
  creativeBrief: string;
};

type ProductionRequestPreviewResponse = {
  request_type: string;
  episode_slug: string;
  markdown: string;
};

export type ProductionRequestPreview = {
  source: "api" | "sample";
  draft: ProductionRequestDraft;
  markdown: string;
};

export async function loadProductionRequestPreview(
  workspace: WorkspaceViewModel,
): Promise<ProductionRequestPreview> {
  const draft = buildDefaultProductionRequestDraft(workspace);

  try {
    const response = await fetch(`${getSfsApiBaseUrl()}/requests/production/preview`, {
      method: "POST",
      headers: { "content-type": "application/json" },
      body: JSON.stringify(toApiPayload(draft)),
      cache: "no-store",
      next: { revalidate: 0 },
    });

    if (!response.ok) {
      return fallbackPreview(draft);
    }

    const preview = (await response.json()) as ProductionRequestPreviewResponse;
    return {
      source: "api",
      draft,
      markdown: preview.markdown,
    };
  } catch {
    return fallbackPreview(draft);
  }
}

function buildDefaultProductionRequestDraft(workspace: WorkspaceViewModel): ProductionRequestDraft {
  const character =
    workspace.characters.find((item) => item.slug === "jjiroo") ??
    workspace.characters.find((item) => item.hasBible && item.hasPrompts) ??
    workspace.characters[0];
  const format =
    workspace.formats.find((item) => item.slug === "pet-toon-image-only-v1") ?? workspace.formats[0];
  const characterSlug = character?.slug ?? "jjiroo";
  const formatProfileSlug = format?.slug ?? "pet-toon-image-only-v1";

  return {
    requestType: "new_episode",
    episodeSlug: `${characterSlug}-pilot-002`,
    characterSlug,
    formatProfileSlug,
    outputTarget: "vertical 1080x1920 mp4",
    referencePath: `characters/${characterSlug}/refs/canonical-pack`,
    completionCriteria: "final mp4, thumbnail, review report, publish metadata packet",
    creativeBrief: "Build a short vertical episode from existing character canon and keep the model stable.",
  };
}

function toApiPayload(draft: ProductionRequestDraft) {
  return {
    request_type: draft.requestType,
    episode_slug: draft.episodeSlug,
    character_slug: draft.characterSlug,
    format_profile_slug: draft.formatProfileSlug,
    output_target: draft.outputTarget,
    reference_path: draft.referencePath,
    completion_criteria: draft.completionCriteria,
    creative_brief: draft.creativeBrief,
  };
}

function fallbackPreview(draft: ProductionRequestDraft): ProductionRequestPreview {
  return {
    source: "sample",
    draft,
    markdown: [
      `# ${draft.requestType}: ${draft.episodeSlug}`,
      "",
      "## Workspace",
      "- root: /workspace/shortform-factory-studio",
      `- format: ${draft.formatProfileSlug}`,
      `- character: ${draft.characterSlug}`,
      "",
      "## Required output",
      `- ${draft.outputTarget}`,
      `- completion: ${draft.completionCriteria}`,
      "",
      "## Source assets",
      `- reference: ${draft.referencePath}`,
      "",
      "## Creative brief",
      draft.creativeBrief,
      "",
      "## Acceptance",
      "- Do not publish externally until rights.md is confirmed.",
      "- Keep generated character output aligned to the canonical reference pack.",
    ].join("\n"),
  };
}
