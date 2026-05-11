'use client';

import { useState } from 'react';
import { fetchStats, UnifiedStats } from '@/lib/api';
import { extractSteamId } from '@/lib/utils';
import StatsDisplay from './components/StatsDisplay';
import RecentAchievements from './components/RecentAchievements';

type Platform = 'steam' | 'psn' | 'xbox';

export default function Home() {
  const [platform, setPlatform] = useState<Platform>('steam');
  const [userId, setUserId] = useState('');
  const [stats, setStats] = useState<UnifiedStats | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    if (!userId.trim()) return;

    setLoading(true);
    setError(null);
    setStats(null);

    try {
      // Для Steam извлекаем ID из URL, если пользователь вставил полный URL
      const processedUserId = platform === 'steam'
        ? extractSteamId(userId.trim())
        : userId.trim();

      const data = await fetchStats(platform, processedUserId);
      setStats(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to fetch stats');
    } finally {
      setLoading(false);
    }
  };

  const platformPlaceholders = {
    steam: 'Enter Steam username or ID',
    psn: 'Enter PSN Online ID',
    xbox: 'Enter Xbox Gamertag',
  };

  const platformHints = {
    steam: 'Paste your Steam profile URL or enter your custom URL/Steam ID64',
    psn: 'Your PlayStation Network Online ID',
    xbox: 'Your Xbox Live Gamertag',
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-zinc-50 to-zinc-100 dark:from-zinc-950 dark:to-black py-12 px-4">
      <div className="max-w-6xl mx-auto">
        <header className="text-center mb-12">
          <h1 className="text-5xl font-bold text-zinc-900 dark:text-zinc-50 mb-3">
            🎮 GameStats Aggregator
          </h1>
          <p className="text-lg text-zinc-600 dark:text-zinc-400">
            View your gaming stats across Steam, PlayStation, and Xbox
          </p>
        </header>

        <div className="bg-white dark:bg-zinc-900 rounded-xl shadow-lg p-8 mb-8">
          <form onSubmit={handleSubmit} className="space-y-6">
            <div>
              <label className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-3">
                Select Platform
              </label>
              <div className="grid grid-cols-3 gap-3">
                {(['steam', 'psn', 'xbox'] as Platform[]).map((p) => (
                  <button
                    key={p}
                    type="button"
                    onClick={() => setPlatform(p)}
                    className={`py-3 px-4 rounded-lg font-semibold transition-all ${
                      platform === p
                        ? 'bg-blue-600 text-white shadow-md'
                        : 'bg-zinc-100 dark:bg-zinc-800 text-zinc-700 dark:text-zinc-300 hover:bg-zinc-200 dark:hover:bg-zinc-700'
                    }`}
                  >
                    {p.toUpperCase()}
                  </button>
                ))}
              </div>
            </div>

            <div>
              <label htmlFor="userId" className="block text-sm font-medium text-zinc-700 dark:text-zinc-300 mb-2">
                User ID
              </label>
              <input
                id="userId"
                type="text"
                value={userId}
                onChange={(e) => setUserId(e.target.value)}
                placeholder={platformPlaceholders[platform]}
                className="w-full px-4 py-3 rounded-lg border border-zinc-300 dark:border-zinc-700 bg-white dark:bg-zinc-800 text-zinc-900 dark:text-zinc-100 focus:ring-2 focus:ring-blue-500 focus:border-transparent outline-none"
              />
              <p className="mt-2 text-xs text-zinc-500 dark:text-zinc-400">
                {platformHints[platform]}
              </p>
            </div>

            <button
              type="submit"
              disabled={loading || !userId.trim()}
              className="w-full py-3 px-6 bg-gradient-to-r from-blue-600 to-purple-600 text-white font-semibold rounded-lg hover:from-blue-700 hover:to-purple-700 disabled:opacity-50 disabled:cursor-not-allowed transition-all shadow-md hover:shadow-lg"
            >
              {loading ? 'Loading...' : 'Fetch Stats'}
            </button>
          </form>

          {error && (
            <div className="mt-6 p-4 bg-red-50 dark:bg-red-900/20 border border-red-200 dark:border-red-800 rounded-lg">
              <p className="text-red-800 dark:text-red-200">{error}</p>
            </div>
          )}
        </div>

        {stats && (
          <>
            <StatsDisplay stats={stats} />
            <RecentAchievements stats={stats} />
          </>
        )}
      </div>
    </div>
  );
}
