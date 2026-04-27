from fastapi import FastAPI, HTTPException
import httpx

app = FastAPI()

STEAM_API_KEY = "ffff"

@app.get("/fetch/steam/{steam_id}")
async def fetch_steam(steam_id: str):
    url = f"http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": steam_id,
        "include_appinfo": True,
        "format": "json"
    }
    
    async with httpx.AsyncClient() as client:
        response = await client.get(url, params=params)
        
    if response.status_code != 200:
        raise HTTPException(status_code=400, detail="Error fetching from Steam")
    
    data = response.json()
    
    # Приводим к нашему единому формату
    games = []
    for game in data.get("response", {}).get("games", []):
        games.append({
            "externalId": str(game["appid"]),
            "title": game["name"],
            "playtimeMinutes": game["playtime_forever"],
            "iconUrl": f"http://media.steampowered.com/steamcommunity/public/images/apps/{game['appid']}/{game['img_icon_url']}.jpg"
        })
        
    return {
        "platform": "steam",
        "userId": steam_id,
        "games": games
    }