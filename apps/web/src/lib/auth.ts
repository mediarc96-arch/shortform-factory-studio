export const AUTH_COOKIE_NAME = "sfs_console_session";

const SESSION_TTL_SECONDS = 8 * 60 * 60;
const encoder = new TextEncoder();
const decoder = new TextDecoder();

type SessionPayload = {
  sub: string;
  role: "operator";
  exp: number;
};

export type AuthSession = {
  username: string;
  role: "operator";
  expiresAt: Date;
};

export function isAuthConfigured(): boolean {
  return Boolean(process.env.SFS_OPERATOR_PASSWORD && process.env.SFS_AUTH_SECRET);
}

export function getOperatorUsername(): string {
  return process.env.SFS_OPERATOR_USERNAME?.trim() || "sfs-admin";
}

export function isValidOperatorCredential(username: string, password: string): boolean {
  const expectedUsername = getOperatorUsername();
  const expectedPassword = process.env.SFS_OPERATOR_PASSWORD;
  if (!expectedPassword) return false;
  return username === expectedUsername && password === expectedPassword;
}

export function getSessionMaxAgeSeconds(): number {
  return SESSION_TTL_SECONDS;
}

export async function createSessionToken(username: string): Promise<string> {
  const payload: SessionPayload = {
    sub: username,
    role: "operator",
    exp: Math.floor(Date.now() / 1000) + SESSION_TTL_SECONDS
  };
  const encodedPayload = encodeBase64Url(JSON.stringify(payload));
  const signature = await sign(encodedPayload);
  return `${encodedPayload}.${signature}`;
}

export async function verifySessionToken(token: string | undefined): Promise<AuthSession | null> {
  if (!token || !isAuthConfigured()) return null;
  const [encodedPayload, signature, extra] = token.split(".");
  if (!encodedPayload || !signature || extra !== undefined) return null;

  const valid = await verify(encodedPayload, signature);
  if (!valid) return null;

  let payload: SessionPayload;
  try {
    payload = JSON.parse(decodeBase64Url(encodedPayload)) as SessionPayload;
  } catch {
    return null;
  }

  if (payload.role !== "operator" || payload.sub !== getOperatorUsername()) return null;
  if (!Number.isFinite(payload.exp) || payload.exp <= Math.floor(Date.now() / 1000)) {
    return null;
  }

  return {
    username: payload.sub,
    role: payload.role,
    expiresAt: new Date(payload.exp * 1000)
  };
}

export function normalizeNextPath(value: string | null): string {
  if (!value || !value.startsWith("/") || value.startsWith("//")) return "/ko/production";
  if (value.startsWith("/api/auth") || value.startsWith("/login")) return "/ko/production";
  return value;
}

async function sign(value: string): Promise<string> {
  const key = await importHmacKey();
  const signature = await crypto.subtle.sign("HMAC", key, encoder.encode(value));
  return bytesToBase64Url(new Uint8Array(signature));
}

async function verify(value: string, signature: string): Promise<boolean> {
  const key = await importHmacKey();
  try {
    return await crypto.subtle.verify(
      "HMAC",
      key,
      base64UrlToBytes(signature),
      encoder.encode(value)
    );
  } catch {
    return false;
  }
}

async function importHmacKey(): Promise<CryptoKey> {
  const secret = process.env.SFS_AUTH_SECRET;
  if (!secret) {
    throw new Error("SFS_AUTH_SECRET is required when SFS Console auth is enabled");
  }
  return crypto.subtle.importKey(
    "raw",
    encoder.encode(secret),
    { name: "HMAC", hash: "SHA-256" },
    false,
    ["sign", "verify"]
  );
}

function encodeBase64Url(value: string): string {
  return bytesToBase64Url(encoder.encode(value));
}

function decodeBase64Url(value: string): string {
  return decoder.decode(base64UrlToBytes(value));
}

function bytesToBase64Url(bytes: Uint8Array): string {
  let binary = "";
  for (const byte of bytes) {
    binary += String.fromCharCode(byte);
  }
  return btoa(binary).replaceAll("+", "-").replaceAll("/", "_").replaceAll("=", "");
}

function base64UrlToBytes(value: string): Uint8Array<ArrayBuffer> {
  const padded = value.replaceAll("-", "+").replaceAll("_", "/").padEnd(
    Math.ceil(value.length / 4) * 4,
    "="
  );
  const binary = atob(padded);
  const bytes = new Uint8Array(binary.length);
  for (let index = 0; index < binary.length; index += 1) {
    bytes[index] = binary.charCodeAt(index);
  }
  return bytes;
}
