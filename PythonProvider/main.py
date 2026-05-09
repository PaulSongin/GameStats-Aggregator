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

@app.get("/fetch/steam/{user_id}")
async def fetch_steam(user_id: str):
    # ИСПРАВЛЕНО: правильный URL (steampowered)
    url = "http://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
    params = {
        "key": STEAM_API_KEY,
        "steamid": user_id,
        "include_appinfo": True,
        "format": "json"
    }
    async with httpx.AsyncClient() as client:
        try:
            res = await client.get(url, params=params, timeout=10.0)
            res.raise_for_status()
            data = res.json()
        except Exception as e:
            logger.error(f"Steam Error: {e}")
            raise HTTPException(status_code=502, detail=f"Steam API unreachable: {e}")
    
    games_data = data.get("response", {}).get("games", [])
    games = []
    for g in games_data:
        # Формируем иконку (иногда img_icon_url может отсутствовать)
        icon_hash = g.get('img_icon_url', '')
        icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{g['appid']}/{icon_hash}.jpg" if icon_hash else None
        
        games.append({
            "externalId": str(g["appid"]),
            "title": g["name"],
            "playtimeMinutes": g.get("playtime_forever", 0),
            "iconUrl": icon_url
        })
    return {"platform": "steam", "userId": user_id, "games": games}

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