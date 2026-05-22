#!/usr/bin/env python3
"""Módulo de clima usando wttr.in (gratis, sin API key)."""

import json
import urllib.request
import logging

logger = logging.getLogger("DateTimeUserbot")

# Cache de clima para no hacer requests cada minuto
_weather_cache = {"data": None, "timestamp": 0}

def get_weather(city: str = "Havana") -> dict:
    """
    Obtiene el clima actual de una ciudad usando wttr.in.
    Retorna: {"temp": "28°C", "desc": "Soleado", "emoji": "☀️", "humidity": "65%"}
    """
    import time
    global _weather_cache
    
    # Usar cache por 10 minutos
    now = time.time()
    if _weather_cache["data"] and (now - _weather_cache["timestamp"]) < 600:
        return _weather_cache["data"]
    
    try:
        url = f"https://wttr.in/{city}?format=j1"
        req = urllib.request.Request(url, headers={"User-Agent": "curl/7.68.0"})
        with urllib.request.urlopen(req, timeout=10) as response:
            data = json.loads(response.read().decode())
        
        current = data.get("current_condition", [{}])[0]
        temp_c = current.get("temp_C", "?")
        humidity = current.get("humidity", "?")
        desc = current.get("weatherDesc", [{}])[0].get("value", "N/A")
        code = int(current.get("weatherCode", 113))
        
        # Mapear código a emoji
        emoji = _weather_code_to_emoji(code)
        
        result = {
            "temp": f"{temp_c}°C",
            "desc": desc,
            "emoji": emoji,
            "humidity": f"{humidity}%",
        }
        
        _weather_cache = {"data": result, "timestamp": now}
        return result
        
    except Exception as e:
        logger.debug(f"Error obteniendo clima: {e}")
        return {"temp": "?°C", "desc": "N/A", "emoji": "🌡", "humidity": "?%"}

def _weather_code_to_emoji(code: int) -> str:
    """Convierte código de clima de wttr.in a emoji."""
    if code in (113,):  # Clear/Sunny
        return "☀️"
    elif code in (116,):  # Partly cloudy
        return "⛅"
    elif code in (119, 122):  # Cloudy
        return "☁️"
    elif code in (143, 248, 260):  # Fog
        return "🌫"
    elif code in (176, 263, 266, 293, 296, 299, 302, 305, 308, 311, 314, 317, 353, 356, 359):  # Rain
        return "🌧"
    elif code in (200, 386, 389, 392, 395):  # Thunder
        return "⛈"
    elif code in (179, 182, 185, 227, 230, 320, 323, 326, 329, 332, 335, 338, 350, 362, 365, 368, 371, 374, 377):  # Snow
        return "❄️"
    else:
        return "🌡"
