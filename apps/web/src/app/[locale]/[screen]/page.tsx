import { notFound } from "next/navigation";
import { ConsoleShell } from "@/components/console-shell";
import { getDictionary } from "@/i18n/get-dictionary";
import { normalizeLocale, SCREEN_IDS, type ScreenId } from "@/i18n/locales";

export default async function ConsolePage({
  params
}: {
  params: Promise<{ locale: string; screen: string }>;
}) {
  const { locale: rawLocale, screen: rawScreen } = await params;
  const locale = normalizeLocale(rawLocale);
  const screen = SCREEN_IDS.includes(rawScreen as ScreenId) ? (rawScreen as ScreenId) : null;

  if (!locale || !screen) {
    notFound();
  }

  return <ConsoleShell dictionary={getDictionary(locale)} locale={locale} screen={screen} />;
}
