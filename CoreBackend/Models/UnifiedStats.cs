namespace CoreBackend.Models;

public record GameInfo(
    string ExternalId, 
    string Title, 
    int PlaytimeMinutes, 
    string? IconUrl
);

public record UnifiedStats(
    string Platform, 
    string UserId, 
    List<GameInfo> Games
);