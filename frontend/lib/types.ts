export interface GameInfo {
  externalId: string;
  title: string;
  playtimeMinutes: number;
  iconUrl: string | null;
}

export interface UnifiedStats {
  platform: string;
  userId: string;
  games: GameInfo[];
}

export interface ErrorResponse {
  code: string;
  message: string;
  statusCode: number;
}

export type Platform = 'steam' | 'psn' | 'xbox';
