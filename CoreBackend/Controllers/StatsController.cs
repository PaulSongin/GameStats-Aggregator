using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CoreBackend.Models;
using CoreBackend.Data;

namespace CoreBackend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StatsController : ControllerBase
{
    private readonly IHttpClientFactory _clientFactory;
    private readonly AppDbContext _db;

    public StatsController(IHttpClientFactory clientFactory, AppDbContext db)
    {
        _clientFactory = clientFactory;
        _db = db;
    }

    [HttpGet("{platform}/{id}")]
    public async Task<IActionResult> GetStats(string platform, string id, [FromQuery] bool refresh = false)
    {
        // Проверяем кэш в БД, если не требуется обновление
        if (!refresh)
        {
            var cached = await _db.UserProfiles
                .Include(u => u.Games)
                .FirstOrDefaultAsync(u => u.Platform == platform && u.UserId == id);

            if (cached != null && (DateTime.UtcNow - cached.LastUpdated).TotalMinutes < 30)
            {
                var cachedStats = new UnifiedStats(
                    cached.Platform,
                    cached.UserId,
                    cached.Games.Select(g => new GameInfo(g.ExternalId, g.Title, g.PlaytimeMinutes, g.IconUrl)).ToList()
                );
                return Ok(cachedStats);
            }
        }

        // Получаем свежие данные из Python Provider
        var client = _clientFactory.CreateClient();
        try
        {
            var url = $"http://python-provider:8000/fetch/{platform}/{id}";
            var response = await client.GetAsync(url);

            if (!response.IsSuccessStatusCode)
                return BadRequest($"Provider error: {response.StatusCode}");

            var stats = await response.Content.ReadFromJsonAsync<UnifiedStats>();
            if (stats == null)
                return StatusCode(500, "Failed to parse provider response");

            // Сохраняем в БД
            await SaveToDatabase(stats);

            return Ok(stats);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"Internal Gateway Error: {ex.Message}");
        }
    }

    private async Task SaveToDatabase(UnifiedStats stats)
    {
        var profile = await _db.UserProfiles
            .Include(u => u.Games)
            .FirstOrDefaultAsync(u => u.Platform == stats.Platform && u.UserId == stats.UserId);

        if (profile == null)
        {
            profile = new UserProfile
            {
                Platform = stats.Platform,
                UserId = stats.UserId,
                LastUpdated = DateTime.UtcNow
            };
            _db.UserProfiles.Add(profile);
        }
        else
        {
            profile.LastUpdated = DateTime.UtcNow;
            _db.GameRecords.RemoveRange(profile.Games);
        }

        profile.Games = stats.Games.Select(g => new GameRecord
        {
            ExternalId = g.ExternalId,
            Title = g.Title,
            PlaytimeMinutes = g.PlaytimeMinutes,
            IconUrl = g.IconUrl
        }).ToList();

        await _db.SaveChangesAsync();
    }
}