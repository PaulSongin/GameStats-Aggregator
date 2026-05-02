using Microsoft.AspNetCore.Mvc;
using CoreBackend.Models;

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
            // Обращаемся к внутреннему имени сервиса в Docker
            var url = $"http://python-provider:8000/fetch/{platform}/{id}";
            var response = await client.GetAsync(url);

            if (!response.IsSuccessStatusCode)
                return BadRequest($"Provider error: {response.StatusCode}");

            var stats = await response.Content.ReadFromJsonAsync<UnifiedStats>();
            return Ok(stats);
        }
        catch (Exception ex)
        {
            return StatusCode(500, $"Internal Gateway Error: {ex.Message}");
        }
    }
}