from fastapi import FastAPI, HTTPException
import httpx
from psnawp_api import PSNAWP
import logging
import os
from dotenv import load_dotenv

# Загружаем переменные окружения из .env файла
load_dotenv()

app = FastAPI()

# Настраиваем логи, чтобы видеть ошибки в терминале Docker
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# === CONFIGURATION ===
STEAM_API_KEY = os.getenv("STEAM_API_KEY", "")
PSN_NPSSO = os.getenv("PSN_NPSSO", "")
XBOX_API_KEY = os.getenv("XBOX_API_KEY", "")

@app.get("/")
async def root():
    return {"message": "Data Provider is running"}

@app.get("/resolve/steam/{vanity_name}")
async def resolve_steam_vanity(vanity_name: str):
    """Конвертирует Steam никнейм (vanity URL) в Steam ID64"""
    url = "http://api.steampowered.com/ISteamUser/ResolveVanityURL/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "vanityurl": vanity_name
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, params=params, timeout=10.0)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            logger.error(f"Steam Resolve Error: {e}")
            raise HTTPException(status_code=502, detail=f"Steam API unreachable: {e}")

    response = data.get("response", {})
    if response.get("success") == 1:
        return {"steamId": response.get("steamid")}
    else:
        raise HTTPException(status_code=404, detail="Steam user not found")

@app.get("/fetch/steam/{user_id}")
async def fetch_steam(user_id: str):
    # Если user_id не является числом (Steam ID64), пытаемся резолвить как vanity URL
    steam_id = user_id
    if not user_id.isdigit():
        try:
            resolve_result = await resolve_steam_vanity(user_id)
            steam_id = resolve_result["steamId"]
        except HTTPException:
            raise HTTPException(status_code=404, detail=f"Steam user '{user_id}' not found")

    async with httpx.AsyncClient() as client:
        try:
            # 1. Получаем owned games (игры в библиотеке)
            owned_url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
            owned_params = {
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "include_appinfo": True,
                "format": "json"
            }
            owned_res = await client.get(owned_url, params=owned_params, timeout=10.0)
            owned_res.raise_for_status()
            owned_data = owned_res.json()

            # 2. Получаем recently played games (включая семейные игры)
            recent_url = "http://api.steampowered.com/IPlayerService/GetRecentlyPlayedGames/v0001/"
            recent_params = {
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "format": "json"
            }
            recent_res = await client.get(recent_url, params=recent_params, timeout=10.0)
            recent_res.raise_for_status()
            recent_data = recent_res.json()

        except Exception as e:
            logger.error(f"Steam Error: {e}")
            raise HTTPException(status_code=502, detail=f"Steam API unreachable: {e}")

    # Объединяем данные из обоих источников
    games_dict = {}

    # Добавляем owned games
    owned_games = owned_data.get("response", {}).get("games", [])
    for g in owned_games:
        icon_hash = g.get('img_icon_url', '')
        icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{g['appid']}/{icon_hash}.jpg" if icon_hash else None

        games_dict[str(g["appid"])] = {
            "externalId": str(g["appid"]),
            "title": g["name"],
            "playtimeMinutes": g.get("playtime_forever", 0),
            "iconUrl": icon_url
        }

    # Добавляем/обновляем recently played games (могут включать семейные игры)
    recent_games = recent_data.get("response", {}).get("games", [])
    for g in recent_games:
        app_id = str(g["appid"])
        icon_hash = g.get('img_icon_url', '')
        icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{g['appid']}/{icon_hash}.jpg" if icon_hash else None

        # Если игра уже есть, обновляем время (используем максимальное)
        if app_id in games_dict:
            games_dict[app_id]["playtimeMinutes"] = max(
                games_dict[app_id]["playtimeMinutes"],
                g.get("playtime_forever", 0)
            )
        else:
            # Добавляем новую игру (например, из семейного доступа)
            games_dict[app_id] = {
                "externalId": app_id,
                "title": g["name"],
                "playtimeMinutes": g.get("playtime_forever", 0),
                "iconUrl": icon_url
            }

    games = list(games_dict.values())
    return {"platform": "steam", "userId": steam_id, "games": games}

@app.get("/fetch/psn/{online_id}")
async def fetch_psn(online_id: str):
    try:
        psnawp = PSNAWP(PSN_NPSSO)
        user = psnawp.user(online_id=online_id)
        titles = user.title_stats()
        
        games = []
        for t in titles:
            games.append({
                "externalId": t.title_id,
                "title": t.name,
                "playtimeMinutes": int(t.play_duration.total_seconds() // 60) if t.play_duration else 0,
                "iconUrl": t.image_url
            })
        return {"platform": "psn", "userId": online_id, "games": games}
    except Exception as e:
        logger.error(f"PSN Error for {online_id}: {e}")
        # Если игр нет, возвращаем пустой список вместо ошибки
        return {"platform": "psn", "userId": online_id, "games": []}

@app.get("/fetch/xbox/{gamertag}")
async def fetch_xbox(gamertag: str):
    headers = {"X-Authorization": XBOX_API_KEY}
    async with httpx.AsyncClient() as client:
        try:
            # 1. Получаем XUID
            res = await client.get(f"https://xbl.io/api/v2/friends/search?gt={gamertag}", headers=headers, timeout=10.0)
            res.raise_for_status()
            user_data = res.json()
            
            profiles = user_data.get('profileUsers', [])
            if not profiles:
                return {"platform": "xbox", "userId": gamertag, "games": [], "message": "User not found"}
            
            xuid = profiles[0]['id']
            
            # 2. Получаем игры
            games_res = await client.get(f"https://xbl.io/api/v2/achievements/player/{xuid}", headers=headers, timeout=10.0)
            games_res.raise_for_status()
            data = games_res.json()
        except Exception as e:
            logger.error(f"Xbox Error for {gamertag}: {e}")
            raise HTTPException(status_code=502, detail=f"Xbox API error: {e}")
        
    titles = data.get("titles", [])
    games = []
    for t in titles:
        games.append({
            "externalId": str(t.get("titleId")),
            "title": t.get("name"),
            "playtimeMinutes": 0,
            "iconUrl": t.get("displayImage")
        })
    return {"platform": "xbox", "userId": gamertag, "games": games}