import { loadPublicDeliveryPackage } from "@/lib/delivery-api";

export default async function PublicDeliveryPage({
  params
}: {
  params: Promise<{ token: string }>;
}) {
  const { token } = await params;
  const delivery = await loadPublicDeliveryPackage(token);

  if (!delivery) {
    return (
      <main className="public-delivery">
        <section className="delivery-public-panel">
          <div className="delivery-public-brand">SFS</div>
          <h1>전달 링크를 확인할 수 없습니다</h1>
          <p>링크가 만료되었거나 폐기되었습니다. 운영자에게 새 전달 링크를 요청하세요.</p>
        </section>
      </main>
    );
  }

  const finalVideo = delivery.assets.find((asset) => asset.key === "final_video");
  const thumbnail = delivery.assets.find((asset) => asset.key === "thumbnail");

  return (
    <main className="public-delivery">
      <section className="delivery-public-panel">
        <div className="delivery-public-header">
          <div className="delivery-public-brand">SFS</div>
          <div>
            <h1>{delivery.episode_slug}</h1>
            <p>{`${delivery.access_count}/${delivery.max_accesses} access · ${delivery.expires_at}`}</p>
          </div>
        </div>

        {finalVideo ? (
          <video
            className="delivery-video"
            controls
            poster={thumbnail?.download_path}
            preload="metadata"
            src={finalVideo.download_path}
          />
        ) : null}

        <div className="delivery-file-list">
          {delivery.assets.map((asset) => (
            <a href={asset.download_path} key={asset.key}>
              <strong>{asset.label}</strong>
              <span>{asset.filename}</span>
              <code>{formatBytes(asset.size_bytes)}</code>
            </a>
          ))}
        </div>

        <form
          className="delivery-revision-form"
          action={`/delivery/${encodeURIComponent(token)}/revision-request`}
          method="post"
        >
          <div>
            <h2>수정 요청</h2>
            <p>타임스탬프와 요청 내용을 남기면 SFS Console에 기록됩니다.</p>
          </div>
          <div className="delivery-form-grid">
            <label>
              이름
              <input name="requester_name" placeholder="Client" />
            </label>
            <label>
              이메일
              <input name="requester_email" placeholder="client@example.com" type="email" />
            </label>
            <label className="wide">
              타임스탬프
              <input name="timestamp" placeholder="예: 00:12 - 오프닝 컷" />
            </label>
            <label className="wide">
              요청 내용
              <textarea
                name="message"
                placeholder="수정할 장면, 원하는 방향, 기준 파일을 적어주세요."
                required
              />
            </label>
          </div>
          <button className="primary" type="submit">
            수정 요청 보내기
          </button>
        </form>
      </section>
    </main>
  );
}

function formatBytes(bytes: number): string {
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}
