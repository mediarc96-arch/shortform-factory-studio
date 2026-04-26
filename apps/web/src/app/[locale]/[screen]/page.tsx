import { notFound } from "next/navigation";
import { ConsoleShell } from "@/components/console-shell";
import { getDictionary } from "@/i18n/get-dictionary";
import { normalizeLocale, SCREEN_IDS, type ScreenId } from "@/i18n/locales";
import { loadProductionRequestPreview } from "@/lib/production-request-api";
import { loadWorkspaceViewModel } from "@/lib/workspace-api";

export default async function ConsolePage({
  params,
  searchParams
}: {
  params: Promise<{ locale: string; screen: string }>;
  searchParams: Promise<{ episode?: string | string[] }>;
}) {
  const { locale: rawLocale, screen: rawScreen } = await params;
  const { episode } = await searchParams;
  const locale = normalizeLocale(rawLocale);
  const screen = SCREEN_IDS.includes(rawScreen as ScreenId) ? (rawScreen as ScreenId) : null;

  if (!locale || !screen) {
    notFound();
  }

  const workspace = await loadWorkspaceViewModel();
  const requestPreview = screen === "request" ? await loadProductionRequestPreview(workspace) : undefined;

  return (
    <ConsoleShell
      dictionary={getDictionary(locale)}
      locale={locale}
      requestPreview={requestPreview}
      screen={screen}
      selectedEpisodeSlug={normalizeEpisodeQuery(episode)}
      workspace={workspace}
    />
  );
}

function normalizeEpisodeQuery(value: string | string[] | undefined): string | undefined {
  const episode = Array.isArray(value) ? value[0] : value;
  const trimmed = episode?.trim();
  return trimmed ? trimmed : undefined;
}
