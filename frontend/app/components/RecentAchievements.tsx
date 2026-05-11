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
    .slice(0, 10); // Показываем топ-10 последних

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
    if (diffDays < 7) return `${diffDays} days ago`;
    return date.toLocaleDateString();
  };

  return (
    <div className="w-full max-w-4xl mx-auto mt-6">
      <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-lg p-6">
        <h3 className="text-xl font-semibold text-zinc-900 dark:text-zinc-100 mb-4 flex items-center gap-2">
          <span>🏆</span>
          Recent Achievements
        </h3>
        <div className="space-y-3">
          {allRecentAchievements.map((ach, idx) => (
            <div
              key={`${ach.gameName}-${ach.unlockTime}-${idx}`}
              className="flex items-center justify-between p-3 bg-zinc-50 dark:bg-zinc-800 rounded-lg"
            >
              <div className="flex-1 min-w-0">
                <p className="font-medium text-zinc-900 dark:text-zinc-100 truncate">
                  {ach.gameName}
                </p>
                <p className="text-sm text-zinc-600 dark:text-zinc-400 truncate">
                  {ach.achievementName}
                </p>
              </div>
              <span className="text-xs text-zinc-500 dark:text-zinc-400 ml-4 whitespace-nowrap">
                {formatDate(ach.unlockTime)}
              </span>
            </div>
          ))}
        </div>
      </div>
    </div>
  );
}
