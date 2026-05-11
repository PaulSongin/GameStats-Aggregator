import { UnifiedStats } from '@/lib/api';
import GameCard from './GameCard';

interface StatsDisplayProps {
  stats: UnifiedStats;
}

export default function StatsDisplay({ stats }: StatsDisplayProps) {
  const totalPlaytime = stats.games.reduce((sum, game) => sum + game.playtimeMinutes, 0);
  const totalHours = Math.floor(totalPlaytime / 60);

  return (
    <div className="w-full max-w-4xl mx-auto space-y-6">
      <div className="bg-gradient-to-r from-blue-500 to-purple-600 rounded-lg p-6 text-white">
        <h2 className="text-2xl font-bold mb-2">
          {stats.platform.toUpperCase()} Profile
        </h2>
        <p className="text-lg opacity-90">{stats.userId}</p>
        <div className="mt-4 flex gap-6">
          <div>
            <p className="text-sm opacity-75">Total Games</p>
            <p className="text-3xl font-bold">{stats.games.length}</p>
          </div>
          <div>
            <p className="text-sm opacity-75">Total Playtime</p>
            <p className="text-3xl font-bold">{totalHours}h</p>
          </div>
        </div>
      </div>

      <div className="space-y-3">
        <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100">
          Games Library
        </h3>
        <p className="text-sm text-zinc-600 dark:text-zinc-400">
          Sorted by recent activity
        </p>
        {stats.games.length === 0 ? (
          <p className="text-zinc-600 dark:text-zinc-400 text-center py-8">
            No games found for this user.
          </p>
        ) : (
          <div className="grid gap-3">
            {stats.games.map((game) => (
              <GameCard key={game.externalId} game={game} />
            ))}
          </div>
        )}
      </div>
    </div>
  );
}
