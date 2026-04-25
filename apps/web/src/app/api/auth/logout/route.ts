import { NextRequest, NextResponse } from "next/server";
import { AUTH_COOKIE_NAME, buildPublicUrl } from "@/lib/auth";

export async function POST(request: NextRequest) {
  const response = NextResponse.redirect(buildPublicUrl("/login", request.headers), { status: 303 });
  response.cookies.set({
    name: AUTH_COOKIE_NAME,
    value: "",
    httpOnly: true,
    sameSite: "lax",
    secure: process.env.NODE_ENV === "production",
    path: "/",
    maxAge: 0
  });
  return response;
}
