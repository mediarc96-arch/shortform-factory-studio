import { cookies } from "next/headers";
import { redirect } from "next/navigation";
import {
  AUTH_COOKIE_NAME,
  getOperatorUsername,
  isAuthConfigured,
  normalizeNextPath,
  verifySessionToken
} from "@/lib/auth";

export default async function LoginPage({
  searchParams
}: {
  searchParams: Promise<{ error?: string; next?: string }>;
}) {
  const params = await searchParams;
  const nextPath = normalizeNextPath(params.next ?? null);
  const cookieStore = await cookies();
  const session = await verifySessionToken(cookieStore.get(AUTH_COOKIE_NAME)?.value);

  if (session) {
    redirect(nextPath);
  }

  return (
    <main className="login-shell">
      <section className="login-panel" aria-labelledby="login-title">
        <div className="login-brand">
          <span>SFS</span>
          <div>
            <h1 id="login-title">운영자 로그인</h1>
            <p>Shortform Factory Studio</p>
          </div>
        </div>

        <form className="login-form" action="/api/auth/login" method="post">
          <input type="hidden" name="next" value={nextPath} />
          <label>
            계정
            <input
              autoComplete="username"
              autoFocus
              defaultValue={getOperatorUsername()}
              name="username"
              required
              type="text"
            />
          </label>
          <label>
            비밀번호
            <input autoComplete="current-password" name="password" required type="password" />
          </label>
          {params.error ? <p className="login-error">계정 또는 비밀번호를 확인하세요.</p> : null}
          {!isAuthConfigured() ? (
            <p className="login-error">SFS 인증 환경변수가 아직 설정되지 않았습니다.</p>
          ) : null}
          <button className="primary" disabled={!isAuthConfigured()} type="submit">
            로그인
          </button>
        </form>
      </section>
    </main>
  );
}
