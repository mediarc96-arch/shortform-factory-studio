"use client";

import { useEffect, useMemo, useState, useTransition } from "react";
import type { ReactNode } from "react";
import { useRouter } from "next/navigation";
import {
  navOrder,
  productionGates,
  referenceFiles,
  reviewFrames,
  shots
} from "@/features/console-data";
import {
  LOCALE_LABELS,
  SUPPORTED_LOCALES,
  toLocaleSegment,
  type ScreenId,
  type SupportedLocale
} from "@/i18n/locales";
import type { Dictionary } from "@/i18n/get-dictionary";
import type {
  ProductionRequestDraft,
  ProductionRequestPreview,
  ProductionRequestRecord
} from "@/lib/production-request-api";
import { statusLabel } from "@/lib/status";
import type { WorkspaceViewModel } from "@/lib/workspace-api";

type ConsoleShellProps = {
  dictionary: Dictionary;
  locale: SupportedLocale;
  requestPreview?: ProductionRequestPreview;
  screen: ScreenId;
  workspace: WorkspaceViewModel;
};

type ActionState = {
  tone: "idle" | "good" | "warn" | "risk";
  message: string;
};

type CharacterCreatePayload = {
  slug: string;
  display_name: string;
  series: string;
  voice_default: string;
  rights_status: "needs_review" | "production_safe" | "internal_only";
  negative_prompt: string;
};

type ProductionRequestPreviewResponse = {
  request_type: string;
  episode_slug: string;
  markdown: string;
};

type DeliveryTokenResponse = {
  id: string;
  episode_slug: string;
  status: string;
  max_accesses: number;
  access_count: number;
  expires_at: string;
  created_at: string;
  revoked_at: string | null;
  last_accessed_at: string | null;
  token: string | null;
};

type OpsHealthResponse = {
  status: string;
  components: { key: string; status: string; detail: string }[];
};

export function ConsoleShell({
  dictionary,
  locale,
  requestPreview,
  screen,
  workspace
}: ConsoleShellProps) {
  const router = useRouter();
  const common = dictionary.common;

  useEffect(() => {
    document.documentElement.lang = locale;
  }, [locale]);

  const navigate = (nextScreen: ScreenId) => {
    router.push(`/${toLocaleSegment(locale)}/${nextScreen}`);
  };

  const switchLocale = (nextLocale: SupportedLocale) => {
    router.push(`/${toLocaleSegment(nextLocale)}/${screen}`);
  };

  const currentScreen = useMemo(() => {
    if (screen === "production") {
      return <ProductionScreen dictionary={dictionary} navigate={navigate} workspace={workspace} />;
    }
    if (screen === "review") return <ReviewScreen dictionary={dictionary} navigate={navigate} />;
    if (screen === "request") {
      return <RequestScreen dictionary={dictionary} requestPreview={requestPreview} workspace={workspace} />;
    }
    if (screen === "characters") return <CharactersScreen dictionary={dictionary} workspace={workspace} />;
    if (screen === "delivery") return <DeliveryScreen dictionary={dictionary} workspace={workspace} />;
    return <OpsScreen dictionary={dictionary} />;
  }, [dictionary, requestPreview, screen, workspace]);

  return (
    <div className="console-app">
      <aside className="sidebar">
        <div className="brand">
          <div className="brand-mark">SFS</div>
          <div>
            <strong>{common.appName}</strong>
            <span>{common.appSubtitle}</span>
          </div>
        </div>

        <nav className="nav" aria-label="SFS Console screens">
          {navOrder.map((item) => (
            <button
              key={item}
              className={screen === item ? "active" : ""}
              type="button"
              onClick={() => navigate(item)}
            >
              <span className="nav-dot" />
              {common[`nav.${item}` as keyof typeof common]}
            </button>
          ))}
        </nav>

        <RailSection title={common.workspaceTitle}>
          <StatusRow label={common.scanner} tone="good" />
          <StatusRow label={common.postgres} tone="good" />
          <StatusRow label={common.paperclip} tone="warn" />
          <StatusRow label={common.rightsGate} tone="risk" />
        </RailSection>

        <RailSection title={common.fontTitle}>
          <p className="sidebar-note">{common.fontNote}</p>
          <code className="font-stack">Noto Sans KR / JP / SC</code>
        </RailSection>

        <RailSection title={common.designTitle}>
          <p className="sidebar-note">{common.designNote}</p>
        </RailSection>
      </aside>

      <main className="main">
        <header className="topbar">
          <div className="workspace-name">
            <strong>{common.workspace}</strong>
            <span>{common.workspacePath}</span>
          </div>
          <input className="search" aria-label="Global search" defaultValue={common.searchPlaceholder} />
          <div className="locale-switcher" aria-label={common.localeTitle}>
            {SUPPORTED_LOCALES.map((item) => (
              <button
                key={item}
                className={locale === item ? "active" : ""}
                type="button"
                onClick={() => switchLocale(item)}
              >
                {LOCALE_LABELS[item]}
              </button>
            ))}
          </div>
          <div className="operator">
            <span>OP</span>
            {common.operator}
            <form action="/api/auth/logout" method="post">
              <button className="logout-button" type="submit">
                {common.logout}
              </button>
            </form>
          </div>
        </header>

        {currentScreen}
      </main>
    </div>
  );
}

function RailSection({ title, children }: { title: string; children: ReactNode }) {
  return (
    <section className="rail-section">
      <h2>{title}</h2>
      <div className="rail-section-body">{children}</div>
    </section>
  );
}

function StatusRow({ label, tone }: { label: string; tone: "good" | "warn" | "risk" }) {
  return (
    <div className="status-row">
      <span>{label}</span>
      <i className={tone} />
    </div>
  );
}

function ScreenHeader({
  eyebrow,
  title,
  subtitle,
  actions
}: {
  eyebrow: string;
  title: string;
  subtitle: string;
  actions: ReactNode;
}) {
  return (
    <div className="screen-header">
      <div>
        <span className="screen-index">{eyebrow}</span>
        <h1>{title}</h1>
        <p>{subtitle}</p>
      </div>
      <div className="actions">{actions}</div>
    </div>
  );
}

function ProductionScreen({
  dictionary,
  navigate,
  workspace
}: {
  dictionary: Dictionary;
  navigate: (screen: ScreenId) => void;
  workspace: WorkspaceViewModel;
}) {
  const { common, production } = dictionary;

  return (
    <section>
      <ScreenHeader
        eyebrow={production.eyebrow}
        title={production.title}
        subtitle={production.subtitle}
        actions={
          <>
            <button type="button">{common.runScanner}</button>
            <button type="button" onClick={() => navigate("request")}>
              {common.newRequest}
            </button>
            <button className="primary" type="button" onClick={() => navigate("review")}>
              {common.openReview}
            </button>
          </>
        }
      />

      <div className="workspace-grid">
        <div className="stack">
          <Panel title={production.activeReview} meta={production.needsRights} tone="warn">
            <MediaPreview />
            <div className="status-strip">
              <InfoCell title={production.picture} detail={production.pictureDetail} />
              <InfoCell title={production.dubbing} detail={production.dubbingDetail} />
              <InfoCell title={production.review} detail={production.reviewDetail} />
              <InfoCell title={production.delivery} detail={production.deliveryDetail} />
            </div>
          </Panel>

          <Panel title={production.filmstrip} meta={production.shotEvidence}>
            <div className="filmstrip">
              {shots.map(([title, time]) => (
                <div className="shot" key={title}>
                  <div className="thumb portrait" />
                  <strong>{title}</strong>
                  <span>{time}</span>
                </div>
              ))}
            </div>
          </Panel>

          <Panel
            title={production.queue}
            meta={`${workspace.episodeCount} episodes · ${workspace.source}`}
          >
            <div className="queue-table">
              <div className="queue-row header">
                <span>Episode</span>
                <span>Character</span>
                <span>Status</span>
                <span>Next Gate</span>
                <span>Action</span>
              </div>
              {workspace.queue.map((episode) => (
                <div className="queue-row" key={episode.slug}>
                  <span>{episode.slug}</span>
                  <span>{episode.character}</span>
                  <span className={`badge ${episode.status}`}>{statusLabel(episode.status)}</span>
                  <span>{episode.nextGate}</span>
                  <button type="button" onClick={() => navigate(episode.status === "ready" ? "delivery" : "review")}>
                    {episode.status === "ready" ? "Package" : "Open"}
                  </button>
                </div>
              ))}
            </div>
          </Panel>
        </div>

        <div className="stack">
          <Panel title={production.gateStack} meta={production.openCount}>
            <div className="gate-list">
              {productionGates.map((gate) => (
                <div className={`gate ${gate.state}`} key={gate.index}>
                  <b>{gate.index}</b>
                  <div>
                    <strong>{gate.title}</strong>
                    <span>{gate.detail}</span>
                  </div>
                  <em>{gate.state}</em>
                </div>
              ))}
            </div>
          </Panel>

          <Panel title={production.producerNotes} meta={production.paperclipAware}>
            <Note title={production.bestNext} text={production.bestNextDetail} />
            <Note title={production.noGeneration} text={production.noGenerationDetail} />
            <Note title={production.deploymentConstraint} text={production.deploymentConstraintDetail} />
          </Panel>
        </div>
      </div>
    </section>
  );
}

function ReviewScreen({
  dictionary,
  navigate
}: {
  dictionary: Dictionary;
  navigate: (screen: ScreenId) => void;
}) {
  const { common, review } = dictionary;

  return (
    <section>
      <ScreenHeader
        eyebrow={review.eyebrow}
        title={review.title}
        subtitle={review.subtitle}
        actions={
          <>
            <button type="button">{common.requestRevision}</button>
            <button className="primary" type="button" onClick={() => navigate("delivery")}>
              {common.approveDelivery}
            </button>
          </>
        }
      />
      <div className="workspace-grid">
        <div className="stack">
          <Panel title={review.player} meta={review.format}>
            <MediaPreview />
            <div className="timeline">
              <Track label="picture" clips={[18, 24, 22, 25]} />
              <Track label="voice" clips={[31, 28, 18]} tone="voice" />
              <Track label="type" clips={[12, 14, 16]} tone="type" />
              <Track label="notes" clips={[8, 10]} tone="notes" />
            </div>
          </Panel>
          <Panel title={review.contactSheet} meta={review.frameMap}>
            <div className="contact-sheet">
              {reviewFrames.map(([frame, state]) => (
                <div className="frame" key={frame}>
                  <div className="thumb landscape" />
                  <span>{frame}</span>
                  <em>{state}</em>
                </div>
              ))}
            </div>
          </Panel>
        </div>
        <div className="stack">
          <Panel title={review.openNotes} meta={review.unresolved} tone="risk">
            <Note title="scene-04 / frame 1182" text="Character silhouette drifts from canonical ref." />
            <Note title="scene-05 / frame 1688" text="Subtitle contrast is low over bright background." />
            <Note title={review.rightsMissing} text="rights.md must be present before a public delivery token is issued." />
          </Panel>
          <Panel title={review.audioMeters} meta={review.withinTarget}>
            <Meter label="voice" value={74} suffix="-14 LU" />
            <Meter label="music" value={52} suffix="-22 LU" tone="warn" />
            <Meter label="sfx" value={61} suffix="-19 LU" />
            <Meter label="peak" value={31} suffix="-1.8 dB" tone="risk" />
          </Panel>
          <Panel title={review.decision} meta={review.conditional}>
            <Checklist
              items={[
                ["Final mp4 exists and matches target format", true],
                ["Review report generated", true],
                ["Rights note confirmed for public client delivery", false],
                ["Paperclip revision comment linked to episode", false]
              ]}
            />
          </Panel>
        </div>
      </div>
    </section>
  );
}

function RequestScreen({
  dictionary,
  requestPreview,
  workspace
}: {
  dictionary: Dictionary;
  requestPreview?: ProductionRequestPreview;
  workspace: WorkspaceViewModel;
}) {
  const { common, request } = dictionary;
  const initialDraft: ProductionRequestDraft = requestPreview?.draft ?? {
    requestType: "new_episode",
    episodeSlug: "jjiroo-pilot-002",
    characterSlug: "jjiroo",
    formatProfileSlug: "pet-toon-image-only-v1",
    outputTarget: "vertical 1080x1920 mp4",
    referencePath: "characters/jjiroo/refs/canonical-pack",
    completionCriteria: "final mp4, thumbnail, review report, publish metadata packet",
    creativeBrief: "Build a short vertical episode from existing character canon and keep the model stable."
  };
  const [draft, setDraft] = useState<ProductionRequestDraft>(initialDraft);
  const [markdown, setMarkdown] = useState(requestPreview?.markdown ?? "");
  const [savedRequests, setSavedRequests] = useState<ProductionRequestRecord[]>(
    requestPreview?.savedRequests ?? []
  );
  const [action, setAction] = useState<ActionState>({ tone: "idle", message: "" });
  const [isPending, startTransition] = useTransition();
  const previewSource = requestPreview?.source ?? "sample";

  const validateDraft = () => {
    startTransition(async () => {
      const result = await postJson<ProductionRequestPreviewResponse>(
        "/api/sfs/requests/production/preview",
        toProductionRequestPayload(draft)
      );
      if (!result.ok) {
        setAction({ tone: "risk", message: result.error });
        return;
      }
      setMarkdown(result.data.markdown);
      setAction({ tone: "good", message: "Markdown preview refreshed." });
    });
  };

  const saveDraft = () => {
    startTransition(async () => {
      const result = await postJson<ProductionRequestRecord>(
        "/api/sfs/requests/production",
        toProductionRequestPayload(draft)
      );
      if (!result.ok) {
        setAction({ tone: "risk", message: result.error });
        return;
      }
      setMarkdown(result.data.markdown);
      setSavedRequests((current) => [result.data, ...current.filter((item) => item.id !== result.data.id)]);
      setAction({ tone: "good", message: `Saved draft ${result.data.id.slice(0, 8)}.` });
    });
  };

  const sendToPaperclip = (requestId: string) => {
    startTransition(async () => {
      const result = await postJson<ProductionRequestRecord>(
        `/api/sfs/requests/production/${requestId}/paperclip`,
        {}
      );
      if (!result.ok) {
        setAction({ tone: "warn", message: result.error });
        return;
      }
      setSavedRequests((current) =>
        current.map((item) => (item.id === result.data.id ? result.data : item))
      );
      setAction({
        tone: "good",
        message: `Paperclip issue ${result.data.paperclip_issue_ref ?? result.data.id} linked.`
      });
    });
  };

  return (
    <section>
      <ScreenHeader
        eyebrow={request.eyebrow}
        title={request.title}
        subtitle={request.subtitle}
        actions={
          <>
            <button type="button" onClick={validateDraft} disabled={isPending}>
              {common.validate}
            </button>
            <button className="primary" type="button" onClick={saveDraft} disabled={isPending}>
              Save draft
            </button>
          </>
        }
      />
      <div className="two-column">
        <Panel title={request.productionRequest} meta={draft.requestType}>
          <FormGrid
            draft={draft}
            request={request}
            setDraft={setDraft}
            workspace={workspace}
          />
          <ActionMessage state={action} />
          <div className="saved-list">
            {savedRequests.length ? (
              savedRequests.slice(0, 5).map((item) => (
                <div className="saved-row" key={item.id}>
                  <div>
                    <strong>{item.episode_slug}</strong>
                    <span>{item.status}</span>
                  </div>
                  <code>{item.paperclip_issue_ref ?? item.id.slice(0, 8)}</code>
                  <button
                    type="button"
                    onClick={() => sendToPaperclip(item.id)}
                    disabled={isPending || Boolean(item.paperclip_issue_ref)}
                  >
                    Paperclip
                  </button>
                </div>
              ))
            ) : (
              <p className="empty-state">No saved production requests yet.</p>
            )}
          </div>
        </Panel>
        <Panel title={request.generatedMarkdown} meta={`Paperclip · ${previewSource}`}>
          <pre className="markdown-preview">{markdown}</pre>
        </Panel>
      </div>
    </section>
  );
}

function CharactersScreen({
  dictionary,
  workspace
}: {
  dictionary: Dictionary;
  workspace: WorkspaceViewModel;
}) {
  const { characters } = dictionary;
  const primaryCharacter = workspace.characters[0];
  const [payload, setPayload] = useState<CharacterCreatePayload>({
    slug: "new-character",
    display_name: "New Character",
    series: "Pet Toon",
    voice_default: "warm Korean narrator",
    rights_status: "needs_review",
    negative_prompt: "Do not alter face structure, fur pattern, eye spacing, or collar color."
  });
  const [createdFiles, setCreatedFiles] = useState<string[]>([]);
  const [action, setAction] = useState<ActionState>({ tone: "idle", message: "" });
  const [isPending, startTransition] = useTransition();

  const update = <Key extends keyof CharacterCreatePayload>(
    key: Key,
    value: CharacterCreatePayload[Key]
  ) => setPayload({ ...payload, [key]: value });

  const createCharacter = () => {
    startTransition(async () => {
      const result = await postJson<{ slug: string; created_files: string[] }>(
        "/api/sfs/characters",
        payload
      );
      if (!result.ok) {
        setAction({ tone: "risk", message: result.error });
        return;
      }
      setCreatedFiles(result.data.created_files);
      setAction({ tone: "good", message: `Created characters/${result.data.slug}.` });
    });
  };

  return (
    <section>
      <ScreenHeader
        eyebrow={characters.eyebrow}
        title={characters.title}
        subtitle={characters.subtitle}
        actions={
          <>
            <button type="button">{characters.importRefs}</button>
            <button
              className="primary"
              type="button"
              onClick={createCharacter}
              disabled={isPending}
            >
              {characters.createCharacter}
            </button>
          </>
        }
      />
      <div className="workspace-grid">
        <Panel title={characters.referenceWall} meta={characters.safeRefs}>
          <div className="reference-wall">
            {referenceFiles.map((file, index) => (
              <div className="reference" key={file}>
                <div className={`ref-art variant-${index % 3}`} />
                <span>{file}</span>
              </div>
            ))}
          </div>
        </Panel>
        <div className="stack">
          <Panel title={characters.dossier} meta={primaryCharacter?.rightsStatus ?? characters.rightsReview}>
            <div className="form-grid">
              <EditableField
                label="slug"
                value={payload.slug}
                onChange={(value) => update("slug", value)}
              />
              <EditableField
                label={characters.displayName}
                value={payload.display_name}
                onChange={(value) => update("display_name", value)}
              />
              <EditableField
                label={characters.series}
                value={payload.series}
                onChange={(value) => update("series", value)}
              />
              <EditableField
                label={characters.voiceDefault}
                value={payload.voice_default}
                onChange={(value) => update("voice_default", value)}
              />
              <label>
                {characters.rightsStatus}
                <select
                  value={payload.rights_status}
                  onChange={(event) =>
                    update("rights_status", event.target.value as CharacterCreatePayload["rights_status"])
                  }
                >
                  <option value="needs_review">needs_review</option>
                  <option value="production_safe">production_safe</option>
                  <option value="internal_only">internal_only</option>
                </select>
              </label>
              <label className="wide">
                {characters.negativePrompt}
                <textarea
                  value={payload.negative_prompt}
                  onChange={(event) => update("negative_prompt", event.target.value)}
                />
              </label>
            </div>
            <ActionMessage state={action} />
            {createdFiles.length ? (
              <div className="created-files">
                {createdFiles.map((file) => (
                  <code key={file}>{file}</code>
                ))}
              </div>
            ) : null}
          </Panel>
          <Panel
            title={characters.generatedFiles}
            meta={`${workspace.characterCount} characters · ${workspace.source}`}
          >
            <div className="character-list">
              {workspace.characters.map((character) => (
                <div className="character-row" key={character.slug}>
                  <div className="character-avatar">{character.slug.slice(0, 2).toUpperCase()}</div>
                  <div>
                    <strong>{character.displayName}</strong>
                    <span>{`characters/${character.slug}`}</span>
                  </div>
                  <div className="character-flags">
                    <span className={character.hasBible ? "present" : ""}>bible</span>
                    <span className={character.hasPrompts ? "present" : ""}>prompt</span>
                    <span className={character.rightsStatus === "present" ? "present" : "missing"}>
                      rights
                    </span>
                    <span className={character.hasVoice ? "present" : ""}>voice</span>
                  </div>
                </div>
              ))}
            </div>
          </Panel>
        </div>
      </div>
    </section>
  );
}

function DeliveryScreen({
  dictionary,
  workspace
}: {
  dictionary: Dictionary;
  workspace: WorkspaceViewModel;
}) {
  const { common, delivery } = dictionary;
  const initialEpisode =
    workspace.queue.find((episode) => episode.status === "ready")?.slug ?? workspace.queue[0]?.slug ?? "";
  const [episodeSlug, setEpisodeSlug] = useState(initialEpisode);
  const [expiresInHours, setExpiresInHours] = useState(168);
  const [maxAccesses, setMaxAccesses] = useState(5);
  const [token, setToken] = useState<DeliveryTokenResponse | null>(null);
  const [tokens, setTokens] = useState<DeliveryTokenResponse[]>([]);
  const [tokensLoaded, setTokensLoaded] = useState(false);
  const [isTokensLoading, setIsTokensLoading] = useState(false);
  const [action, setAction] = useState<ActionState>({ tone: "idle", message: "" });
  const [isPending, startTransition] = useTransition();
  const deliveryPath = token?.token ? `/delivery/${token.token}` : null;
  const tokenRows = useMemo(() => {
    if (!token) {
      return tokens;
    }
    return [token, ...tokens.filter((storedToken) => storedToken.id !== token.id)];
  }, [token, tokens]);

  useEffect(() => {
    let isMounted = true;

    const loadInitialTokens = async () => {
      setIsTokensLoading(true);
      const result = await getJson<DeliveryTokenResponse[]>("/api/sfs/deliveries/tokens");
      if (!isMounted) {
        return;
      }
      setIsTokensLoading(false);
      setTokensLoaded(true);
      if (!result.ok) {
        setAction({ tone: "risk", message: result.error });
        return;
      }
      setTokens(result.data);
    };

    void loadInitialTokens();
    return () => {
      isMounted = false;
    };
  }, []);

  const refreshTokens = async (reportErrors = false) => {
    const result = await getJson<DeliveryTokenResponse[]>("/api/sfs/deliveries/tokens");
    setTokensLoaded(true);
    if (!result.ok) {
      if (reportErrors) {
        setAction({ tone: "risk", message: result.error });
      }
      return null;
    }
    setTokens(result.data);
    return result.data;
  };

  const generateToken = () => {
    startTransition(async () => {
      const result = await postJson<DeliveryTokenResponse>("/api/sfs/deliveries/tokens", {
        episode_slug: episodeSlug,
        expires_in_hours: expiresInHours,
        max_accesses: maxAccesses
      });
      if (!result.ok) {
        setAction({ tone: "risk", message: result.error });
        return;
      }
      setToken(result.data);
      setTokens((currentTokens) => [
        result.data,
        ...currentTokens.filter((currentToken) => currentToken.id !== result.data.id)
      ]);
      setAction({ tone: "good", message: `Delivery token issued for ${result.data.episode_slug}.` });
      await refreshTokens();
    });
  };

  const revokeToken = (tokenId?: string) => {
    const selectedToken = tokenId ? tokenRows.find((row) => row.id === tokenId) : token;
    if (!selectedToken) {
      setAction({ tone: "warn", message: "No active token selected." });
      return;
    }
    startTransition(async () => {
      const result = await postJson<DeliveryTokenResponse>(
        `/api/sfs/deliveries/tokens/${selectedToken.id}/revoke`,
        {}
      );
      if (!result.ok) {
        setAction({ tone: "risk", message: result.error });
        return;
      }
      if (token?.id === result.data.id) {
        setToken(result.data);
      }
      setTokens((currentTokens) => [
        result.data,
        ...currentTokens.filter((currentToken) => currentToken.id !== result.data.id)
      ]);
      setAction({ tone: "good", message: `Token ${result.data.id.slice(0, 8)} revoked.` });
      await refreshTokens();
    });
  };

  return (
    <section>
      <ScreenHeader
        eyebrow={delivery.eyebrow}
        title={delivery.title}
        subtitle={delivery.subtitle}
        actions={
          <>
            <button
              type="button"
              onClick={() => revokeToken()}
              disabled={isPending || !token || token.status !== "active"}
            >
              {common.revokeLink}
            </button>
            <button
              className="primary"
              type="button"
              onClick={generateToken}
              disabled={isPending || !episodeSlug}
            >
              {common.generateToken}
            </button>
          </>
        }
      />
      <div className="delivery-grid">
        <Panel title={delivery.clientPreview} meta={delivery.safePackage}>
          <div className="phone-preview">
            <div className="phone-art" />
            <div className="phone-copy">
              <h2>jjiroo-pilot-001 delivery</h2>
              <p>Final video, thumbnail, review report, and publish metadata are available until 2026-05-01.</p>
              <button className="primary" type="button">
                {delivery.downloadPackage}
              </button>
            </div>
          </div>
        </Panel>
        <div className="stack">
          <Panel title={delivery.includedFiles} meta={delivery.selected}>
            <FileRow kind="MP4" name="final-vertical.mp4" detail="1080x1920, approved" />
            <FileRow kind="PNG" name="thumbnail.png" detail="client preview image" />
            <FileRow kind="MD" name="review-report.md" detail="scene notes and QA result" />
            <FileRow kind="JS" name="publish-packet.json" detail="title, description, tags" />
          </Panel>
          <Panel title={delivery.accessPolicy} meta={delivery.tokenized}>
            <div className="form-grid">
              <label className="wide">
                Episode
                <select value={episodeSlug} onChange={(event) => setEpisodeSlug(event.target.value)}>
                  {workspace.queue.map((episode) => (
                    <option value={episode.slug} key={episode.slug}>
                      {episode.slug}
                    </option>
                  ))}
                </select>
              </label>
              <label>
                {delivery.expires}
                <input
                  min={1}
                  max={1440}
                  type="number"
                  value={expiresInHours}
                  onChange={(event) => setExpiresInHours(Number(event.target.value))}
                />
              </label>
              <label>
                {delivery.maxDownloads}
                <input
                  min={1}
                  max={100}
                  type="number"
                  value={maxAccesses}
                  onChange={(event) => setMaxAccesses(Number(event.target.value))}
                />
              </label>
              <label className="wide">
                {delivery.clientNote}
                <textarea defaultValue="Use revision request for timestamped feedback. Do not forward this link outside the approval group." />
              </label>
            </div>
            <ActionMessage state={action} />
            {token ? (
              <div className="token-box">
                <strong>{token.status}</strong>
                <code>{deliveryPath ?? token.id}</code>
                {deliveryPath ? <a href={deliveryPath}>{delivery.downloadPackage}</a> : null}
                <span>{`${token.access_count}/${token.max_accesses} - ${formatDateTime(token.expires_at)}`}</span>
              </div>
            ) : null}
          </Panel>
          <Panel
            title={delivery.tokenHistory}
            meta={isTokensLoading ? delivery.loadingTokens : `${tokenRows.length} ${delivery.tokens}`}
          >
            <div className="token-history">
              <div className="token-row token-row-head">
                <span>{delivery.episode}</span>
                <span>{delivery.status}</span>
                <span>{delivery.accesses}</span>
                <span>{delivery.expires}</span>
                <span>{delivery.lastAccess}</span>
                <span>{common.revokeLink}</span>
              </div>
              {tokenRows.map((row) => (
                <div className="token-row" key={row.id}>
                  <span>
                    <strong>{row.episode_slug}</strong>
                    <code>{`${row.id.slice(0, 8)} - ${formatDateTime(row.created_at)}`}</code>
                  </span>
                  <span>
                    <span className={`badge ${row.status === "active" ? "ready" : "risk"}`}>
                      {row.status}
                    </span>
                  </span>
                  <span>{`${row.access_count}/${row.max_accesses}`}</span>
                  <span>{formatDateTime(row.expires_at)}</span>
                  <span>{formatDateTime(row.last_accessed_at, delivery.notAccessed)}</span>
                  <span>
                    <button
                      type="button"
                      onClick={() => revokeToken(row.id)}
                      disabled={isPending || row.status !== "active"}
                    >
                      {common.revokeLink}
                    </button>
                  </span>
                </div>
              ))}
              {tokenRows.length === 0 ? (
                <p className="empty-state">
                  {tokensLoaded ? delivery.noTokens : delivery.loadingTokens}
                </p>
              ) : null}
            </div>
          </Panel>
          <Panel title={delivery.audit} meta={delivery.readonly}>
            <Note title="2026-04-24 08:12 UTC" text="Producer generated package draft." />
            <Note title="2026-04-24 08:18 UTC" text="Rights gate passed after Character Lab update." />
          </Panel>
        </div>
      </div>
    </section>
  );
}

function OpsScreen({ dictionary }: { dictionary: Dictionary }) {
  const { common, ops } = dictionary;
  const [health, setHealth] = useState<OpsHealthResponse | null>(null);
  const [action, setAction] = useState<ActionState>({ tone: "idle", message: "" });
  const [isPending, startTransition] = useTransition();

  const runHealthCheck = () => {
    startTransition(async () => {
      const result = await getJson<OpsHealthResponse>("/api/sfs/ops/health");
      if (!result.ok) {
        setAction({ tone: "risk", message: result.error });
        return;
      }
      setHealth(result.data);
      setAction({ tone: result.data.status === "ok" ? "good" : "warn", message: result.data.status });
    });
  };

  return (
    <section>
      <ScreenHeader
        eyebrow={ops.eyebrow}
        title={ops.title}
        subtitle={ops.subtitle}
        actions={
          <>
            <button type="button">{common.openRunbook}</button>
            <button
              className="primary"
              type="button"
              onClick={runHealthCheck}
              disabled={isPending}
            >
              {common.runHealthCheck}
            </button>
          </>
        }
      />
      <div className="stack">
        <Panel title={ops.runtimeMap} meta={ops.edgeRoute}>
          <div className="ops-map">
            <OpsNode label="public" title="sfs.devscent.com" text="External entry through nginx only. No direct host port." />
            <OpsNode label="web" title="sfs-web:3000" text="Next.js app serving console and delivery pages." />
            <OpsNode label="api" title="sfs-api:8000" text="FastAPI scanner, auth, media proxy, delivery token API." />
            <OpsNode label="db" title="postgres14" text="Shared Postgres in /opt/infra for metadata and audit only." />
            <OpsNode label="exec" title="pc.devscent.com" text="Paperclip remains the work execution surface." />
          </div>
          <ActionMessage state={action} />
          {health ? (
            <div className="health-list">
              {health.components.map((component) => (
                <div className="health-row" key={component.key}>
                  <strong>{component.key}</strong>
                  <span className={`badge ${component.status === "ok" ? "ready" : "review"}`}>
                    {component.status}
                  </span>
                  <code>{component.detail}</code>
                </div>
              ))}
            </div>
          ) : null}
        </Panel>
        <div className="three-column">
          <Panel title={ops.scanner} meta="ok">
            <Checklist
              items={[
                ["characters/ indexed", true],
                ["episodes/ indexed", true],
                ["formats/ indexed", true],
                ["missing assets reported without deleting files", false]
              ]}
            />
          </Panel>
          <Panel title={ops.security} meta="MVP">
            <Checklist
              items={[
                ["role-based internal auth", true],
                ["delivery token expiry", true],
                ["signed media URLs", false],
                ["audit export for client access", false]
              ]}
            />
          </Panel>
          <Panel title={ops.architecture} meta={ops.recommended}>
            <Note title={ops.backend} text="Python FastAPI, clean architecture, SQLAlchemy, Alembic, unittest/pytest." />
            <Note title={ops.frontend} text="Next.js App Router, typed dictionaries, Playwright smoke tests." />
            <Note title={ops.worker} text="Optional Python process for scanner/export jobs after MVP read flow lands." />
          </Panel>
        </div>
      </div>
    </section>
  );
}

function Panel({
  title,
  meta,
  tone,
  children
}: {
  title: string;
  meta?: string;
  tone?: "warn" | "risk";
  children: ReactNode;
}) {
  return (
    <section className="panel">
      <header>
        <strong>{title}</strong>
        {meta ? <span className={`badge ${tone ?? ""}`}>{meta}</span> : null}
      </header>
      <div className="panel-body">{children}</div>
    </section>
  );
}

function MediaPreview() {
  return (
    <div className="media-preview" aria-label="Video preview placeholder">
      <div className="scene-card primary-scene" />
      <div className="scene-card secondary-scene" />
      <button type="button" className="play-button" aria-label="Play preview">
        ▶
      </button>
      <span className="timecode">00:19:08 / 00:42:00</span>
    </div>
  );
}

function InfoCell({ title, detail }: { title: string; detail: string }) {
  return (
    <div>
      <strong>{title}</strong>
      <span>{detail}</span>
    </div>
  );
}

function Note({ title, text }: { title: string; text: string }) {
  return (
    <div className="note">
      <strong>{title}</strong>
      <span>{text}</span>
    </div>
  );
}

function Track({
  label,
  clips,
  tone = "picture"
}: {
  label: string;
  clips: number[];
  tone?: "picture" | "voice" | "type" | "notes";
}) {
  let left = 0;
  return (
    <div className="track-row">
      <span>{label}</span>
      <div className="track">
        {clips.map((width, index) => {
          const style = { left: `${left}%`, width: `${width}%` };
          left += width + 4;
          return <i className={tone} style={style} key={`${label}-${index}`} />;
        })}
      </div>
    </div>
  );
}

function Meter({
  label,
  value,
  suffix,
  tone
}: {
  label: string;
  value: number;
  suffix: string;
  tone?: "warn" | "risk";
}) {
  return (
    <div className="meter">
      <span>{label}</span>
      <div>
        <i className={tone ?? ""} style={{ width: `${value}%` }} />
      </div>
      <em>{suffix}</em>
    </div>
  );
}

function Checklist({ items }: { items: [string, boolean][] }) {
  return (
    <div className="checklist">
      {items.map(([label, checked]) => (
        <div className="check" key={label}>
          <span className={checked ? "checked" : ""} />
          {label}
        </div>
      ))}
    </div>
  );
}

function Field({ label, value }: { label: string; value: string }) {
  return (
    <label>
      {label}
      <input defaultValue={value} />
    </label>
  );
}

function FormGrid({
  draft,
  request,
  setDraft,
  workspace
}: {
  draft: ProductionRequestDraft;
  request: Dictionary["request"];
  setDraft: (draft: ProductionRequestDraft) => void;
  workspace: WorkspaceViewModel;
}) {
  const formatOptions =
    workspace.formats.length > 0 ? workspace.formats.map((format) => format.slug) : [draft.formatProfileSlug];
  const characterOptions =
    workspace.characters.length > 0
      ? workspace.characters.map((character) => character.slug)
      : [draft.characterSlug];
  const update = <Key extends keyof ProductionRequestDraft>(
    key: Key,
    value: ProductionRequestDraft[Key]
  ) => setDraft({ ...draft, [key]: value });

  return (
    <div className="form-grid">
      <label>
        {request.requestType}
        <select
          value={draft.requestType}
          onChange={(event) =>
            update("requestType", event.target.value as ProductionRequestDraft["requestType"])
          }
        >
          <option value="new_episode">new_episode</option>
          <option value="revise_episode">revise_episode</option>
          <option value="publish_only">publish_only</option>
          <option value="metadata_update">metadata_update</option>
        </select>
      </label>
      <label>
        {request.formatProfile}
        <select
          value={draft.formatProfileSlug}
          onChange={(event) => update("formatProfileSlug", event.target.value)}
        >
          {formatOptions.map((format) => (
            <option value={format} key={format}>
              {format}
            </option>
          ))}
        </select>
      </label>
      <EditableField
        label={request.episodeSlug}
        value={draft.episodeSlug}
        onChange={(value) => update("episodeSlug", value)}
      />
      <label>
        {request.character}
        <select
          value={draft.characterSlug}
          onChange={(event) => update("characterSlug", event.target.value)}
        >
          {characterOptions.map((character) => (
            <option value={character} key={character}>
              {character}
            </option>
          ))}
        </select>
      </label>
      <label className="wide">
        {request.referencePath}
        <input
          value={draft.referencePath}
          onChange={(event) => update("referencePath", event.target.value)}
        />
      </label>
      <EditableField
        label={request.outputTarget}
        value={draft.outputTarget}
        onChange={(value) => update("outputTarget", value)}
      />
      <EditableField
        label={request.completionCriteria}
        value={draft.completionCriteria}
        onChange={(value) => update("completionCriteria", value)}
      />
      <label className="wide">
        {request.creativeBrief}
        <textarea
          value={draft.creativeBrief}
          onChange={(event) => update("creativeBrief", event.target.value)}
        />
      </label>
    </div>
  );
}

function EditableField({
  label,
  value,
  onChange
}: {
  label: string;
  value: string;
  onChange: (value: string) => void;
}) {
  return (
    <label>
      {label}
      <input value={value} onChange={(event) => onChange(event.target.value)} />
    </label>
  );
}

function FileRow({
  kind,
  name,
  detail,
  state = "ok"
}: {
  kind: string;
  name: string;
  detail: string;
  state?: "ok" | "review";
}) {
  return (
    <div className="file-row">
      <span>{kind}</span>
      <div>
        <strong>{name}</strong>
        <small>{detail}</small>
      </div>
      <em>{state}</em>
    </div>
  );
}

function OpsNode({ label, title, text }: { label: string; title: string; text: string }) {
  return (
    <div className="ops-node">
      <span className="badge">{label}</span>
      <strong>{title}</strong>
      <p>{text}</p>
    </div>
  );
}

function ActionMessage({ state }: { state: ActionState }) {
  if (!state.message) {
    return null;
  }
  return <div className={`action-message ${state.tone}`}>{state.message}</div>;
}

function formatDateTime(value: string | null, fallback = "n/a") {
  if (!value) {
    return fallback;
  }
  const date = new Date(value);
  if (Number.isNaN(date.getTime())) {
    return value;
  }
  return date.toISOString().slice(0, 16).replace("T", " ");
}

function toProductionRequestPayload(draft: ProductionRequestDraft) {
  return {
    request_type: draft.requestType,
    episode_slug: draft.episodeSlug,
    character_slug: draft.characterSlug,
    format_profile_slug: draft.formatProfileSlug,
    output_target: draft.outputTarget,
    reference_path: draft.referencePath,
    completion_criteria: draft.completionCriteria,
    creative_brief: draft.creativeBrief
  };
}

async function getJson<T>(url: string): Promise<{ ok: true; data: T } | { ok: false; error: string }> {
  try {
    const response = await fetch(url, {
      headers: { accept: "application/json" },
      cache: "no-store"
    });
    return parseJsonResponse<T>(response);
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Request failed" };
  }
}

async function postJson<T>(
  url: string,
  payload: unknown
): Promise<{ ok: true; data: T } | { ok: false; error: string }> {
  try {
    const response = await fetch(url, {
      method: "POST",
      headers: {
        accept: "application/json",
        "content-type": "application/json"
      },
      body: JSON.stringify(payload),
      cache: "no-store"
    });
    return parseJsonResponse<T>(response);
  } catch (error) {
    return { ok: false, error: error instanceof Error ? error.message : "Request failed" };
  }
}

async function parseJsonResponse<T>(
  response: Response
): Promise<{ ok: true; data: T } | { ok: false; error: string }> {
  const text = await response.text();
  const data = text ? JSON.parse(text) : null;
  if (!response.ok) {
    const detail =
      data && typeof data === "object" && "detail" in data
        ? String((data as { detail: unknown }).detail)
        : response.statusText;
    return { ok: false, error: detail };
  }
  return { ok: true, data: data as T };
}
