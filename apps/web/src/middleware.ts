import { NextRequest, NextResponse } from "next/server";
import { AUTH_COOKIE_NAME, isAuthConfigured, normalizeNextPath, verifySessionToken } from "@/lib/auth";

const PUBLIC_PREFIXES = ["/_next", "/api/auth", "/delivery", "/login"];

export async function middleware(request: NextRequest) {
  if (!isAuthConfigured() || isPublicPath(request.nextUrl.pathname)) {
    return NextResponse.next();
  }

  const session = await verifySessionToken(request.cookies.get(AUTH_COOKIE_NAME)?.value);
  if (session) {
    return NextResponse.next();
  }

  if (request.nextUrl.pathname.startsWith("/api/")) {
    return NextResponse.json({ detail: "Authentication required" }, { status: 401 });
  }

  const loginUrl = request.nextUrl.clone();
  loginUrl.pathname = "/login";
  loginUrl.search = "";
  loginUrl.searchParams.set("next", normalizeNextPath(`${request.nextUrl.pathname}${request.nextUrl.search}`));
  return NextResponse.redirect(loginUrl);
}

function isPublicPath(pathname: string): boolean {
  if (PUBLIC_PREFIXES.some((prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`))) {
    return true;
  }
  return pathname === "/favicon.ico" || pathname === "/robots.txt";
}

export const config = {
  matcher: ["/((?!_next/static|_next/image|favicon.ico).*)"]
};
