namespace CoreBackend.Models;

public class UserProfile
{
    public int Id { get; set; }
    public required string Platform { get; set; }
    public required string UserId { get; set; }
    public DateTime LastUpdated { get; set; }
    public List<GameRecord> Games { get; set; } = new();
}

public class GameRecord
{
    public int Id { get; set; }
    public required string ExternalId { get; set; }
    public required string Title { get; set; }
    public int PlaytimeMinutes { get; set; }
    public string? IconUrl { get; set; }
    public DateTime? LastPlayed { get; set; }

    // Достижения
    public int? AchievementsTotal { get; set; }
    public int? AchievementsUnlocked { get; set; }
    public string? RecentAchievementsJson { get; set; } // JSON массив [{name, unlockTime}]

    public int UserProfileId { get; set; }
    public UserProfile? UserProfile { get; set; }
}
