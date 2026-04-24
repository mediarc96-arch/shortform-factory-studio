import { readdir, readFile } from "node:fs/promises";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const root = dirname(fileURLToPath(import.meta.url));
const messagesRoot = join(root, "../i18n/messages");
const baseLocale = "ko-KR";

function flatten(value, prefix = "") {
  return Object.entries(value).flatMap(([key, entry]) => {
    const next = prefix ? `${prefix}.${key}` : key;
    if (entry && typeof entry === "object" && !Array.isArray(entry)) {
      return flatten(entry, next);
    }
    return [next];
  });
}

async function readJson(path) {
  return JSON.parse(await readFile(path, "utf8"));
}

const locales = (await readdir(messagesRoot)).filter((item) => !item.startsWith("."));
const namespaces = (await readdir(join(messagesRoot, baseLocale))).filter((item) =>
  item.endsWith(".json")
);

let failed = false;

for (const namespace of namespaces) {
  const baseKeys = new Set(flatten(await readJson(join(messagesRoot, baseLocale, namespace))));

  for (const locale of locales) {
    const keys = new Set(flatten(await readJson(join(messagesRoot, locale, namespace))));
    const missing = [...baseKeys].filter((key) => !keys.has(key));
    const extra = [...keys].filter((key) => !baseKeys.has(key));

    if (missing.length || extra.length) {
      failed = true;
      console.error(`${locale}/${namespace}`);
      if (missing.length) {
        console.error(`  missing: ${missing.join(", ")}`);
      }
      if (extra.length) {
        console.error(`  extra: ${extra.join(", ")}`);
      }
    }
  }
}

if (failed) {
  process.exit(1);
}

console.log(`i18n parity ok: ${locales.length} locales, ${namespaces.length} namespaces`);
