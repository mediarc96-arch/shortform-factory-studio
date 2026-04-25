import { NextRequest } from "next/server";
import { getSfsApiBaseUrl } from "@/lib/sfs-api";

type RouteContext = {
  params: Promise<{ episode: string; asset: string }>;
};

const FORWARDED_HEADERS = [
  "accept-ranges",
  "cache-control",
  "content-disposition",
  "content-length",
  "content-range",
  "content-type",
  "etag",
  "last-modified"
];

export async function GET(request: NextRequest, context: RouteContext): Promise<Response> {
  const { episode, asset } = await context.params;
  const target = new URL(
    `episodes/${encodeURIComponent(episode)}/files/${encodeURIComponent(asset)}`,
    `${getSfsApiBaseUrl().replace(/\/$/, "")}/`
  );

  const headers = new Headers();
  const range = request.headers.get("range");
  if (range) {
    headers.set("range", range);
  }

  const upstream = await fetch(target, { cache: "no-store", headers });
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
