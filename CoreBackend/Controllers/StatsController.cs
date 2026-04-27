using Microsoft.AspNetCore.Mvc;
using CoreBackend.Models; // Чтобы контроллер видел твои модели

namespace CoreBackend.Controllers;

[ApiController]
[Route("api/[controller]")]
public class StatsController : ControllerBase
{
    private readonly IHttpClientFactory _clientFactory;

    public StatsController(IHttpClientFactory clientFactory)
    {
        _clientFactory = clientFactory;
    }

    [HttpGet("{platform}/{id}")]
    public async Task<IActionResult> GetStats(string platform, string id)
    {
        var client = _clientFactory.CreateClient();
        try 
        {
            // Обрати внимание: имя хоста "python-provider" должно быть таким же в docker-compose
            var response = await client.GetAsync($"http://python-provider:8000/fetch/{platform}/{id}");

            if (!response.IsSuccessStatusCode)
                return BadRequest("Could not fetch stats from provider");

            var stats = await response.Content.ReadFromJsonAsync<UnifiedStats>();
            return Ok(stats);
        }
        catch (Exception ex)
        {
            return StatusCode(500, ex.Message);
        }
    }
}