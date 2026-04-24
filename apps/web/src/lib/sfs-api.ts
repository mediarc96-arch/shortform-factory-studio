const DEFAULT_SFS_API_BASE_URL = "http://127.0.0.1:8000";

export function getSfsApiBaseUrl(): string {
  return process.env.SFS_API_BASE_URL ?? DEFAULT_SFS_API_BASE_URL;
}
