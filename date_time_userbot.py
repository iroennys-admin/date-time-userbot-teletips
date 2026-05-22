#!/usr/bin/env python3
"""
DATE TIME USERBOT v2.0 - Version Completa con 18 mejoras
Flask arranca PRIMERO, Pyrogram se inicializa despues.
"""

import os
import sys
import logging
import asyncio
import datetime
import traceback
import threading
import urllib.request
from pathlib import Path

# ─── Logging ──────────────────────────────────────────────────────
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S",
)
logger = logging.getLogger("DateTimeUserbot")

# ─── Estado global del bot ──────────────────────────────────────
bot_state = {
    "started": False,
    "connected": False,
    "last_update": None,
    "error": None,
    "startup_log": [],
    "profile_name": None,
    "update_count": 0,
    "image_style": "auto",
    "bio_category": "random",
    "schedule_mode": True,
    "show_weather": True,
    "show_progress": True,
    "afk_enabled": True,
    "afk_message": "No estoy disponible ahora.",
    "afk_replied": [],
    "countdown_date": "",
    "countdown_label": "",
    "weather_info": None,
    "python_version": sys.version,
}

def log_startup(msg):
    """Agrega mensaje al log de inicio visible via /debug."""
    logger.info(msg)
    bot_state["startup_log"].append(f"{datetime.datetime.now().strftime('%H:%M:%S')} | {msg}")
    # Mantener solo los ultimos 30 mensajes
    bot_state["startup_log"] = bot_state["startup_log"][-30:]

# ─── Flask App (arranca PRIMERO) ─────────────────────────────────
from flask import Flask, jsonify
app = Flask(__name__)

@app.route("/")
def health_check():
    return jsonify({
        "status": "alive",
        "bot": "DateTimeUserbot v2.0",
        "connected": bot_state["connected"],
        "last_update": bot_state["last_update"],
        "update_count": bot_state["update_count"],
        "style": bot_state["image_style"],
    })

@app.route("/health")
def health():
    return jsonify({"status": "healthy", "bot_connected": bot_state["connected"]})

@app.route("/debug")
def debug_info():
    return jsonify({
        "status": "alive",
        "bot_started": bot_state["started"],
        "bot_connected": bot_state["connected"],
        "profile_name": bot_state["profile_name"],
        "last_update": bot_state["last_update"],
        "update_count": bot_state["update_count"],
        "error": bot_state["error"],
        "image_style": bot_state["image_style"],
        "bio_category": bot_state["bio_category"],
        "show_weather": bot_state["show_weather"],
        "show_progress": bot_state["show_progress"],
        "afk_enabled": bot_state["afk_enabled"],
        "countdown": bot_state["countdown_date"],
        "python_version": sys.version,
        "startup_log": bot_state["startup_log"],
    })

log_startup("Flask app creada")

# ─── Cargar configuracion ────────────────────────────────────────
try:
    from config import (
        API_ID, API_HASH, SESSION_STRING, TIME_ZONE, UPDATE_INTERVAL,
        MAX_RETRIES, PORT, EXTRA_TIMEZONES, FONT_PATH, BASE_IMAGE,
        IMAGE_STYLE, BIO_CATEGORY, BIO_CUSTOM_PREFIX, BIO_SHOW_COUNTER,
        BIO_SCHEDULE_MODE, WEATHER_CITY, WEATHER_SHOW, COUNTDOWN_DATE,
        COUNTDOWN_LABEL, AFK_ENABLED, AFK_MESSAGE, NOTIFY_CHAT_ID,
        SHOW_DAY_PROGRESS, DYNAMIC_HOUR_EMOJI, MONITOR_TIMEOUT,
    )
    log_startup(f"Config cargada - TZ: {TIME_ZONE}, PORT: {PORT}")
    
    # Actualizar bot_state con config
    bot_state["image_style"] = IMAGE_STYLE
    bot_state["bio_category"] = BIO_CATEGORY
    bot_state["schedule_mode"] = BIO_SCHEDULE_MODE
    bot_state["show_weather"] = WEATHER_SHOW
    bot_state["show_progress"] = SHOW_DAY_PROGRESS
    bot_state["afk_enabled"] = AFK_ENABLED
    bot_state["afk_message"] = AFK_MESSAGE
    bot_state["countdown_date"] = COUNTDOWN_DATE
    bot_state["countdown_label"] = COUNTDOWN_LABEL
    
except Exception as e:
    log_startup(f"ERROR cargando config: {e}")
    API_ID = 14681595
    API_HASH = "a86730aab5c59953c424abb4396d32d5"
    SESSION_STRING = os.environ.get("SESSION_STRING", "")
    TIME_ZONE = "America/Havana"
    UPDATE_INTERVAL = 60
    MAX_RETRIES = 5
    PORT = int(os.environ.get("PORT", 10000))
    EXTRA_TIMEZONES = ""
    FONT_PATH = "ds-digit.ttf"
    BASE_IMAGE = "image.jpg"
    IMAGE_STYLE = "auto"
    BIO_CATEGORY = "random"
    BIO_CUSTOM_PREFIX = ""
    BIO_SHOW_COUNTER = True
    BIO_SCHEDULE_MODE = True
    WEATHER_CITY = "Havana"
    WEATHER_SHOW = True
    COUNTDOWN_DATE = ""
    COUNTDOWN_LABEL = ""
    AFK_ENABLED = True
    AFK_MESSAGE = "No estoy disponible ahora."
    NOTIFY_CHAT_ID = 0
    SHOW_DAY_PROGRESS = True
    DYNAMIC_HOUR_EMOJI = True
    MONITOR_TIMEOUT = 300

# ─── Event loop ANTES de importar Pyrogram ───────────────────────
loop = asyncio.new_event_loop()
asyncio.set_event_loop(loop)
log_startup("Event loop creado")

# ─── Imports pesados (con manejo de errores) ─────────────────────
pyrogram_ok = False
try:
    from pyrogram import Client, filters
    from pyrogram.errors import FloodWait, AuthKeyUnregistered, SessionRevoked
    pyrogram_ok = True
    log_startup("Pyrogram importado OK")
except Exception as e:
    log_startup(f"ERROR importando Pyrogram: {e}")
    bot_state["error"] = f"Pyrogram import: {e}"

pil_ok = False
try:
    from PIL import Image, ImageDraw, ImageFont
    pil_ok = True
    log_startup("PIL importado OK")
except Exception as e:
    log_startup(f"ERROR importando PIL: {e}")

try:
    import pytz
    log_startup("pytz importado OK")
except Exception as e:
    log_startup(f"ERROR importando pytz: {e}")

image_gen_ok = False
try:
    from image_generator import generate_profile_image
    image_gen_ok = True
    log_startup("Image generator importado OK")
except Exception as e:
    log_startup(f"ERROR importando image_generator: {e}")

weather_ok = False
try:
    from weather import get_weather
    weather_ok = True
    log_startup("Weather importado OK")
except Exception as e:
    log_startup(f"ERROR importando weather: {e}")

emojis_ok = False
try:
    from lists_teletips.emojis_teletips import get_emoji, general_emojis
    emojis_ok = True
    log_startup("Emojis importado OK")
except Exception as e:
    log_startup(f"ERROR importando emojis: {e}")

quotes_ok = False
try:
    from lists_teletips.quotes_teletips import get_quote, quotes_by_category
    quotes_ok = True
    log_startup("Quotes importado OK")
except Exception as e:
    log_startup(f"ERROR importando quotes: {e}")

# ─── Cliente Pyrogram ─────────────────────────────────────────────
userbot = None
if pyrogram_ok:
    try:
        userbot = Client(
            name="date_time_userbot",
            api_id=API_ID,
            api_hash=API_HASH,
            session_string=SESSION_STRING,
        )
        log_startup("Pyrogram Client creado")
    except Exception as e:
        log_startup(f"ERROR creando Pyrogram Client: {e}")
        bot_state["error"] = f"Pyrogram Client: {e}"

# ─── Registrar Dashboard ──────────────────────────────────────────
try:
    from dashboard import register_dashboard
    register_dashboard(app, bot_state, config_module=__import__('config'))
    log_startup("Dashboard registrado")
except Exception as e:
    log_startup(f"ERROR registrando dashboard: {e}")

# ─── Registrar Comandos ───────────────────────────────────────────
if userbot:
    try:
        from commands import register_commands
        register_commands(userbot, bot_state)
        log_startup("Comandos registrados")
    except Exception as e:
        log_startup(f"ERROR registrando comandos: {e}")

# ─── Notificaciones ───────────────────────────────────────────────
async def send_notification(message: str):
    if not NOTIFY_CHAT_ID or not userbot:
        return
    try:
        await userbot.send_message(NOTIFY_CHAT_ID, f"🤖 {message}")
    except Exception as e:
        logger.debug(f"No se pudo enviar notificacion: {e}")

# ─── Calcular Countdown ───────────────────────────────────────────
def get_countdown_days() -> tuple:
    cd_date = bot_state.get("countdown_date", "")
    if not cd_date:
        return None, None
    try:
        target = datetime.datetime.strptime(cd_date, "%Y-%m-%d").date()
        today = datetime.date.today()
        days = (target - today).days
        return days, bot_state.get("countdown_label", "")
    except Exception:
        return None, None

# ─── Zonas horarias adicionales ───────────────────────────────────
def get_extra_tz_times() -> list:
    extra_tz = EXTRA_TIMEZONES
    if not extra_tz:
        return []
    results = []
    for tz_name in extra_tz.split(","):
        tz_name = tz_name.strip()
        if not tz_name:
            continue
        try:
            tz = pytz.timezone(tz_name)
            now_tz = datetime.datetime.now(tz)
            short_name = tz_name.split("/")[-1].replace("_", " ")
            results.append((short_name, now_tz.strftime("%I:%M %p")))
        except Exception:
            pass
    return results

# ─── Bucle Principal del Bot ──────────────────────────────────────
async def main_bot():
    if not userbot:
        log_startup("No se puede iniciar bot: Pyrogram no disponible")
        bot_state["error"] = "Pyrogram no disponible"
        return

    retry_count = 0
    base_delay = 5
    last_success_time = 0

    bot_state["started"] = True
    log_startup("Iniciando bucle principal del bot...")

    # Conectar
    try:
        await userbot.start()
        me = await userbot.get_me()
        bot_state["connected"] = True
        bot_state["profile_name"] = me.first_name
        log_startup(f"Conectado como: {me.first_name} (ID: {me.id})")
        await send_notification(f"Bot iniciado\nConectado como: {me.first_name}")
    except (AuthKeyUnregistered, SessionRevoked) as e:
        log_startup(f"Sesion invalida: {e}")
        bot_state["error"] = str(e)
        return
    except Exception as e:
        log_startup(f"Error al iniciar: {e}")
        bot_state["error"] = str(e)

    while True:
        try:
            # Reconexion si esta desconectado
            if not bot_state["connected"]:
                log_startup("Intentando reconectar...")
                try:
                    await userbot.stop()
                except Exception:
                    pass
                await userbot.start()
                me = await userbot.get_me()
                bot_state["connected"] = True
                bot_state["profile_name"] = me.first_name
                retry_count = 0
                log_startup(f"Reconectado como: {me.first_name}")
                await send_notification("Bot reconectado")

            # Monitoreo proactivo
            import time
            current_time = time.time()
            if last_success_time > 0 and (current_time - last_success_time) > MONITOR_TIMEOUT:
                log_startup(f"No se actualizo en {MONITOR_TIMEOUT}s. Forzando reconexion...")
                bot_state["connected"] = False
                continue

            # Obtener hora
            tz = pytz.timezone(TIME_ZONE)
            now = datetime.datetime.now(tz)
            hour = now.hour

            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%b %d, %Y")
            day_name = now.strftime("%A")
            day_of_year = now.timetuple().tm_yday

            # Emoji
            emoji = get_emoji(hour, dynamic=DYNAMIC_HOUR_EMOJI) if emojis_ok else "✨"

            # Frase
            quote = get_quote(
                category=bot_state.get("bio_category", "random"),
                hour=hour,
                schedule_mode=bot_state.get("schedule_mode", True),
            ) if quotes_ok else "Live your best life"

            # Clima
            weather_data = None
            if bot_state.get("show_weather", True) and weather_ok:
                weather_data = get_weather(WEATHER_CITY)
                bot_state["weather_info"] = f"{weather_data['emoji']} {weather_data['temp']}"

            # Countdown
            countdown_days, countdown_label = get_countdown_days()

            # Zonas horarias extra
            extra_tz = get_extra_tz_times()

            # Generar imagen
            image_path = None
            if image_gen_ok:
                image_path = generate_profile_image(
                    time_str=time_str,
                    date_str=date_str,
                    hour=hour,
                    style=bot_state.get("image_style", "auto"),
                    base_image=BASE_IMAGE,
                    font_path=FONT_PATH,
                    weather=weather_data,
                    show_progress=bot_state.get("show_progress", True),
                    countdown_days=countdown_days,
                    countdown_label=countdown_label,
                    extra_tz_times=extra_tz,
                )

            if image_path:
                try:
                    await userbot.set_profile_photo(photo=image_path)
                    logger.info("Foto de perfil actualizada")
                except FloodWait as e:
                    logger.warning(f"FloodWait en foto: {e.value}s")
                    await asyncio.sleep(e.value)
                    continue
                except Exception as e:
                    logger.error(f"Error actualizando foto: {e}")

                # Eliminar foto anterior
                try:
                    photos = userbot.get_chat_photos("me")
                    async for i, photo in enumerate(photos):
                        if i >= 1:
                            await userbot.delete_profile_photos(photo.file_id)
                            break
                except Exception:
                    pass

                try:
                    Path(image_path).unlink(missing_ok=True)
                except Exception:
                    pass

            # Actualizar apellido y bio
            last_name = f"| {time_str} | {date_str}"
            
            bio_parts = []
            if BIO_CUSTOM_PREFIX:
                bio_parts.append(BIO_CUSTOM_PREFIX)
            bio_parts.append(f"{emoji} {quote}")
            if BIO_SHOW_COUNTER:
                bio_parts.append(f"Dia {day_of_year}")
            bio = " | ".join(bio_parts)

            try:
                await userbot.update_profile(last_name=last_name, bio=bio)
                bot_state["last_update"] = now.isoformat()
                bot_state["update_count"] += 1
                last_success_time = time.time()
                logger.info(f"Perfil actualizado: {day_name} {time_str}")
            except FloodWait as e:
                logger.warning(f"FloodWait en perfil: {e.value}s")
                await asyncio.sleep(e.value)
                continue

            retry_count = 0
            await asyncio.sleep(UPDATE_INTERVAL)

        except FloodWait as e:
            logger.warning(f"FloodWait global: {e.value}s")
            await asyncio.sleep(e.value)

        except (AuthKeyUnregistered, SessionRevoked) as e:
            logger.critical(f"Sesion invalida: {e}")
            bot_state["connected"] = False
            bot_state["error"] = str(e)
            await send_notification(f"Bot DETENIDO - Sesion revocada: {e}")
            break

        except ConnectionError as e:
            retry_count += 1
            delay = min(base_delay * (2 ** retry_count), 300)
            logger.error(f"Error de conexion (intento {retry_count}): {e}")
            bot_state["connected"] = False
            await asyncio.sleep(delay)

        except Exception as e:
            retry_count += 1
            delay = min(base_delay * (2 ** retry_count), 300)
            logger.error(f"Error inesperado (intento {retry_count}): {e}")
            logger.debug(traceback.format_exc())

            if retry_count >= MAX_RETRIES:
                logger.critical("Maximo reintentos. Reiniciando cliente...")
                await send_notification(f"Bot reiniciandose - Error: {e}")
                try:
                    await userbot.stop()
                except Exception:
                    pass
                retry_count = 0
                bot_state["connected"] = False

            await asyncio.sleep(delay)


# ─── Keep-Alive ────────────────────────────────────────────────────
def keep_alive():
    render_url = os.environ.get("RENDER_EXTERNAL_URL", "")
    if not render_url:
        render_url = os.environ.get("RENDER_SERVICE_URL", "")
    
    if render_url:
        def ping():
            while True:
                try:
                    urllib.request.urlopen(f"{render_url}/health", timeout=10)
                except Exception:
                    pass
                threading.Event().wait(14 * 60)
        
        t = threading.Thread(target=ping, daemon=True)
        t.start()
        logger.info(f"Keep-alive activado: {render_url}/health")
    else:
        logger.warning("Keep-alive: RENDER_EXTERNAL_URL no encontrada")


# ─── Punto de Entrada ─────────────────────────────────────────────
if __name__ == "__main__":
    log_startup("=== DateTime Userbot v2.0 iniciando ===")
    
    async def run_all():
        bot_task = asyncio.ensure_future(main_bot())
        
        flask_thread = threading.Thread(
            target=lambda: app.run(host="0.0.0.0", port=PORT, debug=False, use_reloader=False),
            daemon=True
        )
        flask_thread.start()
        log_startup(f"Flask iniciando en puerto {PORT}")
        
        keep_alive()
        
        await bot_task

    loop.run_until_complete(run_all())
