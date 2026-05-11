import Image from 'next/image';
import { GameInfo } from '@/lib/api';

interface GameCardProps {
  game: GameInfo;
}

export default function GameCard({ game }: GameCardProps) {
  const hours = Math.floor(game.playtimeMinutes / 60);
  const minutes = game.playtimeMinutes % 60;
  const achievementProgress = game.achievements
    ? (game.achievements.unlocked / game.achievements.total) * 100
    : 0;

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-md hover:shadow-lg transition-shadow p-4">
      <div className="flex items-center gap-4">
        <div className="relative w-16 h-16 flex-shrink-0">
          {game.iconUrl ? (
            <Image
              src={game.iconUrl}
              alt={game.title}
              fill
              className="object-cover rounded"
              unoptimized
            />
          ) : (
            <div className="w-full h-full bg-zinc-200 dark:bg-zinc-800 rounded flex items-center justify-center">
              <span className="text-2xl">🎮</span>
            </div>
          )}
        </div>
        <div className="flex-1 min-w-0">
          <h3 className="font-semibold text-zinc-900 dark:text-zinc-100 truncate">
            {game.title}
          </h3>
          <p className="text-sm text-zinc-600 dark:text-zinc-400">
            {hours > 0 && `${hours}h `}
            {minutes}m played
          </p>
          {game.achievements && (
            <div className="mt-2">
              <div className="flex items-center gap-2 text-xs text-zinc-600 dark:text-zinc-400 mb-1">
                <span>🏆 {game.achievements.unlocked}/{game.achievements.total}</span>
                <span className="text-zinc-400">({Math.round(achievementProgress)}%)</span>
              </div>
              <div className="w-full bg-zinc-200 dark:bg-zinc-700 rounded-full h-2">
                <div
                  className="bg-gradient-to-r from-yellow-400 to-yellow-600 h-2 rounded-full transition-all"
                  style={{ width: `${achievementProgress}%` }}
                />
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}
