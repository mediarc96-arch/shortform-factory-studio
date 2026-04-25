import Link from "next/link";

export default async function PublicDeliveryRevisionPage({
  params,
  searchParams
}: {
  params: Promise<{ token: string }>;
  searchParams: Promise<{ status?: string }>;
}) {
  const { token } = await params;
  const { status } = await searchParams;
  const sent = status === "sent";

  return (
    <main className="public-delivery">
      <section className="delivery-public-panel delivery-result-panel">
        <div className="delivery-public-brand">SFS</div>
        <h1>{sent ? "수정 요청을 받았습니다" : "수정 요청을 저장하지 못했습니다"}</h1>
        <p>
          {sent
            ? "SFS Console에 요청이 기록되었습니다. 운영자가 확인 후 다음 전달본에 반영합니다."
            : "링크가 만료되었거나 일시적인 오류가 발생했습니다. 다시 시도하거나 운영자에게 새 링크를 요청하세요."}
        </p>
        <div className="delivery-result-actions">
          <Link href={`/delivery/${encodeURIComponent(token)}`}>전달 페이지로 돌아가기</Link>
        </div>
      </section>
    </main>
  );
}
