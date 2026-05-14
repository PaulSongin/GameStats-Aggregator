from fastapi import FastAPI, HTTPException
import httpx
from psnawp_api import PSNAWP
import logging
import os
import asyncio
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
            # 1. Получаем информацию о пользователе (имя профиля)
            user_url = "http://api.steampowered.com/ISteamUser/GetPlayerSummaries/v0002/"
            user_params = {
                "key": STEAM_API_KEY,
                "steamids": steam_id
            }
            user_res = await client.get(user_url, params=user_params, timeout=10.0)
            user_res.raise_for_status()
            user_data = user_res.json()

            # Извлекаем имя пользователя
            players = user_data.get("response", {}).get("players", [])
            username = players[0].get("personaname", steam_id) if players else steam_id

            # 2. Получаем owned games (игры в библиотеке)
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

            # 3. Получаем recently played games (включая семейные игры)
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

    # Функция для получения достижений игры
    async def get_game_achievements(client, app_id: str):
        try:
            # 1. Получаем схему достижений (для локализованных названий)
            schema_url = "http://api.steampowered.com/ISteamUserStats/GetSchemaForGame/v2/"
            schema_params = {
                "key": STEAM_API_KEY,
                "appid": app_id
            }
            schema_res = await client.get(schema_url, params=schema_params, timeout=5.0)

            # Создаём словарь apiname -> displayName
            achievement_names = {}
            if schema_res.status_code == 200:
                schema_data = schema_res.json()
                available_achievements = schema_data.get("game", {}).get("availableGameStats", {}).get("achievements", [])
                achievement_names = {
                    ach.get("name"): ach.get("displayName", ach.get("name"))
                    for ach in available_achievements
                }

            # 2. Получаем статистику достижений пользователя
            user_stats_url = "http://api.steampowered.com/ISteamUserStats/GetPlayerAchievements/v0001/"
            params = {
                "key": STEAM_API_KEY,
                "steamid": steam_id,
                "appid": app_id
            }
            res = await client.get(user_stats_url, params=params, timeout=5.0)

            if res.status_code != 200:
                return None

            data = res.json()
            achievements = data.get("playerstats", {}).get("achievements", [])

            if not achievements:
                return None

            total = len(achievements)
            unlocked = sum(1 for a in achievements if a.get("achieved") == 1)

            # Находим недавние достижения (unlocktime > 0, сортируем по времени)
            recent = sorted(
                [a for a in achievements if a.get("achieved") == 1 and a.get("unlocktime", 0) > 0],
                key=lambda x: x.get("unlocktime", 0),
                reverse=True
            )[:3]  # Берём 3 последних

            return {
                "total": total,
                "unlocked": unlocked,
                "recentAchievements": [
                    {
                        "name": achievement_names.get(a.get("apiname", ""), a.get("apiname", "Unknown Achievement")),
                        "unlockTime": a.get("unlocktime", 0)
                    } for a in recent
                ]
            }
        except Exception as e:
            logger.debug(f"Failed to get achievements for {app_id}: {e}")
            return None

    # Объединяем данные из обоих источников
    games_dict = {}
    recent_app_ids = set()

    # Сначала обрабатываем recently played games для определения порядка
    recent_games = recent_data.get("response", {}).get("games", [])

    # Собираем все игры с наигранным временем для загрузки достижений
    owned_games = owned_data.get("response", {}).get("games", [])
    all_played_games = list(recent_games)

    # Добавляем owned игры с временем, которых нет в recent
    recent_app_ids_temp = {str(g["appid"]) for g in recent_games}
    for g in owned_games:
        if g.get("playtime_forever", 0) > 0 and str(g["appid"]) not in recent_app_ids_temp:
            all_played_games.append(g)

    # Получаем достижения для всех игр с наигранным временем параллельно
    async with httpx.AsyncClient() as client:
        achievement_tasks = [get_game_achievements(client, str(g["appid"])) for g in all_played_games]
        achievement_results = await asyncio.gather(*achievement_tasks, return_exceptions=True)

    # Создаем словарь appid -> achievements для быстрого доступа
    achievements_map = {}
    for idx, game in enumerate(all_played_games):
        if idx < len(achievement_results) and not isinstance(achievement_results[idx], Exception):
            achievements_map[str(game["appid"])] = achievement_results[idx]

    for idx, g in enumerate(recent_games):
        app_id = str(g["appid"])
        recent_app_ids.add(app_id)
        icon_hash = g.get('img_icon_url', '')
        icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{g['appid']}/{icon_hash}.jpg" if icon_hash else None

        # Добавляем данные о достижениях из словаря
        achievements_data = achievements_map.get(app_id)

        game_data = {
            "externalId": app_id,
            "title": g["name"],
            "playtimeMinutes": g.get("playtime_forever", 0),
            "iconUrl": icon_url,
            "recentlyPlayed": True,
            "recentPlayOrder": idx  # Порядок в списке недавних (0 = самая свежая)
        }

        if achievements_data:
            game_data["achievements"] = achievements_data

        games_dict[app_id] = game_data

    # Добавляем owned games (которых нет в недавних)
    for g in owned_games:
        app_id = str(g["appid"])

        if app_id in games_dict:
            # Обновляем время, если owned показывает больше
            games_dict[app_id]["playtimeMinutes"] = max(
                games_dict[app_id]["playtimeMinutes"],
                g.get("playtime_forever", 0)
            )
        else:
            # Добавляем игру, в которую давно не играли
            icon_hash = g.get('img_icon_url', '')
            icon_url = f"http://media.steampowered.com/steamcommunity/public/images/apps/{g['appid']}/{icon_hash}.jpg" if icon_hash else None

            game_data = {
                "externalId": app_id,
                "title": g["name"],
                "playtimeMinutes": g.get("playtime_forever", 0),
                "iconUrl": icon_url,
                "recentlyPlayed": False,
                "recentPlayOrder": 9999  # Большое число для старых игр
            }

            # Добавляем достижения, если они есть
            achievements_data = achievements_map.get(app_id)
            if achievements_data:
                game_data["achievements"] = achievements_data

            games_dict[app_id] = game_data

    # Сортируем: сначала недавние (по recentPlayOrder), потом остальные (по времени игры)
    games = sorted(
        games_dict.values(),
        key=lambda x: (not x["recentlyPlayed"], x["recentPlayOrder"], -x["playtimeMinutes"])
    )

    # Убираем служебные поля перед отправкой
    for game in games:
        game.pop("recentlyPlayed", None)
        game.pop("recentPlayOrder", None)

    return {"platform": "steam", "userId": username, "games": games}

@app.get("/fetch/psn/{online_id}")
async def fetch_psn(online_id: str):
    try:
        psnawp = PSNAWP(PSN_NPSSO)
        user = psnawp.user(online_id=online_id)
        titles = user.title_stats()

        # Получаем все трофеи один раз
        try:
            trophy_titles = user.trophy_titles()
            # Сопоставляем по названию игры (title_name)
            trophy_dict = {tt.title_name.lower().strip(): tt for tt in trophy_titles}
        except Exception as trophy_error:
            logger.warning(f"Failed to get trophy titles for {online_id}: {trophy_error}")
            trophy_dict = {}

        games = []
        for t in titles:
            game_data = {
                "externalId": t.title_id,
                "title": t.name,
                "playtimeMinutes": int(t.play_duration.total_seconds() // 60) if t.play_duration else 0,
                "iconUrl": t.image_url
            }

            # Добавляем трофеи, если они есть (сопоставляем по названию)
            matching_trophy = trophy_dict.get(t.name.lower().strip())
            if matching_trophy:
                earned = matching_trophy.earned_trophies.bronze + matching_trophy.earned_trophies.silver + matching_trophy.earned_trophies.gold + matching_trophy.earned_trophies.platinum
                total = matching_trophy.defined_trophies.bronze + matching_trophy.defined_trophies.silver + matching_trophy.defined_trophies.gold + matching_trophy.defined_trophies.platinum

                if total > 0:
                    game_data["achievements"] = {
                        "total": total,
                        "unlocked": earned,
                        "recentAchievements": []  # PSN API не предоставляет временные метки для трофеев через psnawp
                    }

            games.append(game_data)

        return {"platform": "psn", "userId": online_id, "games": games}
    except Exception as e:
        logger.error(f"PSN Error for {online_id}: {e}")
        # Если игр нет, возвращаем пустой список вместо ошибки
        return {"platform": "psn", "userId": online_id, "games": []}

@app.get("/fetch/xbox/{gamertag}")
async def fetch_xbox(gamertag: str):
    headers = {"X-Authorization": XBOX_API_KEY}

    # Функция для retry с экспоненциальной задержкой
    async def fetch_with_retry(client, url, max_retries=3):
        for attempt in range(max_retries):
            try:
                timeout = httpx.Timeout(120.0 if attempt > 0 else 60.0, connect=15.0)
                res = await client.get(url, headers=headers, timeout=timeout)
                res.raise_for_status()
                return res
            except httpx.ReadTimeout:
                if attempt < max_retries - 1:
                    wait_time = 2 ** attempt  # 1s, 2s, 4s
                    logger.warning(f"Timeout on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise
            except httpx.HTTPStatusError as e:
                if e.response.status_code == 504 and attempt < max_retries - 1:
                    wait_time = 2 ** attempt
                    logger.warning(f"Gateway timeout on attempt {attempt + 1}/{max_retries}, retrying in {wait_time}s...")
                    await asyncio.sleep(wait_time)
                else:
                    raise

    async with httpx.AsyncClient() as client:
        try:
            # 1. Получаем XUID
            res = await client.get(f"https://xbl.io/api/v2/friends/search?gt={gamertag}", headers=headers, timeout=10.0)
            res.raise_for_status()
            user_data = res.json()

            # xbl.io API возвращает данные в структуре {"content": {...}}
            content = user_data.get('content', {})
            profiles = content.get('profileUsers', [])
            if not profiles:
                return {"platform": "xbox", "userId": gamertag, "games": [], "message": "User not found"}

            xuid = profiles[0]['id']

            # 2. Получаем игры с retry логикой
            logger.info(f"Fetching Xbox games for {gamertag} (XUID: {xuid})...")
            games_res = await fetch_with_retry(client, f"https://xbl.io/api/v2/achievements/player/{xuid}")
            games_data = games_res.json()

            # Извлекаем titles из content
            data = games_data.get('content', {})
            titles = data.get("titles", [])
            logger.info(f"Xbox API response for {gamertag}: found {len(titles)} titles")
        except httpx.ReadTimeout:
            logger.error(f"Xbox API timeout for {gamertag} after all retries")
            raise HTTPException(status_code=504, detail="Xbox API timeout - user has too many games, try again later")
        except httpx.HTTPStatusError as e:
            logger.error(f"Xbox API HTTP error for {gamertag}: {e.response.status_code}")
            raise HTTPException(status_code=502, detail=f"Xbox API returned error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Xbox Error for {gamertag}: {str(e)}", exc_info=True)
            raise HTTPException(status_code=502, detail=f"Xbox API error: {str(e)}")

    games = []
    for t in titles:
        try:
            # Извлекаем дату последней игры
            title_history = t.get("titleHistory", {})
            last_played = title_history.get("lastTimePlayed")

            game_data = {
                "externalId": str(t.get("titleId")),
                "title": t.get("name"),
                "playtimeMinutes": 0,
                "iconUrl": t.get("displayImage"),
                "lastPlayed": last_played  # Добавляем дату последней игры
            }

            # Добавляем информацию о достижениях, если есть
            achievement_info = t.get("achievement", {})
            current_achievements = achievement_info.get("currentAchievements", 0)
            total_achievements = achievement_info.get("totalAchievements", 0)
            total_gamerscore = achievement_info.get("totalGamerscore", 0)

            # Xbox API иногда возвращает totalAchievements=0, даже если достижения есть
            # В таком случае показываем только количество разблокированных
            if current_achievements > 0 or total_achievements > 0 or total_gamerscore > 0:
                game_data["achievements"] = {
                    "total": total_achievements if total_achievements > 0 else None,
                    "unlocked": current_achievements,
                    "recentAchievements": []  # Xbox API через xbl.io не предоставляет временные метки
                }

            games.append(game_data)
        except Exception as game_error:
            logger.warning(f"Failed to process game for {gamertag}: {game_error}")
            continue

    return {"platform": "xbox", "userId": gamertag, "games": games}