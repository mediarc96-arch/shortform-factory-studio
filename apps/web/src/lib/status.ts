export function statusLabel(status: "review" | "blocked" | "ready"): string {
  if (status === "ready") {
    return "ready";
  }
  if (status === "blocked") {
    return "blocked";
  }
  return "review";
}
