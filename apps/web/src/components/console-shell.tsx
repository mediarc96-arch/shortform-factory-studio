"use client";

import { useEffect, useMemo } from "react";
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
import { statusLabel } from "@/lib/status";
import type { WorkspaceViewModel } from "@/lib/workspace-api";

type ConsoleShellProps = {
  dictionary: Dictionary;
  locale: SupportedLocale;
  screen: ScreenId;
  workspace: WorkspaceViewModel;
};

export function ConsoleShell({ dictionary, locale, screen, workspace }: ConsoleShellProps) {
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
    if (screen === "request") return <RequestScreen dictionary={dictionary} />;
    if (screen === "characters") return <CharactersScreen dictionary={dictionary} />;
    if (screen === "delivery") return <DeliveryScreen dictionary={dictionary} />;
    return <OpsScreen dictionary={dictionary} />;
  }, [dictionary, screen, workspace]);

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

function RequestScreen({ dictionary }: { dictionary: Dictionary }) {
  const { common, request } = dictionary;
  return (
    <section>
      <ScreenHeader
        eyebrow={request.eyebrow}
        title={request.title}
        subtitle={request.subtitle}
        actions={
          <>
            <button type="button">{common.validate}</button>
            <button className="primary" type="button">
              {common.copyMarkdown}
            </button>
          </>
        }
      />
      <div className="two-column">
        <Panel title={request.productionRequest} meta="new_episode">
          <FormGrid request={request} />
        </Panel>
        <Panel title={request.generatedMarkdown} meta={request.missingField} tone="warn">
          <pre className="markdown-preview">{`# new_episode: jjiroo-pilot-002

## Workspace
- root: /home/kindsr/projects/shortform-factory-studio
- format: pet-toon-image-only-v1
- character: jjiroo

## Required output
- final vertical mp4
- thumbnail candidate
- review report
- publish metadata packet

## Source assets
- canonical refs: characters/jjiroo/refs/canonical-pack
- background refs: missing`}</pre>
        </Panel>
      </div>
    </section>
  );
}

function CharactersScreen({ dictionary }: { dictionary: Dictionary }) {
  const { characters } = dictionary;
  return (
    <section>
      <ScreenHeader
        eyebrow={characters.eyebrow}
        title={characters.title}
        subtitle={characters.subtitle}
        actions={
          <>
            <button type="button">{characters.importRefs}</button>
            <button className="primary" type="button">
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
          <Panel title={characters.dossier} meta={characters.rightsReview}>
            <div className="form-grid">
              <Field label={characters.displayName} value="Jjiroo" />
              <Field label={characters.series} value="Pet Toon" />
              <Field label={characters.voiceDefault} value="warm Korean narrator" />
              <Field label={characters.rightsStatus} value="needs review" />
              <label className="wide">
                {characters.negativePrompt}
                <textarea defaultValue="Do not alter face structure, fur pattern, eye spacing, or collar color." />
              </label>
            </div>
          </Panel>
          <Panel title={characters.generatedFiles} meta={characters.templateBacked}>
            <FileRow kind="MD" name="characters/jjiroo/bible.md" detail="identity, behavior, visual canon" />
            <FileRow kind="MD" name="characters/jjiroo/prompts.md" detail="defaults and banned drift" />
            <FileRow kind="MD" name="characters/jjiroo/rights.md" detail="external use status" state="review" />
            <FileRow kind="JS" name="characters/jjiroo/voice.json" detail="voice slots and take policy" />
          </Panel>
        </div>
      </div>
    </section>
  );
}

function DeliveryScreen({ dictionary }: { dictionary: Dictionary }) {
  const { common, delivery } = dictionary;
  return (
    <section>
      <ScreenHeader
        eyebrow={delivery.eyebrow}
        title={delivery.title}
        subtitle={delivery.subtitle}
        actions={
          <>
            <button type="button">{common.revokeLink}</button>
            <button className="primary" type="button">
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
              <Field label={delivery.expires} value="2026-05-01 23:59 UTC" />
              <Field label={delivery.maxDownloads} value="5" />
              <label className="wide">
                {delivery.clientNote}
                <textarea defaultValue="Use revision request for timestamped feedback. Do not forward this link outside the approval group." />
              </label>
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
  return (
    <section>
      <ScreenHeader
        eyebrow={ops.eyebrow}
        title={ops.title}
        subtitle={ops.subtitle}
        actions={
          <>
            <button type="button">{common.openRunbook}</button>
            <button className="primary" type="button">
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

function FormGrid({ request }: { request: Dictionary["request"] }) {
  return (
    <div className="form-grid">
      <label>
        {request.requestType}
        <select defaultValue="new_episode">
          <option>new_episode</option>
          <option>revise_episode</option>
          <option>publish_only</option>
          <option>metadata_update</option>
        </select>
      </label>
      <label>
        {request.formatProfile}
        <select defaultValue="pet-toon-image-only-v1">
          <option>pet-toon-image-only-v1</option>
          <option>malmoelab-keyframe-dub-after-picture-v1</option>
        </select>
      </label>
      <Field label={request.episodeSlug} value="jjiroo-pilot-002" />
      <Field label={request.character} value="jjiroo" />
      <label className="wide">
        {request.referencePath}
        <input defaultValue="characters/jjiroo/refs/canonical-pack" />
      </label>
      <Field label={request.outputTarget} value="vertical 1080x1920, 42s, Korean narration" />
      <Field label={request.completionCriteria} value="final mp4, thumbnail, review report" />
      <label className="wide">
        {request.creativeBrief}
        <textarea defaultValue="Short emotional pet toon episode. Use existing character canon and keep warm pacing." />
      </label>
    </div>
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
