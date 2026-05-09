using System.Text.RegularExpressions;

namespace CoreBackend.Validators;

public static class PlatformValidator
{
    public static (bool IsValid, string? ErrorMessage) ValidateSteamId(string steamId)
    {
        if (string.IsNullOrWhiteSpace(steamId))
            return (false, "Steam ID cannot be empty");

        if (!Regex.IsMatch(steamId, @"^\d{17}$"))
            return (false, "Steam ID must be exactly 17 digits");

        return (true, null);
    }

    public static (bool IsValid, string? ErrorMessage) ValidatePsnId(string psnId)
    {
        if (string.IsNullOrWhiteSpace(psnId))
            return (false, "PSN ID cannot be empty");

        if (psnId.Length < 3 || psnId.Length > 16)
            return (false, "PSN ID must be between 3 and 16 characters");

        if (!Regex.IsMatch(psnId, @"^[a-zA-Z0-9_-]+$"))
            return (false, "PSN ID can only contain letters, numbers, hyphens, and underscores");

        return (true, null);
    }

    public static (bool IsValid, string? ErrorMessage) ValidateXboxGamertag(string gamertag)
    {
        if (string.IsNullOrWhiteSpace(gamertag))
            return (false, "Xbox Gamertag cannot be empty");

        if (gamertag.Length < 1 || gamertag.Length > 15)
            return (false, "Xbox Gamertag must be between 1 and 15 characters");

        if (!Regex.IsMatch(gamertag, @"^[a-zA-Z0-9 ]+$"))
            return (false, "Xbox Gamertag can only contain letters, numbers, and spaces");

        return (true, null);
    }
}
