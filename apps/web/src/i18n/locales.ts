export const SUPPORTED_LOCALES = ["ko-KR", "en-US", "ja-JP", "zh-CN", "es-ES"] as const;
export type SupportedLocale = (typeof SUPPORTED_LOCALES)[number];

export const DEFAULT_LOCALE: SupportedLocale = "ko-KR";

export const LOCALE_SEGMENTS: Record<SupportedLocale, string> = {
  "ko-KR": "ko",
  "en-US": "en",
  "ja-JP": "ja",
  "zh-CN": "zh",
  "es-ES": "es"
};

export const LOCALE_LABELS: Record<SupportedLocale, string> = {
  "ko-KR": "KO",
  "en-US": "US",
  "ja-JP": "JP",
  "zh-CN": "CN",
  "es-ES": "SP"
};

export const SCREEN_IDS = ["production", "review", "request", "characters", "delivery", "ops"] as const;
export type ScreenId = (typeof SCREEN_IDS)[number];

const LOCALE_BY_SEGMENT = Object.fromEntries(
  Object.entries(LOCALE_SEGMENTS).map(([locale, segment]) => [segment, locale])
) as Record<string, SupportedLocale>;

export function normalizeLocale(value: string): SupportedLocale | null {
  if (SUPPORTED_LOCALES.includes(value as SupportedLocale)) {
    return value as SupportedLocale;
  }
  return LOCALE_BY_SEGMENT[value] ?? null;
}

export function toLocaleSegment(locale: SupportedLocale): string {
  return LOCALE_SEGMENTS[locale];
}
