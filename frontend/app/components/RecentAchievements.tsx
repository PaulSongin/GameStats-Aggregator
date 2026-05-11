import { UnifiedStats } from '@/lib/api';

interface RecentAchievementsProps {
  stats: UnifiedStats;
}

export default function RecentAchievements({ stats }: RecentAchievementsProps) {
  // Собираем все недавние достижения из всех игр
  const allRecentAchievements = stats.games
    .filter(game => game.achievements?.recentAchievements.length)
    .flatMap(game =>
      game.achievements!.recentAchievements.map(ach => ({
        gameName: game.title,
        achievementName: ach.name,
        unlockTime: ach.unlockTime,
      }))
    )
    .sort((a, b) => b.unlockTime - a.unlockTime)
    .slice(0, 15); // Показываем топ-15 последних

  if (allRecentAchievements.length === 0) {
    return null;
  }

  const formatDate = (timestamp: number) => {
    const date = new Date(timestamp * 1000);
    const now = new Date();
    const diffMs = now.getTime() - date.getTime();
    const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));

    if (diffDays === 0) return 'Today';
    if (diffDays === 1) return 'Yesterday';
    if (diffDays < 7) return `${diffDays}d ago`;
    if (diffDays < 30) return `${Math.floor(diffDays / 7)}w ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-4 sticky top-4">
      <h3 className="text-lg font-semibold text-zinc-900 dark:text-zinc-100 mb-3 flex items-center gap-2">
        <span>🏆</span>
        Recent Achievements
      </h3>
      <div className="space-y-2 max-h-[600px] overflow-y-auto">
        {allRecentAchievements.map((ach, idx) => (
          <div
            key={`${ach.gameName}-${ach.unlockTime}-${idx}`}
            className="p-2 bg-zinc-50 dark:bg-zinc-800 rounded"
          >
            <p className="text-xs font-medium text-zinc-900 dark:text-zinc-100 truncate">
              {ach.achievementName}
            </p>
            <p className="text-xs text-zinc-500 dark:text-zinc-400 truncate">
              {ach.gameName}
            </p>
            <p className="text-xs text-zinc-400 dark:text-zinc-500 mt-1">
              {formatDate(ach.unlockTime)}
            </p>
          </div>
        ))}
      </div>
    </div>
  );
}
