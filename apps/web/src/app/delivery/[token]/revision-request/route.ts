import { NextRequest, NextResponse } from "next/server";
import { buildPublicUrl } from "@/lib/auth";
import { getSfsApiBaseUrl } from "@/lib/sfs-api";

type RouteContext = {
  params: Promise<{ token: string }>;
};

const REVISION_WINDOW_MS = 10 * 60 * 1000;
const REVISION_MAX_ATTEMPTS = 4;
const revisionAttempts = new Map<string, number[]>();

export async function POST(request: NextRequest, context: RouteContext) {
  const { token } = await context.params;
  const formData = await request.formData();
  const spamTrap = String(formData.get("company") ?? "").trim();
  if (spamTrap) {
    return redirectToResult(request, token, true);
  }
  if (isRateLimited(request, token)) {
    return redirectToResult(request, token, false);
  }

  const payload = {
    requester_name: readField(formData, "requester_name", 120),
    requester_email: readField(formData, "requester_email", 254),
    timestamp: readField(formData, "timestamp", 120),
    message: readField(formData, "message", 3000)
  };
  if (!payload.message) {
    return redirectToResult(request, token, false);
  }

  let sent = false;
  try {
    const target = new URL(
      `public/deliveries/${encodeURIComponent(token)}/revision-requests`,
      `${getSfsApiBaseUrl().replace(/\/$/, "")}/`
    );
    const response = await fetch(target, {
      method: "POST",
      headers: {
        accept: "application/json",
        "content-type": "application/json"
      },
      body: JSON.stringify(payload),
      cache: "no-store"
    });
    sent = response.ok;
  } catch {
    sent = false;
  }

  return redirectToResult(request, token, sent);
}

function readField(formData: FormData, key: string, maxLength: number) {
  return String(formData.get(key) ?? "").trim().slice(0, maxLength);
}

function isRateLimited(request: NextRequest, token: string) {
  const now = Date.now();
  const clientIp = (
    request.headers.get("x-forwarded-for")?.split(",")[0]?.trim() ||
    request.headers.get("x-real-ip") ||
    "local"
  );
  const key = `${clientIp}:${token.slice(0, 16)}`;
  const attempts = (revisionAttempts.get(key) ?? []).filter((time) => now - time < REVISION_WINDOW_MS);
  if (attempts.length >= REVISION_MAX_ATTEMPTS) {
    revisionAttempts.set(key, attempts);
    return true;
  }
  attempts.push(now);
  revisionAttempts.set(key, attempts);

  if (revisionAttempts.size > 1000) {
    for (const [storedKey, storedAttempts] of revisionAttempts.entries()) {
      if (storedAttempts.every((time) => now - time >= REVISION_WINDOW_MS)) {
        revisionAttempts.delete(storedKey);
      }
    }
  }
  return false;
}

function redirectToResult(request: NextRequest, token: string, sent: boolean) {
  const redirectUrl = buildPublicUrl(
    `/delivery/${encodeURIComponent(token)}/revision`,
    request.headers
  );
  redirectUrl.searchParams.set("status", sent ? "sent" : "error");
  return NextResponse.redirect(redirectUrl, { status: 303 });
}
