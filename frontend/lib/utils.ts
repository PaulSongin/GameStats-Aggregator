/**
 * Извлекает Steam ID или custom URL из различных форматов ввода
 * Поддерживает:
 * - Полный URL: https://steamcommunity.com/id/gaben
 * - Полный URL: https://steamcommunity.com/profiles/76561197960287930
 * - Custom URL: gaben
 * - Steam ID64: 76561197960287930
 */
export function extractSteamId(input: string): string {
  const trimmed = input.trim();

  // Проверяем, является ли это URL
  if (trimmed.includes('steamcommunity.com')) {
    // Извлекаем из URL вида steamcommunity.com/id/USERNAME
    const customUrlMatch = trimmed.match(/steamcommunity\.com\/id\/([^\/\?]+)/);
    if (customUrlMatch) {
      return customUrlMatch[1];
    }

    // Извлекаем из URL вида steamcommunity.com/profiles/STEAMID64
    const profileMatch = trimmed.match(/steamcommunity\.com\/profiles\/(\d{17})/);
    if (profileMatch) {
      return profileMatch[1];
    }
  }

  // Возвращаем как есть (либо custom URL, либо Steam ID64)
  return trimmed;
}
