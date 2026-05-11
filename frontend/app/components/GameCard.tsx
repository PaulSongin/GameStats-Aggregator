import Image from 'next/image';
import { GameInfo } from '@/lib/api';

interface GameCardProps {
  game: GameInfo;
}

export default function GameCard({ game }: GameCardProps) {
  const hours = Math.floor(game.playtimeMinutes / 60);
  const minutes = game.playtimeMinutes % 60;

  return (
    <div className="bg-white dark:bg-zinc-900 rounded-lg shadow-md hover:shadow-lg transition-shadow p-4 flex items-center gap-4">
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
      </div>
    </div>
  );
}
