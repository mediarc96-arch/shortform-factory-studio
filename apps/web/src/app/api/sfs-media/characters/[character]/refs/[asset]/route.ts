import { NextRequest } from "next/server";
import { getSfsApiBaseUrl } from "@/lib/sfs-api";

type RouteContext = {
  params: Promise<{ character: string; asset: string }>;
};

const FORWARDED_HEADERS = [
  "cache-control",
  "content-disposition",
  "content-length",
  "content-type",
  "etag",
  "last-modified"
];

export async function GET(_request: NextRequest, context: RouteContext): Promise<Response> {
  const { character, asset } = await context.params;
  const target = new URL(
    `characters/${encodeURIComponent(character)}/refs/${encodeURIComponent(asset)}`,
    `${getSfsApiBaseUrl().replace(/\/$/, "")}/`
  );

  const upstream = await fetch(target, { cache: "no-store" });
  const responseHeaders = new Headers();
  for (const key of FORWARDED_HEADERS) {
    const value = upstream.headers.get(key);
    if (value) {
      responseHeaders.set(key, value);
    }
  }
  responseHeaders.set("cache-control", "private, no-store");

  return new Response(upstream.body, {
    status: upstream.status,
    statusText: upstream.statusText,
    headers: responseHeaders
  });
}
