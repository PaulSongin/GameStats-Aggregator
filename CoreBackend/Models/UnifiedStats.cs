namespace CoreBackend.Models; // Убедись, что namespace совпадает с названием проекта

public record GameInfo(
    string ExternalId, 
    string Title, 
    int PlaytimeMinutes, 
    string IconUrl
);

public record UnifiedStats(
    string Platform, 
    string UserId, 
    List<GameInfo> Games
);