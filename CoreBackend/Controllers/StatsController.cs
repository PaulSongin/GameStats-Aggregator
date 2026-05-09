using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CoreBackend.Models;
using CoreBackend.Data;
using StackExchange.Redis;
using System.Text.Json;

namespace CoreBackend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StatsController : ControllerBase
{
    private readonly IHttpClientFactory _clientFactory;
    private readonly AppDbContext _db;
    private readonly IDatabase _redis;
    private static int _redisHits = 0;
    private static int _postgresHits = 0;
    private static int _apiCalls = 0;

    public StatsController(IHttpClientFactory clientFactory, AppDbContext db, IConnectionMultiplexer redis)
    {
        _clientFactory = clientFactory;
        _db = db;
        _redis = redis.GetDatabase();
    }

    [HttpGet("{platform}/{id}")]
    public async Task<IActionResult> GetStats(string platform, string id, [FromQuery] bool refresh = false)
    {
        var cacheKey = $"stats:{platform}:{id}";

        // 1. Проверяем Redis (горячий кэш)
        if (!refresh)
        {
            var redisValue = await _redis.StringGetAsync(cacheKey);
            if (redisValue.HasValue)
            {
                Interlocked.Increment(ref _redisHits);
                var stats = JsonSerializer.Deserialize<UnifiedStats>(redisValue.ToString());
                return Ok(stats);
            }

            // 2. Проверяем PostgreSQL (холодный кэш)
            var cached = await _db.UserProfiles
                .Include(u => u.Games)
                .FirstOrDefaultAsync(u => u.Platform == platform && u.UserId == id);

            if (cached != null && (DateTime.UtcNow - cached.LastUpdated).TotalMinutes < 30)
            {
                Interlocked.Increment(ref _postgresHits);
                var cachedStats = new UnifiedStats(
                    cached.Platform,
                    cached.UserId,
                    cached.Games.Select(g => new GameInfo(g.ExternalId, g.Title, g.PlaytimeMinutes, g.IconUrl)).ToList()
                );

                // Сохраняем в Redis для следующих запросов (TTL: 5 минут)
                await _redis.StringSetAsync(cacheKey, JsonSerializer.Serialize(cachedStats), TimeSpan.FromMinutes(5));

                return Ok(cachedStats);
            }
        }

        // 3. Получаем свежие данные из Python Provider
        Interlocked.Increment(ref _apiCalls);
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

            // Сохраняем в PostgreSQL
            await SaveToDatabase(stats);

            // Сохраняем в Redis (TTL: 5 минут)
            await _redis.StringSetAsync(cacheKey, JsonSerializer.Serialize(stats), TimeSpan.FromMinutes(5));

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

    [HttpGet("metrics")]
    public IActionResult GetCacheMetrics()
    {
        var total = _redisHits + _postgresHits + _apiCalls;
        return Ok(new
        {
            redisHits = _redisHits,
            postgresHits = _postgresHits,
            apiCalls = _apiCalls,
            totalRequests = total,
            redisHitRate = total > 0 ? Math.Round((_redisHits / (double)total) * 100, 2) : 0,
            postgresHitRate = total > 0 ? Math.Round((_postgresHits / (double)total) * 100, 2) : 0,
            apiCallRate = total > 0 ? Math.Round((_apiCalls / (double)total) * 100, 2) : 0
        });
    }
}