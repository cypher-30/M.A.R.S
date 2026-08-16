const BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export class ApiError extends Error {
  constructor(message: string, readonly status: number) {
    super(message);
  }
}

async function get<T>(path: string): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${BASE_URL}${path}`, { cache: "no-store" });
  } catch {
    throw new ApiError(`Can't reach the API at ${BASE_URL}. Start the backend and reload.`, 0);
  }
  if (response.status === 404) {
    throw new ApiError("Not found", 404);
  }
  if (!response.ok) {
    throw new ApiError(`The API returned ${response.status}.`, response.status);
  }
  return (await response.json()) as T;
}

export const api = {
  latestScore: () => get<import("./types").SectorScore>("/api/scores/latest"),
  scoreHistory: (limit = 90) =>
    get<import("./types").SectorScore[]>(`/api/scores/history?limit=${limit}`),
  alerts: (limit = 20) => get<import("./types").Alert[]>(`/api/alerts?limit=${limit}`),
  prices: (ticker: string, limit = 90) =>
    get<import("./types").PriceBar[]>(`/api/indicators/prices/${ticker}?limit=${limit}`),
};
