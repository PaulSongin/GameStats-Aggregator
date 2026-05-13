using Microsoft.AspNetCore.Mvc;
using Microsoft.EntityFrameworkCore;
using CoreBackend.Models;
using CoreBackend.Data;
using CoreBackend.Validators;
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
    private readonly ILogger<StatsController> _logger;
    private static int _redisHits = 0;
    private static int _postgresHits = 0;
    private static int _apiCalls = 0;

    public StatsController(IHttpClientFactory clientFactory, AppDbContext db, IConnectionMultiplexer redis, ILogger<StatsController> logger)
    {
        _clientFactory = clientFactory;
        _db = db;
        _redis = redis.GetDatabase();
        _logger = logger;
    }

    [HttpGet("{platform}/{id}")]
    [ProducesResponseType(typeof(UnifiedStats), 200)]
    [ProducesResponseType(typeof(ErrorResponse), 400)]
    [ProducesResponseType(typeof(ErrorResponse), 500)]
    public async Task<IActionResult> GetStats(string platform, string id, [FromQuery] bool refresh = false)
    {
        // Валидация платформы
        platform = platform.ToLower();
        if (platform != "steam" && platform != "psn" && platform != "xbox")
        {
            return BadRequest(new ErrorResponse(
                "InvalidPlatform",
                $"Platform '{platform}' is not supported. Valid platforms: steam, psn, xbox",
                400
            ));
        }

        // Валидация ID в зависимости от платформы
        var (isValid, errorMessage) = platform switch
        {
            "steam" => PlatformValidator.ValidateSteamId(id),
            "psn" => PlatformValidator.ValidatePsnId(id),
            "xbox" => PlatformValidator.ValidateXboxGamertag(id),
            _ => (false, "Unknown platform")
        };

        if (!isValid)
        {
            return BadRequest(new ErrorResponse(
                "InvalidUserId",
                errorMessage!,
                400
            ));
        }

        var cacheKey = $"stats:{platform}:{id}";

        try
        {
            // 1. Проверяем Redis (горячий кэш)
            if (!refresh)
            {
                var redisValue = await _redis.StringGetAsync(cacheKey);
                if (redisValue.HasValue)
                {
                    Interlocked.Increment(ref _redisHits);
                    _logger.LogInformation("Cache hit: Redis for {Platform}:{Id}", platform, id);
                    var redisStats = JsonSerializer.Deserialize<UnifiedStats>(redisValue.ToString());
                    return Ok(redisStats);
                }

                // 2. Проверяем PostgreSQL (холодный кэш)
                var cached = await _db.UserProfiles
                    .Include(u => u.Games)
                    .FirstOrDefaultAsync(u => u.Platform == platform && u.UserId == id);

                if (cached != null && (DateTime.UtcNow - cached.LastUpdated).TotalMinutes < 30)
                {
                    Interlocked.Increment(ref _postgresHits);
                    _logger.LogInformation("Cache hit: PostgreSQL for {Platform}:{Id}", platform, id);
                    var cachedStats = new UnifiedStats(
                        cached.Platform,
                        cached.UserId,
                        cached.Games.Select(g => new GameInfo(g.ExternalId, g.Title, g.PlaytimeMinutes, g.IconUrl, null, g.LastPlayed)).ToList()
                    );

                    // Сохраняем в Redis для следующих запросов (TTL: 5 минут)
                    await _redis.StringSetAsync(cacheKey, JsonSerializer.Serialize(cachedStats), TimeSpan.FromMinutes(5));

                    return Ok(cachedStats);
                }
            }

            // 3. Получаем свежие данные из Python Provider
            Interlocked.Increment(ref _apiCalls);
            _logger.LogInformation("Fetching from API: {Platform}:{Id}", platform, id);
            var client = _clientFactory.CreateClient();

            var url = $"http://python-provider:8000/fetch/{platform}/{id}";
            var response = await client.GetAsync(url);

            if (!response.IsSuccessStatusCode)
            {
                _logger.LogError("Provider error: {StatusCode} for {Platform}:{Id}", response.StatusCode, platform, id);
                return StatusCode((int)response.StatusCode, new ErrorResponse(
                    "ProviderError",
                    $"Failed to fetch data from {platform} provider",
                    (int)response.StatusCode
                ));
            }

            var stats = await response.Content.ReadFromJsonAsync<UnifiedStats>();
            if (stats == null)
            {
                _logger.LogError("Failed to parse provider response for {Platform}:{Id}", platform, id);
                return StatusCode(500, new ErrorResponse(
                    "ParseError",
                    "Failed to parse provider response",
                    500
                ));
            }

            // Сохраняем в PostgreSQL
            await SaveToDatabase(stats);

            // Сохраняем в Redis (TTL: 5 минут)
            await _redis.StringSetAsync(cacheKey, JsonSerializer.Serialize(stats), TimeSpan.FromMinutes(5));

            return Ok(stats);
        }
        catch (HttpRequestException ex)
        {
            _logger.LogError(ex, "Network error while fetching {Platform}:{Id}", platform, id);
            return StatusCode(503, new ErrorResponse(
                "ServiceUnavailable",
                "Unable to reach the data provider. Please try again later.",
                503
            ));
        }
        catch (Exception ex)
        {
            _logger.LogError(ex, "Unexpected error for {Platform}:{Id}", platform, id);
            return StatusCode(500, new ErrorResponse(
                "InternalError",
                "An unexpected error occurred. Please try again later.",
                500
            ));
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
            IconUrl = g.IconUrl,
            LastPlayed = g.LastPlayed
        }).ToList();

        await _db.SaveChangesAsync();
    }

    [HttpGet("metrics")]
    [ProducesResponseType(200)]
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