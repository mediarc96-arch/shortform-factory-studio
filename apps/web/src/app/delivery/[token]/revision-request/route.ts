import { NextRequest, NextResponse } from "next/server";
import { buildPublicUrl } from "@/lib/auth";
import { getSfsApiBaseUrl } from "@/lib/sfs-api";

type RouteContext = {
  params: Promise<{ token: string }>;
};

export async function POST(request: NextRequest, context: RouteContext) {
  const { token } = await context.params;
  const formData = await request.formData();
  const payload = {
    requester_name: String(formData.get("requester_name") ?? ""),
    requester_email: String(formData.get("requester_email") ?? ""),
    timestamp: String(formData.get("timestamp") ?? ""),
    message: String(formData.get("message") ?? "")
  };

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

  const redirectUrl = buildPublicUrl(
    `/delivery/${encodeURIComponent(token)}/revision`,
    request.headers
  );
  redirectUrl.searchParams.set("status", sent ? "sent" : "error");
  return NextResponse.redirect(redirectUrl, { status: 303 });
}
