import { NextRequest, NextResponse } from "next/server";
import {
  AUTH_COOKIE_NAME,
  createSessionToken,
  getSessionMaxAgeSeconds,
  isAuthConfigured,
  isValidOperatorCredential,
  normalizeNextPath
} from "@/lib/auth";

export async function POST(request: NextRequest) {
  const formData = await request.formData();
  const username = String(formData.get("username") ?? "");
  const password = String(formData.get("password") ?? "");
  const nextPath = normalizeNextPath(String(formData.get("next") ?? ""));

  if (!isAuthConfigured() || !isValidOperatorCredential(username, password)) {
    const loginUrl = new URL("/login", request.url);
    loginUrl.searchParams.set("error", "1");
    loginUrl.searchParams.set("next", nextPath);
    return NextResponse.redirect(loginUrl, { status: 303 });
  }

  const response = NextResponse.redirect(new URL(nextPath, request.url), { status: 303 });
  response.cookies.set({
    name: AUTH_COOKIE_NAME,
    value: await createSessionToken(username),
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: getSessionMaxAgeSeconds()
  });
  return response;
}
