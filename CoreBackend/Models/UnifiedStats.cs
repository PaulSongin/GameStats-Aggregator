namespace CoreBackend.Models;

public record AchievementInfo(
    int? Total,
    int Unlocked,
    List<RecentAchievement> RecentAchievements
);

public record RecentAchievement(
    string Name,
    long UnlockTime
);

public record GameInfo(
    string ExternalId,
    string Title,
    int PlaytimeMinutes,
    string? IconUrl,
    AchievementInfo? Achievements,
    DateTime? LastPlayed
);

public record UnifiedStats(
    string Platform,
    string UserId,
    List<GameInfo> Games
);