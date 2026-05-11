const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5000';

export interface GameInfo {
  externalId: string;
  title: string;
  playtimeMinutes: number;
  iconUrl: string | null;
  achievements?: {
    total: number;
    unlocked: number;
    recentAchievements: Array<{
      name: string;
      unlockTime: number;
    }>;
  };
}

export interface UnifiedStats {
  platform: string;
  userId: string;
  games: GameInfo[];
}

export interface ErrorResponse {
  error: string;
  message: string;
  statusCode: number;
}

export interface CacheMetrics {
  redisHits: number;
  postgresHits: number;
  apiCalls: number;
  totalRequests: number;
  redisHitRate: number;
  postgresHitRate: number;
  apiCallRate: number;
}

export async function fetchStats(platform: string, userId: string, refresh = false): Promise<UnifiedStats> {
  const url = `${API_BASE_URL}/api/stats/${platform}/${userId}${refresh ? '?refresh=true' : ''}`;

  const response = await fetch(url);

  if (!response.ok) {
    const error: ErrorResponse = await response.json();
    throw new Error(error.message || 'Failed to fetch stats');
  }

  return response.json();
}

export async function fetchMetrics(): Promise<CacheMetrics> {
  const response = await fetch(`${API_BASE_URL}/api/stats/metrics`);

  if (!response.ok) {
    throw new Error('Failed to fetch metrics');
  }

  return response.json();
}
