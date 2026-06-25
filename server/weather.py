#!/usr/bin/env python3
"""
KeepWell AI — Weather-Aware Nudges
Uses Open-Meteo API (free, no API key required).
Adapts physical and environmental nudges based on current conditions.
"""

import json
import urllib.request
import urllib.error
from datetime import datetime


# WMO Weather Codes mapping
WMO_CODES = {
    0: "clear_sky",
    1: "mainly_clear", 2: "partly_cloudy", 3: "overcast",
    45: "fog", 48: "fog",
    51: "light_drizzle", 53: "moderate_drizzle", 55: "dense_drizzle",
    61: "light_rain", 63: "moderate_rain", 65: "heavy_rain",
    71: "light_snow", 73: "moderate_snow", 75: "heavy_snow",
    80: "light_showers", 81: "moderate_showers", 82: "heavy_showers",
    95: "thunderstorm", 96: "thunderstorm_hail", 99: "thunderstorm_hail",
}


def get_weather(latitude=25.03, longitude=121.57):
    """
    Get current weather from Open-Meteo API.
    Default coordinates: Taipei, Taiwan.
    No API key needed.
    """
    url = (
        f"https://api.open-meteo.com/v1/forecast?"
        f"latitude={latitude}&longitude={longitude}"
        f"&current=temperature_2m,relative_humidity_2m,weather_code,wind_speed_10m,uv_index"
        f"&daily=uv_index_max,temperature_2m_max,temperature_2m_min"
        f"&timezone=auto&forecast_days=1"
    )
    try:
        req = urllib.request.Request(url)
        with urllib.request.urlopen(req, timeout=5) as resp:
            data = json.loads(resp.read().decode("utf-8"))
        current = data.get("current", {})
        return {
            "success": True,
            "temperature": current.get("temperature_2m"),
            "humidity": current.get("relative_humidity_2m"),
            "weather_code": current.get("weather_code", 0),
            "weather_desc": WMO_CODES.get(current.get("weather_code", 0), "unknown"),
            "wind_speed": current.get("wind_speed_10m"),
            "uv_index": current.get("uv_index"),
        }
    except (urllib.error.URLError, TimeoutError, Exception) as e:
        return {"success": False, "error": str(e)}


def is_outdoor_friendly(weather):
    """Determine if conditions are good for outdoor activity."""
    if not weather.get("success"):
        return None  # Unknown

    code = weather.get("weather_code", 0)
    temp = weather.get("temperature", 20)
    wind = weather.get("wind_speed", 0)

    # Not outdoor friendly
    if code >= 51:  # Drizzle or worse
        return False
    if temp < 5 or temp > 38:  # Too cold or too hot
        return False
    if wind > 40:  # Strong wind
        return False

    return True


def get_weather_nudge(weather, lang="en"):
    """
    Generate a weather-aware wellness nudge.
    Returns a contextual physical/environmental tip based on conditions.
    """
    if not weather.get("success"):
        return None

    outdoor_ok = is_outdoor_friendly(weather)
    temp = weather.get("temperature", 20)
    uv = weather.get("uv_index", 0)
    desc = weather.get("weather_desc", "unknown")

    if lang == "zh-TW" or lang == "zh":
        return _get_zh_nudge(outdoor_ok, temp, uv, desc)
    else:
        return _get_en_nudge(outdoor_ok, temp, uv, desc)


def _get_en_nudge(outdoor_ok, temp, uv, desc):
    """English weather nudge."""
    if outdoor_ok:
        if temp >= 25 and temp <= 32:
            nudge = {
                "action": f"It's {temp}°C and {desc.replace('_', ' ')} outside. Perfect for a 5-min walk. Step out and let your eyes focus on something far away.",
                "science": "Outdoor walking combines Attention Restoration Theory (nature gazing) with physical movement, doubling the recovery benefit (Kaplan, 1995).",
                "context": "outdoor_warm",
            }
        elif temp >= 15 and temp < 25:
            nudge = {
                "action": f"It's a pleasant {temp}°C outside. Take your next break outdoors. Even 2 minutes of fresh air resets your attention.",
                "science": "Brief outdoor exposure reduces cortisol by 12-16% and restores directed attention capacity (Hunter et al., 2019).",
                "context": "outdoor_mild",
            }
        else:
            nudge = {
                "action": f"It's {temp}°C outside. Bundle up and step out for 60 seconds. Cold air activates alertness via the sympathetic nervous system.",
                "science": "Brief cold exposure increases norepinephrine by 200-300%, improving focus and mood (Shevchuk, 2008).",
                "context": "outdoor_cold",
            }
    else:
        if "rain" in desc or "drizzle" in desc or "shower" in desc:
            nudge = {
                "action": f"It's raining outside ({temp}°C). Stand by a window and watch the rain for 30 seconds. The sound and visual pattern is naturally calming.",
                "science": "Rain sounds activate parasympathetic nervous system similarly to nature walks (Alvarsson et al., 2010).",
                "context": "indoor_rain",
            }
        else:
            nudge = {
                "action": f"Conditions aren't great outside ({temp}°C, {desc.replace('_', ' ')}). Do an indoor stretch: reach arms overhead, hold 10 seconds, then fold forward.",
                "science": "Indoor stretching during breaks reduces musculoskeletal pain by 32% in desk workers (Shariat et al., 2018).",
                "context": "indoor_general",
            }

    # UV warning
    if uv and uv >= 6 and outdoor_ok:
        nudge["uv_warning"] = f"UV index is {uv} (high). Apply sunscreen or wear a hat if staying out."

    nudge["icon"] = "🌿"
    nudge["dimension"] = "environmental"
    nudge["weather"] = {"temp": temp, "desc": desc, "outdoor_friendly": outdoor_ok}
    return nudge


def _get_zh_nudge(outdoor_ok, temp, uv, desc):
    """Traditional Chinese weather nudge."""
    desc_zh = {
        "clear_sky": "晴朗", "mainly_clear": "大致晴朗",
        "partly_cloudy": "局部多雲", "overcast": "陰天",
        "fog": "起霧", "light_drizzle": "小雨", "moderate_drizzle": "中雨",
        "light_rain": "小雨", "moderate_rain": "中雨", "heavy_rain": "大雨",
        "light_showers": "陣雨", "moderate_showers": "中雷陣雨",
        "thunderstorm": "雷暴", "light_snow": "小雪",
    }.get(desc, desc.replace("_", " "))

    if outdoor_ok:
        if temp >= 25 and temp <= 32:
            nudge = {
                "action": f"現在室外 {temp}°C，{desc_zh}。適合出去走 5 分鐘，讓眼睛看看遠方。",
                "science": "戶外步行結合了注意力恢復理論（自然注視）和身體活動，恢復效果加倍（Kaplan, 1995）。",
                "context": "outdoor_warm",
            }
        elif temp >= 15 and temp < 25:
            nudge = {
                "action": f"室外 {temp}°C，{desc_zh}，很舒適。下次休息去外面走走，2 分鐘新鮮空氣就能重置注意力。",
                "science": "短暫的戶外接觸能降低皮質醇 12-16% 並恢復注意力容量（Hunter et al., 2019）。",
                "context": "outdoor_mild",
            }
        else:
            nudge = {
                "action": f"室外 {temp}°C，{desc_zh}。穿暖一點出去 60 秒，冷空氣能透過交感神經啟動警覺性。",
                "science": "短暫冷刺激能增加去甲腎上腺素 200-300%，改善專注力和情緒（Shevchuk, 2008）。",
                "context": "outdoor_cold",
            }
    else:
        if "rain" in desc or "drizzle" in desc or "shower" in desc:
            nudge = {
                "action": f"外面在下雨（{temp}°C）。站到窗邊看雨 30 秒。雨聲和視覺韻律天然地讓人平靜。",
                "science": "雨聲能啟動副交感神經系統，效果類似自然散步（Alvarsson et al., 2010）。",
                "context": "indoor_rain",
            }
        else:
            nudge = {
                "action": f"室外不太適合出去（{temp}°C，{desc_zh}）。做個室內伸展：雙手高舉過頭撐 10 秒，再前彎。",
                "science": "休息時做室內伸展能減少桌面工作者 32% 的肌肉骨骼疼痛（Shariat et al., 2018）。",
                "context": "indoor_general",
            }

    if uv and uv >= 6 and outdoor_ok:
        nudge["uv_warning"] = f"紫外線指數 {uv}（高）。如果要待在戶外，記得防曬或戴帽子。"

    nudge["icon"] = "🌿"
    nudge["dimension"] = "environmental"
    nudge["weather"] = {"temp": temp, "desc": desc_zh, "outdoor_friendly": outdoor_ok}
    return nudge
