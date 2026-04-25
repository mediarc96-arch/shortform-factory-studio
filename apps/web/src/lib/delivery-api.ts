import { getSfsApiBaseUrl } from "@/lib/sfs-api";

export type PublicDeliveryAsset = {
  key: "final_video" | "thumbnail" | "review_report" | "publish_packet";
  label: string;
  filename: string;
  content_type: string;
  size_bytes: number;
  download_path: string;
};

export type PublicDeliveryPackage = {
  episode_slug: string;
  token_id: string;
  max_accesses: number;
  access_count: number;
  expires_at: string;
  assets: PublicDeliveryAsset[];
};

export async function loadPublicDeliveryPackage(
  token: string
): Promise<PublicDeliveryPackage | null> {
  const target = new URL(
    `public/deliveries/${encodeURIComponent(token)}`,
    `${getSfsApiBaseUrl().replace(/\/$/, "")}/`
  );
  const response = await fetch(target, {
    cache: "no-store",
    headers: { accept: "application/json" }
  });
  if (!response.ok) return null;
  return (await response.json()) as PublicDeliveryPackage;
}
